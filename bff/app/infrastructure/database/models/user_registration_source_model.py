"""
User Registration Source Database Model

This module defines the SQLModel for user registration source tracking in the database.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserRegistrationSourceModel(SQLModel, table=True):
    """User registration source tracking database model."""
    
    __tablename__ = "user_registration_sources"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique registration source record identifier"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        unique=True,
        index=True,
        description="User ID (one-to-one relationship)"
    )
    
    # Channel information
    source_type: str = Field(
        max_length=50,
        index=True,
        description="Source type: organic, referral, social, campaign, api"
    )
    source_detail: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Detailed source information"
    )
    
    # Device and environment information
    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description="User agent string"
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        description="IP address at registration"
    )
    device_type: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Device type: desktop, mobile, tablet"
    )
    platform: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Platform: web, ios, android"
    )
    
    # Marketing tracking
    utm_data: Optional[dict] = Field(
        default=None,
        description="Complete UTM parameters"
    )
    referrer_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Referrer URL"
    )
    landing_page: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Landing page URL"
    )
    
    # Geographic information
    country: Optional[str] = Field(
        default=None,
        max_length=2,
        description="Country code (ISO 3166-1 alpha-2)"
    )
    city: Optional[str] = Field(
        default=None,
        max_length=100,
        description="City name"
    )
    timezone: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Timezone identifier"
    )
    
    # Timestamp
    registered_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Registration timestamp"
    )
    
    # Additional metadata
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional registration metadata"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "source_type": "campaign",
                "source_detail": "google_ads_winter_2024",
                "device_type": "mobile",
                "platform": "web",
                "utm_data": {
                    "utm_source": "google",
                    "utm_medium": "cpc",
                    "utm_campaign": "winter_2024",
                    "utm_term": "ai_collaboration",
                    "utm_content": "banner_ad"
                },
                "country": "US",
                "city": "San Francisco",
                "timezone": "America/Los_Angeles"
            }
        }