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
from .execution_planner import STORAGE_GOALS, COLD_START_HYPOTHESES
from app.ai_agents.exceptions import MLPipelineFailure

logger = logging.getLogger('HamstersActionSelection')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class StorageFixAction:
    """Hamsters' selected storage fix action"""
    
    # Goal — a problem statement from STORAGE_GOALS vocabulary.
    # The ExecutionPlanner resolves this into a primitive sequence at runtime.
    goal: str  # e.g. 'disk_full', 'fragmentation_high', 'log_overflow'
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
    
    # Goal vocabulary — what problems can the Hamsters identify?
    # The ExecutionPlanner resolves goals into primitive sequences.
    # ACTION_MAP is gone. The planner owns the how; the selector owns the what.
    STORAGE_GOALS = STORAGE_GOALS
    
    def __init__(self, personality_traits: Dict[str, Any], db=None, system_id: str = "default"):
        self.personality_traits = personality_traits
        self.db = db
        self.system_id = system_id
        
        # Learned thresholds and action effectiveness (initialized lazily)
        self.learned_thresholds = None
        self.action_effectiveness = None
        
        # Initialize learning systems if db available
        if self.db:
            from .learned_thresholds import LearnedThresholds
            from .action_effectiveness import ActionEffectivenessModel
            
            self.learned_thresholds = LearnedThresholds(db, system_id)
            self.action_effectiveness = ActionEffectivenessModel(db, system_id)
            logger.info("🐹🧠 Learned thresholds and action effectiveness enabled!")
        
        # Exploration vs Exploitation
        self.epsilon = 0.15  # 15% chance to explore (try non-preferred goals)
        self.min_epsilon = 0.05  # Minimum exploration rate
        self.epsilon_decay = 0.995  # Decay exploration over time

        # NOTE: defrag_bias removed. The ExecutionPlanner is the authority on
        # when to defrag — it queries LearnedSequence and composes primitive
        # sequences. A separate bias counter here would create two parallel
        # learning channels that can disagree. Carl's love of defrag is
        # expressed through cold start hypotheses in execution_planner.py,
        # not through a bias that bypasses the learned sequence system.
        
        logger.info("🐹⚡ Hamsters' action selection initialized!")
        logger.info(f"🐹🔬 Exploration rate: {self.epsilon:.1%} (planner owns execution strategy)")
        
    async def select_action(
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
        
        # Identify the storage goal — WHAT problem are we solving?
        # The ExecutionPlanner will figure out HOW to solve it.
        goal = await self._identify_issue_type(context)

        # EPSILON-GREEDY EXPLORATION: Sometimes try an alternative goal framing.
        # With the new architecture, exploration means trying a different goal
        # classification (e.g. treating disk_high as log_overflow to see if
        # log-focused primitives work better). The planner handles the rest.
        if random.random() < self.epsilon:
            alternative_goals = [g for g in self.STORAGE_GOALS if g != goal]
            if alternative_goals:
                explored_goal = random.choice(alternative_goals)
                logger.info(
                    f"🐹🔬 EXPLORING alternative goal: {explored_goal} "
                    f"(was: {goal}, epsilon={self.epsilon:.1%})"
                )
                goal = explored_goal
                self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        # Build sudo command hint — the planner will use this if the first
        # primitive in the composed sequence requires sudo.
        sudo_command = None
        if reasoning.requires_sudo:
            sudo_command = self._build_sudo_command(goal, context)
        
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
            goal=goal,
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
            f"🐹✅ Goal selected: {goal}, "
            f"beers={total_beers}, duct_tape={action.duct_tape_rolls:.1f} rolls, "
            f"strategy={execution_strategy}"
        )
        
        if sudo_command:
            logger.info(f"🐹🔧 Sudo hint: {sudo_command}")
        
        return action
    
    async def _identify_issue_type(self, context: HamstersPerceptionContext) -> str:
        """
        Identify the storage goal — WHAT problem needs solving.

        Returns a goal string from STORAGE_GOALS vocabulary.
        The ExecutionPlanner resolves this into a primitive sequence.

        Pulls from learned_thresholds so adaptive thresholds flow into
        goal classification, not just into the decision to act.
        """
        disk_usage = context.disk_usage_percent
        fragmentation = context.fragmentation_level
        inode_usage = context.inode_usage_percent

        if self.learned_thresholds:
            disk_critical = await self.learned_thresholds.get_threshold('disk_usage', 'critical')
            disk_warning = await self.learned_thresholds.get_threshold('disk_usage', 'warning')
            frag_warning = await self.learned_thresholds.get_threshold('fragmentation', 'warning')
            inode_critical = await self.learned_thresholds.get_threshold('inode_usage', 'critical')
            inode_warning = await self.learned_thresholds.get_threshold('inode_usage', 'warning')
        else:
            logger.error(
                "🐹💥 LEARNED THRESHOLDS UNAVAILABLE in _identify_issue_type — "
                "cannot classify storage issue without adaptive thresholds"
            )
            raise MLPipelineFailure(
                "Cannot identify issue type without learned thresholds. "
                "Ensure db is passed to HamstersActionSelection."
            )

        # --- Combination checks first (most specific) ---

        # Inode exhaustion: inodes full even if disk has space
        if inode_usage > inode_critical:
            logger.warning(
                f"🐹🔴 Inode exhaustion: {inode_usage:.1f}% "
                f"(critical threshold: {inode_critical:.1f}%)"
            )
            return 'inode_exhaustion'

        # Inode warning
        if inode_usage > inode_warning:
            logger.info(f"🐹🟡 Inode pressure: {inode_usage:.1f}%")
            return 'inode_high'

        # Disk critical AND fragmented: compound goal
        if disk_usage > disk_critical and fragmentation > frag_warning:
            logger.warning(
                f"🐹🔴 Disk critical + fragmentation: disk={disk_usage:.1f}%, "
                f"frag={fragmentation:.1f}%"
            )
            return 'disk_full_and_fragmented'

        # Disk critical alone
        if disk_usage > disk_critical:
            return 'disk_full'

        # High fragmentation (performance issue, not space)
        if fragmentation > frag_warning:
            return 'fragmentation_high'

        # Disk warning + inode warning: log overflow likely
        if disk_usage > disk_warning and inode_usage > inode_warning:
            logger.info(
                f"🐹🟡 Disk warning + inode pressure: disk={disk_usage:.1f}%, "
                f"inodes={inode_usage:.1f}%"
            )
            return 'log_overflow'

        # Disk warning alone
        if disk_usage > disk_warning:
            return 'disk_high'

        return 'preventive_maintenance'

    def _build_sudo_command(
        self,
        goal: str,
        context: HamstersPerceptionContext
    ) -> Optional[str]:
        """
        Build a sudo command hint for the goal.

        This is informational — the PrimitiveExecutor handles actual sudo
        execution per-primitive. This hint is logged and included in the
        action record for audit purposes.
        """
        if goal in ('ssd_needs_trim', 'slow_disk_io', 'preventive_maintenance'):
            return "sudo fstrim -av"
        elif goal in ('fragmentation_critical', 'fragmentation_high'):
            return "sudo e4defrag -c /"
        elif goal == 'disk_full_and_fragmented':
            return "sudo fstrim -av && sudo e4defrag -c /"
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
        # TODO(post-launch): Replace with learned duration estimates from
        # ExecutionResult.total_duration_seconds recorded in learning.py.
        # These are goal-level estimates; actual duration depends on the
        # primitive sequence the planner composes.
        base_durations = {
            'disk_full':                10,
            'disk_high':                10,
            'fragmentation_critical':   60,
            'fragmentation_high':       30,
            'inode_exhaustion':         10,
            'inode_high':               10,
            'log_overflow':             7,
            'slow_disk_io':             10,
            'ssd_needs_trim':           5,
            'disk_full_and_fragmented': 70,
            'preventive_maintenance':   5,
            'unknown_storage_issue':    10,
        }
        
        base = base_durations.get(action_type, 10)
        
        # Adjust for disk usage
        if disk_usage > 90:
            base *= 1.5
        
        return int(base)
