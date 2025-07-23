"""
Hamster-specific data types for infrastructure management
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

class InfrastructureEventType(Enum):
    """Types of infrastructure events Hamsters handle"""
    DISK_CLEANUP = "disk_cleanup"
    DEFRAGMENTATION = "defragmentation"
    LOG_ROTATION = "log_rotation"
    EMERGENCY_SPACE = "emergency_space"
    PARTITION_MANAGEMENT = "partition_management"
    THERMAL_EVENT = "thermal_event"
    MYSTERY_NOISE = "mystery_noise"
    CABLE_MANAGEMENT = "cable_management"

class HamsterInterventionStatus(Enum):
    """Status of Hamster interventions"""
    PLANNING = "planning"  # Drinking beer and discussing
    IN_PROGRESS = "in_progress"  # Actively fixing
    TESTING = "testing"  # "Does it work now?"
    COMPLETED = "completed"  # "Fixed!"
    ABANDONED = "abandoned"  # "Call VIC-20"

@dataclass
class HamsterCommunication:
    """Records Hamster communication attempts"""
    timestamp: datetime
    source_hamster: str  # steve, bob, or carl
    telepathic_message: str
    audible_squeaks: str
    human_translation: str
    target_agent: Optional[str] = None
    understood: bool = False

@dataclass
class DuctTapeUsage:
    """Track duct tape consumption"""
    timestamp: datetime
    grade: str  # regular, premium, quantum, carls_special
    amount_strips: int
    purpose: str
    applied_by: str  # Usually Carl
    effectiveness: float  # 0.0 to 1.0

@dataclass
class InfrastructureIntervention:
    """Complete record of a Hamster infrastructure intervention"""
    intervention_id: str
    type: InfrastructureEventType
    status: HamsterInterventionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    
    # The three hamsters' roles
    steve_action: str
    bob_action: str
    carl_action: str
    
    # Resources used
    beer_consumed: int
    duct_tape_used: List[DuctTapeUsage]
    tools_used: List[str]
    
    # Results
    space_freed_gb: float = 0.0
    fragmentation_reduced_percent: float = 0.0
    temperature_reduced_celsius: float = 0.0
    mystery_solved: bool = False
    
    # Communication
    squeaks_emitted: int = 0
    human_readable_summary: str = ""
    
    # Safety
    required_vic20_intervention: bool = False
    caused_stick_anxiety_spike: bool = False

@dataclass
class SupplyClosetInventory:
    """Current supply closet status"""
    last_updated: datetime
    beer_cases: int
    duct_tape_rolls: Dict[str, int]  # grade -> count
    mystery_tools: List[str]
    emergency_supplies: Dict[str, Any]
    last_raided_by: str  # Usually Bob