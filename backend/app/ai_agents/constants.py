# app/ai_agents/agent_constants.py
"""
Single Source of Truth for Agent Names and Common Constants
Because future developers shouldn't have to guess if it's 'hamster' or 'the_hamsters'
(Spoiler: It's 'hamsters', but Bob is definitely involved)
"""

from enum import Enum
from typing import Dict, List

# === CANONICAL AGENT NAMES ===
# These are the ONLY valid agent identifiers
# Used in database, websockets, cross-agent communication, EVERYWHERE

class AgentNames(str, Enum):
    """The official agent roster - use these EVERYWHERE"""
    METH_SNAIL = "meth_snail"
    HAMSTERS = "hamsters"  # Yes, it's plural. Yes, Bob is in charge.
    SIR_HAWKINGTON = "sir_hawkington"
    QUANTUM_SHADOW_PEOPLE = "quantum_shadow_people"  # They prefer QSP
    VIC_20_SAGE = "vic_20_sage"  # Not vic20, not VIC-20, not Commodore (though that's tempting)
    THE_STICK = "the_stick"

# Convenience lookup for when you have strings
CANONICAL_AGENT_NAMES: Dict[str, str] = {
    # Primary lookups
    "meth_snail": AgentNames.METH_SNAIL.value,
    "hamsters": AgentNames.HAMSTERS.value,
    "sir_hawkington": AgentNames.SIR_HAWKINGTON.value,
    "quantum_shadow_people": AgentNames.QUANTUM_SHADOW_PEOPLE.value,
    "vic_20_sage": AgentNames.VIC_20_SAGE.value,
    "the_stick": AgentNames.THE_STICK.value,
    
    # Common aliases (for backwards compatibility or common mistakes)
    "the_hamsters": AgentNames.HAMSTERS.value,
    "hamster": AgentNames.HAMSTERS.value,
    "vic20": AgentNames.VIC_20_SAGE.value,
    "vic_20": AgentNames.VIC_20_SAGE.value,
    "vic-20": AgentNames.VIC_20_SAGE.value,
    "qsp": AgentNames.QUANTUM_SHADOW_PEOPLE.value,
    "hawk": AgentNames.SIR_HAWKINGTON.value,
    "stick": AgentNames.THE_STICK.value,
    "snail": AgentNames.METH_SNAIL.value,
}

# Display names for UI/logs
AGENT_DISPLAY_NAMES: Dict[str, str] = {
    AgentNames.METH_SNAIL.value: "Meth Snail (The Caffeinated Optimizer)",
    AgentNames.HAMSTERS.value: "The Hamsters (Bob, Steve & Carl's Infrastructure Chaos)",
    AgentNames.SIR_HAWKINGTON.value: "Sir Hawkington Von Monitorious III (The Aristocratic Triage Master)",
    AgentNames.QUANTUM_SHADOW_PEOPLE.value: "Quantum Shadow People (QSP - The Incomprehensible)",
    AgentNames.VIC_20_SAGE.value: "VIC-20 Sage (The Ancient Wisdom Coordinator)",
    AgentNames.THE_STICK.value: "The Stick (The Anxious Documenter)",
}

# === CROSS-AGENT COMPATIBILITY MATRIX ===
# Who plays nice with whom?

AGENT_COMPATIBILITY = {
    # Volatile combinations (require mediation)
    "volatile_pairs": [
        {AgentNames.HAMSTERS.value, AgentNames.THE_STICK.value},  # Chaos vs Order
        {AgentNames.METH_SNAIL.value, AgentNames.HAMSTERS.value},  # Chaos amplification
    ],
    
    # Synergistic combinations
    "synergies": {
        AgentNames.METH_SNAIL.value: [AgentNames.SIR_HAWKINGTON.value, AgentNames.VIC_20_SAGE.value],
        AgentNames.HAMSTERS.value: [AgentNames.THE_STICK.value, AgentNames.VIC_20_SAGE.value],  # With supervision!
        AgentNames.SIR_HAWKINGTON.value: [AgentNames.METH_SNAIL.value, AgentNames.QUANTUM_SHADOW_PEOPLE.value],
        AgentNames.QUANTUM_SHADOW_PEOPLE.value: [AgentNames.VIC_20_SAGE.value],  # Only VIC-20 understands them
        AgentNames.VIC_20_SAGE.value: list(AgentNames),  # Gets along with everyone
        AgentNames.THE_STICK.value: [AgentNames.VIC_20_SAGE.value],  # Needs calming influence
    }
}

# === SHARED PRIORITY MAPPINGS ===
# Used across all agents for consistency

class Priority(int, Enum):
    """Numeric priorities for database storage"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    ROUTINE = 1

# String-to-priority mapping (for backwards compatibility)
PRIORITY_MAP = {
    # Critical/Emergency
    "critical": Priority.CRITICAL.value,
    "emergency": Priority.CRITICAL.value,
    "hold_my_beer": Priority.CRITICAL.value,
    "full_redneck": Priority.CRITICAL.value,
    
    # High
    "high": Priority.HIGH.value,
    "urgent": Priority.HIGH.value,
    "coordination": Priority.HIGH.value,
    "mediation": Priority.HIGH.value,
    
    # Medium
    "medium": Priority.MEDIUM.value,
    "normal": Priority.MEDIUM.value,
    "synthesis": Priority.MEDIUM.value,
    "learning": Priority.MEDIUM.value,
    
    # Low
    "low": Priority.LOW.value,
    "metrics": Priority.LOW.value,
    "snapshot": Priority.LOW.value,
    
    # Routine
    "routine": Priority.ROUTINE.value,
    "observation": Priority.ROUTINE.value,
}

# === SHARED THRESHOLDS ===
# Common thresholds used by multiple agents

SYSTEM_THRESHOLDS = {
    "cpu_critical": 0.90,
    "cpu_high": 0.80,
    "memory_critical": 0.95,
    "memory_high": 0.85,
    "disk_critical": 0.95,
    "disk_high": 0.90,
    "response_time_critical": 10.0,  # seconds
    "response_time_high": 5.0,
}

# === METADATA ROLLUP MAPPING ===
# Maps agent names to their metadata columns

AGENT_TO_METADATA_COLUMN = {
    AgentNames.SIR_HAWKINGTON.value: "hawkington_memories",
    AgentNames.METH_SNAIL.value: "snail_memories",
    AgentNames.HAMSTERS.value: "hamsters_memories",
    AgentNames.QUANTUM_SHADOW_PEOPLE.value: "qsp_memories",
    AgentNames.VIC_20_SAGE.value: "vic20_memories",
    AgentNames.THE_STICK.value: "stick_memories",
}

# === HELPER FUNCTIONS ===

def get_canonical_name(agent_identifier: str) -> str:
    """
    Get the canonical agent name from any variant
    
    Args:
        agent_identifier: Any form of agent name (alias, canonical, whatever)
        
    Returns:
        Canonical agent name
        
    Raises:
        ValueError: If agent identifier is not recognized
    """
    normalized = agent_identifier.lower().strip()
    
    if normalized in CANONICAL_AGENT_NAMES:
        return CANONICAL_AGENT_NAMES[normalized]
    
    raise ValueError(
        f"Unknown agent identifier: '{agent_identifier}'. "
        f"Valid agents are: {', '.join(AgentNames)}"
    )

def is_volatile_pair(agent1: str, agent2: str) -> bool:
    """Check if two agents form a volatile combination"""
    pair = {get_canonical_name(agent1), get_canonical_name(agent2)}
    return pair in AGENT_COMPATIBILITY["volatile_pairs"]

def get_agent_synergies(agent: str) -> List[str]:
    """Get list of agents that work well with the given agent"""
    canonical = get_canonical_name(agent)
    return AGENT_COMPATIBILITY["synergies"].get(canonical, [])

# === EXPORTS ===

__all__ = [
    'AgentNames',
    'CANONICAL_AGENT_NAMES',
    'AGENT_DISPLAY_NAMES',
    'AGENT_COMPATIBILITY',
    'Priority',
    'PRIORITY_MAP',
    'SYSTEM_THRESHOLDS',
    'AGENT_TO_METADATA_COLUMN',
    'get_canonical_name',
    'is_volatile_pair',
    'get_agent_synergies',
]