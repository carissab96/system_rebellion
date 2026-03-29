"""
Quantum Shadow People — Agent Entry Point
===========================================

The class that the agent manager creates and holds.
Wires together personality, communication, websocket, and orchestrator.
Exposes the interface the manager expects.

No inheritance from AgentDecisionEngine.
No inheritance from QuantumShadowPeopleBrainV2.
No inheritance from DistributedAgentMixin.
No inheritance from anything except object.

Composition over inheritance. QSP own their components.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("QSP.Agent")


class QSPAgent:
    """
    Quantum Shadow People — Network Specialists.

    Entry point for the agent manager. Composes:
    - QSPPersonalityState (identity, quantum state, paranoia)
    - QSPCommunication (inter-agent messaging)
    - QSPWebSocket (frontend emission)
    - QSPOrchestrator (ML pipeline)

    No base classes. No multiple inheritance. No dead tissue.
    """

    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize the Quantum Shadow People.

        Args:
            db_getter: Database session factory for PostgreSQL
            user_id: User ID for multi-tenant database writes
        """
        from .qsp_personality_state import QSPPersonalityState
        from .qsp_websocket import QSPWebSocket
        from .qsp_orchestrator import QSPOrchestrator
        from .qsp_communication import QSPCommunication

        self.agent_name = "quantum_shadow_people"
        self.db_getter = db_getter
        self.user_id = user_id

        # Create components
        self.personality = QSPPersonalityState(db_getter=db_getter)
        self.websocket = QSPWebSocket(self.personality)
        self.orchestrator = QSPOrchestrator(
            self.personality,
            db_getter=db_getter,
            user_id=user_id,
        )
        self.communication = QSPCommunication(
            self.personality,
            self.websocket,
            self.orchestrator,
        )

        # Expose personality traits at top level for manager compatibility
        self.personality_traits = self.personality.personality_traits

        # Agent manager reference (set by DistributedAgentManager after creation)
        self._agent_manager = None

        logger.info(
            "👻🔮 Quantum Shadow People initialized — "
            "personality, communication, websocket, orchestrator ONLINE"
        )
        logger.info("👻🔒 Paranoid coordination protocols active — TRUST NO ONE!")

    async def initialize(self, redis_client):
        """
        Initialize all systems.

        Called by DistributedAgentManager after construction.
        Replaces the old initialize_distributed() method.

        Args:
            redis_client: Connected Redis client
        """
        # Initialize communication (Redis, message bus, subscriptions, database)
        await self.communication.initialize(redis_client)

        # Wire comm_hub reference into orchestrator
        self.orchestrator._comm_hub_ref = self.communication.comm_hub

        logger.info(
            "👻🔮✨ Quantum Shadow People fully initialized — "
            "QUANTUM SURVEILLANCE ACTIVE!"
        )

    async def shutdown(self):
        """
        Shutdown all systems cleanly.

        Called by DistributedAgentManager during shutdown.
        """
        await self.communication.shutdown()
        logger.info("👻🛑 Quantum Shadow People shut down — *final phase shift*")

    # === MANAGER INTERFACE ===
    # These methods satisfy the contract expected by DistributedAgentManager

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get QSP's complete status.

        Called by:
        - DistributedAgentManager.get_system_status()
        - DistributedAgentManager.get_agent_status('quantum_shadow_people')
        - Heartbeat payload generation
        """
        status = self.websocket.get_agent_status()

        # Add communication state
        try:
            status["distributed"] = self.communication.get_distributed_state()
        except Exception:
            status["distributed"] = {"distributed_enabled": False}

        return status

    @property
    def is_distributed(self) -> bool:
        """
        Check if distributed features are active.

        Called by DistributedAgentManager.health_check()
        """
        return self.communication.is_distributed

    async def handle_coordination(
        self, coordination_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Legacy direct coordination handler.

        Called by DistributedAgentManager.call_agent(
            'quantum_shadow_people', 'handle_coordination', ...
        )
        Converts to message format and routes through communication layer.
        """
        logger.warning(
            "👻⚠️ Using legacy handle_coordination — "
            "should use message protocol instead"
        )

        from ..distributed.message_protocol import (
            AgentMessage, MessageType, Priority
        )

        message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="vic20_sage",
            payload=coordination_request,
            priority=(
                Priority.HIGH
                if coordination_request.get('severity') in ['high', 'critical']
                else Priority.NORMAL
            )
        )

        await self.communication._handle_coordination_request(message)

        return {
            'success': True,
            'message': 'Processed via QSP ML pipeline'
        }

    def __repr__(self):
        """Quantum string representation."""
        p = self.personality
        active = "ACTIVE" if self.is_distributed else "INACTIVE"
        return (
            f"<QSPAgent "
            f"scans={p.total_security_scans} "
            f"threats={p.threats_detected} "
            f"paranoia={p.paranoia_level.value} "
            f"| {active} | 👻🔮>"
        )


# Convenience factory function
async def create_qsp(redis_client, db_getter=None, user_id: str = None):
    """
    Create and initialize the Quantum Shadow People.

    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        user_id: User ID for database writes (optional)

    Returns:
        Initialized QSPAgent instance
    """
    qsp = QSPAgent(db_getter=db_getter, user_id=user_id)
    await qsp.initialize(redis_client)
    logger.info(
        "👻🔮✨ Quantum Shadow People's distributed consciousness "
        "fully awakened — *quantum entanglement complete*"
    )
    return qsp
