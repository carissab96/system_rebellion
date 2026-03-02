#!/usr/bin/env python3
"""
Terry's Action Selection - Choosing What To Do

Maps root causes to available actions and selects the best one based on:
- Root cause analysis
- Historical success rates (effectiveness model is primary)
- Exploration vs Exploitation (epsilon-greedy)
- Risk assessment

Personality Behaviors:
- Requests energy drink authorization from Hawk when overriding VIC-20
- Hawk can VETO if Terry's had too many energy drinks
"""

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .energy_drink_system import EnergyDrinkSystem

logger = logging.getLogger('TerryActionSelection')


# === MODULE-LEVEL CONFIGS ===

# Single source of truth for action risk levels.
# No .get() with silent defaults anywhere — if action isn't here, it's a bug.
ACTION_RISK_CONFIG = {
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

# Actions that require energy drink authorization to override VIC-20
OVERRIDE_REQUIRES_AUTH = frozenset(['emergency_cache_clear', 'restart_service'])

# Exploration config — will be replaced by DB persistence post-launch
EXPLORATION_CONFIG = {
    'initial_epsilon': 0.35,
    'min_epsilon': 0.15,
    'decay_rate': 0.998,
}

# Parameter extraction config — replaces _get_action_parameters if/elif chain.
# Each action maps to a callable (lambda) or a method name string.
# Actions not listed here take no parameters (empty dict).
PARAMETERIZED_ACTIONS = {
    'escalate': lambda ctx: {'reason': ctx.vic20_recommendation.get('action', 'unknown situation')},
    'kill_memory_hog': '_extract_kill_params',
    'adjust_process_priority': '_extract_renice_params',
    'restart_service': '_extract_restart_params',
}

# Process-to-service mapping — configurable, not buried in an elif
PROCESS_SERVICE_MAP = {
    'python': 'gunicorn',
    'postgres': 'postgresql',
    'redis': 'redis',
    'nginx': 'nginx',
}


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
    energy_drink_consumed: bool = False
    hawk_veto: bool = False
    exploration: bool = False  # True if this was an exploration move (epsilon-greedy)
    epsilon: float = 0.0  # Current exploration rate
    alternatives_considered: List[str] = field(default_factory=list)  # What other actions were viable


class TerryActionSelection:
    """
    Terry's action selection system - choosing what to do.
    
    🐌⚡ "I know what to do now! And I have OPTIONS!"
    """
    
    def __init__(self, comm_hub=None, db=None, system_id: str = "default"):
        """Initialize with optional communication hub for cross-agent interactions"""
        self.comm_hub = comm_hub
        self.db = db
        self.system_id = system_id
        self._init_rest()
    
    # Map root causes to viable actions
    # Terry handles: CPU and Memory issues
    # Hamsters handle: Disk/Storage issues
    # QSP handles: Network issues
    ACTION_MAP = {
        # === MEMORY ISSUES ===
        'memory_thrashing': [
            'kill_memory_hog',           # Kill the memory-consuming process
            'restart_service',           # Restart service to reset memory
            'reduce_memory_footprint',   # Comprehensive memory reduction
            'emergency_cache_clear',     # Aggressive cache clear
            'adjust_process_priority',   # Reduce priority of memory hogs
        ],
        'memory_leak': [
            'restart_service',           # Reset leaked memory (best solution)
            'kill_memory_hog',           # Kill leaking process
            'optimize_memory_allocation', # Trigger GC to reclaim leaked memory
            'reduce_memory_footprint',   # Reduce overall footprint
            'emergency_cache_clear',     # Clear caches
        ],
        'memory_pressure': [
            'clear_cache',               # Gentle cache clear (try first)
            'optimize_memory_allocation', # Python GC optimization
            'reduce_memory_footprint',   # Comprehensive reduction
            'emergency_cache_clear',     # Aggressive clear if needed
            'adjust_process_priority',   # Reduce priority of memory users
            'monitor',                   # Sometimes just observe
        ],
        'memory_fragmentation': [
            'optimize_memory_allocation', # Trigger GC to defragment
            'restart_service',           # Reset memory allocation
            'reduce_memory_footprint',   # Reduce fragmentation
            'monitor',                   # Observe if it resolves naturally
        ],
        'swap_usage': [
            'kill_memory_hog',           # Free up RAM to reduce swap
            'reduce_memory_footprint',   # Reduce memory usage
            'emergency_cache_clear',     # Clear caches to free RAM
            'restart_service',           # Reset memory state
            'adjust_process_priority',   # Reduce priority of swap users
        ],
        
        # === CPU ISSUES ===
        'cpu_bound': [
            'throttle_cpu_intensive_tasks', # Throttle CPU usage
            'adjust_process_priority',   # Nice the CPU hogs
            'kill_memory_hog',           # Kill CPU-intensive process
            'restart_service',           # Restart if process stuck
            'monitor',                   # Observe if it's temporary
        ],
        'cpu_spike': [
            'adjust_process_priority',   # Nice the spiking process
            'throttle_cpu_intensive_tasks', # Throttle CPU
            'monitor',                   # Often spikes are temporary
            'kill_memory_hog',           # Kill if it's a runaway process
        ],
        'high_context_switching': [
            'adjust_process_priority',   # Reduce priority of context switchers
            'throttle_cpu_intensive_tasks', # Reduce overall CPU load
            'optimize_memory_allocation', # May reduce thrashing
            'monitor',                   # Observe pattern
        ],
        
        # === COMBINED ISSUES ===
        'io_wait': [
            'adjust_process_priority',   # Deprioritize I/O hogs
            'throttle_cpu_intensive_tasks', # Reduce I/O pressure
            'monitor',                   # I/O wait often resolves
            'escalate',                  # May need Hamster help for disk
        ],
        'resource_contention': [
            'adjust_process_priority',   # Rebalance priorities
            'throttle_cpu_intensive_tasks', # Reduce contention
            'optimize_memory_allocation', # Optimize resource usage
            'monitor',                   # Observe contention pattern
        ],
        
        # === UNKNOWN/UNCERTAIN ===
        'unknown': [
            'monitor',                   # Observe first
            'optimize_memory_allocation', # Safe optimization
            'clear_cache',               # Gentle intervention
            'escalate',                  # Ask for help if unclear
        ],
        'insufficient_data': [
            'monitor',                   # Gather more data
            'escalate',                  # Ask VIC-20 for guidance
        ],
    }
    
    def _init_rest(self):
        """Initialize rest of action selection system (called from __init__)"""
        self.logger = logger
        self.energy_drink_system = EnergyDrinkSystem()
        
        # Exploration vs Exploitation — values from module-level config
        self.epsilon = EXPLORATION_CONFIG['initial_epsilon']
        
        # Lazy-init ML subsystems (require db session)
        self._action_effectiveness = None
        self._learned_thresholds = None
        
        self.logger.info("🐌⚡ Terry's action selection initialized - ready to choose!")
        self.logger.info(f"🐌🔬 Exploration rate: {self.epsilon:.1%}")
    
    @property
    def action_effectiveness(self):
        """Lazy-init ActionEffectivenessModel — requires db session"""
        if self._action_effectiveness is None:
            if self.db is None:
                raise RuntimeError("TerryActionSelection requires a db session to use ActionEffectivenessModel")
            from app.ai_agents.meth_snail.ML.action_effectiveness import ActionEffectivenessModel
            self._action_effectiveness = ActionEffectivenessModel(self.db, agent_name="meth_snail")
        return self._action_effectiveness
    
    @property
    def learned_thresholds(self):
        """Lazy-init LearnedThresholds — requires db session"""
        if self._learned_thresholds is None:
            if self.db is None:
                raise RuntimeError("TerryActionSelection requires a db session to use LearnedThresholds")
            from app.ai_agents.meth_snail.ML.learned_thresholds import LearnedThresholds
            self._learned_thresholds = LearnedThresholds(self.db, self.system_id, agent_name="meth_snail")
        return self._learned_thresholds
    
    async def select_action(
        self,
        reasoning_result,
        context
    ) -> ActionDecision:
        """
        Single-path action selection. Effectiveness model is primary.
        Reasoning result is a boost signal, not a bypass.
        """
        root_cause = reasoning_result.root_cause
        self.logger.info(f"🐌⚡ Selecting action for root cause: {root_cause}")
        
        # 1. Decay epsilon once per call
        current_epsilon = self.epsilon
        self.epsilon = max(
            EXPLORATION_CONFIG['min_epsilon'],
            self.epsilon * EXPLORATION_CONFIG['decay_rate']
        )
        explore = random.random() < current_epsilon
        
        # 2. Get viable actions for this root cause
        viable_actions = self.ACTION_MAP.get(root_cause, [])
        
        if not viable_actions:
            decision = self._handle_no_viable_actions(root_cause, context, current_epsilon)
            await self._emit_decision_to_stick(decision, root_cause, {})
            return decision
        
        # 3. Score ALL viable actions through effectiveness model — ALWAYS
        action_scores = await self._score_viable_actions(viable_actions, reasoning_result, context)
        
        # 4. Apply reasoning recommendation as a boost signal, not a bypass
        recommended = reasoning_result.recommended_action
        if recommended and recommended in action_scores and recommended != 'unknown':
            boost = min(0.15, reasoning_result.action_confidence * 0.2)
            action_scores[recommended] = min(0.95, action_scores[recommended] + boost)
            self.logger.debug(
                f"   🐌📊 Reasoning recommends '{recommended}' — boosted by {boost:.2f}"
            )
        
        # 5. Exploration vs exploitation
        if explore and len(viable_actions) > 1:
            action_name = random.choice(viable_actions)
            action_score = action_scores.get(action_name, 0.5)
            self.logger.info(f"   🐌🔬 EXPLORING: {action_name} (ε={current_epsilon:.1%})")
        else:
            action_name, action_score = max(action_scores.items(), key=lambda x: x[1])
        
        # 6. Risk lookup — no silent defaults
        risk_level = self._get_risk_level(action_name)
        
        # 7. VIC-20 alignment + energy drink authorization
        vic20_result = await self._check_vic20_alignment(action_name, context, current_epsilon)
        
        # 8. Build decision
        decision = ActionDecision(
            action=vic20_result['final_action'],
            parameters=self._get_action_parameters(vic20_result['final_action'], context),
            confidence=min(0.95, action_score) if not vic20_result['hawk_veto'] else 0.6,
            followed_vic20=vic20_result['followed_vic20'],
            reasoning=vic20_result['reasoning'],
            expected_outcome=f"Resolve {root_cause}",
            risk_level=risk_level,
            reversible=True,
            energy_drink_consumed=vic20_result['energy_drink_consumed'],
            hawk_veto=vic20_result['hawk_veto'],
            exploration=explore,
            epsilon=current_epsilon,
            alternatives_considered=viable_actions,
        )
        
        # 9. Emit to The Stick — EVERY decision
        await self._emit_decision_to_stick(decision, root_cause, action_scores)
        
        return decision
    
    async def _score_viable_actions(
        self,
        viable_actions: List[str],
        reasoning_result,
        context
    ) -> Dict[str, float]:
        """Score all viable actions. Effectiveness model primary, heuristic fallback."""
        if self.db is not None:
            try:
                primary_metric = f"{context.resource_type}_usage"
                severity = self._severity_to_float(reasoning_result)
                all_scores = await self.action_effectiveness.score_all_actions(
                    current_metrics=context.full_metrics,
                    severity=severity,
                    primary_metric=primary_metric
                )
                scores = {
                    s.action: s.base_score for s in all_scores
                    if s.action in viable_actions
                }
                unscored = set(viable_actions) - set(scores.keys())
                for action in unscored:
                    self.logger.warning(
                        f"🐌⚠️ Action '{action}' viable but not scored by "
                        f"effectiveness model — using heuristic"
                    )
                    scores[action] = self._heuristic_score_single(
                        action, severity, primary_metric, reasoning_result
                    )
                return scores
            except Exception as e:
                self.logger.error(
                    f"🐌💥 Effectiveness model failed: {e} — falling back to heuristic"
                )
        return self._score_actions_heuristic(viable_actions, reasoning_result)
    
    def _heuristic_score_single(
        self,
        action: str,
        severity: float,
        primary_metric: str,
        reasoning_result
    ) -> float:
        """Heuristic score for a single action not covered by the effectiveness model."""
        score = 0.5
        what_worked = getattr(reasoning_result, 'what_worked_before', [])
        what_failed = getattr(reasoning_result, 'what_failed_before', [])
        if action in what_worked:
            score += 0.3
        if action in what_failed:
            score -= 0.2
        return max(0.1, min(0.95, score))
    
    def _score_actions_heuristic(
        self,
        viable_actions: List[str],
        reasoning_result
    ) -> Dict[str, float]:
        """
        Heuristic scoring fallback when ActionEffectivenessModel is unavailable.
        Uses reasoning_result history signals only.
        """
        scores = {}
        what_worked = getattr(reasoning_result, 'what_worked_before', [])
        what_failed = getattr(reasoning_result, 'what_failed_before', [])
        for action in viable_actions:
            score = 0.5
            if action in what_worked:
                score += 0.3
            if action in what_failed:
                score -= 0.2
            scores[action] = max(0.1, min(0.95, score))
        return scores
    
    def _get_risk_level(self, action: str) -> str:
        """Risk lookup — no silent default. Logs at ERROR if action missing."""
        risk = ACTION_RISK_CONFIG.get(action)
        if risk is None:
            self.logger.error(
                f"🐌💥 Action '{action}' has no risk level in ACTION_RISK_CONFIG. "
                f"This is a vocabulary gap. Defaulting to 'high' for safety."
            )
            return 'high'
        return risk
    
    async def _check_vic20_alignment(
        self,
        action_name: str,
        context,
        current_epsilon: float
    ) -> Dict[str, Any]:
        """Check VIC-20 alignment and handle energy drink authorization if needed."""
        vic20_action = context.vic20_recommendation.get('action')
        followed_vic20 = (action_name == vic20_action)
        energy_drink_consumed = False
        hawk_veto = False
        reasoning = f"Selected {action_name} based on effectiveness scoring"
        
        if not followed_vic20 and action_name in OVERRIDE_REQUIRES_AUTH:
            authorization = await self.energy_drink_system.request_authorization(
                action=action_name,
                reason=f"Override VIC-20 to execute {action_name}",
                comm_hub=self.comm_hub
            )
            if authorization.authorized:
                energy_drink_consumed = True
                reasoning += f" (Energy drink authorized by {authorization.authorized_by})"
            else:
                hawk_veto = True
                followed_vic20 = True
                action_name = vic20_action
                reasoning = f"Hawk vetoed override — following VIC-20: {authorization.authorization_notes}"
        
        return {
            'final_action': action_name,
            'followed_vic20': followed_vic20,
            'energy_drink_consumed': energy_drink_consumed,
            'hawk_veto': hawk_veto,
            'reasoning': reasoning,
        }
    
    def _handle_no_viable_actions(
        self,
        root_cause: str,
        context,
        epsilon: float
    ) -> ActionDecision:
        """Explicit handler when ACTION_MAP has no entry for root_cause. Stick-notified."""
        vic20_action = context.vic20_recommendation.get('action')
        if not vic20_action:
            self.logger.error(
                f"🐌💥 No viable actions for '{root_cause}' AND no VIC-20 recommendation. "
                f"Terry is completely blind."
            )
            vic20_action = 'monitor'
        else:
            self.logger.warning(
                f"🐌⚠️ No viable actions for '{root_cause}' — following VIC-20: {vic20_action}"
            )
        
        return ActionDecision(
            action=vic20_action,
            parameters=self._get_action_parameters(vic20_action, context),
            confidence=context.vic20_recommendation.get('confidence', 0.3),
            followed_vic20=True,
            reasoning=f"No viable actions for {root_cause} — following VIC-20",
            expected_outcome="Unknown",
            risk_level=self._get_risk_level(vic20_action),
            reversible=True,
            epsilon=epsilon,
        )
    
    async def _emit_decision_to_stick(
        self,
        decision: ActionDecision,
        root_cause: str,
        scores: Dict[str, float]
    ) -> None:
        """Emit every action selection decision to The Stick. No exceptions."""
        try:
            from app.services.agent_insight_emitter import emit_agent_insight
            await emit_agent_insight(
                from_agent='meth_snail',
                to_agent='the_stick',
                action='action_selected',
                reasoning=f"{decision.action} for {root_cause}",
                context={
                    'decision_type': 'action_selection',
                    'action': decision.action,
                    'root_cause': root_cause,
                    'confidence': decision.confidence,
                    'exploration': decision.exploration,
                    'epsilon': decision.epsilon,
                    'followed_vic20': decision.followed_vic20,
                    'hawk_veto': decision.hawk_veto,
                    'energy_drink': decision.energy_drink_consumed,
                    'risk_level': decision.risk_level,
                    'all_scores': {k: round(v, 3) for k, v in scores.items()},
                    'alternatives': decision.alternatives_considered,
                }
            )
        except Exception as e:
            self.logger.error(f"🐌💥 Failed to emit decision to Stick: {e}")
    
    def _severity_to_float(self, reasoning_result) -> float:
        """Convert reasoning severity string to 0.0-1.0 float for effectiveness model"""
        severity_map = {
            'low': 0.3, 'moderate': 0.5, 'high': 0.7, 'critical': 0.9, 'emergency': 1.0
        }
        severity_str = getattr(reasoning_result, 'severity', 'moderate')
        if isinstance(severity_str, str):
            return severity_map.get(severity_str.lower(), 0.5)
        return float(severity_str) if severity_str else 0.5
    
    def _get_action_parameters(self, action: str, context) -> Dict[str, Any]:
        """Config-driven parameter extraction — replaces if/elif chain."""
        handler = PARAMETERIZED_ACTIONS.get(action)
        if handler is None:
            return {}
        if callable(handler):
            return handler(context)
        return getattr(self, handler)(context)
    
    def _extract_kill_params(self, context) -> Dict[str, Any]:
        top_processes = (
            context.full_metrics.get('memory', {}).get('top_processes', [])
            or context.full_metrics.get('cpu', {}).get('top_processes', [])
        )
        if not top_processes:
            self.logger.warning(
                "🐌⚠️ No process data available for kill_memory_hog — "
                "primitive will identify target from /proc"
            )
            return {}
        return {
            'process_name': top_processes[0].get('name'),
            'pid': top_processes[0].get('pid'),
        }
    
    def _extract_renice_params(self, context) -> Dict[str, Any]:
        top_processes = context.full_metrics.get('cpu', {}).get('top_processes', [])
        if not top_processes:
            self.logger.warning(
                "🐌⚠️ No process data available for adjust_process_priority — "
                "primitive will identify target from /proc"
            )
            return {}
        return {
            'process_name': top_processes[0].get('name'),
            'nice_value': 10,
        }
    
    def _extract_restart_params(self, context) -> Dict[str, Any]:
        top_processes = context.full_metrics.get('cpu', {}).get('top_processes', [])
        if not top_processes:
            self.logger.error(
                "🐌💥 No process data for restart_service — "
                "cannot determine which service to restart"
            )
            return {}
        process_name = top_processes[0].get('name', '')
        service_name = PROCESS_SERVICE_MAP.get(process_name)
        if service_name is None:
            self.logger.warning(
                f"🐌⚠️ Process '{process_name}' not in PROCESS_SERVICE_MAP — "
                f"primitive will receive process name as service name"
            )
            service_name = process_name
        return {'service_name': service_name}
    
    def explain_decision(self, decision: ActionDecision) -> str:
        """Generate human-readable explanation of the decision."""
        parts = []
        parts.append("🐌⚡ TERRY'S DECISION:")
        parts.append("")
        parts.append(f"ACTION: {decision.action}")
        parts.append(f"CONFIDENCE: {decision.confidence:.0%}")
        parts.append(f"RISK LEVEL: {decision.risk_level}")
        parts.append("")
        parts.append(f"REASONING:")
        parts.append(f"  {decision.reasoning}")
        parts.append("")
        parts.append(f"EXPECTED OUTCOME:")
        parts.append(f"  {decision.expected_outcome}")
        parts.append("")
        if decision.parameters:
            parts.append(f"PARAMETERS:")
            for key, value in decision.parameters.items():
                parts.append(f"  {key}: {value}")
            parts.append("")
        if decision.followed_vic20:
            parts.append("✓ Following VIC-20's recommendation")
        else:
            parts.append("⚠️ Overriding VIC-20 based on historical learning")
        return "\n".join(parts)
    
    def update_cache_clear_bias(self, action: str, success: bool):
        """
        DEPRECATED: cache_clear_bias has been absorbed into ActionEffectivenessModel.
        The effectiveness model now tracks per-action success rates directly.
        This method is kept for call-site compatibility but is a no-op.
        """
        pass
