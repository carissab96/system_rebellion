# Agent Database Writes - Status Check

## Summary: DUAL-WRITE Architecture

All agents use the **DUAL-WRITE pattern**:
1. Write structured data to their **agent-specific table**
2. Write summary to **`central_memory_bank`** (shared table)
3. Some also write to **learning/pattern tables**

---

## ✅ The Stick

**Status:** CONFIRMED WRITING TO `central_memory_bank`

**Should write to:**
1. ✅ `central_memory_bank` - Universal memory (CONFIRMED)
2. ❓ `the_stick_memory_bank` - Compliance violations, hamster encounters
3. ❓ `user_learning_patterns` - User behavior patterns
4. ❓ `agent_global_patterns` - Cross-user patterns
5. ❓ `agent_learning_interactions` - Cross-agent learning
6. ❓ `agent_memory` - Pinned memories

**Methods that write:**
- `store_memory_entry()` → `central_memory_bank` only
- `store_compliance_violation()` → DUAL-WRITE (both tables)
- `store_hamster_encounter()` → DUAL-WRITE (both tables)
- `store_anxiety_event()` → `central_memory_bank` only
- `store_stick_decision()` → `central_memory_bank` only
- `store_user_pattern()` → `central_memory_bank` + pattern tables

**To verify:** Check if `the_stick_memory_bank` has any rows

---

## ❓ VIC-20 Sage

**Should write to:**
1. ❓ `central_memory_bank` - Universal memory
2. ❓ `vic20_memory_bank` - Coordination decisions
3. ❓ Vector storage (Qdrant)

**Methods that write:**
- `store_coordination_decision()` → DUAL-WRITE + vector embedding

**To verify:** Check both `central_memory_bank` and `vic20_memory_bank` for VIC-20 entries

---

## ❓ Meth Snail (Terry)

**Should write to:**
1. ❓ `central_memory_bank` - Universal memory
2. ❓ `meth_snail_memory_bank` - Optimization decisions, shell spins
3. ❓ `agent_memory` - Pinned high-confidence optimizations

**Methods that write:**
- `store_optimization_decision()` → DUAL-WRITE
- `store_shell_spin_incident()` → DUAL-WRITE

**To verify:** Check both `central_memory_bank` and `meth_snail_memory_bank` for Terry entries

---

## ❓ Sir Hawkington

**Should write to:**
1. ❓ `central_memory_bank` - Universal memory
2. ❓ `sir_hawkington_memory_bank` - Triage decisions
3. ❓ `agent_memory` - Pinned critical decisions

**Methods that write:**
- `store_decision()` → DUAL-WRITE

**To verify:** Check both `central_memory_bank` and `sir_hawkington_memory_bank` for Hawkington entries

---

## ❓ The Hamsters (Steve, Bob, Carl)

**Should write to:**
1. ❓ `central_memory_bank` - Universal memory
2. ❓ `hamsters_memory_bank` - Infrastructure interventions
3. ❓ `agent_memory` - Pinned important interventions

**Methods that write:**
- `store_infrastructure_intervention()` → DUAL-WRITE

**To verify:** Check both `central_memory_bank` and `hamsters_memory_bank` for Hamster entries

---

## ❓ Quantum Shadow People

**Should write to:**
1. ❓ `central_memory_bank` - Universal memory
2. ❓ `quantum_shadow_people_memory_bank` - Quantum decisions
3. ❓ `agent_memory` - Pinned quantum decisions

**Methods that write:**
- `store_decision()` → DUAL-WRITE
- `store_network_metrics()` → `central_memory_bank` only
- `store_user_behavior_observation()` → `central_memory_bank` only

**To verify:** Check both `central_memory_bank` and `quantum_shadow_people_memory_bank` for QSP entries

---

## Next Steps

1. **Query each agent-specific table** to see if they have any rows
2. **Check `central_memory_bank`** for entries from each agent (filter by `agent_name`)
3. **Identify which agents are NOT writing** to their tables
4. **Fix database integration** for agents that aren't writing

### SQL Queries to Run:

```sql
-- Check central memory bank by agent
SELECT agent_name, COUNT(*) as count, MAX(created_at) as last_write
FROM central_memory_bank
GROUP BY agent_name;

-- Check agent-specific tables
SELECT COUNT(*) FROM the_stick_memory_bank;
SELECT COUNT(*) FROM vic20_memory_bank;
SELECT COUNT(*) FROM meth_snail_memory_bank;
SELECT COUNT(*) FROM sir_hawkington_memory_bank;
SELECT COUNT(*) FROM hamsters_memory_bank;
SELECT COUNT(*) FROM quantum_shadow_people_memory_bank;
```
