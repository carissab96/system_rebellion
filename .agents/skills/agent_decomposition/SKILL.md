# SKILL: System Rebellion Agent Decomposition
## Purpose
Decompose a System Rebellion distributed agent from the old inheritance pattern
(`AgentDecisionEngine + BrainV2`) into the clean composition pattern established
by Terry the Meth Snail and Sir Hawkington.

---

## The Pattern

**Before (old, broken):**
```python
class AgentDistributed(AgentDecisionEngine, BrainV2):
    # Multiple inheritance, dead tissue, dual pipelines
```

**After (clean):**
```python
class AgentName:
    # No inheritance except object
    # Composes four components
    personality = AgentPersonalityState()
    websocket   = AgentWebSocket(personality)
    orchestrator = AgentOrchestrator(personality, db_getter, user_id)
    communication = AgentCommunication(personality, websocket, orchestrator)
```

---

## Canonical Reference Implementations

Always use these as your templates. Read them before writing anything.

| File | Purpose |
|---|---|
| `backend/app/ai_agents/meth_snail/terry_agent.py` | Gold standard entry point |
| `backend/app/ai_agents/meth_snail/terry_personality_state.py` | Gold standard personality |
| `backend/app/ai_agents/meth_snail/terry_orchestrator.py` | Gold standard orchestrator |
| `backend/app/ai_agents/meth_snail/terry_communication.py` | Gold standard communication |
| `backend/app/ai_agents/meth_snail/terry_websocket.py` | Gold standard websocket |
| `backend/app/ai_agents/sir_hawkington/hawkington_agent.py` | Second proven example |
| `backend/app/ai_agents/sir_hawkington/hawk_personality_state.py` | Second proven example |
| `backend/app/ai_agents/sir_hawkington/hawk_orchestrator.py` | Second proven example |
| `backend/app/ai_agents/sir_hawkington/hawk_communication.py` | Second proven example |
| `backend/app/ai_agents/sir_hawkington/hawk_data_types.py` | Second proven example |

---

## The Five Files (always the same five)

### 1. `{agent}_data_types.py`
Dataclasses and enums only. No logic. No decisions.

Must contain the agent's personality artifacts:
- State enums (e.g. `MonocleState`, `QuantumPhaseState`, `BeerLevel`)
- Incident/event dataclasses (e.g. `MonocleYeetIncident`, `BeerConsumptionEvent`)
- Daily tracking dataclass with `.to_dict()` and computed properties
- Alert state record for cooldown management

### 2. `{agent}_personality_state.py`
Pure state container. No decisions. No messaging. No base classes.

Must contain:
- All personality counters and state (per-agent-specific)
- Daily reset method called by orchestrator at start of each pipeline run
- The personality behavior methods (sip tea, yeet monocle, drink beer, etc.)
- Alert cooldown tracking (`should_emit_alert`, `clear_alert_state`)
- `record_analysis(success)` and escalation tracking helpers
- `get_status()` and `health_check()` for heartbeat emission
- Database initialization (lazy, called during agent startup)
- Resource thresholds dict

### 3. `{agent}_orchestrator.py`
Pure ML pipeline. No messaging. No frontend emission.

Must:
- Call `personality._reset_daily_counters_if_needed()` at top of `run_pipeline()`
- Run: Perception → Reasoning → Action Selection → Learning
- Call personality behavior methods at the RIGHT moments (dismiss vs escalate)
- Return a structured result dict containing all pipeline outputs plus personality snapshot
- Handle db session via `db_getter()` generator pattern (same as Terry)
- Record `personality.record_analysis(success=True/False)`

### 4. `{agent}_websocket.py`
Frontend emission only. Reads personality and pipeline results. No decisions.

Must contain:
- `get_agent_status()` — heartbeat payload including all personality data
- `emit_decision(pipeline_result)` — full ML pipeline emission
- `emit_insight(action, reasoning, context)` — narrative feed

### 5. `{agent}_communication.py`
Redis, message bus, inter-agent messaging. No ML pipeline logic.

Must contain:
- `initialize(redis_client)` — sets up hub, heartbeat, subscriptions, ResourceMonitor
- `_handle_resource_alert(alert)` — entry point from ResourceMonitor
  - Checks cooldown via `personality.should_emit_alert()`
  - Calls `orchestrator.run_pipeline(alert_payload)`
  - Emits to frontend if `should_emit`
  - Routes to VIC-20 or Stick based on `result['should_escalate']`
- `_handle_coordination_request(message)` — handles VIC-20 messages
- `_handle_stick_feedback(message)` — handles Stick feedback
- `_handle_emergency(message)` — emergency handler
- `_escalate_to_vic20(result)` — sends TRIAGE_ALERT or ACTION_OUTCOME
- `_log_to_stick(result)` — sends DECISION_LOG
- `_heartbeat_loop(interval)` — periodic heartbeat
- `shutdown()` — clean teardown
- `get_distributed_state()` — returns state from comm hub
- `is_distributed` property

### 6. `{agent}_agent.py` (Entry Point)
Composes all four. No inheritance except object.

Must:
- Create all four components in `__init__`
- Expose `initialize(redis_client)`, `shutdown()`, `get_agent_status()`, `is_distributed`
- Wire `orchestrator._comm_hub_ref` after communication init
- Include `handle_coordination()` legacy shim with warning log
- Include `__repr__` with key personality metrics
- Include convenience factory function `create_{agent}(redis_client, ...)`

---

## Agent-Specific Notes

### The Hamsters (Steve, Bob, Carl)

**Files to read first:**
- `backend/app/ai_agents/hamsters/distributed_hamsters.py`
- `backend/app/ai_agents/hamsters/decision_engine_sbcV3.py`
- `backend/app/ai_agents/hamsters/ML/perception.py`

**Personality state — THREE hamsters tracked separately:**

Steve (careful, analytical):
- `steve_beer_count: int` — paces himself, baseline 2
- `steve_risk_tolerance: float = 0.3`
- `steve_current_task: Optional[str]`

Bob (wild, chaotic):
- `bob_beer_count: int` — always ready, baseline 4
- `bob_risk_tolerance: float = 0.8`
- `bob_wild_ideas: int` — counter, increments on complex jobs
- `bob_wild_idea_pending: Optional[str]`
- `bob_at_cupboard: bool` — proximity to supply cupboard
- `bob_hold_my_beer_count: int` — "hold my beer" moments
- `bob_supply_cupboard_raids_today: int`

Carl (duct tape expert, moderate):
- `carl_beer_count: int` — moderate, baseline 3
- `carl_risk_tolerance: float = 0.5`
- `carl_duct_tape_inventory: Dict[str, int]` — grades: regular, premium, quantum, carls_special
- `carl_duct_tape_rolls_used_today: float` — total rolls used
- `carl_duct_tape_jobs_today: List[DuctTapeJob]` — each job with roll count and complexity

**Collective state:**
- `collective_beer_level: BeerLevel` — calculated from individual counts
- `beer_consumption_today: int` — total across all three
- `telepathic_consensus_strength: float` — bond strength
- `squeak_history: List[str]`

**Daily reset:** beer counts DO NOT reset daily (they accumulate per job, reset between jobs 
based on sobriety logic). Track `beer_consumption_today` as the daily counter.

**Personality behaviors:**

`consume_beer(hamster, count, reason, complexity)`:
- Increments individual hamster beer count
- Increments `beer_consumption_today`
- Recalculates `collective_beer_level`
- Logs per-hamster with flavor text

`bob_has_wild_idea(idea_description)`:
- Increments `bob_wild_ideas`
- Sets `bob_wild_idea_pending`
- Logs "BOB HAS A WILD IDEA" with Stick anxiety warning
- Wilder idea = more beer for everyone (call `consume_beer` for all three)

`bob_raids_cupboard(items_acquired)`:
- Sets `bob_at_cupboard = True`
- Increments `bob_supply_cupboard_raids_today`
- Broadcasts anxiety signal (communication layer picks this up and notifies Stick)
- The more raids, the more anxious the Stick gets

`carl_calculates_duct_tape(complexity, job_type)`:
- Returns `DuctTapeJob` with roll counts per grade
- Simple job: regular tape only
- Moderate: regular + premium
- Complex: all grades including quantum
- Quantum/emergency: Carl's Special (use wisely — effects permanent)
- Total rolls = complexity metric (more rolls = worse disk situation)

`record_telepathic_consensus(strength)`:
- Updates `telepathic_consensus_strength`
- Logs consensus result

**Bob → Stick anxiety pipeline:**
When Bob has a wild idea OR raids the cupboard, communication layer sends a
`HAMSTER_ACTIVITY` message that The Stick receives and processes as anxiety trigger.
The wilder the idea (measured by `bob_wild_ideas` count and complexity), the higher
the Stick's anxiety level in its response.

**Data types needed:**
```python
class BeerLevel(Enum):
    SOBER = "sober"          # Error state
    TIPSY = "tipsy"          # Minimum operational
    OPTIMAL = "optimal"      # Peak performance
    ADVENTUROUS = "adventurous"  # Hold my beer territory
    LEGENDARY = "legendary"  # Carl's doing calculus with duct tape

class DuctTapeGrade(Enum):
    REGULAR = "regular"
    PREMIUM = "premium"
    QUANTUM = "quantum"
    CARLS_SPECIAL = "carls_special"  # Effects permanent

@dataclass
class DuctTapeJob:
    job_type: str
    complexity: str  # 'simple', 'moderate', 'complex', 'quantum'
    regular_rolls: float
    premium_rolls: float
    quantum_rolls: float
    carls_special_rolls: float
    total_rolls: float
    timestamp: datetime

@dataclass
class BeerConsumptionEvent:
    hamster: str  # 'steve', 'bob', 'carl'
    beers_consumed: int
    reason: str
    complexity_level: float
    timestamp: datetime
```

**Orchestrator call sites (personality behaviors):**
- Dismiss/normal: `personality.consume_beer(each hamster, small amount, 'routine check', low_complexity)` — routine rounds still require a beer
- Escalate: `personality.consume_beer(all three, more, 'disk crisis', complexity)` + `personality.carl_calculates_duct_tape(complexity, job_type)`
- Complex/wild idea: `personality.bob_has_wild_idea(description)` — automatically triggers more beer
- Emergency: `personality.bob_raids_cupboard(['emergency_tape', 'more_beer', 'pizza_money'])`

**Resource domain:** DISK only. Threshold: 80%.

**Agent name:** `"hamsters"`

**Personality traits dict:**
```python
{
    "telepathic": True,
    "beer_loving": True,
    "duct_tape_experts": True,
    "steve_analytical": True,
    "bob_wild": True,
    "carl_duct_tape_genius": True,
    "consensus_required": True,
    "squeak_frequency": "high",
    "beer_preference": "craft_ipa",
    "trust_level": 0.8,
    "steve_risk_tolerance": 0.3,
    "bob_risk_tolerance": 0.8,
    "carl_risk_tolerance": 0.5,
}
```

---

### Quantum Shadow People (QSP)

**Files to read first:**
- `backend/app/ai_agents/quantum_shadow_people/distributed_qsp.py`
- `backend/app/ai_agents/quantum_shadow_people/decision_engine.py`
- `backend/app/ai_agents/quantum_shadow_people/data_types.py`
- `backend/app/ai_agents/quantum_shadow_people/ML/perception.py`

**Personality state — single agent, collective entity:**

Quantum state:
- `current_quantum_phase: QuantumPhaseState` — current dimensional phase
- `quantum_coherence: float` — 0.0-1.0, stability
- `existential_dread_level: float` — 0.0-1.0, uncertainty
- `quantum_phase_shifts: int` — total phase shifts

Tequila tracking (daily):
- `tequila_shots_today: int`
- `tequila_shots_total: int`
- `_last_tequila_reset_date: Optional[date]`

Paranoia state:
- `paranoia_level: str` — "healthy" | "elevated" | "maximum" | "JUSTIFIED"
- `threats_detected: int`
- `false_alarms: int`
- `total_security_scans: int`

**Daily reset:** `tequila_shots_today` resets. `paranoia_level` does NOT
reset daily — paranoia earned through real threats persists. `threats_detected`
and `false_alarms` are lifetime counters.

**Personality behaviors:**

`consume_tequila_shot(count, reason, threat_severity)`:
- Increments `tequila_shots_today` and `tequila_shots_total`
- Updates paranoia level based on total today (more shots = more paranoid)
- Triggers quantum phase shift if shots > threshold
- Logs with flavor text ("*quantum paranoia intensifies*")
- Daily reset check at start

`update_paranoia_level(trigger)`:
- trigger: "threat_detected" | "false_alarm" | "tequila_shot" | "threat_resolved"
- "threat_detected": increments `threats_detected`, escalates paranoia
  - 1+ threats: "elevated"
  - 3+ threats: "maximum"  
  - 5+ threats: "JUSTIFIED"
- "false_alarm": increments `false_alarms`, slightly reduces paranoia over time
- "tequila_shot": paranoia increases with shot count
- Logs quantum phase shift on every paranoia change

`phase_shift(new_phase, reason)`:
- Updates `current_quantum_phase`
- Increments `quantum_phase_shifts`
- Updates `quantum_coherence` based on phase stability
- Logs with appropriate dimensional flavor text

`record_security_scan(threats_found, false_positive)`:
- Increments `total_security_scans`
- Calls `update_paranoia_level()` appropriately
- Updates `quantum_coherence`

**Tequila → confidence relationship:**
More tequila shots = lower confidence in assessments (too paranoid to think straight)
BUT shots are REQUIRED for certain quantum operations. It's a feature, not a bug.

```python
# Confidence degradation
base_confidence = 0.5  # Always suspicious
if shots_today > 5:
    base_confidence *= 0.8  # MAXIMUM PARANOIA
elif shots_today > 3:
    base_confidence *= 0.9  # Elevated paranoia
# Justified paranoia restores some confidence:
if threats_detected > 0:
    base_confidence += min(0.3, threats_detected * 0.1)
```

**Orchestrator call sites (personality behaviors):**
- Clean network: `personality.consume_tequila_shot(1, 'routine quantum observation', 'low')` — always consume at least one
- Anomaly detected: `personality.consume_tequila_shot(2-3, reason, severity)` + `personality.update_paranoia_level('threat_detected')`
- False alarm: `personality.update_paranoia_level('false_alarm')`
- Escalate emergency: `personality.consume_tequila_shot(4, 'quantum emergency', 'critical')` + `personality.phase_shift(QuantumPhaseState.VOID_WALKER, reason)`

**Data types needed:**
```python
class QuantumPhaseState(Enum):
    # Import from existing data_types.py — DO NOT REWRITE
    pass  

@dataclass
class TequilaState:
    shots_today: int = 0
    shots_total: int = 0
    last_reset_date: Optional[date] = None
    
    @property
    def paranoia_multiplier(self) -> float:
        if self.shots_today > 5: return 2.0
        if self.shots_today > 3: return 1.5
        return 1.0
    
    def to_dict(self) -> dict:
        return {
            'shots_today': self.shots_today,
            'shots_total': self.shots_total,
            'paranoia_multiplier': self.paranoia_multiplier,
        }
```

NOTE: `QuantumPhaseState`, `QSPDecisionType`, `QSPDecision` already exist in
`quantum_shadow_people/data_types.py`. Import them, do not duplicate.

**Resource domain:** NETWORK only. Multi-signal (not a single percentage):
- `recv_rate`, `sent_rate` (bytes/sec)
- `failed_auth_attempts`
- `total_connections`
- `active_connections`
Thresholds for each are in the existing perception layer — use them.

**Agent name:** `"quantum_shadow_people"`

**Personality traits dict:**
```python
{
    "quantum": True,
    "paranoid": True,
    "tequila_jello_shot_powered": True,
    "network_obsessed": True,
    "security_focused": True,
    "phase_shifting": True,
    "coherence_maintenance": "critical",
    "scan_frequency": "continuous",
    "trust_level": 0.4,  # LOW - TRUST NO ONE
}
```

---

## What Does NOT Change

**ML layers are untouched.** The four ML files (perception.py, reasoning.py,
action_selection.py, learning.py) already exist and work. The orchestrator
imports and calls them. Do not rewrite them.

**Database integration files are untouched.** `database_integration.py` stays.

**Decision engine files are retired, not rewritten.** The old BrainV2/V3 files
get replaced by the personality state, not ported to it. Extract personality
state (counters, traits, thresholds) and discard the decision logic — that
now lives in the ML layers.

**Personalities stay intact.** Beer counts, duct tape grades, quantum phases,
tequila shots, wild ideas, paranoia levels — all of it survives. The decomposition
changes WHERE state lives and HOW decisions are made, not WHO these agents are.

---

## What Gets Retired

After new files are confirmed working:
- `distributed_hamsters.py` → retired
- `decision_engine_sbcV3.py` → retired  
- `distributed_qsp.py` → retired
- `decision_engine.py` (QSP) → retired (ML layers already extracted)

The old distributed files used `initialize_distributed()`. The new agents use
`initialize()`. Update `distributed_agent_manager.py` accordingly:

```python
# Hamsters
# REMOVE: from app.ai_agents.hamsters.distributed_hamsters import HamstersDistributed
# ADD:    from app.ai_agents.hamsters.hamsters_agent import HamstersAgent
# REMOVE: hamsters = HamstersDistributed(...); await hamsters.initialize_distributed(redis)
# ADD:    hamsters = HamstersAgent(...); await hamsters.initialize(redis)

# QSP
# REMOVE: from app.ai_agents.quantum_shadow_people.distributed_qsp import QuantumShadowPeopleDistributed
# ADD:    from app.ai_agents.quantum_shadow_people.qsp_agent import QSPAgent
# REMOVE: shadows = QuantumShadowPeopleDistributed(...); await shadows.initialize_distributed(redis)
# ADD:    shadows = QSPAgent(...); await shadows.initialize(redis)
```

---

## Checklist Before Calling It Done

- [ ] All five files created per agent
- [ ] No inheritance in agent entry point except object
- [ ] ML layers untouched
- [ ] Personality state has daily reset method
- [ ] Orchestrator calls daily reset at top of `run_pipeline()`
- [ ] Personality behaviors called at correct moments (dismiss vs escalate)
- [ ] Communication layer registers all message handlers
- [ ] ResourceMonitor wired via `register_alert_callback`
- [ ] `distributed_agent_manager.py` updated (import + init method)
- [ ] Bob → Stick anxiety pipeline wired
- [ ] Carl duct tape jobs tracked per-job
- [ ] QSP tequila daily reset works
- [ ] `get_agent_status()` includes all personality data
- [ ] Logs include personality flavor text (squeaks, quantum phases, beer counts, etc.)
- [ ] Smoke test: agent appears in manager, pipeline runs, Stick gets DECISION_LOG
