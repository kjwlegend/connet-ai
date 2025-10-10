"""SQLAlchemy implementations for AI tool repositories."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.modules.ai.tools.models import (
    ToolModel,
    WebhookModel,
    WebhookTriggerModel,
)
from app.modules.ai.tools.repository import (
    ToolRepositoryProtocol,
    WebhookRepositoryProtocol,
    WebhookTriggerRepositoryProtocol,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ToolRepository(BaseRepository[ToolModel], ToolRepositoryProtocol):
    """Persistence implementation for tool definitions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ToolModel)

    async def get_by_id(self, tool_id: UUID) -> Optional[ToolModel]:
        stmt = select(ToolModel).where(ToolModel.id == tool_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[ToolModel]:
        stmt = select(ToolModel).where(ToolModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_creator(self, creator_id: UUID) -> List[ToolModel]:
        stmt = select(ToolModel).where(ToolModel.created_by == creator_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_tools(
        self,
        *,
        query: str,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        security_level: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[ToolModel], int]:
        conditions = [
            or_(
                ToolModel.name.ilike(f"%{query}%"),
                ToolModel.display_name.ilike(f"%{query}%"),
                ToolModel.description.ilike(f"%{query}%"),
            )
        ]

        if tool_type:
            conditions.append(ToolModel.tool_type == tool_type)
        if category:
            conditions.append(ToolModel.category == category)
        if security_level:
            conditions.append(ToolModel.security_level == security_level)
        if status:
            conditions.append(ToolModel.status == status)
        else:
            conditions.append(ToolModel.status == "active")
        if tags:
            for tag in tags:
                conditions.append(func.json_array_contains(ToolModel.tags, tag))

        stmt = (
            select(ToolModel)
            .where(and_(*conditions))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        tools = list(result.scalars().all())

        count_stmt = select(func.count(ToolModel.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = int(count_result.scalar_one())
        return tools, total

    async def get_popular_tools(self, limit: int = 10) -> List[ToolModel]:
        stmt = (
            select(ToolModel)
            .where(ToolModel.status == "active")
            .order_by(ToolModel.usage_count.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recommended_tools(
        self, category: str, limit: int = 5
    ) -> List[ToolModel]:
        stmt = (
            select(ToolModel)
            .where(
                and_(
                    ToolModel.category == category,
                    ToolModel.status == "active",
                    ToolModel.success_rate >= 0.8,
                )
            )
            .order_by(
                ToolModel.success_rate.desc(),
                ToolModel.usage_count.desc(),
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_tool(self, tool: ToolModel) -> ToolModel:
        self.session.add(tool)
        await self.session.flush()
        await self.session.refresh(tool)
        return tool

    async def update_tool(self, tool: ToolModel) -> Optional[ToolModel]:
        stmt = select(ToolModel).where(ToolModel.id == tool.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if not existing:
            return None

        for field in (
            "display_name",
            "description",
            "tool_type",
            "version",
            "configuration",
            "parameters_schema",
            "required_permissions",
            "timeout_seconds",
            "rate_limit",
            "resource_limits",
            "security_level",
            "allowed_domains",
            "blocked_patterns",
            "status",
            "category",
            "tags",
            "usage_count",
            "success_rate",
            "avg_execution_time",
        ):
            setattr(existing, field, getattr(tool, field))

        existing.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def delete_tool(self, tool_id: UUID) -> bool:
        stmt = select(ToolModel).where(ToolModel.id == tool_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        model.status = "inactive"
        model.updated_at = datetime.utcnow()
        await self.session.flush()
        return True

    async def increment_usage_count(self, tool_id: UUID) -> bool:
        stmt = select(ToolModel).where(ToolModel.id == tool_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        model.usage_count += 1
        await self.session.flush()
        return True

    async def update_tool_stats(
        self, *, tool_id: UUID, success: bool, execution_time: float
    ) -> bool:
        stmt = select(ToolModel).where(ToolModel.id == tool_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False

        model.usage_count += 1
        if model.usage_count > 1:
            model.avg_execution_time = (
                (model.avg_execution_time * (model.usage_count - 1) + execution_time)
                / model.usage_count
            )
        else:
            model.avg_execution_time = execution_time

        successful_runs = model.success_rate * (model.usage_count - 1)
        if success:
            successful_runs += 1
        if model.usage_count:
            model.success_rate = successful_runs / model.usage_count

        await self.session.flush()
        return True


class WebhookRepository(BaseRepository[WebhookModel], WebhookRepositoryProtocol):
    """Persistence implementation for webhook configurations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WebhookModel)

    async def get_by_id(self, webhook_id: UUID) -> Optional[WebhookModel]:
        stmt = select(WebhookModel).where(WebhookModel.id == webhook_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_creator(self, creator_id: UUID) -> List[WebhookModel]:
        stmt = select(WebhookModel).where(WebhookModel.created_by == creator_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_webhooks(self) -> List[WebhookModel]:
        stmt = select(WebhookModel).where(WebhookModel.status == "active")
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_webhooks_by_event_type(self, event_type: str) -> List[WebhookModel]:
        stmt = select(WebhookModel).where(
            and_(
                WebhookModel.status == "active",
                func.json_array_contains(WebhookModel.event_types, event_type),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, webhook: WebhookModel) -> WebhookModel:
        self.session.add(webhook)
        await self.session.flush()
        await self.session.refresh(webhook)
        return webhook

    async def update(self, webhook: WebhookModel) -> Optional[WebhookModel]:
        stmt = select(WebhookModel).where(WebhookModel.id == webhook.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        for field in (
            "name",
            "url",
            "method",
            "headers",
            "secret",
            "timeout_seconds",
            "retry_enabled",
            "max_retries",
            "retry_delay_seconds",
            "event_types",
            "event_filters",
            "transform_template",
            "status",
        ):
            setattr(model, field, getattr(webhook, field))

        model.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def delete(self, webhook_id: UUID) -> bool:
        stmt = select(WebhookModel).where(WebhookModel.id == webhook_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def update_webhook_stats(self, webhook_id: UUID, success: bool) -> bool:
        stmt = select(WebhookModel).where(WebhookModel.id == webhook_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False

        model.total_triggers += 1
        if success:
            model.successful_triggers += 1
        else:
            model.failed_triggers += 1
        model.last_triggered_at = datetime.utcnow()

        await self.session.flush()
        return True


class WebhookTriggerRepository(
    BaseRepository[WebhookTriggerModel], WebhookTriggerRepositoryProtocol
):
    """Persistence implementation for webhook trigger history."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WebhookTriggerModel)

    async def get_by_webhook(
        self, webhook_id: UUID, limit: int = 50
    ) -> List[WebhookTriggerModel]:
        stmt = (
            select(WebhookTriggerModel)
            .where(WebhookTriggerModel.webhook_id == webhook_id)
            .order_by(WebhookTriggerModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_failed_triggers(
        self, webhook_id: UUID
    ) -> List[WebhookTriggerModel]:
        stmt = select(WebhookTriggerModel).where(
            and_(
                WebhookTriggerModel.webhook_id == webhook_id,
                WebhookTriggerModel.status == "failed",
                WebhookTriggerModel.retry_count < WebhookTriggerModel.max_retries,
                or_(
                    WebhookTriggerModel.next_retry_at.is_(None),
                    WebhookTriggerModel.next_retry_at <= datetime.utcnow(),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_trigger(
        self, trigger: WebhookTriggerModel
    ) -> WebhookTriggerModel:
        self.session.add(trigger)
        await self.session.flush()
        await self.session.refresh(trigger)
        return trigger

    async def update_trigger(
        self, trigger: WebhookTriggerModel
    ) -> Optional[WebhookTriggerModel]:
        stmt = select(WebhookTriggerModel).where(WebhookTriggerModel.id == trigger.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        for field in (
            "status",
            "success",
            "http_status_code",
            "response_body",
            "response_headers",
            "error_message",
            "retry_count",
            "next_retry_at",
            "sent_at",
            "completed_at",
        ):
            setattr(model, field, getattr(trigger, field))

        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def delete_trigger(self, trigger_id: UUID) -> bool:
        stmt = select(WebhookTriggerModel).where(WebhookTriggerModel.id == trigger_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True


__all__ = [
    "ToolRepository",
    "WebhookRepository",
    "WebhookTriggerRepository",
]
