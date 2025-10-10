"""Backward-compatible shim for contact schemas."""

from app.modules.contacts.schemas import (
    ContactBase,
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactSearchResponse,
    ContactKnowledgeResponse,
    ContactToolResponse,
    QRCodeResponse,
    ConversationStartResponse,
)

__all__ = [
    "ContactBase",
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "ContactSearchResponse",
    "ContactKnowledgeResponse",
    "ContactToolResponse",
    "QRCodeResponse",
    "ConversationStartResponse",
]
