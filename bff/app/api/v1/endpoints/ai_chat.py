"""AI Chat API endpoints for conversational interactions."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    MemoryCreate,
    MemoryResponse,
    ConversationSummaryResponse,
    AIErrorResponse,
)
from app.schemas.user import UserResponse
from app.services.ai_memory_service import AIMemoryService
from app.services.ai_agent_service import AIAgentService

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with AI Agent",
    description="Send messages to an AI agent and get responses",
)
async def chat_with_agent(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    """Chat with an AI agent."""

    try:
        # Verify agent exists and user has access
        agent_service = AIAgentService(db)
        agent = await agent_service.get_agent(request.agent_id, current_user.id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or access denied",
            )

        # Get memory service for context
        memory_service = AIMemoryService(db)

        # Get conversation context if conversation_id provided
        context_memories = []
        if request.conversation_id:
            context_memories = await memory_service.get_contextual_memories(
                user_id=current_user.id,
                conversation_id=request.conversation_id,
                current_context=(
                    request.messages[-1].content if request.messages else ""
                ),
                max_memories=10,
            )

        # TODO: Implement actual LLM integration
        # For now, return a mock response

        # Store user message in short-term memory
        if request.conversation_id and request.messages:
            user_message = request.messages[-1]
            if user_message.role == "user":
                await memory_service.store_short_term_memory(
                    conversation_id=request.conversation_id,
                    content=user_message.content,
                    user_id=current_user.id,
                    agent_id=request.agent_id,
                )

        # Generate mock response
        response_content = await _generate_mock_response(
            request, agent, context_memories
        )

        # Store assistant response in short-term memory
        if request.conversation_id:
            await memory_service.store_short_term_memory(
                conversation_id=request.conversation_id,
                content=response_content,
                user_id=current_user.id,
                agent_id=request.agent_id,
            )

        # Update agent usage statistics
        await agent_service.update_usage_stats(request.agent_id, 1.5, True)

        return ChatResponse(
            conversation_id=request.conversation_id
            or UUID("00000000-0000-0000-0000-000000000000"),
            message_id=UUID("00000000-0000-0000-0000-000000000001"),
            agent_id=request.agent_id,
            content=response_content,
            role="assistant",
            model_used=agent.model_preferences.get("default_model", "gpt-3.5-turbo"),
            token_usage={
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
            generation_time=1.5,
            tools_used=[],
            context_sources=[
                {
                    "type": "memory",
                    "content": (
                        memory.content[:100] + "..."
                        if len(memory.content) > 100
                        else memory.content
                    ),
                    "relevance_score": memory.importance_score,
                }
                for memory in context_memories[:3]
            ],
            confidence_score=0.85,
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}",
        )


@router.get(
    "/conversations/{conversation_id}/context",
    response_model=List[MemoryResponse],
    summary="Get Conversation Context",
    description="Get recent context for a conversation",
)
async def get_conversation_context(
    conversation_id: UUID,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of context items"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[MemoryResponse]:
    """Get conversation context."""

    try:
        memory_service = AIMemoryService(db)
        return await memory_service.get_conversation_context(conversation_id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation context: {str(e)}",
        )


@router.post(
    "/conversations/{conversation_id}/memories",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Memory",
    description="Create a memory entry for a conversation",
)
async def create_memory(
    conversation_id: UUID,
    memory_data: MemoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> MemoryResponse:
    """Create a memory entry."""

    try:
        # Ensure conversation_id matches
        memory_data.conversation_id = conversation_id

        memory_service = AIMemoryService(db)
        return await memory_service.create_memory(memory_data, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create memory: {str(e)}",
        )


@router.get(
    "/conversations/{conversation_id}/memories",
    response_model=List[MemoryResponse],
    summary="Get Conversation Memories",
    description="Get memories for a conversation",
)
async def get_conversation_memories(
    conversation_id: UUID,
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of memories"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[MemoryResponse]:
    """Get memories for a conversation."""

    try:
        memory_service = AIMemoryService(db)

        if memory_type:
            from app.schemas.ai import MemoryType

            memory_type_enum = MemoryType(memory_type)
        else:
            memory_type_enum = None

        return await memory_service.get_user_memories(
            user_id=current_user.id, memory_type=memory_type_enum, limit=limit
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid memory type: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memories: {str(e)}",
        )


@router.get(
    "/memories/search",
    response_model=List[MemoryResponse],
    summary="Search Memories",
    description="Search user's memories",
)
async def search_memories(
    q: str = Query(..., description="Search query"),
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    conversation_id: Optional[UUID] = Query(None, description="Filter by conversation"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[MemoryResponse]:
    """Search memories."""

    try:
        memory_service = AIMemoryService(db)

        if memory_type:
            from app.schemas.ai import MemoryType

            memory_type_enum = MemoryType(memory_type)
        else:
            memory_type_enum = None

        return await memory_service.search_memories(
            user_id=current_user.id,
            query=q,
            memory_type=memory_type_enum,
            conversation_id=conversation_id,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid memory type: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search memories: {str(e)}",
        )


@router.post(
    "/conversations/{conversation_id}/summarize",
    response_model=ConversationSummaryResponse,
    summary="Summarize Conversation",
    description="Create a summary of conversation memories",
)
async def summarize_conversation(
    conversation_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ConversationSummaryResponse:
    """Summarize conversation."""

    try:
        memory_service = AIMemoryService(db)
        summary = await memory_service.compress_short_to_medium_term(conversation_id)

        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No memories found to summarize for this conversation",
            )

        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize conversation: {str(e)}",
        )


@router.get(
    "/conversations/{conversation_id}/summaries",
    response_model=List[ConversationSummaryResponse],
    summary="Get Conversation Summaries",
    description="Get summaries for a conversation",
)
async def get_conversation_summaries(
    conversation_id: UUID,
    limit: Optional[int] = Query(
        10, ge=1, le=50, description="Maximum number of summaries"
    ),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[ConversationSummaryResponse]:
    """Get conversation summaries."""

    try:
        memory_service = AIMemoryService(db)
        return await memory_service.get_conversation_summaries(conversation_id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation summaries: {str(e)}",
        )


@router.get(
    "/summaries/search",
    response_model=List[ConversationSummaryResponse],
    summary="Search Summaries",
    description="Search conversation summaries",
)
async def search_summaries(
    q: str = Query(..., description="Search query"),
    conversation_id: Optional[UUID] = Query(None, description="Filter by conversation"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[ConversationSummaryResponse]:
    """Search conversation summaries."""

    try:
        memory_service = AIMemoryService(db)
        return await memory_service.search_conversation_summaries(
            q, conversation_id, limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search summaries: {str(e)}",
        )


@router.get(
    "/statistics",
    response_model=dict,
    summary="Get Memory Statistics",
    description="Get memory usage statistics for current user",
)
async def get_memory_statistics(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get memory statistics."""

    try:
        memory_service = AIMemoryService(db)
        return await memory_service.get_memory_statistics(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory statistics: {str(e)}",
        )


# Helper functions


async def _generate_mock_response(
    request: ChatRequest, agent, context_memories: List[MemoryResponse]
) -> str:
    """Generate mock AI response (to be replaced with actual LLM integration)."""

    user_message = request.messages[-1].content if request.messages else ""
    agent_name = agent.display_name

    # Use context from memories
    context_info = ""
    if context_memories:
        context_info = (
            f" (I remember we discussed: {context_memories[0].content[:50]}...)"
        )

    # Simple rule-based responses for demo
    if "hello" in user_message.lower() or "hi" in user_message.lower():
        return f"Hello! I'm {agent_name}, your AI assistant. How can I help you today?{context_info}"
    elif "weather" in user_message.lower():
        return f"I'd be happy to help with weather information! However, I would need to use a weather tool to get current conditions. Would you like me to check the weather for a specific location?"
    elif "?" in user_message:
        return f"That's an interesting question! Based on my knowledge and our previous discussions{context_info}, let me provide you with some insights..."
    else:
        return f"I understand you're saying: '{user_message}'. As {agent_name}, I'm here to assist you with various tasks.{context_info} What would you like to do next?"


# Import datetime at the top of the file
from datetime import datetime
