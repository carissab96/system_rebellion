# models/__init__.py
# Core models
from .user import User
from .metrics import SystemMetrics
from .metrics_aggregates import MetricsHourly, MetricsDaily
from .agent_memory_banks import CentralMemoryBank
from .agent_memory_banks import UserLearningPatterns
from .agent_memory_banks import MemoryBankMetadata
from .agent_memory_banks import AgentLearningInteractions
from .agent_memory_banks import SirHawkingtonMemoryBank
from .agent_memory_banks import MethSnailMemoryBank
from .agent_memory_banks import TheStickMemoryBank
from .agent_memory_banks import HamstersMemoryBank
from .agent_memory_banks import QuantumShadowPeopleMemoryBank
from .agent_memory_banks import VIC20MemoryBank

# Vector tables for semantic search
from .vector_tables import AgentDecisionVectors, AgentPatternVectors, AgentInteractionVectors

# Agent learning records (shared across all agents)
from .agent_learning import AgentLearningRecord

# Learned thresholds and action effectiveness
from .learned_thresholds import ThresholdLearningRecord, ActionOutcomeRecord, MetricPatternHistory, LearnedSequence

# Memory bank models
# Ensure all models are imported and registered
__all__ = [
    # Core models
    'User', 'SystemMetrics', 'MetricsHourly', 'MetricsDaily',
    
    # Central Memory Bank
    'CentralMemoryBank', 'UserLearningPatterns', 'MemoryBankMetadata', 'AgentLearningInteractions',
    
    # Agent-specific memory banks
    'SirHawkingtonMemoryBank', 'MethSnailMemoryBank', 'TheStickMemoryBank', 'HamstersMemoryBank', 'QuantumShadowPeopleMemoryBank', 'VIC20MemoryBank',
    
    # Vector tables
    'AgentDecisionVectors', 'AgentPatternVectors', 'AgentInteractionVectors',
    
    # Agent learning records
    'AgentLearningRecord',

    # Learned thresholds
    'ThresholdLearningRecord', 'ActionOutcomeRecord', 'MetricPatternHistory', 'LearnedSequence',
]