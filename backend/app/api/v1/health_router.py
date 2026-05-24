import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.llm_service import check_groq_health
from app.services.vector_store_service import get_qdrant_client

logger = structlog.get_logger()
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    checks = {}

    try:
        await session.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception:
        checks["postgres"] = "error"

    try:
        client = get_qdrant_client()
        client.get_collections()
        checks["qdrant"] = "ok"
    except Exception:
        checks["qdrant"] = "error"

    try:
        groq_ok = await check_groq_health()
        checks["llm"] = "ok" if groq_ok else "error"
    except Exception:
        checks["llm"] = "error"

    try:
        from app.services.embedding_service import embed_query
        emb = await embed_query("test")
        checks["embeddings"] = f"ok (dim={len(emb)})"
    except Exception as e:
        checks["embeddings"] = f"error: {str(e)[:100]}"

    overall = "ok" if all(str(v).startswith("ok") for v in checks.values()) else "degraded"
    return {"status": overall, **checks}
