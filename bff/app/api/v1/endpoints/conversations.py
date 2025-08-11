"""
Conversation Management API Endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from app.api.dependencies import get_current_user
from app.infrastructure.database.connection import get_session
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    ConversationExportResponse,
    ConversationPinRequest,
    MessageResponse
)
from app.services.conversation_service import ConversationService
from app.infrastructure.database.models import UserModel

router = APIRouter()


@router.get("/", response_model=List[ConversationResponse])
async def get_user_conversations(
    skip: int = Query(0, ge=0, description="Skip conversations"),
    limit: int = Query(50, le=100, description="Limit conversations"),
    include_archived: bool = Query(False, description="Include archived conversations"),
    include_pinned_only: bool = Query(False, description="Only pinned conversations"),
    search: Optional[str] = Query(None, description="Search conversations"),
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Get user's conversations with optional filtering and search."""
    return await conversation_service.get_user_conversations(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_archived=include_archived,
        include_pinned_only=include_pinned_only,
        search=search
    )


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Create a new conversation."""
    return await conversation_service.create_conversation(
        user_id=current_user.id,
        conversation_data=conversation_data
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Get specific conversation details."""
    return await conversation_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    conversation_data: ConversationUpdate,
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Update conversation details."""
    return await conversation_service.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        conversation_data=conversation_data
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Delete a conversation."""
    await conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    return {"message": "Conversation deleted successfully"}


@router.post("/{conversation_id}/pin")
async def pin_conversation(
    conversation_id: UUID,
    pin_data: ConversationPinRequest,
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Pin or unpin a conversation for the user."""
    await conversation_service.toggle_pin_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        is_pinned=pin_data.is_pinned,
        pin_order=pin_data.pin_order
    )
    return {"message": f"Conversation {'pinned' if pin_data.is_pinned else 'unpinned'} successfully"}


@router.post("/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Archive a conversation for the user."""
    await conversation_service.archive_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    return {"message": "Conversation archived successfully"}


@router.post("/{conversation_id}/unarchive")
async def unarchive_conversation(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Unarchive a conversation for the user."""
    await conversation_service.unarchive_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    return {"message": "Conversation unarchived successfully"}


@router.post("/{conversation_id}/export", response_model=ConversationExportResponse)
async def export_conversation(
    conversation_id: UUID,
    format: str = Query("markdown", regex="^(markdown|json|txt)$"),
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Export conversation as Markdown, JSON, or plain text."""
    return await conversation_service.export_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        export_format=format
    )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    skip: int = Query(0, ge=0, description="Skip messages"),
    limit: int = Query(50, le=100, description="Limit messages"),
    before: Optional[UUID] = Query(None, description="Get messages before this message ID"),
    after: Optional[UUID] = Query(None, description="Get messages after this message ID"),
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Get messages from a conversation with pagination."""
    return await conversation_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        before_message_id=before,
        after_message_id=after
    )


@router.post("/{conversation_id}/participants/{participant_id}")
async def add_participant(
    conversation_id: UUID,
    participant_id: UUID,
    participant_type: str = Query(..., regex="^(user|agent)$"),
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Add a participant to the conversation."""
    await conversation_service.add_participant(
        conversation_id=conversation_id,
        participant_id=participant_id,
        participant_type=participant_type,
        inviter_id=current_user.id
    )
    return {"message": "Participant added successfully"}


@router.delete("/{conversation_id}/participants/{participant_id}")
async def remove_participant(
    conversation_id: UUID,
    participant_id: UUID,
    participant_type: str = Query(..., regex="^(user|agent)$"),
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Remove a participant from the conversation."""
    await conversation_service.remove_participant(
        conversation_id=conversation_id,
        participant_id=participant_id,
        participant_type=participant_type,
        remover_id=current_user.id
    )
    return {"message": "Participant removed successfully"}


@router.post("/{conversation_id}/read")
async def mark_as_read(
    conversation_id: UUID,
    message_id: Optional[UUID] = Query(None, description="Mark read up to this message"),
    current_user: UserModel = Depends(get_current_user),
    conversation_service: ConversationService = Depends()
):
    """Mark conversation as read up to a specific message."""
    await conversation_service.mark_as_read(
        conversation_id=conversation_id,
        user_id=current_user.id,
        message_id=message_id
    )
    return {"message": "Conversation marked as read"}