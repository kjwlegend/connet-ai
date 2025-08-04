"""Simplified Alembic environment setup."""

import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Import models directly without going through app initialization
from sqlmodel import SQLModel

# Import all database models directly
from app.infrastructure.database.models.user_model import User
from app.infrastructure.database.models.user_invitation_model import UserInvitation
from app.infrastructure.database.models.user_registration_source_model import UserRegistrationSource
from app.infrastructure.database.models.agent_model import Agent
from app.infrastructure.database.models.agent_knowledge_base_model import AgentKnowledgeBase
from app.infrastructure.database.models.conversation_model import Conversation
from app.infrastructure.database.models.conversation_participant_model import ConversationParticipant
from app.infrastructure.database.models.conversation_topic_model import ConversationTopic
from app.infrastructure.database.models.message_model import Message
from app.infrastructure.database.models.contact_model import Contact
from app.infrastructure.database.models.timeline_post_model import TimelinePost
from app.infrastructure.database.models.timeline_comment_model import TimelineComment
from app.infrastructure.database.models.timeline_like_model import TimelineLike
from app.infrastructure.database.models.file_model import File
from app.infrastructure.database.models.file_permission_model import FilePermission

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = SQLModel.metadata

def get_database_url():
    """Get database URL from environment."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get from environment variable
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback to Supabase URL if DATABASE_URL not set
        supabase_url = os.getenv("SUPABASE_URL", "")
        if supabase_url:
            # Extract connection info from Supabase URL
            # Format: https://xxxx.supabase.co
            project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
            db_url = f"postgresql://postgres:[PASSWORD]@db.{project_id}.supabase.co:5432/postgres"
        else:
            raise ValueError("DATABASE_URL or SUPABASE_URL must be set")
    
    # Convert async URL to sync URL for Alembic
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with database connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section)
    db_url = get_database_url()
    configuration["sqlalchemy.url"] = db_url

    connectable = create_async_engine(
        db_url.replace("postgresql://", "postgresql+asyncpg://"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()