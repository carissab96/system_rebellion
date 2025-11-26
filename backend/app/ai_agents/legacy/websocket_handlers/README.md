# Legacy WebSocket Handlers

**⚠️ DEPRECATED AS OF WEEK 5 TASK 5.4 ⚠️**

These files are the old individual websocket handlers that were used by `master_websocket_router.py`.

---

## What's Here

### Individual Agent WebSocket Handlers (DEPRECATED)
- `hawks_websocket_integration.py` - Sir Hawkington's old handler
- `meth_snail_websocket_handler.py` - Terry's old handler  
- `sticks_websocket_integration.py` - The Stick's old handler
- `vic20_websocket_handler.py` - VIC-20's old handler
- `qsp_websocket_integration.py` - Quantum Shadow People's old handler

**NOT HERE**: `hamsters_websocket_integration.py` - Still in use by `hamsters_api_routes_refactored.py` (see TODO below)

---

## Why Deprecated?

### Old Architecture (DEPRECATED)
```
Metrics → master_websocket_router → individual handlers → process → respond
                                           ↑
                                    (these files)
```

Each agent had a websocket handler that:
1. Received metrics via WebSocket
2. Processed them using the agent's brain
3. Sent responses back via WebSocket

### New Architecture (CURRENT)
```
Metrics → Distributed Agents → Redis → WebSocketManager → Frontend
                ↑                              ↑
        (process & decide)            (forward messages)
```

Now:
1. **Distributed agents** process metrics and make decisions
2. **Distributed agents** publish to Redis channels
3. **WebSocketManager** (`app/api/websockets.py`) forwards Redis messages to frontend
4. No individual handlers needed!

---

## What Replaced Them?

### Distributed Agent System
Each agent now has a distributed implementation:
- `sir_hawkington/distributed_hawkington.py`
- `meth_snail/distributed_meth_snail.py`
- `hamsters/distributed_hamsters.py`
- `the_stick/distributed_stick.py`
- `vic_20_sage/distributed_vic20.py`
- `quantum_shadow_people/distributed_qsp.py`

These handle:
- ✅ Metric processing
- ✅ Decision making
- ✅ Redis pub/sub messaging
- ✅ State persistence
- ✅ Resource monitoring

### WebSocket Bridge
`app/api/websockets.py` (WebSocketManager) handles:
- ✅ Redis → WebSocket message forwarding
- ✅ Multiple client connections
- ✅ Message buffering
- ✅ Channel routing

**No individual handlers needed!**

---

## 🚨 TODO: Hamsters Integration

### Current Issue
`app/ai_agents/hamsters/hamsters_api_routes_refactored.py` still uses:
```python
from app.ai_agents.hamsters.hamsters_websocket_integration import broadcast_hamster_event
```

This is a **direct WebSocket broadcast** that bypasses the distributed system.

### Should Be
```python
# Use distributed agent messaging instead
hamsters_agent = manager.get_agent("bob_hamster")
await hamsters_agent.broadcast_message(
    MessageType.AGENT_EVENT,
    {
        'type': 'recommendation',
        'priority': decision.priority.value,
        'squeaks': decision.actual_squeaks,
        ...
    }
)
```

### Action Required
- [ ] Refactor `hamsters_api_routes_refactored.py` to use distributed agent messaging
- [ ] Remove `broadcast_hamster_event` calls
- [ ] Use distributed agent's `broadcast_message()` method instead
- [ ] Move `hamsters_websocket_integration.py` to legacy after refactor

**Estimated Time**: 1-2 hours

---

## Migration Complete For
- ✅ Sir Hawkington - Uses distributed system
- ✅ Terry the Meth Snail - Uses distributed system
- ✅ The Stick - Uses distributed system
- ✅ VIC-20 Sage - Uses distributed system
- ✅ Quantum Shadow People - Uses distributed system
- ⏳ Hamsters - Partially migrated (API routes still use old handler)

---

## See Also
- `../master_websocket_router.py` - The deprecated router that used these handlers
- `../../api/websockets.py` - The new WebSocketManager
- `../../distributed/distributed_agent_manager.py` - Agent initialization
- `/docs/completed-tasks/WEEK5_TASK5.4_COMPLETE.md` - Migration documentation
