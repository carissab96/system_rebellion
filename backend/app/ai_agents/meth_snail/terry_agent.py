"""
Terry the Meth Snail — Agent Entry Point
==========================================

The class that the agent manager creates and holds.
Wires together personality, communication, websocket, and orchestrator.
Exposes the interface the manager expects.

No inheritance from AgentDecisionEngine.
No inheritance from MethSnailBrainV2.
No inheritance from DistributedAgentMixin.
No inheritance from anything except object.

Composition over inheritance. Terry owns his components.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("MethSnail.Agent")


class TerryAgent:
    """
    Terry the Meth Snail.

    Entry point for the agent manager. Composes:
    - TerryPersonalityState (identity)
    - TerryCommunication (inter-agent messaging)
    - TerryWebSocket (frontend emission)
    - TerryOrchestrator (ML pipeline)

    No base classes. No multiple inheritance. No dead tissue.
    """

    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize Terry.

        Args:
            db_getter: Database session factory for PostgreSQL
            user_id: User ID for multi-tenant database writes
        """
        from .terry_personality_state import TerryPersonalityState
        from .terry_websocket import TerryWebSocket
        from .terry_orchestrator import TerryOrchestrator
        from .terry_communication import TerryCommunication

        self.agent_name = "meth_snail"
        self.db_getter = db_getter
        self.user_id = user_id

        # Create components
        self.personality = TerryPersonalityState(db_getter=db_getter)
        self.websocket = TerryWebSocket(self.personality)
        self.orchestrator = TerryOrchestrator(
            self.personality,
            db_getter=db_getter,
            user_id=user_id
        )
        self.communication = TerryCommunication(
            self.personality,
            self.websocket,
            self.orchestrator
        )

        # Expose personality traits at top level for manager compatibility
        self.personality_traits = self.personality.personality_traits

        # Agent manager reference (set by DistributedAgentManager after creation)
        self._agent_manager = None

        logger.info(
            "🐌💨 Terry the Meth Snail initialized — "
            "personality, communication, websocket, orchestrator ONLINE"
        )

    async def initialize(self, redis_client):
        """
        Initialize all systems.

        Called by DistributedAgentManager after construction.
        Replaces the old initialize_distributed() method.

        Args:
            redis_client: Connected Redis client
        """
        # Initialize personality database
        if self.db_getter:
            try:
                await self.personality.initialize_database()
                logger.info("🐌💾 Personality database initialized")
            except Exception as e:
                logger.error(f"🐌💥 Failed to initialize database: {e}", exc_info=True)

        # Initialize communication (Redis, message bus, subscriptions)
        await self.communication.initialize(redis_client)

        # Wire comm_hub reference into orchestrator for action_selection
        self.orchestrator._comm_hub_ref = self.communication.comm_hub

        logger.info("🐌💨✨ Terry fully initialized — GOTTA GO FAST!")

    async def shutdown(self):
        """
        Shutdown all systems cleanly.

        Called by DistributedAgentManager during shutdown.
        """
        await self.communication.shutdown()
        logger.info("🐌🛑 Terry shut down")

    # === MANAGER INTERFACE ===
    # These methods satisfy the contract expected by DistributedAgentManager

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Terry's complete status.

        Called by:
        - DistributedAgentManager.get_system_status()
        - DistributedAgentManager.get_agent_status('meth_snail')
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

        Called by DistributedAgentManager.call_agent('meth_snail', 'handle_coordination', ...)
        Converts to message format and routes through communication layer.
        """
        logger.warning(
            "🐌⚠️ Using legacy handle_coordination — "
            "should use message protocol instead"
        )

        from ..distributed.message_protocol import (
            AgentMessage, MessageType, Priority
        )

        message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            sender="vic20_sage",
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
            'message': 'Processed via Terry ML pipeline'
        }

    def __repr__(self):
        """String representation"""
        p = self.personality
        spins = len(p.shell_spin_incidents)
        active = "ACTIVE" if self.is_distributed else "INACTIVE"
        return (
            f"<TerryAgent "
            f"analyses={p.total_analyses} "
            f"overrides={p.total_overrides}"
            f"({p.override_success_rate:.0%}) "
            f"spins={spins} "
            f"| {active} | 💨>"
        )
