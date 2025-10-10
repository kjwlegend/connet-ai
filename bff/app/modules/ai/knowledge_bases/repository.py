"""Repository protocols for knowledge bases and documents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from app.modules.ai.knowledge_bases.models import (
    KnowledgeBaseModel,
    KnowledgeDocumentModel,
)


class KnowledgeBaseRepositoryProtocol(ABC):
    """Abstract persistence layer for knowledge bases."""

    @abstractmethod
    async def get_by_id(self, knowledge_base_id: UUID) -> Optional[KnowledgeBaseModel]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[KnowledgeBaseModel]:
        ...

    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> List[KnowledgeBaseModel]:
        ...

    @abstractmethod
    async def search_knowledge_bases(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[KnowledgeBaseModel], int]:
        ...

    @abstractmethod
    async def create_knowledge_base(
        self, knowledge_base: KnowledgeBaseModel
    ) -> KnowledgeBaseModel:
        ...

    @abstractmethod
    async def update_knowledge_base(
        self, knowledge_base: KnowledgeBaseModel
    ) -> Optional[KnowledgeBaseModel]:
        ...

    @abstractmethod
    async def delete_knowledge_base(self, knowledge_base_id: UUID) -> bool:
        ...

    # Document operations -------------------------------------------------
    @abstractmethod
    async def add_document_to_knowledge_base(
        self, knowledge_base_id: UUID, document: KnowledgeDocumentModel
    ) -> KnowledgeDocumentModel:
        ...

    @abstractmethod
    async def get_knowledge_base_documents(
        self, knowledge_base_id: UUID
    ) -> List[KnowledgeDocumentModel]:
        ...

    @abstractmethod
    async def remove_document_from_knowledge_base(
        self, knowledge_base_id: UUID, document_id: UUID
    ) -> bool:
        ...


KnowledgeBaseRepository = KnowledgeBaseRepositoryProtocol

__all__ = ["KnowledgeBaseRepositoryProtocol", "KnowledgeBaseRepository"]
