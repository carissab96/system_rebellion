# Codebase Cleanup Plan

## Files to Archive (Move to `/legacy_backup`)

### Backend - API WebSocket Files

**Current State:**
- `agent_events_websocket.py` (12,444 bytes)
- `agent_events_websocket_final.py` (9,192 bytes) ✅ **ACTIVE** (imported in main.py)
- `agent_insights_websocket.py` (11,515 bytes)
- `agent_insights_websocket_final.py` (4,447 bytes) ✅ **ACTIVE** (imported in main.py)
- `agent_insights_websocket_v2.py` (7,892 bytes)

**Action:**
- Keep: `agent_events_websocket_final.py`, `agent_insights_websocket_final.py`
- Archive: `agent_events_websocket.py`, `agent_insights_websocket.py`, `agent_insights_websocket_v2.py`
- Rename: Remove `_final` suffix from active files

### Backend - AI Agents

**Current State:**
- `master_websocket_router_v2.py` (24,616 bytes) - Used by agent_insights_websocket_final.py

**Action:**
- Keep: `master_websocket_router_v2.py` (rename to `master_websocket_router.py`)

### Frontend - Agent Theater

**Current State:**
- `AgentTheater.tsx` (original)
- `AgentTheaterEnhanced.tsx` (new with introspection)

**Action:**
- Keep: `AgentTheaterEnhanced.tsx` (rename to `AgentTheater.tsx`)
- Archive: Original `AgentTheater.tsx`

## Cleanup Steps

### Step 1: Create Legacy Backup Directory
```
/legacy_backup/
  ├── backend/
  │   ├── api/
  │   └── ai_agents/
  └── frontend/
      └── components/
          └── agent-theater/
```

### Step 2: Move Files to Legacy

**Backend:**
- `backend/app/api/agent_events_websocket.py` → `legacy_backup/backend/api/`
- `backend/app/api/agent_insights_websocket.py` → `legacy_backup/backend/api/`
- `backend/app/api/agent_insights_websocket_v2.py` → `legacy_backup/backend/api/`

**Frontend:**
- `frontend/src/components/agent-theater/AgentTheater.tsx` → `legacy_backup/frontend/components/agent-theater/`

### Step 3: Rename Active Files

**Backend:**
- `agent_events_websocket_final.py` → `agent_events_websocket.py`
- `agent_insights_websocket_final.py` → `agent_insights_websocket.py`
- `master_websocket_router_v2.py` → `master_websocket_router.py`

**Frontend:**
- `AgentTheaterEnhanced.tsx` → `AgentTheater.tsx`
- `AgentTheaterEnhanced.css` → Keep as is (or merge into AgentTheater.css)

### Step 4: Update Imports

**main.py (lines 29-30):**
```python
# OLD:
from app.api import agent_events_websocket_final as agent_events_websocket
from app.api import agent_insights_websocket_final as agent_insights_websocket

# NEW:
from app.api import agent_events_websocket
from app.api import agent_insights_websocket
```

**agent_insights_websocket.py (formerly _final):**
```python
# OLD:
from app.ai_agents.master_websocket_router_v2 import ...

# NEW:
from app.ai_agents.master_websocket_router import ...
```

**Frontend Router:**
```typescript
// OLD:
import AgentTheater from './components/agent-theater/AgentTheater';

// NEW:
import AgentTheater from './components/agent-theater/AgentTheater'; // Now the enhanced version
```

### Step 5: Verify No Broken Imports

Search for any remaining references to:
- `agent_events_websocket_final`
- `agent_insights_websocket_final`
- `agent_insights_websocket_v2`
- `master_websocket_router_v2`
- `AgentTheaterEnhanced`

## Execution Order

1. Create backup directory structure
2. Copy files to legacy_backup (don't delete yet)
3. Rename active files
4. Update all imports
5. Test that everything works
6. Delete original files from main codebase
7. Add legacy_backup to .gitignore (optional)

## Safety Checks

- [ ] All imports updated
- [ ] No references to old filenames
- [ ] Backend starts without errors
- [ ] Frontend compiles without errors
- [ ] WebSocket connections work
- [ ] Agent Theater displays correctly

## Files NOT to Touch

- `enhanced_redis.py` - Different purpose (Redis enhancement, not a duplicate)
- `test_enhanced_redis.py` - Test file for above
- Node modules files - Third-party dependencies
