"""
Outcome reporting protocol.
Standardizes how agents report action outcomes up the chain.

Flow: Specialist → VIC-20 → The Stick → feedback to everyone
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime, timezone


@dataclass
class ActionOutcome:
    """Reported by specialists after executing an action."""
    agent_name: str
    action_taken: str
    goal: str
    resource_type: str
    severity: str

    success: bool
    improvement: float

    pre_metrics: Dict[str, Any] = field(default_factory=dict)
    post_metrics: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    error: Optional[str] = None

    coordination_request_id: Optional[str] = None
    triage_alert_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RoutingOutcome:
    """Reported by VIC-20 to The Stick after a specialist reports back."""
    specialist_name: str
    action_recommended: str
    action_taken: str
    resource_type: str
    severity: str

    specialist_success: bool
    specialist_improvement: float

    routing_was_correct: bool
    recommendation_was_followed: bool
    recommendation_was_effective: Optional[bool]

    hawk_severity: str = ''
    hawk_confidence: float = 0.0

    coordination_request_id: Optional[str] = None
    triage_alert_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
