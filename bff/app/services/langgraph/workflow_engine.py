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
from app.services.langgraph.state_models import (
    ConversationState, 
    ContactInfo, 
    ContactResponse,
    WorkflowType,
    MessageState,
    WorkflowConfig
)
from app.services.langgraph.contact_manager import ContactInstanceManager
from app.services.langgraph.mention_parser import MentionParser
from app.services.base import BaseService


class WorkflowEngine(BaseService):
    """LangGraph-based workflow engine for conversation processing"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.settings = get_settings()
        self.contact_manager = ContactInstanceManager(session)
        self.mention_parser = MentionParser()
        
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
            conversation_memory=None,  # TODO: Implement memory retrieval
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
        """Build parallel discussion workflow"""
        
        workflow = StateGraph(ConversationState)
        
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
        """Create a contact processing node"""
        
        async def contact_processor(state: ConversationState) -> ConversationState:
            try:
                # Build enhanced prompt
                system_prompt = contact["system_prompt"]
                user_message = state["current_message"]
                
                # Call LLM
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
                
                response = await self.llm.ainvoke(messages)
                
                # Create contact response
                contact_response = ContactResponse(
                    contact_id=contact["contact_id"],
                    contact_name=contact["display_name"],
                    agent_id=contact["agent_id"],
                    response=response.content,
                    tool_calls=None,  # TODO: Implement tool calls
                    tokens_used=response.response_metadata.get("token_usage", {}).get("total_tokens"),
                    timestamp=datetime.utcnow().isoformat(),
                    status="success",
                    error=None
                )
                
                # Update state
                state["contact_responses"][contact["contact_id"]] = contact_response
                state["execution_path"].append(f"contact_{contact['contact_id']}")
                state["current_step"] = f"processed_contact_{contact['contact_id']}"
                
                return state
                
            except Exception as e:
                # Handle error
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