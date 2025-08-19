"""
Agent Repository Implementation

This module provides the implementation of the agent repository.
"""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.interfaces.repositories.base_repository import BaseRepository as BaseRepositoryInterface
from app.infrastructure.database.models.agent_model import AIAgentModel as Agent
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AgentRepository(BaseRepository[Agent, UUID], BaseRepositoryInterface):
    """Agent repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Agent)
    
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        try:
            statement = select(Agent).where(Agent.name == name)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            self.logger.error(f"Error getting agent by name {name}: {e}")
            raise
    
    async def get_by_display_name(self, display_name: str) -> Optional[Agent]:
        """Get agent by display name."""
        try:
            statement = select(Agent).where(Agent.display_name == display_name)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            self.logger.error(f"Error getting agent by display name {display_name}: {e}")
            raise
    
    async def get_active_agents(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """Get all active agents."""
        try:
            statement = select(Agent).where(
                Agent.is_active == True
            ).offset(offset).limit(limit).order_by(Agent.display_name)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting active agents: {e}")
            raise
    
    async def get_public_agents(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """Get all public agents."""
        try:
            statement = select(Agent).where(
                and_(Agent.is_active == True, Agent.is_public == True)
            ).offset(offset).limit(limit).order_by(Agent.display_name)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting public agents: {e}")
            raise
    
    async def search_agents(
        self,
        query: str,
        offset: int = 0,
        limit: int = 100,
        only_active: bool = True,
        only_public: bool = False
    ) -> Tuple[List[Agent], int]:
        """Search agents by name, display name, or description."""
        try:
            # Build search conditions
            search_conditions = [
                Agent.name.ilike(f"%{query}%"),
                Agent.display_name.ilike(f"%{query}%"),
                Agent.description.ilike(f"%{query}%")
            ]
            
            # Build base statement
            statement = select(Agent).where(or_(*search_conditions))
            
            # Add filters
            filters = []
            if only_active:
                filters.append(Agent.is_active == True)
            if only_public:
                filters.append(Agent.is_public == True)
            
            if filters:
                statement = statement.where(and_(*filters))
            
            # Get total count
            count_statement = select(Agent).where(statement.whereclause)
            count_result = await self.session.exec(count_statement)
            total_count = len(count_result.all())
            
            # Apply pagination and ordering
            statement = statement.offset(offset).limit(limit).order_by(Agent.display_name)
            
            result = await self.session.exec(statement)
            agents = result.all()
            
            return agents, total_count
        except Exception as e:
            self.logger.error(f"Error searching agents with query '{query}': {e}")
            raise
    
    async def get_agents_by_capability(
        self,
        capability: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """Get agents that have a specific capability."""
        try:
            statement = select(Agent).where(
                and_(
                    Agent.is_active == True,
                    Agent.capabilities.contains([capability])
                )
            ).offset(offset).limit(limit).order_by(Agent.display_name)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting agents by capability '{capability}': {e}")
            raise
    
    async def get_agents_by_model_provider(
        self,
        provider: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """Get agents using a specific model provider."""
        try:
            statement = select(Agent).where(
                and_(
                    Agent.is_active == True,
                    Agent.model_provider == provider
                )
            ).offset(offset).limit(limit).order_by(Agent.display_name)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting agents by model provider '{provider}': {e}")
            raise
    
    async def activate_agent(self, agent_id: str) -> bool:
        """Activate an agent."""
        try:
            agent = await self.get_by_id(agent_id)
            if not agent:
                return False
            
            agent.is_active = True
            self.session.add(agent)
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error activating agent {agent_id}: {e}")
            raise
    
    async def deactivate_agent(self, agent_id: str) -> bool:
        """Deactivate an agent."""
        try:
            agent = await self.get_by_id(agent_id)
            if not agent:
                return False
            
            agent.is_active = False
            self.session.add(agent)
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deactivating agent {agent_id}: {e}")
            raise
    
    async def update_agent_config(
        self,
        agent_id: str,
        model_config: dict
    ) -> Optional[Agent]:
        """Update agent model configuration."""
        try:
            agent = await self.get_by_id(agent_id)
            if not agent:
                return None
            
            # Update model configuration fields
            if "model_provider" in model_config:
                agent.model_provider = model_config["model_provider"]
            if "model_name" in model_config:
                agent.model_name = model_config["model_name"]
            if "temperature" in model_config:
                agent.temperature = model_config["temperature"]
            if "max_tokens" in model_config:
                agent.max_tokens = model_config["max_tokens"]
            if "system_prompt" in model_config:
                agent.system_prompt = model_config["system_prompt"]
            
            self.session.add(agent)
            await self.session.flush()
            await self.session.refresh(agent)
            return agent
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating agent config {agent_id}: {e}")
            raise