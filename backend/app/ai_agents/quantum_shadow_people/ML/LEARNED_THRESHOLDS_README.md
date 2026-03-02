# QSP's Learned Thresholds System

## Overview

QSP's learned threshold system adapts security threat detection thresholds based on observed outcomes. Instead of using hardcoded values for when to escalate threats, the system learns from experience.

**CRITICAL DISTINCTION:** False positives (escalated non-threats) and false negatives (missed threats) are tracked separately due to asymmetric costs in the security domain. Missed threats are catastrophic; false alarms are merely annoying.

## Components

### 1. LearnedThresholds (`learned_thresholds.py`)

Manages adaptive thresholds for security metrics:
- **Failed auth attempts** (warning: 5, critical: 15 default) - count-based
- **Network anomalies** (warning: 3, critical: 10 default) - count-based
- **Threat severity** (low: 0.3, medium: 0.6, high: 0.8, critical: 0.95 default) - confidence-based categorical boundaries

**Learning Logic:**
- **False positives** (escalated non-threats) → raise threshold (less sensitive)
- **False negatives** (missed real threats) → lower threshold (more sensitive) **URGENTLY**
- **Successful detections** → reinforce current threshold

**Asymmetric Weighting:**
False negatives receive 2x weight in threshold adjustment calculations. Missing a real threat is catastrophic; escalating a non-threat is recoverable.

### 2. ActionEffectivenessModel (`action_effectiveness.py`)

Learns which security response works best for which threat pattern:
- `block_ip` vs `rate_limit` vs `monitor` vs `escalate_to_hamsters`
- Pattern fingerprints: `brute_force_attack`, `insider_threat`, `network_scan`, etc.

**Scoring:**
- 60% weighted success rate (recent outcomes matter more)
- 40% improvement magnitude (how much did it help?)
- Confidence based on sample size (10+ samples = full confidence)

## Integration with The Stick

Both systems integrate with The Stick's validation layer with **PRIORITY BOOST** for security:

### Threshold Validation
```python
await learned_thresholds.request_stick_validation(
    metric_name='failed_auth_attempts',
    threshold_level='warning',
    learned_value=7,
    default_value=5
)
```

**The Stick validates:**
1. Sample size >= min_threshold_sample_size (5 initial, 10 mature)
2. Shift magnitude <= max_threshold_shift_magnitude (0.15)
3. Direction consistency with trigger reason (false positives → UP, false negatives → DOWN)

**Priority Boost:**
- QSP validations: priority 9 (pass) or 10 (fail)
- QSP false negatives: **always priority 10** with maximum anxiety (100.0)
- Terry/Hamsters validations: priority 8 (pass) or 9 (fail)

### Action Effectiveness Validation
```python
await action_effectiveness.request_stick_validation(
    action='block_ip',
    metric_pattern='brute_force_attack_warning'
)
```

**The Stick validates:**
1. Sample size >= min_action_sample_size (3 initial, 5 mature)
2. Score volatility <= max_action_score_volatility (0.3)
3. Score consistency with raw data (catches model drift)

**Priority Boost:**
- QSP action validation failures: anxiety 50.0 (higher than Terry/Hamsters)

## Database Schema

Reuses Terry's tables with `agent_name='quantum_shadow_people'`:
- `threshold_learning_records` - Stores threshold adjustment outcomes
- `action_outcome_records` - Stores action execution outcomes

No new migrations needed - tables are agent-agnostic.

## Usage Example

```python
from app.ai_agents.quantum_shadow_people.ML.learned_thresholds import LearnedThresholds
from app.ai_agents.quantum_shadow_people.ML.action_effectiveness import ActionEffectivenessModel

# Initialize
learned_thresholds = LearnedThresholds(db, system_id="production")
action_effectiveness = ActionEffectivenessModel(db, system_id="production")

# Get learned threshold
auth_warning = await learned_thresholds.get_threshold('failed_auth_attempts', 'warning')

# Score actions for a threat pattern
action_scores = await action_effectiveness.score_all_actions('brute_force_attack_warning')
best_action = action_scores[0]  # Highest score

# Record outcome with false positive/false negative distinction
await learned_thresholds.record_outcome(
    metric_name='failed_auth_attempts',
    metric_value=7,
    threshold_level='warning',
    was_successful=True,
    was_false_positive=False,
    was_false_negative=False  # SEPARATE from false_positive
)

await action_effectiveness.record_outcome(
    action='block_ip',
    pre_metrics={'threat_count': 5, 'failed_auth_attempts': 7},
    post_metrics={'threat_count': 0, 'failed_auth_attempts': 0},
    severity='warning',
    success=True
)

# Request validation from The Stick
await learned_thresholds.request_stick_validation(
    metric_name='failed_auth_attempts',
    threshold_level='warning',
    learned_value=7,
    default_value=5,
    db_getter=get_async_db
)
```

## Key Differences from Terry and Hamsters

| Aspect | Terry (Meth Snail) | Hamsters | QSP |
|--------|-------------------|----------|-----|
| **Metrics** | CPU, memory, network | Disk, fragmentation, inodes | Threats, failed auth, anomalies |
| **Actions** | restart_service, scale_up | cleanup_temp, defrag | block_ip, rate_limit, escalate |
| **Personality** | Energy drinks, jitter | Beer, duct tape, consensus | Tequila, existential dread, paranoia |
| **Complexity** | Individual agent | Telepathic consensus (3 hamsters) | Quantum state (collapsed/fluctuating/stable) |
| **Defaults** | CPU/memory specific | Storage specific | Security specific (threat classification) |
| **Cost Asymmetry** | Symmetric | Symmetric | **ASYMMETRIC** (false negatives catastrophic) |
| **Priority** | 8/9 | 8/9 | **9/10** (false negatives always 10) |

## Personality vs Learning

**NOT in ML features:**
- Tequila consumption (tracked in personality layer only)
- Existential dread level (tracked in personality layer only)
- Quantum state (tracked in personality layer only)
- Hamster assistance requests (tracked in audit trail metadata only)

**Reason:** Personality metrics muddy the learning signal during cold start. The effectiveness model needs clean data about what action worked for what threat pattern.

**Audit Trail Metadata:**
```python
'execution_metadata': {
    'quantum_state': 'collapsed',
    'existential_dread_level': 0.7,
    'tequila_shots_today': 2,
    'hamster_assistance_requested': True,
    'threat_classification': 'brute_force_attack'
}
```

This allows The Stick and VIC-20 to notice patterns ("QSP in collapsed state has better threat detection") without contaminating the learning model.

## False Positive vs False Negative

**CRITICAL ARCHITECTURAL DECISION:** These are tracked separately, not combined.

### Why This Matters

In Terry's domain and Hamsters' domain, costs are roughly symmetric:
- False alarm: Wasted cycles cleaning disk unnecessarily
- Missed action: Disk fills up and causes problems
- **Roughly equal cost**

In security, costs are wildly asymmetric:
- False positive: Blocked legitimate traffic, wasted hamster time (annoying but recoverable)
- False negative: Actual attack succeeded (**potentially catastrophic**)

### Implementation

```python
# Separate trigger reasons
'trigger_reason': 'false_positive'   # Escalated non-threat → raise threshold
'trigger_reason': 'false_negative'   # Missed real threat → lower threshold URGENTLY

# Separate recording
await learned_thresholds.record_outcome(
    was_false_positive=True,   # Explicit
    was_false_negative=False   # Explicit, not combined
)

# Different urgency in validation
if trigger_reason == "false_negative":
    audit_entry.stick_anxiety_level = 100.0  # Maximum anxiety
    # Priority 10 in CMB audit entry
```

### VIC-20 Audit Layer

When VIC-20's audit layer is implemented, it will see:
- All QSP validations at priority 9/10 (higher than Terry/Hamsters at 8/9)
- False negative validations at priority 10 (maximum)
- Can query: "Show me all security false negatives in the last 7 days"
- Can alert: "QSP missed 3 threats this week - review threshold adjustments"

## Cold Start Strategy

Same as Terry and Hamsters:
1. **Start with conservative defaults** (security industry standard)
2. **Collect data for 30 days** before major adjustments
3. **Validate every adjustment** with The Stick
4. **Gradually increase confidence** as sample size grows
5. **Never auto-promote** to autonomous without explicit policy approval

## Validation Timing

Same as Terry and Hamsters:
- **Real-time validation** after every threshold adjustment
- **Real-time validation** after every action execution
- **Two-hour sweep** as fallback (already implemented in The Stick)

**What differs:** Priority, not frequency. Security validation failures get seen first by VIC-20.

## Session Management

**CRITICAL:** The `request_stick_validation()` methods use `db_getter` to obtain The Stick's database session. This prevents nested session creation, which causes deadlocks.

```python
# CORRECT: Use db_getter to get The Stick's session
async for db in db_getter():
    stick_learning = StickLearning(db, user_id)
    # ... validation logic

# WRONG: Don't create nested sessions
# This will deadlock!
```

This pattern was fixed in Terry's implementation and must be followed here.

## Threshold Types: Counts and Confidence Scores

QSP uses **both** count-based and confidence-based thresholds:

### Count-Based (Continuous)
```python
'failed_auth_attempts': {
    'warning': 5,      # attempts
    'critical': 15     # attempts
}
```
These learn exactly like Terry and Hamsters - slide the number up or down based on false positives and false negatives.

### Confidence-Based (Categorical Boundaries)
```python
'threat_severity': {
    'low': 0.3,        # confidence score
    'medium': 0.6,     # confidence score
    'high': 0.8,       # confidence score
    'critical': 0.95   # confidence score
}
```
The boundaries between categories are continuous numbers even though the categories are discrete. "Low" means confidence below 0.3. "Medium" means 0.3 to 0.6. Learning adjusts those boundary values - sliding 0.6 up to 0.65 means fewer things classify as medium and more stay low.

**Both types learn via continuous threshold adjustment.** The distinction is semantic, not architectural.

## Emergent Patterns

The audit trail metadata allows patterns to emerge through oversight rather than being engineered:

- "QSP's threat detection accuracy correlates with quantum state (collapsed = better)"
- "QSP requests hamster assistance for 80% of critical threats with 90% success"
- "Tequila consumption above 3 shots correlates with false positive rate increase"

These are **findings discovered through The Stick's validation audit trail**, not features fed to the ML model. More valuable because they're emergent patterns rather than assumed correlations.

## Priority in CMB Audit Entries

```python
# Terry validation: priority 8 (pass) or 9 (fail)
# Hamsters validation: priority 8 (pass) or 9 (fail)
# QSP validation: priority 9 (pass) or 10 (fail)
# QSP false negative: priority 10 (always)
```

VIC-20's future audit layer will process entries by priority. Security validation failures appear before storage validation failures. Missed threats appear first.

## One Pattern. One Expectation. One Audit Trail Format.

Consistency across specialists:
- Same validation frequency (real-time + 2-hour sweep)
- Same session management (db_getter, no nested sessions)
- Same database tables (agent_name discriminator)
- Same ValidationAuditEntry format (learning_type discriminator)
- **Different priority** (security gets 9/10 instead of 8/9)

The Stick doesn't need to know three different validation schedules. VIC-20 doesn't need to parse three different audit formats. One pattern. Higher priority for security. That's the distinction.
