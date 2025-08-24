"""AI service schemas for request/response models."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
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


# Memory System Schemas

class MemoryType(str, Enum):
    """Memory types for three-tier system"""
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class MemoryCategory(str, Enum):
    """Memory categories"""
    CONVERSATION = "conversation"
    USER_PREFERENCE = "user_preference"
    KNOWLEDGE = "knowledge"
    PATTERN = "pattern"
    ENTITY = "entity"


class MemoryCreate(BaseModel):
    """Create memory request schema"""
    conversation_id: UUID
    agent_id: Optional[UUID] = Field(default=None)
    memory_type: MemoryType
    memory_category: MemoryCategory
    content: str = Field(..., min_length=1)
    memory_metadata: Dict[str, Any] = Field(default_factory=dict)
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0)


class MemoryResponse(BaseModel):
    """Memory response schema"""
    id: UUID
    conversation_id: UUID
    agent_id: Optional[UUID]
    memory_type: str
    memory_category: str
    content: str
    memory_metadata: Dict[str, Any]
    importance_score: float
    confidence_score: float
    emotional_valence: float
    created_at: datetime
    access_count: int

    class Config:
        from_attributes = True


class ConversationSummaryResponse(BaseModel):
    """Conversation summary response schema"""
    id: UUID
    conversation_id: UUID
    summary_text: str
    key_points: List[str]
    entities: List[Dict[str, Any]]
    topics: List[str]
    sentiment: str
    time_range_start: datetime
    time_range_end: datetime
    message_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Tool System Schemas

class ToolType(str, Enum):
    """Tool types"""
    API_CALL = "api_call"
    FILE_PROCESSING = "file_processing"
    DATA_ANALYSIS = "data_analysis"
    CODE_EXECUTION = "code_execution"
    WEB_SEARCH = "web_search"
    DATABASE_QUERY = "database_query"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


class ToolParameterSchema(BaseModel):
    """Tool parameter definition"""
    name: str
    type: str  # string, integer, boolean, array, object
    description: str
    required: bool = True
    default_value: Any = None
    enum_values: Optional[List[str]] = Field(default=None)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)


class ToolCreate(BaseModel):
    """Create tool request schema"""
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    tool_type: ToolType
    version: str = Field(default="1.0.0")
    
    # Configuration
    configuration: Dict[str, Any] = Field(default_factory=dict)
    parameters_schema: List[ToolParameterSchema] = Field(default=[])
    required_permissions: List[str] = Field(default=[])
    
    # Execution settings
    timeout_seconds: int = Field(default=30, gt=0)
    rate_limit: Optional[Dict[str, int]] = Field(default=None)
    resource_limits: Dict[str, Any] = Field(default_factory=dict)
    
    # Security
    security_level: str = Field(default="medium")
    allowed_domains: List[str] = Field(default=[])
    category: str = Field(default="general")
    tags: List[str] = Field(default=[])

    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores and dashes only')
        return v


class ToolResponse(BaseModel):
    """Tool response schema"""
    id: UUID
    name: str
    display_name: str
    description: str
    tool_type: str
    version: str
    status: str
    category: str
    tags: List[str]
    
    # Configuration
    parameters_schema: List[Dict[str, Any]]
    required_permissions: List[str]
    timeout_seconds: int
    security_level: str
    
    # Statistics
    usage_count: int
    success_rate: float
    avg_execution_time: float
    
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ToolExecutionRequest(BaseModel):
    """Tool execution request schema"""
    tool_name: str
    parameters: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResponse(BaseModel):
    """Tool execution response schema"""
    execution_id: str
    success: bool
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time: float
    artifacts: List[str] = Field(default=[])
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Webhook System Schemas

class WebhookCreate(BaseModel):
    """Create webhook request schema"""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., pattern=r'^https?://.+')
    method: str = Field(default="POST", pattern=r'^(GET|POST|PUT|DELETE|PATCH)$')
    headers: Dict[str, str] = Field(default_factory=dict)
    secret: Optional[str] = Field(default=None, max_length=255)
    timeout_seconds: int = Field(default=30, gt=0)
    
    # Retry configuration
    retry_enabled: bool = Field(default=True)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=60, gt=0)
    
    # Event configuration
    event_types: List[str] = Field(default=[])
    event_filters: Dict[str, Any] = Field(default_factory=dict)
    transform_template: Optional[str] = Field(default=None)


class WebhookResponse(BaseModel):
    """Webhook response schema"""
    id: UUID
    name: str
    url: str
    method: str
    status: str
    event_types: List[str]
    retry_enabled: bool
    max_retries: int
    
    # Statistics
    total_triggers: int
    successful_triggers: int
    failed_triggers: int
    last_triggered_at: Optional[datetime]
    
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookTriggerRequest(BaseModel):
    """Webhook trigger request schema"""
    event_type: str
    event_data: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)


class WebhookTriggerResponse(BaseModel):
    """Webhook trigger response schema"""
    trigger_id: str
    success: bool
    http_status_code: Optional[int]
    error_message: Optional[str]
    triggered_webhooks: int


# RAG System Schemas

class DocumentCreate(BaseModel):
    """Create document request schema"""
    name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    file_type: str = Field(..., max_length=100)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    visibility: str = Field(default="private", pattern=r'^(private|shared|public)$')
    shared_with: List[UUID] = Field(default=[])


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: UUID
    name: str
    file_type: str
    file_size: int
    processing_status: str
    chunk_count: int
    quality_score: float
    visibility: str
    owner_id: UUID
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    """Document search request schema"""
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=50)
    filters: Dict[str, Any] = Field(default_factory=dict)
    search_type: str = Field(default="hybrid", pattern=r'^(vector|keyword|hybrid)$')


class DocumentSearchResult(BaseModel):
    """Document search result schema"""
    chunk_id: UUID
    document_id: UUID
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
    document_name: str
    section_title: Optional[str]
    page_number: Optional[int]


class DocumentSearchResponse(BaseModel):
    """Document search response schema"""
    query: str
    results: List[DocumentSearchResult]
    total_results: int
    search_time: float
    search_type: str


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