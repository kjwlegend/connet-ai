"""Repository protocol for RAG documents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.modules.ai.rag.models import RAGDocumentChunkModel, RAGDocumentModel


class RAGDocumentRepositoryProtocol(ABC):
    """Abstract persistence operations for RAG documents and chunks."""

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Optional[RAGDocumentModel]:
        ...

    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> List[RAGDocumentModel]:
        ...

    @abstractmethod
    async def search_documents(
        self,
        query: str,
        file_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[RAGDocumentModel], int]:
        ...

    @abstractmethod
    async def create(self, document: RAGDocumentModel) -> RAGDocumentModel:
        ...

    @abstractmethod
    async def delete(self, document_id: UUID) -> bool:
        ...

    # Chunk operations ----------------------------------------------------
    @abstractmethod
    async def get_document_chunks(
        self, document_id: UUID
    ) -> List[RAGDocumentChunkModel]:
        ...

    @abstractmethod
    async def add_document_chunk(
        self, chunk: RAGDocumentChunkModel
    ) -> RAGDocumentChunkModel:
        ...

    @abstractmethod
    async def create_chunks(
        self, chunk_data: List[Dict[str, Any]]
    ) -> List[RAGDocumentChunkModel]:
        ...

    @abstractmethod
    async def get_chunks_by_ids(
        self, chunk_ids: List[UUID]
    ) -> List[RAGDocumentChunkModel]:
        ...

    @abstractmethod
    async def update_processing_status(
        self,
        document_id: UUID,
        status: str,
        chunk_count: Optional[int] = None,
        quality_score: Optional[float] = None,
    ) -> None:
        ...


__all__ = ["RAGDocumentRepositoryProtocol"]
