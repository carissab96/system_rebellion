# /models/agent_decision_models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class HawkingtonDecisionLog(Base):
    """Store Sir Hawkington's aristocratic monitoring decisions"""
    __tablename__ = 'hawkington_decision_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String, nullable=False, index=True)
    monocle_state = Column(String, nullable=False)
    monitoring_target = Column(String, nullable=False)
    
    # Alert details
    alert_parameters = Column(JSON, nullable=True)
    monocle_yeet_required = Column(Boolean, default=False)
    aristocratic_explanation = Column(Text, nullable=True)
    technical_details = Column(JSON, nullable=True)
    
    # Performance metrics
    severity_level = Column(String, nullable=True)
    confidence_level = Column(Float, nullable=True)
    
    # Success tracking
    alert_sent = Column(Boolean, default=False)
    user_acknowledged = Column(Boolean, default=False)
    issue_resolved = Column(Boolean, default=False)

class MethSnailDecisionLog(Base):
    """Store Meth Snail's caffeinated optimization decisions"""
    __tablename__ = 'meth_snail_decision_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String, nullable=False, index=True)
    energy_level = Column(String, nullable=False)
    optimization_target = Column(String, nullable=False)
    
    # Optimization details
    optimization_parameters = Column(JSON, nullable=True)
    energy_drinks_consumed = Column(Integer, default=0)
    shell_spinning_required = Column(Boolean, default=False)
    caffeinated_explanation = Column(Text, nullable=True)
    technical_details = Column(JSON, nullable=True)
    
    # Performance metrics
    expected_improvement = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    
    # Success tracking
    optimization_applied = Column(Boolean, default=False)
    actual_improvement = Column(Float, nullable=True)
    success_verified = Column(Boolean, default=False)

class HamstersDecisionLog(Base):
    """Store The Hamsters' beer-powered engineering decisions"""
    __tablename__ = 'hamsters_decision_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String, nullable=False, index=True)
    beer_level = Column(String, nullable=False)
    engineering_target = Column(String, nullable=False)
    
    # Engineering details
    engineering_parameters = Column(JSON, nullable=True)
    beer_consumed = Column(Integer, default=0)
    duct_tape_used = Column(Boolean, default=False)
    supply_closet_raids = Column(Integer, default=0)
    beer_powered_explanation = Column(Text, nullable=True)
    technical_details = Column(JSON, nullable=True)
    
    # Engineering metrics
    redneck_ingenuity_level = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    urgency_level = Column(String, nullable=True)
    priority_level = Column(String, nullable=True)
    
    # Success tracking
    solution_applied = Column(Boolean, default=False)
    actual_improvement = Column(Float, nullable=True)
    success_verified = Column(Boolean, default=False)
    beer_level_after = Column(String, nullable=True)

class AgentPerformanceSummary(Base):
    """Store cross-agent performance summary for intelligence coordination"""
    __tablename__ = 'agent_performance_summary'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    # Agent performance metrics
    agent_name = Column(String, nullable=False, index=True)
    total_decisions = Column(Integer, default=0)
    successful_decisions = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    average_confidence = Column(Float, nullable=True)
    last_decision_timestamp = Column(DateTime, nullable=True)
    
    # Performance stats
    performance_stats = Column(JSON, nullable=True)