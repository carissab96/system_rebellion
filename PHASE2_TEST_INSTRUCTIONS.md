# Phase 2 Test Instructions
**Testing Sir Hawkington as Sole System Monitor**

---

## 🎯 What We're Testing

Phase 2 transformed Sir Hawkington into the sole system monitor with proper triage logic. We need to verify:

1. ✅ **Hawk has ResourceMonitor enabled** (only agent that does)
2. ✅ **Other agents have NO ResourceMonitor** (Terry, Hamsters, QSP, VIC-20, Stick)
3. ✅ **Hawk monitors ALL resources** (CPU, Memory, Disk, Network, Swap)
4. ✅ **Triage methods exist** (_assess_confidence, _should_escalate_to_vic20, etc.)
5. ✅ **Triage logic works** (assesses, escalates, routes to VIC-20, CCs The Stick)

---

## 🧪 Test Method 1: Automated Test Script

### Run on Dell Server:

```bash
cd /home/carissa/Documents/system_rebellion

# Activate venv
source venv/bin/activate

# Run test script
python test_phase2_hawk_triage.py
```

### Expected Output:

```
🧪 PHASE 2 TEST: Sir Hawkington Triage Logic
================================================================================

✅ VERIFICATION 1: Check ResourceMonitor Status
--------------------------------------------------------------------------------
✅ sir_hawkington: HAS ResourceMonitor (CORRECT - sole system monitor)
   Monitoring: [ResourceType.CPU, ResourceType.MEMORY, ResourceType.DISK, ResourceType.NETWORK, ResourceType.SWAP]
✅ meth_snail: NO ResourceMonitor (CORRECT - receives from hierarchy)
✅ hamsters: NO ResourceMonitor (CORRECT - receives from hierarchy)
✅ quantum_shadow_people: NO ResourceMonitor (CORRECT - receives from hierarchy)
✅ vic_20_sage: NO ResourceMonitor (CORRECT - receives from hierarchy)
✅ the_stick: NO ResourceMonitor (CORRECT - receives from hierarchy)

✅ VERIFICATION 2: Check Triage Methods
--------------------------------------------------------------------------------
✅ Sir Hawkington has method: _assess_confidence
✅ Sir Hawkington has method: _should_escalate_to_vic20
✅ Sir Hawkington has method: _send_triage_alert_to_vic20
✅ Sir Hawkington has method: _cc_the_stick

✅ VERIFICATION 3: Test Triage Logic
--------------------------------------------------------------------------------
   72% (threshold 70%): confidence=0.60, escalate=False
   80% (threshold 70%): confidence=0.80, escalate=True
   95% (threshold 70%): confidence=1.00, escalate=True

✅ VERIFICATION 4: Monitor for 30 seconds
--------------------------------------------------------------------------------
Watching for resource alerts and triage decisions...
```

---

## 🧪 Test Method 2: Backend Logs

### Start backend with logging:

```bash
cd /home/carissa/Documents/system_rebellion

# Run with logging
./run_with_logging.sh
```

### Watch for these log patterns:

#### 1. Initialization (should see):
```
🎯 Sir Hawkington will handle all system monitoring and triage
🧐 Sir Hawkington's distributed consciousness initialized
📊 Resource monitoring enabled for sir_hawkington
🎯 No resource monitoring for meth_snail (receives from hierarchy)
🎯 No resource monitoring for hamsters (receives from hierarchy)
🎯 No resource monitoring for quantum_shadow_people (receives from hierarchy)
🎯 No resource monitoring for vic_20_sage (receives from hierarchy)
🎯 No resource monitoring for the_stick (receives from hierarchy)
```

#### 2. When resource threshold exceeded:
```
🧐⚠️ Sir Hawkington observes elevated CPU usage: 75.2% (threshold: 70.0%) - Severity: high
🧐🎯 Triage assessment: severity=high, confidence=0.80, escalate_to_vic20=True
🧐📨 Triage alert sent to VIC-20: cpu at 75.2% (severity=high, confidence=0.80)
🧐📋 Decision logged to The Stick: triage_decision
```

#### 3. What you should NOT see:
```
❌ "📊 Resource monitoring enabled for meth_snail"
❌ "📊 Resource monitoring enabled for hamsters"
❌ "📊 Resource monitoring enabled for quantum_shadow_people"
❌ "📊 Resource monitoring enabled for vic_20_sage"
❌ "📊 Resource monitoring enabled for the_stick"
```

---

## 🧪 Test Method 3: Trigger High CPU

If you want to force an alert to test triage logic:

```bash
# In another terminal, run CPU stress
stress-ng --cpu 4 --timeout 60s
```

Then watch backend logs for Hawk's triage response.

---

## ✅ Success Criteria

Phase 2 is successful if:

1. ✅ **Only Hawk has ResourceMonitor** - All other agents show "No resource monitoring"
2. ✅ **Hawk monitors all 5 resources** - CPU, Memory, Disk, Network, Swap
3. ✅ **Triage methods exist** - All 4 helper methods present
4. ✅ **Triage logic executes** - Confidence assessed, escalation determined
5. ✅ **Messages sent** - Triage alerts to VIC-20, decision logs to The Stick

---

## ❌ Failure Scenarios

If you see these, Phase 2 has issues:

1. ❌ **Other agents have ResourceMonitor** - They shouldn't be monitoring
2. ❌ **Hawk has NO ResourceMonitor** - He must be the sole monitor
3. ❌ **Missing triage methods** - Helper methods not implemented
4. ❌ **No triage messages** - Routing to VIC-20 not working
5. ❌ **No Stick CCs** - Pattern learning not receiving data

---

## 🐛 Debugging

### If Hawk has no ResourceMonitor:

Check `distributed_hawkington.py` line ~130:
```python
await super().initialize_distributed(
    redis_client,
    enable_resource_monitoring=True,  # Must be True
    resource_check_interval=5
)
```

### If other agents still have ResourceMonitor:

Check `distributed_agent.py` line ~57:
```python
enable_resource_monitor: bool = False,  # Must default to False
```

### If no triage messages appear:

1. Check Redis is running: `redis-cli ping`
2. Check Hawk's thresholds are set correctly
3. Verify resource usage actually exceeds thresholds
4. Check logs for errors in `_handle_resource_alert`

---

## 📊 Next Steps After Testing

Once Phase 2 passes:
- **Phase 3**: Implement VIC-20 routing logic to specialists
- **Phase 4**: Update specialists to receive from VIC-20 only
- **Phase 5**: Implement The Stick as universal logger
- **Phase 6**: Test complete flow end-to-end

---

**The hierarchy begins with Hawk. Let's verify he's ready!** 🧐🎯
