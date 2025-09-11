"""
Meth Snail Agent Constants
Defines all constants used across the Meth Snail agent components
"""

from typing import Dict, Any

# Agent Identity
AGENT_NAME = "meth_snail"
AGENT_DISPLAY_NAME = "Meth Snail"
AGENT_DESCRIPTION = "Caffeine-powered optimization engine"

# Learning Configuration
MIN_OBSERVATIONS_FOR_PATTERN = 50  # Observations before pattern learning
PATTERN_CONFIDENCE_THRESHOLD = 0.9  # Confidence required for global promotion
LEARNING_RATE = 0.85  # How quickly the snail adapts
MEMORY_DECAY_RATE = 0.1  # How fast old patterns fade

# Memory Priorities (8+ gets pinned)
PRIORITY_SHELL_SPIN = 8  # Shell spin incidents - always important
PRIORITY_HIGH_CONFIDENCE_DECISION = 8  # High confidence optimizations
PRIORITY_HYPERCAFFEINATED = 9  # Extreme jitter events
PRIORITY_OPTIMIZATION_SUCCESS = 7  # Successful optimizations
PRIORITY_STANDARD = 5  # Regular events

# Pattern Categories
PATTERN_CATEGORIES = {
    "optimization": "System optimization patterns",
    "shell_spinning": "Data quality and shell spin patterns", 
    "caffeine_management": "Energy drink and jitter patterns",
    "performance": "System performance patterns"
}

# Learning Types for Cross-Agent Sharing
LEARNING_TYPES = {
    "optimization_insight": "Performance optimization discoveries",
    "shell_spin_pattern": "Data quality issue patterns",
    "caffeine_protocol": "Energy management insights",
    "jitter_correlation": "Jitter level impact patterns"
}

# Event Types
EVENT_TYPES = {
    "OPTIMIZATION_APPLIED": "optimization_applied",
    "SHELL_SPIN_DETECTED": "shell_spin_detected",
    "JITTER_LEVEL_CRITICAL": "jitter_level_critical",
    "ENERGY_DRINK_CONSUMED": "energy_drink_consumed",
    "PATTERN_DISCOVERED": "pattern_discovered"
}

# Metadata Keys
METADATA_KEYS = {
    "shell_spin_count": "Number of shell spins",
    "optimization_type": "Type of optimization applied",
    "caffeine_level": "Current caffeine level in mg",
    "jitter_level": "Current jitter level (0.0-1.0)",
    "data_quality_score": "Quality of input data"
}

# Pattern Detection Configuration
PATTERN_DETECTION_CONFIG = {
    "min_confidence": 0.7,  # Minimum confidence to store pattern
    "promotion_threshold": 0.9,  # Threshold for global promotion
    "correlation_threshold": 0.6,  # Minimum correlation for relationships
    "max_pattern_age_days": 30,  # Maximum age for relevant patterns
}

# Jitter Level Thresholds
JITTER_THRESHOLDS = {
    "calm": 0.2,
    "normal": 0.4,
    "energized": 0.6,
    "jittery": 0.8,
    "hypercaffeinated": 1.0
}

# Shell Spin Thresholds
SHELL_SPIN_CONFIG = {
    "max_spins_before_alert": 5,  # Alert after this many spins
    "spin_memory_priority": 8,  # Priority for spin memories
    "spin_pattern_weight": 1.5,  # Weight multiplier for spin patterns
}

# Cross-Agent Learning Configuration
CROSS_AGENT_CONFIG = {
    "share_with_agents": ["the_stick", "sir_hawkington", "vic20"],
    "accept_from_agents": ["sir_hawkington", "vic20"],
    "validation_required": True,
    "min_effectiveness_to_share": 0.7
}

# Default Pattern Structure
DEFAULT_PATTERN_STRUCTURE = {
    "pattern_type": None,
    "confidence": 0.0,
    "occurrences": 0,
    "last_seen": None,
    "effectiveness": 0.0,
    "context": {},
    "related_metrics": []
}

# Learning Effectiveness Thresholds
EFFECTIVENESS_THRESHOLDS = {
    "excellent": 0.9,
    "good": 0.7,
    "moderate": 0.5,
    "poor": 0.3,
    "ineffective": 0.0
}