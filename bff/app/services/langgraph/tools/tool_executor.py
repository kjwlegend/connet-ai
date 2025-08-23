"""
Tool Executor

Executes tools within LangGraph workflows with proper error handling,
timeout management, and result tracking.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union
from uuid import UUID
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import TimeoutError

from app.services.langgraph.tools.tool_registry import ToolRegistry, get_tool_registry
from app.services.langgraph.execution_tracker import ExecutionTracker


logger = logging.getLogger(__name__)


class ToolExecutionStatus(str, Enum):
    """Tool execution status"""
    PENDING = "pending"
    RUNNING = "running"  
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ToolExecutionRequest:
    """Request for tool execution"""
    
    tool_name: str
    parameters: Dict[str, Any]
    execution_id: UUID
    node_execution_id: UUID
    timeout_seconds: int = 30
    retry_count: int = 0
    context: Optional[Dict[str, Any]] = None


@dataclass 
class ToolExecutionResult:
    """Result of tool execution"""
    
    tool_name: str
    status: ToolExecutionStatus
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    retry_count: int = 0
    metadata: Dict[str, Any] = None
    
    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.status == ToolExecutionStatus.COMPLETED and self.error_message is None
    
    def get_result_json(self) -> Optional[str]:
        """Get result as JSON string"""
        if self.result is None:
            return None
        try:
            return json.dumps(self.result, default=str)
        except Exception:
            return str(self.result)


class ToolExecutor:
    """Executes tools within workflows"""
    
    def __init__(self, execution_tracker: Optional[ExecutionTracker] = None):
        self.tool_registry = get_tool_registry()
        self.execution_tracker = execution_tracker
        self.active_executions: Dict[str, asyncio.Task] = {}
        
    async def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Execute a single tool"""
        
        start_time = time.time()
        execution_key = f"{request.execution_id}_{request.tool_name}_{int(start_time)}"
        
        try:
            # Get tool from registry
            tool_def = self.tool_registry.get_tool(request.tool_name)
            if not tool_def:
                return ToolExecutionResult(
                    tool_name=request.tool_name,
                    status=ToolExecutionStatus.FAILED,
                    error_message=f"Tool '{request.tool_name}' not found in registry"
                )
            
            # Validate parameters
            validation_result = self.tool_registry.validate_tool_parameters(
                request.tool_name, request.parameters
            )
            if not validation_result["valid"]:
                return ToolExecutionResult(
                    tool_name=request.tool_name,
                    status=ToolExecutionStatus.FAILED,
                    error_message=f"Invalid parameters: {validation_result['errors']}"
                )
            
            # Execute with timeout
            task = asyncio.create_task(
                self._execute_with_context(tool_def.handler, request.parameters, request.context)
            )
            self.active_executions[execution_key] = task
            
            try:
                result = await asyncio.wait_for(task, timeout=request.timeout_seconds)
                
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                # Track execution if tracker available
                if self.execution_tracker:
                    await self.execution_tracker.track_tool_execution(
                        execution_id=request.execution_id,
                        node_execution_id=request.node_execution_id,
                        tool_name=request.tool_name,
                        tool_input=request.parameters,
                        tool_output={"result": result},
                        success=True,
                        duration_ms=execution_time_ms
                    )
                
                return ToolExecutionResult(
                    tool_name=request.tool_name,
                    status=ToolExecutionStatus.COMPLETED,
                    result=result,
                    execution_time_ms=execution_time_ms,
                    retry_count=request.retry_count,
                    metadata={
                        "tool_type": tool_def.tool_type,
                        "version": tool_def.version
                    }
                )
                
            except asyncio.TimeoutError:
                task.cancel()
                
                if self.execution_tracker:
                    await self.execution_tracker.track_tool_execution(
                        execution_id=request.execution_id,
                        node_execution_id=request.node_execution_id,
                        tool_name=request.tool_name,
                        tool_input=request.parameters,
                        success=False,
                        duration_ms=request.timeout_seconds * 1000,
                        error_message="Execution timeout"
                    )
                
                return ToolExecutionResult(
                    tool_name=request.tool_name,
                    status=ToolExecutionStatus.TIMEOUT,
                    error_message=f"Tool execution timed out after {request.timeout_seconds}s",
                    execution_time_ms=request.timeout_seconds * 1000,
                    retry_count=request.retry_count
                )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_message = str(e)
            
            logger.error(f"Tool execution failed: {request.tool_name} - {error_message}")
            
            if self.execution_tracker:
                await self.execution_tracker.track_tool_execution(
                    execution_id=request.execution_id,
                    node_execution_id=request.node_execution_id,
                    tool_name=request.tool_name,
                    tool_input=request.parameters,
                    success=False,
                    duration_ms=execution_time_ms,
                    error_message=error_message
                )
            
            return ToolExecutionResult(
                tool_name=request.tool_name,
                status=ToolExecutionStatus.FAILED,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                retry_count=request.retry_count
            )
            
        finally:
            # Clean up active execution tracking
            if execution_key in self.active_executions:
                del self.active_executions[execution_key]
    
    async def execute_tools_parallel(
        self, 
        requests: List[ToolExecutionRequest]
    ) -> List[ToolExecutionResult]:
        """Execute multiple tools in parallel"""
        
        if not requests:
            return []
        
        logger.info(f"Executing {len(requests)} tools in parallel")
        
        # Create tasks for all tool executions
        tasks = [self.execute_tool(request) for request in requests]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ToolExecutionResult(
                    tool_name=requests[i].tool_name,
                    status=ToolExecutionStatus.FAILED,
                    error_message=f"Execution exception: {str(result)}",
                    retry_count=requests[i].retry_count
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def execute_tools_sequential(
        self,
        requests: List[ToolExecutionRequest],
        stop_on_failure: bool = False
    ) -> List[ToolExecutionResult]:
        """Execute tools sequentially with optional failure handling"""
        
        results = []
        
        for request in requests:
            result = await self.execute_tool(request)
            results.append(result)
            
            # Stop on failure if requested
            if stop_on_failure and not result.is_successful():
                logger.warning(f"Sequential execution stopped due to failure: {result.error_message}")
                break
        
        return results
    
    async def retry_tool_execution(
        self,
        request: ToolExecutionRequest,
        max_retries: int = 3,
        backoff_seconds: float = 1.0
    ) -> ToolExecutionResult:
        """Execute tool with retry logic"""
        
        last_result = None
        
        for attempt in range(max_retries + 1):
            retry_request = ToolExecutionRequest(
                tool_name=request.tool_name,
                parameters=request.parameters,
                execution_id=request.execution_id,
                node_execution_id=request.node_execution_id,
                timeout_seconds=request.timeout_seconds,
                retry_count=attempt,
                context=request.context
            )
            
            result = await self.execute_tool(retry_request)
            
            if result.is_successful():
                return result
            
            last_result = result
            
            # Don't wait after the last attempt
            if attempt < max_retries:
                wait_time = backoff_seconds * (2 ** attempt)  # Exponential backoff
                logger.info(f"Tool execution attempt {attempt + 1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Tool execution failed after {max_retries + 1} attempts: {request.tool_name}")
        return last_result
    
    async def cancel_tool_execution(self, execution_id: UUID, tool_name: str) -> bool:
        """Cancel a running tool execution"""
        
        # Find matching active executions
        to_cancel = []
        for key, task in self.active_executions.items():
            if str(execution_id) in key and tool_name in key:
                to_cancel.append(key)
        
        # Cancel found executions
        cancelled_count = 0
        for key in to_cancel:
            task = self.active_executions.get(key)
            if task and not task.done():
                task.cancel()
                cancelled_count += 1
                del self.active_executions[key]
        
        logger.info(f"Cancelled {cancelled_count} tool executions for {tool_name}")
        return cancelled_count > 0
    
    async def get_execution_status(self, execution_id: UUID) -> Dict[str, Any]:
        """Get status of all tool executions for a workflow"""
        
        active_tools = []
        for key, task in self.active_executions.items():
            if str(execution_id) in key:
                tool_name = key.split('_')[1] if len(key.split('_')) > 1 else "unknown"
                active_tools.append({
                    "tool_name": tool_name,
                    "status": "running" if not task.done() else "completed",
                    "cancelled": task.cancelled() if task.done() else False
                })
        
        return {
            "execution_id": str(execution_id),
            "active_tools": len(active_tools),
            "tools": active_tools
        }
    
    async def _execute_with_context(
        self,
        handler: Callable,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Any:
        """Execute tool handler with context"""
        
        if context:
            # If handler supports context, pass it
            try:
                if asyncio.iscoroutinefunction(handler):
                    return await handler(parameters, context=context)
                else:
                    return handler(parameters, context=context)
            except TypeError:
                # Handler doesn't support context, call without it
                pass
        
        # Execute without context
        if asyncio.iscoroutinefunction(handler):
            return await handler(parameters)
        else:
            return handler(parameters)
    
    def get_active_executions_count(self) -> int:
        """Get count of currently active tool executions"""
        return len(self.active_executions)
    
    def cleanup_completed_executions(self) -> int:
        """Clean up completed/cancelled executions from tracking"""
        
        completed_keys = []
        for key, task in self.active_executions.items():
            if task.done():
                completed_keys.append(key)
        
        for key in completed_keys:
            del self.active_executions[key]
        
        return len(completed_keys)