"""
Contact Service

This module provides Contact-related business logic.
"""

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from app.modules.contacts.repository_impl import ContactRepository
from app.modules.ai.knowledge_bases.repository_impl import KnowledgeBaseRepository
from app.modules.ai.tools.repository import ToolRepositoryProtocol
from app.modules.users.service import UserService
from app.services.ai_agent_service import AIAgentService
from app.modules.contacts.models import (
    ContactModel,
    ContactKnowledgeLink,
    ContactToolLink,
    EntityType,
)
from app.modules.ai.knowledge_bases.models import KnowledgeBaseModel
from app.modules.ai.tools.models import ToolModel
from app.modules.contacts.schemas import (
    ContactResponse,
    ContactCreate,
    ContactUpdate,
    ContactSearchResponse,
    ContactKnowledgeResponse,
    ContactToolResponse,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ContactService:
    """Contact service for managing user contacts and their configurations."""

    def __init__(
        self,
        contact_repository: ContactRepository,
        knowledge_repository: KnowledgeBaseRepository,
        tool_repository: ToolRepositoryProtocol,
        user_service: Optional[UserService] = None,
        ai_agent_service: Optional[AIAgentService] = None
    ):
        self.contact_repository = contact_repository
        self.knowledge_repository = knowledge_repository
        self.tool_repository = tool_repository
        self.user_service = user_service
        self.ai_agent_service = ai_agent_service

    async def get_user_contacts(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        contact_type: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        favorites_only: bool = False,
        search: Optional[str] = None
    ) -> List[ContactResponse]:
        """Get user's contacts with filtering."""
        try:
            # Implementation will filter contacts based on parameters
            # For now, return basic contact list
            contacts, _ = await self.contact_repository.search_contacts(
                query=search or "",
                offset=skip,
                limit=limit
            )
            
            return [self._contact_to_response(contact) for contact in contacts]
        except Exception as e:
            logger.error(f"Error getting user contacts: {e}")
            raise

    async def add_contact(
        self,
        user_id: UUID,
        contact_data: ContactCreate
    ) -> ContactResponse:
        """Add a new contact (follow user or agent)."""
        try:
            # Prevent users from adding themselves as contacts
            if contact_data.following_id == user_id:
                raise ValueError("Cannot add yourself as a contact")
            
            # Check if contact already exists
            existing_contacts = await self.contact_repository.get_by_follower_id(user_id)
            existing_contact = next(
                (c for c in existing_contacts 
                 if c.following_id == contact_data.following_id 
                 and c.following_type.value == contact_data.following_type), 
                None
            )
            
            if existing_contact:
                raise ValueError(f"{contact_data.following_type.title()} is already in your contacts")
            
            # Validate that the user/agent exists
            if contact_data.following_type == "user":
                if self.user_service:
                    target_user = await self.user_service.get_user_by_id(str(contact_data.following_id))
                    if not target_user:
                        raise ValueError("User not found")
            elif contact_data.following_type == "agent":
                if self.ai_agent_service:
                    target_agent = await self.ai_agent_service.get_agent(contact_data.following_id)
                    if not target_agent:
                        raise ValueError("Agent not found")
            
            # Set is_agent flag based on following_type
            is_agent = contact_data.following_type == "agent"
            
            contact = ContactModel(
                follower_id=user_id,
                following_id=contact_data.following_id,
                following_type=EntityType(contact_data.following_type),
                relationship_type=contact_data.relationship_type or "follow",
                display_name=contact_data.display_name,
                notes=contact_data.notes,
                tags=contact_data.tags or [],
                is_favorite=contact_data.is_favorite or False,
                is_agent=is_agent,
                notification_level=contact_data.notification_level or "normal"
            )
            
            created_contact = await self.contact_repository.create_contact(contact)
            return self._contact_to_response(created_contact)
        except Exception as e:
            logger.error(f"Error adding contact: {e}")
            raise

    async def search_contacts(
        self,
        query: str,
        contact_type: Optional[str] = None,
        limit: int = 20,
        current_user_id: Optional[UUID] = None
    ) -> List[ContactSearchResponse]:
        """Search for users and agents to add as contacts."""
        try:
            contacts, _ = await self.contact_repository.search_contacts(
                query=query,
                offset=0,
                limit=limit
            )
            
            return [self._contact_to_search_response(contact) for contact in contacts]
        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            raise

    async def get_contact(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str
    ) -> Optional[ContactResponse]:
        """Get specific contact details."""
        try:
            # Find contact by composite key
            contacts = await self.contact_repository.get_by_follower_id(user_id)
            contact = next((c for c in contacts if c.following_id == contact_id), None)
            
            if contact:
                return self._contact_to_response(contact)
            return None
        except Exception as e:
            logger.error(f"Error getting contact: {e}")
            raise

    async def update_contact(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str,
        contact_data: ContactUpdate
    ) -> Optional[ContactResponse]:
        """Update contact information."""
        try:
            # Find and update contact
            contacts = await self.contact_repository.get_by_follower_id(user_id)
            contact = next((c for c in contacts if c.following_id == contact_id), None)
            
            if contact:
                # Update fields from contact_data
                for field, value in contact_data.model_dump(exclude_unset=True).items():
                    setattr(contact, field, value)
                
                updated_contact = await self.contact_repository.update_contact(contact)
                return self._contact_to_response(updated_contact)
            return None
        except Exception as e:
            logger.error(f"Error updating contact: {e}")
            raise

    async def remove_contact(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str
    ) -> bool:
        """Remove a contact (unfollow)."""
        try:
            # Find and delete contact using composite key
            contacts = await self.contact_repository.get_by_follower_id(user_id)
            contact = next((c for c in contacts if c.following_id == contact_id and c.following_type.value == contact_type), None)
            
            if contact:
                # Use composite key to delete
                return await self.contact_repository.delete_contact(
                    follower_id=contact.follower_id,
                    following_id=contact.following_id,
                    following_type=contact.following_type.value
                )
            return False
        except Exception as e:
            logger.error(f"Error removing contact: {e}")
            raise

    async def toggle_favorite(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str
    ) -> bool:
        """Toggle favorite status for a contact."""
        try:
            contacts = await self.contact_repository.get_by_follower_id(user_id)
            contact = next((c for c in contacts if c.following_id == contact_id), None)
            
            if contact:
                contact.is_favorite = not contact.is_favorite
                await self.contact_repository.update_contact(contact)
                return contact.is_favorite
            return False
        except Exception as e:
            logger.error(f"Error toggling favorite: {e}")
            raise

    # Contact Knowledge Base Management
    async def add_knowledge_to_contact(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str,
        knowledge_base_id: UUID,
        alias: Optional[str] = None
    ) -> ContactKnowledgeResponse:
        """Add knowledge base to a contact."""
        try:
            knowledge_link = await self.contact_repository.add_knowledge_to_contact(
                follower_id=user_id,
                following_id=contact_id,
                following_type=contact_type,
                knowledge_base_id=knowledge_base_id,
                alias=alias
            )
            
            # Get knowledge base details
        knowledge_base = await self.knowledge_repository.get_by_id(knowledge_base_id)
            
            return ContactKnowledgeResponse(
                id=knowledge_link.id,
                knowledge_base_id=knowledge_base_id,
                knowledge_base_name=knowledge_base.name if knowledge_base else None,
                alias=knowledge_link.alias,
                added_at=knowledge_link.added_at
            )
        except Exception as e:
            logger.error(f"Error adding knowledge to contact: {e}")
            raise

    async def remove_knowledge_from_contact(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str,
        knowledge_base_id: UUID
    ) -> bool:
        """Remove knowledge base from a contact."""
        try:
            return await self.contact_repository.remove_knowledge_from_contact(
                follower_id=user_id,
                following_id=contact_id,
                following_type=contact_type,
                knowledge_base_id=knowledge_base_id
            )
        except Exception as e:
            logger.error(f"Error removing knowledge from contact: {e}")
            raise

    async def get_contact_knowledge_bases(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str
    ) -> List[ContactKnowledgeResponse]:
        """Get all knowledge bases for a contact."""
        try:
            knowledge_links = await self.contact_repository.get_contact_knowledge_bases(
                follower_id=user_id,
                following_id=contact_id,
                following_type=contact_type
            )
            
            responses = []
            for link in knowledge_links:
                knowledge_base = await self.knowledge_repository.get_by_id(link.knowledge_base_id)
                responses.append(ContactKnowledgeResponse(
                    id=link.id,
                    knowledge_base_id=link.knowledge_base_id,
                    knowledge_base_name=knowledge_base.name if knowledge_base else None,
                    alias=link.alias,
                    added_at=link.added_at
                ))
            
            return responses
        except Exception as e:
            logger.error(f"Error getting contact knowledge bases: {e}")
            raise

    # Contact Tool Management
    async def add_tool_to_contact(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str,
        tool_id: UUID,
        enabled: bool = True,
        tool_config: Optional[Dict[str, Any]] = None
    ) -> ContactToolResponse:
        """Add tool to a contact."""
        try:
            tool_link = await self.contact_repository.add_tool_to_contact(
                follower_id=user_id,
                following_id=contact_id,
                following_type=contact_type,
                tool_id=tool_id,
                enabled=enabled,
                tool_config=tool_config
            )
            
            # Get tool details
            tool = await self.tool_repository.get_by_id(tool_id)
            
            return ContactToolResponse(
                id=tool_link.id,
                tool_id=tool_id,
                tool_name=tool.name if tool else None,
                enabled=tool_link.enabled,
                tool_config=tool_link.tool_config,
                added_at=tool_link.added_at
            )
        except Exception as e:
            logger.error(f"Error adding tool to contact: {e}")
            raise

    async def remove_tool_from_contact(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str,
        tool_id: UUID
    ) -> bool:
        """Remove tool from a contact."""
        try:
            return await self.contact_repository.remove_tool_from_contact(
                follower_id=user_id,
                following_id=contact_id,
                following_type=contact_type,
                tool_id=tool_id
            )
        except Exception as e:
            logger.error(f"Error removing tool from contact: {e}")
            raise

    async def get_contact_tools(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str
    ) -> List[ContactToolResponse]:
        """Get all tools for a contact."""
        try:
            tool_links = await self.contact_repository.get_contact_tools(
                follower_id=user_id,
                following_id=contact_id,
                following_type=contact_type
            )
            
            responses = []
            for link in tool_links:
                tool = await self.tool_repository.get_by_id(link.tool_id)
                responses.append(ContactToolResponse(
                    id=link.id,
                    tool_id=link.tool_id,
                    tool_name=tool.name if tool else None,
                    enabled=link.enabled,
                    tool_config=link.tool_config,
                    added_at=link.added_at
                ))
            
            return responses
        except Exception as e:
            logger.error(f"Error getting contact tools: {e}")
            raise

    async def update_contact_tool_config(
        self,
        user_id: UUID,
        contact_id: UUID,
        contact_type: str,
        tool_id: UUID,
        enabled: Optional[bool] = None,
        tool_config: Optional[Dict[str, Any]] = None
    ) -> Optional[ContactToolResponse]:
        """Update tool configuration for a contact."""
        try:
            tool_link = await self.contact_repository.update_tool_config(
                follower_id=user_id,
                following_id=contact_id,
                following_type=contact_type,
                tool_id=tool_id,
                enabled=enabled,
                tool_config=tool_config
            )
            
            if tool_link:
                tool = await self.tool_repository.get_by_id(tool_id)
                return ContactToolResponse(
                    id=tool_link.id,
                    tool_id=tool_id,
                    tool_name=tool.name if tool else None,
                    enabled=tool_link.enabled,
                    tool_config=tool_link.tool_config,
                    added_at=tool_link.added_at
                )
            return None
        except Exception as e:
            logger.error(f"Error updating contact tool config: {e}")
            raise

    # Placeholder methods for other contact operations
    async def start_conversation_with_contact(self, user_id: UUID, contact_id: UUID, contact_type: str):
        """Start a conversation with a contact."""
        # Placeholder - will integrate with conversation service
        pass

    async def update_contact_status(self, user_id: UUID, contact_id: UUID, contact_type: str, status: str):
        """Update contact's online status."""
        # Placeholder - will integrate with presence service
        pass

    async def generate_contact_qr_code(self, target_user_id: UUID, requesting_user_id: UUID):
        """Generate QR code for adding user as contact."""
        # Placeholder - will integrate with QR code generation
        pass

    async def add_contact_via_qr_code(self, user_id: UUID, qr_data: str):
        """Scan QR code to add contact."""
        # Placeholder - will integrate with QR code scanning
        pass

    def _contact_to_response(self, contact: ContactModel) -> ContactResponse:
        """Convert contact model to response."""
        return ContactResponse(
            follower_id=contact.follower_id,
            following_id=contact.following_id,
            following_type=contact.following_type.value,
            relationship_type=contact.relationship_type,
            display_name=contact.display_name,
            notes=contact.notes,
            tags=contact.tags,
            is_favorite=contact.is_favorite,
            is_muted=contact.is_muted,
            is_blocked=contact.is_blocked,
            online_status=contact.online_status,
            last_seen_at=contact.last_seen_at,
            is_agent=contact.is_agent,
            is_pinned=contact.is_pinned,
            notification_level=contact.notification_level,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )

    def _contact_to_search_response(self, contact: ContactModel) -> ContactSearchResponse:
        """Convert contact model to search response."""
        return ContactSearchResponse(
            id=contact.following_id,
            type=contact.following_type.value,
            name=contact.display_name or "Unknown",
            description=contact.notes,
            avatar_url=None,  # Will be populated from user/agent details
            is_followed=True  # Assuming this contact is already followed
        )
