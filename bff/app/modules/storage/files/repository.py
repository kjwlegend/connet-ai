"""Repository protocols for stored files and permissions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.storage.files.models import FileModel, FilePermissionModel


class FileRepositoryProtocol(ABC):
    """Abstract persistence operations for file metadata."""

    @abstractmethod
    async def get_by_id(self, file_id: UUID) -> Optional[FileModel]:
        ...

    @abstractmethod
    async def list_files(
        self,
        *,
        uploaded_by: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[FileModel]:
        ...

    @abstractmethod
    async def create_file(self, file: FileModel) -> FileModel:
        ...

    @abstractmethod
    async def update_file(self, file: FileModel) -> Optional[FileModel]:
        ...

    @abstractmethod
    async def delete_file(self, file_id: UUID) -> bool:
        ...

    @abstractmethod
    async def increment_download_count(self, file_id: UUID) -> bool:
        ...


class FilePermissionRepositoryProtocol(ABC):
    """Abstract persistence operations for file permissions."""

    @abstractmethod
    async def grant_permission(
        self, permission: FilePermissionModel
    ) -> FilePermissionModel:
        ...

    @abstractmethod
    async def revoke_permission(
        self, file_id: UUID, user_id: UUID
    ) -> bool:
        ...

    @abstractmethod
    async def get_permissions_for_file(
        self, file_id: UUID
    ) -> List[FilePermissionModel]:
        ...

    @abstractmethod
    async def get_user_permissions(
        self, user_id: UUID
    ) -> List[FilePermissionModel]:
        ...


__all__ = [
    "FileRepositoryProtocol",
    "FilePermissionRepositoryProtocol",
]
