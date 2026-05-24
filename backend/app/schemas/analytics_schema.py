from datetime import datetime

from pydantic import BaseModel


class UsageStatsResponse(BaseModel):
    total_queries: int
    queries_today: int
    avg_confidence: float
    avg_latency_ms: float


class ContentGapResponse(BaseModel):
    query: str
    confidence_score: float
    created_at: datetime
