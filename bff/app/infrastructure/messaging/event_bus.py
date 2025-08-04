"""
Event Bus

This module provides a simple event bus for domain events.
"""

import asyncio
from functools import lru_cache
from typing import Any, Callable, Dict, List

from app.utils.logging import get_logger

logger = get_logger(__name__)


class EventBus:
    """Simple in-memory event bus."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def start(self) -> None:
        """Start the event bus."""
        self._running = True
        logger.info("Event bus started")
    
    async def stop(self) -> None:
        """Stop the event bus."""
        self._running = False
        logger.info("Event bus stopped")
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Handler unsubscribed from event type: {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for event type: {event_type}")
    
    async def publish(self, event_type: str, event_data: Any = None) -> None:
        """Publish an event."""
        if not self._running:
            logger.warning("Event bus is not running, event ignored")
            return
        
        handlers = self._handlers.get(event_type, [])
        
        if not handlers:
            logger.debug(f"No handlers for event type: {event_type}")
            return
        
        logger.debug(f"Publishing event: {event_type} to {len(handlers)} handlers")
        
        # Execute all handlers concurrently
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(event_data))
            else:
                # Wrap sync function in coroutine
                tasks.append(asyncio.create_task(asyncio.to_thread(handler, event_data)))
        
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Error executing event handlers for {event_type}: {e}")
    
    def list_handlers(self) -> Dict[str, int]:
        """List all registered handlers."""
        return {
            event_type: len(handlers)
            for event_type, handlers in self._handlers.items()
        }


@lru_cache()
def get_event_bus() -> EventBus:
    """Get event bus instance."""
    return EventBus()