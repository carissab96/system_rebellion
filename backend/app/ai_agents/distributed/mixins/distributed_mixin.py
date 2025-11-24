"""
Distributed Agent Mixin
=======================

Injects distributed consciousness capabilities into existing agents without
breaking their current functionality.

This mixin adds:
- Redis state persistence
- Inter-agent messaging via pub/sub
- Resource monitoring
- Decision history tracking
- Heartbeat and health monitoring
- Personality trait preservation

Usage:
    class MyAgentDistributed(DistributedAgentMixin, MyExistingAgent):
        def __init__(self):
            super().__init__()
            self.personality_traits = {"trait": "value"}
            self.resource_thresholds = {ResourceType.CPU: 70.0}
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime, timezone

from ..communication import AgentCommunicationHub
from ..resource_monitor import ResourceMonitor, ResourceType
from ..message_protocol import AgentMessage, MessageType, Priority, ResourceAlert


logger = logging.getLogger(__name__)


class DistributedAgentMixin:
    """
    Mixin to add distributed consciousness to existing agents.
    
    CRITICAL: This mixin preserves all existing agent functionality.
    It only ADDS capabilities, never removes or modifies existing behavior.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the mixin.
        
        IMPORTANT: This must be called BEFORE the main agent __init__
        when using multiple inheritance. Use super().__init__() to ensure
        proper MRO (Method Resolution Order).
        """
        # Call parent __init__ to maintain inheritance chain
        super().__init__(*args, **kwargs)
        
        # Distributed state (lazy initialized)
        self._distributed_initialized = False
        self._comm_hub: Optional[AgentCommunicationHub] = None
        self._resource_monitor: Optional[ResourceMonitor] = None
        self._redis_client = None
        
        # Configuration (set by subclasses)
        self.personality_traits: Dict[str, Any] = {}
        self.resource_thresholds: Dict[ResourceType, float] = {}
        
        # Distributed logger
        self._dist_logger = logging.getLogger(f"Distributed.{getattr(self, 'agent_name', 'unknown')}")
    
    @property
    def comm_hub(self) -> Optional[AgentCommunicationHub]:
        """Get the communication hub (lazy init)"""
        return self._comm_hub
    
    @property
    def resource_monitor(self) -> Optional[ResourceMonitor]:
        """Get the resource monitor (lazy init)"""
        return self._resource_monitor
    
    @property
    def is_distributed(self) -> bool:
        """Check if distributed features are initialized"""
        return self._distributed_initialized
    
    async def initialize_distributed(
        self,
        redis_client,
        enable_resource_monitoring: bool = True,
        heartbeat_interval: int = 30,
        resource_check_interval: int = 60
    ) -> None:
        """
        Initialize distributed consciousness features.
        
        This should be called AFTER the agent's normal initialization.
        It's safe to call multiple times (idempotent).
        
        Args:
            redis_client: Connected Redis client (aioredis)
            enable_resource_monitoring: Enable resource monitoring
            heartbeat_interval: Seconds between heartbeats
            resource_check_interval: Seconds between resource checks
        """
        if self._distributed_initialized:
            self._dist_logger.debug("Distributed features already initialized")
            return
        
        try:
            self._dist_logger.info("🌐 Initializing distributed consciousness...")
            
            # Store Redis client
            self._redis_client = redis_client
            
            # Get agent name and role (from existing agent)
            agent_name = getattr(self, 'agent_name', 'unknown_agent')
            agent_role = getattr(self, 'agent_role', 'AI Agent')
            
            # Initialize communication hub
            self._comm_hub = AgentCommunicationHub(
                redis_client=redis_client,
                agent_name=agent_name,
                agent_role=agent_role,
                personality_traits=self.personality_traits
            )
            await self._comm_hub.initialize()
            
            # Set personality traits in state
            if self.personality_traits:
                state = self._comm_hub.get_state()
                state.personality_traits = self.personality_traits
                await self._comm_hub.state_manager.save_state(state)
            
            # Initialize resource monitoring if enabled
            if enable_resource_monitoring:
                self._resource_monitor = ResourceMonitor(
                    agent_name=agent_name,
                    message_bus=self._comm_hub.message_bus,
                    check_interval=resource_check_interval
                )
                
                # Set resource thresholds
                for resource_type, threshold in self.resource_thresholds.items():
                    self._resource_monitor.set_threshold(resource_type, threshold)
                
                # Register alert callback
                self._resource_monitor.register_alert_callback(
                    self._handle_resource_alert
                )
                
                # Start monitoring
                await self._resource_monitor.start()
            
            # Start heartbeat
            self._heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(heartbeat_interval)
            )
            
            self._distributed_initialized = True
            self._dist_logger.info("✅ Distributed consciousness initialized")
            
        except Exception as e:
            self._dist_logger.error(f"❌ Failed to initialize distributed features: {e}", exc_info=True)
            raise
    
    async def shutdown_distributed(self) -> None:
        """
        Shutdown distributed features cleanly.
        
        Saves state, stops monitoring, closes connections.
        Safe to call even if not initialized.
        """
        if not self._distributed_initialized:
            return
        
        try:
            self._dist_logger.info("🌐 Shutting down distributed consciousness...")
            
            # Cancel heartbeat
            if hasattr(self, '_heartbeat_task'):
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            # Stop resource monitoring
            if self._resource_monitor:
                await self._resource_monitor.stop()
            
            # Shutdown communication hub (saves state)
            if self._comm_hub:
                await self._comm_hub.shutdown()
            
            self._distributed_initialized = False
            self._dist_logger.info("✅ Distributed consciousness shutdown complete")
            
        except Exception as e:
            self._dist_logger.error(f"❌ Error during distributed shutdown: {e}", exc_info=True)
    
    async def _heartbeat_loop(self, interval: int) -> None:
        """
        Send periodic heartbeats to maintain presence.
        
        Args:
            interval: Seconds between heartbeats
        """
        while True:
            try:
                await asyncio.sleep(interval)
                
                if self._comm_hub:
                    await self._comm_hub.send_heartbeat()
                    self._dist_logger.debug("💓 Heartbeat sent")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._dist_logger.error(f"❌ Heartbeat error: {e}")
    
    async def _handle_resource_alert(self, alert: ResourceAlert) -> None:
        """
        Handle resource alerts from the monitor.
        
        This is a default implementation. Subclasses should override
        to implement agent-specific resource handling.
        
        Args:
            alert: Resource alert message
        """
        self._dist_logger.warning(
            f"⚠️ Resource alert: {alert.payload['resource_type']} at "
            f"{alert.payload['current_value']:.1f}% "
            f"(threshold: {alert.payload['threshold']:.1f}%) - "
            f"severity: {alert.payload['severity']}"
        )
        
        # Default: just log it
        # Subclasses override this to take action
    
    async def make_distributed_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        confidence: float,
        reasoning: str = "",
        output_data: Optional[Dict[str, Any]] = None,
        triage_severity: Optional[str] = None,
        triage_routing: Optional[str] = None,
        coordination_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a decision and record it in distributed state.
        
        This wraps the agent's existing decision-making with distributed tracking.
        
        Args:
            decision_type: Type of decision being made
            input_data: Input data for the decision
            confidence: Confidence level (0.0 to 1.0)
            reasoning: Optional reasoning for the decision
            output_data: Optional output/result data
            triage_severity: Optional triage severity (Task 3.3)
            triage_routing: Optional triage routing (Task 3.3)
            coordination_id: Optional coordination ID (Task 3.3)
            
        Returns:
            Decision record
        """
        if not self._comm_hub:
            raise RuntimeError("Distributed features not initialized")
        
        decision = await self._comm_hub.make_decision(
            decision_type=decision_type,
            input_data=input_data,
            output_data=output_data or {},
            confidence=confidence,
            reasoning=reasoning,
            triage_severity=triage_severity,
            triage_routing=triage_routing,
            coordination_id=coordination_id
        )
        
        self._dist_logger.info(
            f"📊 Decision recorded: {decision_type} "
            f"(confidence: {confidence:.2f})"
        )
        
        return decision
    
    async def broadcast_to_agents(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Broadcast a message to all other agents.
        
        Args:
            message_type: Type of message
            payload: Message payload
            priority: Message priority
        """
        if not self._comm_hub:
            raise RuntimeError("Distributed features not initialized")
        
        await self._comm_hub.broadcast_message(
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        
        self._dist_logger.debug(f"📡 Broadcast sent: {message_type.value}")
    
    async def send_to_agent(
        self,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Send a message to a specific agent.
        
        Args:
            to_agent: Target agent name
            message_type: Type of message
            payload: Message payload
            priority: Message priority
        """
        if not self._comm_hub:
            raise RuntimeError("Distributed features not initialized")
        
        await self._comm_hub.send_message(
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        
        self._dist_logger.debug(f"📨 Message sent to {to_agent}: {message_type.value}")
    
    async def subscribe_to_messages(
        self,
        message_type: MessageType,
        callback: Callable[[AgentMessage], Awaitable[None]]
    ) -> None:
        """
        Subscribe to messages of a specific type.
        
        Args:
            message_type: Type of messages to subscribe to
            callback: Async callback function to handle messages
        """
        if not self._comm_hub:
            raise RuntimeError("Distributed features not initialized")
        
        # Register the handler for this message type
        self._comm_hub.message_bus.register_handler(message_type, callback)
        
        self._dist_logger.info(f"📬 Subscribed to {message_type.value} messages")
    
    def get_distributed_state(self) -> Dict[str, Any]:
        """
        Get current distributed state.
        
        Returns:
            State dictionary including:
            - Agent health
            - Decision count
            - Message counts
            - Uptime
            - Personality traits
            - Resource monitoring status
        """
        if not self._comm_hub:
            return {
                "distributed_enabled": False,
                "message": "Distributed features not initialized"
            }
        
        state = self._comm_hub.get_state()
        
        return {
            "distributed_enabled": True,
            "agent_name": state.agent_name,
            "health": state.health.value,
            "total_decisions": state.total_decisions,
            "total_messages_sent": state.total_messages_sent,
            "total_messages_received": state.total_messages_received,
            "uptime_seconds": state.calculate_uptime(),
            "restart_count": state.restart_count,
            "personality_traits": state.personality_traits,
            "last_heartbeat": state.last_heartbeat,
            "resource_monitoring_enabled": self._resource_monitor is not None,
            "resource_monitoring_active": self._resource_monitor.is_running if self._resource_monitor else False
        }
    
    async def get_recent_decisions(self, count: int = 10) -> list:
        """
        Get recent decisions from distributed state.
        
        Args:
            count: Number of recent decisions to retrieve
            
        Returns:
            List of decision records
        """
        if not self._comm_hub:
            return []
        
        decisions = await self._comm_hub.state_manager.get_recent_decisions(count)
        return [d.to_dict() for d in decisions]
    
    def __repr__(self):
        """String representation including distributed status"""
        base_repr = super().__repr__() if hasattr(super(), '__repr__') else f"<{self.__class__.__name__}>"
        dist_status = "DISTRIBUTED" if self._distributed_initialized else "LOCAL"
        return f"{base_repr[:-1]} | {dist_status}>"
