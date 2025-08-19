"""
Tools Repository Implementation

This module provides the implementation of the Tools repository.
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlmodel import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

# Removed BaseRepositoryInterface import to avoid MRO conflicts
from app.infrastructure.database.models.tool_model import (
    ToolModel,
    WebhookModel,
    WebhookTriggerModel
)
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ToolRepository(BaseRepository[ToolModel]):
    """Tool Repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ToolModel)
        
    async def get_by_name(self, name: str) -> Optional[ToolModel]:
        """Get tool by name."""
        try:
            statement = select(ToolModel).where(ToolModel.name == name)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting tool by name {name}: {e}")
            raise
            
    async def get_by_creator(self, creator_id: UUID) -> List[ToolModel]:
        """Get tools created by user."""
        try:
            statement = select(ToolModel).where(ToolModel.created_by == creator_id)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting tools for creator {creator_id}: {e}")
            raise

    async def get_by_type(self, tool_type: str) -> List[ToolModel]:
        """Get tools by type."""
        try:
            statement = select(ToolModel).where(ToolModel.tool_type == tool_type)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting tools by type {tool_type}: {e}")
            raise

    async def get_by_category(self, category: str) -> List[ToolModel]:
        """Get tools by category."""
        try:
            statement = select(ToolModel).where(ToolModel.category == category)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting tools by category {category}: {e}")
            raise

    async def search_tools(
        self,
        query: str,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        security_level: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[ToolModel], int]:
        """Search tools with filters."""
        try:
            conditions = []
            
            # Text search
            search_condition = or_(
                ToolModel.name.ilike(f"%{query}%"),
                ToolModel.display_name.ilike(f"%{query}%"),
                ToolModel.description.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
            
            # Filter by type
            if tool_type:
                conditions.append(ToolModel.tool_type == tool_type)
                
            # Filter by category
            if category:
                conditions.append(ToolModel.category == category)
                
            # Filter by security level
            if security_level:
                conditions.append(ToolModel.security_level == security_level)
                
            # Filter by status
            if status:
                conditions.append(ToolModel.status == status)
            else:
                # Default to active tools only
                conditions.append(ToolModel.status == "active")
                
            # Filter by tags
            if tags:
                for tag in tags:
                    conditions.append(func.json_array_contains(ToolModel.tags, tag))
            
            stmt = select(ToolModel).where(and_(*conditions)).offset(offset).limit(limit)
            result = await self.session.exec(stmt)
            tools = result.all()
            
            # Get total count
            count_stmt = select(func.count(ToolModel.id)).where(and_(*conditions))
            count_result = await self.session.exec(count_stmt)
            total_count = count_result.scalar()
            
            return tools, total_count
        except Exception as e:
            logger.error(f"Error searching tools: {e}")
            raise

    async def get_popular_tools(self, limit: int = 10) -> List[ToolModel]:
        """Get most popular tools by usage count."""
        try:
            stmt = select(ToolModel).where(
                ToolModel.status == "active"
            ).order_by(ToolModel.usage_count.desc()).limit(limit)
            result = await self.session.exec(stmt)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting popular tools: {e}")
            raise

    async def get_recommended_tools(self, category: str, limit: int = 5) -> List[ToolModel]:
        """Get recommended tools by category and success rate."""
        try:
            stmt = select(ToolModel).where(
                and_(
                    ToolModel.category == category,
                    ToolModel.status == "active",
                    ToolModel.success_rate >= 0.8
                )
            ).order_by(
                ToolModel.success_rate.desc(),
                ToolModel.usage_count.desc()
            ).limit(limit)
            result = await self.session.exec(stmt)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting recommended tools: {e}")
            raise

    async def create_tool(self, tool: ToolModel) -> ToolModel:
        """Create a new tool."""
        try:
            self.session.add(tool)
            await self.session.commit()
            await self.session.refresh(tool)
            return tool
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating tool: {e}")
            raise

    async def update_tool(self, tool: ToolModel) -> ToolModel:
        """Update a tool."""
        try:
            stmt = select(ToolModel).where(ToolModel.id == tool.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return None
            
            for field, value in tool.model_dump(exclude_unset=True).items():
                if field != 'id':
                    setattr(model, field, value)
            
            model.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(model)
            
            logger.info(f"Tool updated successfully: {tool.id}")
            return model
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update tool {tool.id}: {e}")
            raise

    async def delete_tool(self, tool_id: UUID) -> bool:
        """Delete a tool (soft delete by changing status)."""
        try:
            stmt = select(ToolModel).where(ToolModel.id == tool_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return False
            
            model.status = "inactive"
            model.updated_at = datetime.utcnow()
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to delete tool {tool_id}: {e}")
            return False

    async def increment_usage_count(self, tool_id: UUID) -> bool:
        """Increment tool usage count."""
        try:
            stmt = select(ToolModel).where(ToolModel.id == tool_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return False
            
            model.usage_count += 1
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to increment usage count for tool {tool_id}: {e}")
            return False

    async def update_tool_stats(
        self,
        tool_id: UUID,
        success: bool,
        execution_time: float
    ) -> bool:
        """Update tool statistics after execution."""
        try:
            stmt = select(ToolModel).where(ToolModel.id == tool_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return False
            
            # Update usage count
            model.usage_count += 1
            
            # Update average execution time
            if model.usage_count > 1:
                model.avg_execution_time = (
                    (model.avg_execution_time * (model.usage_count - 1) + execution_time)
                    / model.usage_count
                )
            else:
                model.avg_execution_time = execution_time
            
            # Update success rate
            if success:
                successful_executions = model.success_rate * (model.usage_count - 1) + 1
            else:
                successful_executions = model.success_rate * (model.usage_count - 1)
            
            model.success_rate = successful_executions / model.usage_count
            
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update tool stats for {tool_id}: {e}")
            return False


class WebhookRepository(BaseRepository[WebhookModel]):
    """Webhook Repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, WebhookModel)

    async def get_by_creator(self, creator_id: UUID) -> List[WebhookModel]:
        """Get webhooks created by user."""
        try:
            statement = select(WebhookModel).where(WebhookModel.created_by == creator_id)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting webhooks for creator {creator_id}: {e}")
            raise

    async def get_active_webhooks(self) -> List[WebhookModel]:
        """Get all active webhooks."""
        try:
            statement = select(WebhookModel).where(WebhookModel.status == "active")
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting active webhooks: {e}")
            raise

    async def get_webhooks_by_event_type(self, event_type: str) -> List[WebhookModel]:
        """Get webhooks that handle specific event type."""
        try:
            statement = select(WebhookModel).where(
                and_(
                    WebhookModel.status == "active",
                    func.json_array_contains(WebhookModel.event_types, event_type)
                )
            )
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting webhooks by event type {event_type}: {e}")
            raise

    async def update_webhook_stats(self, webhook_id: UUID, success: bool) -> bool:
        """Update webhook trigger statistics."""
        try:
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
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update webhook stats for {webhook_id}: {e}")
            return False


class WebhookTriggerRepository(BaseRepository[WebhookTriggerModel]):
    """Webhook Trigger Repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, WebhookTriggerModel)

    async def get_by_webhook(self, webhook_id: UUID, limit: int = 50) -> List[WebhookTriggerModel]:
        """Get recent triggers for a webhook."""
        try:
            statement = select(WebhookTriggerModel).where(
                WebhookTriggerModel.webhook_id == webhook_id
            ).order_by(WebhookTriggerModel.created_at.desc()).limit(limit)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting webhook triggers for {webhook_id}: {e}")
            raise

    async def get_failed_triggers(self, webhook_id: UUID) -> List[WebhookTriggerModel]:
        """Get failed triggers for retry."""
        try:
            statement = select(WebhookTriggerModel).where(
                and_(
                    WebhookTriggerModel.webhook_id == webhook_id,
                    WebhookTriggerModel.status == "failed",
                    WebhookTriggerModel.retry_count < WebhookTriggerModel.max_retries,
                    or_(
                        WebhookTriggerModel.next_retry_at.is_(None),
                        WebhookTriggerModel.next_retry_at <= datetime.utcnow()
                    )
                )
            )
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting failed triggers for webhook {webhook_id}: {e}")
            raise

    async def create_trigger(self, trigger: WebhookTriggerModel) -> WebhookTriggerModel:
        """Create a new webhook trigger."""
        try:
            self.session.add(trigger)
            await self.session.commit()
            await self.session.refresh(trigger)
            return trigger
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating webhook trigger: {e}")
            raise