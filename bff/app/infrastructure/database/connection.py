"""
Database Connection Management

This module handles database connections using SQLModel and async SQLAlchemy.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Global variables for database engine and session factory
engine = None
async_session_factory = None


async def init_database() -> None:
    """Initialize database engine and session factory."""
    global engine, async_session_factory
    
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections after 1 hour
    )
    
    # Create session factory
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    logger.info("Database engine initialized")


async def create_tables() -> None:
    """Create all database tables."""
    global engine
    
    if not engine:
        await init_database()
    
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.infrastructure.database.models import (  # noqa: F401
            user_model,
            agent_model,
            conversation_model,
            message_model,
            file_model,
        )
        
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("Database tables created")


async def drop_tables() -> None:
    """Drop all database tables."""
    global engine
    
    if not engine:
        await init_database()
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    logger.info("Database tables dropped")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    global async_session_factory
    
    if not async_session_factory:
        await init_database()
    
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database() -> None:
    """Close database connections."""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")