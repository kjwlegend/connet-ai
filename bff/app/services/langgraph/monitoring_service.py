"""Compatibility shim for workflow monitoring service."""

from app.modules.ai.workflows.monitoring_service import (
    MonitoringService,
    PerformanceMetrics,
    SystemHealth,
    Alert,
)

__all__ = [
    "MonitoringService",
    "PerformanceMetrics",
    "SystemHealth",
    "Alert",
]
