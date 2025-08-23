"""
Workflow Monitoring Service

Provides comprehensive monitoring, analytics, and alerting for LangGraph workflows.
Tracks performance, errors, costs, and system health.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from dataclasses import dataclass, field
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.infrastructure.database.models.workflow_execution_model import (
    WorkflowExecutionModel,
    NodeExecutionModel,
    ToolExecutionModel,
    TokenUsageModel
)
from app.services.langgraph.execution_tracker import ExecutionMetrics


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring dashboard"""
    
    # Time period
    period_start: datetime
    period_end: datetime
    
    # Execution metrics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration_ms: float = 0.0
    median_duration_ms: float = 0.0
    
    # Resource usage
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    average_cost_per_execution: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    top_errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Workflow type breakdown
    workflow_type_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # User activity
    active_users: int = 0
    top_users: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100


@dataclass
class SystemHealth:
    """System health indicators"""
    
    timestamp: datetime
    
    # Resource usage
    active_executions: int = 0
    queued_executions: int = 0
    memory_usage_mb: float = 0.0
    
    # API health
    api_response_time_ms: float = 0.0
    database_response_time_ms: float = 0.0
    llm_response_time_ms: float = 0.0
    
    # Error rates
    api_error_rate: float = 0.0
    database_error_rate: float = 0.0
    llm_error_rate: float = 0.0
    
    # Cost tracking
    hourly_cost_usd: float = 0.0
    daily_cost_usd: float = 0.0
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return (
            self.api_error_rate < 5.0 and
            self.database_error_rate < 2.0 and
            self.llm_error_rate < 10.0 and
            self.api_response_time_ms < 1000
        )


@dataclass
class Alert:
    """System alert"""
    
    id: str
    timestamp: datetime
    severity: str  # "info", "warning", "error", "critical"
    category: str
    title: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class MonitoringService:
    """Monitors workflow execution and system health"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.performance_cache: Dict[str, PerformanceMetrics] = {}
        
        # Monitoring thresholds
        self.thresholds = {
            "max_execution_time_ms": 30000,
            "max_error_rate": 10.0,
            "max_cost_per_hour": 10.0,
            "max_tokens_per_hour": 100000,
            "min_success_rate": 95.0
        }
    
    async def get_performance_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[UUID] = None,
        workflow_type: Optional[str] = None
    ) -> PerformanceMetrics:
        """Get comprehensive performance metrics for a time period"""
        
        cache_key = f"{start_date.isoformat()}_{end_date.isoformat()}_{user_id}_{workflow_type}"
        
        # Check cache
        if cache_key in self.performance_cache:
            cached = self.performance_cache[cache_key]
            # Use cached data if less than 5 minutes old
            if datetime.utcnow() - cached.period_end < timedelta(minutes=5):
                return cached
        
        # Build query
        stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.started_at >= start_date,
            WorkflowExecutionModel.started_at <= end_date
        )
        
        if user_id:
            stmt = stmt.where(WorkflowExecutionModel.user_id == user_id)
        
        if workflow_type:
            stmt = stmt.where(WorkflowExecutionModel.workflow_type == workflow_type)
        
        result = await self.session.execute(stmt)
        executions = result.scalars().all()
        
        # Calculate metrics
        metrics = PerformanceMetrics(
            period_start=start_date,
            period_end=end_date
        )
        
        if not executions:
            return metrics
        
        # Basic counts
        metrics.total_executions = len(executions)
        metrics.successful_executions = sum(1 for e in executions if e.status == "completed")
        metrics.failed_executions = sum(1 for e in executions if e.status == "failed")
        
        # Duration statistics
        durations = [e.total_duration_ms for e in executions if e.total_duration_ms]
        if durations:
            metrics.average_duration_ms = sum(durations) / len(durations)
            metrics.median_duration_ms = sorted(durations)[len(durations) // 2]
        
        # Resource usage
        metrics.total_tokens_used = sum(e.total_tokens for e in executions)
        metrics.total_cost_usd = sum(e.total_cost_usd or 0.0 for e in executions)
        
        if metrics.total_executions > 0:
            metrics.average_cost_per_execution = metrics.total_cost_usd / metrics.total_executions
            metrics.error_rate = (metrics.failed_executions / metrics.total_executions) * 100
        
        # Workflow type breakdown
        workflow_stats = defaultdict(lambda: {"count": 0, "success": 0, "duration": []})
        for execution in executions:
            wf_type = execution.workflow_type
            workflow_stats[wf_type]["count"] += 1
            if execution.status == "completed":
                workflow_stats[wf_type]["success"] += 1
            if execution.total_duration_ms:
                workflow_stats[wf_type]["duration"].append(execution.total_duration_ms)
        
        for wf_type, stats in workflow_stats.items():
            metrics.workflow_type_stats[wf_type] = {
                "total_executions": stats["count"],
                "success_rate": (stats["success"] / stats["count"]) * 100 if stats["count"] > 0 else 0,
                "average_duration_ms": sum(stats["duration"]) / len(stats["duration"]) if stats["duration"] else 0
            }
        
        # User activity
        user_counts = defaultdict(int)
        for execution in executions:
            user_counts[str(execution.user_id)] += 1
        
        metrics.active_users = len(user_counts)
        metrics.top_users = [
            {"user_id": user_id, "executions": count}
            for user_id, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Error analysis
        error_messages = defaultdict(int)
        for execution in executions:
            if execution.status == "failed" and execution.error_data:
                error_msg = execution.error_data.get("error", "Unknown error")[:100]
                error_messages[error_msg] += 1
        
        metrics.top_errors = [
            {"error": error, "count": count}
            for error, count in sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Cache results
        self.performance_cache[cache_key] = metrics
        
        return metrics
    
    async def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        
        health = SystemHealth(timestamp=datetime.utcnow())
        
        # Get active executions from last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        active_stmt = select(func.count(WorkflowExecutionModel.id)).where(
            WorkflowExecutionModel.status == "running"
        )
        result = await self.session.execute(active_stmt)
        health.active_executions = result.scalar() or 0
        
        # Recent performance metrics
        recent_stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.started_at >= one_hour_ago
        )
        result = await self.session.execute(recent_stmt)
        recent_executions = result.scalars().all()
        
        if recent_executions:
            # Calculate response times
            durations = [e.total_duration_ms for e in recent_executions if e.total_duration_ms]
            health.api_response_time_ms = sum(durations) / len(durations) if durations else 0
            
            # Calculate error rates
            total_recent = len(recent_executions)
            failed_recent = sum(1 for e in recent_executions if e.status == "failed")
            health.api_error_rate = (failed_recent / total_recent) * 100 if total_recent > 0 else 0
            
            # Cost tracking
            health.hourly_cost_usd = sum(e.total_cost_usd or 0.0 for e in recent_executions)
        
        # Daily cost
        day_ago = datetime.utcnow() - timedelta(days=1)
        daily_stmt = select(func.sum(WorkflowExecutionModel.total_cost_usd)).where(
            WorkflowExecutionModel.started_at >= day_ago
        )
        result = await self.session.execute(daily_stmt)
        health.daily_cost_usd = result.scalar() or 0.0
        
        return health
    
    async def check_alerts(self) -> List[Alert]:
        """Check for system alerts based on thresholds"""
        
        new_alerts = []
        health = await self.get_system_health()
        
        # High error rate alert
        if health.api_error_rate > self.thresholds["max_error_rate"]:
            alert = Alert(
                id=f"high_error_rate_{int(datetime.utcnow().timestamp())}",
                timestamp=datetime.utcnow(),
                severity="warning",
                category="performance",
                title="High Error Rate Detected",
                message=f"API error rate is {health.api_error_rate:.1f}%, exceeding threshold of {self.thresholds['max_error_rate']}%",
                metadata={"error_rate": health.api_error_rate}
            )
            new_alerts.append(alert)
            self.active_alerts[alert.id] = alert
        
        # High cost alert
        if health.hourly_cost_usd > self.thresholds["max_cost_per_hour"]:
            alert = Alert(
                id=f"high_cost_{int(datetime.utcnow().timestamp())}",
                timestamp=datetime.utcnow(),
                severity="warning",
                category="cost",
                title="High Hourly Cost",
                message=f"Hourly cost is ${health.hourly_cost_usd:.2f}, exceeding threshold of ${self.thresholds['max_cost_per_hour']}",
                metadata={"hourly_cost": health.hourly_cost_usd}
            )
            new_alerts.append(alert)
            self.active_alerts[alert.id] = alert
        
        # Slow response time alert
        if health.api_response_time_ms > self.thresholds["max_execution_time_ms"]:
            alert = Alert(
                id=f"slow_response_{int(datetime.utcnow().timestamp())}",
                timestamp=datetime.utcnow(),
                severity="warning",
                category="performance",
                title="Slow Response Times",
                message=f"Average response time is {health.api_response_time_ms:.0f}ms, exceeding threshold of {self.thresholds['max_execution_time_ms']}ms",
                metadata={"response_time_ms": health.api_response_time_ms}
            )
            new_alerts.append(alert)
            self.active_alerts[alert.id] = alert
        
        # Add alerts to history
        self.alert_history.extend(new_alerts)
        
        return new_alerts
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        
        del self.active_alerts[alert_id]
        
        logger.info(f"Resolved alert: {alert_id}")
        return True
    
    async def get_cost_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        breakdown_by: str = "day"  # "hour", "day", "user", "workflow_type"
    ) -> Dict[str, Any]:
        """Get detailed cost analysis"""
        
        stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.started_at >= start_date,
            WorkflowExecutionModel.started_at <= end_date,
            WorkflowExecutionModel.total_cost_usd.isnot(None)
        )
        
        result = await self.session.execute(stmt)
        executions = result.scalars().all()
        
        total_cost = sum(e.total_cost_usd for e in executions)
        total_tokens = sum(e.total_tokens for e in executions)
        
        analysis = {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "average_cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0,
            "breakdown": {}
        }
        
        # Breakdown by requested dimension
        if breakdown_by == "user":
            user_costs = defaultdict(float)
            for execution in executions:
                user_costs[str(execution.user_id)] += execution.total_cost_usd
            analysis["breakdown"] = dict(user_costs)
            
        elif breakdown_by == "workflow_type":
            workflow_costs = defaultdict(float)
            for execution in executions:
                workflow_costs[execution.workflow_type] += execution.total_cost_usd
            analysis["breakdown"] = dict(workflow_costs)
            
        elif breakdown_by == "day":
            daily_costs = defaultdict(float)
            for execution in executions:
                day_key = execution.started_at.strftime("%Y-%m-%d")
                daily_costs[day_key] += execution.total_cost_usd
            analysis["breakdown"] = dict(daily_costs)
            
        elif breakdown_by == "hour":
            hourly_costs = defaultdict(float)
            for execution in executions:
                hour_key = execution.started_at.strftime("%Y-%m-%d %H:00")
                hourly_costs[hour_key] += execution.total_cost_usd
            analysis["breakdown"] = dict(hourly_costs)
        
        return analysis
    
    async def get_usage_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get usage trends over time"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Daily execution counts
        daily_executions = defaultdict(int)
        daily_costs = defaultdict(float)
        daily_tokens = defaultdict(int)
        
        stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.started_at >= start_date
        )
        
        result = await self.session.execute(stmt)
        executions = result.scalars().all()
        
        for execution in executions:
            day_key = execution.started_at.strftime("%Y-%m-%d")
            daily_executions[day_key] += 1
            daily_costs[day_key] += execution.total_cost_usd or 0.0
            daily_tokens[day_key] += execution.total_tokens
        
        return {
            "period_days": days,
            "daily_executions": dict(daily_executions),
            "daily_costs": dict(daily_costs),
            "daily_tokens": dict(daily_tokens),
            "total_executions": len(executions),
            "total_cost": sum(daily_costs.values()),
            "total_tokens": sum(daily_tokens.values())
        }
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 50) -> List[Alert]:
        """Get recent alert history"""
        return sorted(self.alert_history, key=lambda a: a.timestamp, reverse=True)[:limit]
    
    def update_thresholds(self, thresholds: Dict[str, Any]) -> None:
        """Update monitoring thresholds"""
        self.thresholds.update(thresholds)
        logger.info(f"Updated monitoring thresholds: {thresholds}")
    
    def clear_cache(self) -> None:
        """Clear performance metrics cache"""
        self.performance_cache.clear()
        logger.info("Cleared performance metrics cache")