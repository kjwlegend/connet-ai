#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the database with required tables and indexes.
Run this script to set up the database schema for the BFF service.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlmodel import SQLModel

from app.config.settings import get_settings
from app.core.db import create_engine
from app.utils.logging import get_logger
from app.modules.users import models as user_models  # noqa: F401
from app.modules.users.invitations import models as user_invitation_models  # noqa: F401
from app.modules.users.registration import (
    models as user_registration_models,
)  # noqa: F401
from app.modules.users.subscriptions import (
    models as user_subscription_models,
)  # noqa: F401
from app.modules.users.llm_settings import models as user_llm_models  # noqa: F401
from app.modules.users.prompt_library import models as user_prompt_models  # noqa: F401
from app.modules.ai.agents import models as agent_models  # noqa: F401
from app.modules.ai.memory import models as memory_models  # noqa: F401
from app.modules.contacts import models as contact_models  # noqa: F401
from app.modules.ai.knowledge_bases import models as knowledge_base_models  # noqa: F401
from app.modules.ai.rag import models as rag_models  # noqa: F401
from app.modules.ai.tools import models as tool_models  # noqa: F401
from app.modules.conversations import models as conversation_models  # noqa: F401
from app.modules.conversations.messages import models as message_models  # noqa: F401
from app.modules.conversations.topics import models as topic_models  # noqa: F401
from app.modules.timeline import models as timeline_models  # noqa: F401
from app.modules.storage.files import models as file_models  # noqa: F401
from app.modules.ai.workflows import models as workflow_models  # noqa: F401

logger = get_logger(__name__)


async def create_tables():
    """Create database tables."""
    settings = get_settings()

    # Create async engine
    engine = create_engine(settings.database_url)

    try:
        async with engine.begin() as conn:
            # Drop all tables (be careful in production!)
            logger.info("Dropping existing tables...")
            await conn.run_sync(SQLModel.metadata.drop_all)

            # Create all tables
            logger.info("Creating database tables...")
            await conn.run_sync(SQLModel.metadata.create_all)

            # Create additional indexes
            await create_indexes(conn)

            logger.info("Database tables created successfully!")

    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
    finally:
        await engine.dispose()


async def create_indexes(conn):
    """Create additional database indexes."""
    indexes = [
        # User indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active ON users(email) WHERE is_active = true;",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_active ON users(username) WHERE is_active = true AND username IS NOT NULL;",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_auth_provider_external_id ON users(auth_provider, external_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_invitation_code ON users(invitation_code);",
        # Agent indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agents_name ON agents(name);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agents_type ON agents(agent_type);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agents_status ON agents(status);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agents_created_by ON agents(created_by);",
        # Conversation indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_created_by ON conversations(created_by);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_status ON conversations(status);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at);",
        # Message indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_created_at ON messages(created_at);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_message_type ON messages(message_type);",
        # File indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_uploaded_by ON files(uploaded_by);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_file_type ON files(file_type);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_created_at ON files(created_at);",
        # Contact indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_follower ON contacts(follower_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_following ON contacts(following_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_following_type ON contacts(following_type);",
        # Timeline indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_posts_author_id ON timeline_posts(author_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_posts_created_at ON timeline_posts(created_at);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_posts_visibility ON timeline_posts(visibility);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_comments_post_id ON timeline_comments(post_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_comments_created_at ON timeline_comments(created_at);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_comments_author_id ON timeline_comments(author_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_likes_target ON timeline_likes(target_id, target_type);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_likes_user ON timeline_likes(user_id);",
        # Vector search indexes (if using pgvector)
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_knowledge_base_embedding ON agent_knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);",
    ]

    logger.info("Creating additional indexes...")

    for index_sql in indexes:
        try:
            await conn.execute(text(index_sql))
            logger.info(
                f"Created index: {index_sql.split(' ')[5] if 'idx_' in index_sql else 'custom'}"
            )
        except Exception as e:
            # Log warning but don't fail the entire process
            logger.warning(f"Failed to create index: {e}")


async def create_initial_data():
    """Create initial data for the application."""
    settings = get_settings()
    engine = create_engine(settings.database_url)

    try:
        async with engine.begin() as conn:
            # Create system user (for system operations)
            system_user_sql = """
            INSERT INTO users (
                id,
                email,
                full_name,
                username,
                auth_provider,
                is_active,
                invitation_code,
                created_at,
                updated_at
            ) VALUES (
                'system',
                'system@connet.ai',
                'System User',
                'system',
                'system',
                true,
                'SYSTEM001',
                NOW(),
                NOW()
            ) ON CONFLICT (id) DO NOTHING;
            """

            await conn.execute(text(system_user_sql))
            logger.info("Created system user")

            # Create default admin agent
            admin_agent_sql = """
            INSERT INTO agents (
                id,
                name,
                display_name,
                description,
                agent_type,
                status,
                is_public,
                is_active,
                system_prompt,
                capabilities,
                personality_config,
                model_preferences,
                tags,
                created_by,
                created_at,
                updated_at
            ) VALUES (
                'admin-agent-001',
                'admin_assistant',
                'Admin Assistant',
                'Default administrative assistant for system operations',
                'assistant',
                'active',
                true,
                true,
                'You are the primary administrative assistant responsible for maintaining the platform.',
                '["user_management", "system_administration", "data_analysis"]',
                '{"tone": "professional"}',
                '{"provider": "openai", "model": "gpt-4", "temperature": 0.7}',
                '["administration", "operations"]',
                'system',
                NOW(),
                NOW()
            ) ON CONFLICT (id) DO NOTHING;
            """

            await conn.execute(text(admin_agent_sql))
            logger.info("Created admin agent")

    except Exception as e:
        logger.error(f"Failed to create initial data: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main function to initialize the database."""
    try:
        logger.info("Starting database initialization...")

        # Create tables
        await create_tables()

        # Create initial data
        await create_initial_data()

        logger.info("Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
