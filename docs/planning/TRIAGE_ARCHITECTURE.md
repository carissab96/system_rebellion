# Triage Architecture - The Chain of Command

## Overview

The System Rebellion uses a hierarchical triage and coordination system with clear lines of communication.

## The Command Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Sir Hawkington                           │
│                  (Triage Commander)                         │
│  "One does not simply process metrics without aristocratic  │
│   precision and a properly polished monocle"                │
└─────────────────┬───────────────────────┬───────────────────┘
                  │                       │
                  │ Triage Decisions      │ Triage Decisions
                  │                       │
                  ▼                       ▼
         ┌────────────────┐      ┌────────────────┐
         │   The Stick    │      │    VIC-20      │
         │   (Learning)   │◄─────┤ (Coordinator)  │
         └────────────────┘      └────────┬───────┘
                                          │
                      ┌───────────────────┼───────────────────┐
                      │                   │                   │
                      ▼                   ▼                   ▼
              ┌───────────────┐   ┌──────────┐   ┌──────────────┐
              │ Meth Snail    │   │ Hamsters │   │     QSP      │
              │ (Terry)       │   │ (Steve,  │   │  (Network)   │
              │ (Memory)      │   │ Bob,Carl)│   │  (Security)  │
              └───────────────┘   └──────────┘   └──────────────┘
```

## Message Flow

### 1. Sir Hawkington (Triage Commander)
**Responsibilities:**
- Analyze all system metrics
- Make triage decisions (NORMAL, MEDIUM, HIGH, CRITICAL, EMERGENCY)
- Broadcast decisions to The Stick and VIC-20
- Handle Terry's energy drink authorization directly

**Broadcasts To:**
- `the_stick` - All triage decisions for learning
- `vic_20_sage` - Coordination requests (MEDIUM+)
- `meth_snail` - Energy drink authorization (special case)

**Does NOT:**
- Coordinate other agents directly
- Subscribe to triage decisions (he makes them)

### 2. VIC-20 Sage (Coordinator)
**Responsibilities:**
- Receive triage decisions from Hawkington
- Coordinate multi-agent responses
- Assign tasks to specialist agents
- Report results back to The Stick

**Subscribes To:**
- `triage_decision` - From Sir Hawkington

**Broadcasts To:**
- `coordination_request` - To Hamsters, QSP, Meth Snail
- `coordination_update` - To The Stick

**Coordinates:**
- Hamsters (disk issues)
- QSP (network/security issues)
- Meth Snail (memory optimization)

### 3. The Stick (Learning Coordinator)
**Responsibilities:**
- Receive ALL triage decisions for learning
- Receive coordination updates from VIC-20
- Log everything to database
- Track patterns for future learning

**Subscribes To:**
- `triage_decision` - From Sir Hawkington
- `coordination_update` - From VIC-20

**Broadcasts To:**
- Nothing (patient observer and logger)

### 4. Specialist Agents (Hamsters, QSP, Meth Snail)
**Responsibilities:**
- Receive coordination requests from VIC-20
- Execute specialized tasks
- Report results back to VIC-20

**Subscribes To:**
- `coordination_request` - From VIC-20 only

**Does NOT:**
- Subscribe to triage decisions directly
- Communicate with Sir Hawkington (except Terry's energy drinks)

## Message Types

### `triage_decision`
**Sender:** Sir Hawkington  
**Receivers:** The Stick, VIC-20  
**Content:**
```python
{
    'severity': 'high',
    'routing': 'vic20_coordination',
    'target_agents': ['vic_20_sage', 'meth_snail'],
    'reasoning': 'High memory usage detected',
    'metrics_summary': {...},
    'user_id': 'user_123'
}
```

### `coordination_request`
**Sender:** VIC-20  
**Receivers:** Hamsters, QSP, Meth Snail  
**Content:**
```python
{
    'task_type': 'memory_optimization',
    'target_agent': 'meth_snail',
    'priority': 'high',
    'recommendation': 'Clear caches',
    'context': {...}
}
```

### `coordination_update`
**Sender:** VIC-20  
**Receiver:** The Stick  
**Content:**
```python
{
    'coordination_id': 'coord_123',
    'agents_involved': ['meth_snail', 'hamsters'],
    'results': {...},
    'status': 'completed'
}
```

## Routing Logic

### NORMAL Severity
- **Route:** `STICK_DIRECT`
- **Flow:** Hawkington → The Stick → Agent Manager → All Agents
- **Purpose:** Baseline learning and monitoring

### MEDIUM Severity
- **Route:** `VIC20_COORDINATION`
- **Flow:** Hawkington → VIC-20 → Specialist Agents → The Stick
- **Purpose:** Coordinated response to elevated metrics

### HIGH/CRITICAL/EMERGENCY Severity
- **Route:** `VIC20_EMERGENCY`
- **Flow:** Hawkington → VIC-20 (emergency mode) → All Specialists → The Stick
- **Purpose:** Immediate multi-agent response

### CPU Specialist (Special Case)
- **Route:** `CPU_SPECIALIST`
- **Flow:** Hawkington handles directly
- **Purpose:** Sir Hawkington's domain expertise

## Special Cases

### Terry's Energy Drink Authorization
- **Trigger:** Meth Snail requests energy drink
- **Handler:** Sir Hawkington (direct)
- **Reason:** Only the aristocrat can authorize such chaos

### Monocle Yeeting
- **Trigger:** EMERGENCY severity
- **Broadcast:** `SYSTEM_EVENT` to all agents
- **Purpose:** Maximum alarm and personality expression

## Implementation Notes

### Week 3 Task 3.2 Checklist
- [x] The Stick subscribes to `triage_decision`
- [x] VIC-20 subscribes to `triage_decision`
- [ ] Hamsters subscribes to `coordination_request` (from VIC-20)
- [ ] QSP subscribes to `coordination_request` (from VIC-20)
- [ ] Meth Snail subscribes to `coordination_request` (from VIC-20)
- [ ] VIC-20 broadcasts `coordination_request` messages
- [ ] VIC-20 broadcasts `coordination_update` to The Stick

### Files to Modify
1. `backend/app/ai_agents/hamsters/distributed_hamsters.py` - Remove triage handler, add coordination handler
2. `backend/app/ai_agents/quantum_shadow_people/distributed_qsp.py` - Remove triage handler, add coordination handler
3. `backend/app/ai_agents/meth_snail/distributed_meth_snail.py` - Remove triage handler, add coordination handler
4. `backend/app/ai_agents/vic_20_sage/distributed_vic20.py` - Add coordination broadcasting

## Benefits of This Architecture

1. **Clear Hierarchy:** Everyone knows who to listen to
2. **Reduced Message Load:** Specialists don't get spammed with all triage decisions
3. **Centralized Coordination:** VIC-20 handles all multi-agent orchestration
4. **Complete Logging:** The Stick sees everything for learning
5. **Personality Preservation:** Sir Hawkington maintains aristocratic authority

---

**"The chain of command is not merely a suggestion - it's an aristocratic necessity."**  
— Sir Hawkington, probably
