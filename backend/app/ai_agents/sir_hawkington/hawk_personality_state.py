"""
Sir Hawkington — Personality State
=====================================

Everything that makes Sir Hawkington WHO HE IS.

Owns: monocle state, yeet incidents, earl grey tea system,
alert state tracking, cooldown management, personality traits,
resource thresholds, metrics quality stats.

No decisions. No messaging. No inheritance.
The ML pipeline reads and writes this.
The websocket reads this.
Nobody inherits from this.

Mirrors the structure of meth_snail/terry_personality_state.py.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timezone

from .hawk_data_types import (
    MonocleState,
    MonocleYeetIncident,
    EarlGreyState,
    AlertStateRecord,
    TriageSeverity,
)

logger = logging.getLogger("SirHawkington.Personality")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HawkPersonalityState:
    """
    Sir Hawkington's personality and identity state.

    Pure state container. No decisions. No messaging. No base classes.
    """

    def __init__(self, db_getter=None):
        # Database integration (lazy init)
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter

        self._db_initialized = False
        self.db_integration = None

        # === MONOCLE STATE ===
        self.current_monocle_state = MonocleState.POLISHED
        self.monocle_yeet_incidents: List[MonocleYeetIncident] = []
        self.monocle_yeets_by_severity = {
            "mild":         0,
            "moderate":     0,
            "severe":       0,
            "catastrophic": 0,
        }

        # === EARL GREY TEA SYSTEM ===
        self.earl_grey = EarlGreyState()

        # === ALERT STATE TRACKING (cooldown / spam prevention) ===
        # { resource_type: AlertStateRecord }
        self._alert_states: Dict[str, AlertStateRecord] = {}
        self._alert_cooldown_seconds: int = 60

        # === ANALYSIS TRACKING ===
        self.total_analyses:      int = 0
        self.successful_analyses: int = 0

        # === ESCALATION TRACKING ===
        self.total_alerts_sent:        int = 0
        self.escalated_alerts:         int = 0
        self.emergency_alerts:         int = 0
        self.cooldown_prevented_alerts: int = 0

        # === METRICS QUALITY ===
        self.metrics_quality_stats = {
            'cpu_missing_count':     0,
            'memory_missing_count':  0,
            'disk_missing_count':    0,
            'network_missing_count': 0,
            'invalid_data_count':    0,
            'monocle_yeets_total':   0,
        }

        # === RESOURCE THRESHOLDS ===
        # These are the real production thresholds.
        # The ML reasoning layer uses these; they are tunable over time.
        from app.optimization.resource_monitor import ResourceType
        self.resource_thresholds = {
            ResourceType.CPU:     10.0,
            ResourceType.MEMORY:  20.0,
            ResourceType.DISK:    30.0,
            ResourceType.NETWORK: 20.0,
            ResourceType.SWAP:    10.0,
        }

        # === PERSONALITY TRAITS ===
        self.personality_traits = {
            "aristocratic":             True,
            "monocle_yeeting_enabled":  True,
            "triage_commander":         True,
            "distinguished":            True,
            "concern_threshold":        0.65,
            "alert_threshold":          0.85,
            "critical_threshold":       0.95,
            "preferred_monocle_state":  "polished",
            "trust_level":              0.6,
            "earl_grey_enabled":        True,
            "sips_per_cup":             12,
        }

        logger.info("🧐 Sir Hawkington's personality state initialized — monocle polished, tea ready")

    # =========================================================================
    # DATABASE INITIALIZATION
    # =========================================================================

    async def initialize_database(self):
        """Initialize database integration. Called during agent startup."""
        if not self._db_initialized:
            from app.ai_agents.sir_hawkington.database_integration import HawkingtonDatabaseIntegration
            self.db_integration = HawkingtonDatabaseIntegration(self.db_getter)
            await self.db_integration.initialize()
            self._db_initialized = True
            logger.info("🧐💾 Hawkington personality database initialized")
        return self.db_integration

    # =========================================================================
    # MONOCLE MANAGEMENT
    # =========================================================================

    def polish_monocle(self):
        """Called after a clean, confident triage cycle."""
        self.current_monocle_state = MonocleState.POLISHED

    def adjust_monocle(self):
        """Called when something minor is noted but doesn't warrant escalation."""
        self.current_monocle_state = MonocleState.ADJUSTED

    def fog_monocle(self):
        """Called when data quality is suspect."""
        self.current_monocle_state = MonocleState.FOGGED

    def yeet_monocle(
        self,
        reason: str,
        resource_type: str,
        intensity: str = "moderate",
        user_id: Optional[str] = None,
    ) -> MonocleYeetIncident:
        """
        Sir Hawkington yeeets his monocle.

        Called when:
        - Data is missing/empty (upstream failure) — yeet, log, notify human
        - System-wide failure likely — yeet AT VIC-20 for multi-agent coordination
        """
        self.current_monocle_state = MonocleState.YEETED
        self.monocle_yeets_by_severity[intensity] = (
            self.monocle_yeets_by_severity.get(intensity, 0) + 1
        )
        self.metrics_quality_stats['monocle_yeets_total'] += 1

        incident = MonocleYeetIncident(
            timestamp=utc_now(),
            reason=reason,
            resource_type=resource_type,
            yeet_intensity=intensity,
            user_id=user_id,
        )
        self.monocle_yeet_incidents.append(incident)

        logger.warning(
            f"🧐💥 MONOCLE YEETED ({intensity.upper()}): {reason} "
            f"[resource={resource_type}, total_yeets={self.metrics_quality_stats['monocle_yeets_total']}]"
        )
        return incident

    # =========================================================================
    # EARL GREY TEA SYSTEM
    # =========================================================================

    def _reset_earl_grey_if_needed(self):
        """Reset daily earl grey counters on the first triage of a new day."""
        today = date.today()
        if self.earl_grey.last_reset_date != today:
            self.earl_grey.sips_today       = 0
            self.earl_grey.cups_consumed    = 0
            self.earl_grey.current_cup_sips = 0
            self.earl_grey.interrupted_today = 0
            self.earl_grey.last_reset_date  = today
            logger.debug("🧐🫖 Earl Grey counters reset for new day")

    def sip_earl_grey(self):
        """
        Sir Hawkington takes a measured sip of Earl Grey.
        Called after every DISMISS / NORMAL decision.

        A proper cup takes 12 sips to finish. Completing a cup means
        the system has been calm for 12 consecutive dismiss cycles.
        """
        self._reset_earl_grey_if_needed()

        self.earl_grey.sips_today       += 1
        self.earl_grey.current_cup_sips += 1

        if self.earl_grey.current_cup_sips >= self.earl_grey.sips_per_cup:
            self.earl_grey.cups_consumed    += 1
            self.earl_grey.current_cup_sips  = 0
            logger.info(
                f"🧐🫖 Sir Hawkington finishes his cup of Earl Grey. "
                f"Splendid. Cup #{self.earl_grey.cups_consumed} today. "
                f"The system has been most agreeable."
            )
        else:
            logger.debug(
                f"🧐☕ *sip* "
                f"({self.earl_grey.current_cup_sips}/{self.earl_grey.sips_per_cup})"
            )

    def interrupt_earl_grey(self):
        """
        An escalation interrupts Sir Hawkington's tea.
        Current cup sip progress resets. Called before every escalation.
        """
        self._reset_earl_grey_if_needed()

        if self.earl_grey.current_cup_sips > 0:
            self.earl_grey.interrupted_today += 1
            logger.info(
                f"🧐☕💢 Sir Hawkington's tea is interrupted! "
                f"({self.earl_grey.current_cup_sips} sips wasted) "
                f"How terribly uncouth. "
                f"Interruption #{self.earl_grey.interrupted_today} today."
            )
            self.earl_grey.current_cup_sips = 0

    # =========================================================================
    # ALERT STATE / COOLDOWN MANAGEMENT
    # =========================================================================

    def should_emit_alert(self, resource_type: str, severity: str) -> tuple[bool, str]:
        """
        Determine whether an alert should be emitted to the frontend.

        Returns (should_emit, state_label) where state_label is one of:
        "NEW", "ONGOING_REMINDER", "ONGOING_COOLDOWN", "SEVERITY_CHANGE"
        """
        current_time = utc_now()

        if resource_type not in self._alert_states:
            # Brand new alert
            self._alert_states[resource_type] = AlertStateRecord(
                state="NEW",
                severity=severity,
                last_emission_time=current_time,
                first_seen_time=current_time,
            )
            return (True, "NEW")

        record = self._alert_states[resource_type]

        # Severity changed — always emit
        if record.severity != severity:
            record.severity           = severity
            record.last_emission_time = current_time
            record.state              = "ONGOING"
            return (True, "SEVERITY_CHANGE")

        # Still within cooldown — suppress
        elapsed = (current_time - record.last_emission_time).total_seconds()
        if elapsed < self._alert_cooldown_seconds:
            self.cooldown_prevented_alerts += 1
            logger.debug(
                f"🧐🔇 {resource_type} alert suppressed "
                f"(cooldown: {elapsed:.0f}s / {self._alert_cooldown_seconds}s)"
            )
            return (False, "ONGOING_COOLDOWN")

        # Cooldown expired — emit reminder
        record.last_emission_time = current_time
        record.state              = "ONGOING"
        return (True, "ONGOING_REMINDER")

    def clear_alert_state(self, resource_type: str):
        """Clear alert state when resource returns to normal."""
        if resource_type in self._alert_states:
            del self._alert_states[resource_type]
            logger.info(f"🧐✅ {resource_type} alert RESOLVED — clearing state")

    # =========================================================================
    # TRACKING HELPERS
    # =========================================================================

    def record_analysis(self, success: bool = True):
        self.total_analyses += 1
        if success:
            self.successful_analyses += 1

    def record_escalation(self, emergency: bool = False):
        self.total_alerts_sent += 1
        self.escalated_alerts  += 1
        if emergency:
            self.emergency_alerts += 1

    # =========================================================================
    # STATUS / SERIALIZATION
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Full personality status for heartbeat emission."""
        return {
            "monocle_state":          self.current_monocle_state.value,
            "monocle_yeet_incidents": len(self.monocle_yeet_incidents),
            "monocle_yeets_by_severity": self.monocle_yeets_by_severity,
            "earl_grey":              self.earl_grey.to_dict(),
            "total_analyses":         self.total_analyses,
            "successful_analyses":    self.successful_analyses,
            "escalation_stats": {
                "total_alerts_sent":         self.total_alerts_sent,
                "escalated_alerts":          self.escalated_alerts,
                "emergency_alerts":          self.emergency_alerts,
                "cooldown_prevented_alerts": self.cooldown_prevented_alerts,
            },
            "metrics_quality_stats":  self.metrics_quality_stats,
            "personality_traits":     self.personality_traits,
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "agent_name":            "sir_hawkington",
            "status":                "DISTINGUISHED_AND_OPERATIONAL",
            "monocle_state":         self.current_monocle_state.value,
            "earl_grey_calm_ratio":  self.earl_grey.system_calm_ratio,
            "total_yeets":           self.metrics_quality_stats['monocle_yeets_total'],
            "total_analyses":        self.total_analyses,
            "aristocratic_standards": "MAINTAINED",
        }
