"""SQLModel definitions for user invitations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class UserInvitationModel(SQLModel, table=True):
    """Invitation codes created by users."""

    __tablename__ = "user_invitations"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    code: str = Field(max_length=20, unique=True, index=True)
    invited_by: UUID = Field(foreign_key="users.id", index=True)

    max_uses: int = Field(default=1)
    used_count: int = Field(default=0)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    invitation_type: str = Field(default="standard", max_length=50)
    reward_config: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    invitation_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))


__all__ = ["UserInvitationModel"]
