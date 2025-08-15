"""AI Agent service for managing AI agents and their lifecycle."""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from app.infrastructure.database.repositories.ai_agent_repository_impl import (
    AIAgentRepositoryImpl,
    AIAgentVersionRepositoryImpl,
    AIAgentKnowledgeBaseRepositoryImpl
)
from app.schemas.ai import (
    AIAgentCreate,
    AIAgentUpdate, 
    AIAgentResponse,
    AIAgentListResponse,
    PaginationParams,
    PersonalityProfile,
    ModelPreferences
)
from app.services.base import BaseService


class AIAgentService(BaseService):
    """AI Agent service for managing agents"""
    
    def __init__(self, session):
        super().__init__(session)
        self.agent_repo = AIAgentRepositoryImpl(session)
        self.version_repo = AIAgentVersionRepositoryImpl(session)
        self.knowledge_repo = AIAgentKnowledgeBaseRepositoryImpl(session)
    
    async def create_agent(self, agent_data: AIAgentCreate, user_id: UUID) -> AIAgentResponse:
        """Create a new AI agent"""
        
        # Check if agent name already exists for user
        existing = await self.agent_repo.get_agent_by_name(agent_data.name, user_id)
        if existing:
            raise ValueError(f"Agent with name '{agent_data.name}' already exists")
        
        # Create agent
        agent = await self.agent_repo.create_agent(agent_data, user_id)
        
        # Create initial version
        await self._create_initial_version(agent, user_id)
        
        return AIAgentResponse.model_validate(agent)
    
    async def get_agent(self, agent_id: UUID, user_id: Optional[UUID] = None) -> Optional[AIAgentResponse]:
        """Get agent by ID"""
        
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return None
        
        return AIAgentResponse.model_validate(agent)
    
    async def update_agent(
        self, 
        agent_id: UUID, 
        agent_data: AIAgentUpdate, 
        user_id: UUID
    ) -> Optional[AIAgentResponse]:
        """Update an existing agent"""
        
        # Get current agent
        current_agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not current_agent:
            return None
        
        # Update agent
        updated_agent = await self.agent_repo.update_agent(agent_id, agent_data, user_id)
        if not updated_agent:
            return None
        
        # Create new version if significant changes
        if self._requires_new_version(agent_data):
            await self._create_version_from_update(updated_agent, current_agent, user_id)
        
        return AIAgentResponse.model_validate(updated_agent)
    
    async def list_agents(
        self,
        user_id: Optional[UUID] = None,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        pagination: Optional[PaginationParams] = None
    ) -> AIAgentListResponse:
        """List agents with filtering"""
        
        agents, total = await self.agent_repo.list_agents(
            user_id=user_id,
            agent_type=agent_type,
            status=status,
            search=search,
            pagination=pagination
        )
        
        agent_responses = [AIAgentResponse.model_validate(agent) for agent in agents]
        
        if pagination:
            return AIAgentListResponse(
                agents=agent_responses,
                total=total,
                page=pagination.page,
                size=pagination.size
            )
        
        return AIAgentListResponse(
            agents=agent_responses,
            total=total,
            page=1,
            size=len(agent_responses)
        )
    
    async def delete_agent(self, agent_id: UUID, user_id: UUID) -> bool:
        """Delete an agent"""
        
        return await self.agent_repo.delete_agent(agent_id, user_id)
    
    async def deploy_agent(self, agent_id: UUID, user_id: UUID) -> bool:
        """Deploy agent (placeholder for actual deployment logic)"""
        
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return False
        
        # TODO: Implement actual deployment logic
        # For now, just mark as deployed
        await self.agent_repo.update_agent(
            agent_id,
            AIAgentUpdate(deployment_status="deployed"),
            user_id
        )
        
        return True
    
    async def get_agent_versions(self, agent_id: UUID, user_id: UUID) -> List[Dict[str, Any]]:
        """Get version history for an agent"""
        
        # Verify ownership
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return []
        
        versions = await self.version_repo.get_versions(agent_id)
        return [
            {
                'id': version.id,
                'version_number': version.version_number,
                'previous_version': version.previous_version,
                'changes': version.changes,
                'change_description': version.change_description,
                'created_at': version.created_at,
                'is_current': version.is_current
            }
            for version in versions
        ]
    
    async def rollback_to_version(
        self, 
        agent_id: UUID, 
        version_number: str, 
        user_id: UUID
    ) -> Optional[AIAgentResponse]:
        """Rollback agent to a specific version"""
        
        # Verify ownership
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return None
        
        # Get target version
        target_version = await self.version_repo.get_version_by_number(agent_id, version_number)
        if not target_version:
            return None
        
        # Restore agent from snapshot
        agent_snapshot = target_version.agent_snapshot
        
        # Create update data from snapshot
        update_data = AIAgentUpdate(
            display_name=agent_snapshot.get('display_name'),
            description=agent_snapshot.get('description'),
            system_prompt=agent_snapshot.get('system_prompt'),
            personality_config=PersonalityProfile.model_validate(agent_snapshot.get('personality_config', {})),
            model_preferences=ModelPreferences.model_validate(agent_snapshot.get('model_preferences', {})),
            enabled_tools=agent_snapshot.get('enabled_tools', []),
            behavior_rules=agent_snapshot.get('behavior_rules', []),
            conversation_style=agent_snapshot.get('conversation_style'),
            max_context_length=agent_snapshot.get('max_context_length'),
            timeout_seconds=agent_snapshot.get('timeout_seconds')
        )
        
        # Update agent
        updated_agent = await self.agent_repo.update_agent(agent_id, update_data, user_id)
        if not updated_agent:
            return None
        
        # Create rollback version
        await self._create_rollback_version(updated_agent, target_version, user_id)
        
        return AIAgentResponse.model_validate(updated_agent)
    
    async def update_usage_stats(self, agent_id: UUID, execution_time: float, success: bool):
        """Update agent usage statistics"""
        
        await self.agent_repo.update_usage_stats(agent_id, execution_time, success)
    
    async def _create_initial_version(self, agent, user_id: UUID):
        """Create initial version for new agent"""
        
        version_data = {
            'version_number': '1.0.0',
            'previous_version': None,
            'agent_snapshot': self._create_agent_snapshot(agent),
            'changes': {'type': 'initial_creation', 'description': 'Initial agent creation'},
            'change_description': 'Initial version created'
        }
        
        await self.version_repo.create_version(agent.id, version_data, user_id)
    
    async def _create_version_from_update(self, updated_agent, original_agent, user_id: UUID):
        """Create version from agent update"""
        
        current_version = await self.version_repo.get_current_version(updated_agent.id)
        new_version = self._increment_version(current_version.version_number if current_version else "1.0.0")
        
        # Calculate changes
        changes = self._calculate_changes(original_agent, updated_agent)
        
        version_data = {
            'version_number': new_version,
            'previous_version': current_version.version_number if current_version else None,
            'agent_snapshot': self._create_agent_snapshot(updated_agent),
            'changes': changes,
            'change_description': self._generate_change_description(changes)
        }
        
        await self.version_repo.create_version(updated_agent.id, version_data, user_id)
    
    async def _create_rollback_version(self, agent, target_version, user_id: UUID):
        """Create version for rollback operation"""
        
        current_version = await self.version_repo.get_current_version(agent.id)
        new_version = self._increment_version(current_version.version_number if current_version else "1.0.0")
        
        version_data = {
            'version_number': new_version,
            'previous_version': current_version.version_number if current_version else None,
            'agent_snapshot': self._create_agent_snapshot(agent),
            'changes': {
                'type': 'rollback',
                'target_version': target_version.version_number,
                'description': f'Rolled back to version {target_version.version_number}'
            },
            'change_description': f'Rollback to version {target_version.version_number}'
        }
        
        await self.version_repo.create_version(agent.id, version_data, user_id)
    
    def _requires_new_version(self, agent_data: AIAgentUpdate) -> bool:
        """Check if update requires new version"""
        
        significant_fields = [
            'system_prompt', 'personality_config', 'model_preferences',
            'enabled_tools', 'behavior_rules'
        ]
        
        return any(getattr(agent_data, field, None) is not None for field in significant_fields)
    
    def _create_agent_snapshot(self, agent) -> Dict[str, Any]:
        """Create snapshot of agent state"""
        
        return {
            'name': agent.name,
            'display_name': agent.display_name,
            'description': agent.description,
            'agent_type': agent.agent_type,
            'system_prompt': agent.system_prompt,
            'personality_config': agent.personality_config,
            'model_preferences': agent.model_preferences,
            'enabled_tools': agent.enabled_tools,
            'behavior_rules': agent.behavior_rules,
            'conversation_style': agent.conversation_style,
            'capabilities': agent.capabilities,
            'max_context_length': agent.max_context_length,
            'timeout_seconds': agent.timeout_seconds,
            'required_permissions': agent.required_permissions
        }
    
    def _increment_version(self, current_version: str) -> str:
        """Increment version number"""
        
        try:
            major, minor, patch = map(int, current_version.split('.'))
            return f"{major}.{minor}.{patch + 1}"
        except ValueError:
            return "1.0.1"
    
    def _calculate_changes(self, original, updated) -> Dict[str, Any]:
        """Calculate changes between agent versions"""
        
        changes = {'type': 'update', 'fields_changed': []}
        
        fields_to_check = [
            'display_name', 'description', 'system_prompt', 'personality_config',
            'model_preferences', 'enabled_tools', 'behavior_rules', 'conversation_style'
        ]
        
        for field in fields_to_check:
            original_value = getattr(original, field, None)
            updated_value = getattr(updated, field, None)
            
            if original_value != updated_value:
                changes['fields_changed'].append({
                    'field': field,
                    'old_value': original_value,
                    'new_value': updated_value
                })
        
        return changes
    
    def _generate_change_description(self, changes: Dict[str, Any]) -> str:
        """Generate human-readable change description"""
        
        if changes['type'] == 'update':
            changed_fields = [change['field'] for change in changes['fields_changed']]
            if len(changed_fields) == 1:
                return f"Updated {changed_fields[0]}"
            elif len(changed_fields) <= 3:
                return f"Updated {', '.join(changed_fields)}"
            else:
                return f"Updated {len(changed_fields)} fields"
        
        return changes.get('description', 'Agent updated')


class AIAgentKnowledgeService(BaseService):
    """Service for managing agent knowledge bases"""
    
    def __init__(self, session):
        super().__init__(session)
        self.knowledge_repo = AIAgentKnowledgeBaseRepositoryImpl(session)
        self.agent_repo = AIAgentRepositoryImpl(session)
    
    async def add_knowledge(
        self,
        agent_id: UUID,
        knowledge_data: Dict[str, Any],
        user_id: UUID
    ) -> Dict[str, Any]:
        """Add knowledge to agent's knowledge base"""
        
        # Verify agent ownership
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agent not found or access denied")
        
        knowledge = await self.knowledge_repo.create_knowledge_base(agent_id, knowledge_data)
        
        return {
            'id': knowledge.id,
            'agent_id': knowledge.agent_id,
            'name': knowledge.name,
            'description': knowledge.description,
            'knowledge_type': knowledge.knowledge_type,
            'quality_score': knowledge.quality_score,
            'relevance_score': knowledge.relevance_score,
            'created_at': knowledge.created_at
        }
    
    async def get_agent_knowledge(
        self,
        agent_id: UUID,
        knowledge_type: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get knowledge base entries for an agent"""
        
        # Verify access if user_id provided
        if user_id:
            agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
            if not agent:
                return []
        
        knowledge_entries = await self.knowledge_repo.get_agent_knowledge(agent_id, knowledge_type)
        
        return [
            {
                'id': entry.id,
                'name': entry.name,
                'description': entry.description,
                'knowledge_type': entry.knowledge_type,
                'content': entry.content,
                'metadata': entry.metadata,
                'tags': entry.tags,
                'quality_score': entry.quality_score,
                'relevance_score': entry.relevance_score,
                'usage_count': entry.usage_count,
                'created_at': entry.created_at
            }
            for entry in knowledge_entries
        ]
    
    async def search_knowledge(
        self,
        agent_id: UUID,
        query: str,
        limit: int = 10,
        user_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Search agent's knowledge base"""
        
        # Verify access if user_id provided
        if user_id:
            agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
            if not agent:
                return []
        
        results = await self.knowledge_repo.search_knowledge(agent_id, query, limit)
        
        return [
            {
                'id': result.id,
                'name': result.name,
                'knowledge_type': result.knowledge_type,
                'content': result.content[:500] + "..." if len(result.content) > 500 else result.content,
                'relevance_score': result.relevance_score,
                'quality_score': result.quality_score
            }
            for result in results
        ]
    
    async def update_knowledge_usage(self, knowledge_id: UUID):
        """Update knowledge usage statistics"""
        
        await self.knowledge_repo.update_knowledge_usage(knowledge_id)
    
    async def delete_knowledge(self, knowledge_id: UUID, agent_id: UUID, user_id: UUID) -> bool:
        """Delete knowledge entry"""
        
        # Verify agent ownership
        agent = await self.agent_repo.get_agent_by_id(agent_id, user_id)
        if not agent:
            return False
        
        return await self.knowledge_repo.delete_knowledge(knowledge_id, agent_id)