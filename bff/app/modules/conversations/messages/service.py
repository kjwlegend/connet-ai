"""Business logic for conversation messages."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.agents.service import AIAgentService
from app.modules.conversations.messages.models import MessageModel
from app.modules.conversations.messages.repository import MessageRepositoryProtocol
from app.modules.conversations.messages.schemas import MessageCreate, MessageResponse
from app.modules.conversations.repository import ConversationRepositoryProtocol
from app.modules.users.service import UserService


class MessageService:
    """Coordinates message persistence and presentation."""

    def __init__(
        self,
        message_repository: MessageRepositoryProtocol,
        conversation_repository: ConversationRepositoryProtocol,
        user_service: Optional[UserService] = None,
        agent_service: Optional[AIAgentService] = None,
    ) -> None:
        self.message_repository = message_repository
        self.conversation_repository = conversation_repository
        self.user_service = user_service
        self.agent_service = agent_service

    async def list_messages(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        skip: int,
        limit: int,
        before_id: Optional[UUID],
        after_id: Optional[UUID],
    ) -> List[MessageResponse]:
        if not await self.conversation_repository.is_user_participant(conversation_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        messages = await self.message_repository.list_for_conversation(
            conversation_id,
            skip=skip,
            limit=limit,
            before_id=before_id,
            after_id=after_id,
        )
        return [await self._to_response(message) for message in messages]

    async def list_all_for_export(
        self, *, conversation_id: UUID, user_id: UUID
    ) -> List[MessageResponse]:
        if not await self.conversation_repository.is_user_participant(conversation_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        messages = await self.message_repository.list_all(conversation_id)
        return [await self._to_response(message) for message in messages]

    async def create_message(
        self,
        *,
        conversation_id: UUID,
        sender_id: UUID,
        sender_type: str,
        payload: MessageCreate,
    ) -> MessageResponse:
        if not await self.conversation_repository.is_user_participant(conversation_id, sender_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        message = MessageModel(
            conversation_id=conversation_id,
            sender_id=sender_id,
            sender_type=sender_type,
            content=payload.content,
            message_type=payload.message_type,
            reply_to_id=payload.reply_to_id,
            thread_id=payload.thread_id,
            agent_mentions=list(payload.mentions or []),
            attachments=list(payload.attachments or []),
            message_metadata=payload.metadata,
        )

        created = await self.message_repository.create(message)
        await self.conversation_repository.adjust_counts(
            conversation_id, message_delta=1
        )
        await self.conversation_repository.update_last_message(
            conversation_id,
            message_id=created.id,
            message_at=created.created_at,
        )
        return await self._to_response(created)

    async def get_message_preview(self, message_id: UUID) -> Optional[str]:
        message = await self.message_repository.get(message_id)
        if not message or message.is_deleted:
            return None
        if len(message.content) <= 120:
            return message.content
        return f"{message.content[:117]}..."

    async def _to_response(self, message: MessageModel) -> MessageResponse:
        sender_name: Optional[str] = None
        sender_avatar: Optional[str] = None

        if message.sender_type == "user" and self.user_service:
            user = await self.user_service.get_user_by_id(str(message.sender_id))
            if user:
                sender_name = user.full_name or user.username or user.email
                sender_avatar = user.avatar_url if hasattr(user, "avatar_url") else None
        elif message.sender_type == "agent" and self.agent_service:
            agent = await self.agent_service.get_agent(message.sender_id)
            if agent:
                sender_name = getattr(agent, "name", None)
                sender_avatar = getattr(agent, "avatar", None)

        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            sender_type=message.sender_type,
            sender_name=sender_name,
            sender_avatar_url=sender_avatar,
            content=message.content,
            message_type=message.message_type,
            edited=message.is_edited,
            edited_at=message.edited_at,
            created_at=message.created_at,
            updated_at=message.updated_at,
            attachments=list(message.attachments or []),
            mentions=list(message.agent_mentions or []),
            ai_context=message.ai_context,
            status="deleted" if message.is_deleted else "sent",
            is_system_message=message.is_system,
            metadata=message.message_metadata,
        )


__all__ = ["MessageService"]
