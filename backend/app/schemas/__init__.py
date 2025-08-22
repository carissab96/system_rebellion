# schemas/__init__.py
# Core schemas
from .user import User, UserCreate, UserInDB, UserUpdate, Token, TokenPayload
from .system_metrics import SystemMetrics, SystemMetricsCreate, SystemMetricsUpdate

# Agent schemas
from .sir_hawkington import (
    HawkingtonMemoryType,
    HawkingtonMemoryCreate,
    HawkingtonMemoryUpdate,
    HawkingtonMemoryInDB,
    HawkingtonMemoryResponse
)

from .the_stick import (
    StickMemoryType,
    StickMemoryCreate,
    StickMemoryUpdate,
    StickMemoryInDB,
    StickMemoryResponse
)

from .vic20_sage import (
    VIC20WisdomType,
    VIC20WisdomCreate,
    VIC20WisdomUpdate,
    VIC20WisdomInDB,
    VIC20WisdomResponse
)

# Memory bank schemas
from .agent_memory import (
    AgentMemoryBase,
    AgentMemoryCreate,
    AgentMemoryUpdate,
    AgentMemoryInDB,
    AgentMemoryResponse,
    MemoryBankBase,
    MemoryBankCreate,
    MemoryBankUpdate,
    MemoryBankInDB,
    MemoryBankResponse,
    CentralMemoryCreate,
    CentralMemoryUpdate,
    CentralMemoryResponse
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
    'User', 'UserCreate', 'UserInDB', 'UserUpdate', 'Token', 'TokenPayload',
    'SystemMetrics', 'SystemMetricsCreate', 'SystemMetricsUpdate',
    
    # Agent schemas
    'HawkingtonMemoryType', 'HawkingtonMemoryCreate', 'HawkingtonMemoryUpdate',
    'HawkingtonMemoryInDB', 'HawkingtonMemoryResponse',
    
    'StickMemoryType', 'StickMemoryCreate', 'StickMemoryUpdate',
    'StickMemoryInDB', 'StickMemoryResponse',
    
    'VIC20WisdomType', 'VIC20WisdomCreate', 'VIC20WisdomUpdate',
    'VIC20WisdomInDB', 'VIC20WisdomResponse',
    
    # Memory bank schemas
    'AgentMemoryBase', 'AgentMemoryCreate', 'AgentMemoryUpdate',
    'AgentMemoryInDB', 'AgentMemoryResponse',
    'MemoryBankBase', 'MemoryBankCreate', 'MemoryBankUpdate',
    'MemoryBankInDB', 'MemoryBankResponse',
    'CentralMemoryCreate', 'CentralMemoryUpdate', 'CentralMemoryResponse',
    
    # Response models
    'ResponseStatus', 'StandardResponse', 'PaginatedResponse', 'ErrorResponse'
]
