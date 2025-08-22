"""AI Agents API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.schemas.ai import (
    AIAgentCreate,
    AIAgentUpdate,
    AIAgentResponse,
    AIAgentListResponse,
    PaginationParams,
    AIErrorResponse,
)
from app.schemas.user import UserResponse
from app.services.ai_agent_service import AIAgentService

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.post(
    "/",
    response_model=AIAgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create AI Agent",
    description="Create a new AI agent with specified configuration",
)
async def create_agent(
    agent_data: AIAgentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AIAgentResponse:
    """Create a new AI agent."""

    try:
        service = AIAgentService(db)
        return await service.create_agent(agent_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}",
        )


@router.get(
    "/",
    response_model=AIAgentListResponse,
    summary="List AI Agents",
    description="List AI agents with optional filtering and pagination",
)
async def list_agents(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    agent_status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(
        None, description="Search in name, display_name, or description"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AIAgentListResponse:
    """List AI agents."""

    try:
        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        service = AIAgentService(db)
        return await service.list_agents(
            user_id=current_user.id,
            agent_type=agent_type,
            status=agent_status,
            search=search,
            pagination=pagination,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}",
        )


@router.get(
    "/{agent_id}",
    response_model=AIAgentResponse,
    summary="Get AI Agent",
    description="Get AI agent by ID",
)
async def get_agent(
    agent_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AIAgentResponse:
    """Get AI agent by ID."""

    try:
        service = AIAgentService(db)
        agent = await service.get_agent(agent_id, current_user.id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )

        return agent
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}",
        )


@router.put(
    "/{agent_id}",
    response_model=AIAgentResponse,
    summary="Update AI Agent",
    description="Update AI agent configuration",
)
async def update_agent(
    agent_id: UUID,
    agent_data: AIAgentUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AIAgentResponse:
    """Update AI agent."""

    try:
        service = AIAgentService(db)
        agent = await service.update_agent(agent_id, agent_data, current_user.id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )

        return agent
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}",
        )


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete AI Agent",
    description="Delete AI agent",
)
async def delete_agent(
    agent_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete AI agent."""

    try:
        service = AIAgentService(db)
        success = await service.delete_agent(agent_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}",
        )


@router.post(
    "/{agent_id}/deploy",
    response_model=dict,
    summary="Deploy AI Agent",
    description="Deploy AI agent to production",
)
async def deploy_agent(
    agent_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Deploy AI agent."""

    try:
        service = AIAgentService(db)
        success = await service.deploy_agent(agent_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )

        return {"message": "Agent deployed successfully", "agent_id": agent_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy agent: {str(e)}",
        )


@router.get(
    "/{agent_id}/versions",
    response_model=List[dict],
    summary="Get Agent Versions",
    description="Get version history for an AI agent",
)
async def get_agent_versions(
    agent_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get agent version history."""

    try:
        service = AIAgentService(db)
        return await service.get_agent_versions(agent_id, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent versions: {str(e)}",
        )


@router.post(
    "/{agent_id}/rollback/{version_number}",
    response_model=AIAgentResponse,
    summary="Rollback Agent Version",
    description="Rollback agent to a specific version",
)
async def rollback_agent(
    agent_id: UUID,
    version_number: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AIAgentResponse:
    """Rollback agent to specific version."""

    try:
        service = AIAgentService(db)
        agent = await service.rollback_to_version(
            agent_id, version_number, current_user.id
        )

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent or version not found",
            )

        return agent
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback agent: {str(e)}",
        )


# Knowledge Base endpoints
