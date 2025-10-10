"""Business logic for conversations."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.agents.service import AIAgentService
from app.modules.conversations.messages.schemas import MessageCreate, MessageResponse
from app.modules.conversations.messages.service import MessageService
from app.modules.conversations.models import (
    ConversationModel,
    ConversationParticipantModel,
    ConversationUserSettingModel,
)
from app.modules.conversations.repository import ConversationRepositoryProtocol
from app.modules.conversations.schemas import (
    ConversationCreate,
    ConversationExportResponse,
    ConversationParticipantResponse,
    ConversationPinRequest,
    ConversationResponse,
    ConversationUpdate,
)
from app.modules.users.service import UserService


class ConversationService:
    """Coordinates conversation-level operations."""

    def __init__(
        self,
        conversation_repository: ConversationRepositoryProtocol,
        message_service: MessageService,
        user_service: Optional[UserService] = None,
        agent_service: Optional[AIAgentService] = None,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.message_service = message_service
        self.user_service = user_service
        self.agent_service = agent_service

    async def list_conversations(
        self,
        *,
        user_id: UUID,
        skip: int,
        limit: int,
        include_archived: bool,
        include_pinned_only: bool,
        search: Optional[str],
    ) -> List[ConversationResponse]:
        rows = await self.conversation_repository.list_for_user(
            user_id=user_id,
            include_archived=include_archived,
            pinned_only=include_pinned_only,
            search=search,
            skip=skip,
            limit=limit,
        )

        responses: List[ConversationResponse] = []
        for conversation, settings in rows:
            participants = await self._load_participants(conversation.id)
            last_preview = None
            if conversation.last_message_id:
                last_preview = await self.message_service.get_message_preview(
                    conversation.last_message_id
                )
            responses.append(
                self._to_response(
                    conversation=conversation,
                    settings=settings,
                    participants=participants,
                    last_preview=last_preview,
                )
            )
        return responses

    async def create_conversation(
        self,
        *,
        user_id: UUID,
        conversation_data: ConversationCreate,
    ) -> ConversationResponse:
        conversation = ConversationModel(
            title=conversation_data.title,
            conversation_type=conversation_data.conversation_type,
            is_group=conversation_data.is_group,
            created_by=user_id,
            settings=conversation_data.settings,
        )
        conversation = await self.conversation_repository.create(conversation)

        creator_participant = ConversationParticipantModel(
            conversation_id=conversation.id,
            participant_id=user_id,
            participant_type="user",
            role="owner",
        )
        await self.conversation_repository.add_participant(creator_participant)

        participant_delta = 1
        for participant in conversation_data.participants:
            participant_delta += 1
            await self.conversation_repository.add_participant(
                ConversationParticipantModel(
                    conversation_id=conversation.id,
                    participant_id=UUID(str(participant["id"])),
                    participant_type=participant.get("type", "user"),
                    role="member",
                    invited_by=user_id,
                )
            )

        await self.conversation_repository.adjust_counts(
            conversation.id, participant_delta=participant_delta
        )

        creator_settings = ConversationUserSettingModel(
            conversation_id=conversation.id,
            user_id=user_id,
        )
        await self.conversation_repository.upsert_user_settings(creator_settings)

        if conversation_data.initial_message:
            await self.message_service.create_message(
                conversation_id=conversation.id,
                sender_id=user_id,
                sender_type="user",
                payload=MessageCreate(
                    conversation_id=conversation.id,
                    content=conversation_data.initial_message,
                    message_type="text",
                ),
            )

        return await self.get_conversation(conversation_id=conversation.id, user_id=user_id)

    async def get_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> ConversationResponse:
        record = await self.conversation_repository.get_for_user(conversation_id, user_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        conversation, settings = record
        participants = await self._load_participants(conversation_id)
        last_preview = None
        if conversation.last_message_id:
            last_preview = await self.message_service.get_message_preview(conversation.last_message_id)
        return self._to_response(
            conversation=conversation,
            settings=settings,
            participants=participants,
            last_preview=last_preview,
        )

    async def update_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        conversation_data: ConversationUpdate,
    ) -> ConversationResponse:
        record = await self.conversation_repository.get_for_user(conversation_id, user_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        conversation, settings = record

        if conversation_data.title is not None:
            conversation.title = conversation_data.title
        if conversation_data.settings is not None:
            conversation.settings = conversation_data.settings
        if conversation_data.summary is not None:
            conversation.summary = conversation_data.summary
        conversation.updated_at = datetime.utcnow()

        updated = await self.conversation_repository.save(conversation)
        participants = await self._load_participants(conversation_id)
        last_preview = None
        if updated.last_message_id:
            last_preview = await self.message_service.get_message_preview(updated.last_message_id)
        return self._to_response(
            conversation=updated,
            settings=settings,
            participants=participants,
            last_preview=last_preview,
        )

    async def delete_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> None:
        record = await self.conversation_repository.get_for_user(conversation_id, user_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        conversation, _ = record
        conversation.status = "deleted"
        conversation.updated_at = datetime.utcnow()
        await self.conversation_repository.save(conversation)

    async def toggle_pin_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        pin_request: ConversationPinRequest,
    ) -> None:
        settings = await self.conversation_repository.get_user_settings(conversation_id, user_id)
        if not settings:
            settings = ConversationUserSettingModel(conversation_id=conversation_id, user_id=user_id)
        settings.is_pinned = pin_request.is_pinned
        settings.pin_order = pin_request.pin_order if pin_request.is_pinned else 0
        settings.pinned_at = datetime.utcnow() if pin_request.is_pinned else None
        settings.updated_at = datetime.utcnow()
        await self.conversation_repository.upsert_user_settings(settings)

    async def export_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        export_format: str,
    ) -> ConversationExportResponse:
        conversation = await self.get_conversation(conversation_id=conversation_id, user_id=user_id)
        messages = await self.message_service.list_all_for_export(
            conversation_id=conversation_id, user_id=user_id
        )

        if export_format not in {"markdown", "json", "txt"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported export format")

        rendered: str
        if export_format == "markdown":
            rendered = self._render_markdown(conversation, messages)
            extension = "md"
        elif export_format == "json":
            rendered = self._render_json(conversation, messages)
            extension = "json"
        else:
            rendered = self._render_text(conversation, messages)
            extension = "txt"

        await self.conversation_repository.increment_export(conversation_id)
        filename = f"{conversation.title.replace(' ', '_')}_{datetime.utcnow():%Y%m%d_%H%M%S}.{extension}"
        return ConversationExportResponse(
            conversation_id=conversation_id,
            export_format=export_format,
            content=rendered,
            filename=filename,
            created_at=datetime.utcnow(),
        )

    async def get_conversation_messages(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        skip: int,
        limit: int,
        before_message_id: Optional[UUID],
        after_message_id: Optional[UUID],
    ) -> List[MessageResponse]:
        return await self.message_service.list_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            skip=skip,
            limit=limit,
            before_id=before_message_id,
            after_id=after_message_id,
        )

    async def add_participant(
        self,
        *,
        conversation_id: UUID,
        inviter_id: UUID,
        participant_id: UUID,
        participant_type: str,
    ) -> None:
        if not await self.conversation_repository.is_user_participant(conversation_id, inviter_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        participant = ConversationParticipantModel(
            conversation_id=conversation_id,
            participant_id=participant_id,
            participant_type=participant_type,
            invited_by=inviter_id,
        )
        await self.conversation_repository.add_participant(participant)
        await self.conversation_repository.adjust_counts(
            conversation_id, participant_delta=1
        )

    async def remove_participant(
        self,
        *,
        conversation_id: UUID,
        remover_id: UUID,
        participant_id: UUID,
        participant_type: str,
    ) -> None:
        if not await self.conversation_repository.is_user_participant(conversation_id, remover_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        removed = await self.conversation_repository.remove_participant(
            conversation_id, participant_id, participant_type
        )
        if removed:
            await self.conversation_repository.adjust_counts(
                conversation_id, participant_delta=-1
            )

    async def mark_as_read(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        message_id: Optional[UUID],
    ) -> None:
        await self.conversation_repository.mark_read(
            conversation_id,
            user_id,
            message_id=message_id,
            read_at=datetime.utcnow(),
        )

    async def _load_participants(
        self, conversation_id: UUID
    ) -> List[ConversationParticipantResponse]:
        participants = await self.conversation_repository.list_participants(conversation_id)
        responses: List[ConversationParticipantResponse] = []
        for participant in participants:
            display_name: Optional[str] = None
            avatar_url: Optional[str] = None
            if participant.participant_type == "user" and self.user_service:
                user = await self.user_service.get_user_by_id(str(participant.participant_id))
                if user:
                    display_name = user.full_name or user.username or user.email
                    avatar_url = getattr(user, "avatar_url", None)
            elif participant.participant_type == "agent" and self.agent_service:
                agent = await self.agent_service.get_agent(participant.participant_id)
                if agent:
                    display_name = getattr(agent, "name", None)
                    avatar_url = getattr(agent, "avatar", None)
            responses.append(
                ConversationParticipantResponse(
                    participant_id=participant.participant_id,
                    participant_type=participant.participant_type,
                    role=participant.role,
                    display_name=display_name,
                    avatar_url=avatar_url,
                    is_active=participant.is_active,
                    joined_at=participant.joined_at,
                    last_read_at=participant.last_read_at,
                )
            )
        return responses

    def _to_response(
        self,
        *,
        conversation: ConversationModel,
        settings: Optional[ConversationUserSettingModel],
        participants: List[ConversationParticipantResponse],
        last_preview: Optional[str],
    ) -> ConversationResponse:
        return ConversationResponse(
            id=conversation.id,
            title=settings.custom_title if settings and settings.custom_title else conversation.title,
            conversation_type=conversation.conversation_type,
            is_group=conversation.is_group,
            created_by=conversation.created_by,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at,
            last_message_preview=last_preview,
            is_pinned=settings.is_pinned if settings else False,
            pin_order=settings.pin_order if settings else 0,
            is_archived=settings.is_archived if settings else False,
            unread_count=settings.unread_count if settings else 0,
            notifications_enabled=settings.notifications_enabled if settings else True,
            custom_title=settings.custom_title if settings else None,
            participants=participants,
            participant_count=conversation.participant_count or len(participants),
            message_count=conversation.message_count,
            export_count=conversation.export_count,
            last_exported_at=conversation.last_exported_at,
            summary=conversation.summary,
            settings=conversation.settings,
            status=conversation.status,
        )

    def _render_markdown(
        self,
        conversation: ConversationResponse,
        messages: List[MessageResponse],
    ) -> str:
        lines = [
            f"# {conversation.title}",
            "",
            f"**Created:** {conversation.created_at:%Y-%m-%d %H:%M:%S}",
            f"**Participants:** {conversation.participant_count}",
            f"**Messages:** {len(messages)}",
            "",
            "---",
            "",
        ]
        for message in messages:
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = message.sender_name or str(message.sender_id)
            lines.extend([f"## {author} - {timestamp}", "", message.content, ""])
        return "\n".join(lines)

    def _render_json(
        self,
        conversation: ConversationResponse,
        messages: List[MessageResponse],
    ) -> str:
        import json

        payload = {
            "conversation": conversation.model_dump(),
            "messages": [message.model_dump() for message in messages],
            "exported_at": datetime.utcnow().isoformat(),
        }
        return json.dumps(payload, indent=2)

    def _render_text(
        self,
        conversation: ConversationResponse,
        messages: List[MessageResponse],
    ) -> str:
        lines = [
            f"Conversation: {conversation.title}",
            f"Created: {conversation.created_at:%Y-%m-%d %H:%M:%S}",
            f"Participants: {conversation.participant_count}",
            f"Messages: {len(messages)}",
            "",
            "=" * 50,
            "",
        ]
        for message in messages:
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = message.sender_name or str(message.sender_id)
            lines.extend([f"[{timestamp}] {author}:", message.content, ""])
        return "\n".join(lines)


__all__ = ["ConversationService"]
