"""AI Tool service for managing tools and their executions."""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from app.infrastructure.database.repositories.ai_tool_repository_impl import (
    AIToolRepositoryImpl,
    AIToolExecutionRepositoryImpl
)
from app.schemas.ai import (
    ToolCreate,
    ToolResponse,
    ToolExecutionRequest,
    ToolExecutionResponse,
    PaginationParams
)
from app.services.base import BaseService


class AIToolService(BaseService):
    """AI Tool service for managing tools"""
    
    def __init__(self, session):
        super().__init__(session)
        self.tool_repo = AIToolRepositoryImpl(session)
        self.execution_repo = AIToolExecutionRepositoryImpl(session)
        
        # Built-in tool implementations
        self.tool_implementations = {
            'web_search': WebSearchToolImpl(),
            'api_call': APICallToolImpl(),
            'code_executor': CodeExecutorToolImpl(),
            'file_processor': FileProcessorToolImpl(),
            'data_analyzer': DataAnalyzerToolImpl()
        }
    
    async def create_tool(self, tool_data: ToolCreate, user_id: UUID) -> ToolResponse:
        """Create a new tool"""
        
        # Check if tool name already exists
        existing = await self.tool_repo.get_tool_by_name(tool_data.name)
        if existing:
            raise ValueError(f"Tool with name '{tool_data.name}' already exists")
        
        tool = await self.tool_repo.create_tool(tool_data, user_id)
        return ToolResponse.model_validate(tool)
    
    async def get_tool(self, tool_id: UUID) -> Optional[ToolResponse]:
        """Get tool by ID"""
        
        tool = await self.tool_repo.get_tool_by_id(tool_id)
        if not tool:
            return None
        
        return ToolResponse.model_validate(tool)
    
    async def get_tool_by_name(self, name: str) -> Optional[ToolResponse]:
        """Get tool by name"""
        
        tool = await self.tool_repo.get_tool_by_name(name)
        if not tool:
            return None
        
        return ToolResponse.model_validate(tool)
    
    async def list_tools(
        self,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[UUID] = None,
        pagination: Optional[PaginationParams] = None
    ) -> tuple[List[ToolResponse], int]:
        """List tools with filtering"""
        
        tools, total = await self.tool_repo.list_tools(
            tool_type=tool_type,
            category=category,
            status=status,
            user_id=user_id,
            pagination=pagination
        )
        
        tool_responses = [ToolResponse.model_validate(tool) for tool in tools]
        return tool_responses, total
    
    async def execute_tool(
        self,
        request: ToolExecutionRequest,
        conversation_id: UUID,
        user_id: UUID,
        agent_id: Optional[UUID] = None
    ) -> ToolExecutionResponse:
        """Execute a tool"""
        
        # Get tool definition
        tool = await self.tool_repo.get_tool_by_name(request.tool_name)
        if not tool:
            return ToolExecutionResponse(
                execution_id=str(uuid4()),
                success=False,
                result=None,
                error_message=f"Tool '{request.tool_name}' not found",
                execution_time=0.0
            )
        
        # Generate execution ID
        execution_id = str(uuid4())
        
        # Create execution record
        execution_data = {
            'execution_id': execution_id,
            'tool_id': tool.id,
            'agent_id': agent_id,
            'conversation_id': conversation_id,
            'user_id': user_id,
            'parameters': request.parameters,
            'status': 'running',
            'success': False,
            'started_at': datetime.utcnow()
        }
        
        await self.execution_repo.create_execution(execution_data)
        
        try:
            # Validate parameters
            validation_errors = self._validate_tool_parameters(tool, request.parameters)
            if validation_errors:
                await self.execution_repo.update_execution_result(
                    execution_id,
                    result=None,
                    success=False,
                    error_message=f"Parameter validation failed: {', '.join(validation_errors)}"
                )
                return ToolExecutionResponse(
                    execution_id=execution_id,
                    success=False,
                    result=None,
                    error_message=f"Parameter validation failed: {', '.join(validation_errors)}",
                    execution_time=0.0
                )
            
            # Execute tool
            start_time = time.time()
            result = await self._execute_tool_implementation(tool, request.parameters, request.context)
            execution_time = time.time() - start_time
            
            # Update execution record
            await self.execution_repo.update_execution_result(
                execution_id,
                result=result,
                success=True
            )
            
            # Update tool statistics
            await self.tool_repo.update_tool_usage_stats(tool.id, execution_time, True)
            
            return ToolExecutionResponse(
                execution_id=execution_id,
                success=True,
                result=result,
                error_message=None,
                execution_time=execution_time,
                metadata={'tool_id': str(tool.id), 'tool_type': tool.tool_type}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0.0
            
            # Update execution record with error
            await self.execution_repo.update_execution_result(
                execution_id,
                result=None,
                success=False,
                error_message=str(e)
            )
            
            # Update tool statistics
            await self.tool_repo.update_tool_usage_stats(tool.id, execution_time, False)
            
            return ToolExecutionResponse(
                execution_id=execution_id,
                success=False,
                result=None,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        
        execution = await self.execution_repo.get_execution_by_id(execution_id)
        if not execution:
            return None
        
        return {
            'execution_id': execution.execution_id,
            'status': execution.status,
            'success': execution.success,
            'result': execution.result,
            'error_message': execution.error_message,
            'execution_time': execution.execution_time,
            'started_at': execution.started_at,
            'completed_at': execution.completed_at
        }
    
    async def get_conversation_executions(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get tool executions for a conversation"""
        
        executions = await self.execution_repo.get_executions_by_conversation(conversation_id, limit)
        
        return [
            {
                'execution_id': execution.execution_id,
                'tool_id': execution.tool_id,
                'parameters': execution.parameters,
                'result': execution.result,
                'success': execution.success,
                'execution_time': execution.execution_time,
                'started_at': execution.started_at
            }
            for execution in executions
        ]
    
    async def get_execution_statistics(
        self,
        tool_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get execution statistics"""
        
        return await self.execution_repo.get_execution_stats(tool_id, user_id, days)
    
    async def delete_tool(self, tool_id: UUID, user_id: UUID) -> bool:
        """Delete a tool"""
        
        return await self.tool_repo.delete_tool(tool_id, user_id)
    
    def _validate_tool_parameters(self, tool, parameters: Dict[str, Any]) -> List[str]:
        """Validate tool parameters against schema"""
        
        errors = []
        schema = tool.parameters_schema or []
        
        # Check required parameters
        for param_def in schema:
            param_name = param_def.get('name')
            if param_def.get('required', True) and param_name not in parameters:
                errors.append(f"Required parameter '{param_name}' is missing")
        
        # Validate parameter types and values
        for param_name, param_value in parameters.items():
            param_def = next((p for p in schema if p.get('name') == param_name), None)
            if param_def:
                # Type validation
                expected_type = param_def.get('type')
                if not self._validate_parameter_type(param_value, expected_type):
                    errors.append(f"Parameter '{param_name}' has invalid type")
                
                # Enum validation
                enum_values = param_def.get('enum_values')
                if enum_values and param_value not in enum_values:
                    errors.append(f"Parameter '{param_name}' must be one of: {enum_values}")
        
        return errors
    
    def _validate_parameter_type(self, value: Any, expected_type: str) -> bool:
        """Validate parameter type"""
        
        type_validators = {
            'string': lambda v: isinstance(v, str),
            'integer': lambda v: isinstance(v, int),
            'number': lambda v: isinstance(v, (int, float)),
            'boolean': lambda v: isinstance(v, bool),
            'array': lambda v: isinstance(v, list),
            'object': lambda v: isinstance(v, dict)
        }
        
        validator = type_validators.get(expected_type)
        return validator(value) if validator else True
    
    async def _execute_tool_implementation(
        self,
        tool,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tool implementation"""
        
        tool_impl = self.tool_implementations.get(tool.name)
        if tool_impl:
            return await tool_impl.execute(parameters, context)
        
        # For custom tools, use the configuration to determine execution
        if tool.tool_type == 'api_call':
            return await self._execute_api_call_tool(tool, parameters)
        elif tool.tool_type == 'webhook':
            return await self._execute_webhook_tool(tool, parameters)
        else:
            raise NotImplementedError(f"Tool type '{tool.tool_type}' not implemented")
    
    async def _execute_api_call_tool(self, tool, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call tool"""
        
        import aiohttp
        
        config = tool.configuration
        url = parameters.get('url') or config.get('base_url')
        method = parameters.get('method', 'GET')
        headers = parameters.get('headers', {})
        data = parameters.get('data', {})
        
        # Merge with tool configuration
        if 'default_headers' in config:
            headers = {**config['default_headers'], **headers}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=tool.timeout_seconds)) as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                result = {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'data': await response.text()
                }
                
                # Try to parse JSON
                try:
                    result['data'] = await response.json()
                except:
                    pass
                
                return result
    
    async def _execute_webhook_tool(self, tool, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute webhook tool"""
        
        # This would trigger a webhook call
        # For now, return a placeholder
        return {
            'webhook_triggered': True,
            'tool_id': str(tool.id),
            'parameters': parameters,
            'timestamp': datetime.utcnow().isoformat()
        }


# Tool implementation classes (simplified versions)

class WebSearchToolImpl:
    """Web search tool implementation"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search"""
        
        query = parameters.get('query')
        num_results = parameters.get('num_results', 10)
        
        # TODO: Integrate with actual search API (Google, Bing, etc.)
        # For now, return mock results
        return {
            'query': query,
            'results': [
                {
                    'title': f'Result {i+1} for: {query}',
                    'url': f'https://example.com/result-{i+1}',
                    'snippet': f'This is a sample snippet for result {i+1} about {query}',
                    'relevance_score': 1.0 - (i * 0.1)
                }
                for i in range(min(num_results, 10))
            ],
            'total_results': min(num_results, 10)
        }


class APICallToolImpl:
    """API call tool implementation"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call"""
        
        import aiohttp
        
        url = parameters['url']
        method = parameters.get('method', 'GET')
        headers = parameters.get('headers', {})
        data = parameters.get('data')
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                return {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'data': await response.text()
                }


class CodeExecutorToolImpl:
    """Code executor tool implementation"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code in sandbox"""
        
        code = parameters['code']
        language = parameters['language']
        
        # TODO: Implement actual code execution in sandbox
        # For now, return mock execution result
        return {
            'output': f'Mock execution of {language} code:\n{code}',
            'error_output': '',
            'exit_code': 0,
            'execution_time': 0.1
        }


class FileProcessorToolImpl:
    """File processor tool implementation"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process file"""
        
        file_path = parameters['file_path']
        operation = parameters.get('operation', 'read')
        
        # TODO: Implement actual file processing
        # For now, return mock result
        return {
            'file_path': file_path,
            'operation': operation,
            'result': f'Mock {operation} operation on {file_path}',
            'file_size': 1024
        }


class DataAnalyzerToolImpl:
    """Data analyzer tool implementation"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data"""
        
        data = parameters['data']
        analysis_type = parameters.get('analysis_type', 'summary')
        
        # TODO: Implement actual data analysis
        # For now, return mock analysis
        return {
            'analysis_type': analysis_type,
            'data_size': len(str(data)),
            'summary': f'Mock {analysis_type} analysis completed',
            'insights': ['Insight 1', 'Insight 2', 'Insight 3']
        }