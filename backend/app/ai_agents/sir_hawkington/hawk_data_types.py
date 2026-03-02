"""
Sir Hawkington — Data Types
=============================

Dataclasses and enums that define Hawkington's state and personality artifacts.

Mirrors the structure of meth_snail/data_types.py.
No logic. No decisions. Pure structure.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime


class MonocleState(Enum):
    """The distinguished state of Sir Hawkington's monocle"""
    POLISHED   = "polished"    # All is well
    ADJUSTED   = "adjusted"    # Minor concern noted
    FOGGED     = "fogged"      # Data quality suspect
    YEETED     = "yeeted"      # Something has gone catastrophically wrong
    CLEANING   = "cleaning"    # Recovering from a yeet


class TriageSeverity(Enum):
    """Severity levels Hawkington assigns after assessing incoming data"""
    NORMAL    = "normal"
    MEDIUM    = "medium"
    HIGH      = "high"
    EMERGENCY = "emergency"


class TriageRouting(Enum):
    """Where Hawkington routes a triage decision"""
    STICK_DIRECT      = "stick_direct"       # Earl grey path — log only
    VIC20_COORDINATION = "vic20_coordination" # Single-agent coordination
    VIC20_EMERGENCY   = "vic20_emergency"    # Monocle yeet — multi-agent


@dataclass
class MonocleYeetIncident:
    """
    Record of a monocle yeet incident.

    Yeeting happens when:
    - Incoming data is missing or empty (upstream failure)
    - System is off the rails and multi-agent emergency is required
    """
    timestamp:       datetime
    reason:          str
    resource_type:   str
    yeet_intensity:  str        # "mild" | "moderate" | "severe" | "catastrophic"
    user_id:         Optional[str] = None


@dataclass
class EarlGreyState:
    """
    Tracks Sir Hawkington's tea consumption.

    Sips happen on every dismiss/normal cycle.
    Interruptions happen on every escalation.
    Together they form the system_calm_ratio.
    """
    sips_today:           int   = 0
    cups_consumed:        int   = 0
    current_cup_sips:     int   = 0
    sips_per_cup:         int   = 12   # A proper cup takes 12 sips
    interrupted_today:    int   = 0
    last_reset_date:      Optional[object] = None   # datetime.date

    @property
    def system_calm_ratio(self) -> float:
        """Near 1.0 = calm system. Near 0.0 = constant escalation storms."""
        total = self.sips_today + self.interrupted_today
        return self.sips_today / max(1, total)

    @property
    def cup_completion_rate(self) -> float:
        total = self.cups_consumed + self.interrupted_today
        return self.cups_consumed / max(1, total)

    def to_dict(self) -> dict:
        return {
            'sips_today':          self.sips_today,
            'cups_consumed':       self.cups_consumed,
            'current_cup_progress': f"{self.current_cup_sips}/{self.sips_per_cup}",
            'interruptions_today': self.interrupted_today,
            'system_calm_ratio':   self.system_calm_ratio,
            'cup_completion_rate': self.cup_completion_rate,
        }


@dataclass
class AlertStateRecord:
    """
    Tracks the live state of a single resource alert for cooldown management.
    Prevents frontend spam on ongoing alerts.
    """
    state:               str       # "NEW" | "ONGOING" | "RESOLVED"
    severity:            str
    last_emission_time:  datetime
    first_seen_time:     datetime
