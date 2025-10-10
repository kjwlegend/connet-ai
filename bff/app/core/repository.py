"""Shared repository abstractions for SQLModel persistence."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.utils.logging import get_logger


ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType], ABC):
    """Common CRUD helpers for SQLModel-based repositories."""

    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model
        self.logger = get_logger(self.__class__.__name__)

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        try:
            db_obj = self.model(**obj_in)
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj
        except IntegrityError as exc:
            await self.session.rollback()
            self.logger.error("Integrity error creating %s: %s", self.model.__name__, exc)
            raise ValueError(f"Failed to create {self.model.__name__}: {exc}") from exc
        except Exception:
            await self.session.rollback()
            self.logger.exception("Error creating %s", self.model.__name__)
            raise

    async def get_by_id(self, record_id: Any) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == record_id)
        result = await self.session.exec(statement)
        return result.first()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        statement = select(self.model).offset(offset).limit(limit)
        if order_by and hasattr(self.model, order_by):
            statement = statement.order_by(getattr(self.model, order_by))
        result = await self.session.exec(statement)
        return list(result.all())

    async def update(self, record_id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        db_obj = await self.get_by_id(record_id)
        if not db_obj:
            return None

        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        try:
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj
        except IntegrityError as exc:
            await self.session.rollback()
            self.logger.error(
                "Integrity error updating %s %s: %s", self.model.__name__, record_id, exc
            )
            raise ValueError(f"Failed to update {self.model.__name__}: {exc}") from exc
        except Exception:
            await self.session.rollback()
            self.logger.exception(
                "Error updating %s %s", self.model.__name__, record_id
            )
            raise

    async def delete(self, record_id: Any) -> bool:
        db_obj = await self.get_by_id(record_id)
        if not db_obj:
            return False

        try:
            await self.session.delete(db_obj)
            await self.session.flush()
            return True
        except Exception:
            await self.session.rollback()
            self.logger.exception("Error deleting %s %s", self.model.__name__, record_id)
            raise

    async def count(self, **filters: Any) -> int:
        statement = select(func.count(self.model.id))
        for field, value in filters.items():
            if hasattr(self.model, field):
                statement = statement.where(getattr(self.model, field) == value)
        result = await self.session.exec(statement)
        return int(result.one())

    async def exists(self, record_id: Any) -> bool:
        return await self.get_by_id(record_id) is not None

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        if not hasattr(self.model, field):
            raise ValueError(f"Field '{field}' does not exist on {self.model.__name__}")
        statement = select(self.model).where(getattr(self.model, field) == value)
        result = await self.session.exec(statement)
        return result.first()

    async def get_many_by_field(
        self,
        field: str,
        value: Any,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        if not hasattr(self.model, field):
            raise ValueError(f"Field '{field}' does not exist on {self.model.__name__}")
        statement = (
            select(self.model)
            .where(getattr(self.model, field) == value)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.exec(statement)
        return list(result.all())

    async def search(
        self,
        search_fields: List[str],
        query: str,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        from sqlalchemy import or_

        conditions = [
            getattr(self.model, field).ilike(f"%{query}%")
            for field in search_fields
            if hasattr(self.model, field)
        ]
        if not conditions:
            return []

        statement = select(self.model).where(or_(*conditions)).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return list(result.all())


__all__ = ["BaseRepository"]

