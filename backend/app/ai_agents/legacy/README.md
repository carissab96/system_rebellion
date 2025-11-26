# Legacy Agent System

This directory contains the **legacy agent management system** that has been deprecated in favor of the distributed agent system.

**⚠️ DO NOT USE - DEPRECATED AS OF WEEK 5 TASK 5.4 ⚠️**

## What's Here

### `agents_config.yaml`
YAML configuration file that was used by the legacy `AIAgentManager` to load agents dynamically.

**This is no longer used.** Agents are now initialized directly by `DistributedAgentManager` in:
- `app/ai_agents/distributed/distributed_agent_manager.py`

### `agent_manager.py`
Legacy agent management system that loaded agents from YAML configuration.

**This is no longer used.** Replaced by `DistributedAgentManager` which initializes agents directly.

### `master_agent_database.py`
Centralized database integration for dual-write pattern (agent table + memory bank).

**This is no longer used.** Each distributed agent now has its own `AgentStateManager` for Redis-based state persistence.

### `master_websocket_router.py`
Legacy WebSocket message routing system.

**This is no longer used.** Replaced by `WebSocketManager` in `app/api/websockets.py`

## Why Deprecated?

The legacy system had two major issues:

1. **Duplicate Initialization** - Both `AIAgentManager` and `DistributedAgentManager` were initializing the same agents
2. **Architectural Confusion** - Two parallel systems doing the same thing

## Migration (Completed November 26, 2025)

**Before:**
```python
# main.py - TWO systems running
agent_manager = await get_agent_manager(db_getter=db_session_factory)  # Legacy
await initialize_distributed_agents(redis_url, db_getter=db_session_factory)  # New
```

**After:**
```python
# main.py - ONE unified system
await initialize_distributed_agents(redis_url, db_getter=db_session_factory)  # Only this!
```

## Current System

All agents are now initialized through `DistributedAgentManager`:

```python
from app.ai_agents.distributed.distributed_agent_manager import (
    initialize_distributed_agents,
    shutdown_distributed_agents,
    get_distributed_manager
)

# Initialize all 6 agents
await initialize_distributed_agents(redis_url, db_getter=db_session_factory)

# Get manager instance
manager = get_distributed_manager()

# Get specific agent
sir_hawk = manager.get_agent("sir_hawkington")

# Get all agents
all_agents = manager.get_all_agents()

# Get system status
status = await manager.get_system_status()
```

## Agent Implementations

All agents now use the distributed implementations:
- `sir_hawkington/distributed_hawkington.py` - SirHawkingtonDistributed
- `meth_snail/distributed_meth_snail.py` - TerryMethSnailDistributed
- `hamsters/distributed_hamsters.py` - BobHamsterDistributed
- `quantum_shadow_people/distributed_qsp.py` - QuantumShadowPeopleDistributed
- `the_stick/distributed_stick.py` - TheStickDistributed
- `vic_20_sage/distributed_vic20.py` - VIC20SageDistributed

Each inherits from:
- `AgentDecisionEngine` (distributed interface)
- Their existing brain class (preserves all logic)

## See Also

- `../distributed/distributed_agent_manager.py` - Current agent initialization
- `../distributed/README.md` - Distributed system documentation
- `/docs/completed-tasks/WEEK5_TASK5.4_COMPLETE.md` - Migration documentation
