"""
LangGraph-enhanced Conversation Service

Handles conversation creation, message processing, and participant management
with LangGraph workflow integration.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.modules.conversations.models import (
    ConversationModel,
    ConversationParticipantModel,
    MessageModel,
)
from app.modules.users.models import UserModel
from app.modules.ai.workflows.workflow_engine import WorkflowEngine
from app.modules.ai.workflows.contact_manager import ContactInstanceManager
from app.services.base import BaseService


class ConversationService(BaseService):
    """Enhanced conversation service with LangGraph integration"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.workflow_engine = WorkflowEngine(session)
        self.contact_manager = ContactInstanceManager(session)
    
    async def create_conversation(
        self,
        user_id: UUID,
        title: str,
        conversation_type: str = "chat",
        initial_agent_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """Create a new conversation with optional initial agents"""
        
        # Create conversation
        conversation = ConversationModel(
            id=uuid4(),
            title=title,
            conversation_type=conversation_type,
            created_by=user_id,
            is_group=bool(initial_agent_ids and len(initial_agent_ids) > 1),
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.session.add(conversation)
        await self.session.flush()
        
        # Add user as participant
        user_participant = ConversationParticipantModel(
            conversation_id=conversation.id,
            participant_id=user_id,
            participant_type="user",
            role="owner",
            joined_at=datetime.utcnow(),
            is_active=True
        )
        
        self.session.add(user_participant)
        
        # Add initial agents if provided
        if initial_agent_ids:
            for agent_id in initial_agent_ids:
                await self.add_agent_to_conversation(conversation.id, agent_id, user_id)
        
        await self.session.commit()
        
        return {
            "conversation_id": conversation.id,
            "title": conversation.title,
            "conversation_type": conversation.conversation_type,
            "is_group": conversation.is_group,
            "created_at": conversation.created_at,
            "participant_count": len(initial_agent_ids) + 1 if initial_agent_ids else 1
        }
    
    async def add_agent_to_conversation(
        self,
        conversation_id: UUID,
        agent_id: UUID,
        invited_by: UUID,
        role: str = "member"
    ) -> bool:
        """Add an agent to a conversation"""
        
        # Use contact manager to add the agent
        success = await self.contact_manager.add_contact_to_conversation(
            conversation_id, agent_id, invited_by, role
        )
        
        if success:
            # Update conversation participant count
            await self._update_conversation_stats(conversation_id)
            await self.session.commit()
        
        return success
    
    async def remove_agent_from_conversation(
        self,
        conversation_id: UUID,
        agent_id: UUID
    ) -> bool:
        """Remove an agent from a conversation"""
        
        success = await self.contact_manager.remove_contact_from_conversation(
            conversation_id, agent_id
        )
        
        if success:
            await self._update_conversation_stats(conversation_id)
            await self.session.commit()
        
        return success
    
    async def send_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        content: str,
        message_type: str = "text",
        reply_to_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Send a message and process it through LangGraph workflow"""
        
        # Create message record
        message = MessageModel(
            id=uuid4(),
            conversation_id=conversation_id,
            sender_id=user_id,
            sender_type="user",
            content=content,
            message_type=message_type,
            reply_to_id=reply_to_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.session.add(message)
        await self.session.flush()
        
        # Update conversation last message
        await self._update_conversation_last_message(conversation_id, message.id)
        
        await self.session.commit()
        
        # Process message through workflow engine
        try:
            workflow_result = await self.workflow_engine.execute_conversation_workflow(
                conversation_id=conversation_id,
                user_id=user_id,
                message=content,
                message_id=message.id
            )
            
            # Save AI responses as messages
            ai_message_ids = await self._save_ai_responses(
                conversation_id, workflow_result["contact_responses"]
            )
            
            return {
                "message_id": message.id,
                "workflow_result": workflow_result,
                "ai_responses": ai_message_ids,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Workflow processing failed: {e}", extra={
                "conversation_id": str(conversation_id),
                "message_id": str(message.id),
                "error": str(e)
            })
            
            return {
                "message_id": message.id,
                "workflow_result": None,
                "ai_responses": [],
                "success": False,
                "error": str(e)
            }
    
    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages from a conversation"""
        
        stmt = (
            select(MessageModel)
            .where(
                and_(
                    MessageModel.conversation_id == conversation_id,
                    MessageModel.is_deleted == False
                )
            )
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        
        # Format messages
        formatted_messages = []
        for message in reversed(messages):  # Reverse to get chronological order
            formatted_messages.append({
                "id": message.id,
                "content": message.content,
                "sender_id": message.sender_id,
                "sender_type": message.sender_type,
                "message_type": message.message_type,
                "reply_to_id": message.reply_to_id,
                "agent_mentions": message.agent_mentions,
                "tokens_used": message.tokens_used,
                "created_at": message.created_at,
                "is_edited": message.is_edited
            })
        
        return formatted_messages
    
    async def get_conversation_participants(
        self,
        conversation_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all participants in a conversation"""
        
        stmt = (
            select(ConversationParticipantModel)
            .where(
                and_(
                    ConversationParticipantModel.conversation_id == conversation_id,
                    ConversationParticipantModel.is_active == True
                )
            )
            .order_by(ConversationParticipantModel.joined_at)
        )
        
        result = await self.session.execute(stmt)
        participants = result.scalars().all()
        
        formatted_participants = []
        for participant in participants:
            # Get participant details based on type
            if participant.participant_type == "user":
                user_stmt = select(UserModel).where(UserModel.id == participant.participant_id)
                user_result = await self.session.execute(user_stmt)
                user = user_result.scalar_one_or_none()
                
                if user:
                    formatted_participants.append({
                        "id": participant.participant_id,
                        "type": "user",
                        "name": user.username,
                        "display_name": user.full_name,
                        "role": participant.role,
                        "joined_at": participant.joined_at,
                        "is_active": participant.is_active
                    })
            
            elif participant.participant_type == "agent":
                # Get agent details through contact manager
                contact_info = await self.contact_manager._build_contact_info_from_participant(participant)
                if contact_info:
                    formatted_participants.append({
                        "id": participant.participant_id,
                        "type": "agent",
                        "name": contact_info["agent_name"],
                        "display_name": contact_info["display_name"],
                        "role": participant.role,
                        "joined_at": participant.joined_at,
                        "is_active": participant.is_active
                    })
        
        return formatted_participants
    
    async def get_conversation_details(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get detailed conversation information"""
        
        # Check if user is participant
        participant_stmt = select(ConversationParticipantModel).where(
            and_(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.participant_id == user_id,
                ConversationParticipantModel.participant_type == "user",
                ConversationParticipantModel.is_active == True
            )
        )
        
        participant_result = await self.session.execute(participant_stmt)
        if not participant_result.scalar_one_or_none():
            return None  # User not in conversation
        
        # Get conversation details
        conv_stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        conv_result = await self.session.execute(conv_stmt)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            return None
        
        # Get participants
        participants = await self.get_conversation_participants(conversation_id)
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "conversation_type": conversation.conversation_type,
            "is_group": conversation.is_group,
            "status": conversation.status,
            "created_by": conversation.created_by,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "last_message_at": conversation.last_message_at,
            "message_count": conversation.message_count,
            "participant_count": conversation.participant_count,
            "participants": participants
        }
    
    async def _save_ai_responses(
        self,
        conversation_id: UUID,
        contact_responses: Dict[str, Dict[str, Any]]
    ) -> List[UUID]:
        """Save AI responses as messages"""
        
        message_ids = []
        
        for contact_id, response in contact_responses.items():
            if response["status"] == "success" and response["response"]:
                # Create AI message
                ai_message = MessageModel(
                    id=uuid4(),
                    conversation_id=conversation_id,
                    sender_id=UUID(response["agent_id"]),
                    sender_type="agent",
                    content=response["response"],
                    message_type="text",
                    tokens_used=response.get("tokens_used"),
                    ai_context={
                        "contact_id": contact_id,
                        "workflow_execution": True
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.session.add(ai_message)
                message_ids.append(ai_message.id)
        
        if message_ids:
            await self.session.flush()
            # Update conversation with last AI message
            await self._update_conversation_last_message(conversation_id, message_ids[-1])
        
        return message_ids
    
    async def _update_conversation_last_message(
        self,
        conversation_id: UUID,
        message_id: UUID
    ):
        """Update conversation's last message info"""
        
        stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await self.session.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if conversation:
            conversation.last_message_id = message_id
            conversation.last_message_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()
    
    async def _update_conversation_stats(self, conversation_id: UUID):
        """Update conversation statistics"""
        
        # Count participants
        participant_count_stmt = (
            select(func.count(ConversationParticipantModel.participant_id))
            .where(
                and_(
                    ConversationParticipantModel.conversation_id == conversation_id,
                    ConversationParticipantModel.is_active == True
                )
            )
        )
        
        result = await self.session.execute(participant_count_stmt)
        participant_count = result.scalar()
        
        # Count messages
        message_count_stmt = (
            select(func.count(MessageModel.id))
            .where(
                and_(
                    MessageModel.conversation_id == conversation_id,
                    MessageModel.is_deleted == False
                )
            )
        )
        
        result = await self.session.execute(message_count_stmt)
        message_count = result.scalar()
        
        # Update conversation
        conv_stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        conv_result = await self.session.execute(conv_stmt)
        conversation = conv_result.scalar_one_or_none()
        
        if conversation:
            conversation.participant_count = participant_count
            conversation.message_count = message_count
            conversation.is_group = participant_count > 2  # User + 1 agent = 2
            conversation.updated_at = datetime.utcnow()
