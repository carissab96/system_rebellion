#!/usr/bin/env python3
"""
Terry's Learning System - Remembering What Works

Stores every experience: situation → action → outcome
Builds confidence over time through real results.
Shares learning with The Stick for cross-agent knowledge.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger('TerryLearning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class LearningRecord:
    """What Terry learned from this experience"""
    
    # Hierarchical fingerprints
    fingerprint_l1: str
    fingerprint_l2: str
    fingerprint_l3: str
    
    # Situation
    resource_type: str
    severity: str
    root_cause: str
    process_category: str
    
    # Action
    action: str
    parameters: Dict[str, Any]
    confidence: float
    followed_vic20: bool
    
    # Outcome
    success: bool
    improvement: Dict[str, float]
    
    # Learning
    what_worked: Optional[str] = None
    what_failed: Optional[str] = None
    
    # Personality Behaviors (reactive to real data)
    shell_spins: int = 0
    data_quality_score: float = 1.0
    energy_drink_consumed: bool = False
    hawk_veto: bool = False
    
    # Metadata
    timestamp: str = ""
    agent_name: str = "meth_snail"
    learning_record_id: Optional[str] = None  # Database ID after storage
    storage_success: bool = False  # Whether database storage succeeded


class TerryLearning:
    """
    Terry's learning system - remembering what works.
    
    🐌📚 "I'm getting SMARTER! Every action teaches me something!"
    """
    
    def __init__(self, db_session, agent_state: Dict[str, Any]):
        """
        Initialize learning system.
        
        Args:
            db_session: AsyncSession for database writes
            agent_state: Current agent personality metrics
        """
        self.db = db_session
        self.agent_state = agent_state
        self.logger = logger
        
        self.logger.info("🐌📚 Terry's learning system initialized - ready to learn!")
    
    async def learn(
        self,
        context,
        reasoning_result,
        decision,
        execution_result,
        action_selector=None,
        central_memory_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> LearningRecord:
        """
        Store this experience for future reference.
        
        Success or failure, Terry learns from it.
        
        Args:
            context: PerceptionContext
            reasoning_result: ReasoningResult from reasoning engine
            decision: ActionDecision from action selection
            execution_result: ExecutionResult from action execution
            central_memory_id: Link to CentralMemoryBank (for learned thresholds)
            user_id: User ID for learning event emissions
            
        Returns:
            LearningRecord that was stored
        """
        self.logger.info("🐌📚 Terry learning from this experience...")
        
        # 1. Generate fingerprints
        from app.ai_agents.meth_snail.ML.situation_fingerprint import SituationFingerprint
        
        fingerprints = SituationFingerprint.generate(
            resource_type=context.resource_type,
            severity=context.severity,
            root_cause=reasoning_result.root_cause,
            full_metrics=context.full_metrics
        )
        
        # 2. Calculate improvement
        improvement = self._calculate_improvement(
            execution_result.get('metrics_before', {}),
            execution_result.get('metrics_after', {}),
            context.resource_type
        )
        
        # 3. Determine success
        action_succeeded = execution_result.get('success', False)
        
        # Check if ANY metric improved (not just the trigger resource)
        # Some actions help different resources or have indirect benefits
        any_metric_improved = any(delta < -1.0 for delta in improvement.values())  # -1% threshold
        
        # Primary resource improvement (the one that triggered the alert)
        primary_improved = improvement.get(context.resource_type, 0) < -0.5  # -0.5% threshold
        
        # Success if action executed AND (primary improved OR any metric improved significantly)
        overall_success = action_succeeded and (primary_improved or any_metric_improved)
        
        # Log the decision logic for debugging
        if action_succeeded and not overall_success:
            self.logger.warning(
                f"   ⚠️ Action {decision.action} succeeded but no metrics improved enough. "
                f"Primary ({context.resource_type}): {improvement.get(context.resource_type, 0):.2f}%, "
                f"All improvements: {improvement}"
            )
        
        # 4. Create learning record (with personality behaviors!)
        record = LearningRecord(
            fingerprint_l1=fingerprints['level_1'],
            fingerprint_l2=fingerprints['level_2'],
            fingerprint_l3=fingerprints['level_3'],
            resource_type=context.resource_type,
            severity=context.severity,
            root_cause=reasoning_result.root_cause,
            process_category=fingerprints['process_category'],
            action=decision.action,
            parameters=decision.parameters,
            confidence=decision.confidence,
            followed_vic20=decision.followed_vic20,
            success=overall_success,
            improvement=improvement,
            what_worked=decision.action if overall_success else None,
            what_failed=decision.action if not overall_success else None,
            # Personality behaviors from this experience
            shell_spins=context.shell_spin_count,
            data_quality_score=context.data_quality_score,
            energy_drink_consumed=decision.energy_drink_consumed,
            hawk_veto=decision.hawk_veto,
            timestamp=utc_now().isoformat(),
            agent_name='meth_snail'
        )
        
        # 5. Store in database (returns central_memory_id)
        storage_success, central_memory_id = await self._store_learning(record)
        record.storage_success = storage_success
        
        # 6. NEW: Record in learned thresholds and action effectiveness systems
        if action_selector and central_memory_id:
            try:
                # Get metrics
                metrics_before = execution_result.get('metrics_before', {})
                metrics_after = execution_result.get('metrics_after', {})
                
                # Record in action effectiveness (emits learning event)
                # Skip monitor/escalate — they produce synthetic outcomes that would
                # bias the effectiveness model toward actions that did nothing.
                # These are observation/delegation actions, not interventions.
                INTERVENTION_ACTIONS = {
                    a for a in action_selector.action_effectiveness.ALL_ACTIONS
                    if a not in ('monitor', 'escalate')
                }
                if decision.action in INTERVENTION_ACTIONS:
                    # alternatives_considered may be a list of strings (from action_selection.py)
                    # or a list of dicts — normalise to strings at the call site
                    alts = decision.alternatives_considered or []
                    other_actions = [
                        a if isinstance(a, str) else a.get('action', '')
                        for a in alts
                    ]
                    await action_selector.action_effectiveness.record_outcome(
                        action=decision.action,
                        pre_metrics=metrics_before,
                        post_metrics=metrics_after,
                        severity=self._calculate_severity_score(context.severity),
                        success=overall_success,
                        other_actions_considered=other_actions,
                        central_memory_id=central_memory_id,
                        user_id=user_id
                    )
                else:
                    self.logger.debug(
                        f"   ⏭️ Skipping effectiveness record for '{decision.action}' "
                        f"(observation/delegation action — not an intervention)"
                    )
                
                # Record in learned thresholds if threshold was crossed (emits learning event)
                if hasattr(decision, 'threshold_crossed') and decision.threshold_crossed:
                    primary_metric = f"{context.resource_type}_usage"
                    await action_selector.learned_thresholds.record_outcome(
                        metric_name=primary_metric,
                        metric_value=metrics_before.get(primary_metric, 0.0),
                        threshold_level=decision.threshold_crossed,
                        action_taken=decision.action,
                        outcome={
                            'success': overall_success,
                            'system_state': metrics_before,
                            'resolved_naturally': False,
                            'became_critical_before_action': False,
                            'rapid_escalation': False
                        },
                        context={
                            'time_of_day': utc_now().hour,
                            'day_of_week': utc_now().weekday(),
                            'root_cause': reasoning_result.root_cause
                        },
                        user_id=user_id
                    )
                
                self.logger.debug("   ✓ Recorded in learned thresholds and action effectiveness systems")
            except Exception as e:
                self.logger.error(f"   💥 Failed to record in learned systems: {e}")
        
        # 7. Update agent state
        await self._update_agent_state(record, decision)
        
        # 8. Share with The Stick
        await self._share_with_stick(record)
        
        if overall_success:
            self.logger.info(f"   ✓ SUCCESS! {decision.action} worked. Improvement: {improvement}")
        else:
            self.logger.info(f"   ✗ FAILURE. {decision.action} didn't work. Learning from it.")
        
        return record
    
    def _calculate_severity_score(self, severity_str: str) -> float:
        """Convert severity string to numeric score for learned systems.
        
        NOTE: This is intentionally duplicated in action_selection.py as
        _severity_to_float(). Both maps MUST stay in sync. If you change
        the severity vocabulary here, change it there too.
        """
        severity_map = {
            'low': 0.3,
            'moderate': 0.5,
            'high': 0.7,
            'critical': 0.9,
            'emergency': 1.0
        }
        return severity_map.get(severity_str.lower(), 0.5)
    
    def _calculate_improvement(
        self,
        metrics_before: Dict[str, Any],
        metrics_after: Dict[str, Any],
        resource_type: str
    ) -> Dict[str, float]:
        """
        Calculate metrics improvement (delta).
        
        Negative values = improvement (usage went down)
        Positive values = degradation (usage went up)
        
        Args:
            metrics_before: Metrics before action
            metrics_after: Metrics after action
            resource_type: Which resource to focus on
            
        Returns:
            Dictionary with deltas for each metric
        """
        improvement = {}
        
        # Calculate deltas for key metrics
        metrics_to_check = ['cpu_usage', 'memory_usage', 'disk_usage']
        
        for metric in metrics_to_check:
            before = metrics_before.get(metric, 0)
            after = metrics_after.get(metric, 0)
            delta = after - before
            improvement[metric] = delta
        
        return improvement
    
    async def _store_learning(self, record: LearningRecord) -> tuple[bool, Optional[str]]:
        """
        Store learning record in database.
        
        Args:
            record: LearningRecord to store
            
        Returns:
            Tuple of (success: bool, central_memory_id: Optional[str])
        """
        try:
            import uuid
            from app.models.agent_learning import AgentLearningRecord
            from app.models.agent_memory_banks import CentralMemoryBank
            
            # Generate central_memory_id
            central_memory_id = str(uuid.uuid4())
            
            # Store in AgentLearningRecord (agent-specific table)
            db_record = AgentLearningRecord(
                agent_name=record.agent_name,
                fingerprint_l1=record.fingerprint_l1,
                fingerprint_l2=record.fingerprint_l2,
                fingerprint_l3=record.fingerprint_l3,
                resource_type=record.resource_type,
                severity=record.severity,
                root_cause=record.root_cause,
                process_category=record.process_category,
                action=record.action,
                parameters=record.parameters,
                confidence=record.confidence,
                followed_vic20=record.followed_vic20,
                success=record.success,
                improvement=record.improvement,
                what_worked=record.what_worked,
                what_failed=record.what_failed
            )
            
            self.db.add(db_record)
            await self.db.flush()  # Get the ID without committing
            
            # Set the ID on the record so we can emit it
            record.learning_record_id = str(db_record.id)
            
            # Also store in CentralMemoryBank (cross-agent table)
            central_memory = CentralMemoryBank(
                memory_id=central_memory_id,
                agent_name=record.agent_name,
                event_type="learning_outcome",
                title=f"{record.action} → {'SUCCESS' if record.success else 'FAILURE'}",
                description=f"Action: {record.action}, Root cause: {record.root_cause}",
                details={
                    'fingerprint_l1': record.fingerprint_l1,
                    'fingerprint_l2': record.fingerprint_l2,
                    'fingerprint_l3': record.fingerprint_l3,
                    'action': record.action,
                    'success': record.success,
                    'improvement': record.improvement,
                    'followed_vic20': record.followed_vic20,
                    'energy_drink_consumed': record.energy_drink_consumed,
                    'hawk_veto': record.hawk_veto,
                    'learning_record_id': str(db_record.id)
                },
                priority=3 if record.success else 4,
                occurred_at=utc_now()
            )
            
            self.db.add(central_memory)
            await self.db.flush()  # commit happens at the distributed boundary (get_async_db context)
            
            self.logger.debug(f"   ✓ Learning stored: AgentLearningRecord (ID: {db_record.id}), CentralMemoryBank (ID: {central_memory_id})")
            return True, central_memory_id
            
        except Exception as e:
            self.logger.error(f"   💥 Failed to store learning record: {str(e)}")
            await self.db.rollback()
            return False, None
    
    async def _update_agent_state(self, record: LearningRecord, decision):
        """
        Update Terry's agent state based on learning.
        
        Updates override_success_rate if Terry overrode VIC-20.
        
        Args:
            record: LearningRecord
            decision: ActionDecision
        """
        if not decision.followed_vic20:
            # Terry overrode VIC-20 - update his override success rate
            current_rate = self.agent_state.get('override_success_rate', 0.5)
            
            # Simple moving average with weight on recent results
            if record.success:
                new_rate = current_rate * 0.9 + 0.1  # Increase by 10%
            else:
                new_rate = current_rate * 0.9  # Decrease by 10%
            
            # Clamp to [0.1, 0.95]
            new_rate = max(0.1, min(0.95, new_rate))
            
            self.agent_state['override_success_rate'] = new_rate
            
            self.logger.debug(f"   ✓ Override success rate: {current_rate:.2f} → {new_rate:.2f}")
    
    async def _share_with_stick(self, record: LearningRecord):
        """
        Share learning with The Stick via DECISION_LOG.
        
        Every learning outcome — success or failure — is auditable.
        The Stick aggregates these across all agents.
        
        Args:
            record: LearningRecord to share
        """
        try:
            from app.services.agent_insight_emitter import emit_agent_insight
            
            await emit_agent_insight(
                from_agent=record.agent_name,
                to_agent='the_stick',
                action='learning_outcome',
                reasoning=f"{record.action} → {'SUCCESS' if record.success else 'FAILURE'} | root_cause: {record.root_cause}",
                context={
                    'decision_type': 'learning_outcome',
                    'action': record.action,
                    'success': record.success,
                    'root_cause': record.root_cause,
                    'fingerprint_l1': record.fingerprint_l1,
                    'fingerprint_l2': record.fingerprint_l2,
                    'fingerprint_l3': record.fingerprint_l3,
                    'improvement': record.improvement,
                    'followed_vic20': record.followed_vic20,
                    'energy_drink_consumed': record.energy_drink_consumed,
                    'hawk_veto': record.hawk_veto,
                    'learning_record_id': record.learning_record_id,
                    'timestamp': record.timestamp,
                }
            )
            
            self.logger.debug(
                f"   📤 Shared with The Stick: {record.action} "
                f"{'succeeded' if record.success else 'failed'} "
                f"(record: {record.learning_record_id})"
            )
            
        except Exception as e:
            self.logger.error(f"   💥 Failed to share with The Stick: {str(e)}")
    
    def summarize_learning(self, record: LearningRecord) -> str:
        """
        Generate human-readable summary of what was learned.
        
        Args:
            record: LearningRecord to summarize
            
        Returns:
            Natural language summary
        """
        parts = []
        
        parts.append("🐌📚 TERRY LEARNED:")
        parts.append("")
        parts.append(f"SITUATION:")
        parts.append(f"  {record.fingerprint_l3}")
        parts.append(f"  Root cause: {record.root_cause}")
        parts.append("")
        parts.append(f"ACTION TAKEN:")
        parts.append(f"  {record.action}")
        if record.parameters:
            parts.append(f"  Parameters: {record.parameters}")
        parts.append(f"  Confidence: {record.confidence:.0%}")
        parts.append("")
        parts.append(f"OUTCOME:")
        if record.success:
            parts.append(f"  ✓ SUCCESS!")
            parts.append(f"  What worked: {record.what_worked}")
        else:
            parts.append(f"  ✗ FAILURE")
            parts.append(f"  What failed: {record.what_failed}")
        parts.append("")
        parts.append(f"IMPROVEMENT:")
        for metric, delta in record.improvement.items():
            if delta < 0:
                parts.append(f"  ✓ {metric}: {delta:.1f}% (improved)")
            elif delta > 0:
                parts.append(f"  ✗ {metric}: +{delta:.1f}% (degraded)")
            else:
                parts.append(f"  - {metric}: no change")
        
        return "\n".join(parts)


class ConfidenceCalculator:
    """
    Calculate confidence using Bayesian base + adaptive adjustments.
    
    🐌🎯 "My confidence grows with experience!"
    """
    
    @staticmethod
    def calculate(
        historical_outcomes: list,
        action: str,
        context=None
    ) -> float:
        """
        Hybrid confidence calculation:
        - Bayesian base (statistically sound)
        - Novelty boost (fast learning on new situations)
        - Context adjustments (VIC-20 agreement, personality)
        
        Args:
            historical_outcomes: List of past LearningRecords
            action: Action being considered
            context: Optional PerceptionContext for context adjustments
            
        Returns:
            Confidence score (0.1 - 0.95)
        """
        if not historical_outcomes:
            return 0.5  # Neutral starting point
        
        # 1. BAYESIAN BASE
        successes = sum(1 for r in historical_outcomes if r.get('success', False))
        failures = len(historical_outcomes) - successes
        
        # Beta distribution: alpha=successes+1, beta=failures+1
        base_confidence = (successes + 1) / (successes + failures + 2)
        
        # 2. NOVELTY BOOST
        # More data = less novelty = smaller boost
        novelty_score = 1.0 / (1.0 + len(historical_outcomes))
        novelty_boost = novelty_score * 0.2  # Up to +0.2 for novel situations
        
        # 3. CONTEXT ADJUSTMENTS
        context_boost = 0.0
        
        if context:
            # VIC-20 agreement signal
            vic20_action = context.vic20_recommendation.get('action')
            if vic20_action == action:
                # Check if VIC-20 agreements tend to succeed
                vic20_agreements = sum(
                    1 for r in historical_outcomes 
                    if r.get('success') and r.get('followed_vic20')
                )
                if vic20_agreements > 0:
                    agreement_rate = vic20_agreements / successes if successes > 0 else 0
                    context_boost += agreement_rate * 0.1  # Up to +0.1
        
        # 4. COMBINE
        final_confidence = base_confidence + novelty_boost + context_boost
        
        # 5. BOUND [0.1, 0.95]
        # Never 0.0 (always willing to try)
        # Never 1.0 (never overconfident)
        return max(0.1, min(0.95, final_confidence))
