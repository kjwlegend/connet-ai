"""AI Tool repository implementation."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.ai_agent_model import (
    AIToolModel,
    AIToolExecutionModel,
    AIWebhookModel,
    AIWebhookTriggerModel
)
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.schemas.ai import ToolCreate, PaginationParams


class AIToolRepositoryImpl(BaseRepository[AIToolModel]):
    """AI Tool repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIToolModel)
    
    async def create_tool(self, tool_data: ToolCreate, user_id: UUID) -> AIToolModel:
        """Create a new tool"""
        
        tool_dict = tool_data.model_dump(exclude_unset=True)
        tool_dict.update({
            'created_by': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        
        # Convert parameters schema to dict format
        if 'parameters_schema' in tool_dict:
            tool_dict['parameters_schema'] = [param.model_dump() for param in tool_dict['parameters_schema']]
        
        tool = AIToolModel(**tool_dict)
        self.session.add(tool)
        await self.session.commit()
        await self.session.refresh(tool)
        
        return tool
    
    async def get_tool_by_name(self, name: str) -> Optional[AIToolModel]:
        """Get tool by name"""
        
        stmt = select(AIToolModel).where(
            and_(AIToolModel.name == name, AIToolModel.status == "active")
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_tool_by_id(self, tool_id: UUID) -> Optional[AIToolModel]:
        """Get tool by ID"""
        
        stmt = select(AIToolModel).where(AIToolModel.id == tool_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_tools(
        self,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[UUID] = None,
        pagination: Optional[PaginationParams] = None
    ) -> tuple[List[AIToolModel], int]:
        """List tools with filtering and pagination"""
        
        # Build base query
        stmt = select(AIToolModel)
        
        # Apply filters
        conditions = []
        if tool_type:
            conditions.append(AIToolModel.tool_type == tool_type)
        if category:
            conditions.append(AIToolModel.category == category)
        if status:
            conditions.append(AIToolModel.status == status)
        else:
            conditions.append(AIToolModel.status == "active")  # Default to active only
        if user_id:
            conditions.append(AIToolModel.created_by == user_id)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply sorting
        if pagination and pagination.sort_by:
            sort_column = getattr(AIToolModel, pagination.sort_by, AIToolModel.created_at)
            if pagination.sort_order == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(AIToolModel.name.asc())
        
        # Apply pagination
        if pagination:
            offset = (pagination.page - 1) * pagination.size
            stmt = stmt.offset(offset).limit(pagination.size)
        
        result = await self.session.execute(stmt)
        tools = result.scalars().all()
        
        return list(tools), total
    
    async def get_tools_by_names(self, tool_names: List[str]) -> List[AIToolModel]:
        """Get multiple tools by names"""
        
        stmt = select(AIToolModel).where(
            and_(
                AIToolModel.name.in_(tool_names),
                AIToolModel.status == "active"
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_tool_usage_stats(self, tool_id: UUID, execution_time: float, success: bool):
        """Update tool usage statistics"""
        
        stmt = select(AIToolModel).where(AIToolModel.id == tool_id)
        result = await self.session.execute(stmt)
        tool = result.scalar_one_or_none()
        
        if not tool:
            return
        
        # Calculate new statistics
        total_executions = tool.usage_count + 1
        new_avg_time = (tool.avg_execution_time * tool.usage_count + execution_time) / total_executions
        
        if success:
            new_success_rate = (tool.success_rate * tool.usage_count + 1) / total_executions
        else:
            new_success_rate = (tool.success_rate * tool.usage_count) / total_executions
        
        # Update the tool
        update_data = {
            'usage_count': total_executions,
            'avg_execution_time': new_avg_time,
            'success_rate': new_success_rate,
            'updated_at': datetime.utcnow()
        }
        
        stmt = update(AIToolModel).where(AIToolModel.id == tool_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def delete_tool(self, tool_id: UUID, user_id: UUID) -> bool:
        """Delete a tool (soft delete by setting status)"""
        
        # Check ownership
        stmt = select(AIToolModel).where(
            and_(AIToolModel.id == tool_id, AIToolModel.created_by == user_id)
        )
        result = await self.session.execute(stmt)
        tool = result.scalar_one_or_none()
        
        if not tool:
            return False
        
        # Soft delete
        stmt = update(AIToolModel).where(AIToolModel.id == tool_id).values(
            status="inactive",
            updated_at=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
        return True


class AIToolExecutionRepositoryImpl(BaseRepository[AIToolExecutionModel]):
    """AI Tool execution repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIToolExecutionModel)
    
    async def create_execution(self, execution_data: Dict[str, Any]) -> AIToolExecutionModel:
        """Create tool execution record"""
        
        execution = AIToolExecutionModel(**execution_data)
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        
        return execution
    
    async def update_execution_result(
        self,
        execution_id: str,
        result: Dict[str, Any],
        success: bool,
        error_message: Optional[str] = None
    ):
        """Update execution result"""
        
        update_data = {
            'result': result,
            'success': success,
            'status': 'completed' if success else 'failed',
            'completed_at': datetime.utcnow()
        }
        
        if error_message:
            update_data['error_message'] = error_message
        
        stmt = update(AIToolExecutionModel).where(
            AIToolExecutionModel.execution_id == execution_id
        ).values(**update_data)
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def get_execution_by_id(self, execution_id: str) -> Optional[AIToolExecutionModel]:
        """Get execution by ID"""
        
        stmt = select(AIToolExecutionModel).where(
            AIToolExecutionModel.execution_id == execution_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_executions_by_conversation(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[AIToolExecutionModel]:
        """Get executions for a conversation"""
        
        stmt = select(AIToolExecutionModel).where(
            AIToolExecutionModel.conversation_id == conversation_id
        ).order_by(AIToolExecutionModel.started_at.desc())
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_execution_stats(
        self,
        tool_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get execution statistics"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        conditions = [AIToolExecutionModel.started_at >= since_date]
        
        if tool_id:
            conditions.append(AIToolExecutionModel.tool_id == tool_id)
        if user_id:
            conditions.append(AIToolExecutionModel.user_id == user_id)
        
        # Total executions
        total_result = await self.session.execute(
            select(func.count(AIToolExecutionModel.id)).where(and_(*conditions))
        )
        total = total_result.scalar()
        
        # Success rate
        success_result = await self.session.execute(
            select(func.count(AIToolExecutionModel.id)).where(
                and_(AIToolExecutionModel.success == True, *conditions)
            )
        )
        successful = success_result.scalar()
        
        # Average execution time
        avg_time_result = await self.session.execute(
            select(func.avg(AIToolExecutionModel.execution_time)).where(
                and_(AIToolExecutionModel.status == 'completed', *conditions)
            )
        )
        avg_time = avg_time_result.scalar() or 0.0
        
        return {
            'total_executions': total,
            'successful_executions': successful,
            'success_rate': successful / total if total > 0 else 0.0,
            'average_execution_time': float(avg_time)
        }


class AIWebhookRepositoryImpl(BaseRepository[AIWebhookModel]):
    """AI Webhook repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIWebhookModel)
    
    async def create_webhook(self, webhook_data: Dict[str, Any], user_id: UUID) -> AIWebhookModel:
        """Create webhook"""
        
        webhook_data.update({
            'created_by': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        webhook = AIWebhookModel(**webhook_data)
        self.session.add(webhook)
        await self.session.commit()
        await self.session.refresh(webhook)
        
        return webhook
    
    async def get_active_webhooks(self, event_type: Optional[str] = None) -> List[AIWebhookModel]:
        """Get active webhooks, optionally filtered by event type"""
        
        conditions = [AIWebhookModel.status == "active"]
        
        if event_type:
            conditions.append(
                or_(
                    AIWebhookModel.event_types == [],  # Listen to all events
                    func.jsonb_exists(AIWebhookModel.event_types, event_type)
                )
            )
        
        stmt = select(AIWebhookModel).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_webhook_stats(self, webhook_id: UUID, success: bool):
        """Update webhook trigger statistics"""
        
        if success:
            update_data = {
                'total_triggers': AIWebhookModel.total_triggers + 1,
                'successful_triggers': AIWebhookModel.successful_triggers + 1,
                'last_triggered_at': datetime.utcnow()
            }
        else:
            update_data = {
                'total_triggers': AIWebhookModel.total_triggers + 1,
                'failed_triggers': AIWebhookModel.failed_triggers + 1,
                'last_triggered_at': datetime.utcnow()
            }
        
        stmt = update(AIWebhookModel).where(AIWebhookModel.id == webhook_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()


class AIWebhookTriggerRepositoryImpl(BaseRepository[AIWebhookTriggerModel]):
    """AI Webhook trigger repository implementation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIWebhookTriggerModel)
    
    async def create_trigger(self, trigger_data: Dict[str, Any]) -> AIWebhookTriggerModel:
        """Create webhook trigger record"""
        
        trigger = AIWebhookTriggerModel(**trigger_data)
        self.session.add(trigger)
        await self.session.commit()
        await self.session.refresh(trigger)
        
        return trigger
    
    async def update_trigger_result(
        self,
        trigger_id: str,
        success: bool,
        http_status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        response_headers: Optional[Dict[str, str]] = None,
        error_message: Optional[str] = None
    ):
        """Update trigger result"""
        
        update_data = {
            'success': success,
            'status': 'completed' if success else 'failed',
            'completed_at': datetime.utcnow()
        }
        
        if http_status_code:
            update_data['http_status_code'] = http_status_code
        if response_body:
            update_data['response_body'] = response_body
        if response_headers:
            update_data['response_headers'] = response_headers
        if error_message:
            update_data['error_message'] = error_message
        
        stmt = update(AIWebhookTriggerModel).where(
            AIWebhookTriggerModel.trigger_id == trigger_id
        ).values(**update_data)
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def get_failed_triggers_for_retry(self, limit: int = 100) -> List[AIWebhookTriggerModel]:
        """Get failed triggers that need retry"""
        
        stmt = select(AIWebhookTriggerModel).where(
            and_(
                AIWebhookTriggerModel.status == 'failed',
                AIWebhookTriggerModel.retry_count < AIWebhookTriggerModel.max_retries,
                or_(
                    AIWebhookTriggerModel.next_retry_at.is_(None),
                    AIWebhookTriggerModel.next_retry_at <= datetime.utcnow()
                )
            )
        ).order_by(AIWebhookTriggerModel.created_at.asc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def increment_retry_count(self, trigger_id: str, next_retry_at: datetime):
        """Increment retry count and set next retry time"""
        
        stmt = update(AIWebhookTriggerModel).where(
            AIWebhookTriggerModel.trigger_id == trigger_id
        ).values(
            retry_count=AIWebhookTriggerModel.retry_count + 1,
            next_retry_at=next_retry_at,
            status='retry'
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def get_webhook_trigger_history(
        self,
        webhook_id: UUID,
        limit: int = 50
    ) -> List[AIWebhookTriggerModel]:
        """Get trigger history for a webhook"""
        
        stmt = select(AIWebhookTriggerModel).where(
            AIWebhookTriggerModel.webhook_id == webhook_id
        ).order_by(AIWebhookTriggerModel.created_at.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())