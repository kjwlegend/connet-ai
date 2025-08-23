"""
LangGraph Node Registry

Registry for managing workflow nodes, node types, and node configurations.
Provides centralized management of all available workflow processing nodes.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Type
from uuid import UUID
from dataclasses import dataclass
from enum import Enum

from app.services.langgraph.state_models import ConversationState


logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    """Available workflow node types"""
    
    # Input processing nodes
    INPUT_VALIDATOR = "input_validator"
    MESSAGE_PARSER = "message_parser" 
    MENTION_EXTRACTOR = "mention_extractor"
    
    # Routing nodes
    CONTACT_ROUTER = "contact_router"
    MENTION_ROUTER = "mention_router"
    PARALLEL_ROUTER = "parallel_router"
    SEQUENTIAL_ROUTER = "sequential_router"
    
    # Processing nodes
    CONTACT_PROCESSOR = "contact_processor"
    AI_RESPONDER = "ai_responder"
    TOOL_EXECUTOR = "tool_executor"
    
    # Aggregation nodes
    RESPONSE_AGGREGATOR = "response_aggregator" 
    CONSENSUS_BUILDER = "consensus_builder"
    PRIORITY_SELECTOR = "priority_selector"
    
    # Output nodes
    RESPONSE_FORMATTER = "response_formatter"
    MESSAGE_PERSISTER = "message_persister"
    NOTIFICATION_SENDER = "notification_sender"
    
    # Error handling nodes
    ERROR_HANDLER = "error_handler"
    FALLBACK_PROCESSOR = "fallback_processor"
    RETRY_MANAGER = "retry_manager"


@dataclass
class NodeDefinition:
    """Definition of a workflow node"""
    
    node_id: str
    node_type: NodeType
    name: str
    description: str
    handler_function: Callable[[ConversationState], ConversationState]
    config: Dict[str, Any]
    dependencies: List[str]
    timeout_seconds: Optional[int] = 30
    retry_count: int = 0
    is_async: bool = True
    
    
@dataclass
class NodeExecutionResult:
    """Result of node execution"""
    
    node_id: str
    success: bool
    output_state: Dict[str, Any]
    execution_time_ms: int
    token_usage: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class NodeRegistry:
    """Registry for managing workflow nodes"""
    
    def __init__(self):
        self.nodes: Dict[str, NodeDefinition] = {}
        self.node_types: Dict[NodeType, List[str]] = {}
        self._initialize_default_nodes()
        
    def _initialize_default_nodes(self):
        """Initialize default workflow nodes"""
        
        # Input processing nodes
        self.register_node(NodeDefinition(
            node_id="validate_input",
            node_type=NodeType.INPUT_VALIDATOR,
            name="Input Validator",
            description="Validates user input and conversation context",
            handler_function=self._validate_input,
            config={"max_message_length": 10000},
            dependencies=[]
        ))
        
        self.register_node(NodeDefinition(
            node_id="parse_message",
            node_type=NodeType.MESSAGE_PARSER,
            name="Message Parser",
            description="Parses message content and extracts metadata",
            handler_function=self._parse_message,
            config={"enable_emotion_detection": True},
            dependencies=["validate_input"]
        ))
        
        self.register_node(NodeDefinition(
            node_id="extract_mentions",
            node_type=NodeType.MENTION_EXTRACTOR,
            name="Mention Extractor",
            description="Extracts @mentions from message content",
            handler_function=self._extract_mentions,
            config={"mention_pattern": r"@([a-zA-Z0-9_-]+)"},
            dependencies=["parse_message"]
        ))
        
        # Routing nodes
        self.register_node(NodeDefinition(
            node_id="route_mentions",
            node_type=NodeType.MENTION_ROUTER,
            name="Mention Router",
            description="Routes messages to specifically mentioned contacts",
            handler_function=self._route_mentions,
            config={"max_mentions": 10},
            dependencies=["extract_mentions"]
        ))
        
        self.register_node(NodeDefinition(
            node_id="route_parallel",
            node_type=NodeType.PARALLEL_ROUTER,
            name="Parallel Router", 
            description="Routes messages for parallel processing by multiple contacts",
            handler_function=self._route_parallel,
            config={"max_parallel": 5},
            dependencies=["validate_input"]
        ))
        
        # Processing nodes
        self.register_node(NodeDefinition(
            node_id="process_contact",
            node_type=NodeType.CONTACT_PROCESSOR,
            name="Contact Processor",
            description="Processes message for a specific contact/agent",
            handler_function=self._process_contact,
            config={"include_context": True},
            dependencies=[]
        ))
        
        self.register_node(NodeDefinition(
            node_id="generate_ai_response",
            node_type=NodeType.AI_RESPONDER,
            name="AI Response Generator",
            description="Generates AI response using LLM",
            handler_function=self._generate_ai_response,
            config={"max_tokens": 2000, "temperature": 0.7},
            dependencies=["process_contact"]
        ))
        
        # Aggregation nodes
        self.register_node(NodeDefinition(
            node_id="aggregate_responses",
            node_type=NodeType.RESPONSE_AGGREGATOR,
            name="Response Aggregator",
            description="Aggregates multiple responses into final result",
            handler_function=self._aggregate_responses,
            config={"aggregation_strategy": "priority_weighted"},
            dependencies=[]
        ))
        
        # Output nodes
        self.register_node(NodeDefinition(
            node_id="format_response",
            node_type=NodeType.RESPONSE_FORMATTER,
            name="Response Formatter",
            description="Formats final response for output",
            handler_function=self._format_response,
            config={"include_metadata": True},
            dependencies=["aggregate_responses"]
        ))
        
        self.register_node(NodeDefinition(
            node_id="persist_message",
            node_type=NodeType.MESSAGE_PERSISTER,
            name="Message Persister",
            description="Persists messages and responses to database",
            handler_function=self._persist_message,
            config={"auto_commit": True},
            dependencies=["format_response"]
        ))
        
        # Error handling nodes
        self.register_node(NodeDefinition(
            node_id="handle_error",
            node_type=NodeType.ERROR_HANDLER,
            name="Error Handler",
            description="Handles workflow errors gracefully",
            handler_function=self._handle_error,
            config={"log_errors": True, "user_friendly_messages": True},
            dependencies=[]
        ))
    
    def register_node(self, node_def: NodeDefinition) -> None:
        """Register a new workflow node"""
        
        if node_def.node_id in self.nodes:
            logger.warning(f"Node {node_def.node_id} already registered, overriding")
        
        self.nodes[node_def.node_id] = node_def
        
        # Index by node type
        if node_def.node_type not in self.node_types:
            self.node_types[node_def.node_type] = []
        
        if node_def.node_id not in self.node_types[node_def.node_type]:
            self.node_types[node_def.node_type].append(node_def.node_id)
        
        logger.info(f"Registered node: {node_def.node_id} ({node_def.node_type})")
    
    def get_node(self, node_id: str) -> Optional[NodeDefinition]:
        """Get node definition by ID"""
        return self.nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[NodeDefinition]:
        """Get all nodes of a specific type"""
        node_ids = self.node_types.get(node_type, [])
        return [self.nodes[node_id] for node_id in node_ids if node_id in self.nodes]
    
    def get_available_nodes(self) -> List[str]:
        """Get list of all available node IDs"""
        return list(self.nodes.keys())
    
    def validate_dependencies(self, node_id: str, available_nodes: List[str]) -> bool:
        """Validate that node dependencies are satisfied"""
        
        node = self.get_node(node_id)
        if not node:
            return False
        
        for dep in node.dependencies:
            if dep not in available_nodes:
                logger.error(f"Node {node_id} dependency {dep} not available")
                return False
        
        return True
    
    def get_execution_order(self, node_ids: List[str]) -> List[str]:
        """Get optimal execution order for nodes based on dependencies"""
        
        # Simple topological sort for dependency resolution
        ordered = []
        remaining = node_ids.copy()
        
        while remaining:
            # Find nodes with all dependencies satisfied
            ready = []
            for node_id in remaining:
                node = self.get_node(node_id)
                if node and all(dep in ordered for dep in node.dependencies):
                    ready.append(node_id)
            
            if not ready:
                # Circular dependency or missing dependency
                logger.error("Cannot resolve node dependencies")
                break
            
            # Add ready nodes to ordered list
            for node_id in ready:
                ordered.append(node_id)
                remaining.remove(node_id)
        
        return ordered
    
    # Default node handler functions
    # These are placeholders - actual implementations should be provided by WorkflowEngine
    
    def _validate_input(self, state: ConversationState) -> ConversationState:
        """Placeholder for input validation"""
        return {**state, 'validation_passed': True}
    
    def _parse_message(self, state: ConversationState) -> ConversationState:
        """Placeholder for message parsing"""
        return {**state, 'message_parsed': True}
    
    def _extract_mentions(self, state: ConversationState) -> ConversationState:
        """Placeholder for mention extraction"""
        return {**state, 'mentions_extracted': True}
    
    def _route_mentions(self, state: ConversationState) -> ConversationState:
        """Placeholder for mention routing"""
        return {**state, 'routing_complete': True}
    
    def _route_parallel(self, state: ConversationState) -> ConversationState:
        """Placeholder for parallel routing"""
        return {**state, 'parallel_routing_complete': True}
    
    def _process_contact(self, state: ConversationState) -> ConversationState:
        """Placeholder for contact processing"""
        return {**state, 'contact_processed': True}
    
    def _generate_ai_response(self, state: ConversationState) -> ConversationState:
        """Placeholder for AI response generation"""
        return {**state, 'ai_response_generated': True}
    
    def _aggregate_responses(self, state: ConversationState) -> ConversationState:
        """Placeholder for response aggregation"""
        return {**state, 'responses_aggregated': True}
    
    def _format_response(self, state: ConversationState) -> ConversationState:
        """Placeholder for response formatting"""
        return {**state, 'response_formatted': True}
    
    def _persist_message(self, state: ConversationState) -> ConversationState:
        """Placeholder for message persistence"""
        return {**state, 'message_persisted': True}
    
    def _handle_error(self, state: ConversationState) -> ConversationState:
        """Placeholder for error handling"""
        return {**state, 'error_handled': True}


# Global registry instance
node_registry = NodeRegistry()


def get_node_registry() -> NodeRegistry:
    """Get the global node registry instance"""
    return node_registry