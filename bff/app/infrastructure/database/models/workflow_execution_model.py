"""
Workflow Execution Database Models

Models for tracking LangGraph workflow execution and performance.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import Column, JSON
from sqlalchemy.dialects.postgresql import JSONB


class WorkflowExecutionModel(SQLModel, table=True):
    """Workflow execution tracking model"""
    
    __tablename__ = "workflow_executions"
    
    # Primary identification
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Workflow configuration
    workflow_type: str = Field(max_length=50, index=True)  # single_contact, mention_routing, etc
    routing_strategy: str = Field(default="auto", max_length=50)
    participant_contacts: List[str] = Field(default=[], sa_column=Column(JSONB))  # Contact IDs
    
    # Execution state
    status: str = Field(default="pending", max_length=20, index=True)  # pending, running, completed, failed
    current_step: Optional[str] = Field(default=None, max_length=100)
    execution_path: List[str] = Field(default=[], sa_column=Column(JSONB))
    
    # Input/Output
    input_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    error_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    
    # Performance metrics
    started_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: Optional[datetime] = Field(default=None)
    total_duration_ms: Optional[int] = Field(default=None)
    
    # Resource usage
    total_tokens: int = Field(default=0)
    prompt_tokens: int = Field(default=0) 
    completion_tokens: int = Field(default=0)
    total_cost_usd: Optional[float] = Field(default=0.0)
    
    # Metadata
    workflow_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NodeExecutionModel(SQLModel, table=True):
    """Individual node execution tracking within workflows"""
    
    __tablename__ = "node_executions"
    
    # Primary identification
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    workflow_execution_id: UUID = Field(foreign_key="workflow_executions.id", index=True)
    
    # Node identification
    node_id: str = Field(max_length=100, index=True)
    node_type: str = Field(max_length=50)  # contact_processor, mention_router, etc
    contact_id: Optional[UUID] = Field(default=None)  # Associated contact if applicable
    
    # Execution details
    status: str = Field(default="pending", max_length=20, index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    
    # Input/Output state
    input_state: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    output_state: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    
    # LLM usage for this node
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    cost_usd: float = Field(default=0.0)
    
    # Error handling
    error_message: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    
    # Metadata
    node_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolExecutionModel(SQLModel, table=True):
    """Tool execution tracking within workflow nodes"""
    
    __tablename__ = "tool_executions"
    
    # Primary identification
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    node_execution_id: UUID = Field(foreign_key="node_executions.id", index=True)
    workflow_execution_id: UUID = Field(foreign_key="workflow_executions.id", index=True)
    
    # Tool identification
    tool_name: str = Field(max_length=100, index=True)
    tool_type: str = Field(max_length=50)  # builtin, external, custom
    
    # Execution details
    status: str = Field(default="pending", max_length=20, index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    
    # Tool call details
    tool_input: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    tool_output: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    
    # Error handling
    error_message: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    
    # Metadata
    tool_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TokenUsageModel(SQLModel, table=True):
    """Detailed token usage tracking"""
    
    __tablename__ = "token_usage_logs"
    
    # Primary identification
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    workflow_execution_id: Optional[UUID] = Field(foreign_key="workflow_executions.id", index=True)
    node_execution_id: Optional[UUID] = Field(foreign_key="node_executions.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    contact_id: Optional[UUID] = Field(default=None)
    
    # Model details
    model_name: str = Field(max_length=100, index=True)
    model_provider: str = Field(max_length=50)
    
    # Usage metrics
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    
    # Cost calculation
    cost_per_prompt_token: Optional[float] = Field(default=None)
    cost_per_completion_token: Optional[float] = Field(default=None)
    total_cost_usd: float = Field(default=0.0)
    
    # Context
    usage_type: str = Field(max_length=50)  # conversation, tool_call, analysis, etc
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Metadata
    usage_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))