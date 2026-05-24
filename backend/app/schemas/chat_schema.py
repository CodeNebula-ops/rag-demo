import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    title: str | None = None


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: datetime
    last_active_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


class CitationResponse(BaseModel):
    text_snippet: str
    document_title: str
    section_path: str | None
    document_id: str
    relevance_score: float


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    confidence_score: float | None
    citations: list[CitationResponse] | None
    feedback: str | None
    latency_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    feedback: str = Field(..., pattern="^(up|down)$")
