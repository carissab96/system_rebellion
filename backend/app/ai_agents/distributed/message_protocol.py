"""
System Rebellion: Distributed Agent Message Protocol
=====================================================

Redis-based message protocol for agent-to-agent communication across the distributed network.
Agents maintain personality, memory, and continuous existence through this nervous system.

🧐 Sir Hawkington: "A proper communication protocol ensures aristocratic coordination"
🐌 Terry the Meth Snail: "FAST MESSAGES GO BRRRRR"
🐹 Bob the Hamster: "Organized chaos, just how I like it"
👻 Quantum Shadow People: "We exist in all states simultaneously"
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List
import json
import uuid


class MessageType(Enum):
    """Types of messages agents can send"""
    # Resource monitoring
    RESOURCE_ALERT = "resource_alert"
    RESOURCE_STATUS = "resource_status"
    
    # Decision making
    DECISION_REQUEST = "decision_request"
    DECISION_RESPONSE = "decision_response"
    DECISION_BROADCAST = "decision_broadcast"
    
    # Agent coordination
    AGENT_HEARTBEAT = "agent_heartbeat"
    AGENT_STATE_CHANGE = "agent_state_change"
    AGENT_QUERY = "agent_query"
    AGENT_RESPONSE = "agent_response"
    
    # Triage and coordination (Task 3.4)
    TRIAGE_DECISION = "triage_decision"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_UPDATE = "coordination_update"
    
    # Memory and learning
    MEMORY_SHARE = "memory_share"
    PATTERN_DISCOVERED = "pattern_discovered"
    LEARNING_UPDATE = "learning_update"
    
    # System events
    SYSTEM_EVENT = "system_event"
    EMERGENCY = "emergency"


class Priority(Enum):
    """Message priority levels (matches existing RedisTaskQueue priorities)"""
    CRITICAL = 1    # System emergencies, resource exhaustion
    HIGH = 2        # Important decisions, urgent coordination
    NORMAL = 5      # Regular status updates, routine decisions
    LOW = 10        # Background learning, pattern sharing


@dataclass
class AgentMessage:
    """
    Base message structure for all agent communications.
    
    Every message flows through Redis and maintains full context for debugging
    and learning from past interactions.
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.AGENT_HEARTBEAT
    priority: Priority = Priority.NORMAL
    
    # Agent identification
    from_agent: str = ""  # e.g., "sir_hawkington"
    to_agent: Optional[str] = None  # None = broadcast to all
    
    # Timing
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None  # Optional message expiration
    
    # Content
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Context and tracing
    conversation_id: Optional[str] = None  # Link related messages
    reply_to: Optional[str] = None  # Reply to specific message
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Serialize message to JSON for Redis storage"""
        data = asdict(self)
        # Convert enums to strings
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Deserialize message from JSON"""
        data = json.loads(json_str)
        # Convert strings back to enums
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = Priority(data['priority'])
        return cls(**data)
    
    def to_redis_key(self) -> str:
        """Generate Redis key for this message"""
        return f"agent:message:{self.message_id}"


@dataclass
class ResourceAlert(AgentMessage):
    """
    Specialized message for resource monitoring alerts.
    
    Agents send these when they detect resource issues in their domain.
    """
    def __init__(
        self,
        from_agent: str,
        resource_type: str,  # "cpu", "memory", "disk", "network"
        current_value: float,
        threshold: float,
        severity: str,  # "warning", "critical", "emergency"
        **kwargs
    ):
        # Extract host from kwargs before passing to parent
        host = kwargs.pop("host", "unknown")
        
        super().__init__(
            message_type=MessageType.RESOURCE_ALERT,
            from_agent=from_agent,
            priority=Priority.CRITICAL if severity == "emergency" else Priority.HIGH,
            payload={
                "resource_type": resource_type,
                "current_value": current_value,
                "threshold": threshold,
                "severity": severity,
                "host": host
            },
            **kwargs
        )


@dataclass
class DecisionMessage(AgentMessage):
    """
    Message for agent decision-making coordination.
    
    Agents can request input from others or broadcast their decisions.
    """
    def __init__(
        self,
        from_agent: str,
        decision_type: str,  # "request", "response", "broadcast"
        decision_data: Dict[str, Any],
        **kwargs
    ):
        msg_type_map = {
            "request": MessageType.DECISION_REQUEST,
            "response": MessageType.DECISION_RESPONSE,
            "broadcast": MessageType.DECISION_BROADCAST
        }
        
        super().__init__(
            message_type=msg_type_map.get(decision_type, MessageType.DECISION_BROADCAST),
            from_agent=from_agent,
            priority=kwargs.pop("priority", Priority.NORMAL),
            payload={
                "decision_type": decision_type,
                "decision_data": decision_data
            },
            **kwargs
        )


@dataclass
class HeartbeatMessage(AgentMessage):
    """
    Periodic heartbeat to show agent is alive and report status.
    
    Includes current state, resource usage, and recent activity summary.
    """
    def __init__(
        self,
        from_agent: str,
        agent_status: Dict[str, Any],
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.AGENT_HEARTBEAT,
            from_agent=from_agent,
            priority=Priority.LOW,
            payload={
                "status": agent_status,
                "uptime": agent_status.get("uptime", 0),
                "health": agent_status.get("health", "unknown")
            },
            **kwargs
        )


@dataclass
class MemoryShareMessage(AgentMessage):
    """
    Share learned patterns or memories with other agents.
    
    Enables collective learning across the agent network.
    """
    def __init__(
        self,
        from_agent: str,
        memory_type: str,  # "pattern", "decision_history", "learned_behavior"
        memory_data: Dict[str, Any],
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.MEMORY_SHARE,
            from_agent=from_agent,
            priority=Priority.LOW,
            payload={
                "memory_type": memory_type,
                "memory_data": memory_data,
                "confidence": kwargs.pop("confidence", 0.5)
            },
            **kwargs
        )


# Redis channel naming conventions
class RedisChannels:
    """Standard Redis pub/sub channel names for agent communication"""
    
    @staticmethod
    def broadcast() -> str:
        """Channel for messages to all agents"""
        return "agents:broadcast"
    
    @staticmethod
    def agent_specific(agent_name: str) -> str:
        """Channel for messages to specific agent"""
        return f"agents:{agent_name}"
    
    @staticmethod
    def resource_alerts() -> str:
        """Channel for resource monitoring alerts"""
        return "agents:resources:alerts"
    
    @staticmethod
    def decisions() -> str:
        """Channel for decision coordination"""
        return "agents:decisions"
    
    @staticmethod
    def heartbeats() -> str:
        """Channel for agent heartbeats"""
        return "agents:heartbeats"
    
    @staticmethod
    def learning() -> str:
        """Channel for shared learning and patterns"""
        return "agents:learning"
    
    @staticmethod
    def emergency() -> str:
        """Channel for emergency broadcasts"""
        return "agents:emergency"


# Redis key naming conventions
class RedisKeys:
    """Standard Redis key patterns for agent state and history"""
    
    @staticmethod
    def agent_state(agent_name: str) -> str:
        """Current state of an agent"""
        return f"agent:state:{agent_name}"
    
    @staticmethod
    def agent_history(agent_name: str) -> str:
        """Decision history for an agent (sorted set)"""
        return f"agent:history:{agent_name}"
    
    @staticmethod
    def agent_memory(agent_name: str, memory_type: str) -> str:
        """Agent memory storage"""
        return f"agent:memory:{agent_name}:{memory_type}"
    
    @staticmethod
    def message_archive(date_str: str) -> str:
        """Archive of messages by date"""
        return f"agent:messages:archive:{date_str}"
    
    @staticmethod
    def agent_metrics(agent_name: str) -> str:
        """Real-time metrics for an agent"""
        return f"agent:metrics:{agent_name}"
    
    @staticmethod
    def system_state() -> str:
        """Overall system state"""
        return "system:state:current"
