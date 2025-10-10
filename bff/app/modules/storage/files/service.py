"""Service layer for file storage metadata and permissions."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.modules.storage.files.models import FileModel, FilePermissionModel
from app.modules.storage.files.repository import (
    FilePermissionRepositoryProtocol,
    FileRepositoryProtocol,
)
from app.schemas.files import (
    FileCreate,
    FilePermissionGrant,
    FilePermissionResponse,
    FileResponse,
    FileUpdate,
)


class FileStorageService:
    """Handles CRUD operations for stored files and their permissions."""

    def __init__(
        self,
        *,
        file_repository: FileRepositoryProtocol,
        permission_repository: FilePermissionRepositoryProtocol,
    ) -> None:
        self.file_repository = file_repository
        self.permission_repository = permission_repository

    # ------------------------------------------------------------------
    # File operations
    async def upload_file(
        self, uploaded_by: UUID, payload: FileCreate
    ) -> FileResponse:
        file_record = FileModel(
            filename=payload.filename,
            display_name=payload.display_name or payload.filename,
            file_type=payload.file_type,
            file_size=payload.file_size,
            file_extension=payload.file_extension,
            storage_provider=payload.storage_provider or "supabase",
            storage_path=payload.storage_path,
            storage_bucket=payload.storage_bucket,
            uploaded_by=uploaded_by,
            status=payload.status or "active",
            is_public=payload.is_public or False,
            thumbnail_url=payload.thumbnail_url,
            preview_url=payload.preview_url,
            processed_variants=payload.processed_variants,
            access_level=payload.access_level or "private",
            file_metadata=payload.file_metadata,
            description=payload.description,
            tags=payload.tags or [],
            expires_at=payload.expires_at,
        )
        created = await self.file_repository.create_file(file_record)
        return self._file_to_response(created)

    async def get_file(self, file_id: UUID) -> Optional[FileResponse]:
        file_record = await self.file_repository.get_by_id(file_id)
        return self._file_to_response(file_record) if file_record else None

    async def list_files(
        self,
        *,
        uploaded_by: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[FileResponse]:
        records = await self.file_repository.list_files(
            uploaded_by=uploaded_by,
            is_public=is_public,
            limit=limit,
            offset=offset,
        )
        return [self._file_to_response(record) for record in records]

    async def update_file(
        self, file_id: UUID, payload: FileUpdate
    ) -> Optional[FileResponse]:
        record = await self.file_repository.get_by_id(file_id)
        if not record:
            return None

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        record.updated_at = datetime.utcnow()

        updated = await self.file_repository.update_file(record)
        return self._file_to_response(updated) if updated else None

    async def delete_file(self, file_id: UUID) -> bool:
        return await self.file_repository.delete_file(file_id)

    async def record_download(self, file_id: UUID) -> bool:
        return await self.file_repository.increment_download_count(file_id)

    # ------------------------------------------------------------------
    # Permission operations
    async def grant_permission(
        self, file_id: UUID, payload: FilePermissionGrant, granted_by: UUID
    ) -> FilePermissionResponse:
        permission = FilePermissionModel(
            file_id=file_id,
            user_id=payload.user_id,
            permission_type=payload.permission_type,
            granted_by=granted_by,
            expires_at=payload.expires_at,
        )
        created = await self.permission_repository.grant_permission(permission)
        return self._permission_to_response(created)

    async def revoke_permission(self, file_id: UUID, user_id: UUID) -> bool:
        return await self.permission_repository.revoke_permission(file_id, user_id)

    async def get_file_permissions(
        self, file_id: UUID
    ) -> List[FilePermissionResponse]:
        records = await self.permission_repository.get_permissions_for_file(file_id)
        return [self._permission_to_response(record) for record in records]

    async def get_user_permissions(
        self, user_id: UUID
    ) -> List[FilePermissionResponse]:
        records = await self.permission_repository.get_user_permissions(user_id)
        return [self._permission_to_response(record) for record in records]

    # ------------------------------------------------------------------
    def _file_to_response(self, record: FileModel) -> FileResponse:
        return FileResponse(
            id=record.id,
            filename=record.filename,
            display_name=record.display_name,
            file_type=record.file_type,
            file_size=record.file_size,
            file_extension=record.file_extension,
            storage_provider=record.storage_provider,
            storage_path=record.storage_path,
            storage_bucket=record.storage_bucket,
            uploaded_by=record.uploaded_by,
            uploaded_at=record.uploaded_at,
            status=record.status,
            is_public=record.is_public,
            thumbnail_url=record.thumbnail_url,
            preview_url=record.preview_url,
            processed_variants=record.processed_variants,
            access_level=record.access_level,
            download_count=record.download_count,
            file_metadata=record.file_metadata,
            description=record.description,
            tags=record.tags,
            created_at=record.created_at,
            updated_at=record.updated_at,
            expires_at=record.expires_at,
        )

    def _permission_to_response(
        self, record: FilePermissionModel
    ) -> FilePermissionResponse:
        return FilePermissionResponse(
            file_id=record.file_id,
            user_id=record.user_id,
            permission_type=record.permission_type,
            granted_by=record.granted_by,
            granted_at=record.granted_at,
            expires_at=record.expires_at,
            is_active=record.is_active,
        )


__all__ = ["FileStorageService"]
