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

- `hamsters_websocket_integration.py` - Hamsters' old handler (moved here with API routes)

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

## ✅ Hamsters Direct API Deprecated

### What Was Removed
`app/ai_agents/hamsters/hamsters_api_routes_refactored.py` - Direct API for hamster control

This API provided direct endpoints for:
- `/hamsters/recommendations` - Get infrastructure recommendations
- `/hamsters/apply-engineering` - Apply fixes directly
- `/hamsters/emergency` - Emergency response
- `/hamsters/history` - View intervention history
- `/hamsters/supply-closet` - Check supplies
- `/hamsters/restock` - Restock inventory
- `/hamsters/stats` - Get hamster stats
- `/hamsters/reset` - Reset brain state

### Why Deprecated
This API **bypassed VIC-20's coordination system** completely. It allowed direct control of the Hamsters, which conflicts with the distributed architecture where:
- VIC-20 coordinates all agent activities
- Agents communicate via Redis pub/sub
- Decisions go through triage and verification

### New Architecture
Hamsters now operate through:
1. **Distributed Agent System** - `distributed_hamsters.py` (HamstersDistributed)
2. **VIC-20 Coordination** - VIC-20 routes disk/storage tasks to Hamsters
3. **Redis Messaging** - All communication via Redis channels
4. **Triage System** - Sir Hawkington triages, routes to appropriate agent

### Personalities Preserved
Steve, Bob, and Carl's individual personalities are fully preserved in:
- `decision_engine_sbcV3.py` (HamstersBrainV3) - Core logic
- `distributed_hamsters.py` (HamstersDistributed) - Distributed wrapper

**Steve** (careful, risk_tolerance=0.3), **Bob** (wild, risk_tolerance=0.8, causes Stick anxiety), and **Carl** (duct tape genius, duct_tape_love=1.0) all maintain their distinct personalities and telepathic consensus system.

---

## Migration Complete For
- ✅ Sir Hawkington - Uses distributed system
- ✅ Terry the Meth Snail - Uses distributed system
- ✅ The Stick - Uses distributed system
- ✅ VIC-20 Sage - Uses distributed system
- ✅ Quantum Shadow People - Uses distributed system
- ✅ Hamsters - Fully migrated to distributed system

---

## See Also
- `../master_websocket_router.py` - The deprecated router that used these handlers
- `../../api/websockets.py` - The new WebSocketManager
- `../../distributed/distributed_agent_manager.py` - Agent initialization
- `/docs/completed-tasks/WEEK5_TASK5.4_COMPLETE.md` - Migration documentation
