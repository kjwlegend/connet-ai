"""
User Repository Interface

This module defines the user repository interface.
"""

from abc import abstractmethod
from typing import List, Optional

from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    """User repository interface."""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[object]:
        """Get user by email address."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[object]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def search_users(
        self, 
        query: str, 
        offset: int = 0, 
        limit: int = 20
    ) -> tuple[List[object], int]:
        """Search users by name or email."""
        pass
    
    @abstractmethod
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        pass
    
    @abstractmethod
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        pass