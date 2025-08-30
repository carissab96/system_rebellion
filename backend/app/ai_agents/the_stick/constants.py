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