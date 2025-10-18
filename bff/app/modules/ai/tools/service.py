"""Business logic for AI tools, webhooks, and executions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.modules.ai.tools.models import (
    ToolModel,
    ToolType,
    WebhookModel,
    WebhookTriggerModel,
)
from app.modules.ai.tools.repository import (
    ToolRepositoryProtocol,
    WebhookRepositoryProtocol,
    WebhookTriggerRepositoryProtocol,
)
from app.modules.ai.tools.schemas import (
    ToolCreate,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolResponse,
    ToolUpdate,
    WebhookCreate,
    WebhookResponse,
    WebhookTriggerResponse,
    WebhookUpdate,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ToolsService:
    """Coordinates tool CRUD, execution tracking, and webhook lifecycle."""

    def __init__(
        self,
        *,
        tool_repository: ToolRepositoryProtocol,
        webhook_repository: WebhookRepositoryProtocol,
        webhook_trigger_repository: WebhookTriggerRepositoryProtocol,
    ) -> None:
        self.tool_repository = tool_repository
        self.webhook_repository = webhook_repository
        self.webhook_trigger_repository = webhook_trigger_repository

    # ------------------------------------------------------------------
    # Tool management
    async def create_tool(self, user_id: UUID, payload: ToolCreate) -> ToolResponse:
        tool = ToolModel(
            name=payload.name,
            display_name=payload.display_name,
            description=payload.description,
            tool_type=ToolType(payload.tool_type),
            version=payload.version or "1.0.0",
            configuration=payload.configuration or {},
            parameters_schema=payload.parameters_schema or {},
            required_permissions=payload.required_permissions or [],
            timeout_seconds=payload.timeout_seconds or 30,
            rate_limit=payload.rate_limit,
            resource_limits=payload.resource_limits or {},
            security_level=payload.security_level or "medium",
            allowed_domains=payload.allowed_domains or [],
            blocked_patterns=payload.blocked_patterns or [],
            status=payload.status or "active",
            category=payload.category or "general",
            tags=payload.tags or [],
            created_by=user_id,
        )
        created = await self.tool_repository.create_tool(tool)
        return self._tool_to_response(created)

    async def get_tool(self, tool_id: UUID) -> Optional[ToolResponse]:
        tool = await self.tool_repository.get_by_id(tool_id)
        return self._tool_to_response(tool) if tool else None

    async def get_tool_by_name(self, name: str) -> Optional[ToolResponse]:
        tool = await self.tool_repository.get_by_name(name)
        return self._tool_to_response(tool) if tool else None

    async def get_user_tools(
        self,
        user_id: UUID,
        *,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[ToolResponse]:
        tools = await self.tool_repository.get_by_creator(user_id)
        if tool_type:
            tools = [tool for tool in tools if str(tool.tool_type) == tool_type]
        if category:
            tools = [tool for tool in tools if tool.category == category]
        if status:
            tools = [tool for tool in tools if tool.status == status]
        return [self._tool_to_response(tool) for tool in tools]

    async def search_tools(
        self,
        *,
        query: str,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        security_level: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[ToolResponse], int]:
        tools, total = await self.tool_repository.search_tools(
            query=query,
            tool_type=tool_type,
            category=category,
            tags=tags,
            security_level=security_level,
            status=status,
            offset=skip,
            limit=limit,
        )
        return [self._tool_to_response(tool) for tool in tools], total

    async def get_popular_tools(self, limit: int = 10) -> List[ToolResponse]:
        tools = await self.tool_repository.get_popular_tools(limit)
        return [self._tool_to_response(tool) for tool in tools]

    async def get_recommended_tools(
        self, category: str, limit: int = 5
    ) -> List[ToolResponse]:
        tools = await self.tool_repository.get_recommended_tools(category, limit)
        return [self._tool_to_response(tool) for tool in tools]

    async def update_tool(
        self, tool_id: UUID, user_id: UUID, payload: ToolUpdate
    ) -> Optional[ToolResponse]:
        tool = await self.tool_repository.get_by_id(tool_id)
        if not tool or tool.created_by != user_id:
            return None

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(tool, field, value)

        updated = await self.tool_repository.update_tool(tool)
        return self._tool_to_response(updated) if updated else None

    async def delete_tool(self, tool_id: UUID, user_id: UUID) -> bool:
        tool = await self.tool_repository.get_by_id(tool_id)
        if not tool or tool.created_by != user_id:
            return False
        return await self.tool_repository.delete_tool(tool_id)

    async def execute_tool(
        self,
        tool_id: UUID,
        user_id: UUID,
        payload: ToolExecutionRequest,
    ) -> ToolExecutionResponse:
        tool = await self.tool_repository.get_by_id(tool_id)
        if not tool or tool.status != "active":
            raise ValueError("Tool not found or inactive")

        await self.tool_repository.increment_usage_count(tool_id)

        started_at = datetime.now(timezone.utc)
        result_payload: Dict[str, Any] = {
            "status": "completed",
            "message": f"Tool {tool.name} executed successfully",
        }

        success = True
        error_message: Optional[str] = None

        # TODO: integrate actual execution backend per tool type.

        completed_at = datetime.now(timezone.utc)
        execution_time = (completed_at - started_at).total_seconds()

        await self.tool_repository.update_tool_stats(
            tool_id=tool_id, success=success, execution_time=execution_time
        )

        return ToolExecutionResponse(
            tool_id=tool_id,
            execution_id=(
                f"exec_{tool_id}_{user_id}_{int(started_at.timestamp())}"
            ),
            user_id=user_id,
            parameters=payload.parameters,
            result=result_payload,
            success=success,
            error_message=error_message,
            execution_time=execution_time,
            started_at=started_at,
            completed_at=completed_at,
        )

    # ------------------------------------------------------------------
    # Webhook management
    async def create_webhook(
        self, user_id: UUID, payload: WebhookCreate
    ) -> WebhookResponse:
        webhook = WebhookModel(
            name=payload.name,
            url=payload.url,
            method=payload.method or "POST",
            headers=payload.headers or {},
            secret=payload.secret,
            timeout_seconds=payload.timeout_seconds or 30,
            retry_enabled=payload.retry_enabled if payload.retry_enabled is not None else True,
            max_retries=payload.max_retries or 3,
            retry_delay_seconds=payload.retry_delay_seconds or 60,
            event_types=payload.event_types or [],
            event_filters=payload.event_filters or {},
            transform_template=payload.transform_template,
            status=payload.status or "active",
            created_by=user_id,
        )
        created = await self.webhook_repository.create(webhook)
        return self._webhook_to_response(created)

    async def update_webhook(
        self, webhook_id: UUID, user_id: UUID, payload: WebhookUpdate
    ) -> Optional[WebhookResponse]:
        webhook = await self.webhook_repository.get_by_id(webhook_id)
        if not webhook or webhook.created_by != user_id:
            return None

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(webhook, field, value)

        updated = await self.webhook_repository.update(webhook)
        return self._webhook_to_response(updated) if updated else None

    async def delete_webhook(self, webhook_id: UUID, user_id: UUID) -> bool:
        webhook = await self.webhook_repository.get_by_id(webhook_id)
        if not webhook or webhook.created_by != user_id:
            return False
        return await self.webhook_repository.delete(webhook_id)

    async def get_user_webhooks(self, user_id: UUID) -> List[WebhookResponse]:
        webhooks = await self.webhook_repository.get_by_creator(user_id)
        return [self._webhook_to_response(webhook) for webhook in webhooks]

    async def get_webhooks_by_event_type(
        self, event_type: str
    ) -> List[WebhookResponse]:
        webhooks = await self.webhook_repository.get_webhooks_by_event_type(event_type)
        return [self._webhook_to_response(webhook) for webhook in webhooks]

    async def trigger_webhook(
        self, webhook_id: UUID, event_type: str, event_data: Dict[str, Any]
    ) -> WebhookTriggerResponse:
        webhook = await self.webhook_repository.get_by_id(webhook_id)
        if not webhook or webhook.status != "active":
            raise ValueError("Webhook not found or inactive")

        trigger = WebhookTriggerModel(
            webhook_id=webhook_id,
            trigger_id=f"trigger_{webhook_id}_{int(datetime.now(timezone.utc).timestamp())}",
            event_type=event_type,
            event_data=event_data,
            payload=event_data,
            status="pending",
        )
        created = await self.webhook_trigger_repository.create_trigger(trigger)
        await self.webhook_repository.update_webhook_stats(webhook_id, True)
        return self._webhook_trigger_to_response(created)

    async def get_webhook_triggers(
        self, webhook_id: UUID, user_id: UUID, limit: int = 50
    ) -> List[WebhookTriggerResponse]:
        webhook = await self.webhook_repository.get_by_id(webhook_id)
        if not webhook or webhook.created_by != user_id:
            return []
        triggers = await self.webhook_trigger_repository.get_by_webhook(
            webhook_id, limit
        )
        return [self._webhook_trigger_to_response(trigger) for trigger in triggers]

    # ------------------------------------------------------------------
    # Response helpers
    def _tool_to_response(self, tool: ToolModel) -> ToolResponse:
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
            avg_execution_time=tool.avg_execution_time,
        )

    def _webhook_to_response(self, webhook: WebhookModel) -> WebhookResponse:
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
            last_triggered_at=webhook.last_triggered_at,
        )

    def _webhook_trigger_to_response(
        self, trigger: WebhookTriggerModel
    ) -> WebhookTriggerResponse:
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
            completed_at=trigger.completed_at,
        )


__all__ = ["ToolsService"]
