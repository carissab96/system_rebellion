"""
Pydantic models for Quantum Shadow People (QSP) agent data validation.
"""
from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

# ===================== Network Metrics =====================

class QSPNetworkMetricsBase(BaseModel):
    """Base schema for QSP network metrics."""
    user_id: str
    
    # Core network metrics
    latency: Optional[float] = None
    bandwidth_utilization: Optional[float] = None
    packet_loss: Optional[float] = None
    jitter: Optional[float] = None
    
    # Network details
    download_speed: Optional[float] = None
    upload_speed: Optional[float] = None
    connection_type: Optional[str] = None
    
    # Raw metrics
    raw_metrics: Optional[Any] = None

class QSPNetworkMetricsCreate(QSPNetworkMetricsBase):
    """Schema for creating network metrics records."""
    pass

class QSPNetworkMetricsRead(QSPNetworkMetricsBase):
    """Schema for reading network metrics records."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Decision Log =====================

class QSPDecisionLogBase(BaseModel):
    """Base schema for QSP decision logs."""
    user_id: str
    decision_type: str
    quantum_state: str
    network_target: str
    optimization_parameters: Optional[Any] = None
    tequila_jello_shots_required: int = 0
    mysterious_explanation: Optional[str] = None
    technical_details: Optional[Any] = None

class QSPDecisionLogCreate(QSPDecisionLogBase):
    """Schema for creating decision log records."""
    pass

class QSPDecisionLogRead(QSPDecisionLogBase):
    """Schema for reading decision log records."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Quantum Stats =====================

class QSPQuantumStatsBase(BaseModel):
    """Base schema for QSP quantum statistics."""
    user_id: str
    quantum_fixes_applied: int = 0
    tequila_jello_shots_consumed: int = 0
    dimensional_shifts_performed: int = 0
    average_latency_improvement: Optional[float] = None
    average_bandwidth_improvement: Optional[float] = None
    packet_loss_reductions: int = 0
    network_patterns_learned: int = 0
    optimization_success_rate: Optional[float] = None
    raw_stats: Optional[Any] = None

class QSPQuantumStatsCreate(QSPQuantumStatsBase):
    """Schema for creating quantum statistics records."""
    pass

class QSPQuantumStatsRead(QSPQuantumStatsBase):
    """Schema for reading quantum statistics records."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ===================== Network Patterns =====================

class QSPNetworkPatternsBase(BaseModel):
    """Base schema for QSP network patterns."""
    user_id: str
    pattern_type: str
    pattern_name: Optional[str] = None
    pattern_data: Any
    confidence_score: Optional[float] = None
    optimization_count: int = 0
    success_rate: Optional[float] = None

class QSPNetworkPatternsCreate(QSPNetworkPatternsBase):
    """Schema for creating network pattern records."""
    pass

class QSPNetworkPatternsRead(QSPNetworkPatternsBase):
    """Schema for reading network pattern records."""
    id: int
    timestamp: datetime
    last_updated: datetime

    class Config:
        orm_mode = True
