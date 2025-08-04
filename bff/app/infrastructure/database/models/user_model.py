"""
User Database Model

This module defines the SQLModel for users in the database.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text


class UserModel(SQLModel, table=True):
    """User database model."""
    
    __tablename__ = "users"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique user identifier"
    )
    
    # Basic information
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address"
    )
    full_name: str = Field(
        max_length=100,
        description="User full name"
    )
    username: Optional[str] = Field(
        default=None,
        unique=True,
        index=True,
        max_length=50,
        description="Unique username"
    )
    
    # Authentication
    password_hash: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Hashed password (optional for OAuth users)"
    )
    auth_provider: str = Field(
        default="local",
        max_length=50,
        description="Authentication provider: local, supabase, google, github, etc."
    )
    external_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="External provider user ID"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Whether user account is active"
    )
    
    # Invitation system
    invitation_code: Optional[str] = Field(
        default=None,
        unique=True,
        index=True,
        max_length=20,
        description="User's unique invitation code"
    )
    invited_by_code: Optional[str] = Field(
        default=None,
        index=True,
        max_length=20,
        description="Invitation code used during registration"
    )
    invited_by_user_id: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        description="ID of the user who invited this user"
    )
    
    # Registration channel information
    registration_source: Optional[str] = Field(
        default=None,
        index=True,
        max_length=50,
        description="Registration source: web, mobile, api, admin"
    )
    registration_channel: Optional[str] = Field(
        default=None,
        index=True,
        max_length=50,
        description="Registration channel: organic, invite, social, campaign"
    )
    utm_source: Optional[str] = Field(
        default=None,
        max_length=100,
        description="UTM source parameter"
    )
    utm_medium: Optional[str] = Field(
        default=None,
        max_length=100,
        description="UTM medium parameter"
    )
    utm_campaign: Optional[str] = Field(
        default=None,
        max_length=100,
        description="UTM campaign parameter"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    last_login_at: Optional[datetime] = Field(
        default=None,
        description="Last login timestamp"
    )
    
    # Profile information
    bio: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="User biography"
    )
    avatar_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Avatar image URL"
    )
    
    # Settings (stored as JSON)
    preferences: Optional[dict] = Field(
        default=None,
        description="User preferences and settings"
    )
    
    # Permissions and roles (simplified for now)
    permissions: Optional[List[str]] = Field(
        default=None,
        description="User permissions"
    )
    roles: Optional[List[str]] = Field(
        default=None,
        description="User roles"
    )
    
    # Statistics
    invitation_count: int = Field(
        default=0,
        description="Number of successful invitations"
    )
    total_conversations: int = Field(
        default=0,
        description="Total number of conversations"
    )
    total_messages: int = Field(
        default=0,
        description="Total number of messages sent"
    )
    
    # Metadata
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional user metadata"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "username": "johndoe",
                "invitation_code": "ABC123XYZ",
                "is_active": True,
                "registration_source": "web",
                "registration_channel": "invite",
                "bio": "Software developer and AI enthusiast",
                "preferences": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": True
                }
            }
        }