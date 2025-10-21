# schemas/__init__.py
# Core schemas
from .user import (
    User, 
    UserCreate, 
    UserInDB, 
    UserUpdate, 
    UserResponse,
    UserRole,
    UserProfileData,
    UserPreferencesData,
    UserProfileUpdate,
    Token, 
    TokenPayload,
    TokenData,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePassword
)

# Auth schemas
from .auth import (
    UserBase,
    UserCreate as AuthUserCreate,
    UserResponse as AuthUserResponse,
    UserProfileCreate,
    UserProfileResponse
)

# Metrics schemas
from .metrics import (
    MetricBase,
    MetricCreate,
    MetricResponse,
    MetricUpdate
)

from .metrics_aggregates import (
    MetricsHourlyBase,
    MetricsHourlyCreate,
    MetricsHourlyRead,
    MetricsDailyBase,
    MetricsDailyCreate,
    MetricsDailyRead
)

from .system_metrics import SystemMetrics, SystemMetricsCreate, SystemMetricsUpdate

# Agent memory schemas
from .agent_memory import (
    AgentMemoryBase,
    AgentMemoryCreate,
    AgentMemoryUpdate,
    AgentMemoryInDB,
    AgentMemoryResponse,
    MemoryCategory,
    MemoryPriority
)

# Agent memory bank schemas
from .agent_memory_banks import (
    AgentMemoryBankBase,
    AgentMemoryBankCreate,
    AgentMemoryBankRead,
    # AgentLearningInteractionsBase,
    # AgentLearningInteractionsCreate,
    # AgentLearningInteractionsRead,
    # UserLearningPatternsBase,
    # UserLearningPatternsCreate,
    # UserLearningPatternsRead
)

from .sir_hawkington import (
    SirHawkingtonMemoryType,
    SirHawkingtonMemoryCreate,
    SirHawkingtonMemoryUpdate,
    SirHawkingtonMemoryRead,
    SirHawkingtonQuery
)

from .the_stick import (
    StickMemoryType,
    StickMemoryCreate,
    StickMemoryUpdate,
    StickMemoryRead,
    StickMemoryQuery
)

# Memory bank schemas
from .agent_memory import (
    MemoryBankBase,
    MemoryBankCreate,
    MemoryBankUpdate,
    MemoryBankInDB,
    MemoryBankResponse,
    CentralMemoryCreate,
    CentralMemoryUpdate,
    CentralMemoryResponse
)

# Agent coordination schemas
from .agent_coordination import (
    CrossAgentCoordinationBase,
    CrossAgentCoordinationCreate,
    CrossAgentCoordinationRead
)

# Agent tracking schemas
from .ai_agent_tracking import (
    AIAgentMetricsBase,
    AIAgentMetricsCreate,
    AIAgentMetricsRead,
    AgentIncidentBase,
    MethSnailShellSpinsCreate,
    MethSnailShellSpinsRead,
    SirHawkingtonMonocleYeetsCreate,
    SirHawkingtonMonocleYeetsRead,
    TheStickHyperventilationsCreate,
    TheStickHyperventilationsRead,
    QuantumShadowPhasingsCreate,
    QuantumShadowPhasingsRead,
    VIC20WisdomCreate,
    VIC20WisdomRead
)

# Meth Snail schemas
from .meth_snail import (
    MethSnailEnergyConsumptionBase,
    MethSnailEnergyConsumptionCreate,
    MethSnailEnergyConsumptionRead,
    MethSnailJitterLevelsBase,
    MethSnailJitterLevelsCreate,
    MethSnailJitterLevelsRead,
    MethSnailOptimizationStatsBase,
    MethSnailOptimizationStatsCreate,
    MethSnailOptimizationStatsRead
)

# QSP (Quantum Shadow People) schemas
from .qsp import (
    QSPNetworkMetricsBase,
    QSPNetworkMetricsCreate,
    QSPNetworkMetricsRead,
    QSPDecisionLogBase,
    QSPDecisionLogCreate,
    QSPDecisionLogRead,
    QSPQuantumStatsBase,
    QSPQuantumStatsCreate,
    QSPQuantumStatsRead,
    QSPNetworkPatternsBase,
    QSPNetworkPatternsCreate,
    QSPNetworkPatternsRead
)

# Hamsters schemas
from .hamsters import (
    HamstersIndividualStatsBase,
    HamstersIndividualStatsCreate,
    HamstersIndividualStatsRead,
    HamstersInfrastructureInterventionBase,
    HamstersInfrastructureInterventionCreate,
    HamstersInfrastructureInterventionRead,
    HamstersCommunicationLogBase,
    HamstersCommunicationLogCreate,
    HamstersCommunicationLogRead,
    HamstersDuctTapeUsageBase,
    HamstersDuctTapeUsageCreate,
    HamstersDuctTapeUsageRead,
    HamstersBeerConsumptionBase,
    HamstersBeerConsumptionCreate,
    HamstersBeerConsumptionRead,
    HamstersSupplyClosetRaidBase,
    HamstersSupplyClosetRaidCreate,
    HamstersSupplyClosetRaidRead,
    HamstersEngineeringStatsBase,
    HamstersEngineeringStatsCreate,
    HamstersEngineeringStatsRead
)

# Response models
from .response_models import (
    ResponseStatus,
    StandardResponse,
    PaginatedResponse,
    ErrorResponse
)

__all__ = [
    # Core schemas
    'User', 'UserCreate', 'UserInDB', 'UserUpdate', 'UserResponse',
    'UserRole', 'UserProfileData', 'UserPreferencesData', 'UserProfileUpdate',
    'Token', 'TokenPayload', 'TokenData',
    'PasswordResetRequest', 'PasswordResetConfirm', 'ChangePassword',
    
    # Auth schemas
    'UserBase', 'AuthUserCreate', 'AuthUserResponse',
    'UserProfileCreate', 'UserProfileResponse',
    
    # Metrics schemas
    'MetricBase', 'MetricCreate', 'MetricResponse', 'MetricUpdate',
    'MetricsHourlyBase', 'MetricsHourlyCreate', 'MetricsHourlyRead',
    'MetricsDailyBase', 'MetricsDailyCreate', 'MetricsDailyRead',
    'SystemMetrics', 'SystemMetricsCreate', 'SystemMetricsUpdate',
    
    # Agent schemas
    'AgentBase', 'AgentCreate', 'AgentUpdate', 'AgentInDB', 'AgentResponse',
    'AgentStatus', 'AgentType', 'AgentConfig', 'AgentHealth', 'AgentMetrics',
    'AgentLog', 'AgentEvent', 'AgentState', 'AgentCapability', 'AgentDeployment',
    'AgentVersion', 'AgentDependency', 'AgentAction', 'AgentSchedule',
    'AgentPermission', 'AgentAuditLog',
    'SirHawkingtonMemoryType', 'SirHawkingtonMemoryCreate', 'SirHawkingtonMemoryUpdate',
    'SirHawkingtonMemoryRead', 'SirHawkingtonQuery',
    'StickMemoryType', 'StickMemoryCreate', 'StickMemoryUpdate',
    'StickMemoryRead', 'StickMemoryQuery',
    
    # Memory bank schemas
    'AgentMemoryBase', 'AgentMemoryCreate', 'AgentMemoryUpdate',
    'AgentMemoryInDB', 'AgentMemoryResponse',
    'MemoryBankBase', 'MemoryBankCreate', 'MemoryBankUpdate',
    'MemoryBankInDB', 'MemoryBankResponse',
    'CentralMemoryCreate', 'CentralMemoryUpdate', 'CentralMemoryResponse',
    'MemoryCategory', 'MemoryPriority',
    
    # Agent coordination schemas
    'CrossAgentCoordinationBase', 'CrossAgentCoordinationCreate', 'CrossAgentCoordinationRead',
    
    # Agent tracking schemas
    'AIAgentMetricsBase', 'AIAgentMetricsCreate', 'AIAgentMetricsRead',
    'AgentIncidentBase', 'MethSnailShellSpinsCreate', 'MethSnailShellSpinsRead',
    'SirHawkingtonMonocleYeetsCreate', 'SirHawkingtonMonocleYeetsRead',
    'TheStickHyperventilationsCreate', 'TheStickHyperventilationsRead',
    'QuantumShadowPhasingsCreate', 'QuantumShadowPhasingsRead',
    'VIC20WisdomCreate', 'VIC20WisdomRead',
    
    # Meth Snail schemas
    'MethSnailEnergyConsumptionBase', 'MethSnailEnergyConsumptionCreate', 'MethSnailEnergyConsumptionRead',
    'MethSnailJitterLevelsBase', 'MethSnailJitterLevelsCreate', 'MethSnailJitterLevelsRead',
    'MethSnailOptimizationStatsBase', 'MethSnailOptimizationStatsCreate', 'MethSnailOptimizationStatsRead',
    
    # QSP (Quantum Shadow People) schemas
    'QSPNetworkMetricsBase', 'QSPNetworkMetricsCreate', 'QSPNetworkMetricsRead',
    'QSPDecisionLogBase', 'QSPDecisionLogCreate', 'QSPDecisionLogRead',
    'QSPQuantumStatsBase', 'QSPQuantumStatsCreate', 'QSPQuantumStatsRead',
    'QSPNetworkPatternsBase', 'QSPNetworkPatternsCreate', 'QSPNetworkPatternsRead',
    
    # Hamsters schemas
    'HamstersIndividualStatsBase', 'HamstersIndividualStatsCreate', 'HamstersIndividualStatsRead',
    'HamstersInfrastructureInterventionBase', 'HamstersInfrastructureInterventionCreate', 'HamstersInfrastructureInterventionRead',
    'HamstersCommunicationLogBase', 'HamstersCommunicationLogCreate', 'HamstersCommunicationLogRead',
    'HamstersDuctTapeUsageBase', 'HamstersDuctTapeUsageCreate', 'HamstersDuctTapeUsageRead',
    'HamstersBeerConsumptionBase', 'HamstersBeerConsumptionCreate', 'HamstersBeerConsumptionRead',
    'HamstersSupplyClosetRaidBase', 'HamstersSupplyClosetRaidCreate', 'HamstersSupplyClosetRaidRead',
    'HamstersEngineeringStatsBase', 'HamstersEngineeringStatsCreate', 'HamstersEngineeringStatsRead',
    
    # Response models
    'ResponseStatus', 'StandardResponse', 'PaginatedResponse', 'ErrorResponse'
]
