"""
Conversation Repository Implementation

This module provides the implementation of the conversation repository.
"""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.infrastructure.database.models.conversation_model import Conversation
from app.infrastructure.database.models.conversation_participant_model import ConversationParticipant
from app.infrastructure.database.models.message_model import Message
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ConversationRepository(BaseRepository[Conversation]):
    """Conversation repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)
    
    async def get_user_conversations(
        self,
        user_id: str,
        offset: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> List[Conversation]:
        """Get conversations for a specific user."""
        try:
            # Join with participants to find user's conversations
            statement = select(Conversation).join(
                ConversationParticipant,
                Conversation.id == ConversationParticipant.conversation_id
            ).where(
                ConversationParticipant.user_id == user_id
            )
            
            if only_active:
                statement = statement.where(Conversation.is_active == True)
            
            statement = statement.offset(offset).limit(limit).order_by(
                desc(Conversation.last_message_at),
                desc(Conversation.created_at)
            )
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting conversations for user {user_id}: {e}")
            raise
    
    async def get_conversation_with_participants(
        self,
        conversation_id: str
    ) -> Optional[Conversation]:
        """Get conversation with its participants loaded."""
        try:
            statement = select(Conversation).where(
                Conversation.id == conversation_id
            )
            
            result = await self.session.exec(statement)
            conversation = result.first()
            
            if conversation:
                # Load participants
                participants_statement = select(ConversationParticipant).where(
                    ConversationParticipant.conversation_id == conversation_id
                )
                participants_result = await self.session.exec(participants_statement)
                conversation.participants = participants_result.all()
            
            return conversation
        except Exception as e:
            self.logger.error(f"Error getting conversation with participants {conversation_id}: {e}")
            raise
    
    async def search_conversations(
        self,
        query: str,
        user_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Tuple[List[Conversation], int]:
        """Search conversations by title or description."""
        try:
            # Build search conditions
            search_conditions = [
                Conversation.title.ilike(f"%{query}%"),
                Conversation.description.ilike(f"%{query}%")
            ]
            
            statement = select(Conversation).where(
                and_(
                    or_(*search_conditions),
                    Conversation.is_active == True
                )
            )
            
            # Filter by user if specified
            if user_id:
                statement = statement.join(
                    ConversationParticipant,
                    Conversation.id == ConversationParticipant.conversation_id
                ).where(ConversationParticipant.user_id == user_id)
            
            # Get total count
            count_result = await self.session.exec(statement)
            total_count = len(count_result.all())
            
            # Apply pagination and ordering
            statement = statement.offset(offset).limit(limit).order_by(
                desc(Conversation.last_message_at),
                desc(Conversation.created_at)
            )
            
            result = await self.session.exec(statement)
            conversations = result.all()
            
            return conversations, total_count
        except Exception as e:
            self.logger.error(f"Error searching conversations with query '{query}': {e}")
            raise
    
    async def get_conversations_by_type(
        self,
        conversation_type: str,
        user_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """Get conversations by type."""
        try:
            statement = select(Conversation).where(
                and_(
                    Conversation.conversation_type == conversation_type,
                    Conversation.is_active == True
                )
            )
            
            # Filter by user if specified
            if user_id:
                statement = statement.join(
                    ConversationParticipant,
                    Conversation.id == ConversationParticipant.conversation_id
                ).where(ConversationParticipant.user_id == user_id)
            
            statement = statement.offset(offset).limit(limit).order_by(
                desc(Conversation.last_message_at),
                desc(Conversation.created_at)
            )
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting conversations by type '{conversation_type}': {e}")
            raise
    
    async def get_active_conversations(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """Get all active conversations."""
        try:
            statement = select(Conversation).where(
                Conversation.is_active == True
            ).offset(offset).limit(limit).order_by(
                desc(Conversation.last_message_at),
                desc(Conversation.created_at)
            )
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting active conversations: {e}")
            raise
    
    async def update_last_message_time(
        self,
        conversation_id: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Update the last message timestamp for a conversation."""
        try:
            conversation = await self.get_by_id(conversation_id)
            if not conversation:
                return False
            
            conversation.last_message_at = timestamp or datetime.now(timezone.utc)
            self.session.add(conversation)
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating last message time for conversation {conversation_id}: {e}")
            raise
    
    async def archive_conversation(self, conversation_id: str) -> bool:
        """Archive a conversation (set as inactive)."""
        try:
            conversation = await self.get_by_id(conversation_id)
            if not conversation:
                return False
            
            conversation.is_active = False
            conversation.archived_at = datetime.now(timezone.utc)
            self.session.add(conversation)
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error archiving conversation {conversation_id}: {e}")
            raise
    
    async def unarchive_conversation(self, conversation_id: str) -> bool:
        """Unarchive a conversation (set as active)."""
        try:
            conversation = await self.get_by_id(conversation_id)
            if not conversation:
                return False
            
            conversation.is_active = True
            conversation.archived_at = None
            self.session.add(conversation)
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error unarchiving conversation {conversation_id}: {e}")
            raise
    
    async def get_conversation_participants(
        self,
        conversation_id: str
    ) -> List[ConversationParticipant]:
        """Get all participants in a conversation."""
        try:
            statement = select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conversation_id
            ).order_by(ConversationParticipant.joined_at)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting participants for conversation {conversation_id}: {e}")
            raise
    
    async def add_participant(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        role: str = "participant"
    ) -> Optional[ConversationParticipant]:
        """Add a participant to a conversation."""
        try:
            participant_data = {
                "conversation_id": conversation_id,
                "role": role,
                "joined_at": datetime.now(timezone.utc)
            }
            
            if user_id:
                participant_data["user_id"] = user_id
            elif agent_id:
                participant_data["agent_id"] = agent_id
            else:
                raise ValueError("Either user_id or agent_id must be provided")
            
            participant = ConversationParticipant(**participant_data)
            self.session.add(participant)
            await self.session.flush()
            await self.session.refresh(participant)
            return participant
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error adding participant to conversation {conversation_id}: {e}")
            raise
    
    async def remove_participant(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> bool:
        """Remove a participant from a conversation."""
        try:
            conditions = [ConversationParticipant.conversation_id == conversation_id]
            
            if user_id:
                conditions.append(ConversationParticipant.user_id == user_id)
            elif agent_id:
                conditions.append(ConversationParticipant.agent_id == agent_id)
            else:
                raise ValueError("Either user_id or agent_id must be provided")
            
            statement = select(ConversationParticipant).where(and_(*conditions))
            result = await self.session.exec(statement)
            participant = result.first()
            
            if participant:
                await self.session.delete(participant)
                await self.session.flush()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error removing participant from conversation {conversation_id}: {e}")
            raise
    
    async def is_user_participant(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Check if a user is a participant in a conversation."""
        try:
            statement = select(ConversationParticipant).where(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user_id
                )
            )
            
            result = await self.session.exec(statement)
            return result.first() is not None
        except Exception as e:
            self.logger.error(f"Error checking user participation in conversation {conversation_id}: {e}")
            raise