"""
Pydantic models for metrics aggregates data validation.
"""
from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

# ===================== Hourly Metrics =====================

class MetricsHourlyBase(BaseModel):
    """Base schema for hourly metrics aggregates."""
    user_id: str
    hour_start: datetime
    
    # AI Agent Incident Tracking
    meth_snail_shell_spins: int = 0
    hawkington_monocle_yeets: int = 0
    stick_hyperventilations: int = 0
    quantum_shadow_phasings: int = 0
    vic20_wisdom_dispensed: int = 0
    
    # Overall AI Health
    ai_agent_incident_count: int = 0
    ai_agent_incident_type: Optional[str] = None
    ai_agent_incident_reason: Optional[str] = None
    ai_agent_incident_data_quality_score: Optional[float] = None
    ai_agent_incident_summary: Optional[Any] = None
    
    # System Metrics
    cpu_avg: Optional[float] = None
    cpu_max: Optional[float] = None
    cpu_min: Optional[float] = None
    
    memory_avg: Optional[float] = None
    memory_max: Optional[float] = None
    memory_min: Optional[float] = None
    
    disk_avg: Optional[float] = None
    network_bytes_total: Optional[float] = None
    
    # AI Insights
    ai_events: Optional[Any] = None
    anomaly_count: int = 0

class MetricsHourlyCreate(MetricsHourlyBase):
    """Schema for creating hourly metrics records."""
    pass

class MetricsHourlyRead(MetricsHourlyBase):
    """Schema for reading hourly metrics records."""
    id: int

    class Config:
        orm_mode = True

# ===================== Daily Metrics =====================

class MetricsDailyBase(BaseModel):
    """Base schema for daily metrics aggregates."""
    user_id: str
    date: datetime
    
    # AI Agent Incident Tracking
    daily_meth_snail_shell_spins: int = 0
    daily_hawkington_monocle_yeets: int = 0
    daily_stick_hyperventilations: int = 0
    daily_quantum_shadow_phasings: int = 0
    daily_vic20_wisdom_dispensed: int = 0
    daily_ai_incident_count: int = 0
    daily_ai_incident_type: Optional[str] = None
    daily_ai_incident_reason: Optional[str] = None
    daily_ai_incident_data_quality_score: Optional[float] = None
    daily_ai_incident_summary: Optional[Any] = None
    
    # System Metrics
    cpu_avg: Optional[float] = None
    cpu_peak_time: Optional[datetime] = None
    cpu_peak_value: Optional[float] = None
    
    memory_avg: Optional[float] = None
    memory_peak_time: Optional[datetime] = None
    memory_peak_value: Optional[float] = None
    
    disk_avg: Optional[float] = None
    network_bytes_total: Optional[float] = None
    
    # Usage Patterns
    usage_pattern: Optional[Any] = None

class MetricsDailyCreate(MetricsDailyBase):
    """Schema for creating daily metrics records."""
    pass

class MetricsDailyRead(MetricsDailyBase):
    """Schema for reading daily metrics records."""
    id: int

    class Config:
        orm_mode = True
