"""
The Hamsters — Agent Entry Point
=================================

The class that the agent manager creates and holds.
Wires together personality, communication, websocket, and orchestrator.
Exposes the interface the manager expects.

No inheritance from AgentDecisionEngine.
No inheritance from HamstersBrainV3.
No inheritance from DistributedAgentMixin.
No inheritance from anything except object.

Composition over inheritance. The Hamsters own their components.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("Hamsters.Agent")


class HamstersAgent:
    """
    Steve, Bob, and Carl — The Hamsters.

    Entry point for the agent manager. Composes:
    - HamstersPersonalityState (identity)
    - HamstersCommunication (inter-agent messaging)
    - HamstersWebSocket (frontend emission)
    - HamstersOrchestrator (ML pipeline)

    No base classes. No multiple inheritance. No dead tissue.
    """

    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize the Hamsters.

        Args:
            db_getter: Database session factory for PostgreSQL
            user_id: User ID for multi-tenant database writes
        """
        from .hamsters_personality_state import HamstersPersonalityState
        from .hamsters_websocket import HamstersWebSocket
        from .hamsters_orchestrator import HamstersOrchestrator
        from .hamsters_communication import HamstersCommunication

        self.agent_name = "hamsters"
        self.db_getter = db_getter
        self.user_id = user_id

        # Create components
        self.personality = HamstersPersonalityState(db_getter=db_getter)
        self.websocket = HamstersWebSocket(self.personality)
        self.orchestrator = HamstersOrchestrator(
            self.personality,
            db_getter=db_getter,
            user_id=user_id,
        )
        self.communication = HamstersCommunication(
            self.personality,
            self.websocket,
            self.orchestrator,
        )

        # Expose personality traits at top level for manager compatibility
        self.personality_traits = self.personality.personality_traits

        # Agent manager reference (set by DistributedAgentManager after creation)
        self._agent_manager = None

        logger.info(
            "🐹🐹🐹 Steve, Bob, and Carl initialized — "
            "personality, communication, websocket, orchestrator ONLINE"
        )
        logger.info("🐹🍺 Beer level: OPTIMAL — Peak performance achieved!")

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

        logger.info("🐹🐹🐹✨ Steve, Bob, and Carl fully initialized — TELEPATHIC LINK ACTIVE!")

    async def shutdown(self):
        """
        Shutdown all systems cleanly.

        Called by DistributedAgentManager during shutdown.
        """
        await self.communication.shutdown()
        logger.info("🐹🛑 Steve, Bob, and Carl shut down — *final squeak*")

    # === MANAGER INTERFACE ===
    # These methods satisfy the contract expected by DistributedAgentManager

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the Hamsters' complete status.

        Called by:
        - DistributedAgentManager.get_system_status()
        - DistributedAgentManager.get_agent_status('hamsters')
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

        Called by DistributedAgentManager.call_agent('hamsters', 'handle_coordination', ...)
        Converts to message format and routes through communication layer.
        """
        logger.warning(
            "🐹⚠️ Using legacy handle_coordination — "
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
            'message': 'Processed via Hamsters ML pipeline'
        }

    def __repr__(self):
        """Telepathic string representation"""
        p = self.personality
        active = "ACTIVE" if self.is_distributed else "INACTIVE"
        return (
            f"<HamstersAgent "
            f"steve+bob+carl "
            f"beer={p.collective_beer_level.value} "
            f"bob_ideas={p.bob_wild_ideas} "
            f"analyses={p.total_analyses} "
            f"| {active} | 🐹🐹🐹>"
        )


# Convenience factory function
async def create_hamsters(redis_client, db_getter=None, user_id: str = None):
    """
    Create and initialize the hamster trio.

    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        user_id: User ID for database writes (optional)

    Returns:
        Initialized HamstersAgent instance
    """
    hamsters = HamstersAgent(db_getter=db_getter, user_id=user_id)
    await hamsters.initialize(redis_client)
    logger.info(
        "🐹🐹🐹✨ Steve, Bob, and Carl's distributed consciousness fully awakened — "
        "*telepathic celebration*"
    )
    return hamsters
