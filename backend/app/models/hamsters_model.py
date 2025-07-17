# /models/hamsters_models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()


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

class HamstersEngineeringStats(Base):
    """Store The Hamsters' engineering performance statistics"""
    __tablename__ = 'hamsters_engineering_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Engineering performance
    engineering_solutions_deployed = Column(Integer, default=0)
    beer_consumed_total = Column(Integer, default=0)
    duct_tape_rolls_used = Column(Integer, default=0)
    supply_closet_raids_total = Column(Integer, default=0)
    
    # Beer-powered metrics
    average_redneck_ingenuity = Column(Float, nullable=True)
    engineering_success_rate = Column(Float, nullable=True)
    average_beer_efficiency = Column(Float, nullable=True)
    
    # Raw stats
    raw_stats = Column(JSON, nullable=True)