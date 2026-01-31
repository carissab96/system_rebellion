#!/usr/bin/env python3
"""
Terry's Action Selection v2 - Learned Action Selection

Replaces hardcoded ACTION_MAP with autonomous learning:
- LearnedThresholds: System-specific severity assessment
- ActionEffectivenessModel: Evidence-based action scoring
- PredictiveEngine: Proactive intervention recommendations

Personality Behaviors:
- Requests energy drink authorization from Hawk when overriding VIC-20
- Hawk can VETO if Terry's had too many energy drinks
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .energy_drink_system import EnergyDrinkSystem
from .learned_thresholds import LearnedThresholds
from .action_effectiveness import ActionEffectivenessModel
from .predictive_engine import PredictiveEngine, ProactiveRecommendation

logger = logging.getLogger('TerryActionSelection')


@dataclass
class ActionDecision:
    """Final decision on what action to take"""
    action: str
    parameters: Dict[str, Any]
    confidence: float
    followed_vic20: bool
    reasoning: str
    expected_outcome: str
    risk_level: str  # 'low', 'medium', 'high'
    reversible: bool
    
    # Personality
    energy_drink_consumed: bool = False
    hawk_veto: bool = False
    
    # Learning metadata
    severity_score: float = 0.0  # From learned thresholds
    is_proactive: bool = False  # Proactive vs reactive
    action_score: float = 0.0  # From action effectiveness model
    alternatives_considered: List[Dict[str, float]] = field(default_factory=list)
    
    # For outcome tracking
    decision_timestamp: datetime = field(default_factory=datetime.utcnow)
    pre_metrics: Dict[str, float] = field(default_factory=dict)
    primary_metric: str = ""
    threshold_crossed: Optional[str] = None  # 'warning', 'critical', 'emergency', None


@dataclass
class OutcomeObservation:
    """Observation of action outcome for learning"""
    decision: ActionDecision
    post_metrics: Dict[str, float]
    observation_timestamp: datetime
    
    # Computed outcomes
    success: bool
    improvement: float  # % improvement in primary metric
    
    # Learning signals
    was_false_alarm: bool = False
    should_have_acted_sooner: bool = False
    resolved_naturally: bool = False
    became_critical_before_action: bool = False
    rapid_escalation: bool = False


class TerryActionSelectionV2:
    """
    Terry's learned action selection system.
    
    🐌⚡ "I learn from every decision. No more hardcoded lists!"
    """
    
    # Risk levels for actions (heuristic fallback)
    ACTION_RISKS = {
        'emergency_cache_clear': 'low',
        'clear_cache': 'low',
        'optimize_memory_allocation': 'low',
        'reduce_memory_footprint': 'low',
        'kill_memory_hog': 'high',
        'adjust_process_priority': 'low',
        'throttle_cpu_intensive_tasks': 'medium',
        'restart_service': 'high',
        'monitor': 'low',
        'escalate': 'low',
    }
    
    def __init__(
        self, 
        db_session: Session,
        system_id: str,
        comm_hub=None
    ):
        """Initialize with database session for learning"""
        self.db = db_session
        self.system_id = system_id
        self.comm_hub = comm_hub
        self.logger = logger
        
        # Initialize learning components
        self.learned_thresholds = LearnedThresholds(
            db_session=db_session,
            system_id=system_id,
            agent_name="meth_snail"
        )
        
        self.action_effectiveness = ActionEffectivenessModel(
            db_session=db_session,
            agent_name="meth_snail"
        )
        
        self.predictive_engine = PredictiveEngine(
            db_session=db_session,
            learned_thresholds=self.learned_thresholds,
            system_id=system_id,
            agent_name="meth_snail"
        )
        
        # Personality
        self.energy_drink_system = EnergyDrinkSystem()
        
        # Track pending decisions for outcome observation
        self.pending_decisions: Dict[str, ActionDecision] = {}
        
        self.logger.info("🐌⚡ Terry's learned action selection initialized!")
    
    async def select_action(
        self,
        reasoning_result,
        context,
        recent_history: List[Dict[str, float]] = None
    ) -> ActionDecision:
        """
        Choose the best action using learned components.
        
        Flow:
        1. Assess severity using learned thresholds
        2. Check for proactive recommendations from predictive engine
        3. Score all viable actions using action effectiveness model
        4. Select best action
        5. Check energy drink authorization if needed
        
        Args:
            reasoning_result: ReasoningResult from reasoning engine
            context: PerceptionContext with full situational awareness
            recent_history: Recent metric measurements for forecasting
            
        Returns:
            ActionDecision with chosen action and metadata for learning
        """
        
        # Extract current metrics
        current_metrics = self._extract_metrics(context)
        primary_metric = self._identify_primary_metric(reasoning_result.root_cause)
        
        self.logger.info(f"🐌⚡ Selecting action for root cause: {reasoning_result.root_cause}")
        
        # 1. Assess severity using learned thresholds
        severity_assessment = await self.learned_thresholds.assess_severity(
            metric_name=primary_metric,
            current_value=current_metrics.get(primary_metric, 0.0),
            context={
                'time_of_day': datetime.utcnow().hour,
                'day_of_week': datetime.utcnow().weekday(),
                'root_cause': reasoning_result.root_cause
            }
        )
        
        severity_score = severity_assessment['severity']
        threshold_crossed = severity_assessment.get('threshold_level')
        
        self.logger.info(
            f"   📊 Severity: {severity_score:.2f} "
            f"(threshold: {threshold_crossed or 'none'}, "
            f"confidence: {severity_assessment['confidence']:.2f})"
        )
        
        # 2. Check for proactive recommendations
        proactive_rec = None
        if recent_history:
            forecasts = await self.predictive_engine.forecast(
                current_metrics=current_metrics,
                recent_history=recent_history,
                context={
                    'time_of_day': datetime.utcnow().hour,
                    'day_of_week': datetime.utcnow().weekday()
                }
            )
            
            proactive_rec = await self.predictive_engine.should_act_proactively(forecasts)
            
            if proactive_rec:
                self.logger.info(f"   🔮 PROACTIVE: {proactive_rec.reasoning}")
                # Override severity with proactive recommendation
                severity_score = proactive_rec.recommended_severity
        
        # 3. Score all viable actions
        action_scores = await self.action_effectiveness.score_all_actions(
            current_metrics=current_metrics,
            severity=severity_score,
            primary_metric=primary_metric
        )
        
        if not action_scores:
            # Cold start - no learned actions yet, use VIC-20
            return await self._fallback_to_vic20(
                context, current_metrics, primary_metric, 
                severity_score, threshold_crossed
            )
        
        # Log top 3 actions
        top_3 = sorted(action_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        self.logger.info(f"   🎯 Top actions: {[(a, f'{s:.2f}') for a, s in top_3]}")
        
        # 4. Select best action
        best_action, best_score = top_3[0]
        
        # 5. Check energy drink authorization if overriding VIC-20
        vic20_action = context.vic20_recommendation.get('action')
        followed_vic20 = (best_action == vic20_action)
        energy_drink_consumed = False
        hawk_veto = False
        reasoning = (
            f"Selected {best_action} based on learned effectiveness "
            f"(score: {best_score:.2f}, severity: {severity_score:.2f})"
        )
        
        if proactive_rec:
            reasoning = f"PROACTIVE: {proactive_rec.reasoning}"
        
        if not followed_vic20 and best_action in ['emergency_cache_clear', 'restart_service']:
            authorization = await self.energy_drink_system.request_authorization(
                action=best_action,
                reason=f"Override VIC-20 to execute learned action {best_action}",
                comm_hub=self.comm_hub
            )
            
            if authorization.authorized:
                energy_drink_consumed = True
                reasoning += f" (Energy drink authorized by {authorization.authorized_by})"
            else:
                # HAWK VETO
                hawk_veto = True
                followed_vic20 = True
                best_action = vic20_action
                best_score = 0.6
                reasoning = f"Hawk vetoed override - following VIC-20: {authorization.authorization_notes}"
        
        # Create decision with full metadata for learning
        decision = ActionDecision(
            action=best_action,
            parameters=self._get_action_parameters(best_action, context),
            confidence=min(0.95, best_score) if not hawk_veto else 0.6,
            followed_vic20=followed_vic20,
            reasoning=reasoning,
            expected_outcome=f"Improve {primary_metric} by learned pattern",
            risk_level=self.ACTION_RISKS.get(best_action, 'medium'),
            reversible=True,
            energy_drink_consumed=energy_drink_consumed,
            hawk_veto=hawk_veto,
            severity_score=severity_score,
            is_proactive=proactive_rec is not None,
            action_score=best_score,
            alternatives_considered=[{'action': a, 'score': s} for a, s in top_3[1:]],
            pre_metrics=current_metrics.copy(),
            primary_metric=primary_metric,
            threshold_crossed=threshold_crossed
        )
        
        # Store for outcome tracking
        decision_id = f"{self.system_id}_{decision.decision_timestamp.isoformat()}"
        self.pending_decisions[decision_id] = decision
        
        return decision
    
    async def record_outcome(
        self,
        decision: ActionDecision,
        post_metrics: Dict[str, float],
        observation_window_seconds: int = 300
    ) -> OutcomeObservation:
        """
        Record outcome of an action for learning.
        
        This is where we detect the learning signals you flagged:
        - was_false_alarm
        - should_have_acted_sooner
        - resolved_naturally
        - became_critical_before_action
        - rapid_escalation
        
        Args:
            decision: The action decision that was executed
            post_metrics: Metrics after action execution
            observation_window_seconds: How long to observe (default 5 min)
            
        Returns:
            OutcomeObservation with computed learning signals
        """
        
        observation = OutcomeObservation(
            decision=decision,
            post_metrics=post_metrics,
            observation_timestamp=datetime.utcnow()
        )
        
        # Calculate improvement
        pre_value = decision.pre_metrics.get(decision.primary_metric, 0.0)
        post_value = post_metrics.get(decision.primary_metric, 0.0)
        
        if pre_value > 0:
            observation.improvement = ((pre_value - post_value) / pre_value) * 100
        else:
            observation.improvement = 0.0
        
        # Determine success
        observation.success = observation.improvement > 5.0  # 5% improvement = success
        
        # LEARNING SIGNAL 1: Was it a false alarm?
        # Threshold crossed, we monitored (or took gentle action), it resolved naturally
        if decision.threshold_crossed and decision.action in ['monitor', 'clear_cache']:
            # Check if metric dropped back below threshold without aggressive intervention
            threshold_value = await self.learned_thresholds.get_threshold(
                decision.primary_metric, 
                decision.threshold_crossed
            )
            
            if post_value < threshold_value * 0.95:  # Dropped 5% below threshold
                observation.was_false_alarm = True
                observation.resolved_naturally = True
                self.logger.info(
                    f"   🔔 FALSE ALARM: {decision.primary_metric} crossed {decision.threshold_crossed} "
                    f"but resolved naturally ({pre_value:.1f}% → {post_value:.1f}%)"
                )
        
        # LEARNING SIGNAL 2: Should have acted sooner?
        # Metric became critical before we could act, or escalated rapidly
        time_to_action = (observation.observation_timestamp - decision.decision_timestamp).total_seconds()
        
        if decision.threshold_crossed in ['warning', 'critical']:
            # Check if it crossed to next level during observation window
            next_level = 'critical' if decision.threshold_crossed == 'warning' else 'emergency'
            next_threshold = await self.learned_thresholds.get_threshold(
                decision.primary_metric,
                next_level
            )
            
            if post_value >= next_threshold:
                observation.became_critical_before_action = True
                observation.should_have_acted_sooner = True
                self.logger.warning(
                    f"   ⚠️ ACTED TOO LATE: {decision.primary_metric} escalated from "
                    f"{decision.threshold_crossed} to {next_level} "
                    f"({pre_value:.1f}% → {post_value:.1f}%)"
                )
        
        # LEARNING SIGNAL 3: Rapid escalation?
        # Metric grew faster than expected (>2% per minute)
        if time_to_action > 0:
            growth_rate = (post_value - pre_value) / (time_to_action / 60.0)  # % per minute
            
            if growth_rate > 2.0:
                observation.rapid_escalation = True
                observation.should_have_acted_sooner = True
                self.logger.warning(
                    f"   🚀 RAPID ESCALATION: {decision.primary_metric} grew "
                    f"{growth_rate:.1f}%/min (threshold: 2%/min)"
                )
        
        # Record outcome in learning systems
        
        # 1. Update learned thresholds
        await self.learned_thresholds.record_outcome(
            metric_name=decision.primary_metric,
            metric_value=pre_value,
            threshold_level=decision.threshold_crossed,
            action_taken=decision.action if decision.action != 'monitor' else None,
            outcome={
                'success': observation.success,
                'improvement': observation.improvement,
                'resolved_naturally': observation.resolved_naturally,
                'became_critical_before_action': observation.became_critical_before_action,
                'rapid_escalation': observation.rapid_escalation
            },
            system_state=decision.pre_metrics,
            context={
                'time_of_day': decision.decision_timestamp.hour,
                'day_of_week': decision.decision_timestamp.weekday()
            }
        )
        
        # 2. Update action effectiveness
        await self.action_effectiveness.record_outcome(
            action=decision.action,
            pre_metrics=decision.pre_metrics,
            post_metrics=post_metrics,
            severity=decision.severity_score,
            success=observation.success,
            improvement=observation.improvement
        )
        
        # 3. Update predictive patterns (if we started tracking one)
        # This would be called from the main execution loop at intervals
        
        self.logger.info(
            f"   📝 Outcome recorded: {decision.action} → "
            f"{'SUCCESS' if observation.success else 'FAILED'} "
            f"({observation.improvement:+.1f}% improvement)"
        )
        
        return observation
    
    async def _fallback_to_vic20(
        self,
        context,
        current_metrics: Dict[str, float],
        primary_metric: str,
        severity_score: float,
        threshold_crossed: Optional[str]
    ) -> ActionDecision:
        """Fallback to VIC-20 when no learned actions available (cold start)"""
        
        vic20_action = context.vic20_recommendation.get('action', 'monitor')
        
        self.logger.info(f"   🆕 Cold start - no learned actions yet, following VIC-20")
        
        return ActionDecision(
            action=vic20_action,
            parameters=self._get_action_parameters(vic20_action, context),
            confidence=context.vic20_recommendation.get('confidence', 0.5),
            followed_vic20=True,
            reasoning="Cold start - following VIC-20 until learning data accumulates",
            expected_outcome="Unknown - learning phase",
            risk_level=self.ACTION_RISKS.get(vic20_action, 'medium'),
            reversible=True,
            severity_score=severity_score,
            is_proactive=False,
            action_score=0.5,
            pre_metrics=current_metrics.copy(),
            primary_metric=primary_metric,
            threshold_crossed=threshold_crossed
        )
    
    def _extract_metrics(self, context) -> Dict[str, float]:
        """Extract current metric values from context"""
        
        metrics = {}
        
        # CPU metrics
        if hasattr(context, 'full_metrics') and 'cpu' in context.full_metrics:
            cpu = context.full_metrics['cpu']
            metrics['cpu_usage'] = cpu.get('usage_percent', 0.0)
            metrics['cpu_load'] = cpu.get('load_avg_1min', 0.0)
        
        # Memory metrics
        if hasattr(context, 'full_metrics') and 'memory' in context.full_metrics:
            mem = context.full_metrics['memory']
            metrics['memory_usage'] = mem.get('usage_percent', 0.0)
            metrics['swap_usage'] = mem.get('swap_percent', 0.0)
        
        return metrics
    
    def _identify_primary_metric(self, root_cause: str) -> str:
        """Identify which metric is primary for this root cause"""
        
        if 'memory' in root_cause.lower():
            return 'memory_usage'
        elif 'cpu' in root_cause.lower():
            return 'cpu_usage'
        elif 'swap' in root_cause.lower():
            return 'swap_usage'
        else:
            return 'memory_usage'  # Default
    
    def _get_action_parameters(
        self,
        action: str,
        context
    ) -> Dict[str, Any]:
        """Get parameters for the chosen action"""
        
        if action == 'kill_memory_hog':
            top_processes = context.full_metrics.get('memory', {}).get('top_processes', [])
            if not top_processes:
                top_processes = context.full_metrics.get('cpu', {}).get('top_processes', [])
            
            if top_processes:
                return {
                    'process_name': top_processes[0].get('name', 'python'),
                    'pid': top_processes[0].get('pid')
                }
            return {'process_name': 'python', 'pid': None}
        
        elif action == 'adjust_process_priority':
            top_processes = context.full_metrics.get('cpu', {}).get('top_processes', [])
            if top_processes:
                return {
                    'process_name': top_processes[0].get('name', 'python'),
                    'nice_value': 10
                }
            return {'process_name': 'python', 'nice_value': 10}
        
        elif action == 'restart_service':
            top_processes = context.full_metrics.get('cpu', {}).get('top_processes', [])
            if top_processes:
                process_name = top_processes[0].get('name', 'redis')
                service_map = {
                    'python': 'gunicorn',
                    'postgres': 'postgresql',
                    'redis': 'redis',
                    'nginx': 'nginx',
                }
                service_name = service_map.get(process_name, 'redis')
                return {'service_name': service_name}
            return {'service_name': 'redis'}
        
        elif action == 'escalate':
            return {'reason': context.vic20_recommendation.get('action', 'unknown situation')}
        
        else:
            return {}
    
    async def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status for all components"""
        
        return {
            'thresholds': await self.learned_thresholds.get_learning_summary('memory_usage'),
            'action_effectiveness': await self.action_effectiveness.get_action_statistics('emergency_cache_clear'),
            'forecast_accuracy': await self.predictive_engine.get_forecast_accuracy('memory_usage')
        }
