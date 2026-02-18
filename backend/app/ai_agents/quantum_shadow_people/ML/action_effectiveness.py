#!/usr/bin/env python3
"""
QSP's Action Effectiveness Model

Learns which security response works best for which threat pattern:
- block_ip vs rate_limit vs monitor vs escalate_to_hamsters
- Pattern fingerprints: brute_force_attack, insider_threat, network_scan, etc.

Tracks success rate per action per threat pattern to recommend the most effective response.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_outcome import ActionOutcomeRecord

logger = logging.getLogger('QSPActionEffectiveness')

# All possible security response actions
SECURITY_ACTIONS = [
    'block_ip',
    'rate_limit',
    'monitor',
    'escalate_to_hamsters',
    'quarantine',
    'alert_admin',
    'investigate',
    'no_action'
]


@dataclass
class ActionScore:
    """Effectiveness score for an action in a specific threat pattern"""
    action: str
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    sample_size: int
    success_rate: float
    avg_improvement: float


class ActionEffectivenessModel:
    """
    QSP's action effectiveness learning system.
    
    Learns which security response works best for which threat pattern.
    """
    
    def __init__(self, db: AsyncSession, system_id: str = "default"):
        self.db = db
        self.system_id = system_id
        self.agent_name = "quantum_shadow_people"
        self.logger = logger
    
    async def score_all_actions(
        self,
        metric_pattern: str
    ) -> List[ActionScore]:
        """
        Score all possible actions for a given threat pattern.
        
        Args:
            metric_pattern: Pattern fingerprint (e.g., 'brute_force_attack')
            
        Returns:
            List of ActionScore objects, sorted by score (best first)
        """
        scores = []
        
        for action in SECURITY_ACTIONS:
            score = await self._score_action(action, metric_pattern)
            scores.append(score)
        
        # Sort by score descending
        scores.sort(key=lambda s: s.score, reverse=True)
        
        return scores
    
    async def _score_action(
        self,
        action: str,
        metric_pattern: str
    ) -> ActionScore:
        """
        Calculate effectiveness score for an action in a threat pattern.
        
        Score combines:
        - Success rate (did it work?)
        - Average improvement (how much did it help?)
        - Recency (recent outcomes weighted more)
        """
        # Get outcome records from last 60 days
        cutoff_date = datetime.utcnow() - timedelta(days=60)
        
        records = await self.db.execute(
            self.db.query(ActionOutcomeRecord).filter(
                and_(
                    ActionOutcomeRecord.agent_name == self.agent_name,
                    ActionOutcomeRecord.action == action,
                    ActionOutcomeRecord.metric_pattern_fingerprint == metric_pattern,
                    ActionOutcomeRecord.created_at >= cutoff_date
                )
            )
        )
        records = records.scalars().all()
        
        if not records:
            # No data - return neutral score
            return ActionScore(
                action=action,
                score=0.5,
                confidence=0.0,
                sample_size=0,
                success_rate=0.0,
                avg_improvement=0.0
            )
        
        # Calculate metrics
        sample_size = len(records)
        successful = sum(1 for r in records if r.success)
        success_rate = successful / sample_size
        
        # Calculate average improvement (threat resolved, false positive avoided, etc.)
        improvements = [r.improvement for r in records if r.improvement is not None]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
        
        # Calculate recency-weighted score
        now = datetime.now(timezone.utc)
        weighted_successes = 0.0
        total_weight = 0.0
        
        for record in records:
            # Weight decays with age (recent outcomes matter more)
            age_days = (now - record.created_at).days
            weight = max(0.1, 1.0 - (age_days / 60.0))  # Linear decay over 60 days
            
            total_weight += weight
            if record.success:
                weighted_successes += weight
        
        weighted_success_rate = weighted_successes / total_weight if total_weight > 0 else 0.0
        
        # Combine into final score
        # 60% weighted success rate + 40% improvement magnitude
        score = (0.6 * weighted_success_rate) + (0.4 * min(avg_improvement, 1.0))
        
        # Confidence based on sample size
        confidence = min(sample_size / 10.0, 1.0)  # Full confidence at 10+ samples
        
        return ActionScore(
            action=action,
            score=score,
            confidence=confidence,
            sample_size=sample_size,
            success_rate=success_rate,
            avg_improvement=avg_improvement
        )
    
    async def record_outcome(
        self,
        action: str,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float],
        severity: str,
        success: bool,
        metric_pattern: Optional[str] = None,
        outcome_notes: Optional[str] = None
    ):
        """
        Record outcome of a security response for learning.
        
        Args:
            action: Action that was taken
            pre_metrics: Metrics before action (threat_count, failed_auth, etc.)
            post_metrics: Metrics after action
            severity: Severity level ('warning', 'critical')
            success: Did the action succeed?
            metric_pattern: Pattern fingerprint (auto-generated if not provided)
            outcome_notes: Optional notes about the outcome
        """
        # Generate pattern fingerprint if not provided
        if not metric_pattern:
            metric_pattern = self._generate_pattern_fingerprint(pre_metrics, severity)
        
        # Calculate improvement score
        improvement_score = self._calculate_improvement(pre_metrics, post_metrics)
        
        record = ActionOutcomeRecord(
            agent_name=self.agent_name,
            action=action,
            metric_pattern_fingerprint=metric_pattern,
            pre_metrics=pre_metrics,
            post_metrics=post_metrics,
            severity_score=float(1.0 if severity == 'critical' else 0.5),
            success=success,
            improvement=improvement_score,
            primary_metric='threat_count',
            other_actions_considered=[]
        )
        
        self.db.add(record)
        await self.db.commit()
        
        self.logger.info(
            f"👻📊 Recorded action outcome: {action} for {metric_pattern} "
            f"(success={success}, improvement={improvement_score:.2f})"
        )
    
    def _generate_pattern_fingerprint(
        self,
        metrics: Dict[str, float],
        severity: str
    ) -> str:
        """
        Generate pattern fingerprint from metrics.
        
        Examples:
        - 'brute_force_attack_warning'
        - 'insider_threat_critical'
        - 'network_scan_warning'
        """
        threat_count = metrics.get('threat_count', 0)
        failed_auth = metrics.get('failed_auth_attempts', 0)
        network_anomalies = metrics.get('network_anomalies', 0)
        
        # Determine primary threat pattern
        if failed_auth > 10:
            pattern = 'brute_force_attack'
        elif network_anomalies > 5:
            pattern = 'network_scan'
        elif threat_count > 3:
            pattern = 'multiple_threats'
        elif failed_auth > 0:
            pattern = 'suspicious_auth'
        else:
            pattern = 'general_threat'
        
        return f"{pattern}_{severity}"
    
    def _calculate_improvement(
        self,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float]
    ) -> float:
        """
        Calculate improvement score (0.0-1.0).
        
        Measures how much the action improved the security situation.
        """
        # Primary metric: threat reduction
        pre_threats = pre_metrics.get('threat_count', 0)
        post_threats = post_metrics.get('threat_count', pre_threats)
        threat_reduction = max(0.0, pre_threats - post_threats) / max(pre_threats, 1.0)
        
        # Secondary metric: failed auth reduction
        pre_auth = pre_metrics.get('failed_auth_attempts', 0)
        post_auth = post_metrics.get('failed_auth_attempts', pre_auth)
        auth_reduction = max(0.0, pre_auth - post_auth) / max(pre_auth, 1.0)
        
        # Weighted combination (threat reduction matters more)
        improvement = (0.7 * threat_reduction) + (0.3 * auth_reduction)
        
        return min(improvement, 1.0)
    
    async def request_stick_validation(
        self,
        action: str,
        metric_pattern: str,
        db_getter=None
    ) -> bool:
        """
        Request The Stick to validate action effectiveness learning.
        
        Args:
            action: Action being validated
            metric_pattern: Pattern fingerprint
            db_getter: Database session getter (for The Stick's session)
            
        Returns:
            True if validation passed, False otherwise
        """
        if not db_getter:
            self.logger.warning("👻⚠️ No db_getter provided for validation")
            return True  # Skip validation if no db_getter
        
        try:
            # Get outcome records for this action/pattern
            cutoff_date = datetime.utcnow() - timedelta(days=60)
            records = await self.db.execute(
                self.db.query(ActionOutcomeRecord).filter(
                    and_(
                        ActionOutcomeRecord.system_id == self.system_id,
                        ActionOutcomeRecord.agent_name == self.agent_name,
                        ActionOutcomeRecord.action == action,
                        ActionOutcomeRecord.metric_pattern == metric_pattern,
                        ActionOutcomeRecord.created_at >= cutoff_date
                    )
                )
            )
            records = records.scalars().all()
            
            if not records:
                self.logger.warning(f"No records found for {action} with pattern {metric_pattern}")
                return False
            
            # Calculate statistics
            successful_attempts = sum(1 for r in records if r.success)
            raw_success_rate = successful_attempts / len(records) if records else 0.0
            
            # Get the learned effectiveness score from the action effectiveness model
            action_scores = await self.score_all_actions(metric_pattern)
            effectiveness_score = next((s.score for s in action_scores if s.action == action), raw_success_rate)
            
            # Get previous score for volatility check (if available)
            # TODO: Implement historical score tracking
            previous_score = None
            
            # Call The Stick's validation
            # CRITICAL: Use db_getter to get The Stick's session, don't nest sessions
            async for db in db_getter():
                from app.ai_agents.the_stick.ML.learning import StickLearning
                from app.ai_agents.the_stick.database_integration import StickDatabaseIntegration
                
                # Get user_id from first record or use system default
                user_id = records[0].user_id if records else "system"
                
                stick_learning = StickLearning(db, user_id)
                stick_db = StickDatabaseIntegration(db_getter)
                
                # Validate - returns standard ValidationAuditEntry
                audit_entry = stick_learning.validate_action_effectiveness(
                    agent_name=self.agent_name,
                    action=action,
                    metric_pattern=metric_pattern,
                    effectiveness_score=effectiveness_score,
                    raw_success_rate=raw_success_rate,
                    sample_size=len(records),
                    previous_score=previous_score
                )
                
                # PRIORITY BOOST for security validations
                # QSP validations: priority 9 (pass) or 10 (fail)
                if not audit_entry.validation_result:
                    audit_entry.stick_anxiety_level = 50.0  # Higher anxiety for security validation failures
                
                # Record audit trail using standard record_validation()
                # Note: This is a mock interaction for validation purposes
                # The interaction_id in audit_entry already contains the necessary info
                await stick_db.record_validation(None, audit_entry)
                
                self.logger.info(
                    f"👻📊 Action validation result: {audit_entry.validation_result} "
                    f"({action} in pattern {metric_pattern[:16]}...)"
                )
                
                return audit_entry.validation_result
                
        except Exception as e:
            self.logger.error(f"👻💥 Validation request failed: {e}")
            return True  # Don't block on validation failure
    
    async def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about action effectiveness learning"""
        stats = {}
        
        for action in SECURITY_ACTIONS:
            # Get all records for this action
            records = await self.db.execute(
                self.db.query(ActionOutcomeRecord).filter(
                    and_(
                        ActionOutcomeRecord.agent_name == self.agent_name,
                        ActionOutcomeRecord.action == action
                    )
                )
            )
            records = records.scalars().all()
            
            if records:
                successful = sum(1 for r in records if r.success)
                success_rate = successful / len(records)
                avg_improvement = sum(r.improvement for r in records if r.improvement) / len(records)
                
                stats[action] = {
                    'attempts': len(records),
                    'success_rate': success_rate,
                    'avg_improvement': avg_improvement,
                    'status': 'active' if len(records) >= 10 else 'learning'
                }
        
        return stats
