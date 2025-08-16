"""
User Subscription Database Model

This module defines the SQLModel for user subscriptions and membership plans.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from decimal import Decimal

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class UserSubscriptionModel(SQLModel, table=True):
    """User subscription database model."""
    
    __tablename__ = "user_subscriptions"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique subscription identifier"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="User ID"
    )
    
    # Subscription plan information
    plan_type: str = Field(
        max_length=20,
        index=True,
        description="Plan type: free, basic, premium, enterprise"
    )
    plan_name: str = Field(
        max_length=50,
        description="Human readable plan name"
    )
    plan_price: Decimal = Field(
        decimal_places=2,
        description="Plan price in USD"
    )
    
    # Subscription status
    status: str = Field(
        default="active",
        max_length=20,
        index=True,
        description="Subscription status: active, canceled, expired, suspended"
    )
    
    # Billing information
    billing_cycle: str = Field(
        default="monthly",
        max_length=20,
        description="Billing cycle: monthly, yearly, lifetime"
    )
    current_period_start: datetime = Field(
        description="Current billing period start"
    )
    current_period_end: datetime = Field(
        description="Current billing period end"
    )
    
    # Usage limits based on plan
    monthly_message_limit: int = Field(
        default=1000,
        description="Monthly message limit"
    )
    monthly_ai_token_limit: int = Field(
        default=50000,
        description="Monthly AI token limit"
    )
    max_file_storage_gb: int = Field(
        default=1,
        description="Maximum file storage in GB"
    )
    max_conversation_history_days: int = Field(
        default=30,
        description="Maximum conversation history retention days"
    )
    
    # Features enabled
    features_enabled: dict = Field(default={},
        description="Dictionary of enabled features"
    ,

        sa_column=Column(JSON)

    )
    
    # Payment information
    payment_method: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Payment method: stripe, paypal, etc."
    )
    external_subscription_id: Optional[str] = Field(
        default=None,
        max_length=200,
        description="External subscription ID (Stripe, etc.)"
    )
    
    # Cancellation
    cancel_at_period_end: bool = Field(
        default=False,
        description="Whether subscription will cancel at period end"
    )
    canceled_at: Optional[datetime] = Field(
        default=None,
        description="Cancellation timestamp"
    )
    
    # Trial information
    trial_start: Optional[datetime] = Field(
        default=None,
        description="Trial start timestamp"
    )
    trial_end: Optional[datetime] = Field(
        default=None,
        description="Trial end timestamp"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Subscription creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    model_config = {

    
        "json_schema_extra": {
            "example": {
                "user_id": "12345678-1234-5678-9012-123456789012",
                "plan_type": "premium",
                "plan_name": "Premium Plan",
                "plan_price": 19.99,
                "status": "active",
                "billing_cycle": "monthly",
                "monthly_message_limit": 10000,
                "monthly_ai_token_limit": 500000,
                "max_file_storage_gb": 10,
                "max_conversation_history_days": 365,
                "features_enabled": {
                    "ai_agents": True,
                    "file_upload": True,
                    "export_conversations": True,
                    "priority_support": True,
                    "custom_prompts": True,
                    "advanced_ai_models": True
                }

    
    },
                "payment_method": "stripe",
                "cancel_at_period_end": False
            }
        }