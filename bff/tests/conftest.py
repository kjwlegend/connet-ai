"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.modules.users.models import UserModel
from app.modules.ai.agents.models import AIAgentModel
from app.modules.contacts.models import ContactModel
from app.modules.conversations.models import (
    ConversationModel,
    ConversationParticipantModel,
)
from app.modules.conversations.messages.models import MessageModel
from app.infrastructure.cache.cache_manager import CacheManager


# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Database fixtures
@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


# Mock fixtures
@pytest.fixture
def mock_cache_manager():
    """Mock cache manager."""
    cache = MagicMock(spec=CacheManager)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.invalidate_pattern = AsyncMock()
    return cache


@pytest.fixture
def mock_logger():
    """Mock logger."""
    logger = MagicMock()
    return logger


# Sample data fixtures
@pytest.fixture
def sample_user_id():
    """Sample user ID."""
    return uuid4()


@pytest.fixture
def sample_agent_id():
    """Sample agent ID."""
    return uuid4()


@pytest.fixture
def sample_conversation_id():
    """Sample conversation ID."""
    return uuid4()


@pytest.fixture
def sample_user_data():
    """Sample user data."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "username": "testuser",
        "auth_provider": "local",
        "is_active": True,
        "bio": "This is a test user",
        "preferences": {
            "theme": "dark",
            "language": "en",
            "notifications": True
        }
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data."""
    return {
        "name": "test_agent",
        "display_name": "Test Agent",
        "description": "A test AI agent for automated testing",
        "agent_type": "chat",
        "capabilities": ["code_generation", "debugging"],
        "specialties": ["python", "javascript"],
        "model_provider": "openai",
        "model_name": "gpt-4",
        "model_config": {
            "temperature": 0.7,
            "max_tokens": 2048
        },
        "system_prompt": "You are a helpful test assistant.",
        "is_active": True,
        "is_public": True
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data."""
    return {
        "title": "Test Conversation",
        "conversation_type": "chat",
        "is_group": False,
        "status": "active",
        "settings": {
            "auto_archive_days": 30,
            "allow_agent_mentions": True,
            "notification_level": "all"
        }
    }


@pytest.fixture
def sample_message_data():
    """Sample message data."""
    return {
        "content": "This is a test message",
        "message_type": "text",
        "sender_type": "user",
        "mentioned_users": [],
        "mentioned_agents": [],
        "attachments": [],
        "reactions": {},
        "metadata": {}
    }


@pytest.fixture
def sample_timeline_post_data():
    """Sample timeline post data."""
    return {
        "title": "Test Post",
        "content": "This is a test timeline post",
        "content_type": "text",
        "author_type": "user",
        "visibility": "public",
        "category": "public_square",
        "tags": ["test", "sample"],
        "hashtags": ["testing"],
        "attachments": [],
        "media_urls": []
    }


@pytest.fixture
def sample_contact_data():
    """Sample contact data."""
    return {
        "following_type": "user",
        "relationship_type": "follow",
        "display_name": "Test Contact",
        "notes": "This is a test contact",
        "tags": ["friend", "colleague"],
        "is_favorite": False,
        "notification_level": "normal"
    }


# Authentication fixtures
@pytest.fixture
def sample_jwt_token():
    """Sample JWT token for testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


@pytest.fixture
def mock_authenticated_user(sample_user_id, sample_user_data):
    """Mock authenticated user."""
    user = UserModel(
        id=sample_user_id,
        **sample_user_data
    )
    return user


# Service fixtures
@pytest.fixture
def mock_conversation_service():
    """Mock conversation service."""
    service = MagicMock()
    service.get_user_conversations = AsyncMock(return_value=[])
    service.create_conversation = AsyncMock()
    service.get_conversation = AsyncMock()
    service.update_conversation = AsyncMock()
    service.delete_conversation = AsyncMock()
    service.toggle_pin_conversation = AsyncMock()
    service.export_conversation = AsyncMock()
    return service


@pytest.fixture
def mock_contact_service():
    """Mock contact service."""
    service = MagicMock()
    service.get_user_contacts = AsyncMock(return_value=[])
    service.add_contact = AsyncMock()
    service.remove_contact = AsyncMock()
    service.search_contacts = AsyncMock(return_value=[])
    service.toggle_favorite = AsyncMock()
    service.start_conversation_with_contact = AsyncMock()
    return service


@pytest.fixture
def mock_timeline_service():
    """Mock timeline service."""
    service = MagicMock()
    service.get_timeline_posts = AsyncMock(return_value=[])
    service.create_post = AsyncMock()
    service.get_post = AsyncMock()
    service.update_post = AsyncMock()
    service.delete_post = AsyncMock()
    service.toggle_like_post = AsyncMock()
    service.share_post = AsyncMock()
    service.get_post_comments = AsyncMock(return_value=[])
    service.create_comment = AsyncMock()
    service.delete_comment = AsyncMock()
    service.get_user_timeline_stats = AsyncMock(return_value={})
    service.toggle_pin_post = AsyncMock()
    return service


# Test data creation helpers
@pytest.fixture
async def create_test_user(test_session, sample_user_data):
    """Helper to create a test user in the database."""
    async def _create_user(**kwargs):
        data = {**sample_user_data, **kwargs}
        user = UserModel(**data)
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        return user
    return _create_user


@pytest.fixture
async def create_test_agent(test_session, sample_agent_data):
    """Helper to create a test agent in the database."""
    async def _create_agent(created_by=None, **kwargs):
        data = {**sample_agent_data, **kwargs}
        if created_by:
            data["created_by"] = created_by
        agent = AIAgentModel(**data)
        test_session.add(agent)
        await test_session.commit()
        await test_session.refresh(agent)
        return agent
    return _create_agent


@pytest.fixture
async def create_test_conversation(test_session, sample_conversation_data):
    """Helper to create a test conversation in the database."""
    async def _create_conversation(created_by, **kwargs):
        data = {**sample_conversation_data, **kwargs}
        data["created_by"] = created_by
        conversation = ConversationModel(**data)
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        return conversation
    return _create_conversation


# FastAPI test client fixtures
@pytest.fixture
def test_app():
    """Create test FastAPI application."""
    from app.main import create_app
    return create_app()


@pytest.fixture
def client(test_app):
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(test_app)


# Environment fixtures
@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    """Set test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")


# Async test markers
pytest.mark.asyncio = pytest.mark.asyncio


# Test categories
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "database: Database related tests")
    config.addinivalue_line("markers", "service: Service layer tests")
    config.addinivalue_line("markers", "model: Model tests")
