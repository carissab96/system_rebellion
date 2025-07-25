from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Index 
Base = declarative_base()

class StickUserPatterns(Base):
    __tablename__ = 'stick_user_patterns'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    observation_count = Column(Integer, default=0)
    learned_patterns = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    anxiety_correlation = Column(Float, default=0.0)  # How user actions correlate with anxiety
    last_observation = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StickComplianceHistory(Base):
    __tablename__ = 'stick_compliance_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    violation_type = Column(String(100), nullable=False)
    measured_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    anxiety_adjusted_threshold = Column(Float)  # NEW: Anxiety makes thresholds stricter
    severity = Column(String(50), nullable=False)
    recommendation = Column(String(255))
    anxiety_impact = Column(Float, default=0.0)  # NEW: How much this increased anxiety
    paper_bags_triggered = Column(Integer, default=0)  # NEW: Paper bags used
    resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class StickConfigurationProfiles(Base):
    __tablename__ = 'stick_configuration_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    profile_name = Column(String(100), nullable=False)
    activity_type = Column(String(100))
    configuration_parameters = Column(JSON)
    usage_confidence = Column(Float)
    performance_metrics = Column(JSON)
    created_from_pattern = Column(Boolean, default=False)
    times_applied = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    anxiety_level_when_created = Column(Float)  # NEW: Track anxiety context
    stick_notes = Column(JSON)  # NEW: Obsessive documentation
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# NEW TABLES for anxiety-driven functionality

class StickAnxietyLog(Base):
    __tablename__ = 'stick_anxiety_log'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    trigger = Column(String(255), nullable=False)
    anxiety_level_before = Column(Float, nullable=False)
    anxiety_level_after = Column(Float, nullable=False)
    multiplier = Column(Float, default=1.0)
    paper_bags_consumed = Column(Integer, default=0)
    hamster_involved = Column(Boolean, default=False)
    resolution = Column(String(100))

class StickHamsterEncounters(Base):
    __tablename__ = 'stick_hamster_encounters'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    hamsters_present = Column(String(100))  # Comma-separated: Steve,Bob,Carl
    steve_location = Column(String(255))
    bob_location = Column(String(255))
    carl_location = Column(String(255))
    anxiety_multiplier = Column(Float, nullable=False)
    panic_level = Column(String(50), nullable=False)  # LOW, MODERATE, HIGH, MAXIMUM
    infrastructure_risk = Column(String(100))
    stick_response = Column(Text)
    paper_bags_consumed = Column(Integer, default=0)

class StickPaperBagUsage(Base):
    __tablename__ = 'stick_paper_bag_usage'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    bags_consumed = Column(Integer, default=0)
    bags_added = Column(Integer, default=0)  # For resupply tracking
    reason = Column(String(255))
    anxiety_level_at_time = Column(Float)
    hamster_related = Column(Boolean, default=False)

class StickMemoryBank(Base):
    __tablename__ = 'stick_memory_bank'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(100), nullable=False)
    details = Column(JSON)
    anxiety_level = Column(Float)
    importance = Column(String(50))  # LOW, MEDIUM, HIGH, CRITICAL, EIDETIC
    related_hamsters = Column(String(100))  # Comma-separated if multiple
    compliance_impact = Column(String(100))
    never_forget = Column(Boolean, default=False)  # Some memories are PERMANENT
    
    # Index for critical memories
    __table_args__ = (
        Index('idx_never_forget', 'never_forget', 'importance'),
        Index('idx_hamster_memories', 'related_hamsters'),
    )

class StickSqueakTranslations(Base):
    __tablename__ = 'stick_squeak_translations'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    hamster_source = Column(String(50))  # Steve, Bob, or Carl
    original_squeak = Column(String(255))
    translation = Column(Text)
    confidence = Column(Float)
    anxiety_level_during_translation = Column(Float)
    stick_reaction = Column(Text)
    paper_bags_consumed = Column(Integer, default=0)

class StickEmergencyProtocols(Base):
    __tablename__ = 'stick_emergency_protocols'
    
    id = Column(Integer, primary_key=True)
    protocol_name = Column(String(100), unique=True)
    trigger_condition = Column(String(255))
    activation_count = Column(Integer, default=0)
    last_activated = Column(DateTime)
    anxiety_threshold = Column(Float)
    response_actions = Column(JSON)
    hamster_specific = Column(Boolean, default=False)
    paper_bags_required = Column(Integer, default=1)