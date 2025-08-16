"""
Timeline Like Database Model

This module defines the SQLModel for timeline post and comment likes in the database.
Only users can like content (agents cannot like).
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class TimelineLikeModel(SQLModel, table=True):
    """Timeline like/reaction database model."""
    
    __tablename__ = "timeline_likes"
    
    # Composite primary key
    user_id: UUID = Field(
        foreign_key="users.id",
        primary_key=True,
        description="User who liked (only users can like)"
    )
    target_id: UUID = Field(
        primary_key=True,
        description="Target ID (post or comment being liked)"
    )
    target_type: str = Field(
        primary_key=True,
        max_length=10,
        description="Target type: post or comment"
    )
    
    # Reaction type
    reaction_type: str = Field(
        default="like",
        max_length=20,
        description="Reaction type: like, love, laugh, wow, sad, angry"
    )
    
    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Like creation timestamp"
    )
    
    # Metadata
    like_metadata: Optional[dict] = Field(default=None,
        description="Additional like metadata"
    ,

        sa_column=Column(JSON)

    )
    
    model_config = {

    
        "json_schema_extra": {
            "example": {
                "user_id": "12345678-1234-5678-9012-123456789012",
                "target_id": "87654321-4321-8765-2109-876543210987",
                "target_type": "post",
                "reaction_type": "love"
            }

    
    }
        }