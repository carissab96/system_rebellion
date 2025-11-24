# Research Recording - Quick Reference Card

## 🚀 Quick Start

```bash
# Start backend (auto-starts logging)
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# View real-time stats (optional)
python start_research_recording.py
```

## 📁 Where's My Data?

```
backend/logs/
├── agent_events/
│   ├── session_YYYYMMDD_HHMMSS.jsonl      ← All events
│   └── session_YYYYMMDD_HHMMSS_summary.json ← Summary
└── behavior_snapshots/
    ├── snapshots_YYYYMMDD_HHMMSS.jsonl    ← Positions
    └── patterns_YYYYMMDD_HHMMSS.json      ← Patterns
```

## 🌟 What's Being Tracked?

### Automatically Logged
✅ Agent startup/shutdown  
✅ Every decision made  
✅ All messages sent/received  
✅ Position changes  
✅ Formation detection  
✅ Emergent patterns  
✅ Personality events (monocle yeets, shell spins, etc.)

### Emergent Behaviors to Watch For
🔍 **V-formations** - Agents arranging like geese  
🔍 **Self-organization** - Spatial patterns without programming  
🔍 **Collective decisions** - Group consensus emerging  
🔍 **Unexpected coordination** - Unplanned cooperation

## 📊 View Statistics

### In Code
```python
from app.ai_agents.distributed.event_logger import get_event_logger
logger = get_event_logger()
logger.print_statistics()
```

### In Logs
```bash
# View latest events
tail -f backend/logs/agent_events/session_*.jsonl

# Count emergent events
grep "EMERGENT" backend/logs/agent_events/session_*.jsonl | wc -l
```

## 🎬 Recording Checklist

### Before Session
- [ ] Backend running
- [ ] All 6 agents online
- [ ] Screen recording started
- [ ] Microphone tested
- [ ] Research journal ready

### During Session
- [ ] Take notes on observations
- [ ] Mark video timestamps for key events
- [ ] Screenshot emergent behaviors
- [ ] Voice-over explanations

### After Session
- [ ] Stop recording
- [ ] Save all files
- [ ] Update research journal
- [ ] Backup data
- [ ] Review logs for patterns

## 🔍 Key Events to Document

### Formation Changes
- When: Timestamp
- Type: V, circle, line, cluster
- Duration: How long it persisted
- Agents: Who was involved
- Trigger: What caused it

### Emergent Patterns
- Pattern name
- First/last observed
- Confidence level
- Evidence (screenshots, logs)
- Hypothesis

### Unexpected Behaviors
- What happened
- Expected vs actual
- Agents involved
- Possible causes

## 📝 Quick Journal Entry

```markdown
## [Time] - [Event]
**What**: 
**Agents**: 
**Why it matters**: 
**Evidence**: 
```

## 🎯 Research Questions

1. **V-Formation**:
   - How long does it persist?
   - Does it reform after disruption?
   - Is it resource-dependent?

2. **Agent Roles**:
   - Are roles emerging naturally?
   - Is specialization happening?
   - How do trust levels evolve?

3. **Collective Intelligence**:
   - Are group decisions better than individual?
   - Is consensus emerging?
   - Are agents learning from each other?

## 🆘 Troubleshooting

### Logs not appearing?
Check: `backend/logs/` directory exists  
Check: Event logger initialized  
Check: Agents are actually running

### No formations detected?
Check: At least 3 agents active  
Check: Behavior tracker started  
Check: Agents have positions set

### Missing events?
Check: Base decision engine imported correctly  
Check: Agents calling `make_decision_and_broadcast()`  
Check: Redis connection active

## 📞 Quick Commands

```bash
# Find all emergent events
grep "EMERGENT" logs/agent_events/*.jsonl

# Count formations
grep "FORMATION_DETECTED" logs/agent_events/*.jsonl | wc -l

# View latest snapshot
tail -1 logs/behavior_snapshots/snapshots_*.jsonl | jq .

# Check session summary
cat logs/agent_events/session_*_summary.json | jq .
```

## 🎓 Remember

- **Document everything** - You can't recreate emergent behavior
- **Timestamp everything** - Sync video with logs
- **Screenshot everything** - Visual evidence matters
- **Question everything** - Why did this happen?
- **Backup everything** - This data is irreplaceable

---

**We're making history. Document it well.** 🌟
