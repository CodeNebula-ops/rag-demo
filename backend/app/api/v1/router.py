from fastapi import APIRouter

from app.api.v1.analytics_router import router as analytics_router
from app.api.v1.chat_router import router as chat_router
from app.api.v1.document_router import router as document_router
from app.api.v1.health_router import router as health_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(health_router)
v1_router.include_router(chat_router)
v1_router.include_router(document_router)
v1_router.include_router(analytics_router)
