"""
Unit tests for ConversationService
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.conversation_service import ConversationService
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.infrastructure.database.models import ConversationModel, UserModel


class TestConversationService:
    """Test cases for ConversationService"""

    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        session = AsyncMock()
        return session

    @pytest.fixture
    def mock_cache_manager(self):
        """Mock cache manager"""
        cache = AsyncMock()
        cache.get.return_value = None
        return cache

    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        logger = MagicMock()
        return logger

    @pytest.fixture
    def conversation_service(self, mock_session, mock_cache_manager, mock_logger):
        """ConversationService instance with mocked dependencies"""
        service = ConversationService()
        service.session = mock_session
        service.cache_manager = mock_cache_manager
        service.logger = mock_logger
        return service

    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID"""
        return uuid4()

    @pytest.fixture
    def sample_conversation_data(self):
        """Sample conversation creation data"""
        return ConversationCreate(
            title="Test Conversation",
            conversation_type="chat",
            is_group=False,
            participants=[],
            initial_message="Hello, this is a test conversation"
        )

    @pytest.mark.asyncio
    async def test_create_conversation_success(
        self, 
        conversation_service, 
        sample_user_id, 
        sample_conversation_data,
        mock_session
    ):
        """Test successful conversation creation"""
        # Mock the database operations
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        # Mock the conversation model
        conversation_model = ConversationModel(
            id=uuid4(),
            title=sample_conversation_data.title,
            conversation_type=sample_conversation_data.conversation_type,
            is_group=sample_conversation_data.is_group,
            created_by=sample_user_id,
            participant_count=1,
            message_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Mock the get_conversation method to return the created conversation
        conversation_service.get_conversation = AsyncMock(return_value=conversation_model)

        # Call the method under test
        result = await conversation_service.create_conversation(
            user_id=sample_user_id,
            conversation_data=sample_conversation_data
        )

        # Assertions
        assert result is not None
        assert result.title == sample_conversation_data.title
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_get_user_conversations_with_filters(
        self,
        conversation_service,
        sample_user_id,
        mock_session
    ):
        """Test getting user conversations with various filters"""
        # Mock query results
        mock_results = []
        mock_session.execute.return_value.all.return_value = mock_results
        
        # Mock _get_conversation_participants method
        conversation_service._get_conversation_participants = AsyncMock(return_value=[])

        # Call the method under test
        result = await conversation_service.get_user_conversations(
            user_id=sample_user_id,
            skip=0,
            limit=10,
            include_archived=False,
            include_pinned_only=True,
            search="test"
        )

        # Assertions
        assert isinstance(result, list)
        mock_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_toggle_pin_conversation(
        self,
        conversation_service,
        sample_user_id,
        mock_session
    ):
        """Test pinning/unpinning a conversation"""
        conversation_id = uuid4()
        
        # Mock _get_or_create_user_settings method
        mock_settings = MagicMock()
        conversation_service._get_or_create_user_settings = AsyncMock(return_value=mock_settings)

        # Call the method under test
        await conversation_service.toggle_pin_conversation(
            conversation_id=conversation_id,
            user_id=sample_user_id,
            is_pinned=True,
            pin_order=1
        )

        # Assertions
        assert mock_settings.is_pinned == True
        assert mock_settings.pin_order == 1
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_export_conversation_markdown(
        self,
        conversation_service,
        sample_user_id,
        mock_session
    ):
        """Test exporting conversation to markdown"""
        conversation_id = uuid4()
        
        # Mock get_conversation method
        mock_conversation = MagicMock()
        mock_conversation.title = "Test Conversation"
        mock_conversation.created_at = datetime.utcnow()
        mock_conversation.participant_count = 2
        
        conversation_service.get_conversation = AsyncMock(return_value=mock_conversation)
        
        # Mock get_conversation_messages method
        mock_messages = []
        conversation_service.get_conversation_messages = AsyncMock(return_value=mock_messages)
        
        # Mock _update_export_count method
        conversation_service._update_export_count = AsyncMock()

        # Call the method under test
        result = await conversation_service.export_conversation(
            conversation_id=conversation_id,
            user_id=sample_user_id,
            export_format="markdown"
        )

        # Assertions
        assert result.export_format == "markdown"
        assert result.filename.endswith(".md")
        assert "# Test Conversation" in result.content

    @pytest.mark.asyncio
    async def test_conversation_access_denied(
        self,
        conversation_service,
        sample_user_id,
        mock_session
    ):
        """Test conversation access denied scenario"""
        from fastapi import HTTPException
        
        conversation_id = uuid4()
        
        # Mock no participant found (access denied)
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Call the method and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await conversation_service.get_conversation(
                conversation_id=conversation_id,
                user_id=sample_user_id
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_conversation(
        self,
        conversation_service,
        sample_user_id,
        mock_session
    ):
        """Test updating conversation details"""
        conversation_id = uuid4()
        update_data = ConversationUpdate(
            title="Updated Conversation Title",
            summary="This is a test summary"
        )
        
        # Mock conversation exists and user has access
        mock_conversation = MagicMock()
        conversation_service.get_conversation = AsyncMock(return_value=mock_conversation)

        # Call the method under test
        result = await conversation_service.update_conversation(
            conversation_id=conversation_id,
            user_id=sample_user_id,
            conversation_data=update_data
        )

        # Assertions
        assert result is not None
        conversation_service.get_conversation.assert_called()

    @pytest.mark.asyncio
    async def test_get_message_preview(
        self,
        conversation_service,
        mock_session
    ):
        """Test getting message preview"""
        message_id = uuid4()
        long_content = "A" * 150  # 150 characters
        
        # Mock database query result
        mock_session.execute.return_value.scalar_one_or_none.return_value = long_content

        # Call the method under test
        result = await conversation_service._get_message_preview(message_id)

        # Assertions
        assert len(result) <= 100
        assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_export_invalid_format(
        self,
        conversation_service,
        sample_user_id
    ):
        """Test export with invalid format"""
        from fastapi import HTTPException
        
        conversation_id = uuid4()

        # Call the method with invalid format and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await conversation_service.export_conversation(
                conversation_id=conversation_id,
                user_id=sample_user_id,
                export_format="invalid_format"
            )

        assert exc_info.value.status_code == 400