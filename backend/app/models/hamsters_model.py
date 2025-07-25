# /models/hamsters_models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base

# NOTE: HamstersDecisionLog remains in agent_decision_models.py

class HamstersIndividualStats(Base):
    """Track individual hamster (Steve, Bob, Carl) statistics"""
    __tablename__ = 'hamsters_individual_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    hamster_name = Column(String(10), nullable=False, index=True)  # steve, bob, or carl
    beer_count = Column(Integer, default=0)
    risk_tolerance = Column(Float)
    current_task = Column(String(100))
    duct_tape_love = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class HamstersInfrastructureIntervention(Base):
    """Track infrastructure interventions by the Hamsters"""
    __tablename__ = 'hamsters_infrastructure_interventions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    intervention_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    # Individual hamster actions
    steve_action = Column(Text)
    bob_action = Column(Text)
    carl_action = Column(Text)
    
    # Resources used
    beer_consumed = Column(Integer, default=0)
    tools_used = Column(JSON)
    
    # Results
    space_freed_gb = Column(Float, default=0.0)
    fragmentation_reduced_percent = Column(Float, default=0.0)
    temperature_reduced_celsius = Column(Float, default=0.0)
    mystery_solved = Column(Boolean, default=False)
    
    # Safety tracking
    required_vic20_intervention = Column(Boolean, default=False)
    caused_stick_anxiety_spike = Column(Boolean, default=False)

class HamstersCommunicationLog(Base):
    """Track hamster communications (squeaks and translations)"""
    __tablename__ = 'hamsters_communication_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), index=True)
    source_hamster = Column(String(10), nullable=False)
    telepathic_message = Column(Text)
    audible_squeaks = Column(Text, nullable=False)
    human_translation = Column(Text, nullable=False)
    target_agent = Column(String(50))
    understood = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class HamstersDuctTapeUsage(Base):
    """Track duct tape consumption by grade and purpose"""
    __tablename__ = 'hamsters_duct_tape_usage'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), index=True)
    grade = Column(String(20), nullable=False)  # regular, premium, quantum, carls_special
    strips_used = Column(Integer, nullable=False)
    purpose = Column(Text, nullable=False)
    used_by = Column(String(10), default='carl')
    effectiveness = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class HamstersBeerConsumption(Base):
    """Track beer consumption by individual hamsters"""
    __tablename__ = 'hamsters_beer_consumption'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), index=True)
    hamster_name = Column(String(10), nullable=False, index=True)
    beers_consumed = Column(Integer, nullable=False)
    occasion = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class HamstersSupplyClosetRaid(Base):
    """Track supply closet raids (usually by Bob)"""
    __tablename__ = 'hamsters_supply_closet_raids'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), index=True)
    raided_by = Column(String(10), default='bob')
    items_taken = Column(JSON, nullable=False)
    purpose = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class HamstersEngineeringStats(Base):
    """Aggregate statistics for Hamsters' engineering performance"""
    __tablename__ = 'hamsters_engineering_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Infrastructure performance
    total_interventions = Column(Integer, default=0)
    successful_interventions = Column(Integer, default=0)
    abandoned_interventions = Column(Integer, default=0)
    
    # Resource consumption
    total_beer_consumed = Column(Integer, default=0)
    total_duct_tape_used = Column(Integer, default=0)
    total_supply_closet_raids = Column(Integer, default=0)
    
    # Results
    total_space_freed_gb = Column(Float, default=0.0)
    total_fragmentation_reduced = Column(Float, default=0.0)
    total_mysteries_solved = Column(Integer, default=0)
    
    # Individual hamster stats
    steve_interventions = Column(Integer, default=0)
    bob_interventions = Column(Integer, default=0)
    carl_interventions = Column(Integer, default=0)
    
    # Efficiency metrics
    average_beer_per_intervention = Column(Float)
    average_duct_tape_per_intervention = Column(Float)
    intervention_success_rate = Column(Float)
    three_am_intervention_count = Column(Integer, default=0)
    
    # Raw stats for additional analysis
    raw_stats = Column(JSON)