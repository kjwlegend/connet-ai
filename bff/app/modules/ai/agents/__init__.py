"""Agents module public interface."""

from .models import (
    AIAgentModel,
    AIAgentVersionModel
)
from .repository import AgentRepositoryProtocol
from .repository_impl import AgentRepository, AgentVersionRepository
from .schemas import (
    AIAgentCreate,
    AIAgentUpdate,
    AIAgentResponse,
    AIAgentListResponse,
    PaginationParams,
    AIErrorResponse,
    PersonalityProfile,
    ModelPreferences,
)
from .service import AIAgentService
from .router import router

__all__ = [
    "AIAgentModel",
    "AIAgentVersionModel",

    "AgentRepositoryProtocol",
    "AgentRepository",
    "AgentVersionRepository",
    "AIAgentService",
    "AIAgentCreate",
    "AIAgentUpdate",
    "AIAgentResponse",
    "AIAgentListResponse",
    "PaginationParams",
    "AIErrorResponse",
    "PersonalityProfile",
    "ModelPreferences",
    "router",
]
