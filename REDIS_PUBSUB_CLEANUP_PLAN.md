# Redis Pub/Sub Cleanup Plan

## Current Problem

Agents are using **TWO communication paths** which causes confusion and routing issues:

1. **Legacy Redis Pub/Sub** - Agents subscribe to message types and receive broadcasts
2. **Direct Agent Communication** - VIC-20 sends directly to specific agents via `send_to_agent()`

This dual system causes:
- Terry receiving disk alerts (subscribed to COORDINATION_REQUEST broadcasts)
- Hamsters receiving CPU alerts (subscribed to COORDINATION_REQUEST broadcasts)
- Duplicate message handling code
- Confusion about which path is actually used

## Current Architecture (BROKEN)

```
Hawk → VIC-20 (via TRIAGE_ALERT subscription)
         ↓
    VIC-20 sends COORDINATION_REQUEST to specific specialist
         ↓
    BUT ALL specialists are subscribed to COORDINATION_REQUEST
         ↓
    ALL specialists receive the message (Terry, Hamsters, QSP all get it)
```

## Desired Architecture (CLEAN)

```
Hawk → VIC-20 (direct send_to_agent)
         ↓
    VIC-20 → Specific Specialist (direct send_to_agent)
         ↓
    Only the targeted specialist receives and processes
```

## Files with Legacy Pub/Sub Subscriptions

### 1. Terry (meth_snail/distributed_meth_snail.py)
- **Line 149-152**: Subscribes to COORDINATION_REQUEST
- **Line 158**: `_handle_coordination_request()` callback
- **Line 437**: Legacy `handle_coordination()` method (wraps message in AgentMessage)

### 2. Hamsters (hamsters/distributed_hamsters.py)
- **Line 138-141**: Subscribes to COORDINATION_REQUEST
- **Line 161**: `_handle_coordination_request()` callback
- **Line 380**: Legacy `handle_coordination()` method

### 3. QSP (quantum_shadow_people/distributed_qsp.py)
- **Line 134-137**: Subscribes to COORDINATION_REQUEST
- **Line 157**: `_handle_coordination_request()` callback
- **Line 396**: Legacy `handle_coordination()` method

### 4. VIC-20 (vic_20_sage/distributed_vic20.py)
- **Line 155-158**: Subscribes to TRIAGE_ALERT from Hawk
- **Line 165-168**: Subscribes to ACTION_REPORT from specialists
- **Line 189**: `_handle_triage_alert_from_hawk()` callback

## Solution: Remove Pub/Sub, Use Direct Communication

### Phase 1: Remove Specialist Subscriptions
**Remove from Terry, Hamsters, QSP:**
- Remove `subscribe_to_messages(MessageType.COORDINATION_REQUEST)` calls
- Remove `_handle_coordination_request()` callback methods
- Keep only the ML v2 execution path (no message handling)

### Phase 2: VIC-20 Direct Calls
**VIC-20 should:**
- Remove subscription to TRIAGE_ALERT (Hawk should call directly)
- Remove subscription to ACTION_REPORT (specialists should call directly)
- Keep `send_to_agent()` for routing to specialists

### Phase 3: Hawk Direct Calls
**Hawk should:**
- Call VIC-20 directly instead of sending TRIAGE_ALERT message
- Use method call: `await vic20.handle_triage_alert(alert_data)`

### Phase 4: Specialist Reporting
**Specialists should:**
- Report back to VIC-20 via direct method call
- Use: `await vic20.receive_action_report(report_data)`
- Not broadcast ACTION_REPORT messages

## Implementation Steps

1. **Remove all `subscribe_to_messages()` calls from specialists**
2. **Remove all `_handle_coordination_request()` callbacks**
3. **Keep only direct method calls between agents**
4. **Remove legacy `handle_coordination()` wrapper methods**
5. **Update Hawk to call VIC-20 directly**
6. **Update specialists to report back directly**

## What to Keep

- `send_to_agent()` and `send_message()` for direct communication
- WebSocket broadcasts for frontend observability (separate from agent communication)
- Database writes for learning and history

## What to Remove

- All `subscribe_to_messages()` calls for agent-to-agent communication
- All message callback handlers (`_handle_*` methods)
- Legacy wrapper methods that convert dict → AgentMessage
- Broadcast methods for agent coordination (keep only for frontend)

## Testing After Cleanup

1. Trigger disk alert → Should go to Hamsters ONLY
2. Trigger CPU alert → Should go to Terry ONLY
3. Trigger network alert → Should go to QSP ONLY
4. No agent should receive messages meant for another agent
5. Frontend should still see all activity via WebSocket broadcasts
