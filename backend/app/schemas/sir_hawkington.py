from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class MonocleState(str, Enum):
    """The state of Sir Hawkington's monocle"""
    POLISHED = "polished"
    SMUDGED = "smudged"
    YEETED = "yeeted"  # When thrown in frustration
    LOST = "lost"      # Temporarily misplaced

class DataQualityIssue(str, Enum):
    """Types of data quality issues Sir Hawkington can identify"""
    INCONSISTENCY = "inconsistency"
    DUPLICATE = "duplicate"
    OUTLIER = "outlier"
    MISSING = "missing"
    CORRUPTED = "corrupted"
    ANOMALY = "anomaly"

class TriageDecision(BaseModel):
    """Model for Sir Hawkington's data triage decisions"""
    issue_type: DataQualityIssue
    severity: int = Field(ge=1, le=10)
    confidence: float = Field(ge=0.0, le=1.0)
    affected_columns: List[str]
    suggested_action: str
    notes: Optional[str] = None

class SirHawkingtonMemoryType(BaseModel):
    """Base memory schema for Sir Hawkington's aristocratic data oversight"""
    title: str
    description: str
    data_quality_issues: List[DataQualityIssue] = Field(default_factory=list)
    triage_decisions: List[TriageDecision] = Field(default_factory=list)
    monocle_state: MonocleState = MonocleState.POLISHED
    refinement_notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    importance: int = Field(ge=1, le=10, default=5)

    @validator('title')
    def title_must_be_proper(cls, v):
        """Ensure titles are properly capitalized and end with a period"""
        if not v[0].isupper():
            raise ValueError("Title must start with a capital letter")
        if not v.endswith('.'):
            v += '.'
        return v

class SirHawkingtonMemoryCreate(SirHawkingtonMemoryType):
    """Schema for creating new aristocratic memories"""
    pass

class SirHawkingtonMemoryRead(SirHawkingtonMemoryType):
    """Schema for reading memories with system fields"""
    id: str
    created_at: datetime
    updated_at: datetime
    last_reviewed: Optional[datetime] = None
    review_count: int = 0

    class Config:
        from_attributes = True

class SirHawkingtonMemoryUpdate(BaseModel):
    """Schema for updating existing aristocratic memories"""
    title: Optional[str] = None
    description: Optional[str] = None
    monocle_state: Optional[MonocleState] = None
    refinement_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    importance: Optional[int] = None

class SirHawkingtonQuery(BaseModel):
    """Schema for querying Sir Hawkington's memories"""
    issue_types: Optional[List[DataQualityIssue]] = None
    min_severity: Optional[int] = None
    min_confidence: Optional[float] = None
    monocle_state: Optional[MonocleState] = None
    tags: Optional[List[str]] = None
    time_range: Optional[tuple[datetime, datetime]] = None
    limit: int = 100
    offset: int = 0
