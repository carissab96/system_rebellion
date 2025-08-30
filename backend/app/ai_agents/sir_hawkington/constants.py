# app/ai_agents/sir_hawkington/constants.py
from enum import Enum

class HawkingtonEventTypes(str, Enum):
    """Event types for Sir Hawkington's central memory bank entries"""
    TRIAGE_DECISION = "triage_decision"
    MONOCLE_YEET = "monocle_yeet"
    SYSTEM_ANALYSIS = "system_analysis"
    DATA_QUALITY_ASSESSMENT = "data_quality_assessment"
    ARISTOCRATIC_DECISION = "aristocratic_decision"
    PERFORMANCE_MONITORING = "performance_monitoring"
    AGENT_COORDINATION = "agent_coordination"
    EMERGENCY_ROUTING = "emergency_routing"
    PATTERN_ANALYSIS = "pattern_analysis"
    USER_PATTERN_LEARNED = "user_pattern_learned"
    USER_PATTERN_OBSERVATION = "user_pattern_observation"

AGENT_NAME = "sir_hawkington"

# Triage routing types for memory categorization
class TriageRoutingTypes(str, Enum):
    STICK_DIRECT = "stick_direct"
    VIC20_COORDINATION = "vic20_coordination"
    VIC20_EMERGENCY = "vic20_emergency"
    CPU_SPECIALIST = "cpu_specialist"

# Monocle states for memory tracking
class MonocleStates(str, Enum):
    POLISHED = "polished"
    ADJUSTED = "adjusted"
    FOGGED = "fogged"
    YEETED = "yeeted"
    CLEANING = "cleaning"