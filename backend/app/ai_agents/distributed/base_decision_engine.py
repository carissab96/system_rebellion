"""
Base Agent Decision Engine
===========================

STANDARD interface that ALL distributed agents MUST inherit from.
This ensures consistent communication patterns across the rebellion.

The personality stays in the LOGIC, not the STRUCTURE.
- Sir Hawkington can yeet his monocle
- Terry can spin his shell and chug energy drinks
- Bob can have wild ideas
- The Stick can consume paper bags

But they ALL use the same interface for:
- Analyzing metrics
- Making decisions
- Broadcasting results
- Handling callbacks

Pattern: BaseAgent -> DecisionEngine -> Redis pub/sub -> callback handler
"""

import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from .mixins import DistributedAgentMixin
from .message_protocol import AgentMessage, MessageType, Priority
from .resource_monitor import ResourceType
from .event_logger import get_event_logger, log_agent_startup, log_decision, EventType
from .behavior_tracker import get_behavior_tracker


logger = logging.getLogger(__name__)


class AgentDecisionEngine(DistributedAgentMixin, ABC):
    """
    Base decision engine that ALL agents inherit from.
    
    Provides standardized interface for:
    1. Metric analysis
    2. Decision making
    3. Broadcasting decisions
    4. Handling callbacks
    
    Subclasses implement personality-specific logic while maintaining
    consistent method signatures.
    
    Usage:
        class SirHawkingtonDistributed(AgentDecisionEngine, SirHawkingtonBrainV2):
            def __init__(self, db_getter=None):
                super().__init__(db_getter=db_getter)
                self.agent_name = "sir_hawkington"
                self.personality_traits = {...}
                self.resource_thresholds = {...}
            
            async def analyze_metrics(self, metrics_data, **kwargs):
                # Sir Hawkington's aristocratic logic here
                # Can yeet monocle, adjust thresholds, etc.
                pass
            
            async def _handle_coordination_request(self, message: AgentMessage):
                # Handle VIC-20's coordination
                pass
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize base decision engine.
        
        Subclasses MUST call super().__init__() and set:
        - self.agent_name
        - self.personality_traits
        - self.resource_thresholds
        """
        super().__init__(*args, **kwargs)
        
        # These MUST be set by subclasses
        if not hasattr(self, 'agent_name'):
            self.agent_name: str = "unknown"
        if not hasattr(self, 'personality_traits'):
            self.personality_traits: Dict[str, Any] = {}
        if not hasattr(self, 'resource_thresholds'):
            self.resource_thresholds: Dict[ResourceType, float] = {}
        
        # Standard tracking (all agents) - only set if not already defined
        if not hasattr(self, 'total_analyses'):
            self.total_analyses = 0
        if not hasattr(self, 'successful_analyses'):
            self.successful_analyses = 0
        # Don't set is_active - subclasses may define it as a property
        
        self._logger = logging.getLogger(f"DecisionEngine.{self.agent_name}")
    
    async def initialize_distributed(
        self,
        redis_client,
        enable_resource_monitoring: bool = False,  # Default False - only Hawk enables
        heartbeat_interval: int = 30,
        resource_check_interval: int = 60
    ):
        """
        Initialize distributed features and subscribe to standard channels.
        
        Subclasses can override to add custom subscriptions, but MUST
        call super().initialize_distributed(redis_client) first.
        
        Args:
            redis_client: Connected Redis client
            enable_resource_monitoring: Enable resource monitoring (default False)
            heartbeat_interval: Seconds between heartbeats
            resource_check_interval: Seconds between resource checks
        """
        await super().initialize_distributed(
            redis_client,
            enable_resource_monitoring=enable_resource_monitoring,
            heartbeat_interval=heartbeat_interval,
            resource_check_interval=resource_check_interval
        )
        
        # Standard subscriptions (all agents)
        await self._subscribe_to_standard_channels()
        
        # Log agent startup for research tracking
        await log_agent_startup(
            agent_name=self.agent_name,
            metadata={
                "personality_traits": self.personality_traits,
                "resource_thresholds": {str(k): v for k, v in self.resource_thresholds.items()},
                "initialization_time": str(self._get_current_time())
            }
        )
        
        self._logger.info(f"✅ {self.agent_name} decision engine initialized")
    
    async def _subscribe_to_standard_channels(self):
        """
        Subscribe to standard message types that all agents should handle.
        
        Subclasses can override to customize, but should call super() first.
        """
        try:
            # All agents should handle coordination requests from VIC-20
            await self.subscribe_to_messages(
                message_type=MessageType.COORDINATION_REQUEST,
                callback=self._handle_coordination_request
            )
            
            # All agents should handle emergencies
            await self.subscribe_to_messages(
                message_type=MessageType.EMERGENCY,
                callback=self._handle_emergency
            )
            
            self._logger.info(f"📡 Subscribed to standard channels")
            
        except Exception as e:
            self._logger.error(f"❌ Failed to subscribe to standard channels: {e}")
    
    @abstractmethod
    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Analyze metrics and make decisions.
        
        This is where personality-specific logic lives:
        - Sir Hawkington: Aristocratic triage with monocle-yeeting
        - Terry: Hyperactive optimization with shell-spinning
        - Hamsters: Telepathic consensus with beer-powered decisions
        - QSP: Paranoid security analysis with tequila shots
        - VIC-20: Sage coordination with pattern matching
        - The Stick: Patient learning with paper bag consumption
        
        Args:
            metrics_data: System metrics to analyze
            historical_data: Historical metrics for trend analysis
            user_context: User context information
            user_id: User ID for tracking
            **kwargs: Agent-specific parameters
            
        Returns:
            Agent-specific decision object
        """
        pass
    
    async def make_decision_and_broadcast(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        confidence: float,
        reasoning: str,
        broadcast: bool = True,
        priority: Priority = Priority.NORMAL
    ) -> Dict[str, Any]:
        """
        Make a decision, record it, and optionally broadcast to other agents.
        
        Standard pattern for all agents:
        1. Record decision in distributed state
        2. Broadcast to other agents if requested
        3. Return decision record
        
        Args:
            decision_type: Type of decision
            input_data: Input data for decision
            output_data: Output/result data
            confidence: Confidence level (0.0 to 1.0)
            reasoning: Human-readable reasoning
            broadcast: Whether to broadcast to other agents
            priority: Message priority if broadcasting
            
        Returns:
            Decision record
        """
        # Record decision
        decision = await self.make_distributed_decision(
            decision_type=decision_type,
            input_data=input_data,
            output_data=output_data,
            confidence=confidence,
            reasoning=reasoning
        )
        
        # Log decision for research tracking
        await log_decision(
            agent_name=self.agent_name,
            decision_type=decision_type,
            decision_data={
                "confidence": confidence,
                "reasoning": reasoning,
                "input_summary": {k: str(v)[:100] for k, v in input_data.items()},
                "output_summary": {k: str(v)[:100] for k, v in output_data.items()}
            },
            was_override=False  # Subclasses can override this
        )
        
        # Log to The Stick if requested
        if broadcast and self.is_distributed:
            await self.send_to_agent(
                to_agent="the_stick",
                message_type=MessageType.DECISION_LOG,
                payload={
                    "decision_type": decision_type,
                    "agent": self.agent_name,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "output": output_data
                },
                priority=priority
            )
            
            self._logger.debug(f"📡 Decision broadcast: {decision_type}")
        
        return decision
    
    @abstractmethod
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle coordination requests from VIC-20.
        
        Standard signature for all agents. Personality logic inside:
        - Sir Hawkington: Aristocratic CPU throttling
        - Terry: Hyperactive cache clearing (usually ignores VIC-20!)
        - Hamsters: Telepathic disk cleanup with beer
        - QSP: Paranoid network throttling
        
        Args:
            message: AgentMessage with coordination request
        """
        pass
    
    async def _handle_emergency(self, message: AgentMessage) -> None:
        """
        Handle emergency messages.
        
        Default implementation logs and records. Subclasses can override
        for agent-specific emergency responses.
        
        Args:
            message: AgentMessage with emergency details
        """
        message_data = message.payload
        emergency_type = message_data.get('emergency_type', 'unknown')
        
        self._logger.warning(
            f"🚨 EMERGENCY: {emergency_type} from {message.from_agent}"
        )
        
        # Record emergency receipt
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="emergency_received",
                input_data={
                    "emergency_type": emergency_type,
                    "from_agent": message.from_agent,
                    "details": message_data
                },
                confidence=1.0,
                reasoning=f"Emergency alert received from {message.from_agent}"
            )
    
    async def _handle_resource_alert(self, alert) -> None:
        """
        Handle resource alerts from the monitor.
        
        Default implementation logs. Subclasses SHOULD override for
        agent-specific resource handling.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        resource_type = alert.payload['resource_type']
        
        self._logger.warning(
            f"⚠️ Resource alert: {resource_type} at {current_value:.1f}% "
            f"(threshold: {threshold:.1f}%) - severity: {severity}"
        )
        
        # Record alert
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type=f"resource_alert_{resource_type}",
                input_data={
                    "resource_type": resource_type,
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,
                reasoning=f"{resource_type} usage at {current_value:.1f}% exceeds threshold"
            )
    
    def _get_current_time(self) -> datetime:
        """
        Get current time with timezone.
        
        Returns:
            Current datetime with UTC timezone
        """
        return datetime.now(timezone.utc)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get agent status including distributed state.
        
        Subclasses can override to add agent-specific status fields,
        but should call super().get_agent_status() and extend the result.
        
        Returns:
            Status dictionary
        """
        distributed_state = self.get_distributed_state()
        
        status = {
            "agent_name": self.agent_name,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "personality_traits": self.personality_traits,
            "distributed": distributed_state
        }
        
        # Add is_active if it exists (may be a property in subclasses)
        if hasattr(self, 'is_active'):
            status["is_active"] = self.is_active
        
        return status
    
    def __repr__(self):
        """Standard string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<{self.__class__.__name__} "
            f"agent={self.agent_name} "
            f"analyses={self.total_analyses} "
            f"| {dist_status}>"
        )
