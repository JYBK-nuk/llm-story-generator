from fastapi import APIRouter

from api.langchain.story import router as story_router
from .ws_events import *

api_router = APIRouter(
    prefix="/api",
)

api_router.include_router(story_router, prefix="/langchain", tags=["LangChain"])

__all__ = ["api_router"]
