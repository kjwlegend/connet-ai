"""Backward-compatible shim for AI agent schemas."""

from app.modules.agents.schemas import (
    AIAgentCreate,
    AIAgentUpdate,
    AIAgentResponse,
    AIAgentListResponse,
    PaginationParams,
    AIErrorResponse,
    PersonalityProfile,
    ModelPreferences,
)

__all__ = [
    "AIAgentCreate",
    "AIAgentUpdate",
    "AIAgentResponse",
    "AIAgentListResponse",
    "PaginationParams",
    "AIErrorResponse",
    "PersonalityProfile",
    "ModelPreferences",
]
