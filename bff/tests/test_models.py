"""
Unit tests for database models
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.infrastructure.database.models import (
    UserModel,
    ConversationModel,
    ConversationUserSettingModel,
    MessageModel,
    ContactModel,
    TimelinePostModel,
    UserSubscriptionModel,
    UserLLMSettingsModel,
    UserPromptLibraryModel
)


class TestUserModel:
    """Test cases for UserModel"""

    def test_user_model_creation(self):
        """Test creating a new user model"""
        user = UserModel(
            email="test@example.com",
            full_name="Test User",
            username="testuser",
            auth_provider="local",
            is_active=True
        )
        
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.username == "testuser"
        assert user.auth_provider == "local"
        assert user.is_active == True
        assert user.online_status == "offline"
        assert user.invitation_count == 0
        assert user.total_conversations == 0

    def test_user_model_defaults(self):
        """Test user model default values"""
        user = UserModel(
            email="test@example.com",
            full_name="Test User"
        )
        
        assert user.auth_provider == "local"
        assert user.is_active == True
        assert user.online_status == "offline"
        assert user.qr_code_enabled == True
        assert user.invitation_count == 0
        assert user.invitation_rewards_earned == 0
        assert user.total_conversations == 0
        assert user.total_messages == 0
        assert user.total_ai_interactions == 0
        assert user.total_posts_created == 0

    def test_user_model_invitation_system(self):
        """Test user invitation system fields"""
        inviter_id = uuid4()
        
        user = UserModel(
            email="invited@example.com",
            full_name="Invited User",
            invitation_code="ABC123",
            invited_by_code="XYZ789",
            invited_by_user_id=inviter_id,
            registration_source="web",
            registration_channel="invite"
        )
        
        assert user.invitation_code == "ABC123"
        assert user.invited_by_code == "XYZ789"
        assert user.invited_by_user_id == inviter_id
        assert user.registration_source == "web"
        assert user.registration_channel == "invite"


class TestConversationModel:
    """Test cases for ConversationModel"""

    def test_conversation_model_creation(self):
        """Test creating a new conversation model"""
        user_id = uuid4()
        
        conversation = ConversationModel(
            title="Test Conversation",
            conversation_type="chat",
            is_group=False,
            created_by=user_id
        )
        
        assert conversation.title == "Test Conversation"
        assert conversation.conversation_type == "chat"
        assert conversation.is_group == False
        assert conversation.created_by == user_id
        assert conversation.status == "active"
        assert conversation.message_count == 0
        assert conversation.participant_count == 0
        assert conversation.export_count == 0
        assert conversation.is_pinned == False

    def test_conversation_model_defaults(self):
        """Test conversation model default values"""
        user_id = uuid4()
        
        conversation = ConversationModel(
            title="Default Conversation",
            created_by=user_id
        )
        
        assert conversation.conversation_type == "chat"
        assert conversation.status == "active"
        assert conversation.is_group == False
        assert conversation.is_pinned == False
        assert conversation.message_count == 0
        assert conversation.participant_count == 0
        assert conversation.topic_count == 0
        assert conversation.export_count == 0

    def test_conversation_model_with_settings(self):
        """Test conversation model with custom settings"""
        user_id = uuid4()
        settings = {
            "auto_archive_days": 30,
            "allow_agent_mentions": True,
            "notification_level": "important"
        }
        
        conversation = ConversationModel(
            title="Configured Conversation",
            created_by=user_id,
            settings=settings,
            is_group=True,
            participant_count=5
        )
        
        assert conversation.settings == settings
        assert conversation.is_group == True
        assert conversation.participant_count == 5


class TestConversationUserSettingModel:
    """Test cases for ConversationUserSettingModel"""

    def test_conversation_user_setting_creation(self):
        """Test creating conversation user settings"""
        conversation_id = uuid4()
        user_id = uuid4()
        
        settings = ConversationUserSettingModel(
            conversation_id=conversation_id,
            user_id=user_id,
            is_pinned=True,
            pin_order=1,
            notifications_enabled=True,
            unread_count=5
        )
        
        assert settings.conversation_id == conversation_id
        assert settings.user_id == user_id
        assert settings.is_pinned == True
        assert settings.pin_order == 1
        assert settings.notifications_enabled == True
        assert settings.unread_count == 5

    def test_conversation_user_setting_defaults(self):
        """Test conversation user settings default values"""
        conversation_id = uuid4()
        user_id = uuid4()
        
        settings = ConversationUserSettingModel(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        assert settings.is_pinned == False
        assert settings.pin_order == 0
        assert settings.notifications_enabled == True
        assert settings.notification_level == "all"
        assert settings.unread_count == 0
        assert settings.is_archived == False


class TestContactModel:
    """Test cases for ContactModel"""

    def test_contact_model_creation(self):
        """Test creating a contact relationship"""
        follower_id = uuid4()
        following_id = uuid4()
        
        contact = ContactModel(
            follower_id=follower_id,
            following_id=following_id,
            following_type="user",
            relationship_type="follow",
            display_name="My Friend",
            is_favorite=True
        )
        
        assert contact.follower_id == follower_id
        assert contact.following_id == following_id
        assert contact.following_type == "user"
        assert contact.relationship_type == "follow"
        assert contact.display_name == "My Friend"
        assert contact.is_favorite == True

    def test_contact_model_defaults(self):
        """Test contact model default values"""
        follower_id = uuid4()
        following_id = uuid4()
        
        contact = ContactModel(
            follower_id=follower_id,
            following_id=following_id,
            following_type="agent"
        )
        
        assert contact.relationship_type == "follow"
        assert contact.is_favorite == False
        assert contact.is_muted == False
        assert contact.is_blocked == False
        assert contact.online_status == "unknown"
        assert contact.notification_level == "normal"
        assert contact.qr_code_shared == False

    def test_contact_model_agent_relationship(self):
        """Test contact relationship with AI agent"""
        follower_id = uuid4()
        agent_id = uuid4()
        
        contact = ContactModel(
            follower_id=follower_id,
            following_id=agent_id,
            following_type="agent",
            display_name="Code Assistant",
            tags=["coding", "helpful"],
            online_status="online",
            shared_via="qr_code"
        )
        
        assert contact.following_type == "agent"
        assert contact.display_name == "Code Assistant"
        assert contact.tags == ["coding", "helpful"]
        assert contact.online_status == "online"
        assert contact.shared_via == "qr_code"


class TestUserSubscriptionModel:
    """Test cases for UserSubscriptionModel"""

    def test_subscription_model_creation(self):
        """Test creating a user subscription"""
        user_id = uuid4()
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        subscription = UserSubscriptionModel(
            user_id=user_id,
            plan_type="premium",
            plan_name="Premium Plan",
            plan_price=19.99,
            current_period_start=start_date,
            current_period_end=end_date,
            monthly_message_limit=10000,
            features_enabled={
                "ai_agents": True,
                "file_upload": True,
                "custom_prompts": True
            }
        )
        
        assert subscription.user_id == user_id
        assert subscription.plan_type == "premium"
        assert subscription.plan_name == "Premium Plan"
        assert subscription.plan_price == 19.99
        assert subscription.monthly_message_limit == 10000
        assert subscription.features_enabled["ai_agents"] == True

    def test_subscription_model_defaults(self):
        """Test subscription model default values"""
        user_id = uuid4()
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        subscription = UserSubscriptionModel(
            user_id=user_id,
            plan_type="free",
            plan_name="Free Plan",
            plan_price=0.00,
            current_period_start=start_date,
            current_period_end=end_date
        )
        
        assert subscription.status == "active"
        assert subscription.billing_cycle == "monthly"
        assert subscription.monthly_message_limit == 1000
        assert subscription.monthly_ai_token_limit == 50000
        assert subscription.max_file_storage_gb == 1
        assert subscription.cancel_at_period_end == False


class TestUserLLMSettingsModel:
    """Test cases for UserLLMSettingsModel"""

    def test_llm_settings_creation(self):
        """Test creating user LLM settings"""
        user_id = uuid4()
        
        settings = UserLLMSettingsModel(
            user_id=user_id,
            default_provider="openai",
            default_model="gpt-4",
            chat_model="gpt-3.5-turbo",
            coding_model="gpt-4",
            default_temperature=0.8,
            streaming_enabled=True
        )
        
        assert settings.user_id == user_id
        assert settings.default_provider == "openai"
        assert settings.default_model == "gpt-4"
        assert settings.chat_model == "gpt-3.5-turbo"
        assert settings.coding_model == "gpt-4"
        assert settings.default_temperature == 0.8
        assert settings.streaming_enabled == True

    def test_llm_settings_defaults(self):
        """Test LLM settings default values"""
        user_id = uuid4()
        
        settings = UserLLMSettingsModel(user_id=user_id)
        
        assert settings.default_provider == "openai"
        assert settings.default_model == "gpt-3.5-turbo"
        assert settings.default_temperature == 0.7
        assert settings.default_max_tokens == 2048
        assert settings.default_top_p == 1.0
        assert settings.auto_select_model == True
        assert settings.cost_optimization_enabled == True
        assert settings.streaming_enabled == True
        assert settings.response_format_preference == "markdown"
        assert settings.content_filtering_level == "moderate"


class TestUserPromptLibraryModel:
    """Test cases for UserPromptLibraryModel"""

    def test_prompt_library_creation(self):
        """Test creating a custom prompt"""
        user_id = uuid4()
        
        prompt = UserPromptLibraryModel(
            user_id=user_id,
            title="Code Review Helper",
            description="Helps review code for bugs and best practices",
            prompt_text="Please review this code: {code}",
            category="coding",
            tags=["code-review", "debugging"],
            is_favorite=True,
            variables=[
                {"name": "code", "description": "The code to review", "required": True}
            ],
            preferred_models=["gpt-4", "claude-3-opus"]
        )
        
        assert prompt.user_id == user_id
        assert prompt.title == "Code Review Helper"
        assert prompt.category == "coding"
        assert prompt.tags == ["code-review", "debugging"]
        assert prompt.is_favorite == True
        assert len(prompt.variables) == 1
        assert prompt.variables[0]["name"] == "code"
        assert len(prompt.preferred_models) == 2

    def test_prompt_library_defaults(self):
        """Test prompt library default values"""
        user_id = uuid4()
        
        prompt = UserPromptLibraryModel(
            user_id=user_id,
            title="Test Prompt",
            prompt_text="This is a test prompt"
        )
        
        assert prompt.category == "general"
        assert prompt.tags == []
        assert prompt.use_count == 0
        assert prompt.is_public == False
        assert prompt.is_favorite == False
        assert prompt.variables == []
        assert prompt.preferred_models == []


class TestTimelinePostModel:
    """Test cases for TimelinePostModel"""

    def test_timeline_post_creation(self):
        """Test creating a timeline post"""
        author_id = uuid4()
        
        post = TimelinePostModel(
            author_id=author_id,
            author_type="user",
            title="My First Post",
            content="This is my first post on the timeline!",
            content_type="text",
            visibility="public",
            category="public_square",
            tags=["introduction", "first-post"],
            hashtags=["hello", "newuser"]
        )
        
        assert post.author_id == author_id
        assert post.author_type == "user"
        assert post.title == "My First Post"
        assert post.content_type == "text"
        assert post.visibility == "public"
        assert post.category == "public_square"
        assert post.tags == ["introduction", "first-post"]
        assert post.hashtags == ["hello", "newuser"]

    def test_timeline_post_defaults(self):
        """Test timeline post default values"""
        author_id = uuid4()
        
        post = TimelinePostModel(
            author_id=author_id,
            author_type="agent",
            content="AI-generated insight about the project"
        )
        
        assert post.content_type == "text"
        assert post.visibility == "public"
        assert post.category == "public"
        assert post.like_count == 0
        assert post.comment_count == 0
        assert post.share_count == 0
        assert post.view_count == 0
        assert post.attachments == []
        assert post.media_urls == []
        assert post.tags == []
        assert post.hashtags == []
        assert post.mentioned_users == []
        assert post.mentioned_agents == []
        assert post.status == "published"
        assert post.is_pinned == False
        assert post.is_featured == False

    def test_timeline_post_ai_agent_fields(self):
        """Test timeline post with AI agent specific fields"""
        agent_id = uuid4()
        
        post = TimelinePostModel(
            author_id=agent_id,
            author_type="agent",
            content="I just completed a complex coding task!",
            content_type="achievement",
            agent_mood="excited",
            generated_context={
                "task_type": "coding",
                "completion_time": "2.5 hours",
                "satisfaction_level": "high"
            }
        )
        
        assert post.author_type == "agent"
        assert post.content_type == "achievement"
        assert post.agent_mood == "excited"
        assert post.generated_context["task_type"] == "coding"
        assert post.generated_context["satisfaction_level"] == "high"