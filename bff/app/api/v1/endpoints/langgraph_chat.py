"""
LangGraph Enhanced Chat API Endpoints

Provides enhanced chat functionality with multi-agent workflows.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.infrastructure.database.connection import get_session
from app.infrastructure.database.models import UserModel
from app.services.langgraph.conversation_service import ConversationService
from app.services.langgraph.contact_manager import ContactInstanceManager
from app.services.langgraph.workflow_engine import WorkflowEngine
from app.services.langgraph.mention_parser import MentionParser
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class ChatMessageRequest(BaseModel):
    """Request model for sending chat messages"""
    content: str = Field(..., min_length=1, max_length=8000, description="Message content")
    message_type: str = Field(default="text", description="Message type")
    reply_to_id: Optional[UUID] = Field(default=None, description="ID of message being replied to")


class ConversationCreateRequest(BaseModel):
    """Request model for creating conversations with agents"""
    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    conversation_type: str = Field(default="chat", description="Type of conversation")
    initial_agent_ids: Optional[List[UUID]] = Field(default=None, description="Initial agent IDs to add")


class AddAgentRequest(BaseModel):
    """Request model for adding agents to conversation"""
    agent_id: UUID = Field(..., description="Agent ID to add")
    role: str = Field(default="member", description="Role for the agent")


class ChatMessageResponse(BaseModel):
    """Response model for chat messages"""
    message_id: UUID
    workflow_execution_id: Optional[str] = None
    workflow_type: Optional[str] = None
    success: bool
    ai_responses: List[UUID]
    error: Optional[str] = None


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow execution status"""
    execution_id: str
    status: str  # pending, running, completed, failed
    workflow_type: str
    progress: Dict[str, Any]
    responses: Dict[str, Any]


@router.post("/conversations", response_model=Dict[str, Any])
async def create_enhanced_conversation(
    request: ConversationCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a new conversation with LangGraph support"""
    
    service = ConversationService(session)
    
    try:
        result = await service.create_conversation(
            user_id=current_user.id,
            title=request.title,
            conversation_type=request.conversation_type,
            initial_agent_ids=request.initial_agent_ids
        )
        
        return {
            "success": True,
            "conversation": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    conversation_id: UUID,
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Send a message to a conversation with LangGraph processing"""
    
    service = ConversationService(session)
    
    try:
        # Send message and process through workflow
        result = await service.send_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=request.content,
            message_type=request.message_type,
            reply_to_id=request.reply_to_id
        )
        
        return ChatMessageResponse(
            message_id=result["message_id"],
            workflow_execution_id=result.get("workflow_result", {}).get("execution_id"),
            workflow_type=result.get("workflow_result", {}).get("workflow_type"),
            success=result["success"],
            ai_responses=result["ai_responses"],
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/conversations/{conversation_id}/messages")
async def get_enhanced_messages(
    conversation_id: UUID,
    limit: int = Query(50, le=100, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get messages from a conversation with enhanced metadata"""
    
    service = ConversationService(session)
    
    try:
        messages = await service.get_conversation_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "messages": messages,
            "total": len(messages),
            "has_more": len(messages) == limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.post("/conversations/{conversation_id}/agents", response_model=Dict[str, Any])
async def add_agent_to_conversation(
    conversation_id: UUID,
    request: AddAgentRequest,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add an agent to an existing conversation"""
    
    service = ConversationService(session)
    
    try:
        success = await service.add_agent_to_conversation(
            conversation_id=conversation_id,
            agent_id=request.agent_id,
            invited_by=current_user.id,
            role=request.role
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Agent already in conversation or invalid agent")
        
        # Get updated conversation details
        conversation = await service.get_conversation_details(conversation_id, current_user.id)
        
        return {
            "success": True,
            "message": "Agent added to conversation",
            "conversation": conversation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add agent: {str(e)}")


@router.delete("/conversations/{conversation_id}/agents/{agent_id}")
async def remove_agent_from_conversation(
    conversation_id: UUID,
    agent_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Remove an agent from a conversation"""
    
    service = ConversationService(session)
    
    try:
        success = await service.remove_agent_from_conversation(
            conversation_id=conversation_id,
            agent_id=agent_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found in conversation")
        
        return {
            "success": True,
            "message": "Agent removed from conversation"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove agent: {str(e)}")


@router.get("/conversations/{conversation_id}/participants")
async def get_conversation_participants(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all participants in a conversation"""
    
    service = ConversationService(session)
    
    try:
        participants = await service.get_conversation_participants(conversation_id)
        
        return {
            "participants": participants,
            "total": len(participants)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get participants: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_enhanced_conversation_details(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get detailed conversation information"""
    
    service = ConversationService(session)
    
    try:
        conversation = await service.get_conversation_details(conversation_id, current_user.id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
        return {
            "conversation": conversation,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.post("/mentions/validate")
async def validate_mentions(
    content: str = Query(..., description="Message content to validate"),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Validate @mentions in a message"""
    
    try:
        parser = MentionParser()
        contact_manager = ContactInstanceManager(session)
        
        # Extract mentions
        mentions = parser.extract_mentions(content)
        
        if not mentions:
            return {
                "valid": True,
                "mentions": [],
                "invalid_mentions": []
            }
        
        # Get user's contacts for mentioned agents
        mentioned_contacts = await contact_manager.get_mentioned_contacts(
            current_user.id, mentions
        )
        
        valid_mentions = [c["agent_name"] for c in mentioned_contacts]
        invalid_mentions = [m for m in mentions if m not in valid_mentions]
        
        return {
            "valid": len(invalid_mentions) == 0,
            "mentions": valid_mentions,
            "invalid_mentions": invalid_mentions,
            "suggestion_message": parser._build_validation_message(invalid_mentions) if invalid_mentions else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate mentions: {str(e)}")


@router.get("/user/contacts")
async def get_user_agent_contacts(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get user's agent contacts for @mention suggestions"""
    
    try:
        contact_manager = ContactInstanceManager(session)
        
        # This would need to be implemented in ContactInstanceManager
        # For now, return empty list
        return {
            "contacts": [],
            "total": 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contacts: {str(e)}")


# WebSocket endpoint for real-time workflow updates would go here
# This would require WebSocket support to be added to the application
@router.get("/workflows/{execution_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    execution_id: str,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get the status of a workflow execution"""
    
    # This would require implementing workflow status tracking
    # For now, return a placeholder response
    return WorkflowStatusResponse(
        execution_id=execution_id,
        status="completed",
        workflow_type="single_contact",
        progress={"completed": True},
        responses={}
    )