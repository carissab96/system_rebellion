"""
Quantum Shadow People — Data Types
====================================

Consolidated enums and dataclasses for the decomposed QSP agent.
Re-exports existing types from data_types.py and adds new ones
for the decomposed architecture.

Pure data — no logic, no side effects.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Re-export existing types so ML layers and new code can import from one place
from .data_types import QuantumPhaseState, QSPDecisionType, QSPDecision


class ParanoiaLevel(str, Enum):
    """QSP's paranoia levels — healthy → elevated → maximum → JUSTIFIED"""
    HEALTHY = "healthy"
    ELEVATED = "elevated"
    MAXIMUM = "maximum"
    JUSTIFIED = "JUSTIFIED"


@dataclass
class TequilaJelloEvent:
    """Record of tequila jello shot consumption"""
    shots_consumed: int
    total_shots: int
    quantum_state: str
    courage_level: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QuantumSecurityScan:
    """Result of a quantum security scan"""
    phase_state: str
    anomalies_detected: List[Dict[str, Any]] = field(default_factory=list)
    phase_exclusive_findings: List[Dict[str, Any]] = field(default_factory=list)
    tequila_jello_shots_required: int = 0
    threat_level: str = "none"
    scan_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
