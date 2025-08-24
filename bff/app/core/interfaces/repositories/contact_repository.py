"""
Contact Repository Interface

This module defines the Contact repository interface.
"""

from abc import abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from app.infrastructure.database.models.contact_model import ContactModel as Contact
from .base_repository import BaseRepository



class ContactRepository(BaseRepository):
    """Contact repository interface"""

    @abstractmethod
    async def get_by_follower_id(self, follower_id: UUID) -> Optional[Contact]:
        """Get contact by follower ID."""
        pass

    @abstractmethod
    async def get_by_following_id(self, following_id: UUID) -> Optional[Contact]:
        """Get contact by following ID."""
        pass
    
    @abstractmethod
    async def get_by_follower_username(self, follower_username: str) -> Optional[Contact]:
        """Get contact by follower username."""
        pass
    
    @abstractmethod
    async def get_by_following_username(self, following_username: str) -> Optional[Contact]:
        """Get contact by following username."""
        pass
    
    @abstractmethod
    async def get_friends_list(self, follower_id: UUID) -> List[Contact]:
        """Get friends list for a follower."""
        pass
    
    @abstractmethod
    async def get_blocked_list(self, follower_id: UUID) -> List[Contact]:
        """Get blocked list for a follower."""
        pass
    
    @abstractmethod
    async def get_muted_list(self, follower_id: UUID) -> List[Contact]:
        """Get muted list for a follower."""
        pass
    
    @abstractmethod
    async def get_favorite_list(self, follower_id: UUID) -> List[Contact]:
        """Get favorite list for a follower."""
        pass
    
    @abstractmethod
    async def count_contacts(self, follower_id: UUID) -> int:
        """Count contacts for a follower."""
        pass
    
    @abstractmethod
    async def create_contact(self, contact: Contact) -> Contact:
        """Create a new contact."""
        pass
    
    @abstractmethod
    async def update_contact(self,contact: Contact) -> Contact:
        """Update a contact""" 
        pass
    
    @abstractmethod
    async def delete_contact(self, contact_id: UUID) -> bool:
        """Delete a contact."""
        pass
    
    @abstractmethod
    async def get_all_contacts(self, follower_id: UUID) -> List[Contact]:
        """Get all contacts for a follower."""
        pass
    @abstractmethod
    async def search_contacts(
            self,
            query: str,
            offset: int=0,
            limit: int = 20
    ) -> Tuple[List[Contact], int]:
        """Search contacts by query."""
        pass

    # Contact Instance Management Methods (New for Priority 2)
    @abstractmethod
    async def get_user_contact_by_agent(
        self, 
        user_id: UUID, 
        agent_id: UUID
    ) -> Optional[Contact]:
        """Get user's contact instance for a specific agent."""
        pass

    @abstractmethod
    async def create_contact_instance(
        self,
        user_id: UUID,
        agent_id: UUID,
        custom_system_prompt: Optional[str] = None,
        instance_config: Optional[Dict[str, Any]] = None,
        resource_limits: Optional[Dict[str, Any]] = None
    ) -> Contact:
        """Create a contact instance from an agent for a user."""
        pass

    @abstractmethod
    async def update_contact_config(
        self,
        user_id: UUID,
        agent_id: UUID,
        custom_system_prompt: Optional[str] = None,
        instance_config: Optional[Dict[str, Any]] = None,
        resource_limits: Optional[Dict[str, Any]] = None
    ) -> Optional[Contact]:
        """Update contact instance configuration."""
        pass

    @abstractmethod
    async def get_user_agent_contacts(self, user_id: UUID) -> List[Contact]:
        """Get all agent contacts for a user."""
        pass

    @abstractmethod
    async def delete_contact_instance(
        self, 
        user_id: UUID, 
        agent_id: UUID
    ) -> bool:
        """Delete a contact instance."""
        pass
