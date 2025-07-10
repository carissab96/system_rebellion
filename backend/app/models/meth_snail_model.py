# /models/meth_snail_models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

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

class MethSnailOptimizationStats(Base):
    """Store Meth Snail's optimization performance statistics"""
    __tablename__ = 'meth_snail_optimization_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
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