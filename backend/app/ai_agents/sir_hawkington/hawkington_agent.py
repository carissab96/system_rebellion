"""
Sir Hawkington — Agent Entry Point
=====================================

The class that the agent manager creates and holds.
Wires together personality, communication, websocket, and orchestrator.
Exposes the interface the manager expects.

No inheritance from AgentDecisionEngine.
No inheritance from SirHawkingtonBrainV2.
No inheritance from DistributedAgentMixin.
No inheritance from anything except object.

Composition over inheritance. Hawkington owns his components.

Mirrors the structure of meth_snail/terry_agent.py.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("SirHawkington.Agent")


class HawkingtonAgent:
    """
    Sir Hawkington von Monitorious III.

    Entry point for the agent manager. Composes:
    - HawkPersonalityState  (identity, monocle, earl grey, alert state)
    - HawkCommunication     (Redis, ResourceMonitor, inter-agent messaging)
    - HawkWebSocket         (frontend emission)
    - HawkOrchestrator      (ML pipeline)

    No base classes. No multiple inheritance. No dead tissue.
    """

    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize Sir Hawkington.

        Args:
            db_getter: Database session factory for PostgreSQL
            user_id:   User ID for multi-tenant database writes
        """
        from .hawk_personality_state import HawkPersonalityState
        from .hawk_websocket import HawkWebSocket
        from .hawk_orchestrator import HawkOrchestrator
        from .hawk_communication import HawkCommunication

        self.agent_name = "sir_hawkington"
        self.db_getter  = db_getter
        self.user_id    = user_id

        # Create components
        self.personality = HawkPersonalityState(db_getter=db_getter)
        self.websocket   = HawkWebSocket(self.personality)
        self.orchestrator = HawkOrchestrator(
            self.personality,
            db_getter=db_getter,
            user_id=user_id,
        )
        self.communication = HawkCommunication(
            self.personality,
            self.websocket,
            self.orchestrator,
        )

        # Expose personality traits at top level for manager compatibility
        self.personality_traits = self.personality.personality_traits

        # Agent manager reference (set by DistributedAgentManager after creation)
        self._agent_manager = None

        logger.info(
            "🧐 Sir Hawkington von Monitorious III initialized — "
            "personality, communication, websocket, orchestrator ONLINE. "
            "Monocle polished. Tea steeped. Ready to triage."
        )

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

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
                logger.info("🧐💾 Personality database initialized")
            except Exception as e:
                logger.error(
                    f"🧐💥 Failed to initialize personality database: {e}",
                    exc_info=True,
                )

        # Initialize communication (Redis, ResourceMonitor, message bus, subscriptions)
        await self.communication.initialize(redis_client)

        # Wire comm_hub reference into orchestrator
        self.orchestrator._comm_hub_ref = self.communication.comm_hub

        logger.info(
            "🧐✨ Sir Hawkington fully initialized — "
            "ARISTOCRATIC TRIAGE COMMANDER ONLINE"
        )

    async def shutdown(self):
        """
        Shutdown all systems cleanly.

        Called by DistributedAgentManager during shutdown.
        """
        await self.communication.shutdown()
        logger.info("🧐🛑 Sir Hawkington shut down")

    # =========================================================================
    # MANAGER INTERFACE
    # =========================================================================

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Sir Hawkington's complete status.

        Called by:
        - DistributedAgentManager.get_system_status()
        - DistributedAgentManager.get_agent_status('sir_hawkington')
        - Heartbeat payload generation
        """
        status = self.websocket.get_agent_status()

        # Add communication / distributed state
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
            'sir_hawkington', 'handle_coordination', ...
        )
        Converts to message format and routes through communication layer.
        """
        logger.warning(
            "🧐⚠️ Using legacy handle_coordination — "
            "should use message protocol instead"
        )

        from ..distributed.message_protocol import AgentMessage, MessageType, Priority

        message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            sender="vic20_sage",
            payload=coordination_request,
            priority=(
                Priority.HIGH
                if coordination_request.get('severity') in ['high', 'critical']
                else Priority.NORMAL
            ),
        )

        await self.communication._handle_coordination_request(message)

        return {
            'success': True,
            'message': 'Processed via Hawkington ML pipeline',
        }

    def __repr__(self):
        p = self.personality
        active = "ACTIVE" if self.is_distributed else "INACTIVE"
        return (
            f"<HawkingtonAgent "
            f"analyses={p.total_analyses} "
            f"yeets={len(p.monocle_yeet_incidents)} "
            f"sips={p.earl_grey.sips_today} "
            f"cups={p.earl_grey.cups_consumed} "
            f"calm={p.earl_grey.system_calm_ratio:.0%} "
            f"| {active} | 🧐>"
        )


# ── Convenience factory ───────────────────────────────────────────────────────

async def create_hawkington_agent(redis_client, db_getter=None, user_id: str = None):
    """
    Create and initialize Sir Hawkington with full distributed consciousness.

    Args:
        redis_client: Connected Redis client
        db_getter:    Database session getter (optional)
        user_id:      User ID for multi-tenant writes (optional)

    Returns:
        Initialized HawkingtonAgent instance
    """
    hawk = HawkingtonAgent(db_getter=db_getter, user_id=user_id)
    await hawk.initialize(redis_client)
    logger.info(
        "🧐✨ Sir Hawkington's aristocratic consciousness fully awakened — "
        "TRIAGE COMMANDER READY"
    )
    return hawk
