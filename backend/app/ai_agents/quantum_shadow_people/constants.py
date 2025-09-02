# app/ai_agents/qsp/constants.py
"""
Constants for Quantum Shadow People (QSP) agent
Network specialists who phase through dimensions to fix network issues
"""

from enum import Enum

class QSPEventTypes(str, Enum):
    """Event types for QSP's central memory bank entries"""
    # Network monitoring
    NETWORK_METRICS_RECORDED = "qsp.network_metrics_recorded"
    NETWORK_PATTERN_LEARNED = "qsp.network_pattern_learned"
    
    # Quantum interventions
    QUANTUM_FIX_APPLIED = "qsp.quantum_fix_applied"
    LATENCY_OPTIMIZATION = "qsp.latency_optimization"
    BANDWIDTH_BOOST = "qsp.bandwidth_boost"
    PACKET_RECOVERY = "qsp.packet_recovery"
    DIMENSION_SHIFT = "qsp.dimension_shift"
    SECURITY_INTERVENTION = "qsp.security_intervention"
    
    # Resource consumption
    TEQUILA_JELLO_CONSUMED = "qsp.tequila_jello_consumed"
    QUANTUM_PHASE_SHIFT = "qsp.quantum_phase_shift"
    
    # Cross-agent communication
    HAMSTER_TELEPATHY_DETECTED = "qsp.hamster_telepathy_detected"
    CROSS_DIMENSIONAL_MESSAGE = "qsp.cross_dimensional_message"
    
    # Performance tracking
    OPTIMIZATION_VERIFIED = "qsp.optimization_verified"
    QUANTUM_STATS_UPDATED = "qsp.quantum_stats_updated"

class QSPDecisionTypes(str, Enum):
    """Types of quantum network interventions"""
    QUANTUM_PHASE_ROUTER = "quantum_phase_router"
    TEQUILA_JELLO_OPTIMIZATION = "tequila_jello_optimization"
    PHANTOM_PACKET_RECOVERY = "phantom_packet_recovery"
    NETWORK_DIMENSION_SHIFT = "network_dimension_shift"
    MYSTERIOUS_LATENCY_FIX = "mysterious_latency_fix"
    SPECTRAL_BANDWIDTH_BOOST = "spectral_bandwidth_boost"
    INTERDIMENSIONAL_SECURITY = "interdimensional_security"  # Add this
    PREEMPTIVE_QUANTUM_FIX = "preemptive_quantum_fix"      # Add this

# Agent identifier
AGENT_NAME = "quantum_shadow_people"

# Priority mappings for CMB
PRIORITY_MAP = {
    "network_monitoring": 1,
    "routine_optimization": 2,
    "quantum_intervention": 3,
    "critical_fix": 4,
    "security_threat": 5
}

# Quantum phase states for tracking
QUANTUM_PHASES = [
    "corporeal",
    "phased", 
    "partially_phased",
    "quantum_entangled",
    "quantum_superposition",
    "interdimensional",
    "void_walker",
    "tequila_jello_dimension"
]

# Network thresholds
NETWORK_THRESHOLDS = {
    'latency': {
        'gaming': 20,
        'streaming': 50,
        'general': 100,
        'critical': 5
    },
    'packet_loss': {
        'acceptable': 0.01,
        'concerning': 0.05,
        'critical': 0.10
    },
    'bandwidth': {
        'normal': 0.70,
        'high': 0.85,
        'critical': 0.95
    }
}