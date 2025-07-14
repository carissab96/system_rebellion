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

class AnalysisDepth(Enum):
    """How deep should the Meth Snail think?"""
    BASIC = "basic"           # Quick WebSocket analysis
    STANDARD = "standard"     # Normal depth
    THOROUGH = "thorough"     # Full background optimization analysis

@dataclass
class ShellSpinIncident:
    """Track when the Meth Snail spins his shell waiting for real data"""
    timestamp: datetime
    missing_metrics: List[str]
    invalid_metrics: List[str]
    reason: str
    user_id: Optional[str] = None

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
    
class AnalysisDepth(Enum):
    """How deep should the Meth Snail think?"""
    BASIC = "basic"           # Quick WebSocket analysis
    STANDARD = "standard"     # Normal depth
    THOROUGH = "thorough"     # Full background optimization analysis

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