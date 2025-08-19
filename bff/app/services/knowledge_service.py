"""
Knowledge Base Service

This module provides Knowledge Base-related business logic.
"""

from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime

from app.infrastructure.database.repositories.knowledge_repository_impl import (
    KnowledgeRepository,
    RAGDocumentRepository
)
from app.infrastructure.database.models.knowledge_model import (
    KnowledgeBaseModel,
    KnowledgeDocumentModel,
    RAGDocumentModel,
    RAGDocumentChunkModel
)
from app.schemas.knowledge import (
    KnowledgeBaseResponse,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentCreate,
    RAGDocumentResponse,
    RAGDocumentCreate
)
from app.services.base import BaseRepositoryService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class KnowledgeService(BaseRepositoryService):
    """Knowledge base service for managing knowledge bases and documents."""

    def __init__(
        self,
        knowledge_repository: KnowledgeRepository,
        rag_document_repository: RAGDocumentRepository
    ):
        self.knowledge_repository = knowledge_repository
        self.rag_document_repository = rag_document_repository

    async def create_knowledge_base(
        self,
        user_id: UUID,
        knowledge_data: KnowledgeBaseCreate
    ) -> KnowledgeBaseResponse:
        """Create a new knowledge base."""
        try:
            knowledge_base = KnowledgeBaseModel(
                name=knowledge_data.name,
                description=knowledge_data.description,
                knowledge_type=knowledge_data.knowledge_type,
                owner_id=user_id,
                created_by=user_id,
                metadata=knowledge_data.metadata,
                rag_config=knowledge_data.rag_config,
                tags=knowledge_data.tags or [],
                knowledge_metadata=knowledge_data.knowledge_metadata or {}
            )
            
            created_knowledge_base = await self.knowledge_repository.create_knowledge_base(knowledge_base)
            return self._knowledge_base_to_response(created_knowledge_base)
        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            raise

    async def get_knowledge_base(self, knowledge_base_id: UUID) -> Optional[KnowledgeBaseResponse]:
        """Get knowledge base by ID."""
        try:
            knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
            if knowledge_base:
                return self._knowledge_base_to_response(knowledge_base)
            return None
        except Exception as e:
            logger.error(f"Error getting knowledge base: {e}")
            raise

    async def get_user_knowledge_bases(
        self,
        user_id: UUID,
        knowledge_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[KnowledgeBaseResponse]:
        """Get user's knowledge bases with filtering."""
        try:
            knowledge_bases = await self.knowledge_repository.get_by_owner(user_id)
            
            # Apply filters
            if knowledge_type:
                knowledge_bases = [kb for kb in knowledge_bases if kb.knowledge_type == knowledge_type]
            
            if tags:
                knowledge_bases = [
                    kb for kb in knowledge_bases 
                    if any(tag in kb.tags for tag in tags)
                ]
            
            # Apply pagination
            knowledge_bases = knowledge_bases[skip:skip + limit]
            
            return [self._knowledge_base_to_response(kb) for kb in knowledge_bases]
        except Exception as e:
            logger.error(f"Error getting user knowledge bases: {e}")
            raise

    async def search_knowledge_bases(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[KnowledgeBaseResponse], int]:
        """Search knowledge bases."""
        try:
            knowledge_bases, total_count = await self.knowledge_repository.search_knowledge_bases(
                query=query,
                knowledge_type=knowledge_type,
                owner_id=owner_id,
                tags=tags,
                offset=skip,
                limit=limit
            )
            
            responses = [self._knowledge_base_to_response(kb) for kb in knowledge_bases]
            return responses, total_count
        except Exception as e:
            logger.error(f"Error searching knowledge bases: {e}")
            raise

    async def update_knowledge_base(
        self,
        knowledge_base_id: UUID,
        user_id: UUID,
        knowledge_data: KnowledgeBaseUpdate
    ) -> Optional[KnowledgeBaseResponse]:
        """Update knowledge base."""
        try:
            knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
            if not knowledge_base or knowledge_base.owner_id != user_id:
                return None
            
            # Update fields from knowledge_data
            for field, value in knowledge_data.model_dump(exclude_unset=True).items():
                setattr(knowledge_base, field, value)
            
            updated_knowledge_base = await self.knowledge_repository.update_knowledge_base(knowledge_base)
            if updated_knowledge_base:
                return self._knowledge_base_to_response(updated_knowledge_base)
            return None
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
            raise

    async def delete_knowledge_base(
        self,
        knowledge_base_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete knowledge base (soft delete)."""
        try:
            knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
            if not knowledge_base or knowledge_base.owner_id != user_id:
                return False
            
            return await self.knowledge_repository.delete_knowledge_base(knowledge_base_id)
        except Exception as e:
            logger.error(f"Error deleting knowledge base: {e}")
            raise

    # Knowledge Document Operations
    async def add_document_to_knowledge_base(
        self,
        knowledge_base_id: UUID,
        user_id: UUID,
        document_data: KnowledgeDocumentCreate
    ) -> KnowledgeDocumentResponse:
        """Add document to knowledge base."""
        try:
            # Verify ownership
            knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
            if not knowledge_base or knowledge_base.owner_id != user_id:
                raise ValueError("Knowledge base not found or access denied")
            
            document = KnowledgeDocumentModel(
                knowledge_base_id=knowledge_base_id,
                title=document_data.title,
                content=document_data.content,
                metadata=document_data.metadata
            )
            
            created_document = await self.knowledge_repository.add_document_to_knowledge_base(
                knowledge_base_id, document
            )
            return self._knowledge_document_to_response(created_document)
        except Exception as e:
            logger.error(f"Error adding document to knowledge base: {e}")
            raise

    async def get_knowledge_base_documents(
        self,
        knowledge_base_id: UUID,
        user_id: UUID
    ) -> List[KnowledgeDocumentResponse]:
        """Get all documents for a knowledge base."""
        try:
            # Verify access
            knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
            if not knowledge_base or knowledge_base.owner_id != user_id:
                return []
            
            documents = await self.knowledge_repository.get_knowledge_base_documents(knowledge_base_id)
            return [self._knowledge_document_to_response(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting knowledge base documents: {e}")
            raise

    async def remove_document_from_knowledge_base(
        self,
        knowledge_base_id: UUID,
        document_id: UUID,
        user_id: UUID
    ) -> bool:
        """Remove document from knowledge base."""
        try:
            # Verify ownership
            knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
            if not knowledge_base or knowledge_base.owner_id != user_id:
                return False
            
            return await self.knowledge_repository.remove_document_from_knowledge_base(
                knowledge_base_id, document_id
            )
        except Exception as e:
            logger.error(f"Error removing document from knowledge base: {e}")
            raise

    # RAG Document Basic Operations (CRUD only - processing handled by RAG service)
    async def create_rag_document(
        self,
        user_id: UUID,
        rag_document_data: RAGDocumentCreate
    ) -> RAGDocumentResponse:
        """Create a new RAG document (without processing)."""
        try:
            rag_document = RAGDocumentModel(
                name=rag_document_data.name,
                file_path=rag_document_data.file_path,
                file_type=rag_document_data.file_type,
                file_size=rag_document_data.file_size,
                content=rag_document_data.content,
                owner_id=user_id,
                visibility=rag_document_data.visibility or "private",
                shared_with=rag_document_data.shared_with or [],
                agent_metadata=rag_document_data.agent_metadata or {}
            )
            
            created_document = await self.rag_document_repository.create(rag_document)
            return self._rag_document_to_response(created_document)
        except Exception as e:
            logger.error(f"Error creating RAG document: {e}")
            raise

    async def get_user_rag_documents(
        self,
        user_id: UUID,
        file_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[RAGDocumentResponse]:
        """Get user's RAG documents."""
        try:
            documents = await self.rag_document_repository.get_by_owner(user_id)
            
            if file_type:
                documents = [doc for doc in documents if doc.file_type == file_type]
            
            documents = documents[skip:skip + limit]
            return [self._rag_document_to_response(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting user RAG documents: {e}")
            raise

    async def get_rag_document(
        self,
        document_id: UUID,
        user_id: UUID
    ) -> Optional[RAGDocumentResponse]:
        """Get a single RAG document."""
        try:
            document = await self.rag_document_repository.get_by_id(document_id)
            if not document or document.owner_id != user_id:
                return None
            return self._rag_document_to_response(document)
        except Exception as e:
            logger.error(f"Error getting RAG document: {e}")
            raise
            
    async def delete_rag_document(
        self,
        document_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a RAG document."""
        try:
            document = await self.rag_document_repository.get_by_id(document_id)
            if not document or document.owner_id != user_id:
                return False
            
            return await self.rag_document_repository.delete(document_id)
        except Exception as e:
            logger.error(f"Error deleting RAG document: {e}")
            raise

    def _knowledge_base_to_response(self, knowledge_base: KnowledgeBaseModel) -> KnowledgeBaseResponse:
        """Convert knowledge base model to response."""
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
            created_by=knowledge_base.created_by
        )

    def _knowledge_document_to_response(self, document: KnowledgeDocumentModel) -> KnowledgeDocumentResponse:
        """Convert knowledge document model to response."""
        return KnowledgeDocumentResponse(
            id=document.id,
            knowledge_base_id=document.knowledge_base_id,
            title=document.title,
            content=document.content,
            metadata=document.metadata,
            created_at=document.created_at,
            updated_at=document.updated_at,
            is_active=document.is_active
        )

    def _rag_document_to_response(self, document: RAGDocumentModel) -> RAGDocumentResponse:
        """Convert RAG document model to response."""
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
            processed_at=document.processed_at
        )