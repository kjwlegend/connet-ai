"""
API v1 Main Router

This module contains the main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.modules.users.router import router as users_router
from app.modules.contacts.router import router as contacts_router
from app.modules.agents.router import router as agents_router
from app.modules.conversations.router import router as conversations_router
from app.modules.timeline.router import router as timeline_router
from app.modules.auth.router import router as auth_router
from app.modules.ai.chat import router as ai_chat_router
from app.modules.ai.workflows import router as workflows_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(users_router, prefix="/users", tags=["users"])

# AI Service endpoints
api_router.include_router(agents_router, prefix="/agents", tags=["AI Agents"])
api_router.include_router(ai_chat_router)

# contacts
api_router.include_router(contacts_router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(timeline_router, prefix="/timeline", tags=["Timeline"])

# Conversations
api_router.include_router(conversations_router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(workflows_router)

# Note: Original conversations endpoint replaced with LangGraph-enhanced version

# TODO: Uncomment as endpoints are implemented
# api_router.include_router(files.router, prefix="/files", tags=["files"])
