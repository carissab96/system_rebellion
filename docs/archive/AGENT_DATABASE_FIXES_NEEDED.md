# Agent Database Write Fixes Needed

## Database Query Results

### Central Memory Bank (All agents writing here)
```
sir_hawkington | 2992 entries
the_stick      | 1322 entries  
vic20_sage     |  669 entries
meth_snail     |   81 entries
```

### Agent-Specific Tables (DUAL-WRITE status)
```
the_stick_memory_bank             | 1224 ✅ WORKING
vic20_memory_bank                 |   45 ✅ WORKING
meth_snail_memory_bank            |    0 ❌ BROKEN
sir_hawkington_memory_bank        |    0 ❌ BROKEN
hamsters_memory_bank              |    0 ❌ BROKEN
quantum_shadow_people_memory_bank |    0 ❌ BROKEN
```

---

## Root Cause Analysis

### ✅ The Stick - WORKING
- **Status:** DUAL-WRITE working correctly
- **Method:** Uses `async for session in self.db_getter()`
- **Calls:** `store_compliance_violation()`, `store_hamster_encounter()`, `store_memory_entry()`
- **Result:** 1,224 rows in agent table

### ✅ VIC-20 - WORKING  
- **Status:** DUAL-WRITE working correctly
- **Method:** Uses `async for session in self.db_getter()`
- **Calls:** `store_coordination_decision()` from coordination logic
- **Result:** 45 rows in agent table

### ❌ Sir Hawkington - BROKEN
- **Status:** Has correct `db_getter` pattern, calls `store_decision()`, but 0 rows
- **Method:** Uses `async for session in self.db_getter()` ✅
- **Calls:** `store_hawkington_decision()` from `triage_engine.py` line 776 ✅
- **Problem:** Method is being called but writes are failing silently OR not committing
- **Fix Needed:** Debug why commits aren't persisting to agent table

### ❌ Meth Snail - BROKEN (Multiple Issues)
- **Status:** Wrong session pattern AND not calling DUAL-WRITE method
- **Method:** Uses `self.session` ❌ (doesn't exist!)
- **Calls:** Only calls `store_optimization_metrics()` (CMB only), NOT `store_optimization_decision()` (DUAL-WRITE)
- **Problems:**
  1. `self.session` doesn't exist - should use `async for session in self.db_getter()`
  2. `decision_engine.py` line 347 calls `store_optimization_metrics()` instead of `store_optimization_decision()`
- **Fix Needed:**
  1. Replace all `self.session` with `async for session in self.db_getter()` pattern
  2. Update `decision_engine.py` to call `store_optimization_decision()` when making decisions

### ❌ Hamsters - BROKEN
- **Status:** Correct session pattern, but NOT calling DUAL-WRITE method
- **Method:** Uses `async with await self.get_session()` ✅
- **Calls:** NO calls to `store_infrastructure_intervention()` found in codebase
- **Problem:** The DUAL-WRITE method exists but is never called
- **Fix Needed:** Add calls to `store_infrastructure_intervention()` in hamster decision logic

### ❌ Quantum Shadow People - BROKEN
- **Status:** Correct session pattern, calls method, but 0 rows
- **Method:** Uses `async with AsyncSession(self.engine)` ✅
- **Calls:** `store_decision()` from `decision_engine.py` line 246 ✅
- **Problem:** Method is being called but writes are failing silently OR not committing
- **Fix Needed:** Debug why commits aren't persisting to agent table

---

## Fix Priority

### Priority 1: Meth Snail (Code is broken)
1. Replace all `self.session` with `async for session in self.db_getter()` 
2. Update `decision_engine.py` to call `store_optimization_decision()`

### Priority 2: Hamsters (Method never called)
1. Find where hamsters make infrastructure decisions
2. Add calls to `store_infrastructure_intervention()`

### Priority 3: Sir Hawkington & QSP (Silent failures)
1. Add debug logging to see if method is reached
2. Check for exceptions being swallowed
3. Verify session commits are working

---

## Next Steps

1. **Fix Meth Snail's `self.session` bug** - Replace with `db_getter` pattern
2. **Update Meth Snail's decision engine** - Call `store_optimization_decision()`
3. **Add Hamster intervention calls** - Wire up `store_infrastructure_intervention()`
4. **Debug Sir Hawkington** - Add logging to see why writes fail
5. **Debug QSP** - Add logging to see why writes fail
6. **Re-run database queries** - Verify all agents writing to both tables
