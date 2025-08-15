"""AI Memory repository implementation for three-tier memory system."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.ai_agent_model import (
    AIMemoryModel,
    AIConversationSummaryModel
)
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.schemas.ai import MemoryCreate, MemoryType, MemoryCategory


class AIMemoryRepositoryImpl(BaseRepository[AIMemoryModel]):
    """AI Memory repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIMemoryModel)
    
    async def create_memory(self, memory_data: MemoryCreate, user_id: UUID) -> AIMemoryModel:
        """Create a new memory entry"""
        
        memory = AIMemoryModel(
            conversation_id=memory_data.conversation_id,
            agent_id=memory_data.agent_id,
            user_id=user_id,
            memory_type=memory_data.memory_type.value,
            memory_category=memory_data.memory_category.value,
            content=memory_data.content,
            metadata=memory_data.metadata,
            importance_score=memory_data.importance_score,
            confidence_score=memory_data.confidence_score,
            emotional_valence=memory_data.emotional_valence,
            created_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow(),
            access_count=0
        )
        
        # Set expiration based on memory type
        if memory_data.memory_type == MemoryType.SHORT_TERM:
            memory.expires_at = datetime.utcnow() + timedelta(hours=2)
        elif memory_data.memory_type == MemoryType.MEDIUM_TERM:
            memory.expires_at = datetime.utcnow() + timedelta(days=30)
        # Long-term memories don't expire
        
        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)
        
        return memory
    
    async def get_memories_by_conversation(
        self, 
        conversation_id: UUID, 
        memory_type: Optional[MemoryType] = None,
        limit: Optional[int] = None
    ) -> List[AIMemoryModel]:
        """Get memories for a conversation"""
        
        conditions = [
            AIMemoryModel.conversation_id == conversation_id,
            or_(AIMemoryModel.expires_at.is_(None), AIMemoryModel.expires_at > datetime.utcnow())
        ]
        
        if memory_type:
            conditions.append(AIMemoryModel.memory_type == memory_type.value)
        
        stmt = select(AIMemoryModel).where(and_(*conditions)).order_by(
            AIMemoryModel.importance_score.desc(),
            AIMemoryModel.last_accessed_at.desc()
        )
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_memories_by_user(
        self,
        user_id: UUID,
        memory_type: Optional[MemoryType] = None,
        memory_category: Optional[MemoryCategory] = None,
        limit: Optional[int] = None
    ) -> List[AIMemoryModel]:
        """Get memories for a user"""
        
        conditions = [
            AIMemoryModel.user_id == user_id,
            or_(AIMemoryModel.expires_at.is_(None), AIMemoryModel.expires_at > datetime.utcnow())
        ]
        
        if memory_type:
            conditions.append(AIMemoryModel.memory_type == memory_type.value)
        if memory_category:
            conditions.append(AIMemoryModel.memory_category == memory_category.value)
        
        stmt = select(AIMemoryModel).where(and_(*conditions)).order_by(
            AIMemoryModel.importance_score.desc(),
            AIMemoryModel.created_at.desc()
        )
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        memory_type: Optional[MemoryType] = None,
        conversation_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[AIMemoryModel]:
        """Search memories by content (basic text search)"""
        
        search_pattern = f"%{query}%"
        conditions = [
            AIMemoryModel.user_id == user_id,
            AIMemoryModel.content.ilike(search_pattern),
            or_(AIMemoryModel.expires_at.is_(None), AIMemoryModel.expires_at > datetime.utcnow())
        ]
        
        if memory_type:
            conditions.append(AIMemoryModel.memory_type == memory_type.value)
        if conversation_id:
            conditions.append(AIMemoryModel.conversation_id == conversation_id)
        
        stmt = select(AIMemoryModel).where(and_(*conditions)).order_by(
            AIMemoryModel.importance_score.desc(),
            AIMemoryModel.confidence_score.desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_memory_access(self, memory_id: UUID):
        """Update memory access statistics"""
        
        stmt = update(AIMemoryModel).where(
            AIMemoryModel.id == memory_id
        ).values(
            last_accessed_at=datetime.utcnow(),
            access_count=AIMemoryModel.access_count + 1
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def get_expired_memories(self, batch_size: int = 100) -> List[AIMemoryModel]:
        """Get expired memories for cleanup"""
        
        stmt = select(AIMemoryModel).where(
            and_(
                AIMemoryModel.expires_at.is_not(None),
                AIMemoryModel.expires_at < datetime.utcnow()
            )
        ).limit(batch_size)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_expired_memories(self) -> int:
        """Delete expired memories"""
        
        stmt = delete(AIMemoryModel).where(
            and_(
                AIMemoryModel.expires_at.is_not(None),
                AIMemoryModel.expires_at < datetime.utcnow()
            )
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
    
    async def get_memory_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get memory usage statistics for a user"""
        
        # Total memories by type
        type_stats = await self.session.execute(
            select(
                AIMemoryModel.memory_type,
                func.count(AIMemoryModel.id).label('count')
            ).where(
                and_(
                    AIMemoryModel.user_id == user_id,
                    or_(AIMemoryModel.expires_at.is_(None), AIMemoryModel.expires_at > datetime.utcnow())
                )
            ).group_by(AIMemoryModel.memory_type)
        )
        
        # Category distribution
        category_stats = await self.session.execute(
            select(
                AIMemoryModel.memory_category,
                func.count(AIMemoryModel.id).label('count')
            ).where(
                and_(
                    AIMemoryModel.user_id == user_id,
                    or_(AIMemoryModel.expires_at.is_(None), AIMemoryModel.expires_at > datetime.utcnow())
                )
            ).group_by(AIMemoryModel.memory_category)
        )
        
        # Average importance and confidence scores
        avg_stats = await self.session.execute(
            select(
                func.avg(AIMemoryModel.importance_score).label('avg_importance'),
                func.avg(AIMemoryModel.confidence_score).label('avg_confidence'),
                func.count(AIMemoryModel.id).label('total_memories')
            ).where(
                and_(
                    AIMemoryModel.user_id == user_id,
                    or_(AIMemoryModel.expires_at.is_(None), AIMemoryModel.expires_at > datetime.utcnow())
                )
            )
        )
        
        return {
            'by_type': {row.memory_type: row.count for row in type_stats},
            'by_category': {row.memory_category: row.count for row in category_stats},
            'averages': avg_stats.one()._asdict()
        }


class AIConversationSummaryRepositoryImpl(BaseRepository[AIConversationSummaryModel]):
    """AI Conversation Summary repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIConversationSummaryModel)
    
    async def create_summary(self, summary_data: Dict[str, Any]) -> AIConversationSummaryModel:
        """Create conversation summary"""
        
        summary = AIConversationSummaryModel(**summary_data)
        self.session.add(summary)
        await self.session.commit()
        await self.session.refresh(summary)
        
        return summary
    
    async def get_conversation_summaries(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[AIConversationSummaryModel]:
        """Get summaries for a conversation"""
        
        stmt = select(AIConversationSummaryModel).where(
            AIConversationSummaryModel.conversation_id == conversation_id
        ).order_by(AIConversationSummaryModel.time_range_end.desc())
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_summaries_for_processing(
        self,
        user_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[AIConversationSummaryModel]:
        """Get unprocessed summaries"""
        
        conditions = [AIConversationSummaryModel.is_processed == False]
        
        stmt = select(AIConversationSummaryModel).where(and_(*conditions)).order_by(
            AIConversationSummaryModel.created_at.asc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def mark_summary_processed(self, summary_id: UUID):
        """Mark summary as processed"""
        
        stmt = update(AIConversationSummaryModel).where(
            AIConversationSummaryModel.id == summary_id
        ).values(
            is_processed=True,
            processed_at=datetime.utcnow()
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def search_summaries(
        self,
        query: str,
        conversation_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[AIConversationSummaryModel]:
        """Search summaries by content"""
        
        search_pattern = f"%{query}%"
        conditions = [
            or_(
                AIConversationSummaryModel.summary_text.ilike(search_pattern),
                func.array_to_string(AIConversationSummaryModel.key_points, ' ').ilike(search_pattern),
                func.array_to_string(AIConversationSummaryModel.topics, ' ').ilike(search_pattern)
            )
        ]
        
        if conversation_id:
            conditions.append(AIConversationSummaryModel.conversation_id == conversation_id)
        
        stmt = select(AIConversationSummaryModel).where(and_(*conditions)).order_by(
            AIConversationSummaryModel.summary_quality_score.desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_recent_summaries(
        self,
        days: int = 7,
        user_conversations: Optional[List[UUID]] = None,
        limit: int = 20
    ) -> List[AIConversationSummaryModel]:
        """Get recent summaries within specified days"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        conditions = [AIConversationSummaryModel.time_range_end >= since_date]
        
        if user_conversations:
            conditions.append(AIConversationSummaryModel.conversation_id.in_(user_conversations))
        
        stmt = select(AIConversationSummaryModel).where(and_(*conditions)).order_by(
            AIConversationSummaryModel.time_range_end.desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_summary_quality(self, summary_id: UUID, quality_score: float, completeness_score: float):
        """Update summary quality scores"""
        
        stmt = update(AIConversationSummaryModel).where(
            AIConversationSummaryModel.id == summary_id
        ).values(
            summary_quality_score=quality_score,
            completeness_score=completeness_score
        )
        
        await self.session.execute(stmt)
        await self.session.commit()