"""AI Tools API endpoints for tool management and execution."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.schemas.ai import (
    ToolCreate,
    ToolResponse,
    ToolExecutionRequest,
    ToolExecutionResponse,
    PaginationParams,
    AIErrorResponse
)
from app.schemas.user import UserResponse
from app.services.ai_tool_service import AIToolService

router = APIRouter(prefix="/ai/tools", tags=["AI Tools"])


@router.post(
    "/",
    response_model=ToolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Tool",
    description="Create a new AI tool"
)
async def create_tool(
    tool_data: ToolCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> ToolResponse:
    """Create a new AI tool."""
    
    try:
        service = AIToolService(db)
        return await service.create_tool(tool_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tool: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[ToolResponse],
    summary="List Tools",
    description="List available AI tools with optional filtering"
)
async def list_tools(
    tool_type: Optional[str] = Query(None, description="Filter by tool type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    my_tools: bool = Query(False, description="Show only user's tools"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[ToolResponse]:
    """List AI tools."""
    
    try:
        pagination = PaginationParams(
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        service = AIToolService(db)
        tools, total = await service.list_tools(
            tool_type=tool_type,
            category=category,
            status=status,
            user_id=current_user.id if my_tools else None,
            pagination=pagination
        )
        
        return tools
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get(
    "/{tool_id}",
    response_model=ToolResponse,
    summary="Get Tool",
    description="Get tool by ID"
)
async def get_tool(
    tool_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> ToolResponse:
    """Get tool by ID."""
    
    try:
        service = AIToolService(db)
        tool = await service.get_tool(tool_id)
        
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found"
            )
        
        return tool
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool: {str(e)}"
        )


@router.get(
    "/by-name/{tool_name}",
    response_model=ToolResponse,
    summary="Get Tool by Name",
    description="Get tool by name"
)
async def get_tool_by_name(
    tool_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> ToolResponse:
    """Get tool by name."""
    
    try:
        service = AIToolService(db)
        tool = await service.get_tool_by_name(tool_name)
        
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found"
            )
        
        return tool
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool: {str(e)}"
        )


@router.delete(
    "/{tool_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Tool",
    description="Delete a tool"
)
async def delete_tool(
    tool_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a tool."""
    
    try:
        service = AIToolService(db)
        success = await service.delete_tool(tool_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found or permission denied"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tool: {str(e)}"
        )


@router.post(
    "/execute",
    response_model=ToolExecutionResponse,
    summary="Execute Tool",
    description="Execute a tool with given parameters"
)
async def execute_tool(
    request: ToolExecutionRequest,
    conversation_id: UUID = Query(..., description="Conversation ID for context"),
    agent_id: Optional[UUID] = Query(None, description="Agent ID if executed by agent"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> ToolExecutionResponse:
    """Execute a tool."""
    
    try:
        service = AIToolService(db)
        return await service.execute_tool(
            request=request,
            conversation_id=conversation_id,
            user_id=current_user.id,
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )


@router.get(
    "/executions/{execution_id}",
    response_model=dict,
    summary="Get Execution Status",
    description="Get tool execution status"
)
async def get_execution_status(
    execution_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get execution status."""
    
    try:
        service = AIToolService(db)
        status_info = await service.get_execution_status(execution_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )
        
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution status: {str(e)}"
        )


@router.get(
    "/executions/conversation/{conversation_id}",
    response_model=List[dict],
    summary="Get Conversation Executions",
    description="Get tool executions for a conversation"
)
async def get_conversation_executions(
    conversation_id: UUID,
    limit: Optional[int] = Query(50, ge=1, le=200, description="Maximum number of executions"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get executions for a conversation."""
    
    try:
        service = AIToolService(db)
        return await service.get_conversation_executions(conversation_id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation executions: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=dict,
    summary="Get Tool Statistics",
    description="Get tool usage statistics"
)
async def get_tool_statistics(
    tool_id: Optional[UUID] = Query(None, description="Filter by specific tool"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get tool usage statistics."""
    
    try:
        service = AIToolService(db)
        return await service.get_execution_statistics(
            tool_id=tool_id,
            user_id=current_user.id,
            days=days
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool statistics: {str(e)}"
        )


# Built-in tools endpoints

@router.post(
    "/web-search",
    response_model=dict,
    summary="Web Search",
    description="Perform web search using built-in search tool"
)
async def web_search(
    query: str = Query(..., description="Search query"),
    num_results: int = Query(10, ge=1, le=50, description="Number of results"),
    language: str = Query("en", description="Search language"),
    safe_search: bool = Query(True, description="Enable safe search"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Perform web search."""
    
    try:
        request = ToolExecutionRequest(
            tool_name="web_search",
            parameters={
                "query": query,
                "num_results": num_results,
                "language": language,
                "safe_search": safe_search
            }
        )
        
        service = AIToolService(db)
        result = await service.execute_tool(
            request=request,
            conversation_id=UUID('00000000-0000-0000-0000-000000000000'),  # Default conversation
            user_id=current_user.id
        )
        
        return result.result if result.success else {"error": result.error_message}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {str(e)}"
        )


@router.post(
    "/api-call",
    response_model=dict,
    summary="API Call",
    description="Make HTTP API call using built-in API tool"
)
async def api_call(
    url: str = Query(..., description="API endpoint URL"),
    method: str = Query("GET", regex="^(GET|POST|PUT|DELETE|PATCH)$", description="HTTP method"),
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Make API call."""
    
    try:
        request = ToolExecutionRequest(
            tool_name="api_call",
            parameters={
                "url": url,
                "method": method,
                "headers": headers or {},
                "data": data
            }
        )
        
        service = AIToolService(db)
        result = await service.execute_tool(
            request=request,
            conversation_id=UUID('00000000-0000-0000-0000-000000000000'),  # Default conversation
            user_id=current_user.id
        )
        
        return result.result if result.success else {"error": result.error_message}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API call failed: {str(e)}"
        )


@router.post(
    "/code-execution",
    response_model=dict,
    summary="Execute Code",
    description="Execute code in secure sandbox using built-in code executor"
)
async def execute_code(
    code: str = Query(..., description="Code to execute"),
    language: str = Query(..., regex="^(python|javascript|sql|bash)$", description="Programming language"),
    timeout: int = Query(30, ge=1, le=300, description="Execution timeout in seconds"),
    memory_limit_mb: int = Query(128, ge=64, le=512, description="Memory limit in MB"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute code."""
    
    try:
        request = ToolExecutionRequest(
            tool_name="code_executor",
            parameters={
                "code": code,
                "language": language,
                "timeout": timeout,
                "memory_limit_mb": memory_limit_mb
            }
        )
        
        service = AIToolService(db)
        result = await service.execute_tool(
            request=request,
            conversation_id=UUID('00000000-0000-0000-0000-000000000000'),  # Default conversation
            user_id=current_user.id
        )
        
        return result.result if result.success else {"error": result.error_message}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code execution failed: {str(e)}"
        )