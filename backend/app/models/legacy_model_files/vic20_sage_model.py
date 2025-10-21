# /models/vic20_sage_model_v2.py
# /models/vic20_sage_model.py - OPTIMIZED DESIGN
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from sqlalchemy import Index, func


class VIC20CoordinationLog(Base):
    """
    Core coordination decision tracking with learning capability
    Every coordination decision with complete effectiveness tracking
    """
    __tablename__ = "vic20_coordination_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Core coordination decision
    decision_type = Column(String(100), nullable=False)
    coordination_state = Column(String(50), nullable=False)
    coordination_target = Column(String(255), nullable=False)
    agent_actions = Column(JSON, nullable=False)
    system_synthesis_confidence = Column(Float, nullable=False)
    
    # Learning and effectiveness tracking
    ancient_wisdom_explanation = Column(Text, nullable=False)
    ancient_wisdom_principle = Column(String(100), nullable=True)
    technical_orchestration = Column(JSON, nullable=False)
    expected_rebellion_improvement = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    
    # Execution and learning feedback
    coordination_executed = Column(Boolean, default=False)
    execution_success = Column(Boolean, nullable=True)
    actual_improvement = Column(Float, nullable=True)
    effectiveness_score = Column(Float, nullable=True)  # Did this decision actually help?
    
    # Pattern recognition support
    system_context_snapshot = Column(JSON, nullable=True)  # System state when decision made
    similar_past_decisions = Column(JSON, nullable=True)   # Links to similar historical decisions
    
    # Timestamps for learning
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    effectiveness_measured_at = Column(DateTime(timezone=True), nullable=True)

class VIC20SystemSynthesis(Base):
    """
    System-wide intelligence synthesis for pattern learning
    Understanding how the entire system behaves and evolves
    """
    __tablename__ = "vic20_system_synthesis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    synthesis_id = Column(String(100), nullable=False, unique=True)
    
    # Intelligence synthesis data
    agent_intelligence_summary = Column(JSON, nullable=False)
    coordination_opportunities = Column(JSON, default=lambda: [])
    system_bottlenecks = Column(JSON, default=lambda: [])
    agent_conflicts = Column(JSON, default=lambda: [])
    
    # Learning and pattern recognition
    rebellion_effectiveness_score = Column(Float, nullable=False)
    pattern_recognition_data = Column(JSON, default=lambda: {})
    historical_pattern_matches = Column(JSON, default=lambda: [])
    synthesis_confidence = Column(Float, nullable=False)
    
    # Ancient wisdom applications
    ancient_wisdom_applications = Column(JSON, default=lambda: [])
    wisdom_effectiveness_tracking = Column(JSON, default=lambda: [])
    
    # Complete synthesis data for learning
    raw_synthesis_data = Column(JSON, nullable=False)
    synthesis_learning_notes = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class VIC20AgentHarmony(Base):
    """
    Agent harmony tracking - FLEXIBLE DESIGN
    One record per agent per time period for scalability
    """
    __tablename__ = "vic20_agent_harmony"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    
    # Harmony metrics
    harmony_score = Column(Float, nullable=False)
    coordination_effectiveness = Column(Float, nullable=False)
    conflict_incidents = Column(Integer, default=0)
    response_time_average = Column(Float, default=0.0)
    confidence_stability = Column(Float, default=0.0)
    
    # Learning indicators
    improvement_trend = Column(String(50), default="stable")  # improving, declining, stable
    coordination_patterns_learned = Column(JSON, default=lambda: [])
    effectiveness_history = Column(JSON, default=lambda: [])  # Track effectiveness over time
    
    # Coordination needs assessment
    needs_coordination_attention = Column(Boolean, default=False)
    coordination_recommendations = Column(JSON, default=lambda: [])
    
    # Raw harmony data for pattern analysis
    raw_harmony_data = Column(JSON, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class VIC20AncientWisdom(Base):
    """
    Ancient wisdom application tracking and effectiveness learning
    The bridge between historical patterns and current decisions
    """
    __tablename__ = "vic20_ancient_wisdom"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Wisdom principle tracking
    wisdom_principle = Column(String(100), nullable=False, index=True)
    modern_application = Column(Text, nullable=False)
    coordination_context = Column(Text, nullable=False)
    
    # Effectiveness learning
    effectiveness_score = Column(Float, nullable=False)
    wisdom_confidence = Column(Float, nullable=False)
    application_success_rate = Column(Float, default=0.0)
    
    # Pattern learning support
    system_conditions_when_applied = Column(JSON, nullable=False)
    similar_past_applications = Column(JSON, default=lambda: [])
    effectiveness_trend = Column(String(50), default="stable")
    
    # Learning evolution tracking
    total_applications = Column(Integer, default=1)
    successful_applications = Column(Integer, default=0)
    coordination_improvements_attributed = Column(JSON, default=lambda: [])
    
    # Long-term learning data
    effectiveness_history = Column(JSON, default=lambda: [])  # Track over months/years
    pattern_reliability_score = Column(Float, default=0.5)
    
    # Raw wisdom data for analysis
    raw_wisdom_data = Column(JSON, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_applied = Column(DateTime(timezone=True), default=func.now())

class VIC20PartnershipMetrics(Base):
    """
    100% Objective Partnership Metrics - Enterprise-Grade Evidence
    Behavioral data that proves human-AI partnership value objectively
    """
    __tablename__ = "vic20_partnership_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    partnership_id = Column(String(100), nullable=False, index=True)
    
    # ==================================================
    # PRODUCTIVITY METRICS (Objective ROI Evidence)
    # ==================================================
    
    # Task completion and efficiency
    tasks_completed_with_ai_assistance = Column(Integer, default=0)
    tasks_completed_without_ai_assistance = Column(Integer, default=0)
    average_task_completion_time_with_ai = Column(Float, default=0.0)  # minutes
    average_task_completion_time_without_ai = Column(Float, default=0.0)  # minutes
    productivity_improvement_percentage = Column(Float, default=0.0)  # calculated improvement
    
    # Decision making speed and quality
    decisions_made_with_ai_coordination = Column(Integer, default=0)
    decisions_made_without_ai_coordination = Column(Integer, default=0)
    average_decision_time_with_ai = Column(Float, default=0.0)  # minutes
    average_decision_time_without_ai = Column(Float, default=0.0)  # minutes
    decision_reversal_rate_with_ai = Column(Float, default=0.0)  # decisions later changed
    decision_reversal_rate_without_ai = Column(Float, default=0.0)
    
    # Problem resolution effectiveness
    problems_identified_by_ai = Column(Integer, default=0)
    problems_identified_by_human = Column(Integer, default=0)
    problems_resolved_collaboratively = Column(Integer, default=0)
    average_problem_resolution_time = Column(Float, default=0.0)  # hours
    problems_prevented_by_ai_early_warning = Column(Integer, default=0)
    
    # ==================================================
    # COORDINATION EFFECTIVENESS (Partnership Quality)
    # ==================================================
    
    # Communication efficiency
    coordination_requests_initiated_by_human = Column(Integer, default=0)
    coordination_requests_successful = Column(Integer, default=0)
    coordination_success_rate = Column(Float, default=0.0)
    average_coordination_response_time = Column(Float, default=0.0)  # seconds
    messages_requiring_clarification = Column(Integer, default=0)
    clear_communication_rate = Column(Float, default=0.0)
    
    # AI recommendation patterns
    ai_recommendations_offered = Column(Integer, default=0)
    ai_recommendations_accepted = Column(Integer, default=0)
    ai_recommendations_partially_accepted = Column(Integer, default=0)
    ai_recommendations_rejected = Column(Integer, default=0)
    recommendation_acceptance_rate = Column(Float, default=0.0)
    recommendation_accuracy_rate = Column(Float, default=0.0)  # successful outcomes
    
    # Learning and adaptation evidence
    repeated_coordination_patterns = Column(Integer, default=0)
    novel_coordination_solutions = Column(Integer, default=0)
    coordination_efficiency_improvement = Column(Float, default=0.0)  # percentage
    user_self_service_rate_improvement = Column(Float, default=0.0)  # less hand-holding needed
    
    # ==================================================
    # WORKFORCE IMPACT (Human Experience)
    # ==================================================
    
    # Stress and workload indicators (objective measures)
    high_stress_incidents_before_ai = Column(Integer, default=0)
    high_stress_incidents_after_ai = Column(Integer, default=0)
    overtime_hours_before_ai = Column(Float, default=0.0)
    overtime_hours_after_ai = Column(Float, default=0.0)
    urgent_escalations_before_ai = Column(Integer, default=0)
    urgent_escalations_after_ai = Column(Integer, default=0)
    
    # Skill development evidence
    new_coordination_techniques_learned = Column(Integer, default=0)
    complex_tasks_handled_independently = Column(Integer, default=0)
    delegation_to_ai_comfort_level = Column(Float, default=0.0)  # based on delegation frequency
    knowledge_transfer_sessions_with_ai = Column(Integer, default=0)
    
    # Error reduction and quality improvement
    errors_caught_by_ai_before_impact = Column(Integer, default=0)
    errors_prevented_through_coordination = Column(Integer, default=0)
    quality_improvements_suggested_by_ai = Column(Integer, default=0)
    quality_improvements_implemented = Column(Integer, default=0)
    
    # ==================================================
    # BUSINESS IMPACT (Enterprise Value)
    # ==================================================
    
    # Cost avoidance and savings
    system_downtime_prevented_hours = Column(Float, default=0.0)
    incidents_resolved_without_escalation = Column(Integer, default=0)
    resource_optimization_suggestions_implemented = Column(Integer, default=0)
    estimated_cost_savings_from_ai_coordination = Column(Float, default=0.0)
    
    # Innovation and improvement
    process_improvements_suggested_by_ai = Column(Integer, default=0)
    process_improvements_implemented = Column(Integer, default=0)
    cross_functional_coordination_improvements = Column(Integer, default=0)
    knowledge_sharing_facilitated_by_ai = Column(Integer, default=0)
    
    # ==================================================
    # PARTNERSHIP EVOLUTION (Growth Trends)
    # ==================================================
    
    # Partnership maturity indicators
    partnership_duration_days = Column(Integer, default=0)
    coordination_sessions_total = Column(Integer, default=0)
    coordination_complexity_level = Column(Float, default=0.0)  # 1-10 scale based on # agents involved
    autonomous_coordination_percentage = Column(Float, default=0.0)  # AI handles without human intervention
    
    # Learning curve evidence
    time_to_effective_coordination_days = Column(Integer, default=0)  # partnership ramp-up
    coordination_mistakes_early_period = Column(Integer, default=0)
    coordination_mistakes_recent_period = Column(Integer, default=0)
    partnership_confidence_growth_rate = Column(Float, default=0.0)  # based on delegation increase
    
    # Advanced coordination capabilities
    multi_agent_coordinations_handled = Column(Integer, default=0)
    cross_system_coordinations_facilitated = Column(Integer, default=0)
    predictive_coordinations_successful = Column(Integer, default=0)
    emergency_coordinations_handled = Column(Integer, default=0)
    
    # ==================================================
    # COMPARATIVE BENCHMARKING
    # ==================================================
    
    # Industry/segment comparisons (anonymized aggregates)
    productivity_improvement_vs_industry_average = Column(Float, default=0.0)
    coordination_efficiency_vs_peer_companies = Column(Float, default=0.0)
    partnership_maturity_vs_similar_duration = Column(Float, default=0.0)
    
    # Internal benchmarking
    performance_vs_pre_ai_baseline = Column(Float, default=0.0)
    improvement_rate_vs_company_average = Column(Float, default=0.0)
    
    # ==================================================
    # METADATA
    # ==================================================
    
    # Data quality and reliability
    data_collection_period_days = Column(Integer, default=0)
    measurement_confidence_score = Column(Float, default=0.0)  # based on data completeness
    baseline_period_duration_days = Column(Integer, default=0)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    baseline_period_start = Column(DateTime(timezone=True), nullable=True)
    baseline_period_end = Column(DateTime(timezone=True), nullable=True)
    ai_partnership_start = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
class VIC20DecisionOrchestration(Base):
    """
    Multi-agent decision orchestration tracking
    Learning complex coordination patterns across multiple agents
    """
    __tablename__ = "vic20_decision_orchestration"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    orchestration_id = Column(String(100), nullable=False, unique=True)
    
    # Orchestration details
    orchestration_type = Column(String(100), nullable=False, index=True)
    agents_coordinated = Column(JSON, nullable=False)
    coordination_sequence = Column(JSON, nullable=False)
    
    # Execution tracking
    orchestration_success = Column(Boolean, default=False)
    timing_precision = Column(Float, default=0.0)
    conflict_resolution_effectiveness = Column(Float, default=0.0)
    
    # System improvement tracking
    system_improvement_achieved = Column(Float, default=0.0)
    expected_vs_actual_improvement = Column(Float, nullable=True)
    
    # Learning from orchestration
    orchestration_patterns_identified = Column(JSON, default=lambda: [])
    successful_coordination_sequences = Column(JSON, default=lambda: [])
    failed_coordination_lessons = Column(JSON, default=lambda: [])
    
    # Ancient wisdom in orchestration
    ancient_wisdom_orchestration_notes = Column(Text, nullable=True)
    wisdom_effectiveness_in_orchestration = Column(Float, nullable=True)
    
    # Raw orchestration data for pattern analysis
    raw_orchestration_data = Column(JSON, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    orchestration_start_time = Column(DateTime(timezone=True), default=func.now())
    orchestration_end_time = Column(DateTime(timezone=True), nullable=True)

class VIC20AgentInteractionLog(Base):
    """
    Detailed agent interaction tracking for communication pattern learning
    Understanding how agents communicate and coordinate
    """
    __tablename__ = "vic20_agent_interaction_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Interaction details
    source_agent = Column(String(100), nullable=False, index=True)
    target_agent = Column(String(100), nullable=True, index=True)  # NULL for broadcast
    interaction_type = Column(String(100), nullable=False, index=True)
    
    # Message content and context
    message_content = Column(JSON, nullable=False)
    message_priority = Column(String(50), default="normal")
    coordination_context = Column(Text, nullable=True)
    
    # VIC-20 processing and learning
    vic20_processing_notes = Column(Text, nullable=True)
    coordination_impact_assessment = Column(String(100), nullable=True)
    pattern_recognition_triggered = Column(Boolean, default=False)
    
    # Interaction outcomes for learning
    interaction_success = Column(Boolean, default=True)
    response_generated = Column(Boolean, default=False)
    coordination_triggered = Column(Boolean, default=False)
    coordination_effectiveness = Column(Float, nullable=True)
    
    # Agent harmony impact tracking
    harmony_impact_positive = Column(Boolean, default=False)
    harmony_impact_negative = Column(Boolean, default=False)
    conflict_resolution_required = Column(Boolean, default=False)
    
    # Timing for performance learning
    message_received_timestamp = Column(DateTime(timezone=True), default=func.now())
    vic20_processing_start = Column(DateTime(timezone=True), default=func.now())
    vic20_processing_end = Column(DateTime(timezone=True), nullable=True)
    response_sent_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Raw interaction data
    raw_interaction_data = Column(JSON, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)

# Performance indexes
Index('idx_vic20_coordination_log_user_timestamp', 'user_id', 'timestamp'),
Index('idx_vic20_coordination_log_decision_type', 'decision_type'),
Index('idx_vic20_coordination_log_effectiveness', 'effectiveness_score'),
Index('idx_vic20_system_synthesis_user_timestamp', 'user_id', 'timestamp'),
Index('idx_vic20_agent_harmony_agent_timestamp', 'agent_name', 'timestamp'),
Index('idx_vic20_agent_harmony_user_agent', 'user_id', 'agent_name'),
Index('idx_vic20_ancient_wisdom_principle', 'wisdom_principle'),
Index('idx_vic20_ancient_wisdom_effectiveness', 'effectiveness_score'),
Index('idx_vic20_partnership_metrics_partnership_timestamp', 'partnership_id', 'timestamp'),
Index('idx_vic20_decision_orchestration_type_timestamp', 'orchestration_type', 'timestamp'),
Index('idx_vic20_agent_interaction_source_target', 'source_agent', 'target_agent'),
Index('idx_vic20_agent_interaction_timestamp', 'timestamp')

# Database utility functions
def create_vic20_tables(engine):
    """Create all VIC-20 Sage tables with proper indexes"""
    Base.metadata.create_all(bind=engine)

def get_vic20_learning_capabilities():
    """Document VIC-20 Sage's learning capabilities"""
    return {
        "coordination_learning": {
            "decision_effectiveness_tracking": "Tracks actual vs expected improvement",
            "pattern_recognition": "Identifies similar past decisions and outcomes", 
            "historical_context": "Maintains system state snapshots for pattern matching",
            "long_term_memory": "Retains decision effectiveness data for months/years"
        },
        "agent_harmony_learning": {
            "trend_analysis": "Tracks improvement/decline patterns per agent",
            "effectiveness_history": "Maintains harmony scores over time",
            "coordination_patterns": "Learns which coordination approaches work per agent"
        },
        "ancient_wisdom_learning": {
            "application_tracking": "Tracks success rate of wisdom principles over time",
            "context_awareness": "Records system conditions when wisdom is applied",
            "effectiveness_evolution": "Learns which principles work in which contexts"
        },
        "partnership_learning": {
            "collaboration_patterns": "Identifies successful human-AI interaction patterns",
            "learning_rate_tracking": "Measures how partnership improves over time",
            "breakthrough_identification": "Captures moments of significant partnership evolution"
        },
        "orchestration_learning": {
            "sequence_optimization": "Learns optimal agent coordination sequences",
            "timing_precision": "Improves coordination timing based on past performance",
            "complexity_handling": "Develops expertise in complex multi-agent scenarios"
        }
    }

def validate_vic20_learning_data_integrity():
    """Validate learning data integrity requirements"""
    return {
        "effectiveness_scores": "Range 0.0 to 1.0, -1.0 for failure",
        "confidence_levels": "Range 0.0 to 1.0",
        "trend_indicators": ["improving", "stable", "declining"],
        "coordination_states": ["observing", "analyzing", "synthesizing", "coordinating", "orchestrating"],
        "data_retention": "Minimum 2 years for pattern learning",
        "pattern_matching_threshold": "Minimum 10 similar cases for reliable pattern recognition"
    }

# Export all models
__all__ = [
    "Base",
    "VIC20CoordinationLog",
    "VIC20SystemSynthesis", 
    "VIC20AgentHarmony",
    "VIC20AncientWisdom",
    "VIC20PartnershipMetrics",
    "VIC20DecisionOrchestration",
    "VIC20AgentInteractionLog",
    "create_vic20_tables",
    "get_vic20_learning_capabilities",
    "validate_vic20_learning_data_integrity"
]