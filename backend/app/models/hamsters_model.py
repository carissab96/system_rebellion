# /models/hamsters_models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()


# NOTE: HamstersDecisionLog is now centralized in agent_decision_models.py

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