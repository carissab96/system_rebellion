"""
The Hamsters — Data Types
==========================

Pure dataclasses and enums. No logic. No decisions.
These define WHO the hamsters are and WHAT they track.

Migrated from decision_engine_sbcV3.py + SKILL.md spec.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone


class BeerLevel(Enum):
    """The Hamsters' operational fuel levels"""
    SOBER = "sober"              # Error state - cannot function
    TIPSY = "tipsy"              # Minimum operational (1-2 beers avg)
    OPTIMAL = "optimal"          # Peak performance (3-4 beers avg)
    ADVENTUROUS = "adventurous"  # Hold my beer territory (5-6 beers avg)
    LEGENDARY = "legendary"      # Carl's doing calculus with duct tape (7+ beers avg)


class DuctTapeGrade(Enum):
    REGULAR = "regular"
    PREMIUM = "premium"
    QUANTUM = "quantum"
    CARLS_SPECIAL = "carls_special"  # Effects permanent


class HamstersPriority(Enum):
    BEER_BREAK = "beer_break"
    ROUTINE_MAINTENANCE = "routine_maintenance"
    SUPPLY_CLOSET_RAID = "supply_closet_raid"
    HOLD_MY_BEER = "hold_my_beer"
    FULL_REDNECK = "full_redneck"


@dataclass
class DuctTapeJob:
    """Carl's duct tape assessment for a single job"""
    job_type: str
    complexity: str  # 'simple', 'moderate', 'complex', 'quantum'
    regular_rolls: float
    premium_rolls: float
    quantum_rolls: float
    carls_special_rolls: float
    total_rolls: float
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            'job_type': self.job_type,
            'complexity': self.complexity,
            'regular_rolls': self.regular_rolls,
            'premium_rolls': self.premium_rolls,
            'quantum_rolls': self.quantum_rolls,
            'carls_special_rolls': self.carls_special_rolls,
            'total_rolls': self.total_rolls,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class BeerConsumptionEvent:
    """Record of a hamster drinking beer"""
    hamster: str  # 'steve', 'bob', 'carl'
    beers_consumed: int
    reason: str
    complexity_level: float
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            'hamster': self.hamster,
            'beers_consumed': self.beers_consumed,
            'reason': self.reason,
            'complexity_level': self.complexity_level,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class AlertStateRecord:
    """Cooldown tracking for alert emissions"""
    last_alert_time: Optional[datetime] = None
    cooldown_seconds: float = 30.0
    alerts_emitted: int = 0

    def should_emit(self) -> bool:
        if self.last_alert_time is None:
            return True
        elapsed = (datetime.now(timezone.utc) - self.last_alert_time).total_seconds()
        return elapsed >= self.cooldown_seconds

    def record_emission(self):
        self.last_alert_time = datetime.now(timezone.utc)
        self.alerts_emitted += 1

    def clear(self):
        self.last_alert_time = None
        self.alerts_emitted = 0


@dataclass
class HamsterDailyTracking:
    """Daily counters for the trio — resets each day"""
    beer_consumption_today: int = 0
    bob_supply_cupboard_raids_today: int = 0
    carl_duct_tape_rolls_used_today: float = 0.0
    carl_duct_tape_jobs_today: List[DuctTapeJob] = field(default_factory=list)
    beer_events_today: List[BeerConsumptionEvent] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'beer_consumption_today': self.beer_consumption_today,
            'bob_supply_cupboard_raids_today': self.bob_supply_cupboard_raids_today,
            'carl_duct_tape_rolls_used_today': self.carl_duct_tape_rolls_used_today,
            'carl_duct_tape_jobs_today': [j.to_dict() for j in self.carl_duct_tape_jobs_today],
            'beer_events_today': [e.to_dict() for e in self.beer_events_today],
        }
