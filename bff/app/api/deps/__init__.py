"""Convenience re-export for FastAPI dependencies."""

from .auth import get_current_active_user, get_current_user, security
from .cache import CacheManager, get_cache_manager
from .db import (
    get_contact_repository,
    get_db_session,
    get_knowledge_repository,
    get_session,
    get_tool_repository,
    get_user_repository,
)
from .pagination import get_pagination_params
from .rbac import require_permission, require_roles
from .services import (
    get_contact_service,
    get_conversation_service,
    get_supabase_auth_service,
    get_timeline_service,
    get_user_service,
)

__all__ = [
    "CacheManager",
    "get_cache_manager",
    "get_session",
    "get_db_session",
    "get_user_repository",
    "get_contact_repository",
    "get_knowledge_repository",
    "get_tool_repository",
    "get_user_service",
    "get_contact_service",
    "get_conversation_service",
    "get_supabase_auth_service",
    "get_timeline_service",
    "get_current_user",
    "get_current_active_user",
    "security",
    "require_permission",
    "require_roles",
    "get_pagination_params",
]
