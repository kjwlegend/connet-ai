"""AI Agent repository implementation."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.ai_agent_model import (
    AIAgentModel, 
    AIAgentVersionModel, 
    AIAgentKnowledgeBaseModel
)
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.schemas.ai import AIAgentCreate, AIAgentUpdate, PaginationParams


class AIAgentRepositoryImpl(BaseRepository[AIAgentModel, UUID]):
    """AI Agent repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIAgentModel)
    
    async def create_agent(self, agent_data: AIAgentCreate, user_id: UUID) -> AIAgentModel:
        """Create a new AI agent"""
        
        agent_dict = agent_data.model_dump(exclude_unset=True)
        agent_dict.update({
            'created_by': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        
        # Convert Pydantic models to dictionaries for JSON storage
        if 'personality_config' in agent_dict:
            agent_dict['personality_config'] = agent_dict['personality_config'].model_dump()
        if 'model_preferences' in agent_dict:
            agent_dict['model_preferences'] = agent_dict['model_preferences'].model_dump()
        
        agent = AIAgentModel(**agent_dict)
        self.session.add(agent)
        await self.session.commit()
        await self.session.refresh(agent)
        
        return agent
    
    async def update_agent(self, agent_id: UUID, agent_data: AIAgentUpdate, 
                          user_id: UUID) -> Optional[AIAgentModel]:
        """Update an existing AI agent"""
        
        # Get existing agent and check ownership
        stmt = select(AIAgentModel).where(
            and_(AIAgentModel.id == agent_id, AIAgentModel.created_by == user_id)
        )
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if not agent:
            return None
        
        # Prepare update data
        update_data = agent_data.model_dump(exclude_unset=True, exclude_none=True)
        update_data['updated_at'] = datetime.utcnow()
        
        # Convert Pydantic models to dictionaries
        if 'personality_config' in update_data:
            update_data['personality_config'] = update_data['personality_config'].model_dump()
        if 'model_preferences' in update_data:
            update_data['model_preferences'] = update_data['model_preferences'].model_dump()
        
        # Update the agent
        stmt = update(AIAgentModel).where(AIAgentModel.id == agent_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()
        
        # Return updated agent
        await self.session.refresh(agent)
        return agent
    
    async def get_agent_by_id(self, agent_id: UUID, user_id: Optional[UUID] = None) -> Optional[AIAgentModel]:
        """Get agent by ID, optionally filtered by user"""
        
        conditions = [AIAgentModel.id == agent_id]
        if user_id:
            conditions.append(AIAgentModel.created_by == user_id)
        
        stmt = select(AIAgentModel).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_agent_by_name(self, name: str, user_id: Optional[UUID] = None) -> Optional[AIAgentModel]:
        """Get agent by name, optionally filtered by user"""
        
        conditions = [AIAgentModel.name == name]
        if user_id:
            conditions.append(AIAgentModel.created_by == user_id)
        
        stmt = select(AIAgentModel).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_agents(self, user_id: Optional[UUID] = None, 
                         agent_type: Optional[str] = None,
                         status: Optional[str] = None,
                         search: Optional[str] = None,
                         pagination: Optional[PaginationParams] = None) -> tuple[List[AIAgentModel], int]:
        """List agents with filtering and pagination"""
        
        # Build base query
        stmt = select(AIAgentModel)
        
        # Apply filters
        conditions = []
        if user_id:
            conditions.append(AIAgentModel.created_by == user_id)
        if agent_type:
            conditions.append(AIAgentModel.agent_type == agent_type)
        if status:
            conditions.append(AIAgentModel.status == status)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    AIAgentModel.name.ilike(search_pattern),
                    AIAgentModel.display_name.ilike(search_pattern),
                    AIAgentModel.description.ilike(search_pattern)
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Count total for pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply sorting
        if pagination and pagination.sort_by:
            sort_column = getattr(AIAgentModel, pagination.sort_by, AIAgentModel.created_at)
            if pagination.sort_order == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(AIAgentModel.created_at.desc())
        
        # Apply pagination
        if pagination:
            offset = (pagination.page - 1) * pagination.size
            stmt = stmt.offset(offset).limit(pagination.size)
        
        result = await self.session.execute(stmt)
        agents = result.scalars().all()
        
        return list(agents), total
    
    async def delete_agent(self, agent_id: UUID, user_id: UUID) -> bool:
        """Delete an agent"""
        
        # Check ownership and get agent
        stmt = select(AIAgentModel).where(
            and_(AIAgentModel.id == agent_id, AIAgentModel.created_by == user_id)
        )
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if not agent:
            return False
        
        # Delete the agent (cascading deletes should handle related records)
        stmt = delete(AIAgentModel).where(AIAgentModel.id == agent_id)
        await self.session.execute(stmt)
        await self.session.commit()
        
        return True
    
    async def update_usage_stats(self, agent_id: UUID, execution_time: float, success: bool):
        """Update agent usage statistics"""
        
        stmt = select(AIAgentModel).where(AIAgentModel.id == agent_id)
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if not agent:
            return
        
        # Calculate new statistics
        total_executions = agent.usage_count + 1
        new_avg_time = (agent.avg_response_time * agent.usage_count + execution_time) / total_executions
        
        if success:
            new_success_rate = (agent.success_rate * agent.usage_count + 1) / total_executions
        else:
            new_success_rate = (agent.success_rate * agent.usage_count) / total_executions
        
        # Update the agent
        update_data = {
            'usage_count': total_executions,
            'avg_response_time': new_avg_time,
            'success_rate': new_success_rate,
            'last_used_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        stmt = update(AIAgentModel).where(AIAgentModel.id == agent_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()


class AIAgentVersionRepositoryImpl(BaseRepository[AIAgentVersionModel, UUID]):
    """AI Agent version repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIAgentVersionModel)
    
    async def create_version(self, agent_id: UUID, version_data: Dict[str, Any], 
                           user_id: UUID) -> AIAgentVersionModel:
        """Create a new agent version"""
        
        # Mark previous versions as not current
        stmt = update(AIAgentVersionModel).where(
            and_(AIAgentVersionModel.agent_id == agent_id, AIAgentVersionModel.is_current == True)
        ).values(is_current=False)
        await self.session.execute(stmt)
        
        # Create new version
        version = AIAgentVersionModel(
            agent_id=agent_id,
            version_number=version_data['version_number'],
            previous_version=version_data.get('previous_version'),
            agent_snapshot=version_data['agent_snapshot'],
            changes=version_data.get('changes', {}),
            change_description=version_data.get('change_description'),
            created_by=user_id,
            created_at=datetime.utcnow(),
            is_current=True
        )
        
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        
        return version
    
    async def get_versions(self, agent_id: UUID) -> List[AIAgentVersionModel]:
        """Get all versions for an agent"""
        
        stmt = select(AIAgentVersionModel).where(
            AIAgentVersionModel.agent_id == agent_id
        ).order_by(AIAgentVersionModel.created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_current_version(self, agent_id: UUID) -> Optional[AIAgentVersionModel]:
        """Get current version for an agent"""
        
        stmt = select(AIAgentVersionModel).where(
            and_(
                AIAgentVersionModel.agent_id == agent_id,
                AIAgentVersionModel.is_current == True
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_version_by_number(self, agent_id: UUID, version_number: str) -> Optional[AIAgentVersionModel]:
        """Get specific version by number"""
        
        stmt = select(AIAgentVersionModel).where(
            and_(
                AIAgentVersionModel.agent_id == agent_id,
                AIAgentVersionModel.version_number == version_number
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class AIAgentKnowledgeBaseRepositoryImpl(BaseRepository[AIAgentKnowledgeBaseModel, UUID]):
    """AI Agent knowledge base repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIAgentKnowledgeBaseModel)
    
    async def create_knowledge_base(self, agent_id: UUID, knowledge_data: Dict[str, Any]) -> AIAgentKnowledgeBaseModel:
        """Create knowledge base entry"""
        
        knowledge = AIAgentKnowledgeBaseModel(
            agent_id=agent_id,
            name=knowledge_data['name'],
            description=knowledge_data.get('description'),
            knowledge_type=knowledge_data['knowledge_type'],
            content=knowledge_data['content'],
            metadata=knowledge_data.get('metadata', {}),
            tags=knowledge_data.get('tags', []),
            embedding_model=knowledge_data.get('embedding_model'),
            embedding_dimension=knowledge_data.get('embedding_dimension'),
            quality_score=knowledge_data.get('quality_score', 1.0),
            relevance_score=knowledge_data.get('relevance_score', 1.0),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.session.add(knowledge)
        await self.session.commit()
        await self.session.refresh(knowledge)
        
        return knowledge
    
    async def get_agent_knowledge(self, agent_id: UUID, knowledge_type: Optional[str] = None) -> List[AIAgentKnowledgeBaseModel]:
        """Get knowledge base entries for an agent"""
        
        conditions = [AIAgentKnowledgeBaseModel.agent_id == agent_id, AIAgentKnowledgeBaseModel.status == "active"]
        if knowledge_type:
            conditions.append(AIAgentKnowledgeBaseModel.knowledge_type == knowledge_type)
        
        stmt = select(AIAgentKnowledgeBaseModel).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_knowledge_usage(self, knowledge_id: UUID):
        """Update knowledge usage statistics"""
        
        stmt = update(AIAgentKnowledgeBaseModel).where(
            AIAgentKnowledgeBaseModel.id == knowledge_id
        ).values(
            usage_count=AIAgentKnowledgeBaseModel.usage_count + 1,
            updated_at=datetime.utcnow()
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def delete_knowledge(self, knowledge_id: UUID, agent_id: UUID) -> bool:
        """Delete knowledge base entry"""
        
        stmt = delete(AIAgentKnowledgeBaseModel).where(
            and_(
                AIAgentKnowledgeBaseModel.id == knowledge_id,
                AIAgentKnowledgeBaseModel.agent_id == agent_id
            )
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def search_knowledge(self, agent_id: UUID, query: str, limit: int = 10) -> List[AIAgentKnowledgeBaseModel]:
        """Search knowledge base entries (basic text search)"""
        
        search_pattern = f"%{query}%"
        
        stmt = select(AIAgentKnowledgeBaseModel).where(
            and_(
                AIAgentKnowledgeBaseModel.agent_id == agent_id,
                AIAgentKnowledgeBaseModel.status == "active",
                or_(
                    AIAgentKnowledgeBaseModel.name.ilike(search_pattern),
                    AIAgentKnowledgeBaseModel.description.ilike(search_pattern),
                    # Note: For JSONB content search, you might want to use specialized functions
                )
            )
        ).order_by(AIAgentKnowledgeBaseModel.relevance_score.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())