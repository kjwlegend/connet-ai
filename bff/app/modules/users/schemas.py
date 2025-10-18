"""
User Schemas

This module contains Pydantic schemas for user-related operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.core.schemas import BaseSchema, TimestampMixin, UUIDMixin


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    is_active: bool = Field(True, description="Whether user is active")


class UserCreate(UserBase):
    """Schema for creating a user."""

    id: Optional[UUID] = Field(
        None, description="User ID (for external auth providers)"
    )
    password: Optional[str] = Field(
        None, min_length=8, description="User password (optional for OAuth)"
    )
    password_hash: Optional[str] = Field(None, description="Pre-hashed password")
    auth_provider: str = Field("local", description="Authentication provider")
    external_id: Optional[str] = Field(None, description="External provider user ID")

    # Invitation system
    invitation_code: Optional[str] = Field(
        None, description="User's unique invitation code"
    )
    invited_by_code: Optional[str] = Field(
        None, description="Invitation code used during registration"
    )
    invited_by_user_id: Optional[UUID] = Field(
        None, description="ID of the user who invited this user"
    )

    # Registration tracking
    registration_source: Optional[str] = Field(
        None, description="Registration source: web, mobile, api, admin"
    )
    registration_channel: Optional[str] = Field(
        None, description="Registration channel: organic, invite, social, campaign"
    )
    utm_source: Optional[str] = Field(None, description="UTM source parameter")
    utm_medium: Optional[str] = Field(None, description="UTM medium parameter")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign parameter")

    user_metadata: Optional[dict] = Field(None, description="Additional user metadata")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if v and len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    is_active: Optional[bool] = None


class UserResponse(UUIDMixin, UserBase, TimestampMixin):
    """Schema for user responses."""

    invitation_code: Optional[str] = Field(
        None, description="User's unique invitation code"
    )
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    roles: Optional[List[str]] = Field(None, description="User roles")
    is_verified: bool = Field(False, description="Whether user email is verified")

    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user: "User") -> "UserResponse":
        """Create response from user entity."""
        return cls(
            id=str(user.id),  # Convert UUID to string
            email=user.email,
            full_name=user.full_name,
            username=user.username,
            is_active=user.is_active,
            is_verified=getattr(user, "is_verified", False),
            invitation_code=getattr(user, "invitation_code", None),
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=getattr(user, "last_login_at", None),
            permissions=getattr(user, "permissions", []),
            roles=getattr(user, "roles", []),
        )


class UserUpdateRequest(BaseSchema):
    """Schema for user update requests."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)


# User entity (simplified for now)
class User(UUIDMixin, UserBase, TimestampMixin):
    """User entity."""

    password_hash: Optional[str] = Field(
        None, description="Hashed password (optional for OAuth)"
    )
    auth_provider: str = Field("local", description="Authentication provider")
    external_id: Optional[str] = Field(None, description="External provider user ID")
    is_verified: bool = Field(False, description="Whether user email is verified")

    # Invitation system
    invitation_code: Optional[str] = Field(
        None, description="User's unique invitation code"
    )
    invited_by_code: Optional[str] = Field(
        None, description="Invitation code used during registration"
    )
    invited_by_user_id: Optional[UUID] = Field(
        None, description="ID of the user who invited this user"
    )

    # Registration tracking
    registration_source: Optional[str] = Field(None, description="Registration source")
    registration_channel: Optional[str] = Field(
        None, description="Registration channel"
    )
    utm_source: Optional[str] = Field(None, description="UTM source parameter")
    utm_medium: Optional[str] = Field(None, description="UTM medium parameter")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign parameter")

    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    roles: Optional[List[str]] = Field(None, description="User roles")
    user_metadata: Optional[dict] = Field(None, description="Additional user metadata")


class UserSubscriptionResponse(BaseSchema):
    """Subscription details returned to the caller."""

    plan: str = Field(..., description="Active subscription plan")
    status: str = Field(..., description="Subscription status")
    current_period_end: Optional[datetime] = Field(
        None, description="End of current billing period"
    )
    cancel_at_period_end: bool = Field(
        False, description="Whether cancellation takes effect at period end"
    )
    payment_method: Optional[str] = Field(
        None, description="Last used payment method identifier"
    )
    seats_used: Optional[int] = Field(None, description="Seats currently in use")
    seats_limit: Optional[int] = Field(None, description="Seat limit for the plan")


class UserLLMSettingsResponse(BaseSchema):
    """Persisted LLM configuration for a user."""

    user_id: UUID = Field(..., description="User identifier")
    default_provider: str = Field(..., description="Default LLM provider")
    default_model: str = Field(..., description="Default model identifier")
    provider_configs: dict = Field(
        default_factory=dict, description="Per-provider configuration"
    )
    chat_model: Optional[str] = Field(None, description="Chat model override")
    coding_model: Optional[str] = Field(None, description="Coding model override")
    writing_model: Optional[str] = Field(None, description="Writing model override")
    analysis_model: Optional[str] = Field(None, description="Analysis model override")
    creative_model: Optional[str] = Field(None, description="Creative model override")
    default_temperature: float = Field(..., description="Default temperature")
    default_max_tokens: int = Field(..., description="Default maximum tokens")
    default_top_p: float = Field(..., description="Default top-p value")
    default_frequency_penalty: float = Field(
        ..., description="Default frequency penalty"
    )
    default_presence_penalty: float = Field(
        ..., description="Default presence penalty"
    )
    api_keys: dict = Field(default_factory=dict, description="Provider API keys")
    auto_select_model: bool = Field(..., description="Allows automatic model choice")
    cost_optimization_enabled: bool = Field(
        ..., description="Cost optimisation toggle"
    )
    quality_preference: str = Field(..., description="Quality preference setting")
    streaming_enabled: bool = Field(..., description="Streaming responses enabled")
    response_format_preference: str = Field(
        ..., description="Preferred response format"
    )
    content_filtering_level: str = Field(
        ..., description="Content filtering strictness"
    )
    enable_fact_checking: bool = Field(
        ..., description="Fact checking toggle"
    )
    global_system_prompt: Optional[str] = Field(
        None, description="Global system prompt override"
    )
    context_length_preference: int = Field(
        ..., description="Preferred context window length"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserLLMSettingsUpdate(BaseSchema):
    """Update payload for user LLM settings."""

    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    provider_configs: Optional[dict] = None
    chat_model: Optional[str] = None
    coding_model: Optional[str] = None
    writing_model: Optional[str] = None
    analysis_model: Optional[str] = None
    creative_model: Optional[str] = None
    default_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    default_max_tokens: Optional[int] = Field(None, gt=0)
    default_top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    default_frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    default_presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    api_keys: Optional[dict] = None
    auto_select_model: Optional[bool] = None
    cost_optimization_enabled: Optional[bool] = None
    quality_preference: Optional[str] = None
    streaming_enabled: Optional[bool] = None
    response_format_preference: Optional[str] = None
    content_filtering_level: Optional[str] = None
    enable_fact_checking: Optional[bool] = None
    global_system_prompt: Optional[str] = None
    context_length_preference: Optional[int] = Field(None, gt=0)


class InviteStatsResponse(BaseSchema):
    """Summary of a user's invite program statistics."""

    invite_code: Optional[str] = Field(None, description="Active invite code")
    total_sent: int = Field(..., description="Total invites sent")
    accepted: int = Field(..., description="Invites accepted")
    pending: int = Field(..., description="Invites pending acceptance")
    rewards_earned: float = Field(..., description="Total rewards earned")
    currency: str = Field("USD", description="Reward currency")


class OrderHistoryResponse(BaseSchema):
    """Billing or order record returned from settings API."""

    order_id: UUID = Field(..., description="Order identifier")
    amount: float = Field(..., description="Order amount")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Order status")
    created_at: datetime = Field(..., description="Order creation time")
    description: Optional[str] = Field(None, description="Order description")
