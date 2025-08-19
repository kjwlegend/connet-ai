"""
Knowledge Base Repository Implementation

This module provides the implementation of the Knowledge Base repository.
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlmodel import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

# Removed BaseRepositoryInterface import to avoid MRO conflicts
from app.infrastructure.database.models.knowledge_model import (
    KnowledgeBaseModel,
    KnowledgeDocumentModel,
    RAGDocumentModel,
    RAGDocumentChunkModel
)
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)


class KnowledgeRepository(BaseRepository[KnowledgeBaseModel]):
    """Knowledge Base Repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, KnowledgeBaseModel)
        
    async def get_by_name(self, name: str) -> Optional[KnowledgeBaseModel]:
        """Get knowledge base by name."""
        try:
            statement = select(KnowledgeBaseModel).where(KnowledgeBaseModel.name == name)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting knowledge base by name {name}: {e}")
            raise
            
    async def get_by_owner(self, owner_id: UUID) -> List[KnowledgeBaseModel]:
        """Get knowledge bases by owner."""
        try:
            statement = select(KnowledgeBaseModel).where(KnowledgeBaseModel.owner_id == owner_id)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting knowledge bases for owner {owner_id}: {e}")
            raise

    async def search_knowledge_bases(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[KnowledgeBaseModel], int]:
        """Search knowledge bases."""
        try:
            conditions = []
            
            # Text search
            search_condition = or_(
                KnowledgeBaseModel.name.ilike(f"%{query}%"),
                KnowledgeBaseModel.description.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
            
            # Filter by type
            if knowledge_type:
                conditions.append(KnowledgeBaseModel.knowledge_type == knowledge_type)
                
            # Filter by owner
            if owner_id:
                conditions.append(KnowledgeBaseModel.owner_id == owner_id)
                
            # Filter by tags
            if tags:
                # PostgreSQL JSON array contains check
                for tag in tags:
                    conditions.append(func.json_array_contains(KnowledgeBaseModel.tags, tag))
            
            # Only active knowledge bases
            conditions.append(KnowledgeBaseModel.is_active == True)
            
            stmt = select(KnowledgeBaseModel).where(and_(*conditions)).offset(offset).limit(limit)
            result = await self.session.exec(stmt)
            knowledge_bases = result.all()
            
            # Get total count
            count_stmt = select(func.count(KnowledgeBaseModel.id)).where(and_(*conditions))
            count_result = await self.session.exec(count_stmt)
            total_count = count_result.scalar()
            
            return knowledge_bases, total_count
        except Exception as e:
            logger.error(f"Error searching knowledge bases: {e}")
            raise

    async def create_knowledge_base(self, knowledge_base: KnowledgeBaseModel) -> KnowledgeBaseModel:
        """Create a new knowledge base."""
        try:
            self.session.add(knowledge_base)
            await self.session.commit()
            await self.session.refresh(knowledge_base)
            return knowledge_base
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating knowledge base: {e}")
            raise

    async def update_knowledge_base(self, knowledge_base: KnowledgeBaseModel) -> KnowledgeBaseModel:
        """Update a knowledge base."""
        try:
            stmt = select(KnowledgeBaseModel).where(KnowledgeBaseModel.id == knowledge_base.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return None
            
            for field, value in knowledge_base.model_dump(exclude_unset=True).items():
                if field != 'id':
                    setattr(model, field, value)
            
            model.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(model)
            
            logger.info(f"Knowledge base updated successfully: {knowledge_base.id}")
            return model
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update knowledge base {knowledge_base.id}: {e}")
            raise

    async def delete_knowledge_base(self, knowledge_base_id: UUID) -> bool:
        """Delete a knowledge base (soft delete)."""
        try:
            stmt = select(KnowledgeBaseModel).where(KnowledgeBaseModel.id == knowledge_base_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return False
            
            model.is_active = False
            model.updated_at = datetime.utcnow()
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to delete knowledge base {knowledge_base_id}: {e}")
            return False

    # Knowledge Document Operations
    async def add_document_to_knowledge_base(
        self,
        knowledge_base_id: UUID,
        document: KnowledgeDocumentModel
    ) -> KnowledgeDocumentModel:
        """Add document to knowledge base."""
        try:
            document.knowledge_base_id = knowledge_base_id
            self.session.add(document)
            await self.session.commit()
            await self.session.refresh(document)
            return document
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding document to knowledge base: {e}")
            raise

    async def get_knowledge_base_documents(
        self,
        knowledge_base_id: UUID
    ) -> List[KnowledgeDocumentModel]:
        """Get all documents for a knowledge base."""
        try:
            stmt = select(KnowledgeDocumentModel).where(
                and_(
                    KnowledgeDocumentModel.knowledge_base_id == knowledge_base_id,
                    KnowledgeDocumentModel.is_active == True
                )
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting knowledge base documents: {e}")
            raise

    async def remove_document_from_knowledge_base(
        self,
        knowledge_base_id: UUID,
        document_id: UUID
    ) -> bool:
        """Remove document from knowledge base (soft delete)."""
        try:
            stmt = select(KnowledgeDocumentModel).where(
                and_(
                    KnowledgeDocumentModel.id == document_id,
                    KnowledgeDocumentModel.knowledge_base_id == knowledge_base_id
                )
            )
            result = await self.session.execute(stmt)
            document = result.scalar_one_or_none()
            if document:
                document.is_active = False
                document.updated_at = datetime.now(datetime.utc)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error removing document from knowledge base: {e}")
            raise


class RAGDocumentRepository(BaseRepository[RAGDocumentModel]):
    """RAG Document Repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, RAGDocumentModel)

    async def get_by_owner(self, owner_id: UUID) -> List[RAGDocumentModel]:
        """Get RAG documents by owner."""
        try:
            statement = select(RAGDocumentModel).where(RAGDocumentModel.owner_id == owner_id)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting RAG documents for owner {owner_id}: {e}")
            raise

    async def search_documents(
        self,
        query: str,
        file_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[RAGDocumentModel], int]:
        """Search RAG documents."""
        try:
            conditions = []
            
            # Text search
            search_condition = or_(
                RAGDocumentModel.name.ilike(f"%{query}%"),
                RAGDocumentModel.content.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
            
            # Filter by file type
            if file_type:
                conditions.append(RAGDocumentModel.file_type == file_type)
                
            # Filter by owner
            if owner_id:
                conditions.append(RAGDocumentModel.owner_id == owner_id)
            
            stmt = select(RAGDocumentModel).where(and_(*conditions)).offset(offset).limit(limit)
            result = await self.session.exec(stmt)
            documents = result.all()
            
            # Get total count
            count_stmt = select(func.count(RAGDocumentModel.id)).where(and_(*conditions))
            count_result = await self.session.exec(count_stmt)
            total_count = count_result.scalar()
            
            return documents, total_count
        except Exception as e:
            logger.error(f"Error searching RAG documents: {e}")
            raise

    async def get_document_chunks(self, document_id: UUID) -> List[RAGDocumentChunkModel]:
        """Get all chunks for a RAG document."""
        try:
            stmt = select(RAGDocumentChunkModel).where(
                RAGDocumentChunkModel.document_id == document_id
            ).order_by(RAGDocumentChunkModel.chunk_index)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting document chunks: {e}")
            raise

    async def add_document_chunk(self, chunk: RAGDocumentChunkModel) -> RAGDocumentChunkModel:
        """Add chunk to RAG document."""
        try:
            self.session.add(chunk)
            await self.session.commit()
            await self.session.refresh(chunk)
            return chunk
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding document chunk: {e}")
            raise