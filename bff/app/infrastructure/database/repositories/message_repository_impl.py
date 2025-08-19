"""
Message Repository Implementation

This module provides the implementation of the message repository.
"""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import select, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.infrastructure.database.models.message_model import Message
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MessageRepository(BaseRepository[Message]):
    """Message repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        offset: int = 0,
        limit: int = 100,
        order_desc: bool = True
    ) -> List[Message]:
        """Get messages for a specific conversation."""
        try:
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).offset(offset).limit(limit)
            
            if order_desc:
                statement = statement.order_by(desc(Message.created_at))
            else:
                statement = statement.order_by(asc(Message.created_at))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting messages for conversation {conversation_id}: {e}")
            raise
    
    async def get_messages_after_timestamp(
        self,
        conversation_id: str,
        timestamp: datetime,
        limit: int = 100
    ) -> List[Message]:
        """Get messages after a specific timestamp."""
        try:
            statement = select(Message).where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.created_at > timestamp
                )
            ).order_by(asc(Message.created_at)).limit(limit)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting messages after timestamp for conversation {conversation_id}: {e}")
            raise
    
    async def get_messages_before_timestamp(
        self,
        conversation_id: str,
        timestamp: datetime,
        limit: int = 100
    ) -> List[Message]:
        """Get messages before a specific timestamp."""
        try:
            statement = select(Message).where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.created_at < timestamp
                )
            ).order_by(desc(Message.created_at)).limit(limit)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting messages before timestamp for conversation {conversation_id}: {e}")
            raise
    
    async def get_user_messages(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages sent by a specific user."""
        try:
            conditions = [Message.sender_user_id == user_id]
            
            if conversation_id:
                conditions.append(Message.conversation_id == conversation_id)
            
            statement = select(Message).where(
                and_(*conditions)
            ).offset(offset).limit(limit).order_by(desc(Message.created_at))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting messages for user {user_id}: {e}")
            raise
    
    async def get_agent_messages(
        self,
        agent_id: str,
        conversation_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages sent by a specific agent."""
        try:
            conditions = [Message.sender_agent_id == agent_id]
            
            if conversation_id:
                conditions.append(Message.conversation_id == conversation_id)
            
            statement = select(Message).where(
                and_(*conditions)
            ).offset(offset).limit(limit).order_by(desc(Message.created_at))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting messages for agent {agent_id}: {e}")
            raise
    
    async def search_messages(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Tuple[List[Message], int]:
        """Search messages by content."""
        try:
            conditions = [Message.content.ilike(f"%{query}%")]
            
            if conversation_id:
                conditions.append(Message.conversation_id == conversation_id)
            
            if user_id:
                conditions.append(Message.sender_user_id == user_id)
            
            statement = select(Message).where(and_(*conditions))
            
            # Get total count
            count_result = await self.session.exec(statement)
            total_count = len(count_result.all())
            
            # Apply pagination and ordering
            statement = statement.offset(offset).limit(limit).order_by(desc(Message.created_at))
            
            result = await self.session.exec(statement)
            messages = result.all()
            
            return messages, total_count
        except Exception as e:
            self.logger.error(f"Error searching messages with query '{query}': {e}")
            raise
    
    async def get_messages_by_type(
        self,
        message_type: str,
        conversation_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages by type."""
        try:
            conditions = [Message.message_type == message_type]
            
            if conversation_id:
                conditions.append(Message.conversation_id == conversation_id)
            
            statement = select(Message).where(
                and_(*conditions)
            ).offset(offset).limit(limit).order_by(desc(Message.created_at))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting messages by type '{message_type}': {e}")
            raise
    
    async def get_messages_with_mentions(
        self,
        mention: str,
        conversation_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages that mention a specific user or agent."""
        try:
            conditions = [Message.mentions.contains([mention])]
            
            if conversation_id:
                conditions.append(Message.conversation_id == conversation_id)
            
            statement = select(Message).where(
                and_(*conditions)
            ).offset(offset).limit(limit).order_by(desc(Message.created_at))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting messages with mention '{mention}': {e}")
            raise
    
    async def get_thread_messages(
        self,
        thread_id: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages in a specific thread."""
        try:
            statement = select(Message).where(
                Message.thread_id == thread_id
            ).offset(offset).limit(limit).order_by(asc(Message.created_at))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting thread messages for {thread_id}: {e}")
            raise
    
    async def get_replies_to_message(
        self,
        message_id: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get replies to a specific message."""
        try:
            statement = select(Message).where(
                Message.in_reply_to_message_id == message_id
            ).offset(offset).limit(limit).order_by(asc(Message.created_at))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting replies to message {message_id}: {e}")
            raise
    
    async def get_latest_message_in_conversation(
        self,
        conversation_id: str
    ) -> Optional[Message]:
        """Get the latest message in a conversation."""
        try:
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(desc(Message.created_at)).limit(1)
            
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            self.logger.error(f"Error getting latest message in conversation {conversation_id}: {e}")
            raise
    
    async def count_messages_in_conversation(
        self,
        conversation_id: str,
        after_timestamp: Optional[datetime] = None
    ) -> int:
        """Count messages in a conversation."""
        try:
            conditions = [Message.conversation_id == conversation_id]
            
            if after_timestamp:
                conditions.append(Message.created_at > after_timestamp)
            
            return await self.count(
                conversation_id=conversation_id,
                **({"created_at__gt": after_timestamp} if after_timestamp else {})
            )
        except Exception as e:
            self.logger.error(f"Error counting messages in conversation {conversation_id}: {e}")
            raise
    
    async def mark_message_as_edited(
        self,
        message_id: str,
        new_content: str
    ) -> Optional[Message]:
        """Mark a message as edited with new content."""
        try:
            message = await self.get_by_id(message_id)
            if not message:
                return None
            
            message.content = new_content
            message.is_edited = True
            message.edited_at = datetime.now(timezone.utc)
            
            self.session.add(message)
            await self.session.flush()
            await self.session.refresh(message)
            return message
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error marking message as edited {message_id}: {e}")
            raise
    
    async def delete_message(
        self,
        message_id: str,
        soft_delete: bool = True
    ) -> bool:
        """Delete a message (soft delete by default)."""
        try:
            message = await self.get_by_id(message_id)
            if not message:
                return False
            
            if soft_delete:
                message.is_deleted = True
                message.deleted_at = datetime.now(timezone.utc)
                message.content = "[Message deleted]"
                self.session.add(message)
            else:
                await self.session.delete(message)
            
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting message {message_id}: {e}")
            raise