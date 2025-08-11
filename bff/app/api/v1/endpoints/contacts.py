"""
Contacts Management API Endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user
from app.schemas.contact import (
    ContactResponse,
    ContactCreate,
    ContactUpdate,
    ContactSearchResponse
)
from app.services.contact_service import ContactService
from app.infrastructure.database.models import UserModel

router = APIRouter()


@router.get("/", response_model=List[ContactResponse])
async def get_user_contacts(
    skip: int = Query(0, ge=0, description="Skip contacts"),
    limit: int = Query(50, le=100, description="Limit contacts"),
    contact_type: Optional[str] = Query(None, regex="^(user|agent|all)$", description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by online status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    favorites_only: bool = Query(False, description="Only favorite contacts"),
    search: Optional[str] = Query(None, description="Search contacts"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Get user's contacts with optional filtering."""
    
    tag_list = tags.split(",") if tags else None
    
    return await contact_service.get_user_contacts(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        contact_type=contact_type,
        status=status,
        tags=tag_list,
        favorites_only=favorites_only,
        search=search
    )


@router.post("/", response_model=ContactResponse)
async def add_contact(
    contact_data: ContactCreate,
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Add a new contact (follow user or agent)."""
    return await contact_service.add_contact(
        user_id=current_user.id,
        contact_data=contact_data
    )


@router.get("/search", response_model=List[ContactSearchResponse])
async def search_contacts(
    query: str = Query(..., min_length=2, description="Search query"),
    contact_type: Optional[str] = Query(None, regex="^(user|agent|all)$", description="Filter by type"),
    limit: int = Query(20, le=50, description="Limit results"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Search for users and agents to add as contacts."""
    return await contact_service.search_contacts(
        query=query,
        contact_type=contact_type,
        limit=limit,
        current_user_id=current_user.id
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    contact_type: str = Query(..., regex="^(user|agent)$"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Get specific contact details."""
    return await contact_service.get_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        contact_type=contact_type
    )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact_type: str = Query(..., regex="^(user|agent)$"),
    contact_data: ContactUpdate,
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Update contact information."""
    return await contact_service.update_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        contact_type=contact_type,
        contact_data=contact_data
    )


@router.delete("/{contact_id}")
async def remove_contact(
    contact_id: UUID,
    contact_type: str = Query(..., regex="^(user|agent)$"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Remove a contact (unfollow)."""
    await contact_service.remove_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        contact_type=contact_type
    )
    return {"message": "Contact removed successfully"}


@router.post("/{contact_id}/start-conversation")
async def start_conversation_with_contact(
    contact_id: UUID,
    contact_type: str = Query(..., regex="^(user|agent)$"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Start a conversation with a contact (smart conversation creation)."""
    conversation_response = await contact_service.start_conversation_with_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        contact_type=contact_type
    )
    return conversation_response


@router.post("/{contact_id}/toggle-favorite")
async def toggle_favorite_contact(
    contact_id: UUID,
    contact_type: str = Query(..., regex="^(user|agent)$"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Toggle favorite status for a contact."""
    is_favorite = await contact_service.toggle_favorite(
        user_id=current_user.id,
        contact_id=contact_id,
        contact_type=contact_type
    )
    return {"message": f"Contact {'added to' if is_favorite else 'removed from'} favorites"}


@router.post("/{contact_id}/update-status")
async def update_contact_status(
    contact_id: UUID,
    contact_type: str = Query(..., regex="^(user|agent)$"),
    status: str = Query(..., regex="^(online|offline|away|busy)$"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Update contact's online status (for agents, this might be their availability)."""
    await contact_service.update_contact_status(
        user_id=current_user.id,
        contact_id=contact_id,
        contact_type=contact_type,
        status=status
    )
    return {"message": "Contact status updated"}


@router.get("/qr/{user_id}")
async def generate_qr_code(
    user_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Generate QR code for adding user as contact."""
    qr_code_data = await contact_service.generate_contact_qr_code(
        target_user_id=user_id,
        requesting_user_id=current_user.id
    )
    return qr_code_data


@router.post("/qr/scan")
async def scan_qr_code(
    qr_data: str = Query(..., description="QR code data"),
    current_user: UserModel = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Scan QR code to add contact."""
    contact_response = await contact_service.add_contact_via_qr_code(
        user_id=current_user.id,
        qr_data=qr_data
    )
    return contact_response