# FRONTEND AUDIT - What to Keep, Update, or Remove

**Date**: November 13, 2025  
**Status**: Auditing existing code before building Consciousness Theater

---

## TYPE DEFINITIONS

### **`src/types/backend-generated.ts`** ✅ KEEP - JUST CREATED
- **Purpose**: Auto-generated from backend dataclasses
- **Contains**: Decision types, enums, agent data structures
- **Status**: Perfect, single source of truth
- **Action**: KEEP, use as primary source

### **`src/types/agents.ts`** ✅ KEEP - DIFFERENT PURPOSE
- **Purpose**: Database memory record types (PostgreSQL schema)
- **Contains**: Agent memory structures, WebSocket message types
- **Status**: Still needed for database records
- **Action**: KEEP, but consider renaming to `agent-memories.ts` for clarity
- **Note**: These are MEMORY RECORDS, not DECISION types

### **`src/types/websocketMessages.ts`** 🔍 REVIEW
- **Purpose**: WebSocket message types
- **Status**: Need to check for overlap with backend-generated
- **Action**: Review and potentially consolidate

### **`src/types/agentIntrospection.ts`** 🔍 REVIEW
- **Purpose**: Agent introspection data
- **Status**: Check if still used
- **Action**: Review usage, keep if active

---

## REDUX SLICES

### **`src/store/slices/sirHawkingtonSlice.ts`** ⚠️ UPDATE NEEDED
- **Current**: Has `monocle_yeet_count` (number)
- **Backend**: Has `monocle_yeeted` (boolean)
- **Action**: Update to use backend-generated types
- **Priority**: HIGH - This is the mismatch we're fixing!

### **Other Agent Slices** ⚠️ UPDATE NEEDED
- Review all agent slices for type mismatches
- Update to use backend-generated types where appropriate
- Keep memory-specific fields separate

---

## COMPONENTS

### **`src/pages/LiveAgentTheaterPage.tsx`** 🤔 DECISION NEEDED
- **Purpose**: Current agent theater view
- **Status**: Works, but not revolutionary
- **Options**:
  1. Keep as "classic view" alongside Consciousness Theater
  2. Replace entirely with Consciousness Theater
  3. Merge best parts into new design
- **Action**: DISCUSS - What do you want to do with this?

### **`src/components/agent-theater/`** 🔍 REVIEW
- **Purpose**: Agent theater components
- **Status**: Some may be reusable
- **Action**: Review each component, keep useful ones

### **`src/pages/dashboard/`** ✅ KEEP
- **Purpose**: Dashboard pages (Memory Banks, System Monitor, etc.)
- **Status**: Working, separate from theater
- **Action**: KEEP, will enhance later

---

## SERVICES

### **`src/services/websocket.ts`** ✅ KEEP
- **Purpose**: WebSocket connection management
- **Status**: Working well
- **Action**: KEEP, already integrated

### **`src/services/api/`** ✅ KEEP
- **Purpose**: API calls
- **Status**: Working
- **Action**: KEEP, may add new endpoints

---

## HOOKS

### **`src/hooks/useWebSocketConnection.ts`** ✅ KEEP
- **Purpose**: WebSocket hook
- **Status**: Working
- **Action**: KEEP

### **`src/hooks/redux.ts`** ✅ KEEP
- **Purpose**: Typed Redux hooks
- **Status**: Essential
- **Action**: KEEP

---

## RECOMMENDATIONS

### **IMMEDIATE ACTIONS:**

1. **Update Redux Slices** ⚠️ HIGH PRIORITY
   - Import from `backend-generated.ts`
   - Fix type mismatches
   - Use proper enums and interfaces

2. **Clarify Type Files** 📝 MEDIUM PRIORITY
   - Rename `agents.ts` → `agent-memories.ts`
   - Add comments explaining the difference
   - Create index file for easy imports

3. **Review WebSocket Types** 🔍 MEDIUM PRIORITY
   - Check for duplicates with backend-generated
   - Consolidate where possible
   - Keep message envelope types

4. **Decide on LiveAgentTheaterPage** 🤔 DISCUSSION NEEDED
   - Keep as fallback?
   - Replace entirely?
   - Merge components?

### **CAN DELETE:**
- Nothing yet - need to review component usage first

### **CAN'T DELETE:**
- `backend-generated.ts` - Just created, essential
- `agent-memories.ts` (agents.ts) - Database schema types
- WebSocket service - Core functionality
- Redux hooks - Essential

---

## NEXT STEPS

1. ✅ **Types generated** - DONE
2. 🔄 **Audit complete** - THIS DOCUMENT
3. ⏭️ **Update Redux slices** - Use new types
4. ⏭️ **Install dependencies** - Three.js, Framer Motion
5. ⏭️ **Build incrementally** - Consciousness Theater

---

## QUESTIONS FOR CARISSA

1. **LiveAgentTheaterPage**: Keep, replace, or merge?
2. **Old components**: Want to review together or trust the audit?
3. **Type organization**: Happy with the plan to rename `agents.ts`?

---

**STATUS**: Audit complete, ready for Step 3 (dependencies) once decisions made.
