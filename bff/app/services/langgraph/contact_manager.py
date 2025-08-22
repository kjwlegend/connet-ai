"""
Contact Instance Manager

Manages the mapping between Agent definitions and Contact instances,
providing the personalized agent configurations for conversations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database.models.contact_model import ContactModel, EntityType
from app.infrastructure.database.models.agent_model import AIAgentModel
from app.infrastructure.database.models.conversation_participant_model import ConversationParticipantModel
from app.services.langgraph.state_models import ContactInfo


class ContactInstanceManager:
    """Manager for Contact instances in LangGraph workflows"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
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
            is_active=True
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
            system_prompt=agent.system_prompt,
            model_preferences=agent.model_preferences or {},
            is_active=not contact.is_blocked and not contact.is_muted
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