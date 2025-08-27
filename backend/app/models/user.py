from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, ForeignKey, TEXT
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy import JSON 
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func
from app.models.agent_memory import AgentMemory

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: uuid_str(uuid.uuid4()))
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Onboarding Status
    is_onboarded = Column(Boolean, default=False)
    onboarding_progress = Column(Integer, nullable=True)  # Current step number
    
    # Enhanced onboarding tracking
    onboarding_data = Column(JSON, nullable=True)  # Full form data as JSON
    onboarding_started_at = Column(DateTime, nullable=True)
    onboarding_last_step_at = Column(DateTime, nullable=True)
    onboarding_abandoned_count = Column(Integer, default=0, nullable=False)
    onboarding_step_timestamps = Column(JSON, default=dict)  # {"step_1": timestamp, "step_2": timestamp}
    onboarding_abandonment_reasons = Column(JSON, default=list)  # Track why they left
    onboarding_device_info = Column(JSON, nullable=True)  # Browser, OS, screen size
    onboarding_referral_source = Column(String(100), nullable=True)  # How they found you
    
    # Preview/Trial tracking
    preview_agent_selected = Column(String(20), nullable=True)  # 'hawkington', 'stick', 'vic20'
    preview_started_at = Column(DateTime, nullable=True)
    preview_expires_at = Column(DateTime, nullable=True)
    preview_conversion_emails_sent = Column(JSON, default=list)  # Track which emails sent
    preview_converted_at = Column(DateTime, nullable=True)  # When they upgraded to paid
    
    # Email campaign tracking
    email_campaign_responses = Column(JSON, default=dict)  # Track opens, clicks, conversions
    last_engagement_at = Column(DateTime, nullable=True)

    # Profile Information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    company_name = Column(String(100), nullable=True)
    job_title = Column(String(50), nullable=True)
    
    # System Information
    system_name = Column(String(100), nullable=True)  # User's custom system name
    avatar = Column(String(50), default='sir-hawkington')
    
    # Agent Configuration (from onboarding) - UPDATED TO MATCH ACTUAL PREFERENCES
    agent_preferences = Column(JSON, default=lambda: {
        # Sir Hawkington
        "hawkington_triage_normal_threshold": 30,
        "hawkington_triage_medium_threshold": 65,
        "hawkington_triage_emergency_threshold": 85,
        "hawkington_message_frequency": 10,
        "hawkington_analysis_thoroughness": 7,
        
        # The Stick
        "stick_base_anxiety": 25,
        "stick_paper_bag_threshold": 60,
        "stick_bob_anxiety_multiplier": 30,
        "stick_compliance_strictness": 50,
        "stick_pattern_memory_depth": 7,
        
        # The Hamsters
        "hamster_beer_optimal_level": 3,
        "hamster_disk_intervention_threshold": 70,
        "hamster_3am_activity_boost": 5,
        "hamster_carl_duct_tape_quality": 5,
        "hamster_bob_wildness_factor": 8,
        
        # Meth Snail
        "snail_caffeine_sensitivity": 5,
        "snail_optimization_aggression": 5,
        "snail_trail_intensity": 5,
        
        # Quantum Shadow People
        "qsp_tequila_jello_tolerance": 5,
        "qsp_phase_shift_threshold": 5,
        "qsp_quantum_fix_confidence": 5,
        "qsp_comprehensibility": 3,
        
        # VIC-20
        "vic20_pattern_recognition_depth": 5,
        "vic20_mediation_patience": 5,
        "vic20_recommendation_confidence": 5,
        
        # Inter-agent dynamics
        "agent_interaction_frequency": 5,
        "hamster_stick_proximity_alerts": 5,
        "cross_agent_memory_sharing": 5
    })
    
    # Monitoring Preferences (from onboarding) - UPDATED TO MATCH ACTUAL PREFERENCES
    monitoring_preferences = Column(JSON, default=lambda: {
        # Stress calculation weights
        "cpu_stress_weight": 25,
        "memory_stress_weight": 35,
        "disk_stress_weight": 40,
        
        # Compliance thresholds
        "cpu_compliance_threshold": 80,
        "memory_compliance_threshold": 85,
        "temperature_paranoia_threshold": 75,
        
        # Hamster triggers
        "disk_cleanup_threshold": 70,
        "disk_emergency_threshold": 90,
        "fragmentation_threshold": 20,
        
        # QSP network thresholds
        "latency_gaming_threshold": 20,
        "latency_streaming_threshold": 50,
        "latency_critical_threshold": 5,
        "packet_loss_intervention": 1,
        
        # System-wide settings
        "alert_frequency": "balanced",
        "enable_3am_operations": True,
        "quantum_interventions_allowed": True,
        "cross_agent_collaboration": True
    })
    
    # System Profile (from onboarding)
    system_profile = Column(JSON, nullable=True, default=lambda: {
        'os_type': None,
        'os_version': None,
        'total_ram_gb': None,
        'storage_type': None,
        'total_storage_gb': None,
        'cpu_cores': None,  
        'is_virtual': False,
        'network_type': 'standard',
        'admin_access': 'full',
        'mdm_controlled': False,
        'custom_restrictions': []
    })
    
    # Installation tracking
    agent_installed = Column(Boolean, default=False)
    agent_version = Column(String(20), nullable=True)
    installation_method = Column(String(50), nullable=True)
    permissions_granted_at = Column(DateTime, nullable=True)
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_enterprise = Column(Boolean, default=False)  # For $5k/month clients
    
    # Security Tracking
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime, nullable=True)
    
    # Persistent AI Memory Stats
    total_interactions = Column(Integer, default=0)
    patterns_learned = Column(Integer, default=0)
    decisions_made = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships - all using string references and consistent lazy loading
    
    metrics = relationship(
        "SystemMetrics",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Relationships to agent memory banks - using string reference to avoid circular imports
    agent_memories = relationship(
        "AgentMemory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Central memory bank relationship
    central_memory_bank = relationship(
        "CentralMemoryBank",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Agent-specific memory bank relationships
    # sir_hawkington_memories = relationship(
    #     "SirHawkingtonMemoryBank",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin"
    # )
    
    # meth_snail_memories = relationship(
    #     "MethSnailMemoryBank",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin"
    # )
    
    # hamsters_memories = relationship(
    #     "HamstersMemoryBank",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin"
    # )
    
    # quantum_sp_memories = relationship(
    #     "QuantumShadowPeopleMemoryBank",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin"
    # )
    
    # vic20_memories = relationship(
    #     "VIC20MemoryBank",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin"
    # )
    
    # Cross-agent learning relationships
    # learning_interactions = relationship(
    #     "AgentLearningInteractions",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin"
    # )
    
    user_learning_patterns = relationship(
        "UserLearningPatterns",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )