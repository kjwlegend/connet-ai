"""Database related FastAPI dependencies."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import session as core_session
from app.modules.contacts.repository_impl import ContactRepository
from app.modules.ai.knowledge_bases.repository_impl import KnowledgeBaseRepository
from app.modules.ai.tools.repository import ToolRepositoryProtocol
from app.modules.ai.tools.repository_impl import ToolRepository
from app.modules.conversations.repository_impl import ConversationRepository
from app.modules.conversations.messages.repository_impl import MessageRepository
from app.modules.timeline.repository_impl import TimelineRepository
from app.modules.users.repository import UserRepository
from app.modules.users.repository_impl import UserRepositoryImpl


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session with managed transaction boundaries."""
    async with core_session() as db_session:
        yield db_session


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepositoryImpl(session)


async def get_contact_repository(
    session: AsyncSession = Depends(get_session),
) -> ContactRepository:
    return ContactRepository(session)


async def get_knowledge_repository(
    session: AsyncSession = Depends(get_session),
) -> KnowledgeBaseRepository:
    return KnowledgeBaseRepository(session)


async def get_tool_repository(
    session: AsyncSession = Depends(get_session),
) -> ToolRepositoryProtocol:
    return ToolRepository(session)


async def get_timeline_repository(
    session: AsyncSession = Depends(get_session),
) -> TimelineRepository:
    return TimelineRepository(session)


async def get_conversation_repository(
    session: AsyncSession = Depends(get_session),
) -> ConversationRepository:
    return ConversationRepository(session)


async def get_message_repository(
    session: AsyncSession = Depends(get_session),
) -> MessageRepository:
    return MessageRepository(session)


# Backwards compatibility alias
get_db_session = get_session


__all__ = [
    "get_session",
    "get_db_session",
    "get_user_repository",
    "get_contact_repository",
    "get_knowledge_repository",
    "get_tool_repository",
    "get_timeline_repository",
    "get_conversation_repository",
    "get_message_repository",
]
