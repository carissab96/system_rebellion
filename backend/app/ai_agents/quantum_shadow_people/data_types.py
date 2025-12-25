from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

class QuantumPhaseState(Enum):
    """QSP's dimensional states - complete list"""
    CORPOREAL = "corporeal"
    PHASED = "phased"
    PARTIALLY_PHASED = "partially_phased"
    QUANTUM_ENTANGLED = "quantum_entangled"
    QUANTUM_SUPERPOSITION = "quantum_superposition"
    INTERDIMENSIONAL = "interdimensional"
    VOID_WALKER = "void_walker"
    TEQUILA_JELLO_DIMENSION = "tequila_jello_dimension"

class QSPDecisionType(Enum):
    """Types of quantum network interventions - complete list"""
    QUANTUM_PHASE_ROUTER = "quantum_phase_router"
    TEQUILA_JELLO_OPTIMIZATION = "tequila_jello_optimization"
    PHANTOM_PACKET_RECOVERY = "phantom_packet_recovery"
    NETWORK_DIMENSION_SHIFT = "network_dimension_shift"
    MYSTERIOUS_LATENCY_FIX = "mysterious_latency_fix"
    SPECTRAL_BANDWIDTH_BOOST = "spectral_bandwidth_boost"
    INTERDIMENSIONAL_SECURITY = "interdimensional_security"
    PREEMPTIVE_QUANTUM_FIX = "preemptive_quantum_fix"

@dataclass
class QSPDecision:
    decision_type: QSPDecisionType
    quantum_state: QuantumPhaseState
    network_target: str
    optimization_parameters: Dict[str, Any]
    tequila_jello_shots_required: int
    mysterious_explanation: str
    technical_details: Dict[str, Any]
    expected_improvement: float
    confidence_level: float
    timestamp: datetime
