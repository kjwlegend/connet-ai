"""Service layer dependencies used by FastAPI routers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.cache import CacheManager, get_cache_manager
from app.api.deps.db import (
    get_contact_repository,
    get_knowledge_repository,
    get_session,
    get_timeline_repository,
    get_tool_repository,
    get_user_repository,
)
from app.modules.timeline.service import TimelineService
from app.modules.contacts.repository_impl import ContactRepository
from app.modules.ai.knowledge_bases.repository_impl import KnowledgeRepository
from app.modules.ai.tools.repository import ToolRepositoryProtocol
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
from app.modules.contacts.service import ContactService
from app.modules.agents.service import AIAgentService
from app.modules.conversations.repository_impl import ConversationRepository
from app.modules.conversations.messages.repository_impl import MessageRepository
from app.modules.conversations.messages.service import MessageService
from app.modules.conversations.service import ConversationService
from app.modules.timeline.repository_impl import TimelineRepository
from app.modules.auth.service import SupabaseAuthService


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    cache_manager: CacheManager = Depends(get_cache_manager),
) -> UserService:
    return UserService(user_repository=user_repository, cache_manager=cache_manager)


async def get_contact_service(
    contact_repo: ContactRepository = Depends(get_contact_repository),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repository),
    tool_repo: ToolRepositoryProtocol = Depends(get_tool_repository),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
) -> ContactService:
    ai_agent_service = AIAgentService(session)
    return ContactService(
        contact_repository=contact_repo,
        knowledge_repository=knowledge_repo,
        tool_repository=tool_repo,
        user_service=user_service,
        ai_agent_service=ai_agent_service,
    )


async def get_supabase_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> SupabaseAuthService:
    return SupabaseAuthService(user_repository=user_repository)


async def get_timeline_service(
    timeline_repository: TimelineRepository = Depends(get_timeline_repository),
) -> TimelineService:
    return TimelineService(repository=timeline_repository)


async def get_conversation_service(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
) -> ConversationService:
    conversation_repository = ConversationRepository(session)
    message_repository = MessageRepository(session)
    agent_service = AIAgentService(session)
    message_service = MessageService(
        message_repository=message_repository,
        conversation_repository=conversation_repository,
        user_service=user_service,
        agent_service=agent_service,
    )
    return ConversationService(
        conversation_repository=conversation_repository,
        message_service=message_service,
        user_service=user_service,
        agent_service=agent_service,
    )


__all__ = [
    "get_contact_service",
    "get_supabase_auth_service",
    "get_timeline_service",
    "get_conversation_service",
    "get_user_service",
]
