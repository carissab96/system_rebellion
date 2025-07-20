# /models/meth_snail_model.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
Base = declarative_base()

# NOTE: MethSnailDecisionLog is now centralized in agent_decision_models.py

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