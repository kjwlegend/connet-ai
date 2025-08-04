"""
Supabase Realtime Integration

This module provides real-time functionality using Supabase Realtime.
"""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

from supabase import Client
from realtime.connection import Socket
from realtime.channel import Channel

from app.infrastructure.external.supabase.client import get_supabase_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RealtimeEventType(str, Enum):
    """Supabase Realtime event types."""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"


class RealtimeChannel:
    """Wrapper for Supabase Realtime channel."""
    
    def __init__(self, channel: Channel, topic: str):
        self.channel = channel
        self.topic = topic
        self.is_subscribed = False
    
    def on_insert(self, callback: Callable[[Dict], None]) -> 'RealtimeChannel':
        """Listen for INSERT events."""
        self.channel.on("postgres_changes", {
            "event": RealtimeEventType.INSERT,
            "schema": "public"
        }, callback)
        return self
    
    def on_update(self, callback: Callable[[Dict], None]) -> 'RealtimeChannel':
        """Listen for UPDATE events."""
        self.channel.on("postgres_changes", {
            "event": RealtimeEventType.UPDATE,
            "schema": "public"
        }, callback)
        return self
    
    def on_delete(self, callback: Callable[[Dict], None]) -> 'RealtimeChannel':
        """Listen for DELETE events."""
        self.channel.on("postgres_changes", {
            "event": RealtimeEventType.DELETE,
            "schema": "public"
        }, callback)
        return self
    
    def on_table_change(
        self,
        table: str,
        callback: Callable[[Dict], None],
        event: Optional[RealtimeEventType] = None
    ) -> 'RealtimeChannel':
        """Listen for changes on a specific table."""
        filter_config = {
            "schema": "public",
            "table": table
        }
        
        if event:
            filter_config["event"] = event
        
        self.channel.on("postgres_changes", filter_config, callback)
        return self
    
    def on_presence_sync(self, callback: Callable[[Dict], None]) -> 'RealtimeChannel':
        """Listen for presence sync events."""
        self.channel.on("presence", {"event": "sync"}, callback)
        return self
    
    def on_presence_join(self, callback: Callable[[Dict], None]) -> 'RealtimeChannel':
        """Listen for presence join events."""
        self.channel.on("presence", {"event": "join"}, callback)
        return self
    
    def on_presence_leave(self, callback: Callable[[Dict], None]) -> 'RealtimeChannel':
        """Listen for presence leave events."""
        self.channel.on("presence", {"event": "leave"}, callback)
        return self
    
    def track_presence(self, data: Dict) -> 'RealtimeChannel':
        """Track user presence."""
        self.channel.track(data)
        return self
    
    def untrack_presence(self) -> 'RealtimeChannel':
        """Stop tracking user presence."""
        self.channel.untrack()
        return self
    
    def subscribe(self) -> 'RealtimeChannel':
        """Subscribe to the channel."""
        if not self.is_subscribed:
            self.channel.subscribe()
            self.is_subscribed = True
            logger.info(f"Subscribed to realtime channel: {self.topic}")
        return self
    
    def unsubscribe(self) -> bool:
        """Unsubscribe from the channel."""
        if self.is_subscribed:
            self.channel.unsubscribe()
            self.is_subscribed = False
            logger.info(f"Unsubscribed from realtime channel: {self.topic}")
            return True
        return False
    
    def send(self, event: str, payload: Dict) -> 'RealtimeChannel':
        """Send a message to the channel."""
        self.channel.send({
            "type": "broadcast",
            "event": event,
            "payload": payload
        })
        return self


class SupabaseRealtimeManager:
    """Supabase Realtime manager for real-time features."""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()
        self.channels: Dict[str, RealtimeChannel] = {}
        self.socket: Optional[Socket] = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connect to Supabase Realtime."""
        try:
            if not self.is_connected:
                # Initialize the realtime connection
                self.socket = self.client.realtime
                self.is_connected = True
                logger.info("Connected to Supabase Realtime")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase Realtime: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Supabase Realtime."""
        try:
            if self.is_connected:
                # Unsubscribe from all channels
                for channel in self.channels.values():
                    channel.unsubscribe()
                
                self.channels.clear()
                
                if self.socket:
                    self.socket.disconnect()
                
                self.is_connected = False
                logger.info("Disconnected from Supabase Realtime")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect from Supabase Realtime: {e}")
            return False
    
    def create_channel(self, topic: str) -> RealtimeChannel:
        """Create a new realtime channel."""
        if topic in self.channels:
            return self.channels[topic]
        
        # Ensure we're connected
        if not self.is_connected:
            self.connect()
        
        # Create channel
        channel = self.client.channel(topic)
        realtime_channel = RealtimeChannel(channel, topic)
        
        self.channels[topic] = realtime_channel
        logger.info(f"Created realtime channel: {topic}")
        
        return realtime_channel
    
    def get_channel(self, topic: str) -> Optional[RealtimeChannel]:
        """Get existing channel by topic."""
        return self.channels.get(topic)
    
    def remove_channel(self, topic: str) -> bool:
        """Remove and unsubscribe from a channel."""
        if topic in self.channels:
            channel = self.channels[topic]
            channel.unsubscribe()
            del self.channels[topic]
            logger.info(f"Removed realtime channel: {topic}")
            return True
        return False
    
    def create_conversation_channel(self, conversation_id: str) -> RealtimeChannel:
        """Create a channel for conversation updates."""
        topic = f"conversation:{conversation_id}"
        return self.create_channel(topic)
    
    def create_user_channel(self, user_id: str) -> RealtimeChannel:
        """Create a channel for user-specific updates."""
        topic = f"user:{user_id}"
        return self.create_channel(topic)
    
    def create_presence_channel(self, room_id: str) -> RealtimeChannel:
        """Create a presence channel for a room/conversation."""
        topic = f"presence:{room_id}"
        return self.create_channel(topic)
    
    def broadcast_to_channel(
        self,
        topic: str,
        event: str,
        payload: Dict
    ) -> bool:
        """Broadcast message to a channel."""
        try:
            channel = self.get_channel(topic)
            if not channel:
                logger.warning(f"Channel not found: {topic}")
                return False
            
            channel.send(event, payload)
            logger.debug(f"Broadcasted to {topic}: {event}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to broadcast to {topic}: {e}")
            return False
    
    def setup_database_changes_listener(
        self,
        table: str,
        callback: Callable[[Dict], None],
        event_type: Optional[RealtimeEventType] = None
    ) -> RealtimeChannel:
        """Setup listener for database changes on a table."""
        topic = f"db_changes:{table}"
        channel = self.create_channel(topic)
        
        channel.on_table_change(table, callback, event_type)
        channel.subscribe()
        
        return channel
    
    def setup_conversation_listener(
        self,
        conversation_id: str,
        on_message: Callable[[Dict], None],
        on_user_join: Optional[Callable[[Dict], None]] = None,
        on_user_leave: Optional[Callable[[Dict], None]] = None
    ) -> RealtimeChannel:
        """Setup comprehensive conversation listener."""
        channel = self.create_conversation_channel(conversation_id)
        
        # Listen for new messages
        channel.on_table_change("messages", on_message, RealtimeEventType.INSERT)
        
        # Listen for presence changes if callbacks provided
        if on_user_join:
            channel.on_presence_join(on_user_join)
        
        if on_user_leave:
            channel.on_presence_leave(on_user_leave)
        
        channel.subscribe()
        return channel


# Global instance
_realtime_manager: Optional[SupabaseRealtimeManager] = None


def get_supabase_realtime_manager() -> SupabaseRealtimeManager:
    """Get global Supabase realtime manager instance."""
    global _realtime_manager
    
    if _realtime_manager is None:
        _realtime_manager = SupabaseRealtimeManager()
    
    return _realtime_manager


# Convenience functions for common operations
async def setup_conversation_realtime(
    conversation_id: str,
    on_new_message: Callable[[Dict], None],
    user_id: Optional[str] = None
):
    """Setup real-time listeners for a conversation."""
    manager = get_supabase_realtime_manager()
    
    # Setup message listener
    channel = manager.setup_conversation_listener(
        conversation_id=conversation_id,
        on_message=on_new_message
    )
    
    # Track user presence if user_id provided
    if user_id:
        channel.track_presence({
            "user_id": user_id,
            "online_at": str(asyncio.get_event_loop().time())
        })
    
    return channel


async def cleanup_conversation_realtime(conversation_id: str):
    """Cleanup real-time listeners for a conversation."""
    manager = get_supabase_realtime_manager()
    topic = f"conversation:{conversation_id}"
    manager.remove_channel(topic)