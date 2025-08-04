"""
Base Repository Interface

This module defines the base repository interface for data access.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")  # Entity type
ID = TypeVar("ID")  # ID type


class BaseRepository(ABC, Generic[T, ID]):
    """Abstract base repository interface."""
    
    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        offset: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get all entities with pagination and filtering."""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def update(self, entity_id: ID, updates: Dict[str, Any]) -> Optional[T]:
        """Update an entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        """Delete an entity."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: ID) -> bool:
        """Check if entity exists."""
        pass