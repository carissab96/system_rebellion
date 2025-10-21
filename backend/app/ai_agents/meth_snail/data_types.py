from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class OptimizationPriority(Enum):
    """The Meth Snail's optimization focus modes"""
    SPEED = "speed"                    # GOTTA GO FAST
    EFFICIENCY = "efficiency"          # Resource conservation
    BALANCED = "balanced"              # The sweet spot
    AGGRESSIVE = "aggressive"          # MAXIMUM OVERDRIVE
    HIBERNATION = "hibernation"        # Low activity mode
    SHELL_SPINNING = "shell_spinning"  # Waiting for real data
    DECAFFEINATED = "decaffeinated"    # Performance degraded - needs energy drink

class AnalysisDepth(Enum):
    """How deep should the Meth Snail think?"""
    BASIC = "basic"           # Quick WebSocket analysis
    STANDARD = "standard"     # Normal depth
    THOROUGH = "thorough"     # Full background optimization analysis

class EnergyDrinkType(Enum):
    """Types of energy drinks Meth Snail can consume"""
    COFFEE = "coffee"                    # Basic caffeine
    ENERGY_DRINK = "energy_drink"        # Standard energy drink
    QUANTUM_CAFFEINE = "quantum_caffeine" # Maximum overdrive
    EMERGENCY_OVERRIDE = "emergency_override" # When Sir Hawkington is unavailable

class JitterLevel(Enum):
    """Meth Snail's jitter intensity levels"""
    CALM = "calm"                      # 0.0 - 0.2
    NORMAL = "normal"                  # 0.2 - 0.4
    ENERGIZED = "energized"            # 0.4 - 0.6
    JITTERY = "jittery"                # 0.6 - 0.8
    HYPERCAFFEINATED = "hypercaffeinated" # 0.8 - 1.0

@dataclass
class ShellSpinIncident:
    """Track when the Meth Snail spins his shell waiting for real data"""
    timestamp: datetime
    missing_metrics: List[str]
    invalid_metrics: List[str]
    reason: str
    user_id: Optional[str] = None

@dataclass
class EnergyDrinkRequest:
    """Meth Snail's energy drink authorization request"""
    user_id: str
    energy_drink_type: EnergyDrinkType
    caffeine_mg: float
    consumption_reason: str
    current_jitter_level: float
    energy_drinks_consumed_today: int
    time_since_last_drink_minutes: Optional[int]
    optimization_urgency: str  # immediate, soon, eventual
    timestamp: datetime

@dataclass
class EnergyDrinkAuthorization:
    """Sir Hawkington's energy drink authorization response"""
    request_id: str
    authorized: bool
    authorized_by: str  # sir_hawkington, emergency_override
    authorization_notes: str
    recommended_caffeine_mg: Optional[float]
    recommended_type: Optional[EnergyDrinkType]
    safety_warnings: List[str]
    timestamp: datetime

@dataclass
class OptimizationDecision:
    """The Meth Snail's optimization verdict"""
    priority: OptimizationPriority
    actions: List[Dict[str, Any]]
    confidence: float                    # 0.0 to 1.0
    rationale: str
    estimated_impact: Dict[str, float]   # Expected improvements
    urgency: str                         # immediate, soon, eventual
    analysis_depth: AnalysisDepth
    shell_spin_count: int               # How many times we spun waiting for data
    data_quality_score: float           # 0.0 to 1.0
    timestamp: datetime
    
    # Safety protocol additions
    current_jitter_level: float = 0.0
    caffeine_level_mg: float = 0.0
    is_decaffeinated: bool = False
    requires_energy_drink: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'priority': self.priority.value,
            'actions': self.actions,
            'confidence': self.confidence,
            'rationale': self.rationale,
            'estimated_impact': self.estimated_impact,
            'urgency': self.urgency,
            'analysis_depth': self.analysis_depth.value,
            'shell_spin_count': self.shell_spin_count,
            'data_quality_score': self.data_quality_score,
            'timestamp': self.timestamp.isoformat(),
            'current_jitter_level': self.current_jitter_level,
            'caffeine_level_mg': self.caffeine_level_mg,
            'is_decaffeinated': self.is_decaffeinated,
            'requires_energy_drink': self.requires_energy_drink
        }