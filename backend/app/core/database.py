from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _get_db_url() -> str:
    url = settings.database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if "render.com" in url or "oregon-postgres" in url or "dpg-" in url:
        separator = "&" if "?" in url else "?"
        url += f"{separator}ssl=require"
    return url


engine = create_async_engine(_get_db_url(), echo=False, pool_size=5, max_overflow=5)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
