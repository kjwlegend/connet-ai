"""Contacts module public interface."""

from .models import ContactModel, ContactKnowledgeLink, ContactToolLink, EntityType
from .repository import ContactRepositoryProtocol as ContactRepositoryInterface
from .repository_impl import ContactRepository
from .schemas import (
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
from .service import ContactService
from .router import router

__all__ = [
    "ContactModel",
    "ContactKnowledgeLink",
    "ContactToolLink",
    "EntityType",
    "ContactRepositoryInterface",
    "ContactRepository",
    "ContactService",
    "ContactBase",
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "ContactSearchResponse",
    "ContactKnowledgeResponse",
    "ContactToolResponse",
    "QRCodeResponse",
    "ConversationStartResponse",
    "router",
]
