#!/usr/bin/env python3
"""
Action Effectiveness Model

Learns which actions work in which metric patterns.
Not "restart_service is aggressive" but "restart_service has X% success
when metrics look like THIS."
"""

import logging
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.learned_thresholds import ActionOutcomeRecord


@dataclass
class ActionScore:
    """Score for a specific action in current situation"""
    action: str
    base_score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0 based on sample size
    expected_improvement: float  # Estimated % improvement
    sample_size: int
    reasoning: str
    historical_success_rate: float


class ActionEffectivenessModel:
    """
    Learn which actions work in which situations.
    
    Builds a database of:
    - Action X in situation Y → success rate Z
    - Expected improvement for each action
    - Confidence based on sample size
    """
    
    # ALL actions Terry can perform (not filtered by category)
    ALL_ACTIONS = [
        # Memory actions
        'emergency_cache_clear',
        'clear_cache',
        'optimize_memory_allocation',
        'reduce_memory_footprint',
        'kill_memory_hog',
        'restart_service',
        
        # CPU actions
        'throttle_cpu_intensive_tasks',
        'adjust_process_priority',
        
        # Learning actions
        'monitor',
        'escalate',
    ]
    
    def __init__(self, db_session: Session, agent_name: str = "meth_snail"):
        self.db = db_session
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{agent_name}.action_effectiveness")
        
        # Cache of action effectiveness (pattern -> action -> stats)
        self._effectiveness_cache: Dict[str, Dict[str, ActionScore]] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=10)
    
    async def score_all_actions(
        self,
        current_metrics: Dict[str, float],
        severity: float,
        primary_metric: str
    ) -> List[ActionScore]:
        """
        Score every action against current situation.
        
        Returns sorted list of actions by appropriateness.
        """
        
        scores = []
        
        # Create pattern fingerprint for current situation
        pattern = self._create_metric_pattern(current_metrics, severity)
        
        for action in self.ALL_ACTIONS:
            score = await self._score_action(
                action, pattern, current_metrics, severity, primary_metric
            )
            scores.append(score)
        
        # Sort by base_score (highest first)
        return sorted(scores, key=lambda x: x.base_score, reverse=True)
    
    async def _score_action(
        self,
        action: str,
        pattern: str,
        current_metrics: Dict[str, float],
        severity: float,
        primary_metric: str
    ) -> ActionScore:
        """Score a single action based on historical outcomes"""
        
        # Query similar situations where this action was used
        similar_outcomes = await self._query_similar_situations(
            action, pattern, severity
        )
        
        if not similar_outcomes:
            # No history for this action in this situation
            # Use heuristic scoring based on action type and severity
            heuristic_score = self._get_heuristic_score(action, severity, primary_metric)
            
            return ActionScore(
                action=action,
                base_score=heuristic_score,
                confidence=0.0,
                expected_improvement=0.0,
                sample_size=0,
                reasoning=f'No historical data - using heuristic (severity: {severity:.2f})',
                historical_success_rate=0.0
            )
        
        # Calculate success rate from historical data
        success_rate = sum(1 for o in similar_outcomes if o.success) / len(similar_outcomes)
        
        # Calculate average improvement
        improvements = [o.improvement for o in similar_outcomes if o.success]
        avg_improvement = statistics.mean(improvements) if improvements else 0.0
        
        # Confidence based on sample size (full confidence at 20+ samples)
        confidence = min(1.0, len(similar_outcomes) / 20.0)
        
        # Base score is weighted combination of success rate and improvement
        base_score = (success_rate * 0.6) + (min(1.0, avg_improvement) * 0.4)
        
        # Adjust score based on recency (recent outcomes weighted more)
        recent_outcomes = [o for o in similar_outcomes if o.created_at >= datetime.utcnow() - timedelta(days=7)]
        if recent_outcomes:
            recent_success_rate = sum(1 for o in recent_outcomes if o.success) / len(recent_outcomes)
            # Blend recent with overall (70% recent, 30% overall)
            base_score = (recent_success_rate * 0.7) + (base_score * 0.3)
        
        reasoning = (
            f"Success rate: {success_rate:.0%} in {len(similar_outcomes)} similar situations, "
            f"avg improvement: {avg_improvement:.1%}"
        )
        
        if recent_outcomes and len(recent_outcomes) >= 3:
            recent_success_rate = sum(1 for o in recent_outcomes if o.success) / len(recent_outcomes)
            reasoning += f" (recent: {recent_success_rate:.0%})"
        
        return ActionScore(
            action=action,
            base_score=base_score,
            confidence=confidence,
            expected_improvement=avg_improvement,
            sample_size=len(similar_outcomes),
            reasoning=reasoning,
            historical_success_rate=success_rate
        )
    
    def _get_heuristic_score(self, action: str, severity: float, primary_metric: str) -> float:
        """
        Heuristic scoring when no historical data exists.
        
        This is the bootstrap - as data accumulates, historical scoring takes over.
        """
        
        # Aggressive actions score higher at high severity
        if action in ['emergency_cache_clear', 'restart_service', 'kill_memory_hog']:
            if severity > 0.8:
                return 0.7
            elif severity > 0.6:
                return 0.5
            else:
                return 0.3  # Too aggressive for low severity
        
        # Gentle actions score higher at low-medium severity
        elif action in ['clear_cache', 'optimize_memory_allocation', 'adjust_process_priority']:
            if severity < 0.5:
                return 0.7
            elif severity < 0.7:
                return 0.6
            else:
                return 0.4  # May not be enough for high severity
        
        # Monitor scores high when severity is low
        elif action == 'monitor':
            if severity < 0.4:
                return 0.8
            else:
                return 0.3
        
        # Escalate scores high when uncertain or outside domain
        elif action == 'escalate':
            if 'disk' in primary_metric or 'network' in primary_metric:
                return 0.7  # Outside Terry's domain
            else:
                return 0.2
        
        return 0.5  # Default neutral score
    
    async def _query_similar_situations(
        self,
        action: str,
        pattern: str,
        severity: float
    ) -> List[ActionOutcomeRecord]:
        """
        Find past situations where:
        - This action was taken
        - Metrics were similar (pattern match)
        - Severity was similar (±0.2)
        """
        
        cutoff_date = datetime.utcnow() - timedelta(days=60)  # Last 60 days
        
        # Query for exact pattern match first
        exact_matches = self.db.query(ActionOutcomeRecord).filter(
            and_(
                ActionOutcomeRecord.agent_name == self.agent_name,
                ActionOutcomeRecord.action == action,
                ActionOutcomeRecord.metric_pattern_fingerprint == pattern,
                ActionOutcomeRecord.severity_score.between(severity - 0.2, severity + 0.2),
                ActionOutcomeRecord.created_at >= cutoff_date
            )
        ).order_by(ActionOutcomeRecord.created_at.desc()).limit(50).all()
        
        if len(exact_matches) >= 5:
            return exact_matches
        
        # If not enough exact matches, find similar patterns
        # Similar = same metric bins, even if not identical
        similar_pattern = self._generalize_pattern(pattern)
        
        similar_matches = self.db.query(ActionOutcomeRecord).filter(
            and_(
                ActionOutcomeRecord.agent_name == self.agent_name,
                ActionOutcomeRecord.action == action,
                ActionOutcomeRecord.metric_pattern_fingerprint.like(f"{similar_pattern}%"),
                ActionOutcomeRecord.severity_score.between(severity - 0.3, severity + 0.3),
                ActionOutcomeRecord.created_at >= cutoff_date
            )
        ).order_by(ActionOutcomeRecord.created_at.desc()).limit(50).all()
        
        # Combine exact and similar matches
        all_matches = list(set(exact_matches + similar_matches))
        
        return all_matches[:50]  # Cap at 50 most recent
    
    def _create_metric_pattern(
        self, 
        metrics: Dict[str, float],
        severity: float
    ) -> str:
        """
        Create fingerprint of metric pattern.
        
        Similar patterns should have similar fingerprints.
        Uses binning to group similar values.
        """
        
        pattern_parts = []
        
        # Add severity bin (critical for matching)
        severity_bin = int(severity * 10) * 10  # 0-10, 10-20, etc.
        pattern_parts.append(f"sev:{severity_bin}")
        
        # Add metric bins for key metrics
        key_metrics = ['memory_usage', 'cpu_usage', 'swap_usage', 'disk_usage']
        
        for metric in sorted(key_metrics):
            if metric in metrics:
                value = metrics[metric]
                
                # Bin into 10% ranges for usage metrics
                if 'usage' in metric or 'percent' in metric:
                    bin_value = int(value / 10) * 10
                    pattern_parts.append(f"{metric}:{bin_value}")
        
        # Add growth rate bins if available
        if 'memory_growth_rate' in metrics:
            rate = metrics['memory_growth_rate']
            if rate < 0.5:
                pattern_parts.append("growth:low")
            elif rate < 2.0:
                pattern_parts.append("growth:medium")
            else:
                pattern_parts.append("growth:high")
        
        return "|".join(pattern_parts)
    
    def _generalize_pattern(self, pattern: str) -> str:
        """
        Generalize a pattern for similarity matching.
        
        Example: "sev:80|memory_usage:90|cpu_usage:70" 
              -> "sev:80|memory_usage:90"
        """
        
        parts = pattern.split("|")
        
        # Keep severity and primary metric only
        if len(parts) >= 2:
            return "|".join(parts[:2])
        
        return pattern
    
    async def record_outcome(
        self,
        action: str,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float],
        severity: float,
        success: bool,
        other_actions_considered: List[str] = None,
        central_memory_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Record outcome of an action.
        
        This builds the dataset that makes future predictions better.
        """
        
        # Identify primary metric (one that changed most)
        primary_metric = self._identify_primary_metric(pre_metrics, post_metrics)
        
        # Calculate improvement
        improvement = self._calculate_improvement(
            pre_metrics.get(primary_metric, 0),
            post_metrics.get(primary_metric, 0)
        )
        
        # Create pattern fingerprint
        pattern = self._create_metric_pattern(pre_metrics, severity)
        
        # Get old score before recording
        old_score = await self._score_action(action, pattern, pre_metrics, severity, primary_metric)
        
        # Create outcome record
        record = ActionOutcomeRecord(
            agent_name=self.agent_name,
            action=action,
            pre_metrics=pre_metrics,
            post_metrics=post_metrics,
            metric_pattern_fingerprint=pattern,
            success=success,
            improvement=improvement,
            primary_metric=primary_metric,
            severity_score=severity,
            other_actions_considered=other_actions_considered or [],
            central_memory_id=central_memory_id
        )
        
        self.db.add(record)
        self.db.commit()
        
        # Invalidate cache for this pattern
        if pattern in self._effectiveness_cache:
            del self._effectiveness_cache[pattern]
            if pattern in self._cache_expiry:
                del self._cache_expiry[pattern]
        
        # Get new score after recording
        new_score = await self._score_action(action, pattern, pre_metrics, severity, primary_metric)
        
        # Log learning
        self.logger.info(
            f"📚 LEARNED: {action} → {'SUCCESS' if success else 'FAILED'} "
            f"(improvement: {improvement:+.1%}, pattern: {pattern[:50]}...)"
        )
        
        # Emit learning event if score changed significantly (>0.1) or first time
        score_changed = abs(new_score.base_score - old_score.base_score) > 0.1
        first_time = old_score.sample_size == 0
        
        if score_changed or first_time:
            try:
                from app.services.agent_decision_emitter import emit_learning_event
                
                # Get overall stats for this action
                stats = await self.get_action_statistics(action)
                
                await emit_learning_event(
                    agent_name=self.agent_name,
                    event_type="action_scored",
                    learning_data={
                        "action": action,
                        "pattern": pattern[:80],  # Truncate for readability
                        "success_rate": round(stats['success_rate'], 2),
                        "sample_size": stats['total_uses'],
                        "improvement_avg": round(stats['avg_improvement'] * 100, 1),
                        "confidence": round(new_score.confidence, 2),
                        "first_time": first_time
                    },
                    user_id=user_id
                )
            except Exception as e:
                self.logger.warning(f"Failed to emit learning event: {e}")
    
    def _identify_primary_metric(
        self,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float]
    ) -> str:
        """Identify which metric was the target of the action"""
        
        max_change = 0.0
        primary = 'memory_usage'
        
        for metric in pre_metrics.keys():
            if metric in post_metrics:
                change = abs(pre_metrics[metric] - post_metrics[metric])
                if change > max_change:
                    max_change = change
                    primary = metric
        
        return primary
    
    def _calculate_improvement(self, before: float, after: float) -> float:
        """
        Calculate improvement percentage.
        
        Positive = improvement (metric went down)
        Negative = worsening (metric went up)
        """
        
        if before == 0:
            return 0.0
        
        # For usage metrics, lower is better
        return (before - after) / before
    
    async def get_action_statistics(self, action: str) -> Dict[str, Any]:
        """Get overall statistics for an action"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        records = self.db.query(ActionOutcomeRecord).filter(
            and_(
                ActionOutcomeRecord.agent_name == self.agent_name,
                ActionOutcomeRecord.action == action,
                ActionOutcomeRecord.created_at >= cutoff_date
            )
        ).all()
        
        if not records:
            return {
                'action': action,
                'total_uses': 0,
                'success_rate': 0.0,
                'avg_improvement': 0.0,
                'status': 'no_data'
            }
        
        successes = sum(1 for r in records if r.success)
        success_rate = successes / len(records)
        
        improvements = [r.improvement for r in records if r.success]
        avg_improvement = statistics.mean(improvements) if improvements else 0.0
        
        return {
            'action': action,
            'total_uses': len(records),
            'success_rate': success_rate,
            'avg_improvement': avg_improvement,
            'successes': successes,
            'failures': len(records) - successes,
            'status': 'active' if len(records) >= 10 else 'learning'
        }
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of all action learning"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        total_records = self.db.query(func.count(ActionOutcomeRecord.id)).filter(
            and_(
                ActionOutcomeRecord.agent_name == self.agent_name,
                ActionOutcomeRecord.created_at >= cutoff_date
            )
        ).scalar()
        
        action_stats = {}
        for action in self.ALL_ACTIONS:
            stats = await self.get_action_statistics(action)
            action_stats[action] = stats
        
        # Find best and worst performing actions
        actions_with_data = [a for a in action_stats.values() if a['total_uses'] >= 5]
        
        best_action = None
        worst_action = None
        
        if actions_with_data:
            best_action = max(actions_with_data, key=lambda x: x['success_rate'])
            worst_action = min(actions_with_data, key=lambda x: x['success_rate'])
        
        return {
            'agent_name': self.agent_name,
            'total_outcomes_recorded': total_records,
            'actions_tracked': len(self.ALL_ACTIONS),
            'action_statistics': action_stats,
            'best_performing_action': best_action['action'] if best_action else None,
            'worst_performing_action': worst_action['action'] if worst_action else None,
            'learning_status': 'active' if total_records >= 50 else 'learning'
        }
