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
    
    # Metadata
    timestamp: str = ""
    agent_name: str = "meth_snail"


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
        execution_result
    ) -> LearningRecord:
        """
        Store this experience for future reference.
        
        Success or failure, Terry learns from it.
        
        Args:
            context: PerceptionContext
            reasoning_result: ReasoningResult from reasoning engine
            decision: ActionDecision from action selection
            execution_result: ExecutionResult from action execution
            
        Returns:
            LearningRecord that was stored
        """
        self.logger.info("🐌📚 Terry learning from this experience...")
        
        # 1. Generate fingerprints
        from app.ai_agents.meth_snail.situation_fingerprint import SituationFingerprint
        
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
        metrics_improved = improvement.get(context.resource_type, 0) < 0  # Negative = improvement
        overall_success = action_succeeded and metrics_improved
        
        # 4. Create learning record
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
            timestamp=utc_now().isoformat(),
            agent_name='meth_snail'
        )
        
        # 5. Store in database
        await self._store_learning(record)
        
        # 6. Update agent state
        await self._update_agent_state(record, decision)
        
        # 7. Share with The Stick
        await self._share_with_stick(record)
        
        if overall_success:
            self.logger.info(f"   ✓ SUCCESS! {decision.action} worked. Improvement: {improvement}")
        else:
            self.logger.info(f"   ✗ FAILURE. {decision.action} didn't work. Learning from it.")
        
        return record
    
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
    
    async def _store_learning(self, record: LearningRecord):
        """
        Store learning record in database.
        
        Args:
            record: LearningRecord to store
        """
        try:
            from app.models.agent_learning import AgentLearningRecord
            
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
            await self.db.commit()
            
            self.logger.debug(f"   ✓ Learning record stored in database (ID: {db_record.id})")
            
        except Exception as e:
            self.logger.error(f"   💥 Failed to store learning record: {str(e)}")
            await self.db.rollback()
    
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
        Share learning with The Stick for cross-agent knowledge.
        
        The Stick will aggregate learning from all Terry instances
        and make it available to other agents.
        
        Args:
            record: LearningRecord to share
        """
        try:
            # TODO: Implement when The Stick's learning hub is ready
            # For now, just log that we would share
            self.logger.debug(f"   📤 Would share with The Stick: {record.action} {'succeeded' if record.success else 'failed'}")
            
        except Exception as e:
            self.logger.warning(f"   ⚠️ Failed to share with The Stick: {str(e)}")
    
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
        
        # Personality bias (Terry loves cache clears)
        if action == 'emergency_cache_clear':
            context_boost += 0.05  # Meth-fueled bias
        
        # 4. COMBINE
        final_confidence = base_confidence + novelty_boost + context_boost
        
        # 5. BOUND [0.1, 0.95]
        # Never 0.0 (always willing to try)
        # Never 1.0 (never overconfident)
        return max(0.1, min(0.95, final_confidence))
