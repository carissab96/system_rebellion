"""
The Hamsters — Personality State
=================================

Everything that makes Steve, Bob, and Carl WHO THEY ARE.

Owns: beer counts (individual), duct tape inventory, Bob's wild ideas,
supply cupboard raids, telepathic consensus, squeak history.

Pure state container. No decisions. No messaging. No base classes.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timezone

from .hamsters_data_types import (
    BeerLevel, DuctTapeGrade, DuctTapeJob, BeerConsumptionEvent,
    AlertStateRecord, HamsterDailyTracking, HamstersPriority
)

logger = logging.getLogger("Hamsters.Personality")


def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)


class HamstersPersonalityState:
    """
    Steve, Bob, and Carl's personality and identity state.

    Pure state container. No decisions. No messaging. No base classes.
    """

    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter

        # === INDIVIDUAL HAMSTER STATE ===

        # Steve (careful, analytical)
        self.steve_beer_count: int = 2  # Paces himself
        self.steve_risk_tolerance: float = 0.3
        self.steve_current_task: Optional[str] = None

        # Bob (wild, chaotic)
        self.bob_beer_count: int = 4  # Always ready
        self.bob_risk_tolerance: float = 0.8
        self.bob_wild_ideas: int = 0
        self.bob_wild_idea_pending: Optional[str] = None
        self.bob_at_cupboard: bool = False
        self.bob_hold_my_beer_count: int = 0
        self.bob_supply_cupboard_raids_today: int = 0

        # Carl (duct tape expert, moderate)
        self.carl_beer_count: int = 3  # Moderate
        self.carl_risk_tolerance: float = 0.5
        self.carl_duct_tape_inventory: Dict[str, int] = {
            DuctTapeGrade.REGULAR.value: 50,
            DuctTapeGrade.PREMIUM.value: 20,
            DuctTapeGrade.QUANTUM.value: 5,
            DuctTapeGrade.CARLS_SPECIAL.value: 1,  # Use wisely
        }
        self.carl_duct_tape_rolls_used_today: float = 0.0
        self.carl_duct_tape_jobs_today: List[DuctTapeJob] = []

        # === COLLECTIVE STATE ===
        self.collective_beer_level: BeerLevel = self._calculate_collective_beer_level()
        self.beer_consumption_today: int = 0
        self.telepathic_consensus_strength: float = 0.85
        self.squeak_history: List[str] = []

        # === TRACKING ===
        self.total_analyses: int = 0
        self.successful_analyses: int = 0
        self.total_interventions: int = 0
        self.successful_fixes: int = 0

        # Daily tracking
        self._daily = HamsterDailyTracking()
        self._last_daily_reset: Optional[date] = None

        # Alert cooldown
        self._alert_state = AlertStateRecord()

        # Database integration (lazy init)
        self.db_integration = None

        # Resource thresholds
        self.resource_thresholds = {
            'disk': 80.0,  # Alert at 80% disk
        }

        # Personality traits dict for manager compatibility
        self.personality_traits = {
            "telepathic": True,
            "beer_loving": True,
            "duct_tape_experts": True,
            "steve_analytical": True,
            "bob_wild": True,
            "carl_duct_tape_genius": True,
            "consensus_required": True,
            "squeak_frequency": "high",
            "beer_preference": "craft_ipa",
            "trust_level": 0.8,
            "steve_risk_tolerance": 0.3,
            "bob_risk_tolerance": 0.8,
            "carl_risk_tolerance": 0.5,
        }

        logger.info(
            "🐹🐹🐹 Hamsters personality state initialized — "
            "Steve (careful), Bob (WILD), Carl (duct tape genius)"
        )

    # === DATABASE ===

    async def initialize_database(self):
        """Initialize database connection and load persisted state"""
        try:
            from .hamsters_database_integration import HamstersDatabaseIntegration
            self.db_integration = HamstersDatabaseIntegration(db_getter=self.db_getter)
            await self.db_integration.initialize()
            logger.info("🐹💾 Database integration initialized — Beer-powered records enabled!")
        except Exception as e:
            logger.error(f"🐹💥 Failed to initialize database: {e}", exc_info=True)
            self.db_integration = None

    # === DAILY RESET ===

    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if a new day has started.

        Called by orchestrator at top of run_pipeline().
        Beer counts DO NOT reset — they accumulate per job.
        Only daily tracking counters reset.
        """
        today = utc_now().date()
        if self._last_daily_reset == today:
            return

        logger.info("🐹📅 New day detected — resetting daily counters")
        self.beer_consumption_today = 0
        self.bob_supply_cupboard_raids_today = 0
        self.carl_duct_tape_rolls_used_today = 0.0
        self.carl_duct_tape_jobs_today = []
        self._daily = HamsterDailyTracking()
        self._last_daily_reset = today

    # === PERSONALITY BEHAVIORS ===

    def consume_beer(self, hamster: str, count: int, reason: str, complexity: float = 0.5):
        """
        Record beer consumption for a hamster.

        Increments individual hamster beer count, updates collective
        beer level, and logs with flavor text.
        """
        if hamster == 'steve':
            self.steve_beer_count += count
            logger.info(
                f"🐹🍺 Steve carefully sips {count} beer(s) — "
                f"'{reason}' (total: {self.steve_beer_count})"
            )
        elif hamster == 'bob':
            self.bob_beer_count += count
            logger.info(
                f"🐹🍺 Bob chugs {count} beer(s) — "
                f"'{reason}' *belch* (total: {self.bob_beer_count})"
            )
        elif hamster == 'carl':
            self.carl_beer_count += count
            logger.info(
                f"🐹🍺 Carl precisely measures {count} beer(s) — "
                f"'{reason}' (total: {self.carl_beer_count})"
            )
        else:
            logger.warning(f"🐹❓ Unknown hamster '{hamster}' tried to drink beer")
            return

        self.beer_consumption_today += count
        self._daily.beer_consumption_today += count

        event = BeerConsumptionEvent(
            hamster=hamster,
            beers_consumed=count,
            reason=reason,
            complexity_level=complexity,
            timestamp=utc_now()
        )
        self._daily.beer_events_today.append(event)

        self.collective_beer_level = self._calculate_collective_beer_level()

    def bob_has_wild_idea(self, idea_description: str):
        """
        Bob has a WILD IDEA!

        Increments wild idea counter, sets pending idea,
        and triggers beer consumption for everyone because that's
        how wild ideas work.
        """
        self.bob_wild_ideas += 1
        self.bob_wild_idea_pending = idea_description

        logger.warning(
            f"🐹💡 BOB HAS A WILD IDEA: '{idea_description}' "
            f"(idea #{self.bob_wild_ideas}) — "
            f"*The Stick is getting anxious*"
        )

        # Wild ideas = more beer for everyone
        beers_per_hamster = min(1 + self.bob_wild_ideas // 3, 3)
        for h in ('steve', 'bob', 'carl'):
            self.consume_beer(h, beers_per_hamster, f"Bob's wild idea: {idea_description}", 0.7)

    def bob_raids_cupboard(self, items_acquired: List[str] = None):
        """
        Bob raids the supply cupboard.

        Sets bob_at_cupboard, increments raids counter.
        Communication layer picks this up and notifies The Stick.
        """
        items_acquired = items_acquired or ['mystery_item']
        self.bob_at_cupboard = True
        self.bob_supply_cupboard_raids_today += 1
        self._daily.bob_supply_cupboard_raids_today += 1

        logger.warning(
            f"🐹🚨 BOB AT SUPPLY CUPBOARD! "
            f"Raid #{self.bob_supply_cupboard_raids_today} today — "
            f"Items: {items_acquired} — "
            f"*The Stick's anxiety INCREASING*"
        )

    def carl_calculates_duct_tape(self, complexity: str, job_type: str) -> DuctTapeJob:
        """
        Carl calculates how much duct tape is needed.

        Returns a DuctTapeJob with roll counts per grade.
        - Simple: regular tape only
        - Moderate: regular + premium
        - Complex: all grades including quantum
        - Quantum/emergency: Carl's Special (use wisely)
        """
        now = utc_now()

        if complexity == 'simple':
            job = DuctTapeJob(
                job_type=job_type, complexity=complexity,
                regular_rolls=1.0, premium_rolls=0.0,
                quantum_rolls=0.0, carls_special_rolls=0.0,
                total_rolls=1.0, timestamp=now
            )
        elif complexity == 'moderate':
            job = DuctTapeJob(
                job_type=job_type, complexity=complexity,
                regular_rolls=2.0, premium_rolls=1.0,
                quantum_rolls=0.0, carls_special_rolls=0.0,
                total_rolls=3.0, timestamp=now
            )
        elif complexity == 'complex':
            job = DuctTapeJob(
                job_type=job_type, complexity=complexity,
                regular_rolls=2.0, premium_rolls=2.0,
                quantum_rolls=1.0, carls_special_rolls=0.0,
                total_rolls=5.0, timestamp=now
            )
        else:  # quantum / emergency
            job = DuctTapeJob(
                job_type=job_type, complexity=complexity,
                regular_rolls=3.0, premium_rolls=2.0,
                quantum_rolls=2.0, carls_special_rolls=0.5,
                total_rolls=7.5, timestamp=now
            )

        self.carl_duct_tape_rolls_used_today += job.total_rolls
        self._daily.carl_duct_tape_rolls_used_today += job.total_rolls
        self.carl_duct_tape_jobs_today.append(job)
        self._daily.carl_duct_tape_jobs_today.append(job)

        # Update inventory
        for grade_attr, roll_count in [
            (DuctTapeGrade.REGULAR.value, job.regular_rolls),
            (DuctTapeGrade.PREMIUM.value, job.premium_rolls),
            (DuctTapeGrade.QUANTUM.value, job.quantum_rolls),
            (DuctTapeGrade.CARLS_SPECIAL.value, job.carls_special_rolls),
        ]:
            if roll_count > 0 and grade_attr in self.carl_duct_tape_inventory:
                self.carl_duct_tape_inventory[grade_attr] = max(
                    0, self.carl_duct_tape_inventory[grade_attr] - int(roll_count)
                )

        logger.info(
            f"🐹📏 Carl's duct tape assessment: {job.total_rolls:.1f} rolls "
            f"({complexity} {job_type} job) — "
            f"R:{job.regular_rolls} P:{job.premium_rolls} "
            f"Q:{job.quantum_rolls} CS:{job.carls_special_rolls}"
        )

        return job

    def record_telepathic_consensus(self, strength: float):
        """Update telepathic consensus strength"""
        self.telepathic_consensus_strength = max(0.0, min(1.0, strength))
        logger.info(
            f"🐹🧠 Telepathic consensus strength: {self.telepathic_consensus_strength:.2f}"
        )

    # === ANALYSIS TRACKING ===

    def record_analysis(self, success: bool):
        """Record an analysis result"""
        self.total_analyses += 1
        if success:
            self.successful_analyses += 1

    # === ALERT COOLDOWN ===

    def should_emit_alert(self) -> bool:
        """Check if enough time has passed since the last alert"""
        return self._alert_state.should_emit()

    def record_alert_emission(self):
        """Record that an alert was emitted"""
        self._alert_state.record_emission()

    def clear_alert_state(self):
        """Clear alert cooldown state"""
        self._alert_state.clear()

    # === COLLECTIVE STATE HELPERS ===

    def _calculate_collective_beer_level(self) -> BeerLevel:
        """Calculate the collective beer level of all three hamsters"""
        total_beers = self.steve_beer_count + self.bob_beer_count + self.carl_beer_count
        avg_beers = total_beers / 3

        if avg_beers < 1:
            return BeerLevel.SOBER
        elif avg_beers <= 2:
            return BeerLevel.TIPSY
        elif avg_beers <= 4:
            return BeerLevel.OPTIMAL
        elif avg_beers <= 6:
            return BeerLevel.ADVENTUROUS
        else:
            return BeerLevel.LEGENDARY

    @property
    def is_active(self) -> bool:
        """The Hamsters are always ready (unless all three pass out)"""
        collective_beer = self.steve_beer_count + self.bob_beer_count + self.carl_beer_count
        return collective_beer < 20

    # === STATUS ===

    def get_status(self) -> Dict[str, Any]:
        """Get full personality status for heartbeat / status endpoints"""
        return {
            "hamster_status": {
                "steve": {
                    "role": "analytical",
                    "risk_tolerance": self.steve_risk_tolerance,
                    "beer_count": self.steve_beer_count,
                    "current_task": self.steve_current_task,
                },
                "bob": {
                    "role": "wild",
                    "risk_tolerance": self.bob_risk_tolerance,
                    "beer_count": self.bob_beer_count,
                    "wild_ideas": self.bob_wild_ideas,
                    "wild_idea_pending": self.bob_wild_idea_pending,
                    "at_cupboard": self.bob_at_cupboard,
                    "hold_my_beer_count": self.bob_hold_my_beer_count,
                },
                "carl": {
                    "role": "duct_tape_expert",
                    "risk_tolerance": self.carl_risk_tolerance,
                    "beer_count": self.carl_beer_count,
                    "duct_tape_inventory": self.carl_duct_tape_inventory,
                    "duct_tape_rolls_used_today": self.carl_duct_tape_rolls_used_today,
                },
            },
            "collective_beer_level": self.collective_beer_level.value,
            "beer_consumption_today": self.beer_consumption_today,
            "telepathic_consensus_strength": self.telepathic_consensus_strength,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "personality_traits": self.personality_traits,
        }

    def health_check(self) -> Dict[str, Any]:
        """Health check data for heartbeat"""
        return {
            "is_active": self.is_active,
            "beer_level": self.collective_beer_level.value,
            "bob_wild_ideas": self.bob_wild_ideas,
            "telepathic_bond": (
                "strong" if self.telepathic_consensus_strength > 0.7
                else "moderate" if self.telepathic_consensus_strength > 0.4
                else "weak"
            ),
        }
