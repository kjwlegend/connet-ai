"""Models for stored files and file permissions."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class FileModel(SQLModel, table=True):
    """Metadata for uploaded files."""

    __tablename__ = "files"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    filename: str = Field(max_length=255)
    display_name: str = Field(max_length=255)
    file_type: str = Field(max_length=100)
    file_size: int = Field()
    file_extension: str = Field(max_length=10, index=True)

    storage_provider: str = Field(default="supabase", max_length=20)
    storage_path: str = Field(max_length=500)
    storage_bucket: Optional[str] = Field(default=None, max_length=100)

    uploaded_by: UUID = Field(foreign_key="users.id", index=True)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    status: str = Field(default="active", max_length=20, index=True)
    is_public: bool = Field(default=False)

    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    preview_url: Optional[str] = Field(default=None, max_length=500)
    processed_variants: Optional[Dict[str, str]] = Field(
        default=None, sa_column=Column(JSON)
    )

    access_level: str = Field(default="private", max_length=20)
    download_count: int = Field(default=0)

    file_metadata: Optional[Dict[str, str]] = Field(
        default=None, sa_column=Column(JSON)
    )
    description: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)


class FilePermissionModel(SQLModel, table=True):
    """Access control entries for shared files."""

    __tablename__ = "file_permissions"

    file_id: UUID = Field(foreign_key="files.id", primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    permission_type: str = Field(max_length=20)
    granted_by: UUID = Field(foreign_key="users.id", index=True)
    granted_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)


__all__ = ["FileModel", "FilePermissionModel"]
