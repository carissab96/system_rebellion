from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

class ComplianceState(Enum):
    COMPLIANT = "compliant"
    MINOR_VIOLATION = "minor_violation"
    MAJOR_VIOLATION = "major_violation"
    CRITICAL_VIOLATION = "critical_violation"
    OPTIMIZING = "optimizing"
    LEARNING = "learning"

class StickDecisionType(Enum):
    USER_PATTERN_OPTIMIZATION = "user_pattern_optimization"
    CONFIGURATION_PROFILE_SWITCH = "configuration_profile_switch"
    COMPLIANCE_ENFORCEMENT = "compliance_enforcement"
    PREDICTIVE_CONFIGURATION = "predictive_configuration"
    BEHAVIOR_ANOMALY_DETECTION = "behavior_anomaly_detection"
    SYSTEM_PREPARATION = "system_preparation"

@dataclass
class StickDecision:
    decision_type: StickDecisionType
    compliance_state: ComplianceState
    configuration_target: str
    optimization_parameters: Dict[str, Any]
    user_pattern_confidence: float
    compliance_explanation: str
    technical_details: Dict[str, Any]
    expected_improvement: float
    confidence_level: float
    timestamp: datetime

@dataclass
class UserPattern:
    user_id: str
    pattern_type: str
    time_based_patterns: Dict[int, Dict[str, Any]]  # hour -> pattern data
    activity_patterns: Dict[str, Dict[str, Any]]    # activity -> usage data
    compliance_history: Dict[str, Any]
    confidence_score: float
    learning_sessions: int
    last_updated: datetime
    
@dataclass
class ComplianceViolation:
    violation_type: str
    measured_value: float
    threshold_value: float
    severity: str
    timestamp: datetime
    user_id: str
    recommendation: str
    resolved: bool = False
    
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