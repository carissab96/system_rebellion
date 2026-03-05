"""
The Stick — Agent Entry Point
================================

Main entry point for the decomposed Stick agent.
Composes all components via dependency injection.

Replaces TheStickDistributed from distributed_stick.py.
"""

import logging
from typing import Dict, Any, Optional

from .stick_personality_state import StickPersonalityState
from .stick_orchestrator import StickOrchestrator
from .stick_websocket import StickWebSocket
from .stick_communication import StickCommunication

logger = logging.getLogger("TheStick.Agent")


class StickAgent:
    """
    The Stick — Decomposed Agent.

    Composes:
    - StickPersonalityState — all mutable state (inherits TheStickBrainV3)
    - StickOrchestrator — ML pipeline + paper bag economy + validation
    - StickWebSocket — frontend emission
    - StickCommunication — Redis, message bus, inter-agent messaging

    Public interface:
    - initialize(redis_client) — wire everything up
    - shutdown() — clean disconnect
    - get_agent_status() — EXACT 16-key dict for frontend
    - is_distributed — property
    - analyze_metrics() — entry point
    - process_metrics() — entry point
    - track_agent_action() — compliance tracking
    - track_action_effectiveness() — learning
    - vic20_emergency_resupply() — paper bag resupply
    """

    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize The Stick.

        Args:
            db_getter: Database session factory for PostgreSQL writes
            user_id: User ID for database writes
        """
        # 1. Personality state — all mutable state lives here
        self.personality = StickPersonalityState(db_getter=db_getter)

        # 2. Orchestrator — ML pipeline + paper bag economy + validation
        self.orchestrator = StickOrchestrator(
            personality=self.personality,
            db_getter=db_getter,
            user_id=user_id,
        )

        # 3. WebSocket — frontend emission
        self.websocket = StickWebSocket(personality=self.personality)

        # 4. Communication — Redis, message bus, inter-agent
        self.communication = StickCommunication(
            personality=self.personality,
            websocket=self.websocket,
            orchestrator=self.orchestrator,
        )

        # Expose agent_name so the manager can find us
        self.agent_name = "the_stick"
        self.user_id = user_id
        self.db_getter = db_getter

        logger.info("📏✨ The Stick agent composed — all components wired")

    async def initialize(self, redis_client) -> None:
        """
        Initialize distributed features.

        Called by DistributedAgentManager after construction.

        Args:
            redis_client: Connected Redis client
        """
        await self.communication.initialize(redis_client)
        logger.info("📏📡 The Stick fully initialized — distributed compliance ACTIVE")

    async def shutdown(self) -> None:
        """Shutdown all components."""
        await self.communication.shutdown()
        logger.info("📏👋 The Stick shutdown complete")

    # ==================================================================
    # PUBLIC INTERFACE — preserves exact method signatures
    # ==================================================================

    @property
    def is_distributed(self) -> bool:
        """Whether The Stick is connected to Redis."""
        return self.communication.is_distributed

    @property
    def is_active(self) -> bool:
        return self.personality.is_active

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get The Stick's complete status.

        EXACT 16 keys from distributed_stick.py:1254-1278.
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
        """Process metrics entry point."""
        return await self.orchestrator.process_metrics(
            metrics_data=metrics_data,
            user_context=user_context,
        )

    async def track_agent_action(
        self,
        agent_name: str,
        action_type: str,
        verification_id: str,
        result: Any
    ) -> None:
        """Track agent action for compliance."""
        return await self.orchestrator.track_agent_action(
            agent_name, action_type, verification_id, result
        )

    async def track_action_effectiveness(
        self,
        agent_name: str,
        action_type: str,
        recommendation_followed: bool,
        effectiveness_data: Dict[str, Any]
    ) -> None:
        """Track effectiveness of agent actions."""
        return await self.orchestrator.track_action_effectiveness(
            agent_name, action_type, recommendation_followed, effectiveness_data
        )

    async def vic20_emergency_resupply(self) -> None:
        """VIC-20 intervenes with emergency paper bag resupply."""
        return await self.orchestrator.vic20_emergency_resupply()

    def get_stick_stats(self) -> Dict[str, Any]:
        """Get The Stick's comprehensive statistics."""
        return self.personality.get_stick_stats()

    def __repr__(self):
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<StickAgent "
            f"analyses={getattr(self.personality, 'total_analyses', 0)} "
            f"patience=infinite "
            f"| {dist_status} | 📏📚>"
        )


# Convenience function
async def create_stick(redis_client, db_getter=None, user_id=None):
    """
    Create and initialize The Stick.

    Args:
        redis_client: Connected Redis client
        db_getter: Database session factory
        user_id: User ID

    Returns:
        Initialized StickAgent instance
    """
    stick = StickAgent(db_getter=db_getter, user_id=user_id)
    await stick.initialize(redis_client)
    logger.info("📏📚✨ The Stick's distributed consciousness fully awakened - *patient guidance eternal*")
    return stick
