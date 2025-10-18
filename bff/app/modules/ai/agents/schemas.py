"""AI service schemas for request/response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, validator


class AIAgentType(str, Enum):
    """AI Agent types"""
    SYSTEM = "system"
    CUSTOM = "custom" 
    SPECIALIZED = "specialized"


class AIAgentStatus(str, Enum):
    """AI Agent status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class PersonalityProfile(BaseModel):
    """AI Agent personality profile"""
    role: str = Field(..., description="Agent role/profession")
    expertise: List[str] = Field(default=[], description="Areas of expertise")
    communication_style: str = Field(default="professional", description="Communication style")
    language_traits: List[str] = Field(default=[], description="Language characteristics")
    emotional_tendency: str = Field(default="neutral", description="Emotional tendency")
    
    # Advanced personality traits
    creativity_level: float = Field(default=0.5, ge=0.0, le=1.0)
    formality_level: float = Field(default=0.7, ge=0.0, le=1.0)
    empathy_level: float = Field(default=0.6, ge=0.0, le=1.0)
    curiosity_level: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Behavior configuration
    behavior_rules: List[str] = Field(default=[])
    goals: List[str] = Field(default=[])


class ModelPreferences(BaseModel):
    """AI Model preferences configuration"""
    default_model: str = Field(default="gpt-3.5-turbo")
    fallback_models: List[str] = Field(default=[])
    intent_model: Optional[str] = Field(default=None)
    code_model: Optional[str] = Field(default=None)
    creative_model: Optional[str] = Field(default=None)
    
    model_config = {"protected_namespaces": ()}
    
    # Generation parameters
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)


class AIAgentCreate(BaseModel):
    """Create AI Agent request schema"""
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    introduction: Optional[str] = Field(default=None)
    agent_type: AIAgentType = Field(default=AIAgentType.CUSTOM)
    version: str = Field(default="1.0.0")
    
    # UI & Presentation
    avatar_url: Optional[str] = Field(default=None)
    avatar_style: Optional[str] = Field(default="default")
    conversation_style: str = Field(default="professional")
    
    # Configuration
    system_prompt: str = Field(..., min_length=1)
    personality_config: PersonalityProfile = Field(default_factory=PersonalityProfile)
    model_preferences: ModelPreferences = Field(default_factory=ModelPreferences)
    
    # Capabilities & Permissions
    capabilities: List[str] = Field(default=[])
    required_permissions: List[str] = Field(default=[])
    
    # Categorization & Discovery
    tags: List[str] = Field(default=[])
    category: Optional[str] = Field(default=None)
    
    # Visibility
    is_public: bool = Field(default=True)
    is_active: bool = Field(default=True)

    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores and dashes only')
        return v
    
    model_config = {"protected_namespaces": ()}


class AIAgentUpdate(BaseModel):
    """Update AI Agent request schema"""
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    introduction: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    avatar_style: Optional[str] = Field(default=None)
    conversation_style: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None, min_length=1)
    personality_config: Optional[PersonalityProfile] = Field(default=None)
    model_preferences: Optional[ModelPreferences] = Field(default=None)
    capabilities: Optional[List[str]] = Field(default=None)
    required_permissions: Optional[List[str]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    category: Optional[str] = Field(default=None)
    status: Optional[AIAgentStatus] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    
    model_config = {"protected_namespaces": ()}


class AIAgentResponse(BaseModel):
    """AI Agent response schema"""
    id: UUID
    name: str
    display_name: str
    description: Optional[str]
    introduction: Optional[str]
    agent_type: str
    version: str
    status: str
    
    # Visibility & Ownership
    is_public: bool
    is_active: bool
    
    # UI & Presentation
    avatar_url: Optional[str]
    avatar_style: Optional[str]
    conversation_style: str
    
    # Configuration (simplified for API response)
    personality_config: Dict[str, Any]
    model_preferences: Dict[str, Any]
    capabilities: List[str]
    required_permissions: List[str]
    
    # Categorization & Discovery
    tags: List[str]
    category: Optional[str]
    
    # Metadata
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    
    # Statistics
    usage_count: int
    follower_count: int
    
    # Optional calculated fields
    success_rate: Optional[float] = Field(default=None)
    avg_response_time: Optional[float] = Field(default=None)
    deployment_status: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True


class AIAgentListResponse(BaseModel):
    """AI Agent list response schema"""

    agents: List[AIAgentResponse]
    total: int
    page: int
    size: int


# Chat/Generation Schemas

class ChatMessage(BaseModel):
    """Chat message schema"""
    role: str = Field(..., pattern=r'^(user|assistant|system)$')
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Chat request schema"""
    agent_id: UUID
    messages: List[ChatMessage] = Field(..., min_items=1)
    conversation_id: Optional[UUID] = Field(default=None)
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # Generation parameters
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    stream: bool = Field(default=False)
    
    # Tool usage
    enable_tools: bool = Field(default=True)
    allowed_tools: Optional[List[str]] = Field(default=None)


class ChatResponse(BaseModel):
    """Chat response schema"""
    conversation_id: UUID
    message_id: UUID
    agent_id: UUID
    content: str
    role: str = Field(default="assistant")
    
    # Generation metadata
    model_used: str
    token_usage: Dict[str, int]
    generation_time: float
    
    # Context and tools
    tools_used: List[Dict[str, Any]] = Field(default=[])
    context_sources: List[Dict[str, Any]] = Field(default=[])
    confidence_score: float = Field(default=1.0)
    
    created_at: datetime
    
    model_config = {"protected_namespaces": ()}


# Error Schemas

class AIErrorResponse(BaseModel):
    """AI service error response schema"""
    error_type: str
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Pagination and Lists

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = Field(default=None)
    sort_order: str = Field(default="desc", pattern=r'^(asc|desc)$')


class BaseListResponse(BaseModel):
    """Base list response with pagination"""
    total: int
    page: int
    size: int
    pages: int

    @validator('pages', always=True)
    def calculate_pages(cls, v, values):
        total = values.get('total', 0)
        size = values.get('size', 1)
        return (total + size - 1) // size if size > 0 else 0
