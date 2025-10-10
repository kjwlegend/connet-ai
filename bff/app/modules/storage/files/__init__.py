"""Storage files slice exports."""

from app.modules.storage.files.models import FileModel, FilePermissionModel
from app.modules.storage.files.repository import (
    FilePermissionRepositoryProtocol,
    FileRepositoryProtocol,
)
from app.modules.storage.files.repository_impl import (
    FilePermissionRepository,
    FileRepository,
)
from app.modules.storage.files.service import FileStorageService

__all__ = [
    "FileModel",
    "FilePermissionModel",
    "FileRepositoryProtocol",
    "FilePermissionRepositoryProtocol",
    "FileRepository",
    "FilePermissionRepository",
    "FileStorageService",
]
