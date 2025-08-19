"""
AI Agent Repository Implementation (Unified)

This module provides the unified implementation of the AI Agent repository.
Combines functionality from both ai_agent_repository_impl.py and agent_repository_impl.py.
"""

from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.agent_model import (
    AIAgentModel,
    AIAgentVersionModel
)
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AgentRepository(BaseRepository[AIAgentModel]):
    """Unified AI Agent repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIAgentModel)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    # Basic CRUD Operations
    async def create_agent(self, agent_data: Dict[str, Any], user_id: UUID) -> AIAgentModel:
        """Create a new AI agent."""
        try:
            agent_dict = agent_data.copy()
            agent_dict.update({
                'created_by': user_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
            
            agent = AIAgentModel(**agent_dict)
            self.session.add(agent)
            await self.session.commit()
            await self.session.refresh(agent)
            
            return agent
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating agent: {e}")
            raise
    
    async def update_agent(self, agent_id: UUID, update_data: Dict[str, Any], 
                          user_id: Optional[UUID] = None) -> Optional[AIAgentModel]:
        """Update an existing AI agent."""
        try:
            # Build conditions
            conditions = [AIAgentModel.id == agent_id]
            if user_id:
                conditions.append(AIAgentModel.created_by == user_id)
            
            # Get existing agent
            stmt = select(AIAgentModel).where(and_(*conditions))
            result = await self.session.execute(stmt)
            agent = result.scalar_one_or_none()
            
            if not agent:
                return None
            
            # Prepare update data
            update_data = update_data.copy()
            update_data['updated_at'] = datetime.utcnow()
            
            # Update the agent
            stmt = update(AIAgentModel).where(AIAgentModel.id == agent_id).values(**update_data)
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Return updated agent
            await self.session.refresh(agent)
            return agent
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise
    
    async def delete_agent(self, agent_id: UUID, user_id: Optional[UUID] = None) -> bool:
        """Delete an agent."""
        try:
            # Build conditions
            conditions = [AIAgentModel.id == agent_id]
            if user_id:
                conditions.append(AIAgentModel.created_by == user_id)
            
            # Check if agent exists
            stmt = select(AIAgentModel).where(and_(*conditions))
            result = await self.session.execute(stmt)
            agent = result.scalar_one_or_none()
            
            if not agent:
                return False
            
            # Delete the agent
            stmt = delete(AIAgentModel).where(AIAgentModel.id == agent_id)
            await self.session.execute(stmt)
            await self.session.commit()
            
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting agent {agent_id}: {e}")
            raise
    
    # Query Operations
    async def get_agent_by_id(self, agent_id: UUID, user_id: Optional[UUID] = None) -> Optional[AIAgentModel]:
        """Get agent by ID, optionally filtered by user."""
        try:
            conditions = [AIAgentModel.id == agent_id]
            if user_id:
                conditions.append(AIAgentModel.created_by == user_id)
            
            stmt = select(AIAgentModel).where(and_(*conditions))
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting agent by ID {agent_id}: {e}")
            raise
    
    async def get_agent_by_name(self, name: str, user_id: Optional[UUID] = None) -> Optional[AIAgentModel]:
        """Get agent by name, optionally filtered by user."""
        try:
            conditions = [AIAgentModel.name == name]
            if user_id:
                conditions.append(AIAgentModel.created_by == user_id)
            
            stmt = select(AIAgentModel).where(and_(*conditions))
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting agent by name {name}: {e}")
            raise
    
    async def get_agent_by_display_name(self, display_name: str) -> Optional[AIAgentModel]:
        """Get agent by display name."""
        try:
            stmt = select(AIAgentModel).where(AIAgentModel.display_name == display_name)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting agent by display name {display_name}: {e}")
            raise
    
    # List and Search Operations
    async def list_agents(
        self,
        user_id: Optional[UUID] = None,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        only_active: bool = True,
        only_public: bool = False,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> Tuple[List[AIAgentModel], int]:
        """List agents with filtering and pagination."""
        try:
            # Build conditions
            conditions = []
            
            if user_id:
                conditions.append(AIAgentModel.created_by == user_id)
            if agent_type:
                conditions.append(AIAgentModel.agent_type == agent_type)
            if status:
                conditions.append(AIAgentModel.status == status)
            if category:
                conditions.append(AIAgentModel.category == category)
            if only_active:
                conditions.append(AIAgentModel.is_active == True)
            if only_public:
                conditions.append(AIAgentModel.is_public == True)
            
            # Add search conditions
            if search:
                search_pattern = f"%{search}%"
                search_conditions = [
                    AIAgentModel.name.ilike(search_pattern),
                    AIAgentModel.display_name.ilike(search_pattern),
                    AIAgentModel.description.ilike(search_pattern)
                ]
                conditions.append(or_(*search_conditions))
            
            # Build base query
            base_stmt = select(AIAgentModel)
            if conditions:
                base_stmt = base_stmt.where(and_(*conditions))
            
            # Count total for pagination
            count_stmt = select(func.count()).select_from(base_stmt.subquery())
            total_result = await self.session.execute(count_stmt)
            total = total_result.scalar()
            
            # Apply sorting and pagination
            stmt = base_stmt.order_by(AIAgentModel.created_at.desc())
            stmt = stmt.offset(offset).limit(limit)
            
            result = await self.session.execute(stmt)
            agents = result.scalars().all()
            
            return list(agents), total
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            raise
    
    async def search_agents(
        self,
        query: str,
        offset: int = 0,
        limit: int = 100,
        only_active: bool = True,
        only_public: bool = False
    ) -> Tuple[List[AIAgentModel], int]:
        """Search agents by name, display name, or description."""
        return await self.list_agents(
            only_active=only_active,
            only_public=only_public,
            offset=offset,
            limit=limit,
            search=query
        )
    
    async def get_active_agents(self, offset: int = 0, limit: int = 100) -> List[AIAgentModel]:
        """Get all active agents."""
        try:
            agents, _ = await self.list_agents(
                only_active=True,
                offset=offset,
                limit=limit
            )
            return agents
        except Exception as e:
            logger.error(f"Error getting active agents: {e}")
            raise
    
    async def get_public_agents(self, offset: int = 0, limit: int = 100) -> List[AIAgentModel]:
        """Get all public agents."""
        try:
            agents, _ = await self.list_agents(
                only_active=True,
                only_public=True,
                offset=offset,
                limit=limit
            )
            return agents
        except Exception as e:
            logger.error(f"Error getting public agents: {e}")
            raise
    
    async def get_agents_by_capability(
        self,
        capability: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[AIAgentModel]:
        """Get agents that have a specific capability."""
        try:
            stmt = select(AIAgentModel).where(
                and_(
                    AIAgentModel.is_active == True,
                    AIAgentModel.capabilities.contains([capability])
                )
            ).offset(offset).limit(limit).order_by(AIAgentModel.display_name)
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting agents by capability '{capability}': {e}")
            raise
    
    async def get_agents_by_category(
        self,
        category: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[AIAgentModel]:
        """Get agents in a specific category."""
        try:
            agents, _ = await self.list_agents(
                category=category,
                only_active=True,
                offset=offset,
                limit=limit
            )
            return agents
        except Exception as e:
            logger.error(f"Error getting agents by category '{category}': {e}")
            raise
    
    # Status Management
    async def activate_agent(self, agent_id: UUID) -> bool:
        """Activate an agent."""
        try:
            agent = await self.get_agent_by_id(agent_id)
            if not agent:
                return False
            
            agent.is_active = True
            agent.updated_at = datetime.utcnow()
            self.session.add(agent)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error activating agent {agent_id}: {e}")
            raise
    
    async def deactivate_agent(self, agent_id: UUID) -> bool:
        """Deactivate an agent."""
        try:
            agent = await self.get_agent_by_id(agent_id)
            if not agent:
                return False
            
            agent.is_active = False
            agent.updated_at = datetime.utcnow()
            self.session.add(agent)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deactivating agent {agent_id}: {e}")
            raise
    
    # Statistics and Usage
    async def update_usage_stats(self, agent_id: UUID, success: bool = True):
        """Update agent usage statistics."""
        try:
            stmt = select(AIAgentModel).where(AIAgentModel.id == agent_id)
            result = await self.session.execute(stmt)
            agent = result.scalar_one_or_none()
            
            if not agent:
                return
            
            # Update usage count and last used time
            agent.usage_count += 1
            agent.last_used_at = datetime.utcnow()
            agent.updated_at = datetime.utcnow()
            
            self.session.add(agent)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating usage stats for agent {agent_id}: {e}")
            raise
    
    async def increment_follower_count(self, agent_id: UUID) -> bool:
        """Increment follower count for an agent."""
        try:
            stmt = update(AIAgentModel).where(
                AIAgentModel.id == agent_id
            ).values(
                follower_count=AIAgentModel.follower_count + 1,
                updated_at=datetime.utcnow()
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error incrementing follower count for agent {agent_id}: {e}")
            raise
    
    async def decrement_follower_count(self, agent_id: UUID) -> bool:
        """Decrement follower count for an agent."""
        try:
            stmt = update(AIAgentModel).where(
                and_(
                    AIAgentModel.id == agent_id,
                    AIAgentModel.follower_count > 0
                )
            ).values(
                follower_count=AIAgentModel.follower_count - 1,
                updated_at=datetime.utcnow()
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error decrementing follower count for agent {agent_id}: {e}")
            raise


class AgentVersionRepository(BaseRepository[AIAgentVersionModel]):
    """AI Agent version repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIAgentVersionModel)
    
    async def create_version(self, agent_id: UUID, version_data: Dict[str, Any], 
                           user_id: UUID) -> AIAgentVersionModel:
        """Create a new agent version."""
        try:
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
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating agent version: {e}")
            raise
    
    async def get_versions(self, agent_id: UUID) -> List[AIAgentVersionModel]:
        """Get all versions for an agent."""
        try:
            stmt = select(AIAgentVersionModel).where(
                AIAgentVersionModel.agent_id == agent_id
            ).order_by(AIAgentVersionModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting versions for agent {agent_id}: {e}")
            raise
    
    async def get_current_version(self, agent_id: UUID) -> Optional[AIAgentVersionModel]:
        """Get current version for an agent."""
        try:
            stmt = select(AIAgentVersionModel).where(
                and_(
                    AIAgentVersionModel.agent_id == agent_id,
                    AIAgentVersionModel.is_current == True
                )
            )
            
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting current version for agent {agent_id}: {e}")
            raise
    
    async def get_version_by_number(self, agent_id: UUID, version_number: str) -> Optional[AIAgentVersionModel]:
        """Get specific version by number."""
        try:
            stmt = select(AIAgentVersionModel).where(
                and_(
                    AIAgentVersionModel.agent_id == agent_id,
                    AIAgentVersionModel.version_number == version_number
                )
            )
            
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting version {version_number} for agent {agent_id}: {e}")
            raise