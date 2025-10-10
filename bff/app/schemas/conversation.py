"""Backward-compatible import for conversation schemas."""

from app.modules.conversations.schemas import (
    ConversationBase,
    ConversationCreate,
    ConversationExportResponse,
    ConversationParticipantResponse,
    ConversationPinRequest,
    ConversationResponse,
    ConversationUpdate,
)
from app.modules.conversations.messages.schemas import (
    MessageCreate,
    MessageResponse,
)

__all__ = [
    "ConversationBase",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationPinRequest",
    "ConversationParticipantResponse",
    "ConversationResponse",
    "ConversationExportResponse",
    "MessageCreate",
    "MessageResponse",
]
