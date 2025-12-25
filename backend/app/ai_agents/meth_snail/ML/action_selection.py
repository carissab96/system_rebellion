#!/usr/bin/env python3
"""
Terry's Action Selection - Choosing What To Do

Maps root causes to available actions and selects the best one based on:
- Root cause analysis
- Historical success rates
- Personality bias (Terry loves cache clears!)
- Risk assessment

Personality Behaviors:
- Requests energy drink authorization from Hawk when overriding VIC-20
- Hawk can VETO if Terry's had too many energy drinks
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from .energy_drink_system import EnergyDrinkSystem

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
    energy_drink_consumed: bool = False
    hawk_veto: bool = False


class TerryActionSelection:
    """
    Terry's action selection system - choosing what to do.
    
    🐌⚡ "I know what to do now! And I have OPTIONS!"
    """
    
    # Map root causes to viable actions
    ACTION_MAP = {
        'memory_thrashing': [
            'restart_service',  # Kill memory hog
            'emergency_cache_clear',  # Free up memory
        ],
        'memory_leak': [
            'restart_service',  # Reset leaked memory
            'emergency_cache_clear',
        ],
        'memory_pressure': [
            'emergency_cache_clear',
            'adjust_process_priority',
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
        ],
        'disk_full': [
            'rotate_logs',  # Clear old logs
            'emergency_cache_clear',
        ],
        'network_congestion': [
            'scan_open_ports',
            'throttle_cpu_intensive_tasks',
        ],
    }
    
    # Risk levels for each action
    ACTION_RISKS = {
        'emergency_cache_clear': 'low',  # Safe, just clears cache
        'adjust_process_priority': 'low',  # Reversible
        'throttle_cpu_intensive_tasks': 'medium',  # May slow things down
        'rotate_logs': 'low',  # Safe
        'scan_open_ports': 'low',  # Read-only
        'restart_service': 'high',  # Disruptive
    }
    
    def __init__(self):
        """Initialize action selection system"""
        self.logger = logger
        self.energy_drink_system = EnergyDrinkSystem()
        self.logger.info("🐌⚡ Terry's action selection initialized - ready to choose!")
    
    async def select_action(
        self,
        reasoning_result,
        context
    ) -> ActionDecision:
        """
        Choose the best action based on reasoning and personality.
        
        Terry loves cache clears, but he'll learn when they don't work.
        
        Args:
            reasoning_result: ReasoningResult from reasoning engine
            context: PerceptionContext with full situational awareness
            
        Returns:
            ActionDecision with chosen action and parameters
        """
        root_cause = reasoning_result.root_cause
        recommended_action = reasoning_result.recommended_action
        confidence = reasoning_result.action_confidence
        
        self.logger.info(f"🐌⚡ Selecting action for root cause: {root_cause}")
        
        # If reasoning engine already picked an action from historical learning, use it
        if recommended_action and recommended_action != 'unknown':
            self.logger.info(f"   ✓ Using reasoning engine's recommendation: {recommended_action}")
            
            vic20_action = context.vic20_recommendation.get('action')
            followed_vic20 = (recommended_action == vic20_action)
            
            # Check if Terry needs energy drink to override VIC-20
            energy_drink_consumed = False
            hawk_veto = False
            reasoning = f"Using learned action {recommended_action} for {root_cause} (confidence: {confidence:.2f})"
            
            if not followed_vic20 and recommended_action in ['emergency_cache_clear', 'restart_service']:
                authorization = await self.energy_drink_system.request_authorization(
                    action=recommended_action,
                    reason=f"Override VIC-20 to execute learned action {recommended_action}"
                )
                
                if authorization.authorized:
                    energy_drink_consumed = True
                    reasoning += f" (Energy drink authorized by {authorization.authorized_by})"
                else:
                    # HAWK VETO - must follow VIC-20
                    hawk_veto = True
                    followed_vic20 = True
                    recommended_action = vic20_action
                    reasoning = f"Hawk vetoed override - following VIC-20: {authorization.authorization_notes}"
            
            return ActionDecision(
                action=recommended_action,
                parameters=self._get_action_parameters(recommended_action, context),
                confidence=confidence if not hawk_veto else 0.6,
                followed_vic20=followed_vic20,
                reasoning=reasoning,
                expected_outcome=f"Resolve {root_cause} based on historical success",
                risk_level=self.ACTION_RISKS.get(recommended_action, 'medium'),
                reversible=True,
                energy_drink_consumed=energy_drink_consumed,
                hawk_veto=hawk_veto
            )
        
        # Otherwise, select from action map based on root cause
        viable_actions = self.ACTION_MAP.get(root_cause, [])
        
        if not viable_actions:
            # No known actions for this root cause - fall back to VIC-20
            self.logger.warning(f"   ⚠️ No known actions for {root_cause}, using VIC-20's recommendation")
            vic20_action = context.vic20_recommendation.get('action', 'emergency_cache_clear')
            
            return ActionDecision(
                action=vic20_action,
                parameters=self._get_action_parameters(vic20_action, context),
                confidence=context.vic20_recommendation.get('confidence', 0.5),
                followed_vic20=True,
                reasoning=f"No learned actions for {root_cause}, following VIC-20",
                expected_outcome="Unknown",
                risk_level=self.ACTION_RISKS.get(vic20_action, 'medium'),
                reversible=True
            )
        
        # Score each viable action
        action_scores = self._score_actions(viable_actions, reasoning_result)
        
        # Apply Terry's personality bias (loves cache clears!)
        if 'emergency_cache_clear' in action_scores:
            original_score = action_scores['emergency_cache_clear']
            action_scores['emergency_cache_clear'] *= 1.2  # 20% meth-fueled bias
            self.logger.debug(f"   🐌💨 Terry's bias: cache_clear {original_score:.2f} → {action_scores['emergency_cache_clear']:.2f}")
        
        # Select highest scoring action
        best_action = max(action_scores.items(), key=lambda x: x[1])
        action_name = best_action[0]
        action_score = best_action[1]
        
        self.logger.info(f"   ✓ Selected: {action_name} (score: {action_score:.2f})")
        
        # Check if Terry needs energy drink to override VIC-20
        vic20_action = context.vic20_recommendation.get('action')
        followed_vic20 = (action_name == vic20_action)
        energy_drink_consumed = False
        hawk_veto = False
        reasoning = f"Selected {action_name} for {root_cause} based on action scoring"
        
        if not followed_vic20 and action_name in ['emergency_cache_clear', 'restart_service']:
            authorization = await self.energy_drink_system.request_authorization(
                action=action_name,
                reason=f"Override VIC-20 to execute {action_name}"
            )
            
            if authorization.authorized:
                energy_drink_consumed = True
                reasoning += f" (Energy drink authorized by {authorization.authorized_by})"
            else:
                # HAWK VETO - must follow VIC-20
                hawk_veto = True
                followed_vic20 = True
                action_name = vic20_action
                reasoning = f"Hawk vetoed override - following VIC-20: {authorization.authorization_notes}"
        
        return ActionDecision(
            action=action_name,
            parameters=self._get_action_parameters(action_name, context),
            confidence=min(0.95, action_score) if not hawk_veto else 0.6,
            followed_vic20=followed_vic20,
            reasoning=reasoning,
            expected_outcome=f"Resolve {root_cause}",
            risk_level=self.ACTION_RISKS.get(action_name, 'medium'),
            reversible=True,
            energy_drink_consumed=energy_drink_consumed,
            hawk_veto=hawk_veto
        )
    
    def _score_actions(
        self,
        viable_actions: List[str],
        reasoning_result
    ) -> Dict[str, float]:
        """
        Score each viable action based on historical success.
        
        Args:
            viable_actions: List of actions that could work for this root cause
            reasoning_result: ReasoningResult with historical learning
            
        Returns:
            Dictionary mapping action names to scores (0.0 - 1.0)
        """
        scores = {}
        
        # Get historical success rates
        what_worked = reasoning_result.what_worked_before
        what_failed = reasoning_result.what_failed_before
        
        for action in viable_actions:
            # Start with base score
            score = 0.5
            
            # Boost if it worked before
            if action in what_worked:
                score += 0.3
            
            # Penalize if it failed before
            if action in what_failed:
                score -= 0.2
            
            # Ensure score stays in valid range
            score = max(0.1, min(0.95, score))
            
            scores[action] = score
        
        return scores
    
    def _get_action_parameters(
        self,
        action: str,
        context
    ) -> Dict[str, Any]:
        """
        Get parameters for the chosen action.
        
        Some actions need specific parameters based on context.
        
        Args:
            action: Action name
            context: PerceptionContext
            
        Returns:
            Dictionary of parameters for the action
        """
        # Most actions don't need parameters
        if action == 'emergency_cache_clear':
            return {}
        
        elif action == 'adjust_process_priority':
            # Try to nice the top CPU process
            top_processes = context.full_metrics.get('cpu', {}).get('top_processes', [])
            if top_processes:
                return {
                    'process_name': top_processes[0].get('name', 'python'),
                    'nice_value': 10  # Lower priority
                }
            return {'process_name': 'python', 'nice_value': 10}
        
        elif action == 'restart_service':
            # Restart the service causing issues
            top_processes = context.full_metrics.get('cpu', {}).get('top_processes', [])
            if top_processes:
                process_name = top_processes[0].get('name', 'redis')
                # Map process names to service names
                service_map = {
                    'python': 'gunicorn',
                    'postgres': 'postgresql',
                    'redis': 'redis',
                    'nginx': 'nginx',
                }
                service_name = service_map.get(process_name, 'redis')
                return {'service_name': service_name}
            return {'service_name': 'redis'}
        
        elif action == 'throttle_cpu_intensive_tasks':
            return {}
        
        elif action == 'rotate_logs':
            return {}
        
        elif action == 'scan_open_ports':
            return {}
        
        else:
            return {}
    
    def explain_decision(self, decision: ActionDecision) -> str:
        """
        Generate human-readable explanation of the decision.
        
        Args:
            decision: ActionDecision to explain
            
        Returns:
            Natural language explanation
        """
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
