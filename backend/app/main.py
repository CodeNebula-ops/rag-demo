import asyncio
import subprocess
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import v1_router
from app.config import settings
from app.core.database import async_session_factory, engine
from app.core.exceptions import AppException
from app.models.base import Base
from app.services.embedding_service import load_embedding_model
from app.services.reranker_service import load_reranker_model
from app.services.retrieval_service import rebuild_bm25_index
from app.services.vector_store_service import init_collection

logger = structlog.get_logger()


async def _wait_for_db(retries: int = 10, delay: int = 3) -> None:
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("db_connected", attempt=attempt)
            return
        except Exception as e:
            logger.warning("db_not_ready", attempt=attempt, error=str(e)[:100])
            if attempt < retries:
                await asyncio.sleep(delay)
    raise RuntimeError("Could not connect to database after retries")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup_begin")

    await _wait_for_db()

    logger.info("running_migrations")
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=False,
        capture_output=True,
    )

    await init_collection()

    load_embedding_model()
    load_reranker_model()

    async with async_session_factory() as session:
        await rebuild_bm25_index(session)

    if not settings.groq_api_key:
        logger.warning("groq_api_key_not_set", hint="Set GROQ_API_KEY env var")

    logger.info("startup_complete")
    yield

    await engine.dispose()
    logger.info("shutdown_complete")


app = FastAPI(
    title="Retrion",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(v1_router)
