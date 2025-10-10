"""SQLModel definitions for user registration sources."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class UserRegistrationSourceModel(SQLModel, table=True):
    """Track how and where a user registered."""

    __tablename__ = "user_registration_sources"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)

    source_type: str = Field(max_length=50, index=True)
    source_detail: Optional[str] = Field(default=None, max_length=200)

    user_agent: Optional[str] = Field(default=None, max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    device_type: Optional[str] = Field(default=None, max_length=20)
    platform: Optional[str] = Field(default=None, max_length=20)

    utm_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    referrer_url: Optional[str] = Field(default=None, max_length=500)
    landing_page: Optional[str] = Field(default=None, max_length=500)

    country: Optional[str] = Field(default=None, max_length=2)
    city: Optional[str] = Field(default=None, max_length=100)
    timezone: Optional[str] = Field(default=None, max_length=50)

    registered_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    registration_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))


__all__ = ["UserRegistrationSourceModel"]
