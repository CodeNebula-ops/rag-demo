from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.analytics_schema import ContentGapResponse, UsageStatsResponse
from app.services.analytics_service import get_content_gaps, get_usage_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/usage", response_model=UsageStatsResponse)
async def usage_stats(session: AsyncSession = Depends(get_session)):
    return await get_usage_stats(session)


@router.get("/content-gaps", response_model=list[ContentGapResponse])
async def content_gaps(session: AsyncSession = Depends(get_session)):
    return await get_content_gaps(session)
