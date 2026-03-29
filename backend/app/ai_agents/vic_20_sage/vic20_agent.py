"""
VIC-20 Sage — Agent Entry Point
=================================

Main entry point for the decomposed VIC-20 Sage.
Composes all components via dependency injection.

Replaces VIC20SageDistributed from distributed_vic20.py.
"""

import logging
from typing import Dict, Any, Optional

from .vic20_personality_state import VIC20PersonalityState
from .vic20_orchestrator import VIC20Orchestrator
from .vic20_websocket import VIC20WebSocket
from .vic20_communication import VIC20Communication

logger = logging.getLogger("VIC20.Agent")


class VIC20Agent:
    """
    VIC-20 Sage — Decomposed Agent.

    Composes:
    - VIC20PersonalityState — all mutable state
    - VIC20Orchestrator — ML pipeline + coordination + mediation
    - VIC20WebSocket — frontend emission
    - VIC20Communication — Redis, message bus, inter-agent messaging

    Public interface:
    - initialize(redis_client) — wire everything up
    - shutdown() — clean disconnect
    - get_agent_status() — EXACT dict for frontend
    - is_distributed — property
    - analyze_metrics() — legacy entry point
    - process_metrics() — coordination loop
    """

    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize VIC-20 Sage.

        Args:
            db_getter: Database session factory for PostgreSQL writes
            user_id: User ID for database writes
        """
        # 1. Personality state — all mutable state lives here
        self.personality = VIC20PersonalityState(db_getter=db_getter)

        # 2. Orchestrator — ML pipeline + coordination logic
        self.orchestrator = VIC20Orchestrator(
            personality=self.personality,
            db_getter=db_getter,
            user_id=user_id,
        )

        # 3. WebSocket — frontend emission
        self.websocket = VIC20WebSocket(personality=self.personality)

        # 4. Communication — Redis, message bus, inter-agent
        self.communication = VIC20Communication(
            personality=self.personality,
            websocket=self.websocket,
            orchestrator=self.orchestrator,
        )

        # Expose agent_name so the manager can find us
        self.agent_name = "vic_20_sage"
        self.user_id = user_id

        logger.info("🖥️✨ VIC-20 Sage agent composed — all components wired")

    async def initialize(self, redis_client) -> None:
        """
        Initialize distributed features.

        Called by DistributedAgentManager after construction.

        Args:
            redis_client: Connected Redis client
        """
        await self.communication.initialize(redis_client)
        logger.info("🖥️📡 VIC-20 Sage fully initialized — distributed consciousness ACTIVE")

    async def shutdown(self) -> None:
        """Shutdown all components."""
        await self.communication.shutdown()
        logger.info("🖥️👋 VIC-20 Sage shutdown complete")

    # ==================================================================
    # PUBLIC INTERFACE — preserves exact method signatures
    # ==================================================================

    @property
    def is_distributed(self) -> bool:
        """Whether VIC-20 is connected to Redis."""
        return self.communication.is_distributed

    @property
    def is_active(self) -> bool:
        return self.personality.is_active

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get VIC-20's complete status.

        EXACT keys from distributed_vic20.py:1483-1494.
        """
        distributed_state = self.communication.get_distributed_state()
        return self.websocket.get_agent_status(distributed_state)

    def get_distributed_state(self) -> Dict[str, Any]:
        """Get distributed state from communication hub."""
        return self.communication.get_distributed_state()

    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.
        Legacy entry point for backwards compatibility.
        """
        return await self.communication.analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            user_id=user_id,
        )

    async def process_metrics(
        self,
        metrics_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Coordination loop entry point."""
        return await self.orchestrator.process_metrics(
            metrics_data=metrics_data,
            user_context=user_context,
        )

    async def coordinate_system_rebellion(
        self,
        all_agent_data: Dict[str, Any],
        system_context: Dict[str, Any],
        user_id: str
    ) -> Optional[Any]:
        """Direct access to coordination loop."""
        return await self.orchestrator.coordinate_system_rebellion(
            all_agent_data, system_context, user_id
        )

    async def coordinate_agent_emergency_response(
        self,
        emergency_type: str,
        affected_agents: list,
        system_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Emergency response coordination."""
        from .data_types import utc_now
        plan = {
            "type": emergency_type,
            "agents": affected_agents,
            "started_at": utc_now().isoformat(),
            "status": "planned",
        }
        await self.orchestrator._store_coordination_for_learning(user_id, None, {
            "emergency": True,
            "plan": plan,
            "system_context": system_context,
        })
        plan["status"] = "completed"
        plan["ended_at"] = utc_now().isoformat()
        return plan

    def get_vic20_coordination_stats(self) -> Dict[str, Any]:
        """Get coordination stats."""
        return self.personality.get_vic20_coordination_stats()

    def get_partnership_metrics_data(self, user_id: str) -> Dict[str, Any]:
        """Get partnership metrics."""
        return self.personality.get_partnership_metrics_data(user_id)

    def __repr__(self):
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<VIC20Agent "
            f"analyses={self.personality.total_analyses} "
            f"wisdom=sage "
            f"| {dist_status} | 🖥️🧙>"
        )


# Convenience function
async def create_vic20(redis_client, db_getter=None, user_id=None):
    """
    Create and initialize VIC-20 Sage.

    Args:
        redis_client: Connected Redis client
        db_getter: Database session factory
        user_id: User ID

    Returns:
        Initialized VIC20Agent instance
    """
    vic20 = VIC20Agent(db_getter=db_getter, user_id=user_id)
    await vic20.initialize(redis_client)
    logger.info("🖥️🧙✨ VIC-20 Sage's distributed consciousness fully awakened - *ancient wisdom flows*")
    return vic20
