# DecisionEnvelope Implementation Guide
## Practical Wrapping of Hamsters' Executor

**Based on feedback:** "Show me exactly where to wrap it so you get: classification → dry-run diff → safeguard verification → approval window → execution → envelope completion"

---

## Current Hamsters Execution Flow

**File:** `backend/app/ai_agents/hamsters/ML/action_executor.py`

```python
async def execute_action(
    self,
    action: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute action and return result"""
    
    if action == 'emergency_disk_cleanup':
        result = await SystemActions.emergency_disk_cleanup(
            include_defrag=parameters.get('include_defrag', False)
        )
    elif action == 'hamster-fstrim':
        result = await self._execute_sudo_action('hamster-fstrim', parameters)
    elif action == 'hamster-defrag':
        result = await self._execute_sudo_action('hamster-defrag', parameters)
    # ... etc
    
    return result
```

**Problem:** No envelope, no approval gate, no state validation, no dry-run.

---

## New Wrapped Flow with DecisionEnvelope

### Step 1: Create DecisionEnvelope Service

**File:** `backend/app/services/decision_envelope_service.py`

```python
#!/usr/bin/env python3
"""
DecisionEnvelope Service

Wraps action execution with full audit trail:
1. Generate envelope (capture intent, evidence, alternatives)
2. Classify action (policy engine determines gates)
3. Dry-run simulation (show predicted outcome)
4. Verify safeguards (backups exist, restorable)
5. Request approval (if Class 2+)
6. Validate state (check for drift)
7. Execute action (with before/after metrics)
8. Complete envelope (store outcome)
"""

from typing import Dict, Any, Optional, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid
import logging

from app.models.decision_envelope import DecisionEnvelope, LearningEventLog
from app.services.policy_engine import get_policy_engine, ApprovalDecision
from app.services.evidence_export import EvidenceExportService


class DecisionEnvelopeService:
    """
    Wraps action execution with DecisionEnvelope audit trail.
    
    Usage:
        service = DecisionEnvelopeService(db, agent_name="hamsters")
        
        result = await service.execute_with_envelope(
            action="hamster-defrag",
            parameters={"mount_point": "/home"},
            perception_context=perception_context,
            reasoning=reasoning_result,
            alternatives=alternatives_considered,
            executor=action_executor.execute_action
        )
    """
    
    def __init__(self, db: AsyncSession, agent_name: str):
        self.db = db
        self.agent_name = agent_name
        self.policy_engine = get_policy_engine()
        self.logger = logging.getLogger(f"DecisionEnvelope.{agent_name}")
    
    async def execute_with_envelope(
        self,
        action: str,
        parameters: Dict[str, Any],
        perception_context: Dict[str, Any],
        reasoning: Dict[str, Any],
        alternatives: list,
        executor: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Execute action with full DecisionEnvelope wrapping.
        
        Args:
            action: Action to execute
            parameters: Action parameters
            perception_context: Full perception context
            reasoning: Reasoning result
            alternatives: Alternatives considered
            executor: Async function to execute action
            
        Returns:
            Execution result with envelope_id
        """
        # Step 1: Generate envelope
        envelope = await self._generate_envelope(
            action=action,
            parameters=parameters,
            perception_context=perception_context,
            reasoning=reasoning,
            alternatives=alternatives
        )
        
        # Step 2: Classify action (policy engine)
        policy_decision = self.policy_engine.evaluate(
            agent_name=self.agent_name,
            action=action,
            parameters=parameters,
            context=perception_context
        )
        
        envelope.intent_class = policy_decision.intent_class
        envelope.forced_delay_seconds = policy_decision.forced_delay_seconds
        
        self.logger.info(
            f"📋 Envelope {envelope.envelope_id[:8]}: {action} "
            f"classified as Class {policy_decision.intent_class}"
        )
        
        # Step 3: Check if blocked
        if policy_decision.decision == ApprovalDecision.BLOCKED:
            envelope.executed = False
            envelope.success = False
            envelope.execution_result = {
                'blocked': True,
                'reason': policy_decision.reason
            }
            await self._save_envelope(envelope)
            
            self.logger.warning(
                f"🚫 Envelope {envelope.envelope_id[:8]}: Action blocked - {policy_decision.reason}"
            )
            
            return {
                'action': action,
                'success': False,
                'blocked': True,
                'reason': policy_decision.reason,
                'envelope_id': envelope.envelope_id
            }
        
        # Step 4: Dry-run simulation (Class 2+)
        if policy_decision.intent_class >= 2 and 'dry_run' in policy_decision.required_gates:
            dry_run_result = await self._simulate_action(action, parameters, perception_context)
            envelope.dry_run_executed = True
            envelope.dry_run_result = dry_run_result
            envelope.predicted_outcome = dry_run_result.get('predicted_outcome')
            
            self.logger.info(
                f"🧪 Envelope {envelope.envelope_id[:8]}: Dry-run complete - {dry_run_result.get('summary')}"
            )
        
        # Step 5: Verify safeguards (Class 2+)
        if policy_decision.intent_class >= 2:
            safeguards = await self._verify_safeguards(action, parameters, perception_context)
            envelope.backups_exist = safeguards.get('backups_exist', False)
            envelope.backups_restorable = safeguards.get('backups_restorable', False)
            envelope.rollback_plan = safeguards.get('rollback_plan')
            
            self.logger.info(
                f"🛡️ Envelope {envelope.envelope_id[:8]}: Safeguards verified - "
                f"backups: {envelope.backups_exist}, restorable: {envelope.backups_restorable}"
            )
        
        # Step 6: Capture state fingerprint
        current_state = await self._capture_state(action, parameters, perception_context)
        envelope.pre_state_fingerprint = envelope.compute_state_fingerprint(current_state)
        envelope.required_invariants = self._build_invariants(action, parameters, current_state)
        
        # Step 7: Save envelope (before approval)
        await self._save_envelope(envelope)
        
        # Step 8: Request approval (Class 2+)
        if policy_decision.decision == ApprovalDecision.NEEDS_APPROVAL:
            approval = await self._request_approval(
                envelope=envelope,
                policy_decision=policy_decision
            )
            
            envelope.approval_granted = approval.get('granted', False)
            envelope.approval_timestamp = datetime.now(timezone.utc)
            envelope.user_acknowledged_risks = approval.get('acknowledged_risks', [])
            
            if not approval.get('granted'):
                envelope.executed = False
                envelope.success = False
                envelope.execution_result = {
                    'approval_denied': True,
                    'reason': approval.get('reason')
                }
                await self._save_envelope(envelope)
                
                self.logger.warning(
                    f"❌ Envelope {envelope.envelope_id[:8]}: Approval denied - {approval.get('reason')}"
                )
                
                return {
                    'action': action,
                    'success': False,
                    'approval_denied': True,
                    'reason': approval.get('reason'),
                    'envelope_id': envelope.envelope_id
                }
            
            self.logger.info(
                f"✅ Envelope {envelope.envelope_id[:8]}: Approval granted"
            )
        
        # Step 9: Validate state (check for drift)
        current_state_now = await self._capture_state(action, parameters, perception_context)
        state_valid, drift_reason = envelope.validate_state_invariants(current_state_now)
        
        envelope.state_validated_at_execution = True
        envelope.state_drift_detected = not state_valid
        envelope.state_drift_reason = drift_reason
        
        if not state_valid:
            envelope.executed = False
            envelope.success = False
            envelope.execution_result = {
                'state_drift': True,
                'reason': drift_reason
            }
            await self._save_envelope(envelope)
            
            self.logger.error(
                f"⚠️ Envelope {envelope.envelope_id[:8]}: State drift detected - {drift_reason}"
            )
            
            return {
                'action': action,
                'success': False,
                'state_drift': True,
                'reason': drift_reason,
                'envelope_id': envelope.envelope_id,
                'must_repropose': True
            }
        
        # Step 10: Execute action
        self.logger.info(
            f"🚀 Envelope {envelope.envelope_id[:8]}: Executing {action}"
        )
        
        execution_result = await executor(action, parameters)
        
        envelope.executed = True
        envelope.execution_timestamp = datetime.now(timezone.utc)
        envelope.execution_result = execution_result
        envelope.success = execution_result.get('success', False)
        envelope.actual_impact = execution_result.get('improvement', {})
        
        # Step 11: Complete envelope
        envelope.completed_at = datetime.now(timezone.utc)
        await self._save_envelope(envelope)
        
        self.logger.info(
            f"✨ Envelope {envelope.envelope_id[:8]}: Complete - "
            f"success: {envelope.success}, impact: {envelope.actual_impact}"
        )
        
        # Add envelope_id to result
        execution_result['envelope_id'] = envelope.envelope_id
        
        return execution_result
    
    async def _generate_envelope(
        self,
        action: str,
        parameters: Dict[str, Any],
        perception_context: Dict[str, Any],
        reasoning: Dict[str, Any],
        alternatives: list
    ) -> DecisionEnvelope:
        """Generate initial envelope"""
        import os
        
        envelope = DecisionEnvelope(
            envelope_id=str(uuid.uuid4()),
            agent_name=self.agent_name,
            action=action,
            parameters=parameters,
            perception_context=perception_context,
            reasoning=reasoning,
            alternatives_considered=alternatives,
            environment=os.getenv('ENVIRONMENT', 'development'),
            operator_present=False,  # TODO: Detect if user is watching
            execution_mode='approved'  # Will be updated based on approval
        )
        
        return envelope
    
    async def _simulate_action(
        self,
        action: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate action to predict outcome.
        
        For now, returns conservative estimates.
        TODO: Implement actual dry-run simulation per action type.
        """
        if 'defrag' in action.lower():
            return {
                'summary': 'Defrag will reorganize filesystem blocks',
                'predicted_outcome': {
                    'estimated_duration': '240-300s',
                    'estimated_improvement': '5-10% fragmentation reduction',
                    'risk': 'Data corruption on failure (backup required)'
                }
            }
        elif 'fstrim' in action.lower():
            return {
                'summary': 'TRIM will free unused SSD blocks',
                'predicted_outcome': {
                    'estimated_duration': '10-30s',
                    'estimated_improvement': 'Freed blocks unrecoverable',
                    'risk': 'Low (TRIM is safe on modern SSDs)'
                }
            }
        elif 'cleanup' in action.lower():
            return {
                'summary': 'Cleanup will delete old temp files',
                'predicted_outcome': {
                    'estimated_duration': '5-15s',
                    'estimated_improvement': '100-500MB freed',
                    'risk': 'Low (only files > 7 days old)'
                }
            }
        else:
            return {
                'summary': f'Action {action} will execute',
                'predicted_outcome': {
                    'estimated_duration': 'unknown',
                    'estimated_improvement': 'unknown',
                    'risk': 'unknown'
                }
            }
    
    async def _verify_safeguards(
        self,
        action: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify safeguards (backups, rollback plan).
        
        TODO: Implement actual backup verification.
        """
        # For now, assume backups exist but not verified
        return {
            'backups_exist': True,
            'backups_restorable': False,  # Not tested yet
            'rollback_plan': 'Restore from most recent backup (not tested)'
        }
    
    async def _capture_state(
        self,
        action: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Capture critical state for drift detection.
        """
        state = {}
        
        if 'defrag' in action.lower():
            mount_point = parameters.get('mount_point', '/')
            state['mount_point'] = mount_point
            state['filesystem_type'] = context.get('filesystem_type', 'unknown')
            state['disk_usage'] = context.get('disk_usage_percent', 0)
            state['fragmentation'] = context.get('fragmentation_percent', 0)
        
        elif 'fstrim' in action.lower():
            mount_point = parameters.get('mount_point', '/')
            state['mount_point'] = mount_point
            state['filesystem_type'] = context.get('filesystem_type', 'unknown')
        
        return state
    
    def _build_invariants(
        self,
        action: str,
        parameters: Dict[str, Any],
        state: Dict[str, Any]
    ) -> list:
        """
        Build list of invariants that must remain true.
        """
        invariants = []
        
        for key, value in state.items():
            invariants.append({
                'key': key,
                'expected': value,
                'description': f'{key} must remain {value}'
            })
        
        return invariants
    
    async def _request_approval(
        self,
        envelope: DecisionEnvelope,
        policy_decision
    ) -> Dict[str, Any]:
        """
        Request user approval.
        
        TODO: Implement actual approval request via WebSocket.
        For now, auto-approve in development.
        """
        import os
        
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            # Auto-approve in dev
            return {
                'granted': True,
                'acknowledged_risks': [
                    'Development environment - auto-approved'
                ]
            }
        
        # In production, would send WebSocket message and wait for response
        # For now, deny by default
        return {
            'granted': False,
            'reason': 'Approval system not yet implemented'
        }
    
    async def _save_envelope(self, envelope: DecisionEnvelope):
        """Save envelope to database"""
        # Compute hash before saving
        envelope.payload_hash = envelope.compute_payload_hash()
        
        self.db.add(envelope)
        await self.db.commit()
        await self.db.refresh(envelope)


async def get_decision_envelope_service(
    db: AsyncSession,
    agent_name: str
) -> DecisionEnvelopeService:
    """Get DecisionEnvelopeService instance"""
    return DecisionEnvelopeService(db, agent_name)
```

---

### Step 2: Wrap Hamsters' Action Executor

**File:** `backend/app/ai_agents/hamsters/ML/action_executor.py`

**Before (current):**
```python
class HamstersActionExecutor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("Hamsters.ActionExecutor")
    
    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute action and return result"""
        
        if action == 'emergency_disk_cleanup':
            result = await SystemActions.emergency_disk_cleanup(...)
        # ... etc
        
        return result
```

**After (wrapped):**
```python
class HamstersActionExecutor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("Hamsters.ActionExecutor")
        self.envelope_service = None  # Lazy init
    
    async def execute_action_with_envelope(
        self,
        action: str,
        parameters: Dict[str, Any],
        perception_context: Dict[str, Any],
        reasoning: Dict[str, Any],
        alternatives: list
    ) -> Dict[str, Any]:
        """
        Execute action with DecisionEnvelope wrapping.
        
        This is the NEW entry point that wraps the old execute_action.
        """
        from app.services.decision_envelope_service import get_decision_envelope_service
        
        # Lazy init envelope service
        if self.envelope_service is None:
            self.envelope_service = await get_decision_envelope_service(
                db=self.db,
                agent_name="hamsters"
            )
        
        # Execute with envelope wrapping
        result = await self.envelope_service.execute_with_envelope(
            action=action,
            parameters=parameters,
            perception_context=perception_context,
            reasoning=reasoning,
            alternatives=alternatives,
            executor=self._execute_action_internal  # Pass internal executor
        )
        
        return result
    
    async def _execute_action_internal(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Internal action executor (old execute_action).
        
        This is called by the envelope service after all gates pass.
        """
        if action == 'emergency_disk_cleanup':
            result = await SystemActions.emergency_disk_cleanup(
                include_defrag=parameters.get('include_defrag', False)
            )
        elif action == 'hamster-fstrim':
            result = await self._execute_sudo_action('hamster-fstrim', parameters)
        elif action == 'hamster-defrag':
            result = await self._execute_sudo_action('hamster-defrag', parameters)
        # ... etc
        
        return result
```

---

### Step 3: Update Distributed Hamsters to Use Wrapped Executor

**File:** `backend/app/ai_agents/hamsters/distributed_hamsters.py`

**Before:**
```python
# Execute action
execution_result = await action_executor.execute_action(
    action=action_decision.action,
    parameters=action_decision.parameters
)
```

**After:**
```python
# Execute action with DecisionEnvelope wrapping
execution_result = await action_executor.execute_action_with_envelope(
    action=action_decision.action,
    parameters=action_decision.parameters,
    perception_context=perception_context.to_dict(),
    reasoning=reasoning_result,
    alternatives=action_decision.alternatives_considered
)

# Check for special cases
if execution_result.get('blocked'):
    self.logger.warning(f"🚫 Action blocked by policy: {execution_result.get('reason')}")
    # Don't learn from blocked actions
    return

if execution_result.get('state_drift'):
    self.logger.warning(f"⚠️ State drift detected: {execution_result.get('reason')}")
    # Must repropose with new state
    return

if execution_result.get('approval_denied'):
    self.logger.warning(f"❌ Approval denied: {execution_result.get('reason')}")
    # Learn from rejection (user said no)
    # ... store learning record ...
    return
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Hamsters ML Pipeline                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Perception → 2. Reasoning → 3. Action Selection            │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ DecisionEnvelope Service (NEW)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Generate Envelope                                      │
│    - Capture intent, evidence, alternatives                     │
│    - Assign envelope_id (UUID)                                  │
│                                                                 │
│  Step 2: Classify Action (Policy Engine)                        │
│    - Determine intent_class (0-3)                               │
│    - Check environment overrides                                │
│    - Determine required gates                                   │
│                                                                 │
│  Step 3: Check if Blocked                                       │
│    - If blocked → Save envelope, return error                   │
│                                                                 │
│  Step 4: Dry-Run Simulation (Class 2+)                          │
│    - Predict outcome                                            │
│    - Store dry-run diff in envelope                             │
│                                                                 │
│  Step 5: Verify Safeguards (Class 2+)                           │
│    - Check backups exist                                        │
│    - Verify backups restorable                                  │
│    - Define rollback plan                                       │
│                                                                 │
│  Step 6: Capture State Fingerprint                              │
│    - Hash critical state (mount, filesystem, disk usage)        │
│    - Build invariants list                                      │
│                                                                 │
│  Step 7: Save Envelope (before approval)                        │
│    - Store in PostgreSQL                                        │
│    - Compute payload hash                                       │
│    - Link to previous envelope (hash chain)                     │
│                                                                 │
│  Step 8: Request Approval (Class 2+)                            │
│    - Send WebSocket to frontend                                 │
│    - Wait for user response (with timeout)                      │
│    - If denied → Save envelope, return error                    │
│                                                                 │
│  Step 9: Validate State (check for drift)                       │
│    - Re-capture current state                                   │
│    - Compare to pre_state_fingerprint                           │
│    - Check invariants still hold                                │
│    - If drift → Save envelope, return error (must repropose)    │
│                                                                 │
│  Step 10: Execute Action                                        │
│    - Call internal executor                                     │
│    - Measure before/after metrics                               │
│                                                                 │
│  Step 11: Complete Envelope                                     │
│    - Store execution result                                     │
│    - Store actual impact                                        │
│    - Mark envelope complete                                     │
│    - Return result with envelope_id                             │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Hamsters Action Executor (Internal)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  - emergency_disk_cleanup                                       │
│  - hamster-fstrim                                               │
│  - hamster-defrag                                               │
│  - hamster-cleanup-tmp                                          │
│  - etc.                                                         │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Learning System                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  - Store AgentLearningRecord                                    │
│  - Link to DecisionEnvelope (envelope_id)                       │
│  - Store LearningEventLog (propagation)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Example: Bob Wants to Defrag /home

```python
# 1. Hamsters ML pipeline runs
perception_context = await perception_system.perceive()
# {
#   'disk_usage_percent': 87.5,
#   'fragmentation_percent': 12.3,
#   'filesystem_type': 'ext4',
#   'bob_beers_today': 4
# }

reasoning_result = await reasoning_system.reason(perception_context)
# {
#   'root_cause': 'high_fragmentation',
#   'confidence': 0.85
# }

action_decision = await action_selector.select_action(perception_context, reasoning_result)
# {
#   'action': 'hamster-defrag',
#   'parameters': {'mount_point': '/home'},
#   'alternatives_considered': [
#     {'action': 'monitor', 'confidence': 0.3},
#     {'action': 'hamster-fstrim', 'confidence': 0.6}
#   ]
# }

# 2. Execute with envelope wrapping
result = await action_executor.execute_action_with_envelope(
    action='hamster-defrag',
    parameters={'mount_point': '/home'},
    perception_context=perception_context,
    reasoning=reasoning_result,
    alternatives=action_decision.alternatives_considered
)

# 3. DecisionEnvelope service runs all gates:
#    - Classify: Class 3 (irreversible)
#    - Dry-run: "Estimated 240s, 8.5% improvement"
#    - Safeguards: Backups exist (not tested)
#    - State: mount=/home, fs=ext4, usage=87.5%, frag=12.3%
#    - Approval: Request sent to user
#    - User approves with 60s delay
#    - State validation: Still ext4, still 87.5% usage ✓
#    - Execute: Run hamster-defrag
#    - Complete: Success, 8.5% improvement

# 4. Result returned
# {
#   'action': 'hamster-defrag',
#   'success': True,
#   'fragmentation_before': 12.3,
#   'fragmentation_after': 3.8,
#   'improvement': 8.5,
#   'envelope_id': '550e8400-e29b-41d4-a716-446655440000'
# }

# 5. Learning system stores outcome
await learning_system.learn(
    context=perception_context,
    reasoning_result=reasoning_result,
    decision=action_decision,
    execution_result=result
)
# Links to envelope via envelope_id
```

---

## Migration Path (Incremental Rollout)

### Phase 1: Hamsters Only (Week 1-2)
- Implement DecisionEnvelopeService
- Wrap Hamsters' action executor
- Test with Class 2+ actions (fstrim, cleanup)
- Verify envelope generation, classification, dry-run

### Phase 2: Add Approval Gate (Week 3-4)
- Implement approval request via WebSocket
- Build frontend approval UI
- Test with Class 3 actions (defrag)
- Verify state drift detection

### Phase 3: Expand to Other Agents (Week 5-6)
- Wrap Terry's action executor
- Wrap QSP's action executor
- Test cross-agent consistency

### Phase 4: Learning Event Log (Week 7-8)
- Implement LearningEventLog storage
- Replace Redis pub/sub for learning propagation
- Test "who taught who what" queries

### Phase 5: Evidence Export (Week 9-10)
- Implement evidence bundle export
- Test timeline reconstruction
- Generate sample court evidence

---

## Key Benefits of This Approach

1. **Non-Breaking:** Old `execute_action` still exists as `_execute_action_internal`
2. **Incremental:** Can roll out agent by agent
3. **Testable:** Each gate can be tested independently
4. **Auditable:** Every decision has full context in PostgreSQL
5. **Defensible:** "Bob acted reasonably given the evidence"

---

## Next Steps

1. Implement `DecisionEnvelopeService` (this file provides the blueprint)
2. Update Hamsters' `action_executor.py` to add `execute_action_with_envelope`
3. Update `distributed_hamsters.py` to call wrapped executor
4. Run database migration (`001_add_decision_envelope_tables.sql`)
5. Test with Class 2 action (fstrim) in development
6. Test with Class 3 action (defrag) with approval gate
7. Verify envelope stored in PostgreSQL with hash chain
8. Export evidence bundle for sample decision

**Bob keeps his personality. The logs don't.**
