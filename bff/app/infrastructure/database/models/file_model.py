"""
File Database Model

This module defines the SQLModel for files in the database.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class FileModel(SQLModel, table=True):
    """File database model."""

    __tablename__ = "files"

    # Primary key and basic information
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique file identifier",
    )
    filename: str = Field(max_length=255, description="Original filename")
    display_name: str = Field(max_length=255, description="Display name for the file")

    # File information
    file_type: str = Field(max_length=100, description="MIME type of the file")
    file_size: int = Field(description="File size in bytes")
    file_extension: str = Field(
        max_length=10, index=True, description="File extension (e.g., .pdf, .jpg)"
    )

    # Storage information
    storage_provider: str = Field(
        default="supabase",
        max_length=20,
        description="Storage provider: supabase, local, s3",
    )
    storage_path: str = Field(max_length=500, description="Storage path or key")
    storage_bucket: Optional[str] = Field(
        default=None, max_length=100, description="Storage bucket name"
    )

    # Upload information
    uploaded_by: UUID = Field(
        foreign_key="users.id", index=True, description="User who uploaded the file"
    )
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow, index=True, description="Upload timestamp"
    )

    # File status
    status: str = Field(
        default="active",
        max_length=20,
        index=True,
        description="File status: active, processing, failed, deleted",
    )
    is_public: bool = Field(
        default=False, description="Whether file is publicly accessible"
    )

    # Processing information (for images, videos, etc.)
    thumbnail_url: Optional[str] = Field(
        default=None, max_length=500, description="Thumbnail image URL"
    )
    preview_url: Optional[str] = Field(
        default=None, max_length=500, description="Preview URL"
    )
    processed_variants: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Processed file variants (different sizes, formats)",
    )

    # Access control
    access_level: str = Field(
        default="private",
        max_length=20,
        description="Access level: public, shared, private",
    )
    download_count: int = Field(
        default=0, description="Number of times file has been downloaded"
    )

    # Metadata
    file_metadata: Optional[dict] = Field(
        default=None, sa_column=Column(JSON), description="File metadata (EXIF, etc.)"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="File description"
    )
    tags: List[str] = Field(
        default=[], description="File tags for organization", sa_column=Column(JSON)
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="File record creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="File expiration timestamp"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "project_diagram.png",
                "display_name": "Project Architecture Diagram",
                "file_type": "image/png",
                "file_size": 1024000,
                "file_extension": ".png",
                "storage_provider": "supabase",
                "storage_path": "files/2025/01/project_diagram_abc123.png",
                "storage_bucket": "connet-ai-files",
                "status": "active",
                "is_public": False,
                "access_level": "shared",
                "description": "System architecture diagram for the project",
                "tags": ["diagram", "architecture", "planning"],
                "download_count": 5,
            }
        }
    }
