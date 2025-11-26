# Legacy System Audit - Week 5 Task 5.4
**Date**: November 26, 2025  
**Purpose**: Identify all legacy files that can be deprecated after distributed system migration

---

## ✅ Already Deprecated (Moved to legacy/)

### `agents_config.yaml`
- **Status**: DEPRECATED - Moved to `legacy/agents_config.yaml`
- **Was used by**: `AIAgentManager` (also deprecated)
- **Replaced by**: Direct initialization in `DistributedAgentManager`

---

## 🔴 Should Be Deprecated (Used Only by Legacy AIAgentManager)

### `agent_manager.py`
- **Status**: DEPRECATED - No longer used in `main.py`
- **Purpose**: Legacy YAML-based agent loading system
- **Used by**: Nothing (removed from main.py in Task 5.4)
- **Imports that can also be deprecated**:
  - `MasterAgentDatabase` (only used here)
- **Action**: Move to `legacy/agent_manager.py`

### `master_agent_database.py`
- **Status**: DEPRECATED - Only used by `agent_manager.py`
- **Purpose**: Centralized database integration for dual-write pattern
- **Used by**: Only `agent_manager.py` (which is deprecated)
- **Replaced by**: Each distributed agent has its own `AgentStateManager`
- **Action**: Move to `legacy/master_agent_database.py`

### `master_websocket_router.py`
- **Status**: DEPRECATED - Old WebSocket routing system
- **Purpose**: Legacy WebSocket message routing
- **Used by**: Only test files
- **Replaced by**: `app/api/websockets.py` (WebSocketManager)
- **Action**: Move to `legacy/master_websocket_router.py`

---

## 🟡 Utility Files (Keep - Still Useful)

### `base_agent.py`
- **Status**: KEEP - Base class for all agents
- **Purpose**: Common agent interface
- **Used by**: All distributed agent implementations inherit from this
- **Note**: Distributed agents use this + add distributed features

### `constants.py`
- **Status**: KEEP - Shared constants
- **Purpose**: Common constants across agents
- **Used by**: Multiple agent files

### `permissions.py`
- **Status**: KEEP - Agent permissions system
- **Purpose**: Permission management for agents
- **Used by**: Various agent operations

---

## 🟢 Development/Testing Files (Keep - Not Production)

### `agent_instrumentation.py`
- **Status**: KEEP - Development tool
- **Used by**: Test files only
- **Purpose**: Agent testing and debugging

### `agent_interactions.py`
- **Status**: KEEP - Development tool
- **Used by**: Test files only
- **Purpose**: Testing agent social dynamics

### `agent_introspection.py`
- **Status**: KEEP - Development tool
- **Used by**: Test files only
- **Purpose**: Agent analysis and introspection

### `agent_learning.py`
- **Status**: KEEP - Development tool
- **Used by**: Test files only
- **Purpose**: Learning system testing

---

## 📊 Summary

### Files to Move to legacy/
1. ✅ `agents_config.yaml` (already moved)
2. 🔴 `agent_manager.py` (deprecated, should move)
3. 🔴 `master_agent_database.py` (deprecated, should move)
4. 🔴 `master_websocket_router.py` (deprecated, should move)

### Files to Keep
- ✅ `base_agent.py` - Used by distributed agents
- ✅ `constants.py` - Shared constants
- ✅ `permissions.py` - Active permission system
- ✅ `agent_instrumentation.py` - Dev/test tool
- ✅ `agent_interactions.py` - Dev/test tool
- ✅ `agent_introspection.py` - Dev/test tool
- ✅ `agent_learning.py` - Dev/test tool

---

## 🎯 Recommended Actions

### Immediate (Part of Task 5.4)
```bash
# Move deprecated files to legacy/
git mv app/ai_agents/agent_manager.py app/ai_agents/legacy/agent_manager.py
git mv app/ai_agents/master_agent_database.py app/ai_agents/legacy/master_agent_database.py
git mv app/ai_agents/master_websocket_router.py app/ai_agents/legacy/master_websocket_router.py
```

### Update legacy/README.md
Add documentation for newly moved files explaining why they were deprecated.

---

## 🔍 Verification

After moving files, verify:
- [ ] Backend starts without errors
- [ ] All 6 distributed agents initialize
- [ ] No imports of deprecated files in production code
- [ ] Tests still pass (or update test imports to legacy/)
- [ ] WebSocket bridge works
- [ ] Agent status endpoints work

---

## 📝 Notes

**Why These Files Are Safe to Deprecate:**

1. **`agent_manager.py`** - Replaced by `DistributedAgentManager`
2. **`master_agent_database.py`** - Replaced by individual `AgentStateManager` per agent
3. **`master_websocket_router.py`** - Replaced by `WebSocketManager` in `app/api/websockets.py`

All functionality has been migrated to the distributed system with better architecture:
- State persistence via Redis (not just database)
- Individual agent state managers (not centralized)
- Modern WebSocket handling (not legacy router)
- Direct initialization (not YAML-based)

**The distributed system is the complete replacement, not a complement.**
