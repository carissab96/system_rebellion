"""
Pydantic models for Hamsters agent data validation.
"""
from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import UUID

# ===================== Individual Hamster Stats =====================

class HamstersIndividualStatsBase(BaseModel):
    """Base schema for individual hamster statistics."""
    user_id: str
    hamster_name: str  # steve, bob, or carl
    beer_count: int = 0
    risk_tolerance: Optional[float] = None
    current_task: Optional[str] = None
    duct_tape_love: Optional[float] = None

class HamstersIndividualStatsCreate(HamstersIndividualStatsBase):
    """Schema for creating individual hamster statistics."""
    pass

class HamstersIndividualStatsRead(HamstersIndividualStatsBase):
    """Schema for reading individual hamster statistics."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Infrastructure Interventions =====================

class HamstersInfrastructureInterventionBase(BaseModel):
    """Base schema for infrastructure interventions by the Hamsters."""
    user_id: str
    type: str
    status: str
    priority: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steve_action: Optional[str] = None
    bob_action: Optional[str] = None
    carl_action: Optional[str] = None
    beer_consumed: int = 0
    tools_used: Optional[Any] = None
    space_freed_gb: float = 0.0
    fragmentation_reduced_percent: float = 0.0
    temperature_reduced_celsius: float = 0.0
    mystery_solved: bool = False

class HamstersInfrastructureInterventionCreate(HamstersInfrastructureInterventionBase):
    """Schema for creating infrastructure interventions."""
    pass

class HamstersInfrastructureInterventionRead(HamstersInfrastructureInterventionBase):
    """Schema for reading infrastructure interventions."""
    id: int
    intervention_id: UUID
    started_at: datetime

    class Config:
        orm_mode = True

# ===================== Communication Logs =====================

class HamstersCommunicationLogBase(BaseModel):
    """Base schema for hamster communication logs."""
    user_id: Optional[str] = None
    source_hamster: str
    telepathic_message: Optional[str] = None
    audible_squeaks: str
    human_translation: str
    target_agent: Optional[str] = None
    understood: bool = False

class HamstersCommunicationLogCreate(HamstersCommunicationLogBase):
    """Schema for creating communication logs."""
    pass

class HamstersCommunicationLogRead(HamstersCommunicationLogBase):
    """Schema for reading communication logs."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Duct Tape Usage =====================

class HamstersDuctTapeUsageBase(BaseModel):
    """Base schema for duct tape usage tracking."""
    user_id: Optional[str] = None
    grade: str
    strips_used: int
    purpose: str
    used_by: str = 'carl'
    effectiveness: Optional[float] = None

class HamstersDuctTapeUsageCreate(HamstersDuctTapeUsageBase):
    """Schema for creating duct tape usage records."""
    pass

class HamstersDuctTapeUsageRead(HamstersDuctTapeUsageBase):
    """Schema for reading duct tape usage records."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Beer Consumption =====================

class HamstersBeerConsumptionBase(BaseModel):
    """Base schema for beer consumption tracking."""
    user_id: Optional[str] = None
    hamster_name: str
    beers_consumed: int
    occasion: Optional[str] = None

class HamstersBeerConsumptionCreate(HamstersBeerConsumptionBase):
    """Schema for creating beer consumption records."""
    pass

class HamstersBeerConsumptionRead(HamstersBeerConsumptionBase):
    """Schema for reading beer consumption records."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Supply Closet Raids =====================

class HamstersSupplyClosetRaidBase(BaseModel):
    """Base schema for supply closet raid tracking."""
    user_id: Optional[str] = None
    raided_by: str = 'bob'
    items_taken: Any
    purpose: Optional[str] = None

class HamstersSupplyClosetRaidCreate(HamstersSupplyClosetRaidBase):
    """Schema for creating supply closet raid records."""
    pass

class HamstersSupplyClosetRaidRead(HamstersSupplyClosetRaidBase):
    """Schema for reading supply closet raid records."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Engineering Stats =====================

class HamstersEngineeringStatsBase(BaseModel):
    """Base schema for Hamsters' engineering statistics."""
    user_id: str
    total_interventions: int = 0
    successful_interventions: int = 0
    abandoned_interventions: int = 0
    total_beer_consumed: int = 0
    total_duct_tape_used: int = 0
    total_supply_closet_raids: int = 0
    total_space_freed_gb: float = 0.0
    total_fragmentation_reduced: float = 0.0
    total_mysteries_solved: int = 0
    steve_interventions: int = 0
    bob_interventions: int = 0
    carl_interventions: int = 0
    average_beer_per_intervention: Optional[float] = None
    average_duct_tape_per_intervention: Optional[float] = None
    intervention_success_rate: Optional[float] = None
    three_am_intervention_count: int = 0
    raw_stats: Optional[Any] = None

class HamstersEngineeringStatsCreate(HamstersEngineeringStatsBase):
    """Schema for creating engineering statistics."""
    pass

class HamstersEngineeringStatsRead(HamstersEngineeringStatsBase):
    """Schema for reading engineering statistics."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
