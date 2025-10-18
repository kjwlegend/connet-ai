"""Business logic for knowledge bases and associated documents."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.modules.ai.knowledge_bases.models import (
    KnowledgeBaseModel,
    KnowledgeDocumentModel,
)
from app.modules.ai.knowledge_bases.repository import KnowledgeBaseRepositoryProtocol
from app.modules.ai.rag.models import RAGDocumentModel
from app.modules.ai.rag.repository import RAGDocumentRepositoryProtocol
from app.modules.ai.knowledge_bases.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
)
from app.modules.ai.rag.schemas import RAGDocumentCreate, RAGDocumentResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)


class KnowledgeService:
    """Coordinates CRUD operations for knowledge bases and their documents."""

    def __init__(
        self,
        knowledge_repository: KnowledgeBaseRepositoryProtocol,
        rag_document_repository: RAGDocumentRepositoryProtocol,
    ) -> None:
        self.knowledge_repository = knowledge_repository
        self.rag_document_repository = rag_document_repository

    async def create_knowledge_base(
        self, user_id: UUID, payload: KnowledgeBaseCreate
    ) -> KnowledgeBaseResponse:
        knowledge_base = KnowledgeBaseModel(
            name=payload.name,
            description=payload.description,
            knowledge_type=payload.knowledge_type,
            owner_id=user_id,
            created_by=user_id,
            metadata=payload.metadata,
            tags=payload.tags or [],
            rag_config=payload.rag_config,
            knowledge_metadata=payload.knowledge_metadata or {},
        )
        created = await self.knowledge_repository.create_knowledge_base(knowledge_base)
        return self._to_knowledge_response(created)

    async def get_knowledge_base(
        self, knowledge_base_id: UUID
    ) -> Optional[KnowledgeBaseResponse]:
        knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
        return self._to_knowledge_response(knowledge_base) if knowledge_base else None

    async def get_user_knowledge_bases(
        self,
        user_id: UUID,
        knowledge_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[KnowledgeBaseResponse]:
        knowledge_bases = await self.knowledge_repository.get_by_owner(user_id)
        if knowledge_type:
            knowledge_bases = [
                kb for kb in knowledge_bases if kb.knowledge_type == knowledge_type
            ]
        if tags:
            knowledge_bases = [
                kb for kb in knowledge_bases if any(tag in (kb.tags or []) for tag in tags)
            ]
        return [
            self._to_knowledge_response(kb)
            for kb in knowledge_bases[skip : skip + limit]
        ]

    async def search_knowledge_bases(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[KnowledgeBaseResponse], int]:
        records, total = await self.knowledge_repository.search_knowledge_bases(
            query=query,
            knowledge_type=knowledge_type,
            owner_id=owner_id,
            tags=tags,
            offset=skip,
            limit=limit,
        )
        return [self._to_knowledge_response(kb) for kb in records], total

    async def update_knowledge_base(
        self,
        knowledge_base_id: UUID,
        user_id: UUID,
        payload: KnowledgeBaseUpdate,
    ) -> Optional[KnowledgeBaseResponse]:
        knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
        if not knowledge_base or knowledge_base.owner_id != user_id:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(knowledge_base, field, value)
        updated = await self.knowledge_repository.update_knowledge_base(knowledge_base)
        return self._to_knowledge_response(updated) if updated else None

    async def delete_knowledge_base(
        self, knowledge_base_id: UUID, user_id: UUID
    ) -> bool:
        knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
        if not knowledge_base or knowledge_base.owner_id != user_id:
            return False
        return await self.knowledge_repository.delete_knowledge_base(knowledge_base_id)

    async def add_document_to_knowledge_base(
        self,
        knowledge_base_id: UUID,
        user_id: UUID,
        payload: KnowledgeDocumentCreate,
    ) -> KnowledgeDocumentResponse:
        kb = await self.knowledge_repository.get_by_id(knowledge_base_id)
        if not kb or kb.owner_id != user_id:
            raise ValueError("Knowledge base not found or access denied")
        document = KnowledgeDocumentModel(
            knowledge_base_id=knowledge_base_id,
            title=payload.title,
            content=payload.content,
            knowledge_document_metadata=payload.metadata,
        )
        created = await self.knowledge_repository.add_document_to_knowledge_base(
            knowledge_base_id, document
        )
        return self._to_document_response(created)

    async def get_knowledge_base_documents(
        self, knowledge_base_id: UUID, user_id: UUID
    ) -> List[KnowledgeDocumentResponse]:
        kb = await self.knowledge_repository.get_by_id(knowledge_base_id)
        if not kb or kb.owner_id != user_id:
            return []
        documents = await self.knowledge_repository.get_knowledge_base_documents(
            knowledge_base_id
        )
        return [self._to_document_response(doc) for doc in documents]

    async def remove_document_from_knowledge_base(
        self, knowledge_base_id: UUID, document_id: UUID, user_id: UUID
    ) -> bool:
        kb = await self.knowledge_repository.get_by_id(knowledge_base_id)
        if not kb or kb.owner_id != user_id:
            return False
        return await self.knowledge_repository.remove_document_from_knowledge_base(
            knowledge_base_id, document_id
        )

    # RAG document helpers -------------------------------------------------
    async def create_rag_document(
        self, user_id: UUID, payload: RAGDocumentCreate
    ) -> RAGDocumentResponse:
        document = RAGDocumentModel(
            name=payload.name,
            file_path=payload.file_path,
            file_type=payload.file_type,
            file_size=payload.file_size,
            content=payload.content,
            owner_id=user_id,
            visibility=payload.visibility or "private",
            shared_with=payload.shared_with or [],
            agent_metadata=payload.agent_metadata or {},
        )
        created = await self.rag_document_repository.create(document)
        return self._to_rag_document_response(created)

    async def get_user_rag_documents(
        self,
        user_id: UUID,
        file_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[RAGDocumentResponse]:
        documents = await self.rag_document_repository.get_by_owner(user_id)
        if file_type:
            documents = [doc for doc in documents if doc.file_type == file_type]
        return [
            self._to_rag_document_response(doc)
            for doc in documents[skip : skip + limit]
        ]

    async def get_rag_document(
        self, document_id: UUID, user_id: UUID
    ) -> Optional[RAGDocumentResponse]:
        document = await self.rag_document_repository.get_by_id(document_id)
        if not document or document.owner_id != user_id:
            return None
        return self._to_rag_document_response(document)

    async def delete_rag_document(
        self, document_id: UUID, user_id: UUID
    ) -> bool:
        document = await self.rag_document_repository.get_by_id(document_id)
        if not document or document.owner_id != user_id:
            return False
        return await self.rag_document_repository.delete(document_id)

    # ------------------------------------------------------------------
    def _to_knowledge_response(
        self, knowledge_base: KnowledgeBaseModel
    ) -> KnowledgeBaseResponse:
        return KnowledgeBaseResponse(
            id=knowledge_base.id,
            name=knowledge_base.name,
            description=knowledge_base.description,
            knowledge_type=knowledge_base.knowledge_type,
            owner_id=knowledge_base.owner_id,
            metadata=knowledge_base.metadata,
            document_ids=knowledge_base.document_ids,
            rag_config=knowledge_base.rag_config,
            is_active=knowledge_base.is_active,
            tags=knowledge_base.tags,
            knowledge_metadata=knowledge_base.knowledge_metadata,
            created_at=knowledge_base.created_at,
            updated_at=knowledge_base.updated_at,
            created_by=knowledge_base.created_by,
        )

    def _to_document_response(
        self, document: KnowledgeDocumentModel
    ) -> KnowledgeDocumentResponse:
        return KnowledgeDocumentResponse(
            id=document.id,
            knowledge_base_id=document.knowledge_base_id,
            title=document.title,
            content=document.content,
            metadata=getattr(document, "metadata", document.knowledge_document_metadata),
            created_at=document.created_at,
            updated_at=document.updated_at,
            is_active=document.is_active,
        )

    def _to_rag_document_response(self, document: RAGDocumentModel) -> RAGDocumentResponse:
        return RAGDocumentResponse(
            id=document.id,
            name=document.name,
            file_path=document.file_path,
            file_type=document.file_type,
            file_size=document.file_size,
            content=document.content,
            agent_metadata=document.agent_metadata,
            processing_status=document.processing_status,
            chunk_count=document.chunk_count,
            quality_score=document.quality_score,
            owner_id=document.owner_id,
            visibility=document.visibility,
            shared_with=document.shared_with,
            created_at=document.created_at,
            updated_at=document.updated_at,
            processed_at=document.processed_at,
        )


__all__ = ["KnowledgeService"]
