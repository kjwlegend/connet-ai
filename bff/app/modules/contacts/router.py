"""
Contacts Management API Endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_contact_service, get_current_user
from app.modules.contacts.schemas import (
    ContactResponse,
    ContactCreate,
    ContactUpdate,
    ContactSearchResponse,
    ContactKnowledgeResponse,
    ContactToolResponse,
)
from app.modules.contacts.service import ContactService
from app.modules.users.schemas import User

router = APIRouter()


@router.get("/", response_model=List[ContactResponse])
async def get_user_contacts(
    skip: int = Query(0, ge=0, description="Skip contacts"),
    limit: int = Query(50, le=100, description="Limit contacts"),
    contact_type: Optional[str] = Query(
        None, pattern="^(user|agent|all)$", description="Filter by type"
    ),
    status: Optional[str] = Query(None, description="Filter by online status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    favorites_only: bool = Query(False, description="Only favorite contacts"),
    search: Optional[str] = Query(None, description="Search contacts"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Get user's contacts with optional filtering."""

    tag_list = tags.split(",") if tags else None

    return await contact_service.get_user_contacts(
        user_id=UUID(str(current_user.id)),
        skip=skip,
        limit=limit,
        contact_type=contact_type,
        status=status,
        tags=tag_list,
        favorites_only=favorites_only,
        search=search,
    )


@router.post("/", response_model=ContactResponse)
async def add_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Add a new contact (follow user or agent)."""
    return await contact_service.add_contact(
        user_id=UUID(str(current_user.id)), contact_data=contact_data
    )


@router.get("/search", response_model=List[ContactSearchResponse])
async def search_contacts(
    query: str = Query(..., min_length=2, description="Search query"),
    contact_type: Optional[str] = Query(
        None, pattern="^(user|agent|all)$", description="Filter by type"
    ),
    limit: int = Query(20, le=50, description="Limit results"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Search for users and agents to add as contacts."""
    return await contact_service.search_contacts(
        query=query,
        contact_type=contact_type,
        limit=limit,
        current_user_id=UUID(str(current_user.id)),
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Get specific contact details."""
    return await contact_service.get_contact(
        user_id=UUID(str(current_user.id)), contact_id=contact_id, contact_type=contact_type
    )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Update contact information."""
    return await contact_service.update_contact(
        user_id=UUID(str(current_user.id)),
        contact_id=contact_id,
        contact_type=contact_type,
        contact_data=contact_data,
    )


@router.delete("/{contact_id}")
async def remove_contact(
    contact_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Remove a contact (unfollow)."""
    await contact_service.remove_contact(
        user_id=UUID(str(current_user.id)), contact_id=contact_id, contact_type=contact_type
    )
    return {"message": "Contact removed successfully"}


@router.post("/{contact_id}/start-conversation")
async def start_conversation_with_contact(
    contact_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Start a conversation with a contact (smart conversation creation)."""
    conversation_response = await contact_service.start_conversation_with_contact(
        user_id=UUID(str(current_user.id)), contact_id=contact_id, contact_type=contact_type
    )
    return conversation_response


@router.post("/{contact_id}/toggle-favorite")
async def toggle_favorite_contact(
    contact_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Toggle favorite status for a contact."""
    is_favorite = await contact_service.toggle_favorite(
        user_id=UUID(str(current_user.id)), contact_id=contact_id, contact_type=contact_type
    )
    return {
        "message": f"Contact {'added to' if is_favorite else 'removed from'} favorites"
    }


@router.post("/{contact_id}/update-status")
async def update_contact_status(
    contact_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    status: str = Query(..., pattern="^(online|offline|away|busy)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Update contact's online status (for agents, this might be their availability)."""
    await contact_service.update_contact_status(
        user_id=UUID(str(current_user.id)),
        contact_id=contact_id,
        contact_type=contact_type,
        status=status,
    )
    return {"message": "Contact status updated"}


@router.get("/qr/{user_id}")
async def generate_qr_code(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Generate QR code for adding user as contact."""
    qr_code_data = await contact_service.generate_contact_qr_code(
        target_user_id=user_id, requesting_user_id=UUID(str(current_user.id))
    )
    return qr_code_data


@router.post("/qr/scan")
async def scan_qr_code(
    qr_data: str = Query(..., description="QR code data"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Scan QR code to add contact."""
    contact_response = await contact_service.add_contact_via_qr_code(
        user_id=UUID(str(current_user.id)), qr_data=qr_data
    )
    return contact_response


# Contact Knowledge Base Management
@router.get("/{contact_id}/knowledge", response_model=List[ContactKnowledgeResponse])
async def get_contact_knowledge_bases(
    contact_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Get knowledge bases for a contact."""
    return await contact_service.get_contact_knowledge_bases(
        user_id=UUID(str(current_user.id)), contact_id=contact_id, contact_type=contact_type
    )


@router.post(
    "/{contact_id}/knowledge/{knowledge_base_id}",
    response_model=ContactKnowledgeResponse,
)
async def add_knowledge_to_contact(
    contact_id: UUID,
    knowledge_base_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    alias: Optional[str] = Query(
        None, description="Optional alias for this knowledge base"
    ),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Add knowledge base to a contact."""
    return await contact_service.add_knowledge_to_contact(
        user_id=UUID(str(current_user.id)),
        contact_id=contact_id,
        contact_type=contact_type,
        knowledge_base_id=knowledge_base_id,
        alias=alias,
    )


@router.delete("/{contact_id}/knowledge/{knowledge_base_id}")
async def remove_knowledge_from_contact(
    contact_id: UUID,
    knowledge_base_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Remove knowledge base from a contact."""
    success = await contact_service.remove_knowledge_from_contact(
        user_id=UUID(str(current_user.id)),
        contact_id=contact_id,
        contact_type=contact_type,
        knowledge_base_id=knowledge_base_id,
    )
    return {
        "message": (
            "Knowledge base removed successfully"
            if success
            else "Knowledge base not found"
        )
    }


# Contact Tool Management
@router.get("/{contact_id}/tools", response_model=List[ContactToolResponse])
async def get_contact_tools(
    contact_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Get tools for a contact."""
    return await contact_service.get_contact_tools(
        user_id=UUID(str(current_user.id)), contact_id=contact_id, contact_type=contact_type
    )


@router.post("/{contact_id}/tools/{tool_id}", response_model=ContactToolResponse)
async def add_tool_to_contact(
    contact_id: UUID,
    tool_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    enabled: bool = Query(True, description="Whether the tool is enabled"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Add tool to a contact."""
    return await contact_service.add_tool_to_contact(
        user_id=UUID(str(current_user.id)),
        contact_id=contact_id,
        contact_type=contact_type,
        tool_id=tool_id,
        enabled=enabled,
    )


@router.put("/{contact_id}/tools/{tool_id}", response_model=ContactToolResponse)
async def update_contact_tool_config(
    contact_id: UUID,
    tool_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    enabled: Optional[bool] = Query(None, description="Whether the tool is enabled"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Update tool configuration for a contact."""
    result = await contact_service.update_contact_tool_config(
        user_id=UUID(str(current_user.id)),
        contact_id=contact_id,
        contact_type=contact_type,
        tool_id=tool_id,
        enabled=enabled,
    )
    if result:
        return result
    raise HTTPException(status_code=404, detail="Tool configuration not found")


@router.delete("/{contact_id}/tools/{tool_id}")
async def remove_tool_from_contact(
    contact_id: UUID,
    tool_id: UUID,
    contact_type: str = Query(..., pattern="^(user|agent)$"),
    current_user: User = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Remove tool from a contact."""
    success = await contact_service.remove_tool_from_contact(
        user_id=UUID(str(current_user.id)),
        contact_id=contact_id,
        contact_type=contact_type,
        tool_id=tool_id,
    )
    return {"message": "Tool removed successfully" if success else "Tool not found"}
