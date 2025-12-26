#!/usr/bin/env python3
"""
Hamsters' Action Selection Layer - Telepathic Consensus Execution

Selects:
- Storage fix action based on consensus
- Exploration vs Exploitation (epsilon-greedy)
- Adaptive defrag bias (learns when defrag is actually needed)
- Execution strategy and parameters
- Beer consumption finalization
- Duct tape allocation

Personality behaviors integrated:
- Beer consumption tracked and reported
- Duct tape calculations included
- Bob's chaos level monitored
- Stick panic alerts sent if Bob at cupboard
"""
import logging
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import HamstersPerceptionContext, BeerConsumptionEvent, DuctTapeCalculation
from .reasoning import StorageReasoning, HamsterIndividualAssessment

logger = logging.getLogger('HamstersActionSelection')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class StorageFixAction:
    """Hamsters' selected storage fix action"""
    
    # Core action
    action_type: str  # 'fstrim', 'defrag', 'cleanup', 'quantum_fix'
    requires_sudo: bool
    sudo_command: Optional[str]
    
    # Action details
    priority: str  # 'low', 'normal', 'high', 'critical'
    confidence: float
    
    # Consensus details
    consensus_fix: str
    steve_agreed: bool
    bob_agreed: bool
    carl_agreed: bool
    disagreement_level: float
    
    # Personality behaviors
    total_beers_consumed: int
    steve_beers: int
    bob_beers: int
    carl_beers: int
    duct_tape_rolls: float
    duct_tape_breakdown: DuctTapeCalculation
    
    # Bob chaos tracking
    bob_at_cupboard: bool
    stick_panic_alert: bool
    
    # Execution parameters
    execution_strategy: str  # 'immediate', 'scheduled', 'bob_chaos'
    estimated_duration_minutes: int


class HamstersActionSelection:
    """
    Hamsters' action selection layer for storage fixes.
    
    🐹🐹🐹 "Consensus reached! *cracks beer* *measures duct tape* Let's fix this!"
    """
    
    # Map storage issues to viable actions
    # Hamsters handle: Disk/Storage issues
    ACTION_MAP = {
        'disk_full': [
            'rotate_logs',          # Clear old logs first
            'cleanup',              # Basic cleanup
            'cleanup_with_defrag',  # If fragmentation is also high
        ],
        'high_fragmentation': [
            'defrag_only',          # Just defrag
            'cleanup_with_defrag',  # Cleanup + defrag
        ],
        'log_overflow': [
            'rotate_logs',          # Logs are the problem
            'cleanup',              # General cleanup
        ],
        'general_storage': [
            'cleanup',              # Basic cleanup
            'rotate_logs',          # Check logs
        ],
    }
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        
        # Exploration vs Exploitation
        self.epsilon = 0.15  # 15% chance to explore (try non-preferred actions)
        self.min_epsilon = 0.05  # Minimum exploration rate
        self.epsilon_decay = 0.995  # Decay exploration over time
        
        # Adaptive defrag bias (starts high, decreases if defrag not effective)
        self.defrag_bias = 1.3  # 30% bias toward defrag (Carl loves it!)
        self.defrag_successes = 0
        self.defrag_attempts = 0
        
        logger.info("🐹⚡ Hamsters' action selection initialized!")
        logger.info(f"🐹🔬 Exploration rate: {self.epsilon:.1%}, Defrag bias: {self.defrag_bias:.2f}")
        
    def select_action(
        self,
        context: HamstersPerceptionContext,
        reasoning: StorageReasoning
    ) -> StorageFixAction:
        """
        Select storage fix action based on telepathic consensus.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis with consensus
            
        Returns:
            StorageFixAction with selected action and personality details
        """
        logger.info(f"🐹⚡ Selecting storage fix action from consensus...")
        
        # Determine action type
        action_type = reasoning.selected_fix_type
        
        # Build sudo command if required
        sudo_command = None
        if reasoning.requires_sudo:
            sudo_command = self._build_sudo_command(action_type, context)
        
        # Determine priority
        priority = self._determine_priority(reasoning.urgency)
        
        # Check consensus agreement
        steve_agreed, bob_agreed, carl_agreed = self._check_individual_agreement(
            reasoning
        )
        
        # Calculate total beer consumption
        total_beers = (
            context.steve_beers_today +
            context.bob_beers_today +
            context.carl_beers_today
        )
        
        # Check Bob's cupboard status
        bob_at_cupboard = False
        stick_panic_alert = False
        if context.bob_proximity and context.bob_proximity.bob_at_cupboard:
            bob_at_cupboard = True
            stick_panic_alert = True
            logger.warning(
                f"🐹⚠️ BOB AT CUPBOARD! Alerting The Stick! "
                f"Panic level: {context.bob_proximity.stick_panic_level:.2f}"
            )
        
        # Determine execution strategy
        execution_strategy = self._determine_execution_strategy(
            reasoning.risk_level,
            bob_at_cupboard,
            reasoning.urgency
        )
        
        # Estimate duration
        duration = self._estimate_duration(action_type, context.disk_usage_percent)
        
        action = StorageFixAction(
            action_type=action_type,
            requires_sudo=reasoning.requires_sudo,
            sudo_command=sudo_command,
            priority=priority,
            confidence=reasoning.consensus_confidence,
            consensus_fix=reasoning.consensus_fix,
            steve_agreed=steve_agreed,
            bob_agreed=bob_agreed,
            carl_agreed=carl_agreed,
            disagreement_level=reasoning.disagreement_level,
            total_beers_consumed=total_beers,
            steve_beers=context.steve_beers_today,
            bob_beers=context.bob_beers_today,
            carl_beers=context.carl_beers_today,
            duct_tape_rolls=context.duct_tape_assessment.total_rolls,
            duct_tape_breakdown=context.duct_tape_assessment,
            bob_at_cupboard=bob_at_cupboard,
            stick_panic_alert=stick_panic_alert,
            execution_strategy=execution_strategy,
            estimated_duration_minutes=duration
        )
        
        logger.info(
            f"🐹✅ Action selected: {action_type}, "
            f"beers={total_beers}, duct_tape={action.duct_tape_rolls:.1f} rolls, "
            f"strategy={execution_strategy}"
        )
        
        if sudo_command:
            logger.info(f"🐹🔧 Sudo command: {sudo_command}")
        
        return action
    
    def update_defrag_bias(self, action: str, success: bool):
        """
        Update Hamsters' defrag bias based on outcomes.
        
        If defrag keeps failing or isn't needed, reduce the bias.
        If other actions work better, reduce the bias.
        
        Args:
            action: Action that was executed
            success: Whether it succeeded
        """
        if 'defrag' in action:
            self.defrag_attempts += 1
            if success:
                self.defrag_successes += 1
            
            # Calculate success rate
            success_rate = self.defrag_successes / self.defrag_attempts
            
            # Adjust bias based on success rate
            # If success rate < 60%, reduce bias toward 1.0 (no bias)
            # If success rate > 80%, maintain or increase bias
            if success_rate < 0.6:
                self.defrag_bias = max(1.0, self.defrag_bias * 0.95)
                logger.info(
                    f"🐹📉 Defrag success rate low ({success_rate:.1%}) - "
                    f"reducing bias to {self.defrag_bias:.2f}"
                )
            elif success_rate > 0.8 and self.defrag_bias < 1.3:
                self.defrag_bias = min(1.3, self.defrag_bias * 1.02)
                logger.debug(f"🐹📈 Defrag working well - bias: {self.defrag_bias:.2f}")
        
        elif success:
            # Other action succeeded - slightly reduce defrag bias
            # (Hamsters learn there are other good options)
            self.defrag_bias = max(1.0, self.defrag_bias * 0.98)
            logger.debug(
                f"🐹💡 {action} worked! Learning alternatives exist. "
                f"Defrag bias: {self.defrag_bias:.2f}"
            )
    
    def _build_sudo_command(
        self,
        action_type: str,
        context: HamstersPerceptionContext
    ) -> str:
        """
        Build sudo command for storage fix.
        
        Hamsters have sudo access for:
        - fstrim: TRIM unused blocks
        - defrag: Defragment filesystem
        - quantum_fix: Bob's redneck engineering (various commands)
        """
        if action_type == 'fstrim':
            # TRIM all mounted filesystems
            return "sudo fstrim -av"
        
        elif action_type == 'defrag':
            # Defragment filesystem (e4defrag for ext4)
            return "sudo e4defrag -c /"
        
        elif action_type == 'quantum_fix':
            # Bob's quantum duct tape fix (multiple commands)
            commands = [
                "sudo fstrim -av",
                "sudo sync",
                "sudo e4defrag -c /",
                "# Bob's special sauce goes here"
            ]
            return " && ".join(commands)
        
        else:
            return None
    
    def _determine_priority(self, urgency: str) -> str:
        """
        Determine action priority level.
        """
        priority_map = {
            'critical': 'critical',
            'high': 'high',
            'normal': 'normal'
        }
        return priority_map.get(urgency, 'normal')
    
    def _check_individual_agreement(
        self,
        reasoning: StorageReasoning
    ) -> tuple[bool, bool, bool]:
        """
        Check which hamsters agreed with the consensus.
        """
        consensus = reasoning.consensus_fix
        
        steve_agreed = (reasoning.steve_assessment.recommended_fix == consensus)
        bob_agreed = (reasoning.bob_assessment.recommended_fix == consensus)
        carl_agreed = (reasoning.carl_assessment.recommended_fix == consensus)
        
        return steve_agreed, bob_agreed, carl_agreed
    
    def _determine_execution_strategy(
        self,
        risk_level: str,
        bob_at_cupboard: bool,
        urgency: str
    ) -> str:
        """
        Determine execution strategy.
        """
        # Bob at cupboard = chaos mode
        if bob_at_cupboard:
            return 'bob_chaos'
        
        # Critical urgency = immediate
        if urgency == 'critical':
            return 'immediate'
        
        # High risk = scheduled for maintenance window
        if risk_level in ['high', 'bob_level']:
            return 'scheduled'
        
        # Default = immediate
        return 'immediate'
    
    def _estimate_duration(
        self,
        action_type: str,
        disk_usage: float
    ) -> int:
        """
        Estimate fix duration in minutes.
        """
        base_durations = {
            'fstrim': 5,
            'defrag': 30,
            'cleanup': 10,
            'quantum_fix': 45,  # Bob's fixes take longer
            'inode_cleanup': 15
        }
        
        base = base_durations.get(action_type, 10)
        
        # Adjust for disk usage
        if disk_usage > 90:
            base *= 1.5
        
        return int(base)
