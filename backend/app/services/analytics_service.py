from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.chat import ChatMessage


async def get_usage_stats(session: AsyncSession) -> dict:
    total_q = await session.scalar(
        select(func.count(ChatMessage.id)).where(ChatMessage.role == "user")
    ) or 0

    today_start = datetime.combine(date.today(), datetime.min.time())
    today_q = await session.scalar(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.role == "user",
            ChatMessage.created_at >= today_start,
        )
    ) or 0

    avg_conf = await session.scalar(
        select(func.avg(ChatMessage.confidence_score)).where(
            ChatMessage.role == "assistant",
            ChatMessage.confidence_score.is_not(None),
        )
    ) or 0.0

    avg_lat = await session.scalar(
        select(func.avg(ChatMessage.latency_ms)).where(
            ChatMessage.role == "assistant",
            ChatMessage.latency_ms.is_not(None),
        )
    ) or 0.0

    return {
        "total_queries": total_q,
        "queries_today": today_q,
        "avg_confidence": round(float(avg_conf), 3),
        "avg_latency_ms": round(float(avg_lat), 1),
    }


async def get_content_gaps(session: AsyncSession, limit: int = 50) -> list[dict]:
    result = await session.execute(
        select(
            ChatMessage.content,
            ChatMessage.confidence_score,
            ChatMessage.created_at,
        )
        .where(
            ChatMessage.role == "assistant",
            ChatMessage.confidence_score < settings.confidence_threshold,
            ChatMessage.confidence_score.is_not(None),
        )
        .order_by(ChatMessage.confidence_score.asc())
        .limit(limit)
    )

    rows = result.all()
    gaps = []
    for content, score, created_at in rows:
        gaps.append({
            "query": content[:200],
            "confidence_score": round(float(score), 3),
            "created_at": created_at,
        })

    return gaps
