"""Schemas for the storage.files module."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileBase(BaseModel):
    """Base attributes shared by file payloads."""

    filename: str = Field(..., max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    file_type: str = Field(..., max_length=100)
    file_size: int = Field(..., ge=0)
    file_extension: str = Field(..., max_length=10)
    storage_provider: Optional[str] = Field("supabase", max_length=20)
    storage_path: str = Field(..., max_length=500)
    storage_bucket: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field("active", max_length=20)
    is_public: Optional[bool] = Field(False)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    preview_url: Optional[str] = Field(None, max_length=500)
    processed_variants: Optional[Dict[str, str]] = None
    access_level: Optional[str] = Field("private", max_length=20)
    file_metadata: Optional[Dict[str, str]] = None
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(default_factory=list)
    expires_at: Optional[datetime] = None


class FileCreate(FileBase):
    """Payload for creating a file record."""


class FileUpdate(BaseModel):
    """Payload for updating an existing file record."""

    display_name: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=20)
    is_public: Optional[bool] = None
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    preview_url: Optional[str] = Field(None, max_length=500)
    processed_variants: Optional[Dict[str, str]] = None
    access_level: Optional[str] = Field(None, max_length=20)
    file_metadata: Optional[Dict[str, str]] = None
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class FileResponse(FileBase):
    """Response model for file metadata."""

    id: UUID
    uploaded_by: UUID
    uploaded_at: datetime
    download_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FilePermissionGrant(BaseModel):
    """Payload for granting file permissions."""

    user_id: UUID
    permission_type: str
    expires_at: Optional[datetime] = None


class FilePermissionResponse(BaseModel):
    """Response model for file permission entries."""

    file_id: UUID
    user_id: UUID
    permission_type: str
    granted_by: UUID
    granted_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


__all__ = [
    "FileCreate",
    "FileUpdate",
    "FileResponse",
    "FilePermissionGrant",
    "FilePermissionResponse",
]
