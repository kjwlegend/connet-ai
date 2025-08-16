"""
File Permission Database Model

This module defines the SQLModel for file permissions in the database.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class FilePermissionModel(SQLModel, table=True):
    """File permission database model."""
    
    __tablename__ = "file_permissions"
    
    # Composite primary key
    file_id: UUID = Field(
        foreign_key="files.id",
        primary_key=True,
        description="File ID"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        primary_key=True,
        description="User ID"
    )
    
    # Permission settings
    permission_type: str = Field(
        max_length=20,
        description="Permission type: read, write, delete, share"
    )
    granted_by: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="User who granted this permission"
    )
    granted_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Permission grant timestamp"
    )
    
    # Permission duration
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Permission expiration timestamp"
    )
    is_active: bool = Field(
        default=True,
        description="Whether permission is active"
    )
    
    model_config = {

    
        "json_schema_extra": {
            "example": {
                "file_id": "12345678-1234-5678-9012-123456789012",
                "user_id": "87654321-4321-8765-2109-876543210987",
                "permission_type": "read",
                "granted_by": "11111111-1111-1111-1111-111111111111",
                "expires_at": "2025-12-31T23:59:59Z",
                "is_active": True
            }

    
    }
        }