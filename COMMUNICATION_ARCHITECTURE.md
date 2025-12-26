# Communication Architecture - Clean Separation

## Two Separate Communication Channels

### 1. Agent-to-Agent Communication (Backend Only)
**Purpose:** Agents coordinate with each other  
**Method:** Direct method calls via `send_to_agent()`  
**NO Redis pub/sub subscriptions**

```python
# VIC-20 sends to specific specialist
await self.send_to_agent(
    to_agent="meth_snail",  # Direct to Terry
    message_type=MessageType.COORDINATION_REQUEST,
    payload={...}
)
```

**Flow:**
```
Hawk → VIC-20 (direct send_to_agent)
  ↓
VIC-20 → Specific Specialist (direct send_to_agent)
  ↓
Specialist processes and responds
```

### 2. Frontend Observability (WebSocket Broadcasts)
**Purpose:** Frontend sees agent activity in real-time  
**Method:** `emit_agent_insight()` WebSocket broadcasts  
**Always broadcast, never subscribe**

```python
# Broadcast to frontend (not to other agents!)
from app.services.agent_insight_emitter import emit_agent_insight
await emit_agent_insight(
    from_agent="meth_snail",
    to_agent="vic20_sage",  # For display purposes only
    action="cache_clear_executed",
    reasoning="Freeing memory...",
    context={...}
)
```

**What Gets Broadcast:**
- Agent decisions
- Actions executed
- Success/failure results
- Personality behaviors (shell spins, beer consumption, etc.)
- Coordination events
- Learning outcomes

## Current State (After Cleanup)

### ✅ Correct: Agent-to-Agent
- **Removed:** All `subscribe_to_messages()` for agent coordination
- **Using:** Direct `send_to_agent()` calls
- **Result:** Clean, targeted communication

### ✅ Correct: Frontend Observability  
- **Kept:** All `emit_agent_insight()` WebSocket broadcasts
- **Using:** WebSocket for real-time frontend updates
- **Result:** Frontend sees everything

## What Each Agent Should Do

### Terry (Meth Snail)
**Agent Communication:**
- ❌ NO subscription to COORDINATION_REQUEST
- ✅ Receives direct calls from VIC-20 via `send_to_agent()`

**Frontend Broadcasts:**
- ✅ Broadcast when action selected
- ✅ Broadcast when action executed
- ✅ Broadcast success/failure
- ✅ Broadcast shell spins, energy drinks

### Hamsters
**Agent Communication:**
- ❌ NO subscription to COORDINATION_REQUEST
- ✅ Receives direct calls from VIC-20 via `send_to_agent()`

**Frontend Broadcasts:**
- ✅ Broadcast when consensus reached
- ✅ Broadcast when action executed
- ✅ Broadcast success/failure
- ✅ Broadcast beer consumption, duct tape usage, Bob at cupboard

### QSP (Quantum Shadow People)
**Agent Communication:**
- ❌ NO subscription to COORDINATION_REQUEST
- ✅ Receives direct calls from VIC-20 via `send_to_agent()`

**Frontend Broadcasts:**
- ✅ Broadcast when threat detected
- ✅ Broadcast when action executed
- ✅ Broadcast success/failure
- ✅ Broadcast quantum state, existential dread, Hamster messages

### VIC-20
**Agent Communication:**
- ❌ NO subscription to TRIAGE_ALERT from Hawk
- ❌ NO subscription to ACTION_REPORT from specialists
- ✅ Receives direct calls from Hawk via `send_to_agent()`
- ✅ Sends direct calls to specialists via `send_to_agent()`

**Frontend Broadcasts:**
- ✅ Broadcast when routing to specialist
- ✅ Broadcast coordination decisions
- ✅ Broadcast learning from specialist reports

### Sir Hawkington
**Agent Communication:**
- ✅ Sends direct calls to VIC-20 via `send_to_agent()`

**Frontend Broadcasts:**
- ✅ Broadcast when alert detected
- ✅ Broadcast triage decisions
- ✅ Broadcast monocle yeets

### The Stick
**Agent Communication:**
- ✅ Receives decision logs from all agents

**Frontend Broadcasts:**
- ✅ Broadcast anxiety levels
- ✅ Broadcast paper bag consumption
- ✅ Broadcast Bob detections

## Key Principle

**NEVER mix the two channels:**
- Agent-to-agent = Direct calls (no pub/sub)
- Frontend observability = WebSocket broadcasts (always emit, never subscribe)

The confusion happened because we were using Redis pub/sub for BOTH channels.
Now they're completely separate and clean.
