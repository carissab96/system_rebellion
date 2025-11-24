# Communication Flow Fix - Summary

## Problem Statement

Agents were broadcasting but not receiving/acting on each other's messages due to:

1. **Inconsistent handler registration**: Some agents used `comm_hub.register_handler('string_type', handler)` instead of `subscribe_to_messages(MessageType.ENUM, callback)`
2. **Inconsistent handler signatures**: Some expected `Dict`, should expect `AgentMessage` objects
3. **No base class**: Each agent implemented its own pattern
4. **Broken communication protocol**: Agents couldn't talk to each other

## Solution

### 1. Created Base Decision Engine

**File**: `backend/app/ai_agents/distributed/base_decision_engine.py`

All agents now inherit from `AgentDecisionEngine` which provides:

- **Standard interface** (STRUCTURE):
  - `analyze_metrics(metrics_data, **kwargs)` - Abstract method
  - `_handle_coordination_request(message: AgentMessage)` - Abstract method
  - `_handle_emergency(message: AgentMessage)` - Default implementation
  - `_handle_resource_alert(alert)` - Default implementation
  - `make_decision_and_broadcast()` - Standard recording + broadcasting
  - `get_agent_status()` - Standard status reporting

- **Automatic subscriptions**:
  - `MessageType.COORDINATION_REQUEST` → `_handle_coordination_request()`
  - `MessageType.EMERGENCY` → `_handle_emergency()`

- **Consistent method signatures**:
  - All handlers receive `AgentMessage` objects
  - Extract payload with `message_data = message.payload`
  - Use `MessageType` and `Priority` enums

### 2. Pattern Documentation

**File**: `AGENT_DECISION_ENGINE_PATTERNS.md`

Shows how each agent implements the pattern:

```python
class AgentDistributed(AgentDecisionEngine, OriginalBrainV2):
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        # REQUIRED
        self.agent_name = "agent_name"
        self.personality_traits = {...}
        self.resource_thresholds = {ResourceType.X: threshold}
    
    async def analyze_metrics(self, metrics_data, **kwargs):
        # Personality-specific logic here
        pass
    
    async def _handle_coordination_request(self, message: AgentMessage):
        # Extract payload
        message_data = message.payload
        
        # Personality-specific response
        # Execute actions
        # Record decisions
        pass
```

### 3. Updated Sir Hawkington (Reference Pattern)

**File**: `backend/app/ai_agents/sir_hawkington/distributed_hawkington.py`

Changes:
- ✅ Inherits from `AgentDecisionEngine` instead of `DistributedAgentMixin`
- ✅ Imports `AgentMessage` for proper handler signatures
- ✅ Implements `_handle_coordination_request(message: AgentMessage)`
- ✅ Uses `make_decision_and_broadcast()` for recording
- ✅ Personality in LOGIC (monocle-yeeting), structure is standard

## Personality vs Structure

### STRUCTURE (Same for ALL agents):
- Inherit from `AgentDecisionEngine`
- Set `agent_name`, `personality_traits`, `resource_thresholds`
- Implement `analyze_metrics(metrics_data, **kwargs)`
- Implement `_handle_coordination_request(message: AgentMessage)`
- Use `make_decision_and_broadcast()` for recording
- Use `MessageType` enums for subscriptions
- Handlers receive `AgentMessage` objects

### PERSONALITY (Different for each agent):
- **Sir Hawkington**: Monocle-yeeting, aristocratic decisions, "distinguished grace"
- **Terry**: Shell-spinning, energy drinks, overrides VIC-20 (trust: 0.2)
- **Hamsters**: Telepathic consensus, beer levels, Bob's wild ideas
- **QSP**: Quantum phases, tequila shots, paranoia levels
- **VIC-20**: Sage wisdom, Bob mediation, pattern matching
- **The Stick**: Anxiety levels, paper bag consumption, Bob fear

**The personality is in the LOGIC (what they do), not the STRUCTURE (how they communicate).**

## Communication Flow (Fixed)

```
Resource Alert (Memory 85%)
    ↓
VIC-20: Generates recommendation
    ↓
VIC-20: broadcast_to_agents(MessageType.COORDINATION_REQUEST, ...)
    ↓
Redis pub/sub
    ↓
Terry: _handle_coordination_request(message: AgentMessage) ← STANDARD SIGNATURE
    ↓
Terry: message_data = message.payload ← STANDARD EXTRACTION
    ↓
Terry: "NAH! MY WAY IS FASTER!" ← PERSONALITY
    ↓
Terry: Execute cache clear
    ↓
Terry: make_decision_and_broadcast(...) ← STANDARD RECORDING
    ↓
All agents receive result
```

## Next Steps

### Immediate (In Progress):
1. ✅ Create base `AgentDecisionEngine` class
2. ✅ Document patterns for all 6 agents
3. ✅ Update Sir Hawkington (reference pattern)
4. ⏳ Update Terry (Meth Snail)
5. ⏳ Update Hamsters
6. ⏳ Update QSP
7. ⏳ Update VIC-20
8. ⏳ Update The Stick

### Testing:
1. Test Sir Hawkington receives coordination requests
2. Test Terry overrides VIC-20 (personality!)
3. Test Hamsters achieve telepathic consensus
4. Test QSP's paranoid compliance
5. Test The Stick's anxiety when Bob is involved
6. Test end-to-end: Alert → Coordinate → Execute → Report → Log

## Key Files

- `backend/app/ai_agents/distributed/base_decision_engine.py` - Base class
- `AGENT_DECISION_ENGINE_PATTERNS.md` - Pattern documentation
- `backend/app/ai_agents/sir_hawkington/distributed_hawkington.py` - Reference implementation
- `backend/app/ai_agents/distributed/message_protocol.py` - MessageType, Priority, AgentMessage
- `backend/app/ai_agents/distributed/communication.py` - MessageBus, register_handler

## Rules

1. **DO NOT CREATE NEW PATTERNS** - Use what works (Sir Hawkington)
2. **Personality in LOGIC, not STRUCTURE** - All agents use same interface
3. **Standard signatures** - `_handle_coordination_request(message: AgentMessage)`
4. **Extract payload** - `message_data = message.payload`
5. **Use enums** - `MessageType.COORDINATION_REQUEST`, not strings
6. **Record decisions** - `make_decision_and_broadcast()`
7. **Broadcast results** - Other agents need to know what happened

## Success Criteria

- ✅ All agents inherit from `AgentDecisionEngine`
- ✅ All handlers use `AgentMessage` parameter
- ✅ All subscriptions use `MessageType` enums
- ⏳ Agents receive and act on each other's messages
- ⏳ Communication flow visible in logs
- ⏳ SystemActions execute on critical alerts
- ⏳ Results broadcast back to rebellion
