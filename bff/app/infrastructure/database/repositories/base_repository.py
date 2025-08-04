"""
Base Repository Implementation

This module provides the base repository implementation with common database operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from uuid import UUID

from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.utils.logging import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType], ABC):
    """Base repository with common CRUD operations."""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        try:
            db_obj = self.model(**obj_in)
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.session.rollback()
            self.logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise ValueError(f"Failed to create {self.model.__name__}: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get record by ID."""
        try:
            statement = select(self.model).where(self.model.id == id)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            raise
    
    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get all records with pagination."""
        try:
            statement = select(self.model).offset(offset).limit(limit)
            
            if order_by:
                if hasattr(self.model, order_by):
                    statement = statement.order_by(getattr(self.model, order_by))
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise
    
    async def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record."""
        try:
            db_obj = await self.get_by_id(id)
            if not db_obj:
                return None
            
            # Update fields
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.session.rollback()
            self.logger.error(f"Integrity error updating {self.model.__name__} {id}: {e}")
            raise ValueError(f"Failed to update {self.model.__name__}: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise
    
    async def delete(self, id: str) -> bool:
        """Delete a record."""
        try:
            db_obj = await self.get_by_id(id)
            if not db_obj:
                return False
            
            await self.session.delete(db_obj)
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise
    
    async def count(self, **filters) -> int:
        """Count records with optional filters."""
        try:
            statement = select(func.count(self.model.id))
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
            
            result = await self.session.exec(statement)
            return result.one()
        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}: {e}")
            raise
    
    async def exists(self, id: str) -> bool:
        """Check if record exists."""
        try:
            obj = await self.get_by_id(id)
            return obj is not None
        except Exception as e:
            self.logger.error(f"Error checking existence of {self.model.__name__} {id}: {e}")
            raise
    
    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get record by specific field."""
        try:
            if not hasattr(self.model, field):
                raise ValueError(f"Field '{field}' does not exist on {self.model.__name__}")
            
            statement = select(self.model).where(getattr(self.model, field) == value)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by {field}={value}: {e}")
            raise
    
    async def get_many_by_field(
        self,
        field: str,
        value: Any,
        offset: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records by specific field."""
        try:
            if not hasattr(self.model, field):
                raise ValueError(f"Field '{field}' does not exist on {self.model.__name__}")
            
            statement = select(self.model).where(
                getattr(self.model, field) == value
            ).offset(offset).limit(limit)
            
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by {field}={value}: {e}")
            raise
    
    async def search(
        self,
        search_fields: List[str],
        query: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Search records by text in specified fields."""
        try:
            conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    conditions.append(field_attr.ilike(f"%{query}%"))
            
            if not conditions:
                return []
            
            statement = select(self.model)
            if len(conditions) == 1:
                statement = statement.where(conditions[0])
            else:
                from sqlalchemy import or_
                statement = statement.where(or_(*conditions))
            
            statement = statement.offset(offset).limit(limit)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            self.logger.error(f"Error searching {self.model.__name__}: {e}")
            raise
    
    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in bulk."""
        try:
            db_objects = [self.model(**obj) for obj in objects]
            self.session.add_all(db_objects)
            await self.session.flush()
            
            # Refresh all objects to get generated IDs
            for db_obj in db_objects:
                await self.session.refresh(db_obj)
            
            return db_objects
        except IntegrityError as e:
            await self.session.rollback()
            self.logger.error(f"Integrity error bulk creating {self.model.__name__}: {e}")
            raise ValueError(f"Failed to bulk create {self.model.__name__}: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise
    
    async def bulk_update(self, updates: List[Dict[str, Any]]) -> bool:
        """Update multiple records in bulk."""
        try:
            for update_data in updates:
                if 'id' not in update_data:
                    continue
                
                obj_id = update_data.pop('id')
                db_obj = await self.get_by_id(obj_id)
                
                if db_obj:
                    for field, value in update_data.items():
                        if hasattr(db_obj, field):
                            setattr(db_obj, field, value)
                    self.session.add(db_obj)
            
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error bulk updating {self.model.__name__}: {e}")
            raise
    
    async def bulk_delete(self, ids: List[str]) -> int:
        """Delete multiple records in bulk."""
        try:
            deleted_count = 0
            for obj_id in ids:
                db_obj = await self.get_by_id(obj_id)
                if db_obj:
                    await self.session.delete(db_obj)
                    deleted_count += 1
            
            await self.session.flush()
            return deleted_count
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error bulk deleting {self.model.__name__}: {e}")
            raise


class AsyncRepository(BaseRepository[ModelType]):
    """Async repository implementation."""
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()


class ReadOnlyRepository(Generic[ModelType], ABC):
    """Base read-only repository for queries only."""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get record by ID."""
        return await BaseRepository(self.session, self.model).get_by_id(id)
    
    async def get_all(self, offset: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        return await BaseRepository(self.session, self.model).get_all(offset, limit)
    
    async def count(self, **filters) -> int:
        """Count records with optional filters."""
        return await BaseRepository(self.session, self.model).count(**filters)
    
    async def search(
        self,
        search_fields: List[str],
        query: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Search records by text in specified fields."""
        return await BaseRepository(self.session, self.model).search(
            search_fields, query, offset, limit
        )