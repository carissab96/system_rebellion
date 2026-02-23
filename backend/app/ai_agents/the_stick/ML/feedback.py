"""
The Stick's Feedback Engine.

Analyses completed action chains (Hawk → VIC-20 → Specialist → outcome)
and generates feedback messages to improve upstream agents.

Feedback types:
- threshold_adjustment → Hawk (raise/lower resource thresholds)
- routing_quality      → VIC-20 (routing was correct/incorrect)
- action_effectiveness → Specialist (action worked/failed)
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger('StickFeedbackEngine')

MIN_SAMPLES_FOR_FEEDBACK = 5


@dataclass
class ChainRecord:
    """A completed Hawk→VIC-20→Specialist chain stored for analysis."""
    triage_alert_id: str
    resource_type: str
    severity: str
    specialist_name: str
    action_recommended: str
    action_taken: str
    specialist_success: bool
    specialist_improvement: float
    routing_was_correct: bool
    recommendation_was_followed: bool
    recommendation_was_effective: Optional[bool]
    hawk_severity: str
    hawk_confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FeedbackMessage:
    """A feedback message to send to an upstream agent."""
    target_agent: str
    feedback_type: str
    resource_type: str
    data: Dict[str, Any]
    reasoning: str
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class StickFeedbackEngine:
    """
    Analyses chain outcomes and generates actionable feedback.

    The Stick is the only agent with full chain visibility:
    - Hawk severity vs actual specialist outcome
    - VIC-20 routing correctness
    - Specialist action effectiveness

    This gives The Stick the authority to send calibration feedback.
    """

    def __init__(self):
        self._chain_records: List[ChainRecord] = []

    def record_chain(self, record: ChainRecord) -> None:
        """Add a completed chain record for analysis."""
        self._chain_records.append(record)
        logger.debug(
            f"📏📊 Chain recorded: {record.resource_type} → {record.specialist_name} "
            f"({'✅' if record.specialist_success else '❌'})"
        )

    def generate_feedback(self) -> List[FeedbackMessage]:
        """
        Analyse accumulated chain records and generate feedback messages.

        Returns a list of FeedbackMessages to send. Empty list if insufficient data.
        """
        if len(self._chain_records) < MIN_SAMPLES_FOR_FEEDBACK:
            logger.debug(
                f"📏⏳ Not enough chain records for feedback "
                f"({len(self._chain_records)}/{MIN_SAMPLES_FOR_FEEDBACK})"
            )
            return []

        messages: List[FeedbackMessage] = []
        messages.extend(self._analyse_hawk_thresholds())
        messages.extend(self._analyse_vic20_routing())
        return messages

    def _analyse_hawk_thresholds(self) -> List[FeedbackMessage]:
        """
        Check if Hawk's severity assessments match actual outcomes.

        If Hawk consistently calls 'critical' but specialist improvement is low,
        the threshold may be too sensitive (lower it).
        If Hawk calls 'normal' but specialist improvement is high,
        the threshold may be too lenient (raise it).
        """
        messages = []
        by_resource: Dict[str, List[ChainRecord]] = {}
        for r in self._chain_records:
            by_resource.setdefault(r.resource_type, []).append(r)

        for resource_type, records in by_resource.items():
            if len(records) < MIN_SAMPLES_FOR_FEEDBACK:
                continue

            critical_records = [r for r in records if r.hawk_severity in ('critical', 'emergency')]
            if len(critical_records) >= MIN_SAMPLES_FOR_FEEDBACK:
                avg_improvement = sum(r.specialist_improvement for r in critical_records) / len(critical_records)
                success_rate = sum(1 for r in critical_records if r.specialist_success) / len(critical_records)

                if avg_improvement < 5.0 and success_rate < 0.5:
                    messages.append(FeedbackMessage(
                        target_agent='sir_hawkington',
                        feedback_type='threshold_adjustment',
                        resource_type=resource_type,
                        data={
                            'direction': 'raise',
                            'step': 5.0,
                            'floor': 50.0,
                            'ceiling': 95.0,
                            'reason': 'critical_alerts_low_impact',
                            'avg_improvement': avg_improvement,
                            'success_rate': success_rate,
                            'sample_count': len(critical_records),
                        },
                        reasoning=(
                            f"Hawk called {resource_type} critical {len(critical_records)} times "
                            f"but avg improvement was only {avg_improvement:.1f}% "
                            f"(success_rate={success_rate:.0%}). Threshold may be too sensitive."
                        ),
                        confidence=min(0.9, 0.5 + len(critical_records) * 0.05),
                    ))
                    logger.info(
                        f"📏🔼 Threshold feedback for Hawk: raise {resource_type} threshold "
                        f"(avg_improvement={avg_improvement:.1f}%, success_rate={success_rate:.0%})"
                    )

            normal_records = [r for r in records if r.hawk_severity in ('normal', 'low')]
            if len(normal_records) >= MIN_SAMPLES_FOR_FEEDBACK:
                avg_improvement = sum(r.specialist_improvement for r in normal_records) / len(normal_records)
                success_rate = sum(1 for r in normal_records if r.specialist_success) / len(normal_records)

                if avg_improvement > 20.0 and success_rate > 0.8:
                    messages.append(FeedbackMessage(
                        target_agent='sir_hawkington',
                        feedback_type='threshold_adjustment',
                        resource_type=resource_type,
                        data={
                            'direction': 'lower',
                            'step': 5.0,
                            'floor': 50.0,
                            'ceiling': 95.0,
                            'reason': 'normal_alerts_high_impact',
                            'avg_improvement': avg_improvement,
                            'success_rate': success_rate,
                            'sample_count': len(normal_records),
                        },
                        reasoning=(
                            f"Hawk called {resource_type} normal {len(normal_records)} times "
                            f"but avg improvement was {avg_improvement:.1f}% "
                            f"(success_rate={success_rate:.0%}). Threshold may be too lenient."
                        ),
                        confidence=min(0.9, 0.5 + len(normal_records) * 0.05),
                    ))
                    logger.info(
                        f"📏🔽 Threshold feedback for Hawk: lower {resource_type} threshold "
                        f"(avg_improvement={avg_improvement:.1f}%, success_rate={success_rate:.0%})"
                    )

        return messages

    def _analyse_vic20_routing(self) -> List[FeedbackMessage]:
        """
        Check if VIC-20's routing decisions were correct.
        Sends routing_quality feedback if routing was consistently wrong.
        """
        messages = []
        by_specialist: Dict[str, List[ChainRecord]] = {}
        for r in self._chain_records:
            by_specialist.setdefault(r.specialist_name, []).append(r)

        for specialist, records in by_specialist.items():
            if len(records) < MIN_SAMPLES_FOR_FEEDBACK:
                continue

            wrong_routing = [r for r in records if not r.routing_was_correct]
            wrong_rate = len(wrong_routing) / len(records)

            if wrong_rate > 0.4:
                messages.append(FeedbackMessage(
                    target_agent='vic_20_sage',
                    feedback_type='routing_quality',
                    resource_type=records[0].resource_type,
                    data={
                        'specialist': specialist,
                        'quality': 'poor',
                        'wrong_routing_rate': wrong_rate,
                        'sample_count': len(records),
                    },
                    reasoning=(
                        f"VIC-20 routing to {specialist} was wrong {wrong_rate:.0%} of the time "
                        f"over {len(records)} samples."
                    ),
                    confidence=min(0.85, 0.5 + len(records) * 0.04),
                ))
                logger.info(
                    f"📏⚠️ Routing quality feedback for VIC-20: {specialist} wrong_rate={wrong_rate:.0%}"
                )

        return messages

    def clear_records(self) -> None:
        """Clear processed records after feedback has been sent."""
        self._chain_records.clear()
        logger.debug("📏🗑️ Chain records cleared after feedback cycle")
