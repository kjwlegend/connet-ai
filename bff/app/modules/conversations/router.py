"""API endpoints for conversations and conversation messages."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.api.deps.services import (
    get_conversation_service,
)
from app.modules.conversations.schemas import (
    ConversationCreate,
    ConversationExportResponse,
    ConversationPinRequest,
    ConversationResponse,
    ConversationUpdate,
)
from app.modules.conversations.messages.schemas import MessageResponse
from app.modules.conversations.service import ConversationService
from app.modules.users.schemas import User

router = APIRouter()


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_archived: bool = Query(False),
    include_pinned_only: bool = Query(False),
    search: Optional[str] = Query(None, min_length=1),
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> List[ConversationResponse]:
    return await conversation_service.list_conversations(
        user_id=UUID(str(current_user.id)),
        skip=skip,
        limit=limit,
        include_archived=include_archived,
        include_pinned_only=include_pinned_only,
        search=search,
    )


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    return await conversation_service.create_conversation(
        user_id=UUID(str(current_user.id)),
        conversation_data=payload,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def retrieve_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    return await conversation_service.get_conversation(
        conversation_id=conversation_id,
        user_id=UUID(str(current_user.id)),
    )


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    return await conversation_service.update_conversation(
        conversation_id=conversation_id,
        user_id=UUID(str(current_user.id)),
        conversation_data=payload,
    )


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> None:
    await conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=UUID(str(current_user.id)),
    )


@router.post("/{conversation_id}/pin", status_code=204)
async def pin_conversation(
    conversation_id: UUID,
    payload: ConversationPinRequest,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> None:
    await conversation_service.toggle_pin_conversation(
        conversation_id=conversation_id,
        user_id=UUID(str(current_user.id)),
        pin_request=payload,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageResponse],
)
async def conversation_messages(
    conversation_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    before: Optional[UUID] = Query(None),
    after: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    return await conversation_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=UUID(str(current_user.id)),
        skip=skip,
        limit=limit,
        before_message_id=before,
        after_message_id=after,
    )


@router.post("/{conversation_id}/participants/{participant_id}", status_code=204)
async def add_participant(
    conversation_id: UUID,
    participant_id: UUID,
    participant_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> None:
    await conversation_service.add_participant(
        conversation_id=conversation_id,
        inviter_id=UUID(str(current_user.id)),
        participant_id=participant_id,
        participant_type=participant_type,
    )


@router.delete("/{conversation_id}/participants/{participant_id}", status_code=204)
async def remove_participant(
    conversation_id: UUID,
    participant_id: UUID,
    participant_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> None:
    await conversation_service.remove_participant(
        conversation_id=conversation_id,
        remover_id=UUID(str(current_user.id)),
        participant_id=participant_id,
        participant_type=participant_type,
    )


@router.post("/{conversation_id}/read", status_code=204)
async def mark_read(
    conversation_id: UUID,
    message_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> None:
    await conversation_service.mark_as_read(
        conversation_id=conversation_id,
        user_id=UUID(str(current_user.id)),
        message_id=message_id,
    )


@router.get("/{conversation_id}/export", response_model=ConversationExportResponse)
async def export_conversation(
    conversation_id: UUID,
    format: str = Query("markdown", pattern="^(markdown|json|txt)$"),
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationExportResponse:
    return await conversation_service.export_conversation(
        conversation_id=conversation_id,
        user_id=UUID(str(current_user.id)),
        export_format=format,
    )
