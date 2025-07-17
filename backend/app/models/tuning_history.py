"""
Enhanced TuningHistory Model with Hamsters-specific tracking
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

class TuningHistory(Base):
    """
    Enhanced model to store system tuning history with Hamsters engineering tracking
    """
    __tablename__ = "tuning_history"
    
    # Original fields
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parameter = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=False)
    success = Column(Boolean, default=True)
    error = Column(String, nullable=True)
    metrics_before = Column(JSON, nullable=True)
    metrics_after = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Hamsters-specific engineering tracking
    beer_consumed = Column(Integer, default=0)
    duct_tape_used = Column(Boolean, default=False)
    supply_closet_raids = Column(Integer, default=0)
    redneck_ingenuity_level = Column(Float, default=0.0)
    engineering_solution = Column(String, nullable=True)
    beer_level_before = Column(String, default="FULL")
    beer_level_after = Column(String, default="FULL")
    duct_tape_inventory_used = Column(Integer, default=0)
    supply_closet_items = Column(JSON, nullable=True)  # List of items used
    
    # Engineering quality metrics
    confidence_score = Column(Float, default=0.0)
    impact_score = Column(Float, default=0.0)
    urgency_level = Column(String, default="LOW")
    priority_level = Column(String, default="BEER_BREAK")
    
    # Pattern learning data
    pattern_confidence = Column(Float, default=0.0)
    learned_from_patterns = Column(Boolean, default=False)
    historical_data_points = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="tuning_history")
    
    def to_dict(self):
        """Convert to dictionary for API response with Hamsters engineering data"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "parameter": self.parameter,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "success": self.success,
            "error": self.error,
            "metrics_before": self.metrics_before,
            "metrics_after": self.metrics_after,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            
            # Hamsters engineering data
            "beer_consumed": self.beer_consumed,
            "duct_tape_used": self.duct_tape_used,
            "supply_closet_raids": self.supply_closet_raids,
            "redneck_ingenuity_level": self.redneck_ingenuity_level,
            "engineering_solution": self.engineering_solution,
            "beer_level_before": self.beer_level_before,
            "beer_level_after": self.beer_level_after,
            "duct_tape_inventory_used": self.duct_tape_inventory_used,
            "supply_closet_items": self.supply_closet_items,
            
            # Engineering quality metrics
            "confidence_score": self.confidence_score,
            "impact_score": self.impact_score,
            "urgency_level": self.urgency_level,
            "priority_level": self.priority_level,
            
            # Pattern learning data
            "pattern_confidence": self.pattern_confidence,
            "learned_from_patterns": self.learned_from_patterns,
            "historical_data_points": self.historical_data_points,
            
            "email": None  # Don't access the user relationship to avoid greenlet_spawn error
        }