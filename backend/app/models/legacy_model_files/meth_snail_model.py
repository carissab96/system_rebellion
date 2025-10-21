# /models/meth_snail_model.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from sqlalchemy import func

# NOTE: MethSnailDecisionLog is now centralized in agent_decision_models.py

class MethSnailEnergyConsumption(Base):
    """Track Meth Snail's energy drink consumption and authorization"""
    __tablename__ = 'meth_snail_energy_consumption'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now, nullable=False, index=True)
    
    # Energy drink details
    energy_drink_type = Column(String(50), nullable=False)  # coffee, energy_drink, quantum_caffeine
    caffeine_mg = Column(Float, nullable=False)
    authorization_requested = Column(Boolean, default=False)
    authorization_granted = Column(Boolean, default=False)
    authorized_by = Column(String(50), nullable=True)  # sir_hawkington, emergency_override
    
    # Consumption tracking
    energy_drinks_consumed_today = Column(Integer, default=0)
    time_since_last_drink_minutes = Column(Integer, nullable=True)
    consumption_reason = Column(String(100), nullable=True)  # optimization_needed, jitter_prevention, emergency
    
    # Authorization details
    authorization_request_timestamp = Column(DateTime(timezone=True), nullable=True)
    authorization_response_timestamp = Column(DateTime(timezone=True), nullable=True)
    authorization_notes = Column(Text, nullable=True)


class MethSnailJitterLevels(Base):
    """Track Meth Snail's jitter levels and caffeine effects"""
    __tablename__ = 'meth_snail_jitter_levels'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now, nullable=False, index=True)
    
    # Jitter tracking (0.0 to 1.0)
    current_jitter_level = Column(Float, nullable=False, default=0.0)
    peak_jitter_level = Column(Float, nullable=False, default=0.0)
    baseline_jitter_level = Column(Float, nullable=False, default=0.1)
    
    # Caffeine state
    caffeine_level_mg = Column(Float, nullable=False, default=0.0)
    is_decaffeinated = Column(Boolean, default=False)
    time_since_caffeine_minutes = Column(Integer, nullable=True)
    
    # Performance effects
    shell_spin_probability = Column(Float, nullable=False, default=0.05)  # increases when tired
    optimization_effectiveness = Column(Float, nullable=True)  # degrades when decaffeinated
    focus_level = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    
    # Safety monitoring
    hypercaffeinated = Column(Boolean, default=False)
    requires_stick_intervention = Column(Boolean, default=False)
    vic20_mediation_requested = Column(Boolean, default=False)
    
    # Additional tracking
    energy_source = Column(String(50), nullable=True)  # last consumed energy source
    jitter_trend = Column(String(20), nullable=True)  # increasing, stable, decreasing
    raw_jitter_data = Column(JSON, nullable=True)


class MethSnailOptimizationStats(Base):
    """Store Meth Snail's optimization performance statistics"""
    __tablename__ = 'meth_snail_optimization_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now, nullable=False, index=True)
    
    # Optimization performance
    optimizations_performed = Column(Integer, default=0)
    energy_drinks_consumed = Column(Integer, default=0)
    shell_spins_executed = Column(Integer, default=0)
    
    # Caffeinated metrics
    average_optimization_improvement = Column(Float, nullable=True)
    optimization_success_rate = Column(Float, nullable=True)
    average_energy_level = Column(Float, nullable=True)
    
    # Raw stats
    raw_stats = Column(JSON, nullable=True)