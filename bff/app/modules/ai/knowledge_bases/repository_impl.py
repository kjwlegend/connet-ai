"""SQLAlchemy implementation for knowledge base persistence."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.ai.knowledge_bases.models import (
    KnowledgeBaseModel,
    KnowledgeDocumentModel,
)
from app.modules.ai.knowledge_bases.repository import KnowledgeBaseRepositoryProtocol
from app.utils.logging import get_logger

logger = get_logger(__name__)


class KnowledgeBaseRepository(BaseRepository[KnowledgeBaseModel], KnowledgeBaseRepositoryProtocol):
    """Persistence implementation for knowledge bases and their documents."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, KnowledgeBaseModel)

    async def get_by_id(self, knowledge_base_id: UUID) -> Optional[KnowledgeBaseModel]:
        stmt = select(KnowledgeBaseModel).where(KnowledgeBaseModel.id == knowledge_base_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[KnowledgeBaseModel]:
        stmt = select(KnowledgeBaseModel).where(KnowledgeBaseModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> List[KnowledgeBaseModel]:
        stmt = select(KnowledgeBaseModel).where(KnowledgeBaseModel.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_knowledge_bases(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[KnowledgeBaseModel], int]:
        conditions = [
            or_(
                KnowledgeBaseModel.name.ilike(f"%{query}%"),
                KnowledgeBaseModel.description.ilike(f"%{query}%"),
            )
        ]
        if knowledge_type:
            conditions.append(KnowledgeBaseModel.knowledge_type == knowledge_type)
        if owner_id:
            conditions.append(KnowledgeBaseModel.owner_id == owner_id)
        if tags:
            for tag in tags:
                conditions.append(func.json_array_contains(KnowledgeBaseModel.tags, tag))
        conditions.append(KnowledgeBaseModel.is_active.is_(True))

        stmt = (
            select(KnowledgeBaseModel)
            .where(and_(*conditions))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        knowledge_bases = list(result.scalars().all())

        count_stmt = select(func.count(KnowledgeBaseModel.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = int(count_result.scalar_one())
        return knowledge_bases, total

    async def create_knowledge_base(
        self, knowledge_base: KnowledgeBaseModel
    ) -> KnowledgeBaseModel:
        self.session.add(knowledge_base)
        await self.session.flush()
        await self.session.refresh(knowledge_base)
        return knowledge_base

    async def update_knowledge_base(
        self, knowledge_base: KnowledgeBaseModel
    ) -> Optional[KnowledgeBaseModel]:
        if not knowledge_base.id:
            return None

        stmt = select(KnowledgeBaseModel).where(
            KnowledgeBaseModel.id == knowledge_base.id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        # Apply updates from the provided instance onto the tracked model.
        for field in (
            "name",
            "description",
            "knowledge_type",
            "metadata",
            "rag_config",
            "tags",
            "knowledge_metadata",
            "document_ids",
            "is_active",
        ):
            setattr(model, field, getattr(knowledge_base, field))

        model.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def delete_knowledge_base(self, knowledge_base_id: UUID) -> bool:
        stmt = select(KnowledgeBaseModel).where(
            KnowledgeBaseModel.id == knowledge_base_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        model.is_active = False
        model.updated_at = datetime.utcnow()
        await self.session.flush()
        return True

    async def add_document_to_knowledge_base(
        self, knowledge_base_id: UUID, document: KnowledgeDocumentModel
    ) -> KnowledgeDocumentModel:
        document.knowledge_base_id = knowledge_base_id
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def get_knowledge_base_documents(
        self, knowledge_base_id: UUID
    ) -> List[KnowledgeDocumentModel]:
        stmt = select(KnowledgeDocumentModel).where(
            and_(
                KnowledgeDocumentModel.knowledge_base_id == knowledge_base_id,
                KnowledgeDocumentModel.is_active.is_(True),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def remove_document_from_knowledge_base(
        self, knowledge_base_id: UUID, document_id: UUID
    ) -> bool:
        stmt = select(KnowledgeDocumentModel).where(
            and_(
                KnowledgeDocumentModel.knowledge_base_id == knowledge_base_id,
                KnowledgeDocumentModel.id == document_id,
            )
        )
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()
        if not document:
            return False
        document.is_active = False
        document.updated_at = datetime.utcnow()
        await self.session.flush()
        return True


__all__ = ["KnowledgeBaseRepository"]
