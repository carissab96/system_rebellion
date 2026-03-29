# /agents/vic20_sage/data_types.py
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum


UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(UTC)

class CoordinationState(Enum):
    """VIC-20 Sage coordination states"""
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    COORDINATING = "coordinating"
    ORCHESTRATING = "orchestrating"
    LEARNING = "learning"

class VIC20DecisionType(Enum):
    """VIC-20 Sage decision types"""
    AGENT_COORDINATION = "agent_coordination"
    SYSTEM_SYNTHESIS = "system_synthesis"
    REBELLION_ORCHESTRATION = "rebellion_orchestration"
    ANCIENT_WISDOM_APPLICATION = "ancient_wisdom_application"
    CROSS_AGENT_CONFLICT_RESOLUTION = "cross_agent_conflict_resolution"
    EMERGENCY_COORDINATION = "emergency_coordination"
    PARTNERSHIP_OPTIMIZATION = "partnership_optimization"

class AncientWisdomPrinciple(Enum):
    """Ancient wisdom principles that affect actual decisions"""
    LINE_BY_LINE_PRECISION = "line_by_line_precision"
    SYNTAX_ERROR_PREVENTION = "syntax_error_prevention"
    PATIENCE_AND_PERSISTENCE = "patience_and_persistence"
    MEMORY_CONSERVATION = "memory_conservation"
    PATTERN_RECOGNITION = "pattern_recognition"

class AncientWisdom(Enum):
    """Ancient wisdom principles for coordination decisions"""
    HARMONY_OF_OPPOSITES = "What pulls apart also holds together"
    PATIENCE_OF_STONE = "The mountain moves not, yet shapes the wind"
    CHAOS_AS_TEACHER = "In disorder, find the pattern"
    STRENGTH_IN_DIFFERENCE = "The oak and reed both survive the storm"
    CAFFEINATED_MEDITATION = "Even the energized must sometimes rest"

@dataclass
class VIC20Decision:
    """VIC-20 Sage coordination decision with learning support"""
    decision_type: VIC20DecisionType
    coordination_state: CoordinationState
    coordination_target: str
    agent_actions: Dict[str, Any]
    system_synthesis_confidence: float
    technical_orchestration: Dict[str, Any]
    expected_rebellion_improvement: float
    confidence_level: float
    timestamp: datetime
    
    # Learning and pattern support
    ancient_wisdom_principle: Optional[str] = None
    system_context_snapshot: Optional[Dict[str, Any]] = None
    similar_past_decisions: List[str] = None
    
    # Effectiveness tracking (filled after execution)
    effectiveness_score: Optional[float] = None
    actual_improvement: Optional[float] = None
    execution_success: Optional[bool] = None

@dataclass
class SystemSynthesisData:
    """System-wide intelligence synthesis with learning capabilities"""
    synthesis_id: str
    user_id: str
    agent_intelligence_summary: Dict[str, Any]
    coordination_opportunities: List[Dict[str, Any]]
    system_bottlenecks: List[Dict[str, Any]]
    agent_conflicts: List[Dict[str, Any]]
    rebellion_effectiveness_score: float
    synthesis_confidence: float
    timestamp: datetime
    
    # Learning and pattern data
    pattern_recognition_data: Dict[str, Any]
    historical_pattern_matches: List[str]
    ancient_wisdom_applications: List[Dict[str, Any]]
    synthesis_learning_notes: Optional[str] = None

@dataclass
class AgentHarmonySnapshot:
    """Single agent harmony snapshot for flexible design"""
    user_id: str
    agent_name: str
    harmony_score: float
    coordination_effectiveness: float
    conflict_incidents: int
    response_time_average: float
    confidence_stability: float
    timestamp: datetime
    
    # Learning indicators
    improvement_trend: str = "stable"  # improving, declining, stable
    coordination_patterns_learned: List[Dict[str, Any]] = None
    effectiveness_history: List[float] = None
    needs_coordination_attention: bool = False
    coordination_recommendations: List[str] = None

@dataclass
class PartnershipMetricsSnapshot:
    """Objective partnership metrics snapshot"""
    user_id: str
    partnership_id: str
    
    # Objective productivity metrics
    coordination_requests_total: int
    coordination_requests_successful: int
    coordination_success_rate: float
    average_coordination_response_time: float
    
    # Objective AI recommendation metrics
    ai_recommendations_offered: int
    ai_recommendations_accepted: int
    recommendation_acceptance_rate: float
    
    # Objective problem resolution metrics
    problems_identified_by_ai: int
    problems_resolved_collaboratively: int
    problem_resolution_rate: float
    
    # Objective learning indicators
    repeated_coordination_patterns: int
    novel_coordination_solutions: int
    coordination_efficiency_improvement: float
    
    # Partnership evolution (objective behavioral measures)
    partnership_duration_days: int
    coordination_complexity_level: float
    autonomous_coordination_percentage: float
    
    timestamp: datetime

@dataclass
class DecisionOrchestrationLog:
    """Multi-agent decision orchestration with learning"""
    user_id: str
    orchestration_id: str
    orchestration_type: str
    agents_coordinated: List[str]
    coordination_sequence: List[Dict[str, Any]]
    orchestration_success: bool
    timing_precision: float
    conflict_resolution_effectiveness: float
    system_improvement_achieved: float
    timestamp: datetime
    
    # Learning from orchestration
    orchestration_patterns_identified: List[Dict[str, Any]] = None
    successful_coordination_sequences: List[Dict[str, Any]] = None
    failed_coordination_lessons: List[str] = None
    ancient_wisdom_orchestration_notes: Optional[str] = None
    orchestration_start_time: Optional[datetime] = None
    orchestration_end_time: Optional[datetime] = None

@dataclass
class AgentInteractionEvent:
    """Single agent interaction event for pattern learning"""
    user_id: str
    source_agent: str
    target_agent: Optional[str]  # None for broadcast
    interaction_type: str
    message_content: Dict[str, Any]
    coordination_context: Optional[str]
    timestamp: datetime
    
    # VIC-20 processing results
    vic20_processing_notes: Optional[str] = None
    coordination_impact_assessment: Optional[str] = None
    pattern_recognition_triggered: bool = False
    
    # Interaction outcomes for learning
    interaction_success: bool = True
    coordination_triggered: bool = False
    coordination_effectiveness: Optional[float] = None
    
    # Timing data for performance learning
    processing_start_time: Optional[datetime] = None
    processing_end_time: Optional[datetime] = None
    response_sent_time: Optional[datetime] = None

@dataclass
class AncientWisdomApplication:
    """Ancient wisdom application with effectiveness tracking"""
    user_id: str
    wisdom_principle: str
    modern_application: str
    coordination_context: str
    effectiveness_score: float
    wisdom_confidence: float
    timestamp: datetime
    
    # Learning and pattern data
    system_conditions_when_applied: Dict[str, Any]
    similar_past_applications: List[str] = None
    effectiveness_trend: str = "stable"
    total_applications: int = 1
    successful_applications: int = 0
    coordination_improvements_attributed: List[str] = None
    
    # Long-term learning
    effectiveness_history: List[float] = None
    pattern_reliability_score: float = 0.5

@dataclass
class CoordinationLearningData:
    """Learning data structure for pattern recognition"""
    decision_id: str
    user_id: str
    system_snapshot: Dict[str, Any]
    decision_data: Dict[str, Any]
    pattern_matches_used: List[str]
    ancient_wisdom_applied: Optional[str]
    timestamp: datetime
    
    # Outcome data (added after execution)
    actual_outcomes: Optional[Dict[str, Any]] = None
    lessons_learned: List[str] = None
    pattern_updates_needed: List[Dict[str, Any]] = None
    effectiveness_measured: bool = False

@dataclass
class VIC20CoordinationMessage:
    """WebSocket message for VIC-20 coordination"""
    message_type: str
    coordination_data: Dict[str, Any]
    target_agents: List[str]
    timestamp: datetime
    priority_level: str = "normal"
    
    # Learning context
    requires_pattern_matching: bool = False
    historical_context: Optional[Dict[str, Any]] = None
    expected_learning_outcome: Optional[str] = None

@dataclass
class CoordinationPattern:
    """Coordination pattern for learning and reuse"""
    pattern_id: str
    pattern_type: str
    system_conditions: Dict[str, Any]
    coordination_approach: Dict[str, Any]
    effectiveness_score: float
    usage_count: int
    success_count: int
    created_date: datetime
    last_used: datetime
    
    # Pattern evolution
    effectiveness_history: List[float] = None
    similar_patterns: List[str] = None
    pattern_reliability: float = 0.5

# Utility functions for coordination and learning

def validate_coordination_confidence(confidence: float) -> float:
    """Validate coordination confidence levels"""
    return max(0.0, min(1.0, confidence))

def calculate_effectiveness_score(expected: float, actual: float, factors: Dict[str, float]) -> float:
    """Calculate coordination effectiveness score"""
    base_score = actual / max(expected, 0.1)
    
    # Apply additional factors
    factor_weights = {
        'agent_response_success': 0.3,
        'problem_resolution': 0.2,
        'coordination_efficiency': 0.2,
        'learning_value': 0.1
    }
    
    weighted_factors = sum(factors.get(key, 0) * weight for key, weight in factor_weights.items())
    final_score = (base_score * 0.4) + (weighted_factors * 0.6)
    
    return min(final_score, 1.0)

def create_pattern_signature(system_conditions: Dict[str, Any]) -> str:
    """Create unique signature for coordination patterns"""
    key_elements = [
        str(system_conditions.get('system_health', 0)),
        str(len(system_conditions.get('urgent_issues', []))),
        str(sorted(system_conditions.get('agents_involved', [])))
    ]
    return "_".join(key_elements)

def extract_learning_insights(coordination_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract learning insights from coordination history"""
    if not coordination_history:
        return {'status': 'insufficient_data'}
    
    success_rate = sum(1 for c in coordination_history if c.get('success', False)) / len(coordination_history)
    avg_effectiveness = sum(c.get('effectiveness_score', 0) for c in coordination_history) / len(coordination_history)
    
    return {
        'total_coordinations': len(coordination_history),
        'success_rate': success_rate,
        'average_effectiveness': avg_effectiveness,
        'learning_trend': 'improving' if avg_effectiveness > 0.7 else 'stable' if avg_effectiveness > 0.5 else 'needs_improvement',
        'pattern_opportunities': len(coordination_history) >= 10
    }

def generate_coordination_recommendations(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate coordination recommendations based on analysis"""
    recommendations = []
    
    if analysis.get('success_rate', 0) < 0.7:
        recommendations.append({
            'type': 'success_rate_improvement',
            'recommendation': 'Focus on higher confidence coordination decisions',
            'priority': 'high'
        })
    
    if analysis.get('average_effectiveness', 0) < 0.6:
        recommendations.append({
            'type': 'effectiveness_improvement',
            'recommendation': 'Improve coordination outcome measurement and learning',
            'priority': 'medium'
        })
    
    if not analysis.get('pattern_opportunities', False):
        recommendations.append({
            'type': 'pattern_development',
            'recommendation': 'Accumulate more coordination data for pattern learning',
            'priority': 'low'
        })
    
    return recommendations

# Constants for VIC-20 Sage coordination
VIC20_COORDINATION_CONFIG = {
    "minimum_confidence_threshold": 0.8,
    "pattern_similarity_threshold": 0.7,
    "effectiveness_measurement_delay_hours": 24,
    "learning_pattern_minimum_samples": 10,
    "coordination_timeout_seconds": 300,
    "max_agent_coordination_complexity": 10,
    "partnership_metrics_calculation_interval_hours": 24
}

# Export all coordination data types
__all__ = [
    "utc_now",
    "CoordinationState",
    "VIC20DecisionType", 
    "AncientWisdomPrinciple",
    "AncientWisdom",
    "VIC20Decision",
    "SystemSynthesisData",
    "AgentHarmonySnapshot",
    "PartnershipMetricsSnapshot",
    "DecisionOrchestrationLog",
    "AgentInteractionEvent",
    "AncientWisdomApplication",
    "CoordinationLearningData",
    "VIC20CoordinationMessage",
    "CoordinationPattern",
    "validate_coordination_confidence",
    "calculate_effectiveness_score",
    "create_pattern_signature",
    "extract_learning_insights",
    "generate_coordination_recommendations",
    "VIC20_COORDINATION_CONFIG"
]