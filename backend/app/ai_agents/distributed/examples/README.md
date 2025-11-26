# Distributed Agent Examples

This directory contains **example/prototype code** for educational purposes only.

**⚠️ DO NOT USE THESE IN PRODUCTION ⚠️**

## What's Here

### `example_agents.py`
Prototype implementations of distributed agents using the simpler `DistributedAgent` base class.

**This is example code only!** The actual production implementations are in each agent's directory:
- `sir_hawkington/distributed_hawkington.py`
- `meth_snail/distributed_meth_snail.py`
- `hamsters/distributed_hamsters.py`
- `quantum_shadow_people/distributed_qsp.py`
- `the_stick/distributed_stick.py`
- `vic_20_sage/distributed_vic20.py`

## Production Architecture

All production distributed agents use the `AgentDecisionEngine` pattern:

```python
from app.ai_agents.distributed.base_decision_engine import AgentDecisionEngine
from .decision_engine import AgentBrainV2

class AgentDistributed(AgentDecisionEngine, AgentBrainV2):
    """Agent with distributed consciousness"""
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        self.agent_name = "agent_name"
        self.personality_traits = {...}
        self.resource_thresholds = {...}
    
    async def initialize_distributed(self, redis_client):
        await super().initialize_distributed(redis_client)
        # Agent-specific initialization
```

## Why Examples Are Separate

The example code was useful for prototyping but doesn't follow the production architecture:
- ❌ Uses `DistributedAgent` base class (simpler but less flexible)
- ❌ Doesn't integrate with existing agent brains
- ❌ Different initialization pattern

Production code:
- ✅ Uses `AgentDecisionEngine` (consistent interface)
- ✅ Inherits from existing brain classes (preserves all logic)
- ✅ Standard initialization pattern across all agents

## See Also

- `../distributed_agent_manager.py` - Production agent initialization
- `../base_decision_engine.py` - Standard agent interface
- `../README.md` - Full distributed system documentation
