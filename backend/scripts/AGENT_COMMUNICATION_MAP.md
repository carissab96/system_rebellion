# Agent Communication Map - The Correct Relationships

**Date:** October 20, 2025  
**Purpose:** Define who talks to whom and why

---

## 🎯 CORE PRINCIPLE

**Not all agents communicate with all agents.** Communication follows specific patterns based on roles and capabilities.

---

## 👥 AGENT ROLES & RESPONSIBILITIES

### Sir Hawkington (Triage Commander & Data Quality Enforcer)
**Primary Role:** System-wide triage, CPU monitoring, data quality enforcement  
**Communicates With:**
- **The Stick** - Routes normal operations for eidetic memory storage
- **VIC-20 Sage** - Escalates medium/high severity issues
- **Meth Snail** - Cross-agent coordination for CPU/RAM tandem optimization

**Monitors:**
- Meth Snail's Red Bull consumption (energy oversight)
- Data quality across all metrics
- System stress levels

**Personality Flaw = Safety Feature:**
- Monocle yeeting = Data quality enforcement (won't process bad data)

---

### The Stick (Eidetic Memory & Hypervigilant Monitor)
**Primary Role:** Store ALL patterns, solutions, and learnings. Anxiety-driven anomaly detection.  
**Communicates With:**
- **ALL AGENTS** - Receives and stores their patterns/solutions
- **Hamsters** - Only one who can translate their squeaks (empathetic anxiety)
- **QSP** - Receives network anomaly reports

**Special Abilities:**
- Eidetic memory - NEVER FORGETS anything
- Translates Hamster squeaks (empathetic connection)
- Hypervigilant pattern recognition

**Personality Flaw = Safety Feature:**
- Anxiety = Catches anomalies others miss
- Bob proximity = 3.0x anxiety multiplier (rapid response alert)

---

### Hamsters - Steve, Bob, and Carl (Infrastructure Rapid Response)
**Primary Role:** Physical infrastructure (disk, storage, defrag), emergency 3am fixes  
**Communicates With:**
- **The Stick ONLY** - The Stick translates their squeaks
- **QSP** - Brief interactions (only ones who understand QSP)

**Communication Style:**
- Speak in squeaks only other hamsters understand
- The Stick translates via empathetic anxiety
- Will NOT interact with other agents directly

**Personality Flaw = Safety Feature:**
- Beer consumption = Natural risk assessment gates (won't do risky work sober)
- Bob's chaos = Triggers The Stick's hypervigilance

---

### Meth Snail (RAM Optimization Specialist)
**Primary Role:** Monitor RAM usage, optimize memory performance  
**Communicates With:**
- **Sir Hawkington** - CPU/RAM tandem coordination
- **VIC-20 Sage** - Receives optimization suggestions (has choice to accept/reject)

**Special Relationship:**
- Works WITH Hawkington to ensure CPU(s) and DDR work in tandem
- Red Bull consumption monitored by Hawkington
- Can choose to follow VIC-20's suggestions or create own solutions

**Personality Flaw = Safety Feature:**
- Caffeine limits = Controlled optimization boundaries (jitter prevents over-optimization)

---

### Quantum Shadow People (Network Monitoring Specialists)
**Primary Role:** Phase through routers, monitor network traffic, detect anomalies  
**Communicates With:**
- **The Stick** - Reports network anomalies (packet loss, latency, bytes sent/received)
- **Hamsters** - Brief interactions (only ones who understand QSP)

**Activities:**
- Phase in and out of routers
- Count packets
- Adjust for latency
- Monitor bytes sent/received
- Log when things go awry

**Communication Style:**
- Incomprehensible to everyone except Hamsters
- The Stick receives reports but doesn't fully understand
- VIC-20 asks Hamsters to translate when needed

**Personality Flaw = Safety Feature:**
- Incomprehensibility = Unconventional threat detection (sees patterns others can't)

---

### VIC-20 Sage (Auto-Tuner & Coordinator)
**Primary Role:** Determine which agent handles what, make suggestions (auto-tuner)  
**Communicates With:**
- **ALL AGENTS** - Coordinates system-wide responses
- **Hamsters** - Requests QSP translation when needed

**Decision Making:**
- Determines which agent gets the task
- Makes suggestions about solutions (auto-tuner)
- **Agents have choice** - Can accept VIC-20's recommendation OR create their own solution based on patterns/user habits

**Personality Flaw = Safety Feature:**
- Ancient wisdom = Conflict mediation (prevents agent conflicts)

---

## 🔄 COMMUNICATION FLOWS

### Normal Operations Flow
```
Metrics → Hawkington (Triage) → The Stick (Eidetic Memory Storage)
                              ↓
                         Pattern Stored
```

### Medium Severity Flow
```
Metrics → Hawkington (Triage) → VIC-20 (Coordination)
                              ↓
                    VIC-20 suggests to Meth Snail
                              ↓
                    Meth Snail chooses solution
                              ↓
                    Result → The Stick (Memory)
```

### Emergency Flow
```
Metrics → Hawkington (Monocle Yeet) → VIC-20 (Emergency Coordination)
                                    ↓
                        Multi-agent orchestration
                                    ↓
                        All results → The Stick (Memory)
```

### CPU/RAM Tandem Optimization
```
Hawkington (CPU monitoring) ↔ Meth Snail (RAM monitoring)
            ↓                           ↓
    Cross-agent coordination for optimal performance
            ↓
    Result → The Stick (Memory)
```

### Network Anomaly Flow
```
QSP (phases through routers) → Detects anomaly
                              ↓
                    Reports to The Stick
                              ↓
                    The Stick stores pattern
                              ↓
            If severe → Hawkington → VIC-20
```

### Infrastructure Emergency Flow
```
Disk issue detected → Hawkington → VIC-20
                                  ↓
                    VIC-20 → Hamsters (squeak squeak)
                                  ↓
                    The Stick translates
                                  ↓
                    Hamsters drink beer → Fix infrastructure
                                  ↓
                    Result → The Stick (Memory)
```

### QSP Translation Flow
```
QSP doing incomprehensible things
            ↓
VIC-20 needs to know what's happening
            ↓
VIC-20 → Hamsters: "What are they saying?"
            ↓
Hamsters translate (only ones who understand)
            ↓
Hamsters → The Stick (via squeaks)
            ↓
The Stick → VIC-20 (translated)
```

---

## 🚫 WHO DOES NOT TALK TO WHOM

### Hamsters DO NOT talk to:
- ❌ Sir Hawkington directly
- ❌ Meth Snail directly
- ❌ VIC-20 directly (VIC-20 talks TO them, they respond via The Stick)
- ✅ ONLY The Stick understands their squeaks

### QSP DO NOT talk to:
- ❌ Anyone except The Stick and Hamsters
- ❌ Incomprehensible to all other agents

### Meth Snail DOES NOT:
- ❌ Receive Red Bull FROM Hamsters
- ✅ Red Bull consumption MONITORED by Hawkington
- ✅ Coordinates WITH Hawkington (not receives from)

---

## 💡 KEY INSIGHTS FOR WEBSOCKET EVENTS

### Agent Events to Broadcast:
1. **Sir Hawkington**
   - Monocle yeets (data quality enforcement)
   - Red Bull monitoring decisions

2. **The Stick**
   - Paper bag consumption (anxiety management)
   - Anxiety spikes (especially Bob proximity)
   - Pattern storage (eidetic memory)
   - Hamster squeak translations

3. **Hamsters**
   - Beer consumption (risk assessment)
   - Duct tape usage (infrastructure fixes)
   - Supply closet raids (usually Bob)
   - Infrastructure interventions

4. **Meth Snail**
   - Shell spinning (jitter management)
   - Red Bull consumption (energy boost)
   - Optimization decisions (accept/reject VIC-20 suggestions)

5. **QSP**
   - Dimensional shifts (phase in/out of routers)
   - Network anomaly detection
   - Tequila jello shot consumption

6. **VIC-20**
   - Coordination decisions
   - Auto-tuner suggestions
   - Wisdom dispensing

### Agent Insights to Broadcast:
1. **Hawkington → The Stick**
   - "Store this pattern in eidetic memory"
   - Normal operations routing

2. **Hawkington ↔ Meth Snail**
   - CPU/RAM tandem coordination
   - "Let's optimize this together"

3. **Hawkington → VIC-20**
   - Medium severity: "Need coordination"
   - Emergency: "MONOCLE YEETED - EMERGENCY!"

4. **VIC-20 → Agents**
   - "I suggest this approach" (agent has choice)
   - "Handle this task"

5. **VIC-20 → Hamsters**
   - "What are the QSP saying?"
   - "Fix this infrastructure issue"

6. **QSP → The Stick**
   - "Network anomaly detected: packet loss 15%"
   - "Latency spike on router X"

7. **Hamsters → The Stick** (via squeaks)
   - "Infrastructure fixed"
   - "QSP says: [translation]"

---

## 🎬 IMPLEMENTATION PRIORITIES

### Already Implemented ✅
- Agent event broadcasting (personality moments)
- Hawkington routing insights
- Method instrumentation disabled

### Next Steps
1. **CPU/RAM Tandem Coordination** (Hawkington ↔ Meth Snail)
2. **The Stick Eidetic Memory** (pattern storage broadcasts)
3. **QSP Network Anomaly Reports** (QSP → The Stick)
4. **VIC-20 Auto-Tuner Suggestions** (with agent choice tracking)
5. **Hamster Squeak Translations** (via The Stick)

---

**This is the correct agent communication architecture. Safety through personality.** ✨
