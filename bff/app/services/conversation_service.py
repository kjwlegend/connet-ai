"""Backward-compatible shim for conversation service."""

from app.modules.conversations.service import ConversationService

__all__ = ["ConversationService"]
