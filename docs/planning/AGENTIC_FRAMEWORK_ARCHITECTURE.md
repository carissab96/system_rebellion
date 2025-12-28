# Agentic Framework Architecture - Terry v2 (The Blueprint)

## Core Philosophy

**Agents are not state machines. They are autonomous decision-makers with:**
- **Perception:** Full access to system state
- **Reasoning:** Ability to analyze root causes
- **Action:** Dynamic selection from available tools
- **Learning:** Memory of what works in similar contexts

**No fake data. No fallbacks. No hardcoded decisions. Real thinking, real learning, real autonomy.**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATION REQUEST                      │
│  (from VIC-20: resource_type, severity, recommendation)     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   1. PERCEPTION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Query full metrics from SimplifiedMetricsService   │  │
│  │ • Access historical patterns from PostgreSQL         │  │
│  │ • Retrieve similar past situations                   │  │
│  │ • Get current agent state (personality metrics)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Output: PerceptionContext {                                │
│    full_metrics: {...},                                     │
│    historical_patterns: [...],                              │
│    similar_situations: [...],                               │
│    agent_state: {...}                                       │
│  }                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   2. REASONING ENGINE                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ A. ROOT CAUSE ANALYSIS                               │  │
│  │    • Analyze top processes (CPU hogs)                │  │
│  │    • Check memory pressure (swap thrashing?)         │  │
│  │    • Examine disk I/O (I/O wait?)                    │  │
│  │    • Review network activity (network-bound?)        │  │
│  │                                                       │  │
│  │ B. CONTEXT MATCHING                                  │  │
│  │    • Find similar past situations                    │  │
│  │    • What actions worked before?                     │  │
│  │    • What failed before?                             │  │
│  │    • Confidence scoring                              │  │
│  │                                                       │  │
│  │ C. DECISION SYNTHESIS                                │  │
│  │    • Combine root cause + historical learning        │  │
│  │    • Weight VIC-20's recommendation                  │  │
│  │    • Consider agent personality (meth-fueled bias)   │  │
│  │    • Generate action hypothesis                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Output: ReasoningResult {                                  │
│    root_cause: "memory_thrashing",                          │
│    confidence: 0.87,                                        │
│    recommended_action: "restart_service",                   │
│    reasoning: "Top process is python using 8GB...",         │
│    alternatives: ["emergency_cache_clear", "throttle..."]   │
│  }                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   3. ACTION SELECTION                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Review available actions from SystemActions        │  │
│  │ • Match action to root cause                         │  │
│  │ • Apply personality bias (Terry loves cache clears)  │  │
│  │ • Consider risk vs reward                            │  │
│  │ • Make final decision (override VIC-20 if needed)    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Output: ActionDecision {                                   │
│    action: "restart_service",                               │
│    parameters: {"service_name": "redis"},                   │
│    confidence: 0.87,                                        │
│    followed_vic20: false,                                   │
│    reasoning: "..."                                         │
│  }                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   4. EXECUTION                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Execute action via SystemActions                   │  │
│  │ • Monitor execution (success/failure)                │  │
│  │ • Capture result metrics                             │  │
│  │ • Emit personality events (shell spins!)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Output: ExecutionResult {                                  │
│    success: true,                                           │
│    result: {...},                                           │
│    metrics_after: {...}                                     │
│  }                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   5. LEARNING SYSTEM                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Store situation → action → outcome                 │  │
│  │ • Update success rates for action types              │  │
│  │ • Adjust confidence in similar situations            │  │
│  │ • Share learning with The Stick (cross-agent)        │  │
│  │ • Update personality metrics (override_success_rate) │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Output: LearningRecord {                                   │
│    situation_fingerprint: "cpu_high_memory_thrashing",      │
│    action_taken: "restart_service",                         │
│    outcome: "success",                                      │
│    metrics_improvement: {...},                              │
│    timestamp: "..."                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Structures

### 1. PerceptionContext
```python
@dataclass
class PerceptionContext:
    """Everything Terry needs to perceive the situation"""
    
    # Full system metrics
    full_metrics: Dict[str, Any]  # From SimplifiedMetricsService
    
    # Coordination request context
    resource_type: str  # 'cpu', 'memory', 'disk', 'network'
    current_value: float
    threshold: float
    severity: str
    vic20_recommendation: Dict[str, Any]
    
    # Historical context
    similar_situations: List[Dict[str, Any]]  # Past situations with same fingerprint
    recent_actions: List[Dict[str, Any]]  # Last 10 actions taken
    
    # Agent state
    agent_state: Dict[str, Any]  # Current personality metrics
    override_success_rate: float
    
    # Timestamp
    timestamp: str
```

### 2. ReasoningResult
```python
@dataclass
class ReasoningResult:
    """Terry's analysis of the situation"""
    
    # Root cause analysis
    root_cause: str  # 'cpu_bound', 'memory_thrashing', 'io_wait', 'network_bound'
    root_cause_confidence: float  # 0.0 - 1.0
    
    # Evidence
    evidence: Dict[str, Any]  # What led to this conclusion
    top_culprits: List[Dict[str, Any]]  # Top processes/issues
    
    # Historical learning
    similar_past_situations: List[Dict[str, Any]]
    what_worked_before: List[str]  # Actions that succeeded
    what_failed_before: List[str]  # Actions that failed
    
    # Decision
    recommended_action: str
    action_confidence: float
    alternatives: List[Dict[str, str]]  # Other viable actions
    
    # Reasoning chain
    reasoning: str  # Natural language explanation
    followed_vic20: bool
    override_reason: Optional[str]  # If overriding VIC-20
```

### 3. ActionDecision
```python
@dataclass
class ActionDecision:
    """Final decision on what to do"""
    
    action: str  # Function name from SystemActions
    parameters: Dict[str, Any]  # Parameters for the action
    confidence: float
    
    # Context
    followed_vic20: bool
    reasoning: str
    expected_outcome: str
    
    # Risk assessment
    risk_level: str  # 'low', 'medium', 'high'
    reversible: bool  # Can this be undone?
```

### 4. ExecutionResult
```python
@dataclass
class ExecutionResult:
    """Result of executing the action"""
    
    success: bool
    action: str
    parameters: Dict[str, Any]
    
    # Results
    result_data: Dict[str, Any]  # From SystemActions
    error: Optional[str]
    
    # Metrics
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    improvement: Dict[str, float]  # Calculated deltas
    
    # Timing
    execution_time: float
    timestamp: str
```

### 5. LearningRecord
```python
@dataclass
class LearningRecord:
    """What Terry learned from this experience"""
    
    # Hierarchical situation fingerprints (3 levels)
    fingerprint_l1: str  # 'cpu_high'
    fingerprint_l2: str  # 'cpu_high_memory_thrashing'
    fingerprint_l3: str  # 'cpu_high_memory_thrashing_python'
    
    resource_type: str
    severity: str
    root_cause: str
    process_category: str  # 'python', 'database', 'web_server', 'system', 'other'
    
    # Action taken
    action: str
    parameters: Dict[str, Any]
    confidence: float
    followed_vic20: bool
    
    # Outcome
    success: bool
    improvement: Dict[str, float]
    
    # Learning
    what_worked: Optional[str]
    what_failed: Optional[str]
    
    # Metadata
    timestamp: str
    agent_name: str
```

---

## Hierarchical Fingerprinting System

### Three-Level Structure

```python
class SituationFingerprint:
    """Generate hierarchical fingerprints for situation matching"""
    
    # Process category mapping
    PROCESS_CATEGORIES = {
        'python': ['python', 'python3', 'python3.11'],
        'database': ['postgres', 'postgresql', 'mysql', 'redis', 'mongodb'],
        'web_server': ['nginx', 'apache', 'apache2', 'node', 'npm'],
        'system': ['systemd', 'kworker', 'ksoftirqd', 'migration'],
    }
    
    @staticmethod
    def generate(context: PerceptionContext, root_cause: str) -> Dict[str, str]:
        """
        Generate 3-level hierarchical fingerprint.
        
        Level 1: Resource + Severity (broad matching)
        Level 2: + Root Cause (specific problem type)
        Level 3: + Process Category (context-specific)
        """
        resource = context.resource_type
        severity = context.severity
        
        # Level 1: Broad
        l1 = f"{resource}_{severity}"
        
        # Level 2: Add root cause
        l2 = f"{resource}_{severity}_{root_cause}"
        
        # Level 3: Add process category
        process_category = SituationFingerprint._categorize_process(
            context.full_metrics
        )
        l3 = f"{resource}_{severity}_{root_cause}_{process_category}"
        
        return {
            'level_1': l1,
            'level_2': l2,
            'level_3': l3,
            'process_category': process_category
        }
    
    @staticmethod
    def _categorize_process(metrics: Dict[str, Any]) -> str:
        """Categorize the top process causing issues"""
        top_processes = metrics.get('cpu', {}).get('top_processes', [])
        
        if not top_processes:
            return 'other'
        
        top_process_name = top_processes[0].get('name', '').lower()
        
        for category, process_names in SituationFingerprint.PROCESS_CATEGORIES.items():
            if any(pname in top_process_name for pname in process_names):
                return category
        
        return 'other'
```

### Query Strategy

```python
async def find_similar_situations(
    self,
    fingerprints: Dict[str, str]
) -> List[LearningRecord]:
    """
    Query historical learning with fallback hierarchy.
    
    Try exact match first, fall back to broader matches.
    """
    # Try Level 3 (most specific)
    records = await self._query_by_fingerprint(fingerprints['level_3'])
    
    if len(records) >= 3:  # Enough data at this level
        return records
    
    # Fall back to Level 2
    records_l2 = await self._query_by_fingerprint(fingerprints['level_2'])
    records.extend(records_l2)
    
    if len(records) >= 3:
        return records
    
    # Fall back to Level 1 (broadest)
    records_l1 = await self._query_by_fingerprint(fingerprints['level_1'])
    records.extend(records_l1)
    
    return records
```

**Why 3 data points minimum?** 
- 1 data point: Could be luck/fluke
- 2 data points: Still not enough for pattern
- 3+ data points: Start to see patterns

---

## Adaptive Confidence Calculation

### Bayesian Foundation with Context Adjustments

```python
class ConfidenceCalculator:
    """Calculate confidence using Bayesian base + adaptive adjustments"""
    
    @staticmethod
    def calculate(
        historical_outcomes: List[LearningRecord],
        context: PerceptionContext,
        action: str
    ) -> float:
        """
        Hybrid confidence calculation:
        - Bayesian base (statistically sound)
        - Novelty boost (fast learning on new situations)
        - Context adjustments (VIC-20 agreement, personality)
        """
        if not historical_outcomes:
            return 0.5  # Neutral starting point
        
        # 1. BAYESIAN BASE
        successes = sum(1 for r in historical_outcomes if r.success)
        failures = len(historical_outcomes) - successes
        
        # Beta distribution: alpha=successes+1, beta=failures+1
        base_confidence = (successes + 1) / (successes + failures + 2)
        
        # 2. NOVELTY BOOST
        # More data = less novelty = smaller boost
        novelty_score = 1.0 / (1.0 + len(historical_outcomes))
        novelty_boost = novelty_score * 0.2  # Up to +0.2 for novel situations
        
        # 3. CONTEXT ADJUSTMENTS
        context_boost = 0.0
        
        # VIC-20 agreement signal
        vic20_agreements = sum(
            1 for r in historical_outcomes 
            if r.success and r.followed_vic20
        )
        if vic20_agreements > 0:
            agreement_rate = vic20_agreements / successes if successes > 0 else 0
            context_boost += agreement_rate * 0.1  # Up to +0.1
        
        # Personality bias (Terry loves cache clears)
        if action == 'emergency_cache_clear':
            context_boost += 0.05  # Meth-fueled bias
        
        # 4. COMBINE
        final_confidence = base_confidence + novelty_boost + context_boost
        
        # 5. BOUND [0.1, 0.95]
        # Never 0.0 (always willing to try)
        # Never 1.0 (never overconfident)
        return max(0.1, min(0.95, final_confidence))
    
    @staticmethod
    def calculate_learning_examples():
        """
        Examples of confidence calculation:
        """
        examples = [
            {
                'scenario': 'First time seeing situation',
                'successes': 0,
                'failures': 0,
                'novelty': 1.0,
                'base': 0.5,
                'novelty_boost': 0.2,
                'context': 0.0,
                'final': 0.7,
                'note': 'Fast learning - willing to try'
            },
            {
                'scenario': 'After 1 success',
                'successes': 1,
                'failures': 0,
                'novelty': 0.5,
                'base': 0.67,
                'novelty_boost': 0.1,
                'context': 0.05,
                'final': 0.82,
                'note': 'Quick confidence gain'
            },
            {
                'scenario': 'After 5 successes',
                'successes': 5,
                'failures': 0,
                'novelty': 0.17,
                'base': 0.86,
                'novelty_boost': 0.034,
                'context': 0.05,
                'final': 0.94,
                'note': 'High confidence, near cap'
            },
            {
                'scenario': 'Mixed results (3 success, 2 fail)',
                'successes': 3,
                'failures': 2,
                'novelty': 0.2,
                'base': 0.57,
                'novelty_boost': 0.04,
                'context': 0.03,
                'final': 0.64,
                'note': 'Moderate confidence, still learning'
            },
            {
                'scenario': 'After 20 successes (mature learning)',
                'successes': 20,
                'failures': 0,
                'novelty': 0.05,
                'base': 0.95,
                'novelty_boost': 0.01,
                'context': 0.05,
                'final': 0.95,
                'note': 'Capped at 0.95, stable confidence'
            }
        ]
        return examples
```

### Learning Speed Characteristics

**Novel Situations (0-3 data points):**
- Confidence: 0.5 → 0.82 after 1 success
- Fast learning, high variance
- Willing to experiment

**Emerging Patterns (4-10 data points):**
- Confidence: 0.82 → 0.90 range
- Moderate learning rate
- Pattern recognition forming

**Mature Learning (10+ data points):**
- Confidence: 0.90 → 0.95 (capped)
- Slow adjustments (fine-tuning)
- Stable, reliable decisions

**Why cap at 0.95?**
- Systems change (what worked yesterday may not work today)
- Always leave room for adaptation
- Prevent overconfidence bias

---

## Implementation Plan

### Phase 1: Perception Layer
**File:** `backend/app/ai_agents/meth_snail/perception.py`

```python
class TerryPerception:
    """Terry's perception system - gathering all context"""
    
    async def perceive(
        self,
        coordination_request: Dict[str, Any]
    ) -> PerceptionContext:
        """
        Gather full context for decision-making.
        
        NO FAKE DATA. If metrics unavailable, raise exception.
        """
        # 1. Get full system metrics
        full_metrics = await self._get_full_metrics()
        
        # 2. Query historical patterns
        similar_situations = await self._find_similar_situations(
            resource_type=coordination_request['resource_type'],
            severity=coordination_request['severity']
        )
        
        # 3. Get recent actions
        recent_actions = await self._get_recent_actions(limit=10)
        
        # 4. Get agent state
        agent_state = await self._get_agent_state()
        
        return PerceptionContext(
            full_metrics=full_metrics,
            resource_type=coordination_request['resource_type'],
            current_value=coordination_request['current_value'],
            threshold=coordination_request['threshold'],
            severity=coordination_request['severity'],
            vic20_recommendation=coordination_request['recommendation'],
            similar_situations=similar_situations,
            recent_actions=recent_actions,
            agent_state=agent_state,
            override_success_rate=self.override_success_rate,
            timestamp=utc_now().isoformat()
        )
```

### Phase 2: Reasoning Engine
**File:** `backend/app/ai_agents/meth_snail/reasoning.py`

```python
class TerryReasoning:
    """Terry's reasoning engine - analyzing root causes"""
    
    async def reason(
        self,
        context: PerceptionContext
    ) -> ReasoningResult:
        """
        Analyze the situation and determine best action.
        
        Real analysis. Real reasoning. No hardcoded rules.
        """
        # 1. Root cause analysis
        root_cause = await self._analyze_root_cause(context)
        
        # 2. Historical learning
        learning = await self._apply_historical_learning(context)
        
        # 3. Decision synthesis
        decision = await self._synthesize_decision(
            root_cause=root_cause,
            learning=learning,
            context=context
        )
        
        return decision
    
    async def _analyze_root_cause(self, context: PerceptionContext) -> Dict[str, Any]:
        """
        Determine WHY the resource is stressed.
        
        Not just "CPU is high" but "CPU is high BECAUSE..."
        """
        metrics = context.full_metrics
        
        if context.resource_type == 'cpu':
            # Analyze CPU stress
            top_processes = metrics['cpu']['top_processes']
            memory_percent = metrics['memory']['percent']
            swap_percent = metrics['memory'].get('swap_percent', 0)
            disk_io = metrics['disk'].get('read_bytes', 0) + metrics['disk'].get('write_bytes', 0)
            
            # Is it memory thrashing?
            if swap_percent > 80 and memory_percent > 90:
                return {
                    'cause': 'memory_thrashing',
                    'confidence': 0.9,
                    'evidence': {
                        'swap_usage': swap_percent,
                        'memory_usage': memory_percent,
                        'top_process': top_processes[0] if top_processes else None
                    }
                }
            
            # Is it I/O wait?
            elif disk_io > 1000000000:  # 1GB/s
                return {
                    'cause': 'io_wait',
                    'confidence': 0.85,
                    'evidence': {
                        'disk_io': disk_io,
                        'top_process': top_processes[0] if top_processes else None
                    }
                }
            
            # Pure CPU bound
            else:
                return {
                    'cause': 'cpu_bound',
                    'confidence': 0.8,
                    'evidence': {
                        'cpu_usage': context.current_value,
                        'top_processes': top_processes[:3]
                    }
                }
        
        # Similar analysis for memory, disk, network...
        return {'cause': 'unknown', 'confidence': 0.0}
```

### Phase 3: Action Selection
**File:** `backend/app/ai_agents/meth_snail/action_selection.py`

```python
class TerryActionSelection:
    """Terry's action selection - choosing what to do"""
    
    # Available actions mapped to root causes
    ACTION_MAP = {
        'memory_thrashing': [
            'restart_service',  # Kill memory hog
            'emergency_cache_clear',  # Free up memory
        ],
        'io_wait': [
            'throttle_cpu_intensive_tasks',  # Reduce I/O pressure
            'adjust_process_priority',  # Deprioritize I/O hogs
        ],
        'cpu_bound': [
            'emergency_cache_clear',  # Terry's favorite
            'adjust_process_priority',  # Nice the CPU hogs
            'throttle_cpu_intensive_tasks',
        ],
        'network_bound': [
            'scan_open_ports',  # Identify network issues
            'restart_service',  # Restart network services
        ]
    }
    
    async def select_action(
        self,
        reasoning: ReasoningResult,
        context: PerceptionContext
    ) -> ActionDecision:
        """
        Choose the best action based on reasoning and personality.
        
        Terry loves cache clears, but he'll learn when they don't work.
        """
        root_cause = reasoning.root_cause
        
        # Get viable actions for this root cause
        viable_actions = self.ACTION_MAP.get(root_cause, [])
        
        if not viable_actions:
            # Fallback to VIC-20's recommendation
            return ActionDecision(
                action=context.vic20_recommendation['action'],
                parameters={},
                confidence=context.vic20_recommendation.get('confidence', 0.5),
                followed_vic20=True,
                reasoning="No learned actions for this root cause",
                expected_outcome="Unknown",
                risk_level="medium",
                reversible=True
            )
        
        # Score each action based on historical success
        action_scores = await self._score_actions(
            viable_actions,
            reasoning.similar_past_situations
        )
        
        # Apply personality bias (Terry loves cache clears)
        if 'emergency_cache_clear' in action_scores:
            action_scores['emergency_cache_clear'] *= 1.2  # 20% bias
        
        # Select highest scoring action
        best_action = max(action_scores.items(), key=lambda x: x[1])
        
        return ActionDecision(
            action=best_action[0],
            parameters=self._get_action_parameters(best_action[0], context),
            confidence=best_action[1],
            followed_vic20=(best_action[0] == context.vic20_recommendation['action']),
            reasoning=reasoning.reasoning,
            expected_outcome=f"Resolve {root_cause}",
            risk_level=self._assess_risk(best_action[0]),
            reversible=True
        )
```

### Phase 4: Learning System
**File:** `backend/app/ai_agents/meth_snail/learning.py`

```python
class TerryLearning:
    """Terry's learning system - remembering what works"""
    
    async def learn(
        self,
        context: PerceptionContext,
        reasoning: ReasoningResult,
        decision: ActionDecision,
        result: ExecutionResult
    ) -> LearningRecord:
        """
        Store this experience for future reference.
        
        Success or failure, Terry learns from it.
        """
        # Create situation fingerprint
        fingerprint = self._create_fingerprint(
            resource_type=context.resource_type,
            severity=context.severity,
            root_cause=reasoning.root_cause
        )
        
        # Calculate improvement
        improvement = self._calculate_improvement(
            result.metrics_before,
            result.metrics_after,
            context.resource_type
        )
        
        # Create learning record
        record = LearningRecord(
            situation_fingerprint=fingerprint,
            resource_type=context.resource_type,
            severity=context.severity,
            root_cause=reasoning.root_cause,
            action=decision.action,
            parameters=decision.parameters,
            confidence=decision.confidence,
            success=result.success and improvement > 0,
            improvement=improvement,
            what_worked=decision.action if result.success else None,
            what_failed=decision.action if not result.success else None,
            adjust_confidence=0.1 if result.success else -0.1,
            timestamp=utc_now().isoformat(),
            agent_name='meth_snail'
        )
        
        # Store in PostgreSQL
        await self._store_learning(record)
        
        # Update override success rate
        if not decision.followed_vic20:
            await self._update_override_success_rate(result.success)
        
        # Share with The Stick
        await self._share_with_stick(record)
        
        return record
```

---

## Database Schema Updates

### New Table: `agent_learning_records`
```sql
CREATE TABLE agent_learning_records (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    
    -- Hierarchical fingerprints (3 levels)
    fingerprint_l1 VARCHAR(50) NOT NULL,   -- 'cpu_high'
    fingerprint_l2 VARCHAR(100) NOT NULL,  -- 'cpu_high_memory_thrashing'
    fingerprint_l3 VARCHAR(150) NOT NULL,  -- 'cpu_high_memory_thrashing_python'
    
    resource_type VARCHAR(20) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    root_cause VARCHAR(50),
    process_category VARCHAR(20),  -- 'python', 'database', 'web_server', 'system', 'other'
    
    action VARCHAR(100) NOT NULL,
    parameters JSONB,
    confidence FLOAT,
    followed_vic20 BOOLEAN DEFAULT FALSE,
    
    success BOOLEAN NOT NULL,
    improvement JSONB,
    what_worked TEXT,
    what_failed TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for hierarchical querying
    INDEX idx_fingerprint_l3 (fingerprint_l3),
    INDEX idx_fingerprint_l2 (fingerprint_l2),
    INDEX idx_fingerprint_l1 (fingerprint_l1),
    INDEX idx_agent_action (agent_name, action),
    INDEX idx_success (success),
    INDEX idx_process_category (process_category),
    INDEX idx_created (created_at)
);
```

---

## Integration Points

### 1. VIC-20 → Terry Communication
**Update:** `distributed_vic20.py` to pass full metrics

```python
# OLD (current)
coordination_request = {
    'resource_type': 'cpu',
    'current_value': 85.2,
    'threshold': 80.0,
    'severity': 'high',
    'recommendation': {...}
}

# NEW (agentic)
coordination_request = {
    'resource_type': 'cpu',
    'current_value': 85.2,
    'threshold': 80.0,
    'severity': 'high',
    'recommendation': {...},
    'full_metrics': metrics,  # THE WHOLE PAYLOAD
    'triage_decision': triage_result
}
```

### 2. Terry's New handle_coordination
```python
async def handle_coordination(self, coordination_request: Dict[str, Any]):
    """
    Terry v2 - Agentic decision-making with full context.
    """
    # 1. PERCEIVE
    context = await self.perception.perceive(coordination_request)
    
    # 2. REASON
    reasoning = await self.reasoning.reason(context)
    
    # 3. SELECT ACTION
    decision = await self.action_selection.select_action(reasoning, context)
    
    # 4. EXECUTE
    result = await self._execute_action(decision)
    
    # 5. LEARN
    learning = await self.learning.learn(context, reasoning, decision, result)
    
    # 6. REPORT
    await self._report_to_vic20(result, decision, learning)
    
    return result
```

---

## Testing Strategy

### 1. Unit Tests
- Test each layer independently
- Mock dependencies
- Verify data structures

### 2. Integration Tests
- Full perception → reasoning → action → learning cycle
- Real metrics, real decisions
- Verify PostgreSQL writes

### 3. Learning Verification
- Create similar situations
- Verify Terry remembers past successes
- Verify confidence adjustments
- Verify override rate updates

### 4. Personality Preservation
- Verify shell spins on action execution
- Verify meth-fueled bias toward cache clears
- Verify personality metrics update

---

## Success Criteria

✅ **Terry can perceive:** Access full metrics, not just summaries  
✅ **Terry can reason:** Identify root causes, not just symptoms  
✅ **Terry can choose:** Select from multiple actions dynamically  
✅ **Terry can learn:** Remember what works, adjust confidence  
✅ **Terry has personality:** Meth-fueled bias preserved  
✅ **No fake data:** All decisions based on real metrics  
✅ **No hardcoded rules:** Actions chosen by reasoning, not if/else  

---

## Next Steps

1. Implement `TerryPerception` class
2. Implement `TerryReasoning` class
3. Implement `TerryActionSelection` class
4. Implement `TerryLearning` class
5. Create database migration for `agent_learning_records`
6. Update `distributed_meth_snail.py` to use new system
7. Update VIC-20 to pass full metrics
8. Test with real system load
9. Verify learning over multiple cycles
10. Apply pattern to Hamsters and QSP

**This is the blueprint. Terry v2 will think for real.**
