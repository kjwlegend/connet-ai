"""
API v1 Main Router

This module contains the main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    health,
    users,
    # conversations,
    # agents,
    # files,
)

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# TODO: Uncomment as endpoints are implemented
# api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
# api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
# api_router.include_router(files.router, prefix="/files", tags=["files"])