"""AI Agent models for the database layer."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON, Text
from sqlalchemy import Column, JSON
from sqlalchemy.dialects.postgresql import JSONB


class AIAgentModel(SQLModel, table=True):
    """AI Agent model"""
    __tablename__ = "ai_agents"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    display_name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    agent_type: str = Field(max_length=100)  # system, custom, specialized
    version: str = Field(default="1.0.0", max_length=50)
    status: str = Field(default="active", max_length=50)  # active, inactive, deprecated
    
    # Core configuration
    system_prompt: str = Field(sa_column=Column(Text))
    personality_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    model_preferences: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    generation_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    # Behavior configuration
    behavior_rules: List[str] = Field(default=[], sa_column=Column(JSONB))
    conversation_style: str = Field(default="professional", max_length=100)
    enabled_tools: List[str] = Field(default=[], sa_column=Column(JSONB))
    
    # Capabilities and permissions
    capabilities: List[str] = Field(default=[], sa_column=Column(JSONB))
    required_permissions: List[str] = Field(default=[], sa_column=Column(JSONB))
    max_context_length: int = Field(default=4000)
    timeout_seconds: int = Field(default=30)
    
    # Ownership and metadata
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(default=None)
    
    # Usage statistics
    usage_count: int = Field(default=0)
    success_rate: float = Field(default=1.0)
    avg_response_time: float = Field(default=0.0)
    
    # Deployment information
    deployment_status: str = Field(default="deployed", max_length=50)  # deployed, deploying, failed
    deployment_url: Optional[str] = Field(default=None, max_length=500)
    deployment_version: str = Field(default="1.0.0", max_length=50)


class AIAgentVersionModel(SQLModel, table=True):
    """AI Agent version history model"""
    __tablename__ = "ai_agent_versions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(foreign_key="ai_agents.id", index=True)
    version_number: str = Field(max_length=50)
    previous_version: Optional[str] = Field(default=None, max_length=50)
    
    # Version data
    agent_snapshot: Dict[str, Any] = Field(sa_column=Column(JSONB))
    changes: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    change_description: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Metadata
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_current: bool = Field(default=True)


class AIAgentKnowledgeBaseModel(SQLModel, table=True):
    """AI Agent knowledge base model"""
    __tablename__ = "ai_agent_knowledge_bases"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(foreign_key="ai_agents.id", index=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    knowledge_type: str = Field(max_length=100)  # documents, conversations, facts, procedures
    
    # Knowledge content
    content: Dict[str, Any] = Field(sa_column=Column(JSONB))
    agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    tags: List[str] = Field(default=[], sa_column=Column(JSONB))
    
    # Embedding and search
    embedding_model: Optional[str] = Field(default=None, max_length=100)
    embedding_dimension: Optional[int] = Field(default=None)
    
    # Status and metrics
    status: str = Field(default="active", max_length=50)
    quality_score: float = Field(default=1.0)
    relevance_score: float = Field(default=1.0)
    usage_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AIMemoryModel(SQLModel, table=True):
    """AI Memory storage model for three-tier memory system"""
    __tablename__ = "ai_memories"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    agent_id: Optional[UUID] = Field(foreign_key="ai_agents.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Memory classification
    memory_type: str = Field(max_length=50)  # short_term, medium_term, long_term
    memory_category: str = Field(max_length=100)  # conversation, user_preference, knowledge, pattern
    
    # Memory content
    content: str = Field(sa_column=Column(Text))
    agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    context: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    # Memory attributes
    importance_score: float = Field(default=0.5)  # 0.0 to 1.0
    confidence_score: float = Field(default=1.0)  # 0.0 to 1.0
    emotional_valence: float = Field(default=0.0)  # -1.0 to 1.0
    
    # Lifecycle management
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)
    
    # Embedding for semantic search
    embedding_model: Optional[str] = Field(default=None, max_length=100)
    # Note: actual embedding vectors will be stored in a separate table or vector database


class AIConversationSummaryModel(SQLModel, table=True):
    """AI conversation summary for medium-term memory"""
    __tablename__ = "ai_conversation_summaries"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    agent_id: Optional[UUID] = Field(foreign_key="ai_agents.id", index=True)
    
    # Summary content
    summary_text: str = Field(sa_column=Column(Text))
    key_points: List[str] = Field(default=[], sa_column=Column(JSONB))
    entities: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB))
    topics: List[str] = Field(default=[], sa_column=Column(JSONB))
    sentiment: str = Field(default="neutral", max_length=50)
    
    # Context information
    time_range_start: datetime
    time_range_end: datetime
    message_count: int = Field(default=0)
    participant_count: int = Field(default=0)
    
    # Quality metrics
    summary_quality_score: float = Field(default=1.0)
    completeness_score: float = Field(default=1.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)
    is_processed: bool = Field(default=False)


class AIToolModel(SQLModel, table=True):
    """AI Tool model for external integrations"""
    __tablename__ = "ai_tools"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True, unique=True)
    display_name: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text))
    tool_type: str = Field(max_length=100)  # api_call, file_processing, code_execution, etc.
    version: str = Field(default="1.0.0", max_length=50)
    
    # Tool configuration
    configuration: Dict[str, Any] = Field(sa_column=Column(JSONB))
    parameters_schema: Dict[str, Any] = Field(sa_column=Column(JSONB))
    required_permissions: List[str] = Field(default=[], sa_column=Column(JSONB))
    
    # Execution settings
    timeout_seconds: int = Field(default=30)
    rate_limit: Optional[Dict[str, int]] = Field(default=None, sa_column=Column(JSONB))
    resource_limits: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    # Security and access
    security_level: str = Field(default="medium", max_length=50)  # low, medium, high
    allowed_domains: List[str] = Field(default=[], sa_column=Column(JSONB))
    blocked_patterns: List[str] = Field(default=[], sa_column=Column(JSONB))
    
    # Status and metadata
    status: str = Field(default="active", max_length=50)  # active, inactive, deprecated
    category: str = Field(default="general", max_length=100)
    tags: List[str] = Field(default=[], sa_column=Column(JSONB))
    
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Usage statistics
    usage_count: int = Field(default=0)
    success_rate: float = Field(default=1.0)
    avg_execution_time: float = Field(default=0.0)


class AIToolExecutionModel(SQLModel, table=True):
    """AI Tool execution history model"""
    __tablename__ = "ai_tool_executions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tool_id: UUID = Field(foreign_key="ai_tools.id", index=True)
    agent_id: Optional[UUID] = Field(foreign_key="ai_agents.id", index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Execution details
    execution_id: str = Field(max_length=255, index=True)
    parameters: Dict[str, Any] = Field(sa_column=Column(JSONB))
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    
    # Execution status
    status: str = Field(max_length=50)  # pending, running, completed, failed, timeout
    success: bool = Field(default=False)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Performance metrics
    execution_time: float = Field(default=0.0)
    resource_usage: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    # Artifacts and outputs
    artifacts: List[str] = Field(default=[], sa_column=Column(JSONB))  # Generated files/resources
    output_agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)


class AIWebhookModel(SQLModel, table=True):
    """AI Webhook model for external integrations"""
    __tablename__ = "ai_webhooks"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    url: str = Field(max_length=1000)
    method: str = Field(default="POST", max_length=10)
    
    # Configuration
    headers: Dict[str, str] = Field(default={}, sa_column=Column(JSONB))
    secret: Optional[str] = Field(default=None, max_length=255)  # For signature verification
    timeout_seconds: int = Field(default=30)
    
    # Retry configuration
    retry_enabled: bool = Field(default=True)
    max_retries: int = Field(default=3)
    retry_delay_seconds: int = Field(default=60)
    
    # Event filters
    event_types: List[str] = Field(default=[], sa_column=Column(JSONB))
    event_filters: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    transform_template: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Status and metadata
    status: str = Field(default="active", max_length=50)  # active, inactive, failed
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Statistics
    total_triggers: int = Field(default=0)
    successful_triggers: int = Field(default=0)
    failed_triggers: int = Field(default=0)
    last_triggered_at: Optional[datetime] = Field(default=None)


class AIWebhookTriggerModel(SQLModel, table=True):
    """AI Webhook trigger history model"""
    __tablename__ = "ai_webhook_triggers"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    webhook_id: UUID = Field(foreign_key="ai_webhooks.id", index=True)
    trigger_id: str = Field(max_length=255, index=True)
    
    # Trigger details
    event_type: str = Field(max_length=100)
    event_data: Dict[str, Any] = Field(sa_column=Column(JSONB))
    payload: Dict[str, Any] = Field(sa_column=Column(JSONB))
    
    # Execution details
    status: str = Field(max_length=50)  # pending, sent, completed, failed, retry
    success: bool = Field(default=False)
    http_status_code: Optional[int] = Field(default=None)
    response_body: Optional[str] = Field(default=None, sa_column=Column(Text))
    response_headers: Dict[str, str] = Field(default={}, sa_column=Column(JSONB))
    
    # Error handling
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    next_retry_at: Optional[datetime] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


class AIRAGDocumentModel(SQLModel, table=True):
    """AI RAG document model for knowledge base"""
    __tablename__ = "ai_rag_documents"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    file_path: Optional[str] = Field(default=None, max_length=1000)
    file_type: str = Field(max_length=100)  # pdf, docx, txt, md, html, etc.
    file_size: int = Field(default=0)
    
    # Document content
    content: str = Field(sa_column=Column(Text))
    agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    # Processing information
    processing_status: str = Field(default="pending", max_length=50)  # pending, processing, completed, failed
    chunk_count: int = Field(default=0)
    quality_score: float = Field(default=1.0)
    
    # Access control
    owner_id: UUID = Field(foreign_key="users.id")
    visibility: str = Field(default="private", max_length=50)  # private, shared, public
    shared_with: List[UUID] = Field(default=[], sa_column=Column(JSONB))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)


class AIRAGDocumentChunkModel(SQLModel, table=True):
    """AI RAG document chunk model for semantic search"""
    __tablename__ = "ai_rag_document_chunks"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="ai_rag_documents.id", index=True)
    chunk_index: int = Field(index=True)
    
    # Chunk content
    content: str = Field(sa_column=Column(Text))
    chunk_agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    # Position information
    start_position: int = Field(default=0)
    end_position: int = Field(default=0)
    page_number: Optional[int] = Field(default=None)
    section_title: Optional[str] = Field(default=None, max_length=255)
    
    # Embedding information
    embedding_model: str = Field(max_length=100)
    embedding_dimension: int = Field(default=1536)
    # Note: actual embedding vectors stored in vector database
    
    # Quality and relevance
    quality_score: float = Field(default=1.0)
    token_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)