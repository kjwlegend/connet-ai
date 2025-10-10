"""SQLAlchemy implementation for RAG documents and chunks."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.ai.rag.models import RAGDocumentChunkModel, RAGDocumentModel
from app.modules.ai.rag.repository import (
    RAGDocumentChunkRepositoryProtocol,
    RAGDocumentRepositoryProtocol,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RAGDocumentRepository(
    BaseRepository[RAGDocumentModel], RAGDocumentRepositoryProtocol
):
    """Persistence implementation for RAG documents."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RAGDocumentModel)

    async def get_by_id(self, document_id: UUID) -> Optional[RAGDocumentModel]:
        stmt = select(RAGDocumentModel).where(RAGDocumentModel.id == document_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> List[RAGDocumentModel]:
        stmt = select(RAGDocumentModel).where(RAGDocumentModel.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_documents(
        self,
        query: str,
        file_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[RAGDocumentModel], int]:
        conditions = [
            or_(
                RAGDocumentModel.name.ilike(f"%{query}%"),
                RAGDocumentModel.content.ilike(f"%{query}%"),
            )
        ]
        if file_type:
            conditions.append(RAGDocumentModel.file_type == file_type)
        if owner_id:
            conditions.append(RAGDocumentModel.owner_id == owner_id)

        stmt = (
            select(RAGDocumentModel)
            .where(and_(*conditions))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        documents = list(result.scalars().all())

        count_stmt = select(func.count(RAGDocumentModel.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = int(count_result.scalar_one())
        return documents, total

    async def create(self, document: RAGDocumentModel) -> RAGDocumentModel:
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def delete(self, document_id: UUID) -> bool:
        stmt = select(RAGDocumentModel).where(RAGDocumentModel.id == document_id)
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()
        if not document:
            return False
        await self.session.delete(document)
        await self.session.flush()
        return True

    async def create_chunks(
        self, chunk_data: List[Dict[str, Any]]
    ) -> List[RAGDocumentChunkModel]:
        chunks: List[RAGDocumentChunkModel] = []
        for data in chunk_data:
            chunk = RAGDocumentChunkModel(**data)
            self.session.add(chunk)
            chunks.append(chunk)
        await self.session.flush()
        for chunk in chunks:
            await self.session.refresh(chunk)
        return chunks

    async def get_chunks_by_ids(
        self, chunk_ids: List[UUID]
    ) -> List<RAGDocumentChunkModel]:
        if not chunk_ids:
            return []
        stmt = select(RAGDocumentChunkModel).where(
            RAGDocumentChunkModel.id.in_(chunk_ids)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_processing_status(
        self,
        document_id: UUID,
        status: str,
        chunk_count: Optional[int] = None,
        quality_score: Optional[float] = None,
    ) -> None:
        values: Dict[str, Any] = {
            "processing_status": status,
            "updated_at": datetime.utcnow(),
        }
        if chunk_count is not None:
            values["chunk_count"] = chunk_count
        if quality_score is not None:
            values["quality_score"] = quality_score
            values["processed_at"] = (
                datetime.utcnow() if status == "completed" else None
            )
        stmt = (
            update(RAGDocumentModel)
            .where(RAGDocumentModel.id == document_id)
            .values(**values)
        )
        await self.session.execute(stmt)
        await self.session.flush()


class RAGDocumentChunkRepository(
    BaseRepository[RAGDocumentChunkModel], RAGDocumentChunkRepositoryProtocol
):
    """Persistence implementation for RAG document chunks."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RAGDocumentChunkModel)

    async def get_document_chunks(
        self, document_id: UUID
    ) -> List[RAGDocumentChunkModel]:
        stmt = (
            select(RAGDocumentChunkModel)
            .where(RAGDocumentChunkModel.document_id == document_id)
            .order_by(RAGDocumentChunkModel.chunk_index)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_document_chunk(
        self, chunk: RAGDocumentChunkModel
    ) -> RAGDocumentChunkModel:
        self.session.add(chunk)
        await self.session.flush()
        await self.session.refresh(chunk)
        return chunk


__all__ = ["RAGDocumentRepository", "RAGDocumentChunkRepository"]
