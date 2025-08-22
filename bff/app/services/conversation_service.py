"""
Conversation Service

This service handles conversation management operations including CRUD,
pinning, archiving, exporting, and participant management.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, select, and_, or_, desc, func

from app.services.base import BaseRepositoryService
from app.infrastructure.database.models import (
    ConversationModel,
    ConversationParticipantModel, 
    MessageModel,
    UserModel,
    AIAgentModel
)
# ConversationUserSettingModel not yet enabled
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationExportResponse,
    MessageResponse
)
from app.infrastructure.cache.cache_decorators import cached
from app.utils.constants import (
    CONVERSATION_EXPORT_FORMATS,
    DEFAULT_CONVERSATION_SETTINGS
)


class ConversationService(BaseRepositoryService):
    """Service for conversation management operations."""

    async def get_user_conversations(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        include_archived: bool = False,
        include_pinned_only: bool = False,
        search: Optional[str] = None
    ) -> List[ConversationResponse]:
        """Get user's conversations with optional filtering."""
        
        # Build the query
        query = (
            select(ConversationModel, ConversationUserSettingModel)
            .join(
                ConversationParticipantModel,
                ConversationModel.id == ConversationParticipantModel.conversation_id
            )
            .join(
                ConversationUserSettingModel,
                and_(
                    ConversationModel.id == ConversationUserSettingModel.conversation_id,
                    ConversationUserSettingModel.user_id == user_id
                ),
                isouter=True
            )
            .where(
                and_(
                    ConversationParticipantModel.participant_id == user_id,
                    ConversationParticipantModel.participant_type == "user",
                    ConversationParticipantModel.is_active == True
                )
            )
        )

        # Apply filters
        if not include_archived:
            query = query.where(
                or_(
                    ConversationUserSettingModel.is_archived == False,
                    ConversationUserSettingModel.is_archived.is_(None)
                )
            )

        if include_pinned_only:
            query = query.where(ConversationUserSettingModel.is_pinned == True)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    ConversationModel.title.ilike(search_term),
                    ConversationUserSettingModel.custom_title.ilike(search_term)
                )
            )

        # Order by pinned status first, then by last message time
        query = query.order_by(
            desc(ConversationUserSettingModel.is_pinned.nullslast()),
            ConversationUserSettingModel.pin_order.asc().nullslast(),
            desc(ConversationModel.last_message_at)
        )

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        results = await self.session.execute(query)
        conversations_data = results.all()

        # Convert to response format
        conversations = []
        for conv_model, user_settings in conversations_data:
            # Get participants
            participants = await self._get_conversation_participants(conv_model.id)
            
            # Build response
            conversation_response = ConversationResponse(
                id=conv_model.id,
                title=user_settings.custom_title if user_settings and user_settings.custom_title else conv_model.title,
                conversation_type=conv_model.conversation_type,
                is_group=conv_model.is_group,
                created_by=conv_model.created_by,
                created_at=conv_model.created_at,
                updated_at=conv_model.updated_at,
                last_message_at=conv_model.last_message_at,
                
                # User-specific settings
                is_pinned=user_settings.is_pinned if user_settings else False,
                pin_order=user_settings.pin_order if user_settings else 0,
                is_archived=user_settings.is_archived if user_settings else False,
                unread_count=user_settings.unread_count if user_settings else 0,
                notifications_enabled=user_settings.notifications_enabled if user_settings else True,
                custom_title=user_settings.custom_title if user_settings else None,
                
                # Statistics
                participants=participants,
                participant_count=conv_model.participant_count,
                message_count=conv_model.message_count,
                export_count=conv_model.export_count,
                last_exported_at=conv_model.last_exported_at,
                
                # Content
                summary=conv_model.summary,
                settings=conv_model.settings,
                status=conv_model.status
            )
            
            # Get last message preview
            if conv_model.last_message_id:
                conversation_response.last_message_preview = await self._get_message_preview(
                    conv_model.last_message_id
                )
            
            conversations.append(conversation_response)

        return conversations

    async def create_conversation(
        self,
        user_id: UUID,
        conversation_data: ConversationCreate
    ) -> ConversationResponse:
        """Create a new conversation."""
        
        # Create conversation
        conversation = ConversationModel(
            title=conversation_data.title,
            conversation_type=conversation_data.conversation_type,
            is_group=conversation_data.is_group,
            created_by=user_id,
            settings=conversation_data.settings or DEFAULT_CONVERSATION_SETTINGS,
            participant_count=len(conversation_data.participants) + 1  # +1 for creator
        )
        
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)

        # Add creator as participant
        creator_participant = ConversationParticipantModel(
            conversation_id=conversation.id,
            participant_id=user_id,
            participant_type="user",
            role="owner"
        )
        self.session.add(creator_participant)

        # Add other participants
        for participant_data in conversation_data.participants:
            participant = ConversationParticipantModel(
                conversation_id=conversation.id,
                participant_id=participant_data["id"],
                participant_type=participant_data["type"],
                role="member",
                invited_by=user_id
            )
            self.session.add(participant)

        # Create user settings for the creator
        user_settings = ConversationUserSettingModel(
            conversation_id=conversation.id,
            user_id=user_id
        )
        self.session.add(user_settings)

        await self.session.commit()

        # Send initial message if provided
        if conversation_data.initial_message:
            await self._create_initial_message(
                conversation.id,
                user_id,
                conversation_data.initial_message
            )

        # Return the created conversation
        return await self.get_conversation(conversation.id, user_id)

    async def get_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> ConversationResponse:
        """Get specific conversation details."""
        
        # Check if user has access to the conversation
        participant_query = select(ConversationParticipantModel).where(
            and_(
                ConversationParticipantModel.conversation_id == conversation_id,
                ConversationParticipantModel.participant_id == user_id,
                ConversationParticipantModel.participant_type == "user",
                ConversationParticipantModel.is_active == True
            )
        )
        
        participant_result = await self.session.execute(participant_query)
        participant = participant_result.scalar_one_or_none()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )

        # Get conversation and user settings
        conv_query = select(ConversationModel).where(ConversationModel.id == conversation_id)
        conv_result = await self.session.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get user settings
        settings_query = select(ConversationUserSettingModel).where(
            and_(
                ConversationUserSettingModel.conversation_id == conversation_id,
                ConversationUserSettingModel.user_id == user_id
            )
        )
        settings_result = await self.session.execute(settings_query)
        user_settings = settings_result.scalar_one_or_none()

        # Get participants
        participants = await self._get_conversation_participants(conversation_id)

        # Build response
        response = ConversationResponse(
            id=conversation.id,
            title=user_settings.custom_title if user_settings and user_settings.custom_title else conversation.title,
            conversation_type=conversation.conversation_type,
            is_group=conversation.is_group,
            created_by=conversation.created_by,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at,
            
            # User-specific settings
            is_pinned=user_settings.is_pinned if user_settings else False,
            pin_order=user_settings.pin_order if user_settings else 0,
            is_archived=user_settings.is_archived if user_settings else False,
            unread_count=user_settings.unread_count if user_settings else 0,
            notifications_enabled=user_settings.notifications_enabled if user_settings else True,
            custom_title=user_settings.custom_title if user_settings else None,
            
            # Content
            participants=participants,
            participant_count=conversation.participant_count,
            message_count=conversation.message_count,
            export_count=conversation.export_count,
            last_exported_at=conversation.last_exported_at,
            summary=conversation.summary,
            settings=conversation.settings,
            status=conversation.status
        )

        return response

    async def toggle_pin_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        is_pinned: bool,
        pin_order: int = 0
    ) -> None:
        """Pin or unpin a conversation for a user."""
        
        # Get or create user settings
        settings = await self._get_or_create_user_settings(conversation_id, user_id)
        
        settings.is_pinned = is_pinned
        settings.pin_order = pin_order if is_pinned else 0
        settings.pinned_at = datetime.utcnow() if is_pinned else None
        settings.updated_at = datetime.utcnow()
        
        await self.session.commit()

    async def export_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        export_format: str = "markdown"
    ) -> ConversationExportResponse:
        """Export conversation in specified format."""
        
        if export_format not in CONVERSATION_EXPORT_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid export format. Supported formats: {', '.join(CONVERSATION_EXPORT_FORMATS)}"
            )

        # Check access
        conversation = await self.get_conversation(conversation_id, user_id)
        
        # Get all messages
        messages = await self.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=10000  # Get all messages
        )

        # Generate export content based on format
        if export_format == "markdown":
            content = await self._export_to_markdown(conversation, messages)
            filename = f"{conversation.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        elif export_format == "json":
            content = await self._export_to_json(conversation, messages)
            filename = f"{conversation.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:  # txt
            content = await self._export_to_text(conversation, messages)
            filename = f"{conversation.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Update export count
        await self._update_export_count(conversation_id)

        return ConversationExportResponse(
            conversation_id=conversation_id,
            export_format=export_format,
            content=content,
            filename=filename,
            created_at=datetime.utcnow()
        )

    async def _get_conversation_participants(self, conversation_id: UUID) -> List[Dict[str, Any]]:
        """Get conversation participants with their details."""
        # Implementation would fetch participants and their details
        # This is a simplified version
        return []

    async def _get_message_preview(self, message_id: UUID) -> Optional[str]:
        """Get a preview of the message content."""
        query = select(MessageModel.content).where(MessageModel.id == message_id)
        result = await self.session.execute(query)
        content = result.scalar_one_or_none()
        
        if content and len(content) > 100:
            return content[:97] + "..."
        return content

    async def _get_or_create_user_settings(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> ConversationUserSettingModel:
        """Get or create user settings for a conversation."""
        query = select(ConversationUserSettingModel).where(
            and_(
                ConversationUserSettingModel.conversation_id == conversation_id,
                ConversationUserSettingModel.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = ConversationUserSettingModel(
                conversation_id=conversation_id,
                user_id=user_id
            )
            self.session.add(settings)
        
        return settings

    async def _export_to_markdown(self, conversation: ConversationResponse, messages: List[MessageResponse]) -> str:
        """Export conversation to Markdown format."""
        lines = [
            f"# {conversation.title}",
            "",
            f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Participants:** {conversation.participant_count}",
            f"**Messages:** {len(messages)}",
            "",
            "---",
            ""
        ]

        for message in messages:
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            lines.extend([
                f"## {message.sender_name} - {timestamp}",
                "",
                message.content,
                ""
            ])

        return "\n".join(lines)

    async def _export_to_json(self, conversation: ConversationResponse, messages: List[MessageResponse]) -> str:
        """Export conversation to JSON format."""
        import json
        
        data = {
            "conversation": conversation.dict(),
            "messages": [message.dict() for message in messages],
            "exported_at": datetime.utcnow().isoformat()
        }
        
        return json.dumps(data, indent=2, default=str)

    async def _export_to_text(self, conversation: ConversationResponse, messages: List[MessageResponse]) -> str:
        """Export conversation to plain text format."""
        lines = [
            f"Conversation: {conversation.title}",
            f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Participants: {conversation.participant_count}",
            f"Messages: {len(messages)}",
            "",
            "=" * 50,
            ""
        ]

        for message in messages:
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            lines.extend([
                f"[{timestamp}] {message.sender_name}:",
                message.content,
                ""
            ])

        return "\n".join(lines)

    async def _update_export_count(self, conversation_id: UUID) -> None:
        """Update conversation export count."""
        query = select(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await self.session.execute(query)
        conversation = result.scalar_one()
        
        conversation.export_count += 1
        conversation.last_exported_at = datetime.utcnow()
        
        await self.session.commit()