"""
Alembic environment setup for Connet.AI BFF Service

This configuration supports the new contact-scoped architecture where:
- Knowledge bases and tools are managed at the contact level
- Agents serve as templates without direct tool/knowledge attachments
- Users can have different configurations per agent contact

Key Features:
- Full SQLModel support with proper metadata
- Async database connections
- Comprehensive model imports for all new architecture components
- Support for JSONB fields and enum types
- Robust error handling and filtering
"""

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

# Import all database models for Alembic autogenerate support

# User models
from app.modules.users.models import UserModel
from app.modules.users.invitations.models import UserInvitationModel
from app.modules.users.registration.models import UserRegistrationSourceModel
from app.modules.users.subscriptions.models import UserSubscriptionModel
from app.modules.users.llm_settings.models import UserLLMSettingsModel
from app.modules.users.prompt_library.models import UserPromptLibraryModel

# Agent models
from app.modules.agents.models import (
    AIAgentModel,
    AIAgentVersionModel,
)
from app.modules.ai.memory.models import (
    AIMemoryModel,
    AIConversationSummaryModel,
)

# Contact models (new architecture - contact-scoped)
from app.modules.contacts.models import (
    ContactModel,
    ContactKnowledgeLink,
    ContactToolLink,
)

# Knowledge models (new - for contact-scoped knowledge)
from app.modules.ai.knowledge_bases.models import (
    KnowledgeBaseModel,
    KnowledgeDocumentModel,
)
from app.modules.ai.rag.models import (
    RAGDocumentModel,
    RAGDocumentChunkModel,
)

# Tool models (new - for contact-scoped tools)
from app.modules.ai.tools.models import (
    ToolModel,
    WebhookModel,
    WebhookTriggerModel,
)

# Conversation models
from app.modules.conversations.models import ConversationModel
from app.modules.conversations.models import ConversationParticipantModel
from app.modules.conversations.topics.models import ConversationTopicModel
from app.modules.conversations.models import ConversationUserSettingModel
from app.modules.conversations.messages.models import MessageModel

# Timeline/Social models
from app.modules.timeline.models import (
    TimelineCommentModel,
    TimelineLikeModel,
    TimelinePostModel,
)

# File models
from app.modules.storage.files.models import FileModel, FilePermissionModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = SQLModel.metadata


def include_name(name, type_, parent_names):
    """
    Filter function to control which objects are included in migrations.
    This helps manage complex schemas and avoid unnecessary migrations.
    """
    # Include all tables by default
    if type_ == "table":
        return True
    
    # Include all indexes, but skip some system indexes if needed
    if type_ == "index":
        # Skip SQLAlchemy internal indexes
        if name and name.startswith("ix_"):
            return True
        return True
    
    # Include foreign key constraints
    if type_ == "foreign_key_constraint":
        return True
    
    # Include unique constraints
    if type_ == "unique_constraint":
        return True
    
    # Include check constraints for enums
    if type_ == "check_constraint":
        return True
    
    return True


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
            project_id = supabase_url.replace("https://", "").replace(
                ".supabase.co", ""
            )
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
        # Include schemas for better table organization
        include_schemas=True,
        # Render item for SQLModel/Pydantic enum handling
        render_as_batch=True,
        # Use include_name filter for better control
        include_name=include_name,
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
        # Include schemas for better table organization
        include_schemas=True,
        # Render item for SQLModel/Pydantic enum handling
        render_as_batch=True,
        # Use include_name filter for better control
        include_name=include_name,
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
