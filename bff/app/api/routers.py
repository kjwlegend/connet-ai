"""Top-level API router aggregation for the BFF."""

from fastapi import APIRouter

from app.api.v1 import router as v1_router

api = APIRouter()

api.include_router(v1_router.api_router, prefix="/v1")

__all__ = ["api"]
