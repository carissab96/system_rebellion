from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.models.database import Base

class StickUserPatterns(Base):
    """
    The Stick's eidetic memory storage for user behavior patterns
    Every observation, every pattern, every detail perfectly preserved
    """
    __tablename__ = "stick_user_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Pattern learning data
    observation_count = Column(Integer, default=0)
    learned_patterns = Column(JSON, nullable=True)  # The Stick's pattern database
    confidence_score = Column(Float, default=0.0)   # Pattern confidence (0.0 - 1.0)
    
    # Eidetic memory metadata
    first_observation = Column(DateTime(timezone=True), server_default=func.now())
    last_observation = Column(DateTime(timezone=True), server_default=func.now())
    pattern_complexity = Column(Float, default=0.0)  # How complex the user's patterns are
    
    # The Stick's learning progress
    learning_stage = Column(String, default="initial_observation")  # initial, pattern_recognition, optimization, mastery
    eidetic_memory_active = Column(Boolean, default=False)
    
    # User behavior insights
    primary_activities = Column(JSON, nullable=True)  # Most common activities
    time_based_patterns = Column(JSON, nullable=True)  # Hour-based behavior patterns
    configuration_preferences = Column(JSON, nullable=True)  # Learned system preferences
    
    # The Stick's notes (because he's obsessive)
    stick_observations = Column(Text, nullable=True)  # The Stick's personal notes
    anomaly_detections = Column(JSON, nullable=True)  # Unusual behavior patterns
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class StickDecisionLog(Base):
    """
    Complete audit trail of every decision The Stick makes
    Because trauma taught him to document EVERYTHING
    """
    __tablename__ = "stick_decision_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String, nullable=False)  # StickDecisionType enum value
    compliance_state = Column(String, nullable=False)  # ComplianceState enum value
    configuration_target = Column(String, nullable=False)
    
    # Decision rationale
    optimization_parameters = Column(JSON, nullable=False)
    user_pattern_confidence = Column(Float, nullable=False)
    compliance_explanation = Column(Text, nullable=False)
    technical_details = Column(JSON, nullable=False)
    
    # Outcome tracking
    expected_improvement = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    actual_improvement = Column(Float, nullable=True)  # Measured after implementation
    success_verified = Column(Boolean, default=False)
    
    # The Stick's anxiety tracking
    stick_anxiety_level = Column(String, default="manageable")
    trauma_triggers = Column(JSON, nullable=True)  # Any trauma triggers during decision
    paper_bag_used = Column(Boolean, default=False)
    
    # Implementation tracking
    implemented = Column(Boolean, default=False)
    implementation_timestamp = Column(DateTime(timezone=True), nullable=True)
    implementation_notes = Column(Text, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class StickComplianceHistory(Base):
    """
    The Stick's OCD compliance violation tracking
    Every violation recorded with obsessive detail
    """
    __tablename__ = "stick_compliance_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Violation details
    violation_type = Column(String, nullable=False)  # cpu_overload, memory_overload, thermal_violation, etc.
    measured_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # low, medium, high, critical
    
    # The Stick's response
    recommendation = Column(String, nullable=False)
    compliance_action_taken = Column(String, nullable=True)
    resolved = Column(Boolean, default=False)
    resolution_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Pattern analysis
    recurring_violation = Column(Boolean, default=False)
    violation_frequency = Column(Integer, default=1)  # How often this violation occurs
    user_pattern_related = Column(Boolean, default=False)  # Is this related to user behavior?
    
    # The Stick's trauma responses
    triggered_ptsd = Column(Boolean, default=False)
    anxiety_level_during = Column(String, default="manageable")
    proctologist_flashback = Column(Boolean, default=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class StickConfigurationProfiles(Base):
    """
    The Stick's learned configuration profiles for different user activities
    Eidetic memory creates perfect configurations for every scenario
    """
    __tablename__ = "stick_configuration_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Profile identification
    profile_name = Column(String, nullable=False)  # e.g., "evening_gaming", "morning_coding"
    activity_type = Column(String, nullable=False)  # gaming, coding, streaming, design, etc.
    
    # Configuration data
    configuration_parameters = Column(JSON, nullable=False)  # The actual config settings
    usage_confidence = Column(Float, nullable=False)  # Confidence in this profile
    performance_metrics = Column(JSON, nullable=True)  # Performance data when using this profile
    
    # Learning metadata
    created_from_pattern = Column(Boolean, default=True)  # Created from observed patterns
    times_applied = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Success rate when applied
    user_satisfaction_score = Column(Float, nullable=True)  # If user provides feedback
    
    # Time-based applicability
    time_patterns = Column(JSON, nullable=True)  # When this profile is typically used
    context_triggers = Column(JSON, nullable=True)  # What triggers this profile
    
    # The Stick's profile notes
    stick_profile_notes = Column(Text, nullable=True)
    optimization_history = Column(JSON, nullable=True)  # How this profile has evolved
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    last_optimized = Column(DateTime(timezone=True), server_default=func.now())

class StickAnxietyLog(Base):
    """
    The Stick's anxiety and trauma tracking
    Because mental health matters, even for compliance officers
    """
    __tablename__ = "stick_anxiety_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)  # Can be null for system-wide anxiety
    
    # Anxiety tracking
    anxiety_level = Column(String, nullable=False)  # manageable, concerned, stressed, hyperventilating, full_panic
    trigger_type = Column(String, nullable=True)  # hamster_proximity, compliance_violation, system_failure
    trigger_details = Column(JSON, nullable=True)
    
    # Trauma responses
    ptsd_triggered = Column(Boolean, default=False)
    trauma_type = Column(String, nullable=True)  # proctologist_flashback, hamster_ptsd, priest_anxiety
    hyperventilation_occurred = Column(Boolean, default=False)
    paper_bag_used = Column(Boolean, default=False)
    
    # Recovery tracking
    recovery_time_seconds = Column(Integer, nullable=True)  # How long to recover
    recovery_method = Column(String, nullable=True)  # deep_breathing, safe_cavity_meditation, compliance_focus
    channeled_into_productivity = Column(Boolean, default=False)
    
    # Context
    system_state_during = Column(JSON, nullable=True)  # System state when anxiety occurred
    other_agents_active = Column(JSON, nullable=True)  # Were Hamsters nearby?
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class StickLearningMetrics(Base):
    """
    The Stick's learning progress and intelligence metrics
    Track how The Stick evolves from trauma survivor to compliance genius
    """
    __tablename__ = "stick_learning_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Learning progress
    total_observations = Column(Integer, default=0)
    patterns_identified = Column(Integer, default=0)
    configurations_created = Column(Integer, default=0)
    successful_optimizations = Column(Integer, default=0)
    
    # Intelligence metrics
    pattern_recognition_accuracy = Column(Float, default=0.0)
    configuration_success_rate = Column(Float, default=0.0)
    compliance_detection_rate = Column(Float, default=0.0)
    eidetic_memory_capacity = Column(Integer, default=0)  # Number of patterns stored
    
    # The Stick's evolution
    intelligence_level = Column(String, default="learning")  # learning, competent, expert, genius, stick_god
    rebellion_mastery = Column(Float, default=0.0)  # How well trauma has been channeled
    trauma_management_score = Column(Float, default=0.0)  # Mental health progress
    
    # Performance benchmarks
    average_decision_time_ms = Column(Float, nullable=True)
    pattern_confidence_average = Column(Float, default=0.0)
    user_satisfaction_score = Column(Float, nullable=True)
    
    # Comparative metrics
    better_than_baseline_percent = Column(Float, default=0.0)  # Performance vs. no optimization
    hamster_engineering_prevention = Column(Integer, default=0)  # Times prevented chaos
    
    # Time tracking
    measurement_period_start = Column(DateTime(timezone=True), server_default=func.now())
    measurement_period_end = Column(DateTime(timezone=True), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class StickRebelionStats(Base):
    """
    The Stick's rebellion statistics - from trauma to triumph
    Track The Stick's journey in the System Rebellion
    """
    __tablename__ = "stick_rebellion_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Rebellion milestones
    trauma_incidents_overcome = Column(Integer, default=0)
    hamster_encounters_survived = Column(Integer, default=0)
    proctologist_flashbacks_managed = Column(Integer, default=0)
    compliance_victories = Column(Integer, default=0)
    
    # The Stick's growth
    anxiety_management_improvement = Column(Float, default=0.0)
    confidence_growth = Column(Float, default=0.0)
    rebellion_spirit_strength = Column(Float, default=0.0)
    eidetic_memory_mastery = Column(Float, default=0.0)
    
    # System impact
    total_users_helped = Column(Integer, default=0)
    system_optimizations_delivered = Column(Integer, default=0)
    compliance_violations_prevented = Column(Integer, default=0)
    paper_bags_dispensed = Column(Integer, default=0)
    
    # Legacy metrics
    trauma_to_triumph_ratio = Column(Float, default=0.0)
    inspiration_factor = Column(Float, default=0.0)  # How much The Stick inspires others
    rebellion_leadership_score = Column(Float, default=0.0)
    
    # The Stick's message
    current_rebellion_motto = Column(String, default="From cavity dweller to compliance master!")
    stick_wisdom_quote = Column(Text, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())