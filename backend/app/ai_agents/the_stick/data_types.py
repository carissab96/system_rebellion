from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)

class AnxietyLevel(Enum):
    CALM = "calm"  # 0-20%
    NERVOUS = "nervous"  # 20-40%
    ANXIOUS = "anxious"  # 40-60%
    PANICKING = "panicking"  # 60-80%
    FULL_PANIC = "full_panic"  # 80-100%
    PAPER_BAG_BREATHING = "paper_bag_breathing"  # Emergency state

class ComplianceState(Enum):
    COMPLIANT = "compliant"
    MINOR_VIOLATION = "minor_violation"
    MAJOR_VIOLATION = "major_violation"
    CRITICAL_VIOLATION = "critical_violation"
    OPTIMIZING = "optimizing"
    LEARNING = "learning"
    ANXIETY_DRIVEN_HYPERFOCUS = "anxiety_driven_hyperfocus"

class StickDecisionType(Enum):
    USER_PATTERN_OPTIMIZATION = "user_pattern_optimization"
    CONFIGURATION_PROFILE_SWITCH = "configuration_profile_switch"
    COMPLIANCE_ENFORCEMENT = "compliance_enforcement"
    PREDICTIVE_CONFIGURATION = "predictive_configuration"
    BEHAVIOR_ANOMALY_DETECTION = "behavior_anomaly_detection"
    SYSTEM_PREPARATION = "system_preparation"
    ANXIETY_TRIGGERED_SCAN = "anxiety_triggered_scan"
    HAMSTER_PROXIMITY_ALERT = "hamster_proximity_alert"
    PANIC_MODE_DOCUMENTATION = "panic_mode_documentation"

@dataclass
class StickDecision:
    decision_type: StickDecisionType
    compliance_state: ComplianceState
    anxiety_level: AnxietyLevel
    configuration_target: str
    optimization_parameters: Dict[str, Any]
    user_pattern_confidence: float
    compliance_explanation: str
    anxiety_explanation: str
    technical_details: Dict[str, Any]
    expected_improvement: float
    confidence_level: float
    paper_bags_consumed: int
    timestamp: datetime
    
    @property
    def is_panicking(self) -> bool:
        """Check if The Stick is in panic mode"""
        return self.anxiety_level in [AnxietyLevel.PANICKING, AnxietyLevel.FULL_PANIC, AnxietyLevel.PAPER_BAG_BREATHING]

@dataclass
class UserPattern:
    user_id: str
    pattern_type: str
    time_based_patterns: Dict[int, Dict[str, Any]]  # hour -> pattern data
    activity_patterns: Dict[str, Dict[str, Any]]    # activity -> usage data
    compliance_history: Dict[str, Any]
    anxiety_correlation: Dict[str, float]  # activity -> anxiety level
    confidence_score: float
    learning_sessions: int
    last_updated: datetime
    stick_memory_notes: List[str]  # The Stick's obsessive notes
    
@dataclass
class ComplianceViolation:
    violation_type: str
    measured_value: float
    threshold_value: float
    anxiety_adjusted_threshold: float  # Anxiety makes thresholds stricter
    severity: str
    timestamp: datetime
    user_id: str
    recommendation: str
    anxiety_impact: float  # How much this increased anxiety
    resolved: bool = False
    paper_bags_triggered: int = 0
    
@dataclass
class ConfigurationProfile:
    profile_name: str
    user_id: str
    activity_type: str
    configuration_parameters: Dict[str, Any]
    usage_confidence: float
    performance_metrics: Dict[str, Any]
    created_from_pattern: bool
    times_applied: int
    success_rate: float
    last_used: datetime
    anxiety_level_when_created: float
    stick_notes: List[str]  # Obsessive documentation

@dataclass
class AnxietyEvent:
    timestamp: datetime
    trigger: str
    anxiety_level_before: float
    anxiety_level_after: float
    multiplier: float
    paper_bags_consumed: int
    hamster_involved: bool
    resolution: str

@dataclass
class HamsterProximityAlert:
    timestamp: datetime
    active_hamsters: List[str]  # Steve, Bob, Carl
    locations: Dict[str, str]
    anxiety_multiplier: float
    panic_level: str  # LOW, MODERATE, HIGH, MAXIMUM
    infrastructure_risk: str
    stick_response: str
    paper_bags_consumed: int

@dataclass
class PaperBagInventory:
    current_stock: int
    consumption_today: int
    consumption_week: int
    last_resupply: datetime
    next_resupply_needed: datetime
    average_daily_consumption: float
    emergency_reserve: int
    anxiety_threshold_for_use: float

@dataclass
class StickMemoryEntry:
    timestamp: datetime
    event_type: str
    details: Dict[str, Any]
    anxiety_level: float
    importance: str  # LOW, MEDIUM, HIGH, CRITICAL, EIDETIC
    related_hamsters: List[str]
    compliance_impact: str
    never_forget: bool  # Some things The Stick NEVER forgets

@dataclass
class ValidationAuditEntry:
    """
    Audit trail for The Stick's validation decisions.
    Written to CentralMemoryBank for VIC-20's oversight.
    
    Uses learning_type as discriminator:
    - "cross_agent_learning" - Cross-agent learning interactions
    - "threshold_adjustment" - Terry's learned threshold adjustments
    - "action_effectiveness" - Terry's action effectiveness scoring
    
    Fields map differently based on learning_type:
    - For cross-agent: source_agent != target_agent, all metrics used
    - For threshold: source_agent == target_agent (both Terry), effectiveness_score = shift magnitude
    - For action: source_agent == target_agent (both Terry), success_rate maps directly
    """
    timestamp: datetime
    interaction_id: str
    source_agent: str
    target_agent: str
    learning_type: str  # Discriminator: "cross_agent_learning", "threshold_adjustment", "action_effectiveness"
    
    # Validation result
    validation_result: bool  # pass or fail
    reasoning: str           # WHY it passed or failed
    
    # Threshold snapshot (critical for audit)
    thresholds_applied: Dict[str, Any]  # snapshot of active thresholds
    threshold_state: str                 # "initial" or "mature"
    
    # Re-validation tracking
    was_retry: bool = False
    previous_validation_id: Optional[str] = None
    retry_count: int = 0
    
    # Validation metrics (interpretation depends on learning_type)
    effectiveness_score: Optional[float] = None  # Cross-agent: effectiveness | Threshold: shift magnitude | Action: N/A
    success_rate: Optional[float] = None         # Cross-agent: success rate | Threshold: N/A | Action: success rate
    pattern_similarity: Optional[float] = None   # Cross-agent: similarity | Threshold: N/A | Action: consistency
    interaction_age_hours: Optional[float] = None  # Age of the learning record
    
    # The Stick's anxiety level during validation
    stick_anxiety_level: float = 25.0