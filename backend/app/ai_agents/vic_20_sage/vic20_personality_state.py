"""
VIC-20 Sage — Personality State
================================

Pure state container. Holds all mutable state for VIC-20.

Extracted from:
- distributed_vic20.py (lines 67-121)
- decision_engine.py (lines 40-74)

Database integration initialized here but the actual
session comes from the communication layer.
"""

import logging
import statistics
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

from ..distributed.system_actions import RecommendationEngine
from .data_types import CoordinationState, VIC20DecisionType, VIC20Decision, AncientWisdom
from .coordination_stats import VIC20CoordinationStats

logger = logging.getLogger("VIC20.Personality")


class VIC20PersonalityState:
    """
    VIC-20 Sage's pure state container.

    Holds personality traits, coordination stats, mediation tracking,
    learning patterns, and database integration.

    No Redis. No message bus. No WebSocket. Just state.
    """

    def __init__(self, db_getter=None):
        """
        Initialize VIC-20's personality state.

        Args:
            db_getter: Database session factory for PostgreSQL writes
        """
        self.db_getter = db_getter

        # Agent identity
        self.agent_name = "vic_20_sage"

        # VIC-20's sage personality traits — EXACT keys from distributed_vic20.py:83-92
        self.personality_traits = {
            "coordinator": True,
            "pattern_matcher": True,
            "orchestrator": True,
            "wise": True,
            "patient": True,
            "multi_agent_aware": True,
            "historical_memory": "extensive",
            "coordination_style": "collaborative"
        }

        # VIC-20 does NOT monitor resources — he receives triage alerts
        self.resource_thresholds = {}

        # Recommendation engine (Task 4.1 Enhanced)
        self.recommendation_engine = RecommendationEngine()

        # Week 4 System Integration — lazy init
        self.coordination_manager = None
        self.escalation_manager = None
        self.resource_predictor = None

        # Bob mediation tracking — VIC-20's special duty!
        self.bob_mediation_count = 0
        self.stick_anxiety_prevented = 0
        self.bob_messages_filtered = []

        # Pending learning records keyed by triage_alert_id
        self._pending_learning_records: Dict[str, Any] = {}

        # Coordination & mediation stats (VIC-20's personality)
        self.coordination_stats = VIC20CoordinationStats()

        # --- State from decision_engine.py VIC20SageBrainV2 ---

        # Coordination state
        self.coordination_state = CoordinationState.OBSERVING
        self.is_active = True

        # Learning caches (used as fallback if DB unavailable)
        self.coordination_patterns: Dict[str, Dict[str, Any]] = {}
        self.effectiveness_history: List[Dict[str, Any]] = []
        self.agent_performance_trends: Dict[str, Dict[str, float]] = {}

        # Thresholds
        self.coordination_thresholds = {
            "minimum_confidence": 0.8,
            "agent_response_time_max": 5.0,
            "system_improvement_target": 0.3,
        }

        # Stats — EXACT names from decision_engine.py
        self.coordination_sessions = 0
        self.successful_coordinations = 0
        self.failed_coordinations = 0
        self.pattern_matches_found = 0
        self.total_analyses = 0
        self.successful_analyses = 0

        # Local learning buffer (fallback)
        self._recent_coordinations: List[Dict[str, Any]] = []

        # Default user scope for early boot
        self._default_user_id = "system"

        # Database integration — lazy init
        self.db_integration = None
        self._db_initialized = False

        logger.info(
            "🖥️✨ VIC-20 personality state initialized — "
            "ORCHESTRATION PROTOCOLS ACTIVE!"
        )

    async def initialize_database(self):
        """
        Initialize VIC-20's database integration.

        Called by VIC20Communication.initialize() after Redis is up.
        """
        if not self.db_getter:
            logger.warning("🖥️⚠️ No db_getter — database integration skipped")
            return

        try:
            from .database_integration import VIC20DatabaseIntegration
            self.db_integration = VIC20DatabaseIntegration(self.db_getter)
            await self.db_integration.initialize()
            self._db_initialized = True
            logger.info("🖥️💾 Database integration initialized")
        except Exception as e:
            logger.error(
                f"🖥️💥 Failed to initialize database: {e}", exc_info=True
            )

    def get_status(self) -> Dict[str, Any]:
        """
        Build VIC-20's agent status dict.

        EXACT keys from distributed_vic20.py:1483-1494.
        Frontend reads these — DO NOT rename.
        """
        return {
            "agent_name": self.agent_name,
            "agent_type": "orchestrator",
            "is_active": self.is_active,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "wisdom_level": "sage",
            "coordination_capacity": "unlimited",
            "pattern_library_size": "extensive",
        }

    def get_vic20_coordination_stats(self) -> Dict[str, Any]:
        """
        Get VIC-20's coordination stats.

        EXACT keys from decision_engine.py:667-675.
        """
        total = max(1, self.coordination_sessions)
        return {
            "sessions": self.coordination_sessions,
            "successes": self.successful_coordinations,
            "failures": self.failed_coordinations,
            "pattern_matches_found": self.pattern_matches_found,
            "success_rate": round(self.successful_coordinations / total, 3),
        }

    def get_partnership_metrics_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get partnership metrics.

        EXACT keys from decision_engine.py:677-686.
        """
        avg_eff = statistics.fmean(
            [v.get("effectiveness_score", 0.0)
             for v in self.agent_performance_trends.values()]
        ) if self.agent_performance_trends else 0.0
        return {
            "user_id": user_id,
            "agent_trends": self.agent_performance_trends,
            "avg_effectiveness": round(avg_eff, 3),
            "suggestions_available": avg_eff < 0.75,
        }
