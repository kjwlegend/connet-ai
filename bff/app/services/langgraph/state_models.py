"""Compatibility shim for workflow state models."""

from app.modules.ai.workflows.state_models import (
    ContactInfo,
    ContactResponse,
    ConversationState,
    MessageState,
    NodeExecutionResult,
    WorkflowConfig,
    WorkflowType,
)

__all__ = [
    "ContactInfo",
    "ContactResponse",
    "ConversationState",
    "MessageState",
    "NodeExecutionResult",
    "WorkflowConfig",
    "WorkflowType",
]
