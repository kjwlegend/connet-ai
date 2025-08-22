"""
LangGraph State Models

Defines the state structures used in LangGraph workflows.
"""

from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional, Union
from uuid import UUID
from enum import Enum


class WorkflowType(str, Enum):
    """Workflow execution types"""
    SINGLE_CONTACT = "single_contact"
    MENTION_ROUTING = "mention_routing" 
    PARALLEL_DISCUSSION = "parallel_discussion"
    SEQUENTIAL_PROCESSING = "sequential_processing"


class MessageState(TypedDict):
    """Individual message in conversation state"""
    id: Optional[str]
    content: str
    sender_id: str
    sender_type: str  # 'user' or 'agent'
    sender_name: str
    timestamp: str
    message_type: str
    mentions: List[str]


class ContactInfo(TypedDict):
    """Contact information in workflow state"""
    contact_id: str
    agent_id: str
    follower_id: str
    agent_name: str
    display_name: str
    system_prompt: str
    model_preferences: Dict[str, Any]
    is_active: bool


class ContactResponse(TypedDict):
    """Response from a contact during workflow execution"""
    contact_id: str
    contact_name: str
    agent_id: str
    response: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]]
    tokens_used: Optional[int]
    timestamp: str
    status: str  # 'success', 'failed', 'timeout'
    error: Optional[str]


class ConversationState(TypedDict):
    """Main conversation state for LangGraph workflows"""
    # Basic information
    conversation_id: str
    workflow_execution_id: str
    user_id: str
    
    # Current message processing
    current_message: str
    current_message_id: Optional[str]
    message_history: List[MessageState]
    
    # Participants information
    active_contacts: List[ContactInfo]
    mentioned_contacts: List[str]  # Contact IDs that were @mentioned
    
    # Execution state
    workflow_type: str
    current_step: str
    execution_path: List[str]
    contact_responses: Dict[str, ContactResponse]
    
    # Memory context (simplified for now, can be enhanced with Mem0 later)
    conversation_memory: Optional[str]
    
    # Metadata
    routing_strategy: str
    started_at: str
    metadata: Dict[str, Any]


class WorkflowConfig(TypedDict):
    """Configuration for workflow execution"""
    max_parallel_contacts: int
    timeout_seconds: int
    enable_tracing: bool
    enable_memory: bool
    fallback_on_error: bool


class NodeExecutionResult(TypedDict):
    """Result of a single node execution"""
    node_id: str
    contact_id: Optional[str]
    status: str
    output: Any
    error: Optional[str]
    tokens_used: int
    duration_ms: int
    timestamp: str