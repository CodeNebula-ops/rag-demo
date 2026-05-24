import json
import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.database import get_session
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat_schema import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    FeedbackRequest,
)
from app.services.rag_orchestrator import process_query

logger = structlog.get_logger()
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    body: ChatSessionCreate = None,
    session: AsyncSession = Depends(get_session),
):
    chat_session = ChatSession(
        id=uuid.uuid4(),
        title=body.title if body else None,
    )
    session.add(chat_session)
    await session.flush()
    await session.refresh(chat_session)
    return chat_session


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(ChatSession).order_by(ChatSession.last_active_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: uuid.UUID,
    body: ChatMessageRequest,
    db: AsyncSession = Depends(get_session),
):
    chat_session = await db.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        try:
            async for event in process_query(body.query, session_id, db):
                evt_type = event["event"]
                data = json.dumps(event["data"])
                yield {"event": evt_type, "data": data}
        except Exception as e:
            logger.error("chat_stream_error", error=str(e), session_id=str(session_id))
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())


@router.get("/sessions/{session_id}/history", response_model=list[ChatMessageResponse])
async def get_history(
    session_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return result.scalars().all()


@router.post("/messages/{message_id}/feedback")
async def submit_feedback(
    message_id: uuid.UUID,
    body: FeedbackRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        update(ChatMessage)
        .where(ChatMessage.id == message_id)
        .values(feedback=body.feedback)
        .returning(ChatMessage.id)
    )
    if not result.first():
        raise HTTPException(status_code=404, detail="Message not found")

    from app.services.audit_service import log_event
    await log_event(
        session,
        event_type="FEEDBACK_GIVEN",
        resource_type="query",
        resource_id=str(message_id),
        detail={"feedback": body.feedback},
    )

    return {"status": "ok"}
