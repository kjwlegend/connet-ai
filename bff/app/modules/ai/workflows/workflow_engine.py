"""
LangGraph Workflow Engine

Core engine for executing LangGraph-based conversation workflows.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from uuid import UUID, uuid4

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.modules.ai.workflows.state_models import (
    ConversationState, 
    ContactInfo, 
    ContactResponse,
    WorkflowType,
    MessageState,
    WorkflowConfig
)
from app.modules.ai.workflows.contact_manager import ContactInstanceManager
from app.modules.ai.workflows.mention_parser import MentionParser
from app.modules.ai.workflows.conversation_memory_manager import ConversationMemoryManager
from app.core.services import BaseService


class WorkflowEngine(BaseService):
    """LangGraph-based workflow engine for conversation processing"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.settings = get_settings()
        self.contact_manager = ContactInstanceManager(session)
        self.mention_parser = MentionParser()
        self.memory_manager = ConversationMemoryManager(session)
        
        # Initialize OpenAI client
        self._init_llm_client()
        
        # Default workflow configuration
        self.default_config = WorkflowConfig(
            max_parallel_contacts=5,
            timeout_seconds=30,
            enable_tracing=self.settings.langsmith_tracing,
            enable_memory=True,
            fallback_on_error=True
        )
    
    def _init_llm_client(self):
        """Initialize the LLM client with custom base URL"""
        
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Configure LangSmith tracing if enabled
        if self.settings.langsmith_tracing and self.settings.langsmith_api_key:
            import os
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = self.settings.langsmith_endpoint
            os.environ["LANGCHAIN_API_KEY"] = self.settings.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.settings.langsmith_project
        
        self.llm = ChatOpenAI(
            model=self.settings.openai_default_model,
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
            temperature=0.7,
            max_tokens=2000
        )
    
    async def execute_conversation_workflow(
        self,
        conversation_id: UUID,
        user_id: UUID,
        message: str,
        message_id: Optional[UUID] = None,
        config: Optional[WorkflowConfig] = None
    ) -> Dict[str, Any]:
        """Execute a complete conversation workflow"""
        
        workflow_config = config or self.default_config
        execution_id = uuid4()
        
        try:
            # Build initial state
            initial_state = await self._build_initial_state(
                conversation_id, user_id, message, message_id, execution_id
            )
            
            # Determine workflow type and build graph
            workflow_graph = await self._build_workflow_graph(initial_state, workflow_config)
            
            # Execute workflow
            result = await workflow_graph.ainvoke(initial_state)
            
            # Store workflow results in memory
            await self._store_workflow_memories(result, user_id, conversation_id)
            
            # Process and return result
            return await self._process_workflow_result(result, execution_id)
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}", extra={
                "conversation_id": str(conversation_id),
                "user_id": str(user_id),
                "execution_id": str(execution_id),
                "error": str(e)
            })
            raise
    
    async def _build_initial_state(
        self,
        conversation_id: UUID,
        user_id: UUID,
        message: str,
        message_id: Optional[UUID],
        execution_id: UUID
    ) -> ConversationState:
        """Build initial workflow state"""
        
        # Get conversation participants
        active_contacts = await self.contact_manager.get_conversation_participants(conversation_id)
        
        # Parse mentions
        routing_context = self.mention_parser.build_routing_context(message, active_contacts)
        mentioned_contacts = [c["contact_id"] for c in routing_context["mentioned_contacts"]]
        
        # Get enhanced memory context
        memory_context = await self.memory_manager.get_conversation_context(
            conversation_id=conversation_id,
            user_id=user_id,
            current_message=message,
            max_memories=10
        )
        
        # Build message state
        current_message_state = MessageState(
            id=str(message_id) if message_id else None,
            content=message,
            sender_id=str(user_id),
            sender_type="user",
            sender_name="User",  # TODO: Get actual username
            timestamp=datetime.utcnow().isoformat(),
            message_type="text",
            mentions=routing_context["mentions_found"]
        )
        
        return ConversationState(
            conversation_id=str(conversation_id),
            workflow_execution_id=str(execution_id),
            user_id=str(user_id),
            current_message=message,
            current_message_id=str(message_id) if message_id else None,
            message_history=[current_message_state],
            active_contacts=active_contacts,
            mentioned_contacts=mentioned_contacts,
            workflow_type=self._determine_workflow_type(routing_context, active_contacts),
            current_step="initialized",
            execution_path=[],
            contact_responses={},
            conversation_memory=memory_context,
            routing_strategy=routing_context["routing_strategy"],
            started_at=datetime.utcnow().isoformat(),
            metadata={}
        )
    
    def _determine_workflow_type(
        self, 
        routing_context: Dict[str, Any], 
        active_contacts: List[ContactInfo]
    ) -> str:
        """Determine the appropriate workflow type"""
        
        if routing_context["has_mentions"]:
            return WorkflowType.MENTION_ROUTING.value
        elif len(active_contacts) == 1:
            return WorkflowType.SINGLE_CONTACT.value
        elif len(active_contacts) <= 3:
            return WorkflowType.PARALLEL_DISCUSSION.value
        else:
            return WorkflowType.SEQUENTIAL_PROCESSING.value
    
    async def _build_workflow_graph(
        self, 
        initial_state: ConversationState,
        config: WorkflowConfig
    ) -> StateGraph:
        """Build the appropriate workflow graph"""
        
        workflow_type = initial_state["workflow_type"]
        
        if workflow_type == WorkflowType.SINGLE_CONTACT.value:
            return self._build_single_contact_workflow(initial_state, config)
        elif workflow_type == WorkflowType.MENTION_ROUTING.value:
            return self._build_mention_routing_workflow(initial_state, config)
        elif workflow_type == WorkflowType.PARALLEL_DISCUSSION.value:
            return self._build_parallel_discussion_workflow(initial_state, config)
        else:
            return self._build_sequential_workflow(initial_state, config)
    
    def _build_single_contact_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig
    ) -> StateGraph:
        """Build single contact workflow"""
        
        workflow = StateGraph(ConversationState)
        
        # Add contact processing node
        workflow.add_node("contact_processor", self._create_contact_node(initial_state["active_contacts"][0]))
        workflow.add_node("response_formatter", self._format_single_response)
        
        # Define flow
        workflow.set_entry_point("contact_processor")
        workflow.add_edge("contact_processor", "response_formatter")
        workflow.add_edge("response_formatter", END)
        
        return workflow.compile()
    
    def _build_mention_routing_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig
    ) -> StateGraph:
        """Build mention routing workflow"""
        
        workflow = StateGraph(ConversationState)
        
        # Add mention router
        workflow.add_node("mention_router", self._route_mentions)
        
        # Add nodes for mentioned contacts
        mentioned_contact_ids = set(initial_state["mentioned_contacts"])
        
        for contact in initial_state["active_contacts"]:
            if contact["contact_id"] in mentioned_contact_ids:
                node_id = f"contact_{contact['contact_id']}"
                workflow.add_node(node_id, self._create_contact_node(contact))
        
        # Add response aggregator
        workflow.add_node("response_aggregator", self._aggregate_responses)
        
        # Define flow
        workflow.set_entry_point("mention_router")
        
        # Connect router to mentioned contacts
        for contact in initial_state["active_contacts"]:
            if contact["contact_id"] in mentioned_contact_ids:
                node_id = f"contact_{contact['contact_id']}"
                workflow.add_edge("mention_router", node_id)
                workflow.add_edge(node_id, "response_aggregator")
        
        workflow.add_edge("response_aggregator", END)
        
        return workflow.compile()
    
    def _build_parallel_discussion_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig
    ) -> StateGraph:
        """Build enhanced parallel discussion workflow with multiple collaboration modes"""
        
        workflow = StateGraph(ConversationState)
        
        # Determine collaboration mode based on conversation context and contact count
        collaboration_mode = self._determine_collaboration_mode(initial_state)
        
        if collaboration_mode == "parallel_processing":
            return self._build_parallel_processing_workflow(initial_state, config, workflow)
        elif collaboration_mode == "debate_mode":
            return self._build_debate_workflow(initial_state, config, workflow)
        elif collaboration_mode == "expert_panel":
            return self._build_expert_panel_workflow(initial_state, config, workflow)
        else:
            # Default parallel discussion
            return self._build_default_parallel_workflow(initial_state, config, workflow)

    def _determine_collaboration_mode(self, state: ConversationState) -> str:
        """Determine the best collaboration mode for the contacts"""
        
        contacts = state["active_contacts"]
        message = state["current_message"]
        
        # Check for debate keywords
        debate_keywords = ["vs", "versus", "compare", "which is better", "debate", "argue"]
        if any(keyword in message.lower() for keyword in debate_keywords):
            return "debate_mode"
        
        # Check for expert consultation keywords
        expert_keywords = ["expert opinion", "professional advice", "multiple perspectives", "panel"]
        if any(keyword in message.lower() for keyword in expert_keywords):
            return "expert_panel"
        
        # Check contact configurations for parallel processing preference
        if len(contacts) <= 3 and any(
            contact.get("custom_config", {}).get("parallel_processing", False) 
            for contact in contacts
        ):
            return "parallel_processing"
        
        return "default_parallel"

    def _build_parallel_processing_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig,
        workflow: StateGraph
    ) -> StateGraph:
        """Build true parallel processing workflow"""
        
        # Add discussion coordinator
        workflow.add_node("discussion_coordinator", self._coordinate_discussion)
        
        # Add parallel contact nodes with priority-based execution
        sorted_contacts = sorted(
            initial_state["active_contacts"], 
            key=lambda c: c.get("workflow_priority", 0), 
            reverse=True
        )
        
        for contact in sorted_contacts:
            node_id = f"contact_{contact['contact_id']}"
            workflow.add_node(node_id, self._create_contact_node(contact))
        
        # Add response synthesizer instead of simple aggregator
        workflow.add_node("response_synthesizer", self._synthesize_parallel_responses)
        
        # Define parallel flow
        workflow.set_entry_point("discussion_coordinator")
        
        for contact in sorted_contacts:
            node_id = f"contact_{contact['contact_id']}"
            workflow.add_edge("discussion_coordinator", node_id)
            workflow.add_edge(node_id, "response_synthesizer")
        
        workflow.add_edge("response_synthesizer", END)
        
        return workflow.compile()

    def _build_debate_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig,
        workflow: StateGraph
    ) -> StateGraph:
        """Build debate-style workflow for contrasting viewpoints"""
        
        contacts = initial_state["active_contacts"]
        
        # Add debate moderator
        workflow.add_node("debate_moderator", self._moderate_debate)
        
        # First round: Initial positions
        for i, contact in enumerate(contacts):
            node_id = f"position_{i}_{contact['contact_id']}"
            workflow.add_node(node_id, self._create_position_node(contact, f"position_{i}"))
        
        # Second round: Rebuttals (if more than 2 contacts)
        if len(contacts) > 2:
            for i, contact in enumerate(contacts):
                node_id = f"rebuttal_{i}_{contact['contact_id']}"
                workflow.add_node(node_id, self._create_rebuttal_node(contact))
        
        # Add debate summarizer
        workflow.add_node("debate_summarizer", self._summarize_debate)
        
        # Define debate flow
        workflow.set_entry_point("debate_moderator")
        
        # Connect initial positions
        for i, contact in enumerate(contacts):
            position_node = f"position_{i}_{contact['contact_id']}"
            workflow.add_edge("debate_moderator", position_node)
            
            if len(contacts) > 2:
                rebuttal_node = f"rebuttal_{i}_{contact['contact_id']}"
                workflow.add_edge(position_node, rebuttal_node)
                workflow.add_edge(rebuttal_node, "debate_summarizer")
            else:
                workflow.add_edge(position_node, "debate_summarizer")
        
        workflow.add_edge("debate_summarizer", END)
        
        return workflow.compile()

    def _build_expert_panel_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig,
        workflow: StateGraph
    ) -> StateGraph:
        """Build expert panel consultation workflow"""
        
        contacts = initial_state["active_contacts"]
        
        # Add panel coordinator
        workflow.add_node("panel_coordinator", self._coordinate_expert_panel)
        
        # Add expert consultation nodes
        for contact in contacts:
            node_id = f"expert_{contact['contact_id']}"
            workflow.add_node(node_id, self._create_expert_node(contact))
        
        # Add cross-examination phase if enabled
        workflow.add_node("cross_examination", self._conduct_cross_examination)
        
        # Add consensus building
        workflow.add_node("expert_consensus", self._build_expert_consensus)
        
        # Define expert panel flow
        workflow.set_entry_point("panel_coordinator")
        
        # First phase: Individual expert opinions
        for contact in contacts:
            expert_node = f"expert_{contact['contact_id']}"
            workflow.add_edge("panel_coordinator", expert_node)
            workflow.add_edge(expert_node, "cross_examination")
        
        # Final consensus
        workflow.add_edge("cross_examination", "expert_consensus")
        workflow.add_edge("expert_consensus", END)
        
        return workflow.compile()

    def _build_default_parallel_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig,
        workflow: StateGraph
    ) -> StateGraph:
        """Build default parallel discussion workflow"""
        
        # Add discussion coordinator
        workflow.add_node("discussion_coordinator", self._coordinate_discussion)
        
        # Add parallel contact nodes
        for contact in initial_state["active_contacts"]:
            node_id = f"contact_{contact['contact_id']}"
            workflow.add_node(node_id, self._create_contact_node(contact))
        
        # Add consensus builder
        workflow.add_node("consensus_builder", self._build_consensus)
        
        # Define parallel flow
        workflow.set_entry_point("discussion_coordinator")
        
        for contact in initial_state["active_contacts"]:
            node_id = f"contact_{contact['contact_id']}"
            workflow.add_edge("discussion_coordinator", node_id)
            workflow.add_edge(node_id, "consensus_builder")
        
        workflow.add_edge("consensus_builder", END)
        
        return workflow.compile()
    
    def _build_sequential_workflow(
        self, 
        initial_state: ConversationState, 
        config: WorkflowConfig
    ) -> StateGraph:
        """Build sequential processing workflow"""
        
        workflow = StateGraph(ConversationState)
        
        # Sort contacts by some priority (for now, just use order)
        sorted_contacts = initial_state["active_contacts"]
        
        # Add sequential nodes
        for i, contact in enumerate(sorted_contacts):
            node_id = f"contact_{contact['contact_id']}"
            workflow.add_node(node_id, self._create_contact_node(contact))
            
            if i == 0:
                workflow.set_entry_point(node_id)
            else:
                prev_node = f"contact_{sorted_contacts[i-1]['contact_id']}"
                workflow.add_edge(prev_node, node_id)
        
        # Connect last node to END
        last_node = f"contact_{sorted_contacts[-1]['contact_id']}"
        workflow.add_edge(last_node, END)
        
        return workflow.compile()
    
    def _create_contact_node(self, contact: ContactInfo) -> Callable:
        """Create an enhanced contact processing node with personalization support"""
        
        async def contact_processor(state: ConversationState) -> ConversationState:
            try:
                # Use personalized system prompt and model preferences
                system_prompt = contact["system_prompt"]
                user_message = state["current_message"]
                
                # Apply contact-specific model preferences
                model_prefs = contact.get("model_preferences", {})
                
                # Create LLM with contact-specific configuration
                contact_llm = ChatOpenAI(
                    model=model_prefs.get("model", self.settings.openai_default_model),
                    api_key=self.settings.openai_api_key,
                    base_url=self.settings.openai_base_url,
                    temperature=model_prefs.get("temperature", 0.7),
                    max_tokens=model_prefs.get("max_tokens", 2000),
                    top_p=model_prefs.get("top_p", 1.0)
                )
                
                # Check resource limits
                resource_limits = contact.get("resource_limits", {})
                if resource_limits.get("disable_llm_calls", False):
                    raise Exception("LLM calls disabled for this contact instance")
                
                # Build enhanced message context
                messages = []
                
                # Add system prompt (potentially customized per contact)
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                
                # Add conversation context if available
                if state.get("conversation_memory"):
                    memory_context = await self._build_memory_context_prompt(
                        state["conversation_memory"], contact
                    )
                    if memory_context:
                        messages.append({"role": "system", "content": memory_context})
                
                # Add user message
                messages.append({"role": "user", "content": user_message})
                
                # Apply timeout from resource limits
                timeout = resource_limits.get("max_response_time", 30)
                
                # Execute with timeout
                response = await asyncio.wait_for(
                    contact_llm.ainvoke(messages),
                    timeout=timeout
                )
                
                # Validate response length limits
                max_response_length = resource_limits.get("max_response_length", 5000)
                response_content = response.content
                if len(response_content) > max_response_length:
                    response_content = response_content[:max_response_length] + "... [truncated]"
                
                # Apply response filtering based on contact configuration
                response_content = self._apply_response_filtering(response_content, contact)
                
                # Create enhanced contact response
                contact_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=response_content,
                    tool_calls=None,  # TODO: Implement tool calls with permission checks
                    tokens_used=response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                # Update state with enhanced tracking
                state["contact_responses"][contact["contact_id"]] = contact_response
                state["execution_path"].append(f"contact_{contact['contact_id']}")
                state["current_step"] = f"processed_contact_{contact['contact_id']}"
                
                # Update metadata with contact-specific info
                if "contact_execution_details" not in state["metadata"]:
                    state["metadata"]["contact_execution_details"] = {}
                
                state["metadata"]["contact_execution_details"][contact["contact_id"]] = {
                    "model_used": model_prefs.get("model", self.settings.openai_default_model),
                    "temperature": model_prefs.get("temperature", 0.7),
                    "tokens_consumed": contact_response["tokens_used"],
                    "has_custom_prompt": bool(contact.get("custom_config")),
                    "resource_limits_applied": len(resource_limits) > 0
                }
                
                return state
                
            except asyncio.TimeoutError:
                # Handle timeout specifically
                error_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=None,
                    tool_calls=None,
                    tokens_used=0,
                    timestamp=datetime.utcnow().isoformat(),
                    status="timeout",
                    error=f"Response timeout after {resource_limits.get('max_response_time', 30)}s"
                )
                
                state["contact_responses"][contact["contact_id"]] = error_response
                state["execution_path"].append(f"contact_timeout_{contact['contact_id']}")
                
                return state
                
            except Exception as e:
                # Handle general errors
                error_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=None,
                    tool_calls=None,
                    tokens_used=0,
                    timestamp=datetime.utcnow().isoformat(),
                    status="failed",
                    error=str(e)
                )
                
                state["contact_responses"][contact["contact_id"]] = error_response
                state["execution_path"].append(f"contact_error_{contact['contact_id']}")
                
                return state
        
        return contact_processor

    def _apply_response_filtering(self, response: str, contact: ContactInfo) -> str:
        """Apply contact-specific response filtering"""
        
        # Get custom configuration
        custom_config = contact.get("custom_config", {})
        
        # Apply response style transformations
        if custom_config.get("response_style") == "concise":
            # Simple concise transformation (would be more sophisticated in practice)
            sentences = response.split('. ')
            if len(sentences) > 3:
                response = '. '.join(sentences[:3]) + '.'
        
        elif custom_config.get("response_style") == "detailed":
            # Could expand response or ensure minimum detail level
            pass
        
        # Apply formatting preferences
        if custom_config.get("include_examples", False) and "example" not in response.lower():
            response += "\n\nFor example, you might want to consider the specific context of your situation."
        
        return response
    
    async def _route_mentions(self, state: ConversationState) -> ConversationState:
        """Route message to mentioned contacts"""
        
        state["current_step"] = "routing_mentions"
        state["execution_path"].append("mention_router")
        
        # Add routing metadata
        state["metadata"]["routing_decisions"] = {
            "mentioned_contacts": state["mentioned_contacts"],
            "routing_strategy": "mention_based"
        }
        
        return state
    
    async def _coordinate_discussion(self, state: ConversationState) -> ConversationState:
        """Coordinate parallel discussion"""
        
        state["current_step"] = "coordinating_discussion"
        state["execution_path"].append("discussion_coordinator")
        
        return state
    
    async def _format_single_response(self, state: ConversationState) -> ConversationState:
        """Format single contact response"""
        
        state["current_step"] = "formatting_response"
        state["execution_path"].append("response_formatter")
        
        return state
    
    async def _aggregate_responses(self, state: ConversationState) -> ConversationState:
        """Aggregate multiple contact responses"""
        
        state["current_step"] = "aggregating_responses"
        state["execution_path"].append("response_aggregator")
        
        successful_responses = [
            response for response in state["contact_responses"].values()
            if response["status"] == "success"
        ]
        
        state["metadata"]["aggregation_summary"] = {
            "successful_count": len(successful_responses),
            "failed_count": len(state["contact_responses"]) - len(successful_responses),
            "total_tokens": sum(r["tokens_used"] or 0 for r in successful_responses)
        }
        
        return state
    
    async def _build_consensus(self, state: ConversationState) -> ConversationState:
        """Build consensus from parallel responses"""
        
        state["current_step"] = "building_consensus"
        state["execution_path"].append("consensus_builder")
        
        return state
    
    async def _process_workflow_result(
        self, 
        result: ConversationState, 
        execution_id: UUID
    ) -> Dict[str, Any]:
        """Process and format workflow execution result"""
        
        successful_responses = [
            response for response in result["contact_responses"].values()
            if response["status"] == "success"
        ]
        
        failed_responses = [
            response for response in result["contact_responses"].values()
            if response["status"] == "failed"
        ]
        
        # Format final response
        if len(successful_responses) == 1:
            final_response = successful_responses[0]["response"]
        elif len(successful_responses) > 1:
            final_response = self._format_collaborative_response(successful_responses)
        else:
            final_response = "I apologize, but I'm unable to process your request at the moment."
        
        return {
            "execution_id": str(execution_id),
            "workflow_type": result["workflow_type"],
            "final_response": final_response,
            "contact_responses": result["contact_responses"],
            "execution_path": result["execution_path"],
            "metadata": result["metadata"],
            "success": len(successful_responses) > 0,
            "total_tokens": sum(r["tokens_used"] or 0 for r in successful_responses),
            "duration": "N/A"  # TODO: Calculate actual duration
        }
    
    def _format_collaborative_response(self, responses: List[ContactResponse]) -> str:
        """Format multiple responses into collaborative format"""
        
        formatted_parts = []
        for response in responses:
            contact_name = response["contact_name"]
            content = response["response"]
            formatted_parts.append(f"**{contact_name}**: {content}")
        
        return "\n\n".join(formatted_parts)

    # Enhanced Collaboration Mode Handlers (Priority 3)

    def _create_position_node(self, contact: ContactInfo, position_label: str) -> Callable:
        """Create a position statement node for debate mode"""
        
        async def position_processor(state: ConversationState) -> ConversationState:
            try:
                # Build position-specific prompt
                base_prompt = contact["system_prompt"]
                position_prompt = f"{base_prompt}\n\nYou are participating in a debate/discussion. Present your initial position on the topic. Be clear, concise, and support your viewpoint with reasoning."
                
                user_message = state["current_message"]
                
                # Apply contact-specific model preferences
                model_prefs = contact.get("model_preferences", {})
                contact_llm = ChatOpenAI(
                    model=model_prefs.get("model", self.settings.openai_default_model),
                    api_key=self.settings.openai_api_key,
                    base_url=self.settings.openai_base_url,
                    temperature=model_prefs.get("temperature", 0.8),  # Slightly higher for debate
                    max_tokens=model_prefs.get("max_tokens", 1500)
                )
                
                messages = [
                    {"role": "system", "content": position_prompt},
                    {"role": "user", "content": f"Topic for debate: {user_message}"}
                ]
                
                response = await contact_llm.ainvoke(messages)
                
                contact_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=response.content,
                    tool_calls=None,
                    tokens_used=response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                state["contact_responses"][f"{position_label}_{contact['contact_id']}"] = contact_response
                state["execution_path"].append(f"{position_label}_{contact['contact_id']}")
                
                return state
                
            except Exception as e:
                error_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=None,
                    tool_calls=None,
                    tokens_used=0,
                    timestamp=datetime.utcnow().isoformat(),
                    status="failed",
                    error=str(e)
                )
                
                state["contact_responses"][f"{position_label}_{contact['contact_id']}"] = error_response
                return state
        
        return position_processor

    def _create_rebuttal_node(self, contact: ContactInfo) -> Callable:
        """Create a rebuttal node for debate mode"""
        
        async def rebuttal_processor(state: ConversationState) -> ConversationState:
            try:
                # Gather other positions for context
                other_positions = []
                for key, response in state["contact_responses"].items():
                    if key.startswith("position_") and response["status"] == "success":
                        other_positions.append(f"{response['contact_name']}: {response['response']}")
                
                base_prompt = contact["system_prompt"]
                rebuttal_prompt = f"""{base_prompt}

You are now in the rebuttal phase of a debate. You have seen the initial positions from other participants:

{chr(10).join(other_positions)}

Now provide a thoughtful rebuttal or counter-argument. Address specific points made by others while reinforcing your own perspective."""
                
                model_prefs = contact.get("model_preferences", {})
                contact_llm = ChatOpenAI(
                    model=model_prefs.get("model", self.settings.openai_default_model),
                    api_key=self.settings.openai_api_key,
                    base_url=self.settings.openai_base_url,
                    temperature=model_prefs.get("temperature", 0.7),
                    max_tokens=model_prefs.get("max_tokens", 1200)
                )
                
                messages = [
                    {"role": "system", "content": rebuttal_prompt},
                    {"role": "user", "content": "Please provide your rebuttal or counter-argument."}
                ]
                
                response = await contact_llm.ainvoke(messages)
                
                contact_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=response.content,
                    tool_calls=None,
                    tokens_used=response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                state["contact_responses"][f"rebuttal_{contact['contact_id']}"] = contact_response
                state["execution_path"].append(f"rebuttal_{contact['contact_id']}")
                
                return state
                
            except Exception as e:
                error_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=None,
                    tool_calls=None,
                    tokens_used=0,
                    timestamp=datetime.utcnow().isoformat(),
                    status="failed",
                    error=str(e)
                )
                
                state["contact_responses"][f"rebuttal_{contact['contact_id']}"] = error_response
                return state
        
        return rebuttal_processor

    def _create_expert_node(self, contact: ContactInfo) -> Callable:
        """Create an expert consultation node"""
        
        async def expert_processor(state: ConversationState) -> ConversationState:
            try:
                base_prompt = contact["system_prompt"]
                expert_prompt = f"""{base_prompt}

You are being consulted as an expert in your field. Please provide your professional opinion on the following matter. Structure your response as:
1. Initial Assessment
2. Key Considerations
3. Recommendations
4. Potential Risks/Limitations

Be thorough but concise, focusing on your area of expertise."""
                
                user_message = state["current_message"]
                
                model_prefs = contact.get("model_preferences", {})
                contact_llm = ChatOpenAI(
                    model=model_prefs.get("model", self.settings.openai_default_model),
                    api_key=self.settings.openai_api_key,
                    base_url=self.settings.openai_base_url,
                    temperature=model_prefs.get("temperature", 0.3),  # Lower for expert precision
                    max_tokens=model_prefs.get("max_tokens", 2500)
                )
                
                messages = [
                    {"role": "system", "content": expert_prompt},
                    {"role": "user", "content": f"Expert consultation request: {user_message}"}
                ]
                
                response = await contact_llm.ainvoke(messages)
                
                contact_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=response.content,
                    tool_calls=None,
                    tokens_used=response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                state["contact_responses"][f"expert_{contact['contact_id']}"] = contact_response
                state["execution_path"].append(f"expert_{contact['contact_id']}")
                
                return state
                
            except Exception as e:
                error_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=None,
                    tool_calls=None,
                    tokens_used=0,
                    timestamp=datetime.utcnow().isoformat(),
                    status="failed",
                    error=str(e)
                )
                
                state["contact_responses"][f"expert_{contact['contact_id']}"] = error_response
                return state
        
        return expert_processor

    async def _moderate_debate(self, state: ConversationState) -> ConversationState:
        """Moderate debate setup and context"""
        
        state["current_step"] = "debate_moderation"
        state["execution_path"].append("debate_moderator")
        
        # Set debate context
        state["metadata"]["debate_context"] = {
            "mode": "structured_debate",
            "participants": [contact["contact_id"] for contact in state["active_contacts"]],
            "rounds": 2 if len(state["active_contacts"]) > 2 else 1,
            "topic": state["current_message"]
        }
        
        return state

    async def _coordinate_expert_panel(self, state: ConversationState) -> ConversationState:
        """Coordinate expert panel consultation"""
        
        state["current_step"] = "expert_panel_coordination"
        state["execution_path"].append("panel_coordinator")
        
        # Set panel context
        state["metadata"]["panel_context"] = {
            "consultation_type": "expert_panel",
            "experts": [
                {"contact_id": contact["contact_id"], "expertise": contact.get("capabilities", [])}
                for contact in state["active_contacts"]
            ],
            "question": state["current_message"]
        }
        
        return state

    async def _synthesize_parallel_responses(self, state: ConversationState) -> ConversationState:
        """Synthesize parallel responses into cohesive answer"""
        
        state["current_step"] = "response_synthesis"
        state["execution_path"].append("response_synthesizer")
        
        successful_responses = [
            response for response in state["contact_responses"].values()
            if response["status"] == "success"
        ]
        
        if len(successful_responses) > 1:
            # Use LLM to synthesize responses
            synthesis_prompt = f"""You are a synthesis coordinator. Multiple AI agents have provided responses to a user question. Your task is to create a cohesive, comprehensive answer that incorporates the best insights from all responses.

Original Question: {state['current_message']}

Agent Responses:
{chr(10).join([f"{r['contact_name']}: {r['response']}" for r in successful_responses])}

Please synthesize these into a single, well-structured response that:
1. Addresses the original question comprehensively
2. Incorporates key insights from each agent
3. Resolves any contradictions or provides balanced perspectives
4. Maintains clarity and readability

Format your response naturally, without explicitly mentioning "Agent A said" unless necessary for clarity."""
            
            synthesis_llm = ChatOpenAI(
                model=self.settings.openai_default_model,
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                temperature=0.3,
                max_tokens=3000
            )
            
            try:
                synthesis_response = await synthesis_llm.ainvoke([
                    {"role": "system", "content": synthesis_prompt}
                ])
                
                # Create synthesized response
                synthesized_response = ContactResponse(
                    contact_id="synthesizer",
                    contact_name="Response Synthesizer",
                    agent_id="system",
                    response=synthesis_response.content,
                    tool_calls=None,
                    tokens_used=synthesis_response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                state["contact_responses"]["synthesized"] = synthesized_response
                
            except Exception as e:
                self.logger.error(f"Response synthesis failed: {e}")
                # Fall back to simple aggregation
                pass
        
        state["metadata"]["synthesis_summary"] = {
            "responses_synthesized": len(successful_responses),
            "synthesis_method": "llm_synthesis" if "synthesized" in state["contact_responses"] else "simple_aggregation"
        }
        
        return state

    async def _summarize_debate(self, state: ConversationState) -> ConversationState:
        """Summarize debate with key points and conclusions"""
        
        state["current_step"] = "debate_summary"
        state["execution_path"].append("debate_summarizer")
        
        # Collect all debate responses
        debate_responses = {}
        for key, response in state["contact_responses"].items():
            if response["status"] == "success" and ("position_" in key or "rebuttal_" in key):
                debate_responses[key] = response
        
        if debate_responses:
            summary_prompt = f"""You are a debate moderator tasked with summarizing a structured debate between AI agents.

Original Topic: {state['current_message']}

Debate Responses:
{chr(10).join([f"{key}: {response['response']}" for key, response in debate_responses.items()])}

Please provide a comprehensive debate summary that includes:
1. **Key Positions**: Main viewpoints presented
2. **Arguments**: Strongest arguments from each side
3. **Points of Agreement**: Areas where participants agreed
4. **Points of Disagreement**: Key differences in perspective
5. **Conclusion**: A balanced assessment of the discussion

Format this as a structured summary that would be helpful for someone who didn't witness the debate."""
            
            summary_llm = ChatOpenAI(
                model=self.settings.openai_default_model,
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                temperature=0.2,
                max_tokens=2000
            )
            
            try:
                summary_response = await summary_llm.ainvoke([
                    {"role": "system", "content": summary_prompt}
                ])
                
                debate_summary = ContactResponse(
                    contact_id="debate_moderator",
                    contact_name="Debate Moderator",
                    agent_id="system",
                    response=summary_response.content,
                    tool_calls=None,
                    tokens_used=summary_response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                state["contact_responses"]["debate_summary"] = debate_summary
                
            except Exception as e:
                self.logger.error(f"Debate summary failed: {e}")
        
        return state

    async def _conduct_cross_examination(self, state: ConversationState) -> ConversationState:
        """Conduct cross-examination phase for expert panel"""
        
        state["current_step"] = "cross_examination"
        state["execution_path"].append("cross_examination")
        
        # For now, this is a placeholder for cross-examination logic
        # In a full implementation, this could involve follow-up questions
        state["metadata"]["cross_examination"] = {
            "conducted": True,
            "method": "automatic_synthesis",
            "expert_count": len([r for r in state["contact_responses"].values() if r["status"] == "success"])
        }
        
        return state

    async def _build_expert_consensus(self, state: ConversationState) -> ConversationState:
        """Build expert consensus from panel consultation"""
        
        state["current_step"] = "expert_consensus"
        state["execution_path"].append("expert_consensus")
        
        expert_responses = [
            response for key, response in state["contact_responses"].items()
            if "expert_" in key and response["status"] == "success"
        ]
        
        if len(expert_responses) > 1:
            consensus_prompt = f"""You are facilitating an expert panel consensus. Multiple experts have provided their professional opinions on a question.

Original Question: {state['current_message']}

Expert Opinions:
{chr(10).join([f"Expert {r['contact_name']}: {r['response']}" for r in expert_responses])}

Please synthesize these expert opinions into a consensus recommendation that:
1. **Synthesizes Agreement**: Areas where experts agree
2. **Addresses Differences**: How to handle conflicting expert opinions
3. **Provides Clear Recommendations**: Actionable advice based on expert input
4. **Notes Limitations**: Any caveats or areas requiring further consideration

Present this as a professional expert panel conclusion."""
            
            consensus_llm = ChatOpenAI(
                model=self.settings.openai_default_model,
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                temperature=0.2,
                max_tokens=2500
            )
            
            try:
                consensus_response = await consensus_llm.ainvoke([
                    {"role": "system", "content": consensus_prompt}
                ])
                
                expert_consensus = ContactResponse(
                    contact_id="expert_panel",
                    contact_name="Expert Panel Consensus",
                    agent_id="system",
                    response=consensus_response.content,
                    tool_calls=None,
                    tokens_used=consensus_response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                state["contact_responses"]["expert_consensus"] = expert_consensus
                
            except Exception as e:
                self.logger.error(f"Expert consensus failed: {e}")
        
        return state
    
    async def _store_workflow_memories(
        self, 
        result: ConversationState, 
        user_id: UUID, 
        conversation_id: UUID
    ):
        """Store workflow execution results as memories."""
        
        try:
            memory_ids = await self.memory_manager.store_workflow_memory(
                conversation_id=conversation_id,
                user_id=user_id,
                workflow_state=result,
                contact_responses=result.get("contact_responses", {})
            )
            
            self.logger.info(f"Stored {len(memory_ids)} memories from workflow execution")
            
            # Trigger memory consolidation if needed
            await self.memory_manager.trigger_memory_consolidation(conversation_id)
            
        except Exception as e:
            self.logger.error(f"Failed to store workflow memories: {e}")
    
    async def _build_memory_context_prompt(
        self, 
        memory_context: Dict[str, Any], 
        contact: ContactInfo
    ) -> Optional[str]:
        """Build memory context prompt for contact."""
        
        if not memory_context:
            return None
        
        context_parts = []
        
        # Add conversation summary
        if memory_context.get("conversation_summary"):
            summary = memory_context["conversation_summary"]
            context_parts.append(f"Previous conversation summary: {summary['summary']}")
        
        # Add recent short-term memories
        short_term = memory_context.get("short_term_memories", [])
        if short_term:
            recent_context = "; ".join([mem["content"][:100] for mem in short_term[:3]])
            context_parts.append(f"Recent conversation context: {recent_context}")
        
        # Add relevant memories
        relevant = memory_context.get("relevant_memories", [])
        if relevant:
            relevant_context = "; ".join([mem["content"][:80] for mem in relevant[:2]])
            context_parts.append(f"Relevant past discussions: {relevant_context}")
        
        if not context_parts:
            return None
        
        context_prompt = "Context from previous conversations:\n" + "\n".join(context_parts)
        context_prompt += "\n\nUse this context to provide more personalized and relevant responses."
        
        return context_prompt
