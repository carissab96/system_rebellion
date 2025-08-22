# /models/sir_hawkington_model.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey, event
from sqlalchemy.orm import relationship, Session
from datetime import datetime
import uuid
from sqlalchemy import func
from typing import Optional, Dict, Any, List
from app.schemas.sir_hawkington import (
    SirHawkingtonMemoryCreate,
    SirHawkingtonMemoryUpdate,
    SirHawkingtonQuery,
    DataQualityIssue
)
from app.models.agent_memory_banks import SirHawkingtonMemoryBank
from app.core.base import Base

# NOTE: HawkingtonDecisionLog is now centralized in agent_decision_models.py

class HawkingtonMonitoringStats(Base):
    """Store Sir Hawkington's monitoring performance statistics"""
    __tablename__ = 'hawkington_monitoring_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Monitoring performance
    alerts_generated = Column(Integer, default=0)
    monocle_yeets_performed = Column(Integer, default=0)
    critical_issues_detected = Column(Integer, default=0)
    
    # Aristocratic metrics
    monitoring_precision = Column(Float, nullable=True)
    alert_accuracy_rate = Column(Float, nullable=True)
    user_response_time = Column(Float, nullable=True)
    
    # Raw stats
    raw_stats = Column(JSON, nullable=True)
    
    # Relationship to memory bank
    memory_entries = relationship(
        "SirHawkingtonMemoryBank",
        back_populates="monitoring_stats",
        cascade="all, delete-orphan"
    )
    
    def to_memory_create(self) -> SirHawkingtonMemoryCreate:
        """Convert monitoring stats to a memory creation schema"""
        issues = []
        if self.alert_accuracy_rate and self.alert_accuracy_rate < 0.9:
            issues.append(DataQualityIssue.INCONSISTENCY)
        if self.monitoring_precision and self.monitoring_precision < 0.95:
            issues.append(DataQualityIssue.ANOMALY)
            
        triage_decisions = []
        if self.critical_issues_detected > 0:
            triage_decisions.append({
                "issue_type": DataQualityIssue.CRITICAL,
                "severity": 8 if self.critical_issues_detected > 5 else 5,
                "confidence": 0.9,
                "affected_columns": ["critical_issues_detected"],
                "suggested_action": "Review critical issues immediately"
            })
            
        monocle_state = "yetted" if self.monocle_yeets_performed > 0 else "polished"
        
        return SirHawkingtonMemoryCreate(
            title=f"Monitoring Report - {self.timestamp.strftime('%Y-%m-%d %H:%M')}",
            description=f"Generated {self.alerts_generated} alerts with {self.alert_accuracy_rate*100:.1f}% accuracy",
            data_quality_issues=issues,
            triage_decisions=triage_decisions,
            monocle_state=monocle_state,
            refinement_notes=f"Monitoring precision: {self.monitoring_precision:.2f}",
            tags=["monitoring", "performance_report"],
            importance=8 if issues else 5
        )
    
    @classmethod
    def create_from_memory(
        cls,
        db: Session,
        memory: SirHawkingtonMemoryBank,
        user_id: str
    ) -> 'HawkingtonMonitoringStats':
        """Create monitoring stats from a memory entry"""
        stats = cls(
            user_id=user_id,
            timestamp=memory.timestamp or datetime.now(),
            monocle_yeets_performed=1 if memory.monocle_yeet_trigger else 0,
            raw_stats={
                "memory_id": memory.memory_id,
                "data_quality_pattern": memory.data_quality_pattern,
                "triage_decision_context": memory.triage_decision_context
            }
        )
        db.add(stats)
        db.flush()
        return stats