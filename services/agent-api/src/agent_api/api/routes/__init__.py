from fastapi import APIRouter

from agent_api.api.routes import chat, health, search

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(search.router)

__all__ = ["api_router"]
