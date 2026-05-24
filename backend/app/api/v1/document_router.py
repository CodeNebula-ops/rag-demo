import os
import uuid
import traceback
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_session
from app.models.document import Document, DocumentChunk
from app.schemas.document_schema import DocumentDetailResponse, DocumentResponse
from app.services.audit_service import log_event
from app.services.vector_store_service import deactivate_document_vectors
from app.utils.file_utils import generate_storage_path, validate_file_extension

logger = structlog.get_logger()
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
):
    validate_file_extension(file.filename)

    content = await file.read()
    file_size = len(content)

    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.max_file_size_mb}MB limit",
        )

    storage_path = generate_storage_path(file.filename)
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    with open(storage_path, "wb") as f:
        f.write(content)

    ext = os.path.splitext(file.filename)[1].lower()
    title = os.path.splitext(file.filename)[0].replace("_", " ").replace("-", " ").title()

    doc = Document(
        id=uuid.uuid4(),
        title=title,
        filename=file.filename,
        file_type=ext.lstrip("."),
        file_size_bytes=file_size,
        storage_path=storage_path,
        status="processing",
    )
    session.add(doc)
    await session.flush()

    try:
        await _process_document(doc, storage_path, file.filename, session)
    except Exception as e:
        logger.error("ingestion_failed", doc_id=str(doc.id), error=str(e), tb=traceback.format_exc())
        doc.status = "failed"
        await session.flush()
        raise HTTPException(status_code=422, detail=f"Processing failed: {str(e)}")

    await session.refresh(doc)
    return doc


async def _process_document(doc: Document, file_path: str, filename: str, session: AsyncSession):
    from app.services.ingestion_service import _extract_text
    from app.core.text_preprocessor import normalize_text
    from app.services.chunking_service import chunk_document
    from app.services.embedding_service import embed_texts
    from app.services.vector_store_service import upsert_vectors
    from app.services.retrieval_service import add_to_bm25_index

    logger.info("ingestion_start", doc_id=str(doc.id))

    ext = Path(filename).suffix.lower()
    raw_text = _extract_text(file_path, ext)
    cleaned_text = normalize_text(raw_text)

    if not cleaned_text or len(cleaned_text.strip()) < 10:
        raise ValueError("No text content extracted from document")

    logger.info("ingestion_chunking", doc_id=str(doc.id), text_len=len(cleaned_text))
    chunks = chunk_document(cleaned_text, doc.title)
    if not chunks:
        raise ValueError("No chunks generated from document")

    logger.info("ingestion_embedding", doc_id=str(doc.id), chunks=len(chunks))
    chunk_texts = [c["chunk_text"] for c in chunks]
    embeddings = await embed_texts(chunk_texts)

    logger.info("ingestion_upserting", doc_id=str(doc.id))
    payloads = []
    db_chunks = []
    for chunk_data in chunks:
        chunk_id = uuid.uuid4()
        payloads.append({
            "document_id": str(doc.id),
            "document_title": doc.title,
            "chunk_text": chunk_data["chunk_text"],
            "section_path": chunk_data.get("section_path", ""),
            "chunk_index": chunk_data["chunk_index"],
            "language": chunk_data.get("language", "en"),
            "is_active": True,
        })
        db_chunks.append(DocumentChunk(
            id=chunk_id,
            document_id=doc.id,
            chunk_index=chunk_data["chunk_index"],
            chunk_text=chunk_data["chunk_text"],
            section_path=chunk_data.get("section_path"),
            chunk_level=chunk_data.get("chunk_level", "paragraph"),
            token_count=chunk_data.get("token_count", 0),
            language=chunk_data.get("language", "en"),
        ))

    point_ids = upsert_vectors(embeddings.tolist(), payloads)

    for i, db_chunk in enumerate(db_chunks):
        db_chunk.qdrant_point_id = point_ids[i]

    session.add_all(db_chunks)
    doc.total_chunks = len(db_chunks)
    doc.status = "active"

    add_to_bm25_index(chunk_texts, point_ids)

    await log_event(
        session,
        event_type="DOCUMENT_UPLOADED",
        resource_type="document",
        resource_id=str(doc.id),
        detail={"filename": filename, "chunks": len(db_chunks)},
    )

    await session.flush()
    logger.info("ingestion_complete", doc_id=str(doc.id), chunks=len(db_chunks))


@router.get("", response_model=list[DocumentResponse])
async def list_documents(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status not in ("processing", "failed"):
        raise HTTPException(status_code=400, detail="Document is already active")

    if not os.path.exists(doc.storage_path):
        raise HTTPException(
            status_code=400,
            detail="Source file is missing (server was restarted). Please delete and re-upload.",
        )

    await session.execute(
        sa_delete(DocumentChunk).where(DocumentChunk.document_id == doc.id)
    )

    try:
        await _process_document(doc, doc.storage_path, doc.filename, session)
    except Exception as e:
        logger.error("reprocess_failed", doc_id=str(doc.id), error=str(e))
        doc.status = "failed"
        await session.flush()
        raise HTTPException(status_code=422, detail=f"Processing failed: {str(e)}")

    return {"status": "active", "document_id": str(document_id), "chunks": doc.total_chunks}


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    deactivate_document_vectors(str(document_id))

    storage_path = doc.storage_path
    await session.delete(doc)
    await session.flush()

    if storage_path:
        try:
            os.remove(storage_path)
        except OSError:
            pass

    await log_event(
        session,
        event_type="DOCUMENT_DELETED",
        resource_type="document",
        resource_id=str(document_id),
    )

    return {"status": "deleted", "document_id": str(document_id)}
