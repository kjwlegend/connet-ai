"""AI RAG repository implementation for document processing and search."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.ai_agent_model import (
    AIRAGDocumentModel,
    AIRAGDocumentChunkModel
)
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.schemas.ai import DocumentCreate, PaginationParams


class AIRAGDocumentRepositoryImpl(BaseRepository[AIRAGDocumentModel, UUID]):
    """AI RAG Document repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIRAGDocumentModel)
    
    async def create_document(self, document_data: DocumentCreate, user_id: UUID) -> AIRAGDocumentModel:
        """Create a new document"""
        
        document = AIRAGDocumentModel(
            name=document_data.name,
            file_type=document_data.file_type,
            file_size=len(document_data.content.encode('utf-8')),
            content=document_data.content,
            metadata=document_data.metadata,
            processing_status="pending",
            owner_id=user_id,
            visibility=document_data.visibility,
            shared_with=document_data.shared_with,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        
        return document
    
    async def get_document_by_id(
        self, 
        document_id: UUID, 
        user_id: Optional[UUID] = None
    ) -> Optional[AIRAGDocumentModel]:
        """Get document by ID with access control"""
        
        stmt = select(AIRAGDocumentModel).where(AIRAGDocumentModel.id == document_id)
        
        # Apply access control if user_id is provided
        if user_id:
            stmt = stmt.where(
                or_(
                    AIRAGDocumentModel.owner_id == user_id,
                    AIRAGDocumentModel.visibility == "public",
                    and_(
                        AIRAGDocumentModel.visibility == "shared",
                        func.jsonb_exists(AIRAGDocumentModel.shared_with, str(user_id))
                    )
                )
            )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_documents(
        self,
        user_id: Optional[UUID] = None,
        file_type: Optional[str] = None,
        processing_status: Optional[str] = None,
        search: Optional[str] = None,
        visibility: Optional[str] = None,
        pagination: Optional[PaginationParams] = None
    ) -> tuple[List[AIRAGDocumentModel], int]:
        """List documents with filtering and pagination"""
        
        # Build base query with access control
        stmt = select(AIRAGDocumentModel)
        conditions = []
        
        # Access control
        if user_id:
            conditions.append(
                or_(
                    AIRAGDocumentModel.owner_id == user_id,
                    AIRAGDocumentModel.visibility == "public",
                    and_(
                        AIRAGDocumentModel.visibility == "shared",
                        func.jsonb_exists(AIRAGDocumentModel.shared_with, str(user_id))
                    )
                )
            )
        
        # Apply filters
        if file_type:
            conditions.append(AIRAGDocumentModel.file_type == file_type)
        if processing_status:
            conditions.append(AIRAGDocumentModel.processing_status == processing_status)
        if visibility:
            conditions.append(AIRAGDocumentModel.visibility == visibility)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    AIRAGDocumentModel.name.ilike(search_pattern),
                    AIRAGDocumentModel.content.ilike(search_pattern)
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply sorting
        if pagination and pagination.sort_by:
            sort_column = getattr(AIRAGDocumentModel, pagination.sort_by, AIRAGDocumentModel.created_at)
            if pagination.sort_order == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(AIRAGDocumentModel.created_at.desc())
        
        # Apply pagination
        if pagination:
            offset = (pagination.page - 1) * pagination.size
            stmt = stmt.offset(offset).limit(pagination.size)
        
        result = await self.session.execute(stmt)
        documents = result.scalars().all()
        
        return list(documents), total
    
    async def update_processing_status(
        self,
        document_id: UUID,
        status: str,
        chunk_count: Optional[int] = None,
        quality_score: Optional[float] = None
    ):
        """Update document processing status"""
        
        update_data = {
            'processing_status': status,
            'updated_at': datetime.utcnow()
        }
        
        if status == "completed":
            update_data['processed_at'] = datetime.utcnow()
        if chunk_count is not None:
            update_data['chunk_count'] = chunk_count
        if quality_score is not None:
            update_data['quality_score'] = quality_score
        
        stmt = update(AIRAGDocumentModel).where(
            AIRAGDocumentModel.id == document_id
        ).values(**update_data)
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def get_documents_for_processing(self, limit: int = 10) -> List[AIRAGDocumentModel]:
        """Get documents pending processing"""
        
        stmt = select(AIRAGDocumentModel).where(
            AIRAGDocumentModel.processing_status == "pending"
        ).order_by(AIRAGDocumentModel.created_at.asc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        """Delete document (only by owner)"""
        
        # Check ownership
        stmt = select(AIRAGDocumentModel).where(
            and_(
                AIRAGDocumentModel.id == document_id,
                AIRAGDocumentModel.owner_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            return False
        
        # Delete document (cascading will handle chunks)
        stmt = delete(AIRAGDocumentModel).where(AIRAGDocumentModel.id == document_id)
        await self.session.execute(stmt)
        await self.session.commit()
        
        return True
    
    async def share_document(self, document_id: UUID, user_id: UUID, shared_with: List[UUID]) -> bool:
        """Share document with specified users"""
        
        # Check ownership
        stmt = select(AIRAGDocumentModel).where(
            and_(
                AIRAGDocumentModel.id == document_id,
                AIRAGDocumentModel.owner_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            return False
        
        # Update sharing settings
        stmt = update(AIRAGDocumentModel).where(
            AIRAGDocumentModel.id == document_id
        ).values(
            shared_with=shared_with,
            visibility="shared" if shared_with else "private",
            updated_at=datetime.utcnow()
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
        
        return True


class AIRAGDocumentChunkRepositoryImpl(BaseRepository[AIRAGDocumentChunkModel, UUID]):
    """AI RAG Document Chunk repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIRAGDocumentChunkModel)
    
    async def create_chunks(self, chunks_data: List[Dict[str, Any]]) -> List[AIRAGDocumentChunkModel]:
        """Create multiple document chunks"""
        
        chunks = []
        for chunk_data in chunks_data:
            chunk = AIRAGDocumentChunkModel(**chunk_data)
            chunks.append(chunk)
            self.session.add(chunk)
        
        await self.session.commit()
        
        # Refresh all chunks to get their IDs
        for chunk in chunks:
            await self.session.refresh(chunk)
        
        return chunks
    
    async def get_document_chunks(
        self,
        document_id: UUID,
        limit: Optional[int] = None
    ) -> List[AIRAGDocumentChunkModel]:
        """Get chunks for a document"""
        
        stmt = select(AIRAGDocumentChunkModel).where(
            AIRAGDocumentChunkModel.document_id == document_id
        ).order_by(AIRAGDocumentChunkModel.chunk_index.asc())
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_chunk_by_id(self, chunk_id: UUID) -> Optional[AIRAGDocumentChunkModel]:
        """Get chunk by ID"""
        
        stmt = select(AIRAGDocumentChunkModel).where(AIRAGDocumentChunkModel.id == chunk_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_chunks_by_text(
        self,
        query: str,
        document_ids: Optional[List[UUID]] = None,
        limit: int = 10
    ) -> List[AIRAGDocumentChunkModel]:
        """Basic text search in chunks (for fallback when vector search unavailable)"""
        
        search_pattern = f"%{query}%"
        conditions = [AIRAGDocumentChunkModel.content.ilike(search_pattern)]
        
        if document_ids:
            conditions.append(AIRAGDocumentChunkModel.document_id.in_(document_ids))
        
        stmt = select(AIRAGDocumentChunkModel).where(and_(*conditions)).order_by(
            AIRAGDocumentChunkModel.quality_score.desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_chunks_by_ids(self, chunk_ids: List[UUID]) -> List[AIRAGDocumentChunkModel]:
        """Get multiple chunks by IDs"""
        
        stmt = select(AIRAGDocumentChunkModel).where(
            AIRAGDocumentChunkModel.id.in_(chunk_ids)
        ).order_by(AIRAGDocumentChunkModel.document_id, AIRAGDocumentChunkModel.chunk_index)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_chunk_quality(self, chunk_id: UUID, quality_score: float):
        """Update chunk quality score"""
        
        stmt = update(AIRAGDocumentChunkModel).where(
            AIRAGDocumentChunkModel.id == chunk_id
        ).values(quality_score=quality_score)
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def delete_document_chunks(self, document_id: UUID):
        """Delete all chunks for a document"""
        
        stmt = delete(AIRAGDocumentChunkModel).where(
            AIRAGDocumentChunkModel.document_id == document_id
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount
    
    async def get_chunks_with_embedding_model(
        self,
        embedding_model: str,
        limit: Optional[int] = None
    ) -> List[AIRAGDocumentChunkModel]:
        """Get chunks processed with specific embedding model"""
        
        stmt = select(AIRAGDocumentChunkModel).where(
            AIRAGDocumentChunkModel.embedding_model == embedding_model
        ).order_by(AIRAGDocumentChunkModel.created_at.asc())
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_chunk_statistics(self, document_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get chunk statistics"""
        
        conditions = []
        if document_id:
            conditions.append(AIRAGDocumentChunkModel.document_id == document_id)
        
        base_query = select(AIRAGDocumentChunkModel)
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Total chunks
        total_result = await self.session.execute(
            select(func.count(AIRAGDocumentChunkModel.id)).select_from(base_query.subquery())
        )
        total_chunks = total_result.scalar()
        
        # Average quality score
        avg_quality_result = await self.session.execute(
            select(func.avg(AIRAGDocumentChunkModel.quality_score)).select_from(base_query.subquery())
        )
        avg_quality = avg_quality_result.scalar() or 0.0
        
        # Average token count
        avg_tokens_result = await self.session.execute(
            select(func.avg(AIRAGDocumentChunkModel.token_count)).select_from(base_query.subquery())
        )
        avg_tokens = avg_tokens_result.scalar() or 0.0
        
        # Embedding model distribution
        model_stats = await self.session.execute(
            select(
                AIRAGDocumentChunkModel.embedding_model,
                func.count(AIRAGDocumentChunkModel.id).label('count')
            ).select_from(base_query.subquery()).group_by(AIRAGDocumentChunkModel.embedding_model)
        )
        
        return {
            'total_chunks': total_chunks,
            'average_quality_score': float(avg_quality),
            'average_token_count': float(avg_tokens),
            'embedding_models': {row.embedding_model: row.count for row in model_stats}
        }