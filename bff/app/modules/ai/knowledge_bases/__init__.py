"""AI knowledge base slice exports."""

from app.modules.ai.knowledge_bases.models import (
    KnowledgeBaseModel,
    KnowledgeDocumentModel,
)
from app.modules.ai.knowledge_bases.repository import KnowledgeBaseRepositoryProtocol
from app.modules.ai.knowledge_bases.repository_impl import KnowledgeBaseRepository
from app.modules.ai.knowledge_bases.service import KnowledgeService

__all__ = [
    "KnowledgeBaseModel",
    "KnowledgeDocumentModel",
    "KnowledgeBaseRepositoryProtocol",
    "KnowledgeBaseRepository",
    "KnowledgeService",
]
