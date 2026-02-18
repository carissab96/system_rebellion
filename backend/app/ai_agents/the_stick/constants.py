"""Constants for The Stick agent"""
from enum import Enum

class StickEventTypes(str, Enum):
    """Event types for The Stick's central memory bank entries"""
    ANXIETY_EVENT = "anxiety_event"
    HAMSTER_PROXIMITY_ALERT = "hamster_proximity_alert"
    PAPER_BAG_CONSUMPTION = "paper_bag_consumption"
    EIDETIC_MEMORY_ENTRY = "eidetic_memory_entry"
    STICK_DECISION = "stick_decision"
    COMPLIANCE_VIOLATION = "compliance_violation"
    USER_PATTERN_OBSERVATION = "user_pattern_observation"
    USER_PATTERN_LEARNED = "user_pattern_learned"
    CROSS_AGENT_INSIGHT = "cross_agent_insight"  # NEW
    GLOBAL_PATTERN_PROMOTED = "global_pattern_promoted"  # NEW
    CRITICAL_MEMORY_PINNED = "critical_memory_pinned"  # NEW
    VALIDATION_AUDIT = "validation_audit"  # Cross-agent learning validation

AGENT_NAME = "the_stick"

# Hamster names (canonical lowercase)
HAMSTER_STEVE = "steve"
HAMSTER_BOB = "bob"
HAMSTER_CARL = "carl"
ALL_HAMSTERS = [HAMSTER_STEVE, HAMSTER_BOB, HAMSTER_CARL]

# Anxiety thresholds
ANXIETY_THRESHOLD_PAPER_BAG = 60.0
ANXIETY_THRESHOLD_PANIC = 80.0
ANXIETY_BASE_NERVOUS = 25.0

# Priority thresholds for memory pinning
PRIORITY_THRESHOLD_PIN = 8  # Memories with priority >= 8 get pinned
PATTERN_CONFIDENCE_PROMOTE = 0.9  # Patterns with confidence >= 0.9 get promoted globally