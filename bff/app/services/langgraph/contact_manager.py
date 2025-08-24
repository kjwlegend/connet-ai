"""
Contact Instance Manager

Manages the mapping between Agent definitions and Contact instances,
providing the personalized agent configurations for conversations.
Enhanced for Priority 2 with full contact instance management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database.models.contact_model import ContactModel, EntityType
from app.infrastructure.database.models.agent_model import AIAgentModel
from app.infrastructure.database.models.conversation_participant_model import ConversationParticipantModel
from app.infrastructure.database.repositories.contacts_repository_impl import ContactRepository
from app.services.langgraph.state_models import ContactInfo
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ContactInstanceManager:
    """Manager for Contact instances in LangGraph workflows - Enhanced for Priority 2"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.contact_repo = ContactRepository(session)
    
    async def get_conversation_participants(
        self, 
        conversation_id: UUID
    ) -> List[ContactInfo]:
        """Get all active contact participants in a conversation"""
        
        # Get all agent participants from the conversation
        stmt = select(ConversationParticipantModel).where(
            and_(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.participant_type == "agent",
                ConversationParticipantModel.is_active == True
            )
        )
        
        result = await self.session.execute(stmt)
        participants = result.scalars().all()
        
        contact_infos = []
        
        for participant in participants:
            # For each agent participant, we need to find the contact relationship
            # and get the agent details
            contact_info = await self._build_contact_info_from_participant(participant)
            if contact_info:
                contact_infos.append(contact_info)
        
        return contact_infos
    
    async def get_user_contact_by_agent(
        self,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[ContactInfo]:
        """Get user's contact instance for a specific agent"""
        
        # Find the contact relationship
        stmt = select(ContactModel).where(
            and_(
                ContactModel.follower_id == user_id,
                ContactModel.following_id == agent_id,
                ContactModel.following_type == EntityType.agent
            )
        )
        
        result = await self.session.execute(stmt)
        contact = result.scalar_one_or_none()
        
        if not contact:
            return None
        
        return await self._build_contact_info_from_contact(contact)
    
    async def get_mentioned_contacts(
        self,
        user_id: UUID,
        mentioned_agent_names: List[str]
    ) -> List[ContactInfo]:
        """Get contact instances for mentioned agent names"""
        
        contact_infos = []
        
        for agent_name in mentioned_agent_names:
            # Find agent by name
            agent_stmt = select(AIAgentModel).where(
                and_(
                    AIAgentModel.name == agent_name,
                    AIAgentModel.is_active == True
                )
            )
            
            agent_result = await self.session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            
            if not agent:
                continue
            
            # Find user's contact for this agent
            contact_info = await self.get_user_contact_by_agent(user_id, agent.id)
            if contact_info:
                contact_infos.append(contact_info)
        
        return contact_infos
    
    async def create_contact_instance(
        self,
        user_id: UUID,
        agent_id: UUID,
        custom_display_name: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> ContactInfo:
        """Create a new contact instance for a user and agent"""
        
        # Check if contact already exists
        existing_contact = await self.get_user_contact_by_agent(user_id, agent_id)
        if existing_contact:
            raise ValueError(f"Contact already exists for user {user_id} and agent {agent_id}")
        
        # Get agent details
        agent_stmt = select(AIAgentModel).where(AIAgentModel.id == agent_id)
        agent_result = await self.session.execute(agent_stmt)
        agent = agent_result.scalar_one_or_none()
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Create contact relationship
        contact = ContactModel(
            follower_id=user_id,
            following_id=agent_id,
            following_type=EntityType.agent,
            relationship_type="follow",
            display_name=custom_display_name,
            is_agent=True,
            created_at=datetime.utcnow()
        )
        
        self.session.add(contact)
        await self.session.flush()  # Get the ID without committing
        
        return await self._build_contact_info_from_contact(contact, agent)

    # Enhanced Contact Instance Management Methods (Priority 2)
    async def agent_to_contact_conversion(
        self,
        user_id: UUID,
        agent_id: UUID,
        custom_system_prompt: Optional[str] = None,
        instance_config: Optional[Dict[str, Any]] = None,
        resource_limits: Optional[Dict[str, Any]] = None,
        display_name_override: Optional[str] = None
    ) -> ContactInfo:
        """Convert an Agent definition into a personalized Contact instance for a user."""
        try:
            # Get agent details first
            agent_stmt = select(AIAgentModel).where(
                and_(AIAgentModel.id == agent_id, AIAgentModel.is_active == True)
            )
            agent_result = await self.session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found or inactive")
            
            # Use the repository to create contact instance
            contact = await self.contact_repo.create_contact_instance(
                user_id=user_id,
                agent_id=agent_id,
                custom_system_prompt=custom_system_prompt,
                instance_config=instance_config,
                resource_limits=resource_limits
            )
            
            # Set display name override if provided
            if display_name_override:
                contact.display_name = display_name_override
                await self.session.commit()
                await self.session.refresh(contact)
            
            logger.info(f"Agent {agent_id} converted to contact instance for user {user_id}")
            return await self._build_enhanced_contact_info(contact, agent)
            
        except Exception as e:
            logger.error(f"Error in agent to contact conversion: {e}")
            raise

    async def update_contact_personalization(
        self,
        user_id: UUID,
        agent_id: UUID,
        custom_system_prompt: Optional[str] = None,
        instance_config: Optional[Dict[str, Any]] = None,
        resource_limits: Optional[Dict[str, Any]] = None,
        display_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[ContactInfo]:
        """Update contact instance personalization settings."""
        try:
            # Update via repository
            contact = await self.contact_repo.update_contact_config(
                user_id=user_id,
                agent_id=agent_id,
                custom_system_prompt=custom_system_prompt,
                instance_config=instance_config,
                resource_limits=resource_limits
            )
            
            if not contact:
                logger.warning(f"Contact instance not found for user {user_id} and agent {agent_id}")
                return None
            
            # Update additional fields if provided
            update_needed = False
            if display_name is not None:
                contact.display_name = display_name
                update_needed = True
            if notes is not None:
                contact.notes = notes
                update_needed = True
            
            if update_needed:
                await self.session.commit()
                await self.session.refresh(contact)
            
            # Get agent details
            agent_stmt = select(AIAgentModel).where(AIAgentModel.id == agent_id)
            agent_result = await self.session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            
            logger.info(f"Contact personalization updated for user {user_id} and agent {agent_id}")
            return await self._build_enhanced_contact_info(contact, agent)
            
        except Exception as e:
            logger.error(f"Error updating contact personalization: {e}")
            raise

    async def validate_contact_permissions(
        self,
        user_id: UUID,
        agent_id: UUID,
        requested_permissions: List[str]
    ) -> Dict[str, bool]:
        """Validate what permissions a contact instance has."""
        try:
            contact = await self.contact_repo.get_user_contact_by_agent(user_id, agent_id)
            if not contact:
                return {permission: False for permission in requested_permissions}
            
            # Get agent details for base permissions
            agent_stmt = select(AIAgentModel).where(AIAgentModel.id == agent_id)
            agent_result = await self.session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            
            if not agent:
                return {permission: False for permission in requested_permissions}
            
            # Base permissions from agent
            base_permissions = set(agent.required_permissions or [])
            
            # Contact-specific resource limits
            contact_limits = contact.resource_limits or {}
            
            # Validate each requested permission
            permission_results = {}
            for permission in requested_permissions:
                # Check base agent permissions
                has_base_permission = permission in base_permissions
                
                # Check contact-specific restrictions
                is_restricted = self._check_permission_restriction(permission, contact_limits)
                
                permission_results[permission] = has_base_permission and not is_restricted
            
            return permission_results
            
        except Exception as e:
            logger.error(f"Error validating contact permissions: {e}")
            return {permission: False for permission in requested_permissions}

    def _check_permission_restriction(
        self, 
        permission: str, 
        resource_limits: Dict[str, Any]
    ) -> bool:
        """Check if a permission is restricted by contact-level resource limits."""
        # Example permission restrictions
        if permission == "file_access" and resource_limits.get("disable_file_access", False):
            return True
        if permission == "internet_access" and resource_limits.get("disable_internet", False):
            return True
        if permission == "code_execution" and resource_limits.get("disable_code_exec", False):
            return True
        
        return False

    async def get_contact_effective_config(
        self,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get the effective configuration for a contact instance (agent + personalization)."""
        try:
            contact = await self.contact_repo.get_user_contact_by_agent(user_id, agent_id)
            if not contact:
                return None
            
            # Get agent base configuration
            agent_stmt = select(AIAgentModel).where(AIAgentModel.id == agent_id)
            agent_result = await self.session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            
            if not agent:
                return None
            
            # Build effective configuration
            effective_config = {
                # Base agent configuration
                "system_prompt": contact.custom_system_prompt or agent.system_prompt,
                "model_preferences": {
                    **(agent.model_preferences or {}),
                    **(contact.instance_config or {})
                },
                "capabilities": agent.capabilities or [],
                "resource_limits": {
                    **(agent.resource_limits or {}),
                    **(contact.resource_limits or {})
                },
                "execution_config": agent.execution_config or {},
                "dependencies": agent.dependencies or {},
                
                # Contact-specific overrides
                "display_name": contact.display_name or agent.display_name,
                "is_active": not contact.is_blocked and not contact.is_muted,
                "notification_level": contact.notification_level,
                
                # Metadata
                "contact_created_at": contact.created_at,
                "contact_updated_at": contact.updated_at,
                "agent_version": agent.version
            }
            
            return effective_config
            
        except Exception as e:
            logger.error(f"Error getting contact effective config: {e}")
            return None
    
    async def _build_contact_info_from_participant(
        self,
        participant: ConversationParticipantModel
    ) -> Optional[ContactInfo]:
        """Build ContactInfo from conversation participant"""
        
        # Get the agent details
        agent_stmt = select(AIAgentModel).where(AIAgentModel.id == participant.participant_id)
        agent_result = await self.session.execute(agent_stmt)
        agent = agent_result.scalar_one_or_none()
        
        if not agent:
            return None
        
        # For conversation participants, we might not have the contact relationship
        # so we'll use default values
        return ContactInfo(
            contact_id=f"{participant.conversation_id}_{participant.participant_id}",
            agent_id=str(agent.id),
            follower_id="",  # We don't have this from participant model
            agent_name=agent.name,
            display_name=agent.display_name,
            system_prompt=agent.system_prompt,
            model_preferences=agent.model_preferences or {},
            is_active=True,
            resource_limits=None,
            custom_config=None,
            contact_notes=None
        )
    
    async def _build_contact_info_from_contact(
        self,
        contact: ContactModel,
        agent: Optional[AIAgentModel] = None
    ) -> ContactInfo:
        """Build ContactInfo from contact model"""
        
        if not agent:
            # Get agent details
            agent_stmt = select(AIAgentModel).where(AIAgentModel.id == contact.following_id)
            agent_result = await self.session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
        
        if not agent:
            raise ValueError(f"Agent {contact.following_id} not found")
        
        return ContactInfo(
            contact_id=f"{contact.follower_id}_{contact.following_id}",
            agent_id=str(agent.id),
            follower_id=str(contact.follower_id),
            agent_name=agent.name,
            display_name=contact.display_name or agent.display_name,
            system_prompt=contact.custom_system_prompt or agent.system_prompt,
            model_preferences={
                **(agent.model_preferences or {}),
                **(contact.instance_config or {})
            },
            is_active=not contact.is_blocked and not contact.is_muted,
            resource_limits=contact.resource_limits,
            custom_config=contact.instance_config,
            contact_notes=contact.notes
        )

    async def _build_enhanced_contact_info(
        self,
        contact: ContactModel,
        agent: Optional[AIAgentModel] = None
    ) -> ContactInfo:
        """Build enhanced ContactInfo with new personalization fields"""
        
        if not agent:
            # Get agent details
            agent_id = contact.agent_id or contact.following_id
            agent_stmt = select(AIAgentModel).where(AIAgentModel.id == agent_id)
            agent_result = await self.session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
        
        if not agent:
            raise ValueError(f"Agent not found for contact {contact.follower_id}")
        
        # Use custom system prompt if available, otherwise fall back to agent's
        effective_system_prompt = contact.custom_system_prompt or agent.system_prompt
        
        # Merge agent model preferences with contact instance config
        effective_model_preferences = {
            **(agent.model_preferences or {}),
            **(contact.instance_config or {})
        }
        
        return ContactInfo(
            contact_id=f"{contact.follower_id}_{agent.id}",
            agent_id=str(agent.id),
            follower_id=str(contact.follower_id),
            agent_name=agent.name,
            display_name=contact.display_name or agent.display_name,
            system_prompt=effective_system_prompt,
            model_preferences=effective_model_preferences,
            is_active=not contact.is_blocked and not contact.is_muted,
            # Additional fields for enhanced functionality
            resource_limits=contact.resource_limits,
            custom_config=contact.instance_config,
            contact_notes=contact.notes
        )
    
    async def add_contact_to_conversation(
        self,
        conversation_id: UUID,
        agent_id: UUID,
        invited_by: UUID,
        role: str = "member"
    ) -> bool:
        """Add a contact (agent) to a conversation"""
        
        # Check if participant already exists
        stmt = select(ConversationParticipantModel).where(
            and_(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.participant_id == agent_id,
                ConversationParticipantModel.participant_type == "agent"
            )
        )
        
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Reactivate if inactive
            if not existing.is_active:
                existing.is_active = True
                existing.joined_at = datetime.utcnow()
                return True
            return False
        
        # Create new participant
        participant = ConversationParticipantModel(
            conversation_id=conversation_id,
            participant_id=agent_id,
            participant_type="agent",
            role=role,
            invited_by=invited_by,
            joined_at=datetime.utcnow(),
            is_active=True
        )
        
        self.session.add(participant)
        return True
    
    async def remove_contact_from_conversation(
        self,
        conversation_id: UUID,
        agent_id: UUID
    ) -> bool:
        """Remove a contact (agent) from a conversation"""
        
        stmt = select(ConversationParticipantModel).where(
            and_(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.participant_id == agent_id,
                ConversationParticipantModel.participant_type == "agent"
            )
        )
        
        result = await self.session.execute(stmt)
        participant = result.scalar_one_or_none()
        
        if participant:
            participant.is_active = False
            return True
        
        return False