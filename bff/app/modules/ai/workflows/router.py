"""LangGraph enhanced conversation endpoints."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.deps.db import get_session
from app.modules.ai.workflows.conversation_service import ConversationService
from app.modules.users.models import UserModel

router = APIRouter(
    prefix="/conversations/langgraph",
    tags=["Conversations"],
)


class ChatMessageRequest(BaseModel):
    """Request model for sending chat messages."""

    content: str = Field(..., min_length=1, max_length=8000, description="Message content")
    message_type: str = Field(default="text", description="Message type")
    reply_to_id: Optional[UUID] = Field(default=None, description="ID of message being replied to")


class ConversationCreateRequest(BaseModel):
    """Request model for creating conversations with agents."""

    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    conversation_type: str = Field(default="chat", description="Type of conversation")
    initial_agent_ids: Optional[List[UUID]] = Field(default=None, description="Initial agent IDs to add")


class AddAgentRequest(BaseModel):
    """Request model for adding agents to conversation."""

    agent_id: UUID = Field(..., description="Agent ID to add")
    role: str = Field(default="member", description="Role for the agent")


class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""

    message_id: UUID
    workflow_execution_id: Optional[str] = None
    workflow_type: Optional[str] = None
    success: bool
    ai_responses: List[UUID]
    error: Optional[str] = None


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow execution status."""

    execution_id: str
    status: str  # pending, running, completed, failed
    workflow_type: str
    progress: Dict[str, Any]
    responses: Dict[str, Any]


@router.post("/conversations", response_model=Dict[str, Any])
async def create_enhanced_conversation(
    request: ConversationCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new conversation with LangGraph support."""

    service = ConversationService(session)

    try:
        result = await service.create_conversation(
            user_id=current_user.id,
            title=request.title,
            conversation_type=request.conversation_type,
            initial_agent_ids=request.initial_agent_ids,
        )

        return {"success": True, "conversation": result}

    except Exception as exc:  # pragma: no cover - defensive logging
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    conversation_id: UUID,
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Send a message to a conversation with LangGraph processing."""

    service = ConversationService(session)

    try:
        result = await service.send_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=request.content,
            message_type=request.message_type,
            reply_to_id=request.reply_to_id,
        )

        return ChatMessageResponse(
            message_id=result["message_id"],
            workflow_execution_id=result.get("workflow_result", {}).get("execution_id"),
            workflow_type=result.get("workflow_result", {}).get("workflow_type"),
            success=result["success"],
            ai_responses=result["ai_responses"],
            error=result.get("error"),
        )

    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail=f"Failed to send message: {str(exc)}"
        ) from exc


@router.get("/conversations/{conversation_id}/messages")
async def get_enhanced_messages(
    conversation_id: UUID,
    limit: int = Query(50, le=100, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get messages from a conversation with enhanced metadata."""

    service = ConversationService(session)

    try:
        messages = await service.get_conversation_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )

        return {
            "messages": messages,
            "total": len(messages),
            "has_more": len(messages) == limit,
        }

    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail=f"Failed to get messages: {str(exc)}"
        ) from exc


@router.post("/conversations/{conversation_id}/agents", response_model=Dict[str, Any])
async def add_agent_to_conversation(
    conversation_id: UUID,
    request: AddAgentRequest,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Add an agent to an existing conversation."""

    service = ConversationService(session)

    try:
        success = await service.add_agent_to_conversation(
            conversation_id=conversation_id,
            agent_id=request.agent_id,
            invited_by=current_user.id,
            role=request.role,
        )

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Agent already in conversation or invalid agent",
            )

        conversation = await service.get_conversation_details(
            conversation_id, current_user.id
        )

        return {
            "success": True,
            "message": "Agent added to conversation",
            "conversation": conversation,
        }

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail=f"Failed to add agent: {str(exc)}"
        ) from exc


@router.delete("/conversations/{conversation_id}/agents/{agent_id}")
async def remove_agent_from_conversation(
    conversation_id: UUID,
    agent_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Remove an agent from a conversation."""

    service = ConversationService(session)

    try:
        removed = await service.remove_agent_from_conversation(
            conversation_id=conversation_id,
            agent_id=agent_id,
            requested_by=current_user.id,
        )

        if not removed:
            raise HTTPException(status_code=404, detail="Agent not part of conversation")

        return {"success": True, "message": "Agent removed from conversation"}

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail=f"Failed to remove agent: {str(exc)}"
        ) from exc


@router.get("/workflows/{execution_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    execution_id: str,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get workflow execution status."""

    service = ConversationService(session)

    try:
        status_data = await service.get_workflow_status(
            execution_id=execution_id,
            user_id=current_user.id,
        )

        if not status_data:
            raise HTTPException(status_code=404, detail="Workflow execution not found")

        return WorkflowStatusResponse(**status_data)

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail=f"Failed to get workflow status: {str(exc)}"
        ) from exc


__all__ = [
    "router",
    "ChatMessageRequest",
    "ConversationCreateRequest",
    "AddAgentRequest",
    "ChatMessageResponse",
    "WorkflowStatusResponse",
]
