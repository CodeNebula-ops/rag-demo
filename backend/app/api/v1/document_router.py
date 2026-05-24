import os
import uuid

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_session, async_session_factory
from app.models.document import Document
from app.schemas.document_schema import DocumentDetailResponse, DocumentResponse
from app.services.audit_service import log_event
from app.services.vector_store_service import deactivate_document_vectors
from app.utils.file_utils import generate_storage_path, validate_file_extension

logger = structlog.get_logger()
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
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
    await session.refresh(doc)

    background_tasks.add_task(_run_ingestion, str(doc.id), storage_path, file.filename, file_size)

    return doc


async def _run_ingestion(doc_id: str, file_path: str, filename: str, file_size: int):
    from app.services.ingestion_service import ingest_document

    async with async_session_factory() as session:
        try:
            doc = await session.get(Document, uuid.UUID(doc_id))
            if not doc:
                return

            from app.services.ingestion_service import _extract_text
            from app.core.text_preprocessor import normalize_text
            from app.services.chunking_service import chunk_document
            from app.services.embedding_service import embed_texts
            from app.services.vector_store_service import upsert_vectors
            from app.services.retrieval_service import add_to_bm25_index
            from pathlib import Path
            import uuid as uuid_mod

            from app.models.document import DocumentChunk
            from sqlalchemy import delete as sa_delete

            existing = await session.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == doc.id)
            )
            old_chunks = existing.scalars().all()
            if old_chunks:
                deactivate_document_vectors(doc_id)
                await session.execute(
                    sa_delete(DocumentChunk).where(DocumentChunk.document_id == doc.id)
                )
                await session.flush()

            ext = Path(filename).suffix.lower()
            raw_text = _extract_text(file_path, ext)
            cleaned_text = normalize_text(raw_text)

            if not cleaned_text or len(cleaned_text.strip()) < 10:
                doc.status = "failed"
                await session.commit()
                return

            chunks = chunk_document(cleaned_text, doc.title)
            if not chunks:
                doc.status = "failed"
                await session.commit()
                return

            chunk_texts = [c["chunk_text"] for c in chunks]
            embeddings = await embed_texts(chunk_texts)

            payloads = []
            db_chunks = []

            for i, chunk_data in enumerate(chunks):
                chunk_id = uuid_mod.uuid4()
                payloads.append({
                    "document_id": doc_id,
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
                resource_id=doc_id,
                detail={"filename": filename, "chunks": len(db_chunks)},
            )

            await session.commit()
            logger.info("background_ingestion_complete", doc_id=doc_id, chunks=len(db_chunks))

        except Exception as e:
            logger.error("background_ingestion_failed", doc_id=doc_id, error=str(e))
            try:
                doc = await session.get(Document, uuid.UUID(doc_id))
                if doc:
                    doc.status = "failed"
                    await session.commit()
            except Exception:
                pass


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
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status not in ("processing", "failed"):
        raise HTTPException(status_code=400, detail="Document is already active")

    doc.status = "processing"
    await session.flush()

    background_tasks.add_task(
        _run_ingestion, str(doc.id), doc.storage_path, doc.filename, doc.file_size_bytes
    )

    return {"status": "reprocessing", "document_id": str(document_id)}


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    deactivate_document_vectors(str(document_id))

    doc.status = "archived"
    await session.flush()

    await log_event(
        session,
        event_type="DOCUMENT_DELETED",
        resource_type="document",
        resource_id=str(document_id),
    )

    return {"status": "archived", "document_id": str(document_id)}
