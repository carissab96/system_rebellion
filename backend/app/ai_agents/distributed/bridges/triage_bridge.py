"""
Triage Bridge (Task 3.4)
========================

Routes triage decisions from Sir Hawkington to the appropriate agents
(The Stick and VIC-20) and tracks routing statistics.

The Triage Bridge sits between the triage engine and the distributed agents,
ensuring reliable delivery and providing visibility into triage flow.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass, field

from ..message_protocol import MessageType, Priority, RedisChannels
from ..communication import MessageBus


logger = logging.getLogger(__name__)


@dataclass
class TriageRoutingStats:
    """Statistics for triage routing"""
    total_decisions: int = 0
    decisions_by_severity: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    decisions_by_routing: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    average_delivery_time_ms: float = 0.0
    last_decision_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "total_decisions": self.total_decisions,
            "decisions_by_severity": dict(self.decisions_by_severity),
            "decisions_by_routing": dict(self.decisions_by_routing),
            "successful_deliveries": self.successful_deliveries,
            "failed_deliveries": self.failed_deliveries,
            "average_delivery_time_ms": self.average_delivery_time_ms,
            "last_decision_time": self.last_decision_time,
            "success_rate": (
                self.successful_deliveries / self.total_decisions * 100
                if self.total_decisions > 0 else 0.0
            )
        }


class TriageBridge:
    """
    Bridge for routing triage decisions to distributed agents.
    
    Responsibilities:
    - Subscribe to triage decision channel
    - Route decisions to The Stick and VIC-20
    - Track routing statistics
    - Provide health monitoring
    - Generate triage flow visualization data
    """
    
    def __init__(self, redis_client, agent_manager=None):
        """
        Initialize the triage bridge.
        
        Args:
            redis_client: Redis client for pub/sub
            agent_manager: Optional agent manager for direct routing
        """
        self.redis_client = redis_client
        self.agent_manager = agent_manager
        
        # Message bus for pub/sub
        self.message_bus = MessageBus(redis_client, "triage_bridge")
        
        # Statistics
        self.stats = TriageRoutingStats()
        self._delivery_times: List[float] = []
        
        # Health
        self.is_running = False
        self._last_heartbeat = None
        
        self.logger = logging.getLogger("TriageBridge")
    
    async def start(self):
        """Start the triage bridge"""
        self.logger.info("🌉 Starting Triage Bridge...")
        
        # Start message bus
        await self.message_bus.start()
        
        # Subscribe to triage decisions
        self.message_bus.register_handler(
            MessageType.TRIAGE_DECISION,
            self._handle_triage_decision
        )
        
        self.is_running = True
        self._last_heartbeat = datetime.now(timezone.utc)
        
        self.logger.info("🌉✅ Triage Bridge started and listening for decisions")
    
    async def stop(self):
        """Stop the triage bridge"""
        self.logger.info("🌉 Stopping Triage Bridge...")
        
        self.is_running = False
        
        # Stop message bus
        await self.message_bus.stop()
        
        # Log final statistics
        self.logger.info(f"🌉📊 Final stats: {self.stats.to_dict()}")
        self.logger.info("🌉✅ Triage Bridge stopped")
    
    async def _handle_triage_decision(self, message_data: Dict[str, Any]):
        """
        Handle incoming triage decision and route to appropriate agents.
        
        Args:
            message_data: Triage decision data from Sir Hawkington
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            severity = message_data.get('severity', 'unknown')
            routing = message_data.get('routing', 'unknown')
            target_agents = message_data.get('target_agents', [])
            
            self.logger.info(
                f"🌉📬 Triage decision received: {severity} → {routing} "
                f"(targets: {', '.join(target_agents)})"
            )
            
            # Update statistics
            self.stats.total_decisions += 1
            self.stats.decisions_by_severity[severity] += 1
            self.stats.decisions_by_routing[routing] += 1
            self.stats.last_decision_time = datetime.now(timezone.utc).isoformat()
            
            # Route to target agents
            success = await self._route_to_agents(target_agents, message_data)
            
            if success:
                self.stats.successful_deliveries += 1
                
                # Track delivery time
                delivery_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                self._delivery_times.append(delivery_time_ms)
                
                # Keep only last 100 delivery times for average
                if len(self._delivery_times) > 100:
                    self._delivery_times.pop(0)
                
                self.stats.average_delivery_time_ms = sum(self._delivery_times) / len(self._delivery_times)
                
                self.logger.debug(
                    f"🌉✅ Routed successfully in {delivery_time_ms:.2f}ms "
                    f"(avg: {self.stats.average_delivery_time_ms:.2f}ms)"
                )
            else:
                self.stats.failed_deliveries += 1
                self.logger.error(f"🌉❌ Failed to route decision to agents")
            
            # Update heartbeat
            self._last_heartbeat = datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"🌉💥 Error handling triage decision: {e}", exc_info=True)
            self.stats.failed_deliveries += 1
    
    async def _route_to_agents(
        self,
        target_agents: List[str],
        message_data: Dict[str, Any]
    ) -> bool:
        """
        Route triage decision to target agents.
        
        Args:
            target_agents: List of agent names to route to
            message_data: Triage decision data
            
        Returns:
            True if routing successful
        """
        try:
            # The Stick and VIC-20 should always receive triage decisions
            # (per the architecture documented in TRIAGE_ARCHITECTURE.md)
            recipients = set()
            
            if 'the_stick' in target_agents or 'all' in target_agents:
                recipients.add('the_stick')
            
            if 'vic_20_sage' in target_agents or 'all' in target_agents:
                recipients.add('vic_20_sage')
            
            # Also check routing type
            routing = message_data.get('routing', '')
            if 'vic20' in routing.lower():
                recipients.add('vic_20_sage')
            
            if 'stick' in routing.lower():
                recipients.add('the_stick')
            
            if not recipients:
                self.logger.warning(
                    f"🌉⚠️  No recipients determined for routing: {routing}, "
                    f"targets: {target_agents}"
                )
                # Default: send to both The Stick and VIC-20
                recipients = {'the_stick', 'vic_20_sage'}
            
            # Broadcast to recipients
            for agent_name in recipients:
                channel = RedisChannels.agent_specific(agent_name)
                await self.redis_client.publish(
                    channel,
                    str(message_data)  # Will be properly serialized by message bus
                )
                self.logger.debug(f"🌉📤 Routed to {agent_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"🌉💥 Error routing to agents: {e}", exc_info=True)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current routing statistics"""
        return self.stats.to_dict()
    
    def get_health(self) -> Dict[str, Any]:
        """Get bridge health status"""
        now = datetime.now(timezone.utc)
        
        # Check if heartbeat is recent (within last 60 seconds)
        is_healthy = False
        seconds_since_heartbeat = None
        
        if self._last_heartbeat:
            seconds_since_heartbeat = (now - self._last_heartbeat).total_seconds()
            is_healthy = seconds_since_heartbeat < 60
        
        return {
            "is_running": self.is_running,
            "is_healthy": is_healthy,
            "last_heartbeat": self._last_heartbeat.isoformat() if self._last_heartbeat else None,
            "seconds_since_heartbeat": seconds_since_heartbeat,
            "total_decisions_routed": self.stats.total_decisions,
            "success_rate": (
                self.stats.successful_deliveries / self.stats.total_decisions * 100
                if self.stats.total_decisions > 0 else 0.0
            )
        }
    
    def get_flow_visualization_data(self) -> Dict[str, Any]:
        """
        Get data for visualizing triage flow.
        
        Returns data suitable for frontend visualization of:
        - Decision volume by severity
        - Routing patterns
        - Success rates
        - Delivery performance
        """
        return {
            "overview": {
                "total_decisions": self.stats.total_decisions,
                "success_rate": (
                    self.stats.successful_deliveries / self.stats.total_decisions * 100
                    if self.stats.total_decisions > 0 else 0.0
                ),
                "average_delivery_time_ms": self.stats.average_delivery_time_ms
            },
            "severity_distribution": dict(self.stats.decisions_by_severity),
            "routing_distribution": dict(self.stats.decisions_by_routing),
            "delivery_stats": {
                "successful": self.stats.successful_deliveries,
                "failed": self.stats.failed_deliveries,
                "total": self.stats.total_decisions
            },
            "last_activity": self.stats.last_decision_time,
            "health": self.get_health()
        }


# Convenience function for creating and starting a triage bridge
async def create_triage_bridge(redis_client, agent_manager=None) -> TriageBridge:
    """
    Create and start a triage bridge.
    
    Args:
        redis_client: Redis client
        agent_manager: Optional agent manager
        
    Returns:
        Started TriageBridge instance
    """
    bridge = TriageBridge(redis_client, agent_manager)
    await bridge.start()
    return bridge
