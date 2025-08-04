"""
Logging Configuration

This module sets up structured logging using structlog.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import Processor


def setup_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """Setup structured logging configuration."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Choose processors based on environment
    if environment == "development":
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def add_correlation_id_processor() -> Processor:
    """Add correlation ID to log records."""
    def processor(logger, name, event_dict):
        # In a real implementation, you would extract correlation ID from context
        # For now, we'll add a placeholder
        event_dict.setdefault("correlation_id", "not-set")
        return event_dict
    
    return processor


def add_user_context_processor() -> Processor:
    """Add user context to log records."""
    def processor(logger, name, event_dict):
        # In a real implementation, you would extract user context from request
        # For now, we'll add a placeholder
        user_context = getattr(logger, "_user_context", None)
        if user_context:
            event_dict.update(user_context)
        return event_dict
    
    return processor


class LoggerAdapter:
    """Logger adapter to add context to all log messages."""
    
    def __init__(self, logger: structlog.stdlib.BoundLogger, context: Dict[str, Any]):
        self.logger = logger.bind(**context)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)


def get_request_logger(request_id: str, user_id: str = None) -> LoggerAdapter:
    """Get a logger with request context."""
    logger = get_logger()
    context = {"request_id": request_id}
    
    if user_id:
        context["user_id"] = user_id
    
    return LoggerAdapter(logger, context)