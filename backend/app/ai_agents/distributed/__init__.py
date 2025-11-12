"""
Distributed Agent Consciousness System
======================================

Redis-based distributed agent communication, state persistence, and coordination.
Enables agents to maintain continuous existence across restarts and network boundaries.
"""

from .message_protocol import (
    MessageType,
    Priority,
    AgentMessage,
    ResourceAlert,
    DecisionMessage,
    HeartbeatMessage
)

from .agent_state import (
    AgentState,
    AgentStateManager
)

from .communication import (
    AgentCommunicationHub,
    MessageBus
)

__all__ = [
    'MessageType',
    'Priority',
    'AgentMessage',
    'ResourceAlert',
    'DecisionMessage',
    'HeartbeatMessage',
    'AgentState',
    'AgentStateManager',
    'AgentCommunicationHub',
    'MessageBus'
]
