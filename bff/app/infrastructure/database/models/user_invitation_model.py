"""
User Invitation Database Model

This module defines the SQLModel for user invitations in the database.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class UserInvitationModel(SQLModel, table=True):
    """User invitation database model."""
    
    __tablename__ = "user_invitations"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique invitation identifier"
    )
    
    # Invitation code information
    code: str = Field(
        unique=True,
        index=True,
        max_length=20,
        description="Unique invitation code"
    )
    invited_by: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="ID of user who created this invitation"
    )
    
    # Invitation settings
    max_uses: int = Field(
        default=1,
        description="Maximum number of uses (-1 for unlimited)"
    )
    used_count: int = Field(
        default=0,
        description="Number of times this invitation has been used"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Expiration timestamp (null for no expiration)"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Whether this invitation is active"
    )
    
    # Invitation type and rewards
    invitation_type: str = Field(
        default="standard",
        max_length=50,
        description="Type of invitation: standard, premium, beta"
    )
    reward_config: Optional[dict] = Field(default=None,
        description="Reward configuration for this invitation"
    ,

        sa_column=Column(JSON)

    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Invitation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # Metadata
    invitation_metadata: Optional[dict] = Field(default=None,
        description="Additional invitation metadata"
    ,

        sa_column=Column(JSON)

    )
    
    model_config = {

    
        "json_schema_extra": {
            "example": {
                "code": "INVITE2024ABC",
                "max_uses": 5,
                "used_count": 2,
                "invitation_type": "premium",
                "is_active": True,
                "reward_config": {
                    "inviter_reward": {"type": "credit", "amount": 100},
                    "invitee_reward": {"type": "premium_trial", "days": 30}
                }

    
    }
            }
        }