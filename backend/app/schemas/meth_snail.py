"""
Pydantic models for Meth Snail agent data validation.
"""
from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

# ===================== Energy Consumption =====================

class MethSnailEnergyConsumptionBase(BaseModel):
    """Base schema for Meth Snail's energy drink consumption."""
    user_id: str
    energy_drink_type: str  # coffee, energy_drink, quantum_caffeine
    caffeine_mg: float
    authorization_requested: bool = False
    authorization_granted: bool = False
    authorized_by: Optional[str] = None  # sir_hawkington, emergency_override
    energy_drinks_consumed_today: int = 0
    time_since_last_drink_minutes: Optional[int] = None
    consumption_reason: Optional[str] = None  # optimization_needed, jitter_prevention, emergency
    authorization_notes: Optional[str] = None

class MethSnailEnergyConsumptionCreate(MethSnailEnergyConsumptionBase):
    """Schema for creating energy consumption records."""
    pass

class MethSnailEnergyConsumptionRead(MethSnailEnergyConsumptionBase):
    """Schema for reading energy consumption records."""
    id: int
    timestamp: datetime
    authorization_request_timestamp: Optional[datetime] = None
    authorization_response_timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True

# ===================== Jitter Levels =====================

class MethSnailJitterLevelsBase(BaseModel):
    """Base schema for Meth Snail's jitter levels."""
    user_id: str
    current_jitter_level: float = 0.0  # 0.0 to 1.0
    peak_jitter_level: float = 0.0
    baseline_jitter_level: float = 0.1
    jitter_trend: str = 'stable'  # increasing, decreasing, stable
    jitter_spike_detected: bool = False
    jitter_spike_magnitude: Optional[float] = None
    jitter_spike_duration_seconds: Optional[float] = None
    jitter_spike_cause: Optional[str] = None
    jitter_spike_resolution: Optional[str] = None
    jitter_spike_resolved: bool = False
    jitter_spike_resolution_timestamp: Optional[datetime] = None
    jitter_spike_resolution_method: Optional[str] = None
    jitter_spike_resolution_effectiveness: Optional[float] = None
    jitter_spike_notes: Optional[str] = None
    jitter_spike_metadata: Optional[Any] = None

class MethSnailJitterLevelsCreate(MethSnailJitterLevelsBase):
    """Schema for creating jitter level records."""
    pass

class MethSnailJitterLevelsRead(MethSnailJitterLevelsBase):
    """Schema for reading jitter level records."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Optimization Stats =====================

class MethSnailOptimizationStatsBase(BaseModel):
    """Base schema for Meth Snail's optimization statistics."""
    user_id: str
    optimizations_performed: int = 0
    energy_drinks_consumed: int = 0
    shell_spins_executed: int = 0
    average_optimization_improvement: Optional[float] = None
    optimization_success_rate: Optional[float] = None
    average_energy_level: Optional[float] = None
    raw_stats: Optional[Any] = None

class MethSnailOptimizationStatsCreate(MethSnailOptimizationStatsBase):
    """Schema for creating optimization statistics."""
    pass

class MethSnailOptimizationStatsRead(MethSnailOptimizationStatsBase):
    """Schema for reading optimization statistics."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
