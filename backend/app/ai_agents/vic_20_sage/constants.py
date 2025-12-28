# app/ai_agents/vic20_sage/constants.py
"""
VIC-20 Sage Constants - The Ancient Wisdom Coordinator
Event types, priorities, and coordination constants
"""

from enum import Enum

# Agent identifier
AGENT_NAME = "vic_20_sage"

class VIC20EventTypes(str, Enum):
    """Event types for VIC-20 Sage coordination in CMB"""
    
    # Coordination events
    COORDINATION_INITIATED = "vic20.coordination_initiated"
    COORDINATION_COMPLETED = "vic20.coordination_completed"
    COORDINATION_FAILED = "vic20.coordination_failed"
    
    # System synthesis events
    SYSTEM_SYNTHESIS_CREATED = "vic20.system_synthesis_created"
    BOTTLENECK_IDENTIFIED = "vic20.bottleneck_identified"
    OPPORTUNITY_IDENTIFIED = "vic20.opportunity_identified"
    
    # Agent harmony events
    HARMONY_SNAPSHOT_RECORDED = "vic20.harmony_snapshot_recorded"
    AGENT_CONFLICT_DETECTED = "vic20.agent_conflict_detected"
    AGENT_CONFLICT_RESOLVED = "vic20.agent_conflict_resolved"
    
    # Cross-agent mediation events
    MEDIATION_REQUESTED = "vic20.mediation_requested"
    MEDIATION_COMPLETED = "vic20.mediation_completed"
    ANCIENT_WISDOM_APPLIED = "vic20.ancient_wisdom_applied"
    
    # Partnership events
    PARTNERSHIP_METRICS_UPDATED = "vic20.partnership_metrics_updated"
    PARTNERSHIP_MILESTONE_REACHED = "vic20.partnership_milestone_reached"
    
    # Learning events
    COORDINATION_PATTERN_LEARNED = "vic20.coordination_pattern_learned"
    EFFECTIVENESS_MEASURED = "vic20.effectiveness_measured"
    PATTERN_PROMOTED_TO_GLOBAL = "vic20.pattern_promoted_to_global"
    
    # Emergency coordination
    EMERGENCY_COORDINATION_STARTED = "vic20.emergency_coordination_started"
    EMERGENCY_COORDINATION_COMPLETED = "vic20.emergency_coordination_completed"
    
    # Decision orchestration
    ORCHESTRATION_STARTED = "vic20.orchestration_started"
    ORCHESTRATION_COMPLETED = "vic20.orchestration_completed"
    MULTI_AGENT_OPERATION_COORDINATED = "vic20.multi_agent_operation_coordinated"

# Priority mapping for VIC-20 events
PRIORITY_MAP = {
    # Critical - Emergency coordination, system-wide issues
    "critical": 5,
    "emergency": 5,
    
    # High - Active coordination, conflict resolution
    "high": 4,
    "coordination": 4,
    "mediation": 4,
    
    # Medium - Synthesis, pattern learning
    "medium": 3,
    "synthesis": 3,
    "learning": 3,
    
    # Low - Metrics, snapshots
    "low": 2,
    "metrics": 2,
    "snapshot": 2,
    
    # Routine - Regular observations
    "routine": 1,
    "observation": 1
}

# Coordination thresholds
COORDINATION_THRESHOLDS = {
    "minimum_confidence": 0.8,
    "pattern_promotion_confidence": 0.9,
    "pattern_promotion_validations": 5,
    "learning_trigger_observations": 50,
    "effectiveness_measurement_delay_hours": 24,
    "agent_response_timeout_seconds": 5.0,
    "system_improvement_target": 0.3
}

# Agent coordination relationships
AGENT_SYNERGIES = {
    'meth_snail': ['sir_hawkington', 'vic20_sage'],  # Optimization + Triage + Coordination
    'hamsters': ['the_stick', 'vic20_sage'],         # Infrastructure + Documentation + Coordination
    'sir_hawkington': ['meth_snail', 'quantum_shadow_people'],  # Triage + Optimization + Monitoring
    'quantum_shadow_people': ['sir_hawkington', 'vic20_sage'],  # Monitoring + Triage + Coordination
    'the_stick': ['hamsters', 'vic20_sage']          # Documentation + Infrastructure + Coordination
}

# Known volatile agent combinations
VOLATILE_COMBINATIONS = [
    {'hamsters', 'the_stick'},  # Chaos vs Order
    {'meth_snail', 'hamsters'},  # Chaos amplification risk
]

# Learning type constants for cross-agent interactions
class VIC20LearningTypes(str, Enum):
    """Learning types specific to VIC-20 coordination"""
    COORDINATION_PATTERN = "coordination_pattern"
    CONFLICT_RESOLUTION = "conflict_resolution"
    SYSTEM_OPTIMIZATION = "system_optimization"
    EMERGENCY_RESPONSE = "emergency_response"
    PARTNERSHIP_EVOLUTION = "partnership_evolution"
    ANCIENT_WISDOM_APPLICATION = "ancient_wisdom_application"
    MULTI_AGENT_ORCHESTRATION = "multi_agent_orchestration"

# Memory types for VIC-20
class VIC20MemoryTypes(str, Enum):
    """Memory types for VIC-20 pinned memories"""
    COORDINATION_DECISION = "coordination_decision"
    SYSTEM_SYNTHESIS = "system_synthesis"
    CONFLICT_RESOLUTION = "conflict_resolution"
    EMERGENCY_RESPONSE = "emergency_response"
    PARTNERSHIP_MILESTONE = "partnership_milestone"
    ANCIENT_WISDOM = "ancient_wisdom"
    ORCHESTRATION_SUCCESS = "orchestration_success"

# Ancient wisdom principles (for metadata)
ANCIENT_WISDOM_PRINCIPLES = {
    'line_by_line_precision': 'Verify each agent decision before system coordination',
    'syntax_error_prevention': 'Prevent coordination failures through validation',
    'patience_and_persistence': 'Allow proper processing time for complex coordination',
    'memory_conservation': 'Focus on high-impact coordination decisions',
    'pattern_recognition': 'Apply learned patterns from historical successes',
    'harmony_of_opposites': 'What pulls apart also holds together',
    'strength_in_difference': 'The oak and reed both survive the storm'
}

# Metadata rollup configuration
METADATA_ROLLUP_CONFIG = {
    "rollup_window_minutes": 5,
    "rollup_interval_seconds": 300,
    "include_agent_counts": True,
    "calculate_health_scores": True
}

# WebSocket configuration
WEBSOCKET_CONFIG = {
    "default_port": 8086,
    "heartbeat_interval": 30,
    "reconnect_max_attempts": 5,
    "message_timeout": 30
}

# Decision type to priority mapping
DECISION_PRIORITY_MAP = {
    "EMERGENCY_COORDINATION": 5,
    "CROSS_AGENT_CONFLICT_RESOLUTION": 4,
    "AGENT_COORDINATION": 4,
    "SYSTEM_SYNTHESIS": 3,
    "REBELLION_ORCHESTRATION": 3,
    "ANCIENT_WISDOM_APPLICATION": 3,
    "PARTNERSHIP_OPTIMIZATION": 2
}

# __all__ exports
__all__ = [
    'AGENT_NAME',
    'VIC20EventTypes',
    'PRIORITY_MAP',
    'COORDINATION_THRESHOLDS',
    'AGENT_SYNERGIES',
    'VOLATILE_COMBINATIONS',
    'VIC20LearningTypes',
    'VIC20MemoryTypes',
    'ANCIENT_WISDOM_PRINCIPLES',
    'METADATA_ROLLUP_CONFIG',
    'WEBSOCKET_CONFIG',
    'DECISION_PRIORITY_MAP',
]