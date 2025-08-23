"""
API v1 Main Router

This module contains the main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    health,
    users,
    # conversations,  # Temporarily disabled due to import issues
    # files,
    ai_agents,
    ai_chat,
    contacts,
    langgraph_chat,
)

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# AI Service endpoints
api_router.include_router(ai_agents.router, tags=["AI Agents"])
api_router.include_router(ai_chat.router)

# contacts
api_router.include_router(contacts.router, tags=["Contacts"])

# Enhanced conversation functionality  
api_router.include_router(langgraph_chat.router, prefix="/conversations", tags=["Conversations"])

# Note: Original conversations endpoint replaced with LangGraph-enhanced version

# TODO: Uncomment as endpoints are implemented
# api_router.include_router(files.router, prefix="/files", tags=["files"])
