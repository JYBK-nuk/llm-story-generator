from fastapi import APIRouter

from .ws_events import *

api_router = APIRouter(
    prefix="/api",
)


__all__ = ["api_router"]
