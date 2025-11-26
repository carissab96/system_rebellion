"""
Distributed Agent Base Class
=============================

Base class for agents with distributed consciousness capabilities.
Extends the existing BaseAIAgent with Redis communication, state persistence,
and resource monitoring.

Agents using this class gain:
- Continuous existence across restarts
- Inter-agent communication
- Resource monitoring
- Decision history tracking
- Personality-driven behavior
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime, timezone

from ..base_agent import BaseAIAgent
from .communication import AgentCommunicationHub, MessageBus
from .agent_state import AgentStateManager, AgentHealth, DecisionRecord
from .resource_monitor import ResourceMonitor, ResourceType, ResourceMetrics
from .message_protocol import (
    AgentMessage,
    MessageType,
    Priority,
    HeartbeatMessage,
    DecisionMessage
)

logger = logging.getLogger(__name__)


class DistributedAgent(BaseAIAgent):
    """
    Enhanced agent with distributed consciousness capabilities.
    
    Combines traditional agent functionality with:
    - Redis-based state persistence
    - Inter-agent communication
    - Resource monitoring
    - Decision history
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_role: str,
        redis_client,
        personality_traits: Optional[Dict[str, Any]] = None,
        monitored_resources: Optional[List[ResourceType]] = None,
        resource_check_interval: float = 5.0,
        heartbeat_interval: float = 30.0,
        version: str = "2.0"
    ):
        """
        Initialize distributed agent.
        
        Args:
            agent_name: Agent name
            agent_role: Agent role description
            redis_client: Redis client instance
            personality_traits: Agent personality configuration
            monitored_resources: Resources to monitor (None = all)
            resource_check_interval: Seconds between resource checks
            heartbeat_interval: Seconds between heartbeats
            version: Agent version
        """
        super().__init__(agent_name, version, agent_role)
        
        self.personality_traits = personality_traits or {}
        self.redis_client = redis_client
        
        # Initialize communication hub
        self.comm_hub = AgentCommunicationHub(
            redis_client=redis_client,
            agent_name=agent_name,
            agent_role=agent_role,
            personality_traits=personality_traits
        )
        
        # Initialize resource monitor
        self.resource_monitor = ResourceMonitor(
            agent_name=agent_name,
            message_bus=self.comm_hub.message_bus,
            monitored_resources=monitored_resources,
            check_interval=resource_check_interval
        )
        
        # Heartbeat configuration
        self.heartbeat_interval = heartbeat_interval
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        # Decision tracking
        self._decision_counter = 0
        
        self.logger.info(
            f"🌐 Distributed agent created: {agent_name} "
            f"(role: {agent_role}, personality: {list(personality_traits.keys())})"
        )
    
    async def initialize(self):
        """
        Initialize the distributed agent.
        
        Call this after creating the agent to start all systems.
        """
        # Initialize communication hub (loads state, starts message bus)
        await self.comm_hub.initialize()
        
        # Register message handlers
        self._register_default_handlers()
        
        # Register callback for own resource alerts
        self.resource_monitor.register_alert_callback(self._handle_own_resource_alert)
        
        # Start resource monitoring
        await self.resource_monitor.start()
        
        # Start heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Update health to healthy
        await self.comm_hub.state_manager.update_health(AgentHealth.HEALTHY)
        
        self.logger.info(f"✅ {self.agent_name} fully initialized and online")
    
    async def shutdown(self):
        """
        Gracefully shutdown the agent.
        
        Saves state, stops monitoring, and closes connections.
        """
        self.logger.info(f"🛑 Shutting down {self.agent_name}...")
        
        # Update health
        await self.comm_hub.state_manager.update_health(AgentHealth.SHUTTING_DOWN)
        
        # Stop heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Stop resource monitoring
        await self.resource_monitor.stop()
        
        # Shutdown communication hub (saves state, stops message bus)
        await self.comm_hub.shutdown()
        
        self.logger.info(f"✅ {self.agent_name} shutdown complete")
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        # Handle queries from other agents
        self.comm_hub.register_message_handler(
            MessageType.AGENT_QUERY,
            self._handle_agent_query
        )
        
        # Handle decision requests
        self.comm_hub.register_message_handler(
            MessageType.DECISION_REQUEST,
            self._handle_decision_request
        )
        
        # Handle resource alerts from other agents
        self.comm_hub.register_message_handler(
            MessageType.RESOURCE_ALERT,
            self._handle_resource_alert
        )
    
    async def _handle_agent_query(self, message: AgentMessage):
        """
        Handle query from another agent.
        
        Args:
            message: Query message
        """
        self.logger.info(f"Received query from {message.from_agent}")
        
        # Get current status
        status = self.get_agent_status()
        
        # Send response
        response = AgentMessage(
            from_agent=self.agent_name,
            to_agent=message.from_agent,
            message_type=MessageType.AGENT_RESPONSE,
            priority=Priority.NORMAL,
            payload=status,
            reply_to=message.message_id
        )
        
        await self.comm_hub.send_message(response)
    
    async def _handle_decision_request(self, message: AgentMessage):
        """
        Handle decision request from another agent.
        
        Override this in subclasses to implement agent-specific decision logic.
        
        Args:
            message: Decision request message
        """
        self.logger.info(
            f"Received decision request from {message.from_agent}: "
            f"{message.payload.get('decision_type')}"
        )
        
        # Default: acknowledge but don't make decision
        response = DecisionMessage(
            from_agent=self.agent_name,
            decision_type="response",
            decision_data={
                "status": "acknowledged",
                "note": "No specific decision logic implemented"
            },
            to_agent=message.from_agent,
            reply_to=message.message_id
        )
        
        await self.comm_hub.send_message(response)
    
    async def _handle_own_resource_alert(self, alert):
        """
        Handle resource alert from own monitoring.
        
        This is called when the agent's own resource monitor detects an issue.
        Broadcasts the alert to other agents and can trigger agent-specific logic.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        from .resource_monitor import ResourceAlert
        
        payload = alert.payload
        resource_type = payload.get('resource_type')
        current_value = payload.get('current_value')
        severity = payload.get('severity')
        
        self.logger.warning(
            f"🚨 {self.agent_name} detected {resource_type} at {current_value:.1f}% "
            f"(threshold: {payload.get('threshold')}%) - severity: {severity}"
        )
        
        # Broadcast alert to other agents (already done by resource monitor via message bus)
        # Subclasses can override this to add agent-specific responses
    
    async def _handle_resource_alert(self, message: AgentMessage):
        """
        Handle resource alert from another agent.
        
        Override this in subclasses to implement agent-specific responses.
        
        Args:
            message: Resource alert message
        """
        payload = message.payload
        self.logger.warning(
            f"Resource alert from {message.from_agent}: "
            f"{payload.get('resource_type')} at {payload.get('current_value')}% "
            f"(severity: {payload.get('severity')})"
        )
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        self.logger.info(f"Heartbeat started (interval: {self.heartbeat_interval}s)")
        
        try:
            while True:
                try:
                    # Get current status
                    status = self.get_agent_status()
                    
                    # Send heartbeat
                    heartbeat = HeartbeatMessage(
                        from_agent=self.agent_name,
                        agent_status=status
                    )
                    
                    await self.comm_hub.send_message(heartbeat)
                    
                    # Wait for next heartbeat
                    await asyncio.sleep(self.heartbeat_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Heartbeat error: {e}")
                    await asyncio.sleep(self.heartbeat_interval)
        
        finally:
            self.logger.info("Heartbeat stopped")
    
    async def make_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Make a decision and record it.
        
        Override this in subclasses to implement agent-specific decision logic.
        
        Args:
            decision_type: Type of decision
            input_data: Input data for decision
            confidence: Confidence level (0-1)
            
        Returns:
            Decision output
        """
        self._decision_counter += 1
        
        # Create decision record
        decision_id = f"{self.agent_name}_decision_{self._decision_counter}"
        
        # Default decision logic (override in subclasses)
        output_data = {
            "decision_id": decision_id,
            "status": "processed",
            "note": "Default decision logic"
        }
        
        # Record decision
        record = DecisionRecord(
            decision_id=decision_id,
            agent_name=self.agent_name,
            decision_type=decision_type,
            input_data=input_data,
            output_data=output_data,
            confidence=confidence
        )
        
        await self.comm_hub.state_manager.record_decision(record)
        
        # Broadcast decision if important
        if confidence > 0.7:
            decision_msg = DecisionMessage(
                from_agent=self.agent_name,
                decision_type="broadcast",
                decision_data=output_data,
                priority=Priority.NORMAL
            )
            await self.comm_hub.send_message(decision_msg)
        
        return output_data
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get comprehensive agent status.
        
        Returns:
            Status dictionary
        """
        state = self.comm_hub.get_state()
        metrics = self.resource_monitor.get_last_metrics()
        comm_stats = self.comm_hub.get_stats()
        
        status = {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "version": self.version,
            "personality_traits": self.personality_traits,
            "health": state.health.value if state else "unknown",
            "is_active": self.is_active,
            "uptime_seconds": state.calculate_uptime() if state else 0,
            "restart_count": state.restart_count if state else 0,
            "total_decisions": state.total_decisions if state else 0,
            "error_count": state.error_count if state else 0,
            "communication": comm_stats,
            "resource_monitoring": self.resource_monitor.get_stats()
        }
        
        # Add current resource metrics if available
        if metrics:
            status["current_resources"] = {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
                "hostname": metrics.hostname
            }
        
        return status
    
    async def process_metrics(
        self,
        metrics: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process metrics (required by BaseAIAgent).
        
        Override this in subclasses for agent-specific processing.
        
        Args:
            metrics: System metrics
            user_context: Optional user context
            
        Returns:
            Enhanced metrics
        """
        # Default implementation: add agent status
        enhanced = metrics.copy()
        enhanced["agent_status"] = self.get_agent_status()
        
        return enhanced
    
    async def send_message_to_agent(
        self,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL
    ) -> bool:
        """
        Send a message to another agent.
        
        Args:
            to_agent: Target agent name
            message_type: Type of message
            payload: Message payload
            priority: Message priority
            
        Returns:
            True if successful
        """
        return await self.comm_hub.message_bus.send_to_agent(
            to_agent, message_type, payload, priority
        )
    
    async def broadcast_message(
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
        return await self.comm_hub.message_bus.broadcast(
            message_type, payload, priority
        )
    
    def get_resource_metrics(self) -> Optional[ResourceMetrics]:
        """Get current resource metrics"""
        return self.resource_monitor.get_last_metrics()
    
    def set_resource_threshold(self, resource_type: ResourceType, threshold: float):
        """Set resource alert threshold"""
        self.resource_monitor.set_threshold(resource_type, threshold)
