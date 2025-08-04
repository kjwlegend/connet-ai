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
from app.infrastructure.database.connection import create_engine
from app.infrastructure.database.models import *  # Import all models
from app.utils.logging import get_logger

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
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agents_created_by ON agents(created_by_user_id);",
        
        # Conversation indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_created_by ON conversations(created_by_user_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_status ON conversations(status);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at);",
        
        # Message indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_created_at ON messages(created_at);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_message_type ON messages(message_type);",
        
        # File indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_uploaded_by ON files(uploaded_by_user_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_file_type ON files(file_type);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_created_at ON files(created_at);",
        
        # Contact indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_user_id ON contacts(user_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_contact_user_id ON contacts(contact_user_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_status ON contacts(status);",
        
        # Timeline indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_posts_author_id ON timeline_posts(author_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_posts_created_at ON timeline_posts(created_at);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_posts_visibility ON timeline_posts(visibility);",
        
        # Vector search indexes (if using pgvector)
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_knowledge_base_embedding ON agent_knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);",
    ]
    
    logger.info("Creating additional indexes...")
    
    for index_sql in indexes:
        try:
            await conn.execute(text(index_sql))
            logger.info(f"Created index: {index_sql.split(' ')[5] if 'idx_' in index_sql else 'custom'}")
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
                description,
                agent_type,
                status,
                capabilities,
                configuration,
                created_by_user_id,
                created_at,
                updated_at
            ) VALUES (
                'admin-agent-001',
                'Admin Assistant',
                'Default administrative assistant for system operations',
                'assistant',
                'active',
                '["user_management", "system_administration", "data_analysis"]',
                '{"model": "gpt-4", "max_tokens": 4000, "temperature": 0.7}',
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