from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def log_event(
    session: AsyncSession,
    event_type: str,
    resource_type: str,
    resource_id: str | None = None,
    detail: dict | None = None,
) -> None:
    entry = AuditLog(
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        action_detail=detail,
    )
    session.add(entry)
    await session.flush()
