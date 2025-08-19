"""
Tools Service

This module provides Tools-related business logic.
"""

from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime

from app.infrastructure.database.repositories.tools_repository_impl import (
    ToolRepository,
    WebhookRepository,
    WebhookTriggerRepository
)
from app.infrastructure.database.models.tool_model import (
    ToolModel,
    WebhookModel,
    WebhookTriggerModel,
    ToolType
)
from app.schemas.tools import (
    ToolResponse,
    ToolCreate,
    ToolUpdate,
    WebhookResponse,
    WebhookCreate,
    WebhookUpdate,
    WebhookTriggerResponse,
    ToolExecutionRequest,
    ToolExecutionResponse
)
from app.services.base import BaseRepositoryService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ToolsService(BaseRepositoryService):
    """Tools service for managing tools, webhooks, and executions."""

    def __init__(
        self,
        tool_repository: ToolRepository,
        webhook_repository: WebhookRepository,
        webhook_trigger_repository: WebhookTriggerRepository
    ):
        self.tool_repository = tool_repository
        self.webhook_repository = webhook_repository
        self.webhook_trigger_repository = webhook_trigger_repository

    # Tool Management
    async def create_tool(
        self,
        user_id: UUID,
        tool_data: ToolCreate
    ) -> ToolResponse:
        """Create a new tool."""
        try:
            tool = ToolModel(
                name=tool_data.name,
                display_name=tool_data.display_name,
                description=tool_data.description,
                tool_type=ToolType(tool_data.tool_type),
                version=tool_data.version or "1.0.0",
                configuration=tool_data.configuration or {},
                parameters_schema=tool_data.parameters_schema or {},
                required_permissions=tool_data.required_permissions or [],
                timeout_seconds=tool_data.timeout_seconds or 30,
                rate_limit=tool_data.rate_limit,
                resource_limits=tool_data.resource_limits or {},
                security_level=tool_data.security_level or "medium",
                allowed_domains=tool_data.allowed_domains or [],
                blocked_patterns=tool_data.blocked_patterns or [],
                status=tool_data.status or "active",
                category=tool_data.category or "general",
                tags=tool_data.tags or [],
                created_by=user_id
            )
            
            created_tool = await self.tool_repository.create_tool(tool)
            return self._tool_to_response(created_tool)
        except Exception as e:
            logger.error(f"Error creating tool: {e}")
            raise

    async def get_tool(self, tool_id: UUID) -> Optional[ToolResponse]:
        """Get tool by ID."""
        try:
            tool = await self.tool_repository.get_by_id(tool_id)
            if tool:
                return self._tool_to_response(tool)
            return None
        except Exception as e:
            logger.error(f"Error getting tool: {e}")
            raise

    async def get_tool_by_name(self, name: str) -> Optional[ToolResponse]:
        """Get tool by name."""
        try:
            tool = await self.tool_repository.get_by_name(name)
            if tool:
                return self._tool_to_response(tool)
            return None
        except Exception as e:
            logger.error(f"Error getting tool by name: {e}")
            raise

    async def get_user_tools(
        self,
        user_id: UUID,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ToolResponse]:
        """Get tools created by user."""
        try:
            tools = await self.tool_repository.get_by_creator(user_id)
            
            # Apply filters
            if tool_type:
                tools = [tool for tool in tools if tool.tool_type == tool_type]
            
            if category:
                tools = [tool for tool in tools if tool.category == category]
            
            if status:
                tools = [tool for tool in tools if tool.status == status]
            
            return [self._tool_to_response(tool) for tool in tools]
        except Exception as e:
            logger.error(f"Error getting user tools: {e}")
            raise

    async def search_tools(
        self,
        query: str,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        security_level: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ToolResponse], int]:
        """Search tools with filters."""
        try:
            tools, total_count = await self.tool_repository.search_tools(
                query=query,
                tool_type=tool_type,
                category=category,
                tags=tags,
                security_level=security_level,
                status=status,
                offset=skip,
                limit=limit
            )
            
            responses = [self._tool_to_response(tool) for tool in tools]
            return responses, total_count
        except Exception as e:
            logger.error(f"Error searching tools: {e}")
            raise

    async def get_popular_tools(self, limit: int = 10) -> List[ToolResponse]:
        """Get most popular tools."""
        try:
            tools = await self.tool_repository.get_popular_tools(limit)
            return [self._tool_to_response(tool) for tool in tools]
        except Exception as e:
            logger.error(f"Error getting popular tools: {e}")
            raise

    async def get_recommended_tools(
        self,
        category: str,
        limit: int = 5
    ) -> List[ToolResponse]:
        """Get recommended tools by category."""
        try:
            tools = await self.tool_repository.get_recommended_tools(category, limit)
            return [self._tool_to_response(tool) for tool in tools]
        except Exception as e:
            logger.error(f"Error getting recommended tools: {e}")
            raise

    async def update_tool(
        self,
        tool_id: UUID,
        user_id: UUID,
        tool_data: ToolUpdate
    ) -> Optional[ToolResponse]:
        """Update tool."""
        try:
            tool = await self.tool_repository.get_by_id(tool_id)
            if not tool or tool.created_by != user_id:
                return None
            
            # Update fields from tool_data
            for field, value in tool_data.model_dump(exclude_unset=True).items():
                setattr(tool, field, value)
            
            updated_tool = await self.tool_repository.update_tool(tool)
            if updated_tool:
                return self._tool_to_response(updated_tool)
            return None
        except Exception as e:
            logger.error(f"Error updating tool: {e}")
            raise

    async def delete_tool(
        self,
        tool_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete tool."""
        try:
            tool = await self.tool_repository.get_by_id(tool_id)
            if not tool or tool.created_by != user_id:
                return False
            
            return await self.tool_repository.delete_tool(tool_id)
        except Exception as e:
            logger.error(f"Error deleting tool: {e}")
            raise

    # Tool Execution
    async def execute_tool(
        self,
        tool_id: UUID,
        user_id: UUID,
        execution_request: ToolExecutionRequest
    ) -> ToolExecutionResponse:
        """Execute a tool."""
        try:
            tool = await self.tool_repository.get_by_id(tool_id)
            if not tool or tool.status != "active":
                raise ValueError("Tool not found or inactive")
            
            # Increment usage count
            await self.tool_repository.increment_usage_count(tool_id)
            
            # This is a placeholder - actual execution logic would depend on tool type
            execution_start = datetime.now(datetime.timezone.utc)
            
            # Simulate execution based on tool type
            success = True
            result = {"status": "completed", "message": f"Tool {tool.name} executed successfully"}
            error_message = None
            
            execution_time = (datetime.now(datetime.timezone.utc) - execution_start).total_seconds()
            
            # Update tool statistics
            await self.tool_repository.update_tool_stats(
                tool_id=tool_id,
                success=success,
                execution_time=execution_time
            )
            
            return ToolExecutionResponse(
                tool_id=tool_id,
                execution_id=f"exec_{tool_id}_{user_id}_{int(execution_start.timestamp())}",
                user_id=user_id,
                parameters=execution_request.parameters,
                result=result,
                success=success,
                error_message=error_message,
                execution_time=execution_time,
                started_at=execution_start,
                completed_at=datetime.now(datetime.timezone.utc)
            )
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            raise

    # Webhook Management
    async def create_webhook(
        self,
        user_id: UUID,
        webhook_data: WebhookCreate
    ) -> WebhookResponse:
        """Create a new webhook."""
        try:
            webhook = WebhookModel(
                name=webhook_data.name,
                url=webhook_data.url,
                method=webhook_data.method or "POST",
                headers=webhook_data.headers or {},
                secret=webhook_data.secret,
                timeout_seconds=webhook_data.timeout_seconds or 30,
                retry_enabled=webhook_data.retry_enabled or True,
                max_retries=webhook_data.max_retries or 3,
                retry_delay_seconds=webhook_data.retry_delay_seconds or 60,
                event_types=webhook_data.event_types or [],
                event_filters=webhook_data.event_filters or {},
                transform_template=webhook_data.transform_template,
                status=webhook_data.status or "active",
                created_by=user_id
            )
            
            created_webhook = await self.webhook_repository.create(webhook)
            return self._webhook_to_response(created_webhook)
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            raise

    async def get_user_webhooks(self, user_id: UUID) -> List[WebhookResponse]:
        """Get webhooks created by user."""
        try:
            webhooks = await self.webhook_repository.get_by_creator(user_id)
            return [self._webhook_to_response(webhook) for webhook in webhooks]
        except Exception as e:
            logger.error(f"Error getting user webhooks: {e}")
            raise

    async def get_webhooks_by_event_type(self, event_type: str) -> List[WebhookResponse]:
        """Get webhooks that handle specific event type."""
        try:
            webhooks = await self.webhook_repository.get_webhooks_by_event_type(event_type)
            return [self._webhook_to_response(webhook) for webhook in webhooks]
        except Exception as e:
            logger.error(f"Error getting webhooks by event type: {e}")
            raise

    async def trigger_webhook(
        self,
        webhook_id: UUID,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> WebhookTriggerResponse:
        """Trigger a webhook."""
        try:
            webhook = await self.webhook_repository.get_by_id(webhook_id)
            if not webhook or webhook.status != "active":
                raise ValueError("Webhook not found or inactive")
            
            trigger = WebhookTriggerModel(
                webhook_id=webhook_id,
                trigger_id=f"trigger_{webhook_id}_{int(datetime.now(datetime.timezone.utc).timestamp())}",
                event_type=event_type,
                event_data=event_data,
                payload=event_data,  # This would be transformed based on webhook template
                status="pending"
            )
            
            created_trigger = await self.webhook_trigger_repository.create_trigger(trigger)
            
            # Update webhook stats (simplified)
            await self.webhook_repository.update_webhook_stats(webhook_id, True)
            
            return self._webhook_trigger_to_response(created_trigger)
        except Exception as e:
            logger.error(f"Error triggering webhook: {e}")
            raise

    async def get_webhook_triggers(
        self,
        webhook_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> List[WebhookTriggerResponse]:
        """Get recent triggers for a webhook."""
        try:
            # Verify ownership
            webhook = await self.webhook_repository.get_by_id(webhook_id)
            if not webhook or webhook.created_by != user_id:
                return []
            
            triggers = await self.webhook_trigger_repository.get_by_webhook(webhook_id, limit)
            return [self._webhook_trigger_to_response(trigger) for trigger in triggers]
        except Exception as e:
            logger.error(f"Error getting webhook triggers: {e}")
            raise

    def _tool_to_response(self, tool: ToolModel) -> ToolResponse:
        """Convert tool model to response."""
        return ToolResponse(
            id=tool.id,
            name=tool.name,
            display_name=tool.display_name,
            description=tool.description,
            tool_type=tool.tool_type,
            version=tool.version,
            configuration=tool.configuration,
            parameters_schema=tool.parameters_schema,
            required_permissions=tool.required_permissions,
            timeout_seconds=tool.timeout_seconds,
            rate_limit=tool.rate_limit,
            resource_limits=tool.resource_limits,
            security_level=tool.security_level,
            allowed_domains=tool.allowed_domains,
            blocked_patterns=tool.blocked_patterns,
            status=tool.status,
            category=tool.category,
            tags=tool.tags,
            created_by=tool.created_by,
            created_at=tool.created_at,
            updated_at=tool.updated_at,
            usage_count=tool.usage_count,
            success_rate=tool.success_rate,
            avg_execution_time=tool.avg_execution_time
        )

    def _webhook_to_response(self, webhook: WebhookModel) -> WebhookResponse:
        """Convert webhook model to response."""
        return WebhookResponse(
            id=webhook.id,
            name=webhook.name,
            url=webhook.url,
            method=webhook.method,
            headers=webhook.headers,
            secret=webhook.secret,
            timeout_seconds=webhook.timeout_seconds,
            retry_enabled=webhook.retry_enabled,
            max_retries=webhook.max_retries,
            retry_delay_seconds=webhook.retry_delay_seconds,
            event_types=webhook.event_types,
            event_filters=webhook.event_filters,
            transform_template=webhook.transform_template,
            status=webhook.status,
            created_by=webhook.created_by,
            created_at=webhook.created_at,
            updated_at=webhook.updated_at,
            total_triggers=webhook.total_triggers,
            successful_triggers=webhook.successful_triggers,
            failed_triggers=webhook.failed_triggers,
            last_triggered_at=webhook.last_triggered_at
        )

    def _webhook_trigger_to_response(self, trigger: WebhookTriggerModel) -> WebhookTriggerResponse:
        """Convert webhook trigger model to response."""
        return WebhookTriggerResponse(
            id=trigger.id,
            webhook_id=trigger.webhook_id,
            trigger_id=trigger.trigger_id,
            event_type=trigger.event_type,
            event_data=trigger.event_data,
            payload=trigger.payload,
            status=trigger.status,
            success=trigger.success,
            http_status_code=trigger.http_status_code,
            response_body=trigger.response_body,
            error_message=trigger.error_message,
            retry_count=trigger.retry_count,
            max_retries=trigger.max_retries,
            created_at=trigger.created_at,
            sent_at=trigger.sent_at,
            completed_at=trigger.completed_at
        )