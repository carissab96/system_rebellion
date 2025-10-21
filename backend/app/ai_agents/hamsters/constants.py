# app/ai_agents/hamsters/constants.py
"""
Constants for The Hamsters - Infrastructure Chaos Engineers
Steve, Bob, and Carl's shared definitions
"""

from enum import Enum

class HamstersEventTypes(str, Enum):
    """Event types for The Hamsters' central memory bank entries"""
    
    # Infrastructure interventions
    DISK_CLEANUP = "hamsters.disk_cleanup"
    DEFRAGMENTATION = "hamsters.defragmentation"
    LOG_ROTATION = "hamsters.log_rotation"
    EMERGENCY_SPACE = "hamsters.emergency_space"
    PARTITION_MANAGEMENT = "hamsters.partition_management"
    THERMAL_EVENT = "hamsters.thermal_event"
    MYSTERY_NOISE = "hamsters.mystery_noise"
    CABLE_MANAGEMENT = "hamsters.cable_management"
    
    # Resource consumption
    BEER_CONSUMPTION = "hamsters.beer_consumption"
    DUCT_TAPE_USAGE = "hamsters.duct_tape_usage"
    SUPPLY_CLOSET_RAID = "hamsters.supply_closet_raid"
    
    # Communication
    HAMSTER_SQUEAK = "hamsters.squeak_communication"
    TELEPATHIC_CONSENSUS = "hamsters.telepathic_consensus"
    INTER_AGENT_COMM = "hamsters.inter_agent_communication"
    
    # Collective behavior
    THREE_AM_INTERVENTION = "hamsters.3am_intervention"
    COLLECTIVE_DECISION = "hamsters.collective_decision"
    DISAGREEMENT_RESOLUTION = "hamsters.disagreement_resolution"
    
    # Individual hamster events
    STEVE_ANALYSIS = "hamsters.steve_analysis"
    BOB_WILD_IDEA = "hamsters.bob_wild_idea"
    CARL_DUCT_TAPE_CALC = "hamsters.carl_duct_tape_calculation"
    
    # Pattern observations
    INFRASTRUCTURE_PATTERN = "hamsters.infrastructure_pattern"
    USER_BEHAVIOR_OBSERVATION = "hamsters.user_behavior_observation"
    PATTERN_LEARNED = "hamsters.pattern_learned"

AGENT_NAME = "hamsters"

# Individual hamster names for tracking
HAMSTER_STEVE = "steve"
HAMSTER_BOB = "bob"
HAMSTER_CARL = "carl"
ALL_HAMSTERS = [HAMSTER_STEVE, HAMSTER_BOB, HAMSTER_CARL]

# Priority mappings for central memory bank (integer values)
PRIORITY_MAP = {
    "beer_break": 1,              # LOW
    "routine_maintenance": 2,      # MEDIUM
    "supply_closet_raid": 3,      # MEDIUM-HIGH
    "hold_my_beer": 4,            # HIGH
    "full_redneck": 5             # CRITICAL
}