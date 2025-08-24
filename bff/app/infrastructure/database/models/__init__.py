"""Database models package."""

# Core models for LangGraph integration
from .user_model import UserModel
from .agent_model import AIAgentModel
from .contact_model import ContactModel
from .conversation_model import ConversationModel
from .conversation_participant_model import ConversationParticipantModel
from .conversation_memory_model import ConversationMemoryModel
from .message_model import MessageModel

# Optional models (commented out for now)
# from .agent_knowledge_base_model import AgentKnowledgeBaseModel
# from .conversation_topic_model import ConversationTopicModel
# from .conversation_user_setting_model import ConversationUserSettingModel
# from .file_model import FileModel
# from .file_permission_model import FilePermissionModel
# from .timeline_comment_model import TimelineCommentModel
# from .timeline_like_model import TimelineLikeModel
# from .timeline_post_model import TimelinePostModel
# from .user_invitation_model import UserInvitationModel
# from .user_llm_settings_model import UserLLMSettingsModel
# from .user_prompt_library_model import UserPromptLibraryModel
# from .user_registration_source_model import UserRegistrationSourceModel
# from .user_subscription_model import UserSubscriptionModel

# AI Service models - temporarily commented out
# from .ai_agent_model import (
#     AIAgentModel,
#     AIAgentVersionModel,
#     AIAgentKnowledgeBaseModel,
#     AIMemoryModel,
#     AIConversationSummaryModel,
#     AIToolModel,
#     AIToolExecutionModel,
#     AIWebhookModel,
#     AIWebhookTriggerModel,
#     AIRAGDocumentModel,
#     AIRAGDocumentChunkModel,
# )

__all__ = [
    # Core models for LangGraph integration
    "UserModel",
    "AIAgentModel",
    "ContactModel", 
    "ConversationModel",
    "ConversationParticipantModel",
    "ConversationMemoryModel",
    "MessageModel",
]