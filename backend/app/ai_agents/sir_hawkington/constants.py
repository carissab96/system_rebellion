# app/ai_agents/sir_hawkington/constants.py
"""
Sir Hawkington Von Monitorious III Constants
Event types, priorities, and aristocratic standards
"""

from enum import Enum
from app.ai_agents.constants import AgentNames

# Agent identifier
AGENT_NAME = AgentNames.SIR_HAWKINGTON.value

class HawkingtonEventTypes(str, Enum):
    """Event types for Sir Hawkington in CMB"""
    
    # Decision events
    ARISTOCRATIC_DECISION = "hawkington.aristocratic_decision"
    TRIAGE_DECISION = "hawkington.triage_decision"
    
    # Monocle events
    MONOCLE_YEET = "hawkington.monocle_yeet"
    MONOCLE_POLISHED = "hawkington.monocle_polished"
    
    # Issue classification
    ISSUE_CLASSIFIED = "hawkington.issue_classified"
    ISSUE_TRIAGED = "hawkington.issue_triaged"
    
    # Learning events
    BEHAVIOR_OBSERVED = "hawkington.behavior_observed"
    PATTERN_LEARNED = "hawkington.pattern_learned"
    TRIAGE_PATTERN_DISCOVERED = "hawkington.triage_pattern_discovered"
    
    # Quality events
    DATA_QUALITY_FAILURE = "hawkington.data_quality_failure"
    ARISTOCRATIC_STANDARD_VIOLATED = "hawkington.aristocratic_standard_violated"

# Priority mapping
PRIORITY_MAP = {
    # Critical/Emergency
    "critical": 5,
    "emergency": 5,
    "monocle_yeeted": 5,
    
    # High
    "high": 4,
    "alert": 4,
    
    # Medium
    "medium": 3,
    "concern": 3,
    
    # Low
    "low": 2,
    "normal": 2,
    
    # Routine
    "routine": 1,
    "observation": 1
}

# Triage thresholds
TRIAGE_THRESHOLDS = {
    "normal_threshold": 0.30,
    "medium_threshold": 0.65,
    "emergency_threshold": 0.85,
    "monocle_yeet_threshold": 0.95
}

# Learning thresholds
LEARNING_THRESHOLDS = {
    "min_observations": 25,  # Lower for Hawkington since triage is less frequent
    "pattern_confidence_threshold": 0.7,
    "pattern_promotion_threshold": 0.9,
    "cross_validation_required": 5
}

# Hawkington-specific learning types
class HawkingtonLearningTypes(str, Enum):
    """Learning types specific to Sir Hawkington"""
    TRIAGE_PATTERN = "triage_pattern"
    SEVERITY_ASSESSMENT = "severity_assessment"
    MONOCLE_YEET_TRIGGER = "monocle_yeet_trigger"
    DATA_QUALITY_PATTERN = "data_quality_pattern"
    ROUTING_EFFECTIVENESS = "routing_effectiveness"

# Memory types for pinning
class HawkingtonMemoryTypes(str, Enum):
    """Memory types for Sir Hawkington"""
    CRITICAL_TRIAGE = "critical_triage"
    MONOCLE_YEET = "monocle_yeet"
    TRIAGE_DECISION = "triage_decision"
    DATA_QUALITY_INCIDENT = "data_quality_incident"
    ARISTOCRATIC_WISDOM = "aristocratic_wisdom"

# Triage routing types
class TriageRoutingTypes(str, Enum):
    STICK_DIRECT = "stick_direct"
    VIC20_COORDINATION = "vic20_coordination"
    VIC20_EMERGENCY = "vic20_emergency"
    CPU_SPECIALIST = "cpu_specialist"

# Monocle states
class MonocleStates(str, Enum):
    POLISHED = "polished"
    ADJUSTED = "adjusted"
    FOGGED = "fogged"
    YEETED = "yeeted"
    CLEANING = "cleaning"

# Aristocratic responses
ARISTOCRATIC_RESPONSES = {
    "data_quality_poor": "🧐💥 I say! This data quality is beneath aristocratic standards!",
    "system_normal": "🧐 All systems operating within acceptable parameters, quite satisfactory.",
    "concern_raised": "🧐 *adjusts monocle* This warrants measured concern.",
    "alert_triggered": "🧐⚠️ *monocle fogs* Serious concern detected!",
    "critical_state": "🧐🚨 *YEETS MONOCLE* ARISTOCRATIC HORROR!",
    "triage_complete": "🧐✨ Triage completed with distinguished precision."
}

__all__ = [
    'AGENT_NAME',
    'HawkingtonEventTypes',
    'PRIORITY_MAP',
    'TRIAGE_THRESHOLDS',
    'LEARNING_THRESHOLDS',
    'HawkingtonLearningTypes',
    'HawkingtonMemoryTypes',
    'TriageRoutingTypes',
    'MonocleStates',
    'ARISTOCRATIC_RESPONSES',
    'HawkingtonMemoryCategories',
    'DATA_QUALITY_THRESHOLDS',
    'TRIAGE_ACCURACY_THRESHOLDS'
]
# Memory categories for agent-specific table
class HawkingtonMemoryCategories(str, Enum):
    """Memory categories for SirHawkingtonMemoryBank"""
    QUALITY_ANALYSIS = "quality_analysis"
    QUALITY_ALERT = "quality_alert"
    CRITICAL_ANALYSIS = "critical_analysis"
    TRIAGE = "triage"
    MONOCLE_YEET = "monocle_yeet"

# Data quality thresholds
DATA_QUALITY_THRESHOLDS = {
    'required_metrics': ['cpu_usage', 'memory_usage', 'disk_usage'],
    'valid_range': (0.0, 100.0),
    'yeet_on_missing': True,
    'yeet_on_invalid': True
}

# Triage accuracy thresholds for learning
TRIAGE_ACCURACY_THRESHOLDS = {
    'excellent': 0.95,
    'good': 0.85,
    'acceptable': 0.70,
    'poor': 0.50
}

# Update __all__ export
__all__ = [
    'AGENT_NAME',
    'HawkingtonEventTypes',
    'PRIORITY_MAP',
    'TRIAGE_THRESHOLDS',
    'LEARNING_THRESHOLDS',
    'HawkingtonLearningTypes',
    'HawkingtonMemoryTypes',
    'TriageRoutingTypes',
    'MonocleStates',
    'ARISTOCRATIC_RESPONSES',
    'HawkingtonMemoryCategories',  # NEW
    'DATA_QUALITY_THRESHOLDS',     # NEW
    'TRIAGE_ACCURACY_THRESHOLDS'   # NEW
]