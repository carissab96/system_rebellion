"""
Agent Communication Hub
=======================

Redis pub/sub based communication system for distributed agents.
Enables real-time message passing, event broadcasting, and agent coordination.

Features:
- Pub/sub message routing
- Message filtering and routing
- Subscription management
- Message archiving
- Circuit breaker integration
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime, timezone
import json

from .message_protocol import (
    AgentMessage,
    MessageType,
    Priority,
    RedisChannels,
    RedisKeys
)
from .agent_state import AgentStateManager, AgentHealth

logger = logging.getLogger(__name__)


class MessageBus:
    """
    Redis pub/sub message bus for agent communication.
    
    Handles message publishing, subscription, and routing across the distributed network.
    """
    
    def __init__(self, redis_client, agent_name: str):
        """
        Initialize message bus.
        
        Args:
            redis_client: Redis client instance
            agent_name: Name of this agent
        """
        self.redis = redis_client
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"MessageBus.{agent_name}")
        
        # Subscription management
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._pubsub = None
        self._listener_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Message handlers by type
        self._handlers: Dict[MessageType, List[Callable]] = {}
        
        # Statistics
        self._messages_sent = 0
        self._messages_received = 0
    
    async def start(self):
        """Start the message bus and begin listening"""
        if self._running:
            self.logger.warning("Message bus already running")
            return
        
        try:
            self._pubsub = self.redis.pubsub()
            self._running = True
            
            # Subscribe to agent-specific channel
            await self.subscribe(RedisChannels.agent_specific(self.agent_name))
            
            # Subscribe to broadcast channel
            await self.subscribe(RedisChannels.broadcast())
            
            # Start listener task
            self._listener_task = asyncio.create_task(self._listen_loop())
            
            self.logger.info(f"Message bus started for {self.agent_name}")
        except Exception as e:
            self.logger.error(f"Failed to start message bus: {e}")
            self._running = False
            raise
    
    async def stop(self):
        """Stop the message bus"""
        self._running = False
        
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
        
        self.logger.info(f"Message bus stopped for {self.agent_name}")
    
    async def subscribe(self, channel: str):
        """
        Subscribe to a Redis channel.
        
        Args:
            channel: Channel name to subscribe to
        """
        if not self._pubsub:
            raise RuntimeError("Message bus not started")
        
        await self._pubsub.subscribe(channel)
        self.logger.info(f"Subscribed to channel: {channel}")
    
    async def unsubscribe(self, channel: str):
        """
        Unsubscribe from a Redis channel.
        
        Args:
            channel: Channel name to unsubscribe from
        """
        if self._pubsub:
            await self._pubsub.unsubscribe(channel)
            self.logger.info(f"Unsubscribed from channel: {channel}")
    
    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[AgentMessage], Awaitable[None]]
    ):
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to call when message is received
        """
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        
        self._handlers[message_type].append(handler)
        self.logger.debug(f"Registered handler for {message_type.value}")
    
    async def publish(
        self,
        message: AgentMessage,
        channel: Optional[str] = None
    ) -> bool:
        """
        Publish a message to Redis.
        
        Args:
            message: AgentMessage to publish
            channel: Optional specific channel (auto-determined if None)
            
        Returns:
            True if successful
        """
        try:
            # Determine channel if not specified
            if channel is None:
                if message.to_agent:
                    channel = RedisChannels.agent_specific(message.to_agent)
                elif message.message_type == MessageType.EMERGENCY:
                    channel = RedisChannels.emergency()
                elif message.message_type == MessageType.RESOURCE_ALERT:
                    channel = RedisChannels.resource_alerts()
                elif message.message_type in [MessageType.DECISION_REQUEST, MessageType.DECISION_RESPONSE]:
                    channel = RedisChannels.decisions()
                elif message.message_type == MessageType.AGENT_HEARTBEAT:
                    channel = RedisChannels.heartbeats()
                else:
                    channel = RedisChannels.broadcast()
            
            # Publish message
            await self.redis.publish(channel, message.to_json())
            
            # Archive message
            await self._archive_message(message)
            
            self._messages_sent += 1
            self.logger.info(
                f"📡 REDIS PUB: {message.message_type.value} → {channel} "
                f"| from={message.from_agent} | priority={message.priority.value} | id={message.message_id[:8]}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            return False
    
    async def send_to_agent(
        self,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL
    ) -> bool:
        """
        Send a message to a specific agent.
        
        Args:
            to_agent: Target agent name
            message_type: Type of message
            payload: Message payload
            priority: Message priority
            
        Returns:
            True if successful
        """
        message = AgentMessage(
            from_agent=self.agent_name,
            to_agent=to_agent,
            message_type=message_type,
            priority=priority,
            payload=payload
        )
        return await self.publish(message)
    
    async def broadcast(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL
    ) -> bool:
        """
        Broadcast a message to all agents.
        
        Args:
            message_type: Type of message
            payload: Message payload
            priority: Message priority
            
        Returns:
            True if successful
        """
        message = AgentMessage(
            from_agent=self.agent_name,
            to_agent=None,  # Broadcast
            message_type=message_type,
            priority=priority,
            payload=payload
        )
        return await self.publish(message, channel=RedisChannels.broadcast())
    
    async def _listen_loop(self):
        """Background task to listen for messages"""
        self.logger.info("Message listener started")
        
        try:
            while self._running:
                try:
                    message = await self._pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=1.0
                    )
                    
                    if message and message['type'] == 'message':
                        await self._handle_message(message['data'])
                    
                    await asyncio.sleep(0.01)  # Small delay to prevent tight loop
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in listen loop: {e}")
                    await asyncio.sleep(1.0)  # Back off on error
        
        finally:
            self.logger.info("Message listener stopped")
    
    async def _handle_message(self, data: str):
        """
        Handle incoming message.
        
        Args:
            data: JSON string of AgentMessage
        """
        try:
            message = AgentMessage.from_json(data)
            
            # Skip our own messages
            if message.from_agent == self.agent_name:
                return
            
            # Skip messages not for us (if targeted)
            if message.to_agent and message.to_agent != self.agent_name:
                return
            
            self._messages_received += 1
            
            self.logger.debug(
                f"Received {message.message_type.value} from {message.from_agent} "
                f"(id: {message.message_id})"
            )
            
            # Call registered handlers
            if message.message_type in self._handlers:
                for handler in self._handlers[message.message_type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        self.logger.error(
                            f"Handler error for {message.message_type.value}: {e}"
                        )
        
        except Exception as e:
            self.logger.error(f"Failed to handle message: {e}")
    
    async def _archive_message(self, message: AgentMessage):
        """
        Archive message to Redis for history/debugging.
        
        Args:
            message: Message to archive
        """
        try:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            key = RedisKeys.message_archive(date_str)
            
            # Store in list with TTL
            await self.redis.lpush(key, message.to_json())
            await self.redis.ltrim(key, 0, 9999)  # Keep last 10k messages per day
            await self.redis.expire(key, 86400 * 7)  # 7 day TTL
            
        except Exception as e:
            self.logger.warning(f"Failed to archive message: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "is_running": self._running,
            "subscribed_channels": len(self._subscriptions),
            "registered_handlers": sum(len(h) for h in self._handlers.values())
        }


class AgentCommunicationHub:
    """
    High-level communication hub for an agent.
    
    Combines MessageBus and AgentStateManager for complete agent communication.
    """
    
    def __init__(
        self,
        redis_client,
        agent_name: str,
        agent_role: str,
        personality_traits: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize communication hub.
        
        Args:
            redis_client: Redis client instance
            agent_name: Name of this agent
            agent_role: Role description
            personality_traits: Agent personality configuration
        """
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.personality_traits = personality_traits or {}
        
        self.message_bus = MessageBus(redis_client, agent_name)
        self.state_manager = AgentStateManager(redis_client, agent_name)
        
        self.logger = logging.getLogger(f"CommHub.{agent_name}")
        self._state = None
    
    async def initialize(self):
        """Initialize the communication hub"""
        # Load or create state
        self._state = await self.state_manager.load_state()
        
        if not self._state:
            self.logger.info(f"Creating initial state for {self.agent_name}")
            self._state = await self.state_manager.create_initial_state(
                agent_role=self.agent_role,
                personality_traits=self.personality_traits
            )
        else:
            self.logger.info(f"Restored state for {self.agent_name}")
            # Reset health to STARTING on restart (was SHUTTING_DOWN from previous run)
            await self.state_manager.update_health(AgentHealth.STARTING)
            await self.state_manager.mark_restart()
        
        # Start message bus
        await self.message_bus.start()
        
        # Send startup broadcast
        await self.message_bus.broadcast(
            MessageType.AGENT_STATE_CHANGE,
            {
                "event": "agent_started",
                "agent_name": self.agent_name,
                "agent_role": self.agent_role,
                "restart_count": self._state.restart_count
            },
            priority=Priority.HIGH
        )
        
        self.logger.info(f"Communication hub initialized for {self.agent_name}")
    
    async def shutdown(self):
        """Shutdown the communication hub"""
        # Send shutdown broadcast
        await self.message_bus.broadcast(
            MessageType.AGENT_STATE_CHANGE,
            {
                "event": "agent_stopping",
                "agent_name": self.agent_name
            },
            priority=Priority.HIGH
        )
        
        # Stop message bus
        await self.message_bus.stop()
        
        # Save final state
        if self._state:
            await self.state_manager.save_state(self._state)
        
        self.logger.info(f"Communication hub shutdown for {self.agent_name}")
    
    def register_message_handler(
        self,
        message_type: MessageType,
        handler: Callable[[AgentMessage], Awaitable[None]]
    ):
        """Register a message handler"""
        self.message_bus.register_handler(message_type, handler)
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message"""
        success = await self.message_bus.publish(message)
        if success:
            await self.state_manager.update_metrics(messages_sent=1)
        return success
    
    async def send_heartbeat(self) -> bool:
        """Send a heartbeat message to indicate agent is alive"""
        from .message_protocol import HeartbeatMessage
        
        agent_status = {
            "status": "alive",
            "uptime": self._state.uptime_seconds if self._state else 0,
            "health": self._state.health.value if self._state else "unknown"
        }
        
        heartbeat = HeartbeatMessage(
            from_agent=self.agent_name,
            agent_status=agent_status
        )
        
        success = await self.message_bus.publish(heartbeat)
        if success and self._state:
            self._state.update_heartbeat()
            await self.state_manager.save_state(self._state)
        
        return success
    
    async def broadcast_message(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL
    ) -> bool:
        """Broadcast a message to all agents (wrapper for message_bus.broadcast)"""
        success = await self.message_bus.broadcast(message_type, payload, priority)
        if success:
            await self.state_manager.update_metrics(messages_sent=1)
        return success
    
    async def make_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        confidence: float,
        reasoning: str = "",
        triage_severity: Optional[str] = None,
        triage_routing: Optional[str] = None,
        coordination_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a decision in the agent's history (Task 3.3).
        
        Args:
            decision_type: Type of decision
            input_data: Input data for decision
            output_data: Output/result data
            confidence: Confidence level (0-1)
            reasoning: Optional reasoning
            triage_severity: Optional triage severity
            triage_routing: Optional triage routing
            coordination_id: Optional coordination ID
            
        Returns:
            Decision record as dict
        """
        from .agent_state import DecisionRecord
        import uuid
        
        # Create decision record
        decision_id = f"{self.agent_name}_{uuid.uuid4().hex[:8]}"
        
        record = DecisionRecord(
            decision_id=decision_id,
            agent_name=self.agent_name,
            decision_type=decision_type,
            input_data=input_data,
            output_data=output_data,
            confidence=confidence,
            triggered_by=reasoning,
            triage_severity=triage_severity,
            triage_routing=triage_routing,
            coordination_id=coordination_id
        )
        
        # Record in state manager
        await self.state_manager.record_decision(record)
        
        return {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "confidence": confidence,
            "triage_severity": triage_severity,
            "triage_routing": triage_routing
        }
    
    def get_state(self):
        """Get current agent state"""
        return self._state
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        bus_stats = self.message_bus.get_stats()
        
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "health": self._state.health.value if self._state else "unknown",
            "uptime_seconds": self._state.calculate_uptime() if self._state else 0,
            "total_decisions": self._state.total_decisions if self._state else 0,
            "restart_count": self._state.restart_count if self._state else 0,
            **bus_stats
        }
