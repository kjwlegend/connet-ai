"""SQLAlchemy implementations for file metadata repositories."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.storage.files.models import FileModel, FilePermissionModel
from app.modules.storage.files.repository import (
    FilePermissionRepositoryProtocol,
    FileRepositoryProtocol,
)


class FileRepository(BaseRepository[FileModel], FileRepositoryProtocol):
    """Persistence implementation for file metadata."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FileModel)

    async def get_by_id(self, file_id: UUID) -> Optional[FileModel]:
        stmt = select(FileModel).where(FileModel.id == file_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_files(
        self,
        *,
        uploaded_by: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[FileModel]:
        conditions = []
        if uploaded_by:
            conditions.append(FileModel.uploaded_by == uploaded_by)
        if is_public is not None:
            conditions.append(FileModel.is_public.is_(is_public))

        stmt = select(FileModel).offset(offset).limit(limit)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_file(self, file: FileModel) -> FileModel:
        self.session.add(file)
        await self.session.flush()
        await self.session.refresh(file)
        return file

    async def update_file(self, file: FileModel) -> Optional[FileModel]:
        stmt = select(FileModel).where(FileModel.id == file.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        for field in (
            "display_name",
            "file_type",
            "file_size",
            "file_extension",
            "storage_provider",
            "storage_path",
            "storage_bucket",
            "status",
            "is_public",
            "thumbnail_url",
            "preview_url",
            "processed_variants",
            "access_level",
            "download_count",
            "file_metadata",
            "description",
            "tags",
            "expires_at",
        ):
            setattr(model, field, getattr(file, field))

        # Preserve audit fields from payload when provided
        model.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def delete_file(self, file_id: UUID) -> bool:
        stmt = select(FileModel).where(FileModel.id == file_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def increment_download_count(self, file_id: UUID) -> bool:
        stmt = select(FileModel).where(FileModel.id == file_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        model.download_count += 1
        await self.session.flush()
        return True


class FilePermissionRepository(
    BaseRepository[FilePermissionModel], FilePermissionRepositoryProtocol
):
    """Persistence implementation for file permission entries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FilePermissionModel)

    async def grant_permission(
        self, permission: FilePermissionModel
    ) -> FilePermissionModel:
        self.session.add(permission)
        await self.session.flush()
        await self.session.refresh(permission)
        return permission

    async def revoke_permission(self, file_id: UUID, user_id: UUID) -> bool:
        stmt = select(FilePermissionModel).where(
            and_(
                FilePermissionModel.file_id == file_id,
                FilePermissionModel.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            return False
        await self.session.delete(record)
        await self.session.flush()
        return True

    async def get_permissions_for_file(
        self, file_id: UUID
    ) -> List[FilePermissionModel]:
        stmt = select(FilePermissionModel).where(FilePermissionModel.file_id == file_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_permissions(
        self, user_id: UUID
    ) -> List[FilePermissionModel]:
        stmt = select(FilePermissionModel).where(FilePermissionModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


__all__ = ["FileRepository", "FilePermissionRepository"]
