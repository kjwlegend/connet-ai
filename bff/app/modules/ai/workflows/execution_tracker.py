"""
Workflow Execution Tracker

Tracks workflow execution performance, metrics, and state for monitoring and analytics.
Integrates with database models to persist execution data.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.modules.ai.workflows.models import (
    WorkflowExecutionModel,
    NodeExecutionModel, 
    ToolExecutionModel,
    TokenUsageModel
)
from app.modules.ai.workflows.state_models import ConversationState
from app.modules.ai.workflows.node_registry import NodeExecutionResult


logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Metrics for workflow execution"""
    
    workflow_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration_ms: Optional[int] = None
    
    # Resource usage
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost_usd: float = 0.0
    
    # Execution stats
    nodes_executed: int = 0
    nodes_successful: int = 0
    nodes_failed: int = 0
    tools_executed: int = 0
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def calculate_success_rate(self) -> float:
        """Calculate node execution success rate"""
        if self.nodes_executed == 0:
            return 0.0
        return self.nodes_successful / self.nodes_executed
    
    def is_complete(self) -> bool:
        """Check if execution is complete"""
        return self.completed_at is not None
    
    def get_duration_seconds(self) -> float:
        """Get execution duration in seconds"""
        if self.total_duration_ms:
            return self.total_duration_ms / 1000.0
        return 0.0


class ExecutionTracker:
    """Tracks workflow execution for monitoring and analytics"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.active_executions: Dict[UUID, ExecutionMetrics] = {}
        self.execution_history: List[ExecutionMetrics] = []
        
    async def start_workflow_execution(
        self,
        conversation_id: UUID,
        user_id: UUID,
        workflow_type: str,
        participant_contacts: List[str],
        input_data: Dict[str, Any]
    ) -> UUID:
        """Start tracking a new workflow execution"""
        
        execution_id = uuid4()
        
        # Create database record
        workflow_execution = WorkflowExecutionModel(
            id=execution_id,
            conversation_id=conversation_id,
            user_id=user_id,
            workflow_type=workflow_type,
            participant_contacts=participant_contacts,
            input_data=input_data,
            status="running",
            started_at=datetime.utcnow()
        )
        
        self.session.add(workflow_execution)
        await self.session.commit()
        
        # Initialize metrics tracking
        metrics = ExecutionMetrics(
            workflow_id=execution_id,
            started_at=datetime.utcnow()
        )
        self.active_executions[execution_id] = metrics
        
        logger.info(f"Started workflow execution tracking: {execution_id}")
        return execution_id
    
    async def complete_workflow_execution(
        self,
        execution_id: UUID,
        success: bool,
        final_response: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> ExecutionMetrics:
        """Complete workflow execution tracking"""
        
        metrics = self.active_executions.get(execution_id)
        if not metrics:
            logger.warning(f"No active execution found for {execution_id}")
            return None
        
        # Update metrics
        metrics.completed_at = datetime.utcnow()
        metrics.total_duration_ms = int(
            (metrics.completed_at - metrics.started_at).total_seconds() * 1000
        )
        
        # Update database record
        stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.id == execution_id
        )
        result = await self.session.execute(stmt)
        workflow_execution = result.scalar_one_or_none()
        
        if workflow_execution:
            workflow_execution.status = "completed" if success else "failed"
            workflow_execution.completed_at = metrics.completed_at
            workflow_execution.total_duration_ms = metrics.total_duration_ms
            workflow_execution.total_tokens = metrics.total_tokens
            workflow_execution.prompt_tokens = metrics.prompt_tokens
            workflow_execution.completion_tokens = metrics.completion_tokens
            workflow_execution.total_cost_usd = metrics.total_cost_usd
            
            if final_response:
                workflow_execution.output_data = {"final_response": final_response}
            
            if error_message:
                workflow_execution.error_data = {"error": error_message}
            
            await self.session.commit()
        
        # Move to history and clean up active tracking
        self.execution_history.append(metrics)
        del self.active_executions[execution_id]
        
        logger.info(f"Completed workflow execution: {execution_id} (success: {success})")
        return metrics
    
    async def track_node_execution(
        self,
        execution_id: UUID,
        node_result: NodeExecutionResult,
        contact_id: Optional[UUID] = None
    ) -> None:
        """Track execution of individual nodes"""
        
        metrics = self.active_executions.get(execution_id)
        if not metrics:
            logger.warning(f"No active execution found for {execution_id}")
            return
        
        # Update metrics
        metrics.nodes_executed += 1
        if node_result.success:
            metrics.nodes_successful += 1
        else:
            metrics.nodes_failed += 1
            if node_result.error_message:
                metrics.errors.append(f"{node_result.node_id}: {node_result.error_message}")
        
        # Update token usage if available
        if node_result.token_usage:
            metrics.total_tokens += node_result.token_usage.get('total_tokens', 0)
            metrics.prompt_tokens += node_result.token_usage.get('prompt_tokens', 0)  
            metrics.completion_tokens += node_result.token_usage.get('completion_tokens', 0)
        
        # Create database record
        node_execution = NodeExecutionModel(
            workflow_execution_id=execution_id,
            node_id=node_result.node_id,
            node_type="ai_processor",  # TODO: Get from node registry
            contact_id=contact_id,
            status="completed" if node_result.success else "failed",
            started_at=datetime.utcnow() - timedelta(milliseconds=node_result.execution_time_ms),
            completed_at=datetime.utcnow(),
            duration_ms=node_result.execution_time_ms,
            input_state={"processed": True},  # TODO: Store actual input state
            output_state=node_result.output_state,
            error_message=node_result.error_message,
            retry_count=node_result.retry_count
        )
        
        if node_result.token_usage:
            node_execution.prompt_tokens = node_result.token_usage.get('prompt_tokens', 0)
            node_execution.completion_tokens = node_result.token_usage.get('completion_tokens', 0)
        
        self.session.add(node_execution)
        await self.session.commit()
    
    async def track_token_usage(
        self,
        execution_id: UUID,
        user_id: UUID,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float = 0.0,
        contact_id: Optional[UUID] = None,
        usage_type: str = "conversation"
    ) -> None:
        """Track detailed token usage"""
        
        # Update execution metrics
        metrics = self.active_executions.get(execution_id)
        if metrics:
            metrics.total_tokens += prompt_tokens + completion_tokens
            metrics.prompt_tokens += prompt_tokens
            metrics.completion_tokens += completion_tokens
            metrics.total_cost_usd += cost_usd
        
        # Create detailed usage record
        token_usage = TokenUsageModel(
            workflow_execution_id=execution_id,
            user_id=user_id,
            contact_id=contact_id,
            model_name=model_name,
            model_provider="openai",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            total_cost_usd=cost_usd,
            usage_type=usage_type
        )
        
        self.session.add(token_usage)
        await self.session.commit()
    
    async def track_tool_execution(
        self,
        execution_id: UUID,
        node_execution_id: UUID,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Optional[Dict[str, Any]] = None,
        success: bool = True,
        duration_ms: int = 0,
        error_message: Optional[str] = None
    ) -> None:
        """Track tool execution within nodes"""
        
        metrics = self.active_executions.get(execution_id)
        if metrics:
            metrics.tools_executed += 1
        
        tool_execution = ToolExecutionModel(
            node_execution_id=node_execution_id,
            workflow_execution_id=execution_id,
            tool_name=tool_name,
            tool_type="builtin",  # TODO: Determine tool type
            status="completed" if success else "failed",
            started_at=datetime.utcnow() - timedelta(milliseconds=duration_ms),
            completed_at=datetime.utcnow(),
            duration_ms=duration_ms,
            tool_input=tool_input,
            tool_output=tool_output,
            error_message=error_message
        )
        
        self.session.add(tool_execution)
        await self.session.commit()
    
    def get_active_executions(self) -> Dict[UUID, ExecutionMetrics]:
        """Get all currently active executions"""
        return self.active_executions.copy()
    
    def get_execution_metrics(self, execution_id: UUID) -> Optional[ExecutionMetrics]:
        """Get metrics for specific execution"""
        return self.active_executions.get(execution_id)
    
    async def get_execution_statistics(
        self,
        user_id: Optional[UUID] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get execution statistics for monitoring dashboard"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query
        stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.started_at >= since_date
        )
        
        if user_id:
            stmt = stmt.where(WorkflowExecutionModel.user_id == user_id)
        
        result = await self.session.execute(stmt)
        executions = result.scalars().all()
        
        # Calculate statistics
        total_executions = len(executions)
        successful_executions = sum(1 for e in executions if e.status == "completed")
        failed_executions = sum(1 for e in executions if e.status == "failed")
        
        avg_duration = 0
        total_tokens = 0
        total_cost = 0.0
        
        if executions:
            durations = [e.total_duration_ms for e in executions if e.total_duration_ms]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            total_tokens = sum(e.total_tokens for e in executions)
            total_cost = sum(e.total_cost_usd for e in executions)
        
        return {
            "period_days": days,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_duration_ms": avg_duration,
            "total_tokens_used": total_tokens,
            "total_cost_usd": total_cost,
            "active_executions": len(self.active_executions)
        }
    
    async def get_workflow_performance(self, workflow_type: str) -> Dict[str, Any]:
        """Get performance metrics for specific workflow type"""
        
        stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.workflow_type == workflow_type
        )
        
        result = await self.session.execute(stmt)
        executions = result.scalars().all()
        
        if not executions:
            return {"workflow_type": workflow_type, "executions": 0}
        
        successful = sum(1 for e in executions if e.status == "completed")
        durations = [e.total_duration_ms for e in executions if e.total_duration_ms]
        
        return {
            "workflow_type": workflow_type,
            "total_executions": len(executions),
            "success_rate": successful / len(executions),
            "average_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0
        }
    
    def cleanup_old_metrics(self, days: int = 30) -> None:
        """Clean up old execution metrics from memory"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        self.execution_history = [
            metrics for metrics in self.execution_history
            if metrics.started_at > cutoff_date
        ]
        
        logger.info(f"Cleaned up execution metrics older than {days} days")
