import json
import time
import uuid
from collections.abc import AsyncGenerator

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.chat import ChatMessage, ChatSession
from app.services.audit_service import log_event
from app.services.citation_service import extract_citations, has_citations
from app.services.context_compressor_service import compress_and_order
from app.services.guardrails_service import (
    check_faithfulness,
    compute_confidence,
    should_skip_llm,
)
from app.services.llm_service import generate_stream
from app.services.query_understanding_service import understand_query
from app.services.retrieval_service import retrieve
from app.services.semantic_cache_service import cache as semantic_cache
from app.utils.prompt_templates import (
    SYSTEM_PROMPT,
    format_context_chunks,
    format_conversation_history,
)

logger = structlog.get_logger()

NO_INFO_RESPONSE = (
    "I don't have enough information in the knowledge base to answer this question. "
    "Please consult the relevant document directly."
)

NO_RELEVANT_DOCS = "No relevant information found in the knowledge base for this question."

GREETING_RESPONSE = (
    "Hello! I'm your knowledge base assistant. "
    "Ask me anything about the documents in the system and I'll find the answer for you."
)


async def process_query(
    query: str,
    session_id: uuid.UUID,
    db: AsyncSession,
) -> AsyncGenerator[dict, None]:
    start_time = time.time()

    user_msg = ChatMessage(
        id=uuid.uuid4(),
        session_id=session_id,
        role="user",
        content=query,
    )
    db.add(user_msg)
    await db.flush()

    history = await _get_conversation_history(session_id, db)

    # --- Stage 2: Query Understanding ---
    query_info = await understand_query(query, history)
    search_query = query_info["rewritten_query"]
    intent = query_info["intent"]

    if query_info["is_greeting"]:
        yield {"event": "token", "data": {"token": GREETING_RESPONSE}}
        yield {"event": "confidence", "data": {"score": 1.0, "level": "high"}}
        assistant_msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            role="assistant",
            content=GREETING_RESPONSE,
            confidence_score=1.0,
            latency_ms=int((time.time() - start_time) * 1000),
        )
        db.add(assistant_msg)
        await db.flush()
        yield {"event": "done", "data": {"message_id": str(assistant_msg.id)}}
        return

    # --- Stage 7: Semantic Cache Check ---
    cached = await semantic_cache.get(search_query)
    if cached:
        yield {"event": "token", "data": {"token": cached["answer"]}}
        yield {"event": "citation", "data": {"citations": cached.get("citations", [])}}
        yield {"event": "confidence", "data": cached.get("confidence", {"score": 0.8, "level": "high"})}

        assistant_msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            role="assistant",
            content=cached["answer"],
            confidence_score=cached.get("confidence", {}).get("score", 0.8),
            citations=cached.get("citations", []),
            latency_ms=int((time.time() - start_time) * 1000),
        )
        db.add(assistant_msg)
        await db.flush()
        yield {"event": "done", "data": {"message_id": str(assistant_msg.id)}}
        return

    # --- Stage 3: Retrieval (hybrid: dense + BM25 + RRF) ---
    retrieved_chunks = await retrieve(search_query)

    if query_info["expanded_terms"]:
        expansion = " ".join(query_info["expanded_terms"])
        extra_chunks = await retrieve(expansion, top_n=3)
        seen_ids = {c.get("point_id") for c in retrieved_chunks}
        for ec in extra_chunks:
            if ec.get("point_id") not in seen_ids:
                retrieved_chunks.append(ec)
                seen_ids.add(ec.get("point_id"))

    reranker_scores = [c.get("reranker_score", 0.0) for c in retrieved_chunks]

    # --- Abstention gate ---
    if should_skip_llm(reranker_scores):
        yield {"event": "token", "data": {"token": NO_RELEVANT_DOCS}}
        yield {"event": "confidence", "data": {"score": 0.0, "level": "low"}}

        assistant_msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            role="assistant",
            content=NO_RELEVANT_DOCS,
            confidence_score=0.0,
            latency_ms=int((time.time() - start_time) * 1000),
        )
        db.add(assistant_msg)
        await db.flush()
        yield {"event": "done", "data": {"message_id": str(assistant_msg.id)}}
        return

    # --- Stage 4: Post-retrieval (compress, dedup, order) ---
    processed_chunks = await compress_and_order(retrieved_chunks, intent)

    context = format_context_chunks(processed_chunks)
    history_text = format_conversation_history(history)

    # --- Stage 5: Generation (grounded prompting + citation enforcement) ---
    system_content = SYSTEM_PROMPT.format(
        context_chunks=context,
        conversation_history=history_text,
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": query},
    ]

    full_response = []
    async for token in generate_stream(messages):
        full_response.append(token)
        yield {"event": "token", "data": {"token": token}}

    answer = "".join(full_response)

    if not answer.strip():
        answer = NO_INFO_RESPONSE

    # --- Stage 6: Validation (faithfulness + confidence + citations) ---
    faithfulness = await check_faithfulness(answer, processed_chunks)
    confidence = compute_confidence(reranker_scores, faithfulness["faithful_ratio"])

    citations = extract_citations(answer, processed_chunks)

    if not has_citations(answer) and processed_chunks:
        answer += "\n\nRelevant sources:\n"
        for chunk in processed_chunks[:3]:
            title = chunk.get("document_title", "Unknown")
            section = chunk.get("section_path", "")
            answer += f"- [Source: {title}, {section}]\n"
        citations = extract_citations(answer, processed_chunks)

    if faithfulness["faithful_ratio"] < 0.7:
        answer += (
            "\n\n*Some parts of this answer may not be fully supported "
            "by the source documents.*"
        )

    yield {"event": "citation", "data": {"citations": citations}}
    yield {"event": "confidence", "data": confidence}

    latency_ms = int((time.time() - start_time) * 1000)

    # --- Cache the result ---
    await semantic_cache.put(search_query, {
        "answer": answer,
        "citations": citations,
        "confidence": confidence,
    })

    chunk_refs = [
        {"point_id": c.get("point_id"), "score": c.get("reranker_score", 0.0)}
        for c in processed_chunks
    ]

    assistant_msg = ChatMessage(
        id=uuid.uuid4(),
        session_id=session_id,
        role="assistant",
        content=answer,
        retrieved_chunks={"chunks": chunk_refs},
        confidence_score=confidence["score"],
        citations=citations,
        latency_ms=latency_ms,
    )
    db.add(assistant_msg)

    session = await db.get(ChatSession, session_id)
    if session and not session.title:
        session.title = query[:100]

    await db.flush()

    await log_event(
        db,
        event_type="QUERY_SUBMITTED",
        resource_type="query",
        resource_id=str(assistant_msg.id),
        detail={
            "query": query,
            "rewritten_query": search_query,
            "intent": intent,
            "confidence": confidence["score"],
            "latency_ms": latency_ms,
            "chunks_retrieved": len(retrieved_chunks),
            "chunks_after_compression": len(processed_chunks),
        },
    )

    yield {
        "event": "done",
        "data": {
            "message_id": str(assistant_msg.id),
            "latency_ms": latency_ms,
        },
    }


async def _get_conversation_history(
    session_id: uuid.UUID,
    db: AsyncSession,
) -> list[dict]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(settings.max_conversation_history * 2)
    )

    messages = result.scalars().all()
    messages.reverse()

    return [{"role": m.role, "content": m.content} for m in messages]
