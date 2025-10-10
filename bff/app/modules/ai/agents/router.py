"""AI Agents API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.modules.agents.schemas import (
    AIAgentCreate,
    AIAgentUpdate,
    AIAgentResponse,
    AIAgentListResponse,
    PaginationParams,
    AIErrorResponse,
)
from app.modules.users.schemas import User
from app.modules.agents.service import AIAgentService
from app.modules.ai.workflows.contact_manager import ContactInstanceManager

router = APIRouter()


@router.post(
    "/",
    response_model=AIAgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create AI Agent",
    description="Create a new AI agent with specified configuration",
)
async def create_agent(
    agent_data: AIAgentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AIAgentResponse:
    """Create a new AI agent."""

    try:
        service = AIAgentService(session)
        return await service.create_agent(agent_data, UUID(str(current_user.id)))
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AIAgentListResponse:
    """List AI agents."""

    try:
        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        service = AIAgentService(session)
        return await service.list_agents(
            user_id=UUID(str(current_user.id)),
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AIAgentResponse:
    """Get AI agent by ID."""

    try:
        service = AIAgentService(session)
        agent = await service.get_agent(agent_id, UUID(str(current_user.id)))

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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AIAgentResponse:
    """Update AI agent."""

    try:
        service = AIAgentService(session)
        agent = await service.update_agent(
            agent_id, agent_data, UUID(str(current_user.id))
        )

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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete AI agent."""

    try:
        service = AIAgentService(session)
        success = await service.delete_agent(agent_id, UUID(str(current_user.id)))

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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Deploy AI agent."""

    try:
        service = AIAgentService(session)
        success = await service.deploy_agent(agent_id, UUID(str(current_user.id)))

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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get agent version history."""

    try:
        service = AIAgentService(session)
        return await service.get_agent_versions(agent_id, UUID(str(current_user.id)))
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AIAgentResponse:
    """Rollback agent to specific version."""

    try:
        service = AIAgentService(session)
        agent = await service.rollback_to_version(
            agent_id, version_number, UUID(str(current_user.id))
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


# Agent Marketplace endpoints

@router.get(
    "/marketplace",
    response_model=AIAgentListResponse,
    summary="Get Agent Marketplace",
    description="Browse available agents in the marketplace",
)
async def get_marketplace_agents(
    category: Optional[str] = Query(None, description="Filter by agent category"),
    search: Optional[str] = Query(None, description="Search agents by name or description"),
    featured: Optional[bool] = Query(None, description="Show only featured agents"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of agents"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    session: AsyncSession = Depends(get_session),
) -> AIAgentListResponse:
    """Get marketplace agents."""
    
    try:
        service = AIAgentService(session)
        return await service.get_marketplace_agents(
            category=category,
            search=search,
            featured=featured,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get marketplace agents: {str(e)}",
        )


@router.post(
    "/{agent_id}/add-to-contacts",
    response_model=dict,
    summary="Add Agent to Contacts",
    description="Convert an agent to a personalized contact instance",
)
async def add_agent_to_contacts(
    agent_id: UUID,
    customization_data: dict = {},
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Add agent to user's contacts with optional personalization."""
    
    try:
        # Initialize contact manager
        contact_manager = ContactInstanceManager(session)
        
        # Convert agent to contact instance
        contact_info = await contact_manager.agent_to_contact_conversion(
            user_id=UUID(str(current_user.id)),
            agent_id=agent_id,
            custom_system_prompt=customization_data.get("custom_system_prompt"),
            instance_config=customization_data.get("instance_config"),
            resource_limits=customization_data.get("resource_limits"),
            display_name_override=customization_data.get("display_name")
        )
        
        return {
            "message": "Agent successfully added to contacts",
            "contact_info": contact_info
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add agent to contacts: {str(e)}",
        )


@router.get(
    "/{agent_id}/compatibility",
    response_model=dict,
    summary="Check Agent Compatibility",
    description="Check if agent can be added to user's contacts and any limitations",
)
async def check_agent_compatibility(
    agent_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Check agent compatibility for contact conversion."""
    
    try:
        # Check if agent exists and is accessible
        agent_service = AIAgentService(session)
        agent = await agent_service.get_agent(agent_id, UUID(str(current_user.id)))
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or access denied"
            )
        
        # Check if user already has this agent as a contact
        contact_manager = ContactInstanceManager(session)
        existing_contact = await contact_manager.get_contact_effective_config(
            UUID(str(current_user.id)), agent_id
        )
        
        compatibility_info = {
            "compatible": True,
            "already_added": existing_contact is not None,
            "agent_capabilities": agent.capabilities if hasattr(agent, 'capabilities') else [],
            "required_permissions": agent.required_permissions if hasattr(agent, 'required_permissions') else [],
            "estimated_cost_per_request": "0.02",  # Mock value
            "max_requests_per_hour": 100,  # Default limit
            "customization_options": {
                "custom_system_prompt": True,
                "temperature_adjustment": True,
                "response_length": True,
                "resource_limits": True
            }
        }
        
        return compatibility_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check compatibility: {str(e)}",
        )


# Knowledge Base endpoints
