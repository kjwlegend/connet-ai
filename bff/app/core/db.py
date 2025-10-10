"""Centralised database engine and session management utilities."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

engine: Optional[AsyncEngine] = None
async_session_factory: Optional[sessionmaker] = None


def create_engine(database_url: Optional[str] = None) -> AsyncEngine:
    """Create a standalone async engine using the configured settings."""

    settings = get_settings()
    return create_async_engine(
        database_url or settings.database_url,
        echo=settings.debug,
        future=True,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


async def init_database() -> None:
    """Initialise the global async engine and session factory."""

    global engine, async_session_factory

    if engine and async_session_factory:
        return

    settings = get_settings()
    engine = create_engine(settings.database_url)

    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info("Database engine initialised")


async def create_tables() -> None:
    """Create all SQLModel tables that are currently registered."""

    if not engine:
        await init_database()

    assert engine is not None

    async with engine.begin() as conn:
        # Import model modules so SQLModel metadata is populated.
        from app.modules.agents import models as agent_models  # noqa: F401
        from app.modules.contacts import models as contact_models  # noqa: F401
        from app.modules.conversations import models as conversation_models  # noqa: F401
        from app.modules.conversations.messages import models as message_models  # noqa: F401
        from app.modules.storage.files import models as file_models  # noqa: F401
        from app.modules.ai.workflows import models as workflow_models  # noqa: F401
        from app.modules.ai.knowledge_bases import models as knowledge_models  # noqa: F401
        from app.modules.ai.rag import models as rag_models  # noqa: F401

        await conn.run_sync(SQLModel.metadata.create_all)

    logger.info("Database tables created")


async def drop_tables() -> None:
    """Drop all SQLModel tables."""

    if not engine:
        await init_database()

    assert engine is not None

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    logger.info("Database tables dropped")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session with managed commit/rollback semantics."""

    if not async_session_factory:
        await init_database()

    assert async_session_factory is not None

    async with async_session_factory() as db_session:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise
        finally:
            await db_session.close()


@asynccontextmanager
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Alias maintained for backwards compatibility."""

    async with get_session() as db_session:
        yield db_session


def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Legacy helper returning the same context manager as ``get_session``."""

    return get_session()


__all__ = [
    "engine",
    "async_session_factory",
    "create_engine",
    "init_database",
    "create_tables",
    "drop_tables",
    "get_session",
    "session",
    "get_async_session",
]
