# Frontend/Backend Mismatch Analysis - Dec 27, 2025

## CRITICAL FINDING: Frontend Built on Assumptions, Not Truth

The frontend components built today are looking for **WRONG FIELD NAMES** that don't match what the backend actually emits.

---

## THE BACKEND TRUTH (What Actually Gets Emitted)

### Emission Location
- **Function:** `/backend/app/services/agent_decision_emitter.py` - `emit_agent_decision()`
- **Message Type:** `"agent_decision"`
- **Structure:**
```json
{
  "type": "agent_decision",
  "agent_name": "meth_snail",
  "decision_id": "12345",
  "timestamp": "ISO-8601",
  "perception": { /* agent-specific + personality data */ },
  "reasoning": { /* ML reasoning */ },
  "action_selection": { /* chosen action */ },
  "execution": { /* results */ },
  "learning": { /* storage info */ }
}
```

### Actual Personality Field Names (Backend Reality)

**Terry (meth_snail):**
```json
"perception": {
  "energy_drink_system": {
    "energy_drinks_today": 0,
    "total_energy_drinks": 0,
    "hawk_vetoes": 0,
    "last_drink_time": null
  }
}
```

**The Stick:**
```json
"perception": {
  "paper_bag_economy": {
    "bags_remaining": 100,
    "bags_consumed_today": 0,
    "bags_consumed_total": 0,
    "last_consumption_time": null,
    "anxiety_reduction_per_bag": 20.0
  }
}
```

**Hamsters:**
```json
"perception": {
  "beer_consumption": {
    "steve_beers_today": 2,
    "bob_beers_today": 4,
    "carl_beers_today": 3,
    "total_beers_today": 9
  },
  "duct_tape_assessment": {
    "regular_rolls": 5.0,
    "premium_rolls": 2.0,
    "quantum_rolls": 0.5,
    "total_rolls": 7.5,
    "job_complexity": "moderate"
  },
  "supply_closet": {
    "bob_at_cupboard": false,
    "stick_panic_level": 0.0,
    "items_acquired": [],
    "time_of_raid": null
  }
}
```

**QSP:**
```json
"perception": {
  "tequila_system": {
    "shots_today": 0,
    "paranoia_level": "healthy",
    "threats_detected": 0,
    "false_alarms": 0
  }
}
```

**Sir Hawkington:**
```json
"perception": {
  "monocle_yeets": 0,
  "data_quality_score": 1.0
}
```

**VIC-20:**
```json
"perception": {
  "coordination": {
    "escalations_handled_today": 5,
    "routing_accuracy": 0.92,
    "current_system_drama": "low",
    "routing_breakdown": { "terry": 12, "hamsters": 8, "qsp": 3, "stick": 0 }
  },
  "mediation": {
    "interventions_today": 0,
    "last_intervention": null,
    "hawk_terry_disputes": 0,
    "bob_stick_disputes": 0
  }
}
```

---

## THE FRONTEND LIES (What Components Are Looking For)

### File: `DistributedAgentDashboard.tsx` (lines 399-527)
Component: `AgentPersonalityStats`

**Sir Hawkington - WRONG:**
```tsx
agent.monocle_yeet_count  // ❌ DOESN'T EXIST
agent.monocle_state       // ❌ DOESN'T EXIST
```
**Backend Reality:**
```
perception.monocle_yeets  // ✅ ACTUAL FIELD
```

**Terry - WRONG:**
```tsx
agent.shell_spin_count           // ❌ DOESN'T EXIST
agent.energy_drinks_consumed     // ❌ DOESN'T EXIST
agent.current_jitter_level       // ❌ DOESN'T EXIST
```
**Backend Reality:**
```
perception.energy_drink_system.energy_drinks_today  // ✅ ACTUAL FIELD
perception.energy_drink_system.total_energy_drinks  // ✅ ACTUAL FIELD
perception.shell_spin_incidents (array)             // ✅ ACTUAL FIELD
```

**Hamsters - WRONG:**
```tsx
agent.bob_wild_ideas              // ❌ DOESN'T EXIST
agent.bob_hold_my_beer_count      // ❌ DOESN'T EXIST
agent.collective_beer_level       // ❌ DOESN'T EXIST
agent.duct_tape_inventory         // ❌ WRONG STRUCTURE
```
**Backend Reality:**
```
perception.beer_consumption.bob_beers_today         // ✅ ACTUAL FIELD
perception.duct_tape_assessment.regular_rolls       // ✅ ACTUAL FIELD
perception.duct_tape_assessment.total_rolls         // ✅ ACTUAL FIELD
```

**The Stick - WRONG:**
```tsx
agent.paper_bag_inventory    // ❌ WRONG NAME
agent.paper_bags_consumed    // ❌ WRONG NAME
```
**Backend Reality:**
```
perception.paper_bag_economy.bags_remaining         // ✅ ACTUAL FIELD
perception.paper_bag_economy.bags_consumed_today    // ✅ ACTUAL FIELD
```

**QSP - WRONG:**
```tsx
agent.tequila_jello_shots    // ❌ WRONG NAME
agent.paranoia_level         // ❌ WRONG LOCATION
agent.threats_detected       // ❌ WRONG LOCATION
agent.false_alarms           // ❌ WRONG LOCATION
```
**Backend Reality:**
```
perception.tequila_system.shots_today         // ✅ ACTUAL FIELD
perception.tequila_system.paranoia_level      // ✅ ACTUAL FIELD
perception.tequila_system.threats_detected    // ✅ ACTUAL FIELD
```

---

## THE GOOD NEWS

### File: `PersonalityBehaviors.tsx` - MOSTLY CORRECT ✅

This component actually looks in the right places:
- ✅ `perception.energy_drink_system`
- ✅ `perception.paper_bag_economy`
- ✅ `perception.beer_consumption`
- ✅ `perception.tequila_system`
- ✅ `perception.coordination` / `perception.mediation`

**Minor issues:**
- Uses emojis (violates Carissa Constitution - should use SVG icons)
- Looks for `shell_spin_incidents` array but doesn't count it properly

---

## THE REDUX ISSUE

### File: `agentsSlice.ts` (lines 110-127)

The Redux slice does this:
```tsx
agent.display_data = {
  ...(agent.display_data || {}),
  agent_name,
  status: memory.status || ...,
  last_activity: memory.timestamp || ...,
  summary_stats: { ... },
  ...memory  // ⚠️ SPREADS ENTIRE MEMORY OBJECT
};
```

**Problem:** This spreads the entire `memory` object (which contains `perception`, `reasoning`, etc.) directly onto `display_data`. This means:
- `display_data.perception` exists ✅
- `display_data.energy_drink_system` does NOT exist ❌
- Components need to access `display_data.perception.energy_drink_system`

But `AgentPersonalityStats` is looking for flat fields on `agent` object:
```tsx
agent.monocle_yeet_count  // ❌ Should be agent.perception.monocle_yeets
```

---

## THE WEBSOCKET HANDLER - CORRECT ✅

### File: `useWebSocketConnection.ts` (lines 277-316)

This part is actually RIGHT:
```tsx
dispatch(addAgentMemory({
  agent_name: payload.agent_name,
  memory: {
    decision_id: payload.decision_id,
    timestamp: payload.timestamp,
    perception: payload.perception,      // ✅ Preserves structure
    reasoning: payload.reasoning,        // ✅ Preserves structure
    action_selection: payload.action_selection,
    execution: payload.execution,
    learning: payload.learning,
    ml_decision: true
  }
}));
```

This correctly preserves the nested structure from backend.

---

## ROOT CAUSE ANALYSIS

**Future Cascade built components based on ASSUMPTIONS about field names instead of:**
1. Reading the backend emission code
2. Reading PERSONALITY_PAYLOAD_AUDIT.md
3. Checking what the backend actually sends

**The Carissa Constitution violation:**
> "Backend is ALWAYS source of truth"
> "Frontend ALWAYS adapts to match backend"
> "If backend emits `paper_bags_consumed`, frontend uses `paper_bags_consumed` - NOT `bagCount`"

---

## WHAT NEEDS TO BE FIXED

### 1. Delete `AgentPersonalityStats` Component
**File:** `DistributedAgentDashboard.tsx` (lines 399-543)

This entire component is built on wrong assumptions. It should be deleted.

### 2. Fix `PersonalityBehaviors.tsx`
- ✅ Already looking in correct places (perception.*)
- ❌ Remove emojis, use SVG icons from design system
- ❌ Fix shell spin counting

### 3. Keep Using `PersonalityBehaviors` Component
**File:** `DistributedAgentDashboard.tsx` (line 370-374)

This is already correct:
```tsx
<PersonalityBehaviors 
  agentName={agent.agent_name}
  perception={agentData.perception}  // ✅ Passes perception correctly
  agentData={agentData}
/>
```

### 4. Update Type Definitions (Optional)
The TypeScript types in `agents.ts` are for the OLD memory structure, not the new ML v2 decision chain structure. These could be updated but aren't critical since we're using `any` in most places.

---

## THE PRINCIPLE VIOLATED

**"Truth or graceful failure"**

Future Cascade chose to build based on what he THOUGHT the fields should be named, rather than what they ACTUALLY are.

This is exactly the kind of "looks like it works until someone checks" behavior the Carissa Constitution was written to prevent.

---

## RECOMMENDATION

1. **Delete** `AgentPersonalityStats` component entirely
2. **Keep** `PersonalityBehaviors` component (it's mostly correct)
3. **Fix** emojis in `PersonalityBehaviors` (use SVG icons)
4. **Verify** all field names match PERSONALITY_PAYLOAD_AUDIT.md
5. **Test** with real WebSocket data from Dell server

The good news: The WebSocket handler and Redux are working correctly. The data IS flowing through. The display components just need to look in the right places.
