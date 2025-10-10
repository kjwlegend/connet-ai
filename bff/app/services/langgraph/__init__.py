"""Compatibility package for legacy LangGraph imports."""

from app.modules.ai.workflows import (
    WorkflowEngine,
    ContactInstanceManager,
    MentionParser,
)

__all__ = [
    "WorkflowEngine",
    "ContactInstanceManager",
    "MentionParser",
]
