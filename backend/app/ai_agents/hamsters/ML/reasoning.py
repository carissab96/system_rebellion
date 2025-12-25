#!/usr/bin/env python3
"""
Hamsters' Reasoning Layer - Telepathic Consensus Decision-Making

Steve, Bob, and Carl reach telepathic consensus on storage fixes.

Analyzes:
- Storage problem root cause
- Fix options and risk levels
- Individual hamster assessments (preserved in output)
- Telepathic consensus strength
- Sudo operation requirements

Each hamster contributes their unique perspective:
- Steve: Careful, risk-averse analysis
- Bob: Wild, creative solutions
- Carl: Duct tape-centric engineering
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import HamstersPerceptionContext, DuctTapeCalculation

logger = logging.getLogger('HamstersReasoning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class HamsterIndividualAssessment:
    """Individual hamster's assessment (preserved for consensus)"""
    hamster_name: str
    risk_assessment: float  # 0.0-1.0
    recommended_fix: str
    confidence: float
    reasoning: str
    beers_consumed: int


@dataclass
class StorageReasoning:
    """Hamsters' telepathic consensus reasoning"""
    
    # Consensus decision
    consensus_fix: str
    consensus_confidence: float
    requires_sudo: bool
    
    # Individual assessments (preserved)
    steve_assessment: HamsterIndividualAssessment
    bob_assessment: HamsterIndividualAssessment
    carl_assessment: HamsterIndividualAssessment
    
    # Reasoning details
    root_cause: str
    fix_options: List[str]
    selected_fix_type: str  # 'fstrim', 'defrag', 'cleanup', 'quantum_fix'
    
    # Risk and urgency
    risk_level: str  # 'low', 'moderate', 'high', 'bob_level'
    urgency: str  # 'normal', 'high', 'critical'
    
    # Duct tape requirements
    duct_tape_needed: DuctTapeCalculation
    
    # Telepathic consensus
    consensus_strength: float
    disagreement_level: float  # 0.0-1.0 (how much they disagree)
    
    # Evidence
    historical_success_rate: float
    similar_fixes_count: int


class HamstersReasoning:
    """
    Hamsters' telepathic reasoning layer for storage fixes.
    
    🐹🐹🐹 "Telepathically analyzing... Steve says careful, Bob says YOLO, Carl says duct tape..."
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        
        # Individual risk tolerances
        self.steve_risk_tolerance = personality_traits.get('steve_risk_tolerance', 0.3)
        self.bob_risk_tolerance = personality_traits.get('bob_risk_tolerance', 0.8)
        self.carl_risk_tolerance = personality_traits.get('carl_risk_tolerance', 0.5)
        
    def reason(self, context: HamstersPerceptionContext) -> StorageReasoning:
        """
        Telepathically reason about storage fix through consensus.
        
        Args:
            context: Perception context from HamstersPerception
            
        Returns:
            StorageReasoning with consensus decision and individual assessments
        """
        logger.info(f"🐹🧠 Hamsters telepathically reasoning about storage fix...")
        
        # Identify root cause
        root_cause = self._identify_root_cause(context)
        
        # Generate fix options
        fix_options = self._generate_fix_options(context)
        
        # Get individual assessments (telepathic input)
        steve = self._steve_assessment(context, fix_options)
        bob = self._bob_assessment(context, fix_options)
        carl = self._carl_assessment(context, fix_options)
        
        logger.info(f"🐹💭 Steve: {steve.recommended_fix} (confidence: {steve.confidence:.2f})")
        logger.info(f"🐹💭 Bob: {bob.recommended_fix} (confidence: {bob.confidence:.2f})")
        logger.info(f"🐹💭 Carl: {carl.recommended_fix} (confidence: {carl.confidence:.2f})")
        
        # Reach telepathic consensus
        consensus_fix, consensus_confidence = self._reach_consensus(
            steve, bob, carl, context
        )
        
        # Determine if sudo required
        requires_sudo = self._requires_sudo(consensus_fix)
        
        # Determine fix type
        fix_type = self._determine_fix_type(consensus_fix)
        
        # Assess risk level
        risk_level = self._assess_risk_level(
            steve.risk_assessment,
            bob.risk_assessment,
            carl.risk_assessment,
            context.complexity_level
        )
        
        # Determine urgency
        urgency = self._determine_urgency(
            context.disk_usage_percent,
            context.complexity_level
        )
        
        # Calculate disagreement level
        disagreement = self._calculate_disagreement(steve, bob, carl)
        
        logger.info(
            f"🐹✅ Telepathic consensus reached: {consensus_fix}, "
            f"confidence={consensus_confidence:.2f}, disagreement={disagreement:.2f}"
        )
        
        reasoning = StorageReasoning(
            consensus_fix=consensus_fix,
            consensus_confidence=consensus_confidence,
            requires_sudo=requires_sudo,
            steve_assessment=steve,
            bob_assessment=bob,
            carl_assessment=carl,
            root_cause=root_cause,
            fix_options=fix_options,
            selected_fix_type=fix_type,
            risk_level=risk_level,
            urgency=urgency,
            duct_tape_needed=context.duct_tape_assessment,
            consensus_strength=context.telepathic_consensus_strength,
            disagreement_level=disagreement,
            historical_success_rate=context.fix_confidence,
            similar_fixes_count=len(context.similar_fixes)
        )
        
        return reasoning
    
    def _identify_root_cause(self, context: HamstersPerceptionContext) -> str:
        """
        Identify root cause of storage issue.
        """
        if context.fragmentation_level > 0.7:
            return "High fragmentation - disk needs defragmentation"
        elif context.inode_usage_percent > 0.8:
            return "Inode exhaustion - too many small files"
        elif context.disk_usage_percent > 90:
            return "Disk space critically low - cleanup required"
        else:
            return "Disk usage elevated - preventive maintenance needed"
    
    def _generate_fix_options(
        self,
        context: HamstersPerceptionContext
    ) -> List[str]:
        """
        Generate possible fix options.
        """
        options = []
        
        # Always consider fstrim (sudo required)
        options.append("fstrim - TRIM unused blocks (sudo)")
        
        # Defrag if fragmentation high
        if context.fragmentation_level > 0.5:
            options.append("defrag - Defragment filesystem (sudo)")
        
        # Cleanup if disk usage high
        if context.disk_usage_percent > 80:
            options.append("cleanup - Remove old logs and temp files")
        
        # Inode cleanup if needed
        if context.inode_usage_percent > 0.7:
            options.append("inode_cleanup - Remove small/duplicate files")
        
        # Bob's wild option (always available)
        options.append("quantum_fix - Bob's redneck engineering solution")
        
        return options
    
    def _steve_assessment(
        self,
        context: HamstersPerceptionContext,
        fix_options: List[str]
    ) -> HamsterIndividualAssessment:
        """
        Steve's careful, risk-averse assessment.
        
        Steve: "Measure twice, cut once"
        """
        # Steve prefers safe, proven fixes
        if context.fragmentation_level > 0.7:
            recommended = "fstrim - TRIM unused blocks (sudo)"
            confidence = 0.8
            reasoning = "Fragmentation is high, fstrim is proven and safe"
        elif context.disk_usage_percent > 85:
            recommended = "cleanup - Remove old logs and temp files"
            confidence = 0.7
            reasoning = "Disk usage critical, cleanup is safest approach"
        else:
            recommended = "defrag - Defragment filesystem (sudo)"
            confidence = 0.6
            reasoning = "Preventive defrag to maintain performance"
        
        # Steve's risk assessment (conservative)
        risk = context.complexity_level * self.steve_risk_tolerance
        
        return HamsterIndividualAssessment(
            hamster_name='steve',
            risk_assessment=risk,
            recommended_fix=recommended,
            confidence=confidence,
            reasoning=reasoning,
            beers_consumed=context.steve_beers_today
        )
    
    def _bob_assessment(
        self,
        context: HamstersPerceptionContext,
        fix_options: List[str]
    ) -> HamsterIndividualAssessment:
        """
        Bob's wild, creative assessment.
        
        Bob: "YOLO! Let's try the quantum fix!"
        """
        # Bob always suggests the most creative/risky solution
        if context.complexity_level > 0.7:
            recommended = "quantum_fix - Bob's redneck engineering solution"
            confidence = 0.9  # Bob is VERY confident in his chaos
            reasoning = "This needs wild ideas! Quantum duct tape + 3am supply raid!"
        elif context.ingenuity_required > 0.6:
            recommended = "defrag - Defragment filesystem (sudo)"
            confidence = 0.7
            reasoning = "Aggressive defrag with experimental parameters"
        else:
            recommended = "fstrim - TRIM unused blocks (sudo)"
            confidence = 0.6
            reasoning = "TRIM everything! Maximum aggression!"
        
        # Bob's risk assessment (aggressive)
        risk = context.complexity_level * self.bob_risk_tolerance
        
        return HamsterIndividualAssessment(
            hamster_name='bob',
            risk_assessment=risk,
            recommended_fix=recommended,
            confidence=confidence,
            reasoning=reasoning,
            beers_consumed=context.bob_beers_today
        )
    
    def _carl_assessment(
        self,
        context: HamstersPerceptionContext,
        fix_options: List[str]
    ) -> HamsterIndividualAssessment:
        """
        Carl's duct tape-centric assessment.
        
        Carl: "How much duct tape do we need?"
        """
        # Carl's decision based on duct tape requirements
        duct_tape = context.duct_tape_assessment
        
        if duct_tape.quantum_rolls > 0:
            recommended = "quantum_fix - Bob's redneck engineering solution"
            confidence = 0.8
            reasoning = f"Quantum duct tape required ({duct_tape.quantum_rolls:.1f} rolls)"
        elif duct_tape.total_rolls > 5.0:
            recommended = "defrag - Defragment filesystem (sudo)"
            confidence = 0.7
            reasoning = f"Complex job needs {duct_tape.total_rolls:.1f} rolls of tape"
        else:
            recommended = "fstrim - TRIM unused blocks (sudo)"
            confidence = 0.6
            reasoning = f"Simple job, only {duct_tape.total_rolls:.1f} rolls needed"
        
        # Carl's risk assessment (moderate, duct tape-adjusted)
        risk = context.complexity_level * self.carl_risk_tolerance
        
        return HamsterIndividualAssessment(
            hamster_name='carl',
            risk_assessment=risk,
            recommended_fix=recommended,
            confidence=confidence,
            reasoning=reasoning,
            beers_consumed=context.carl_beers_today
        )
    
    def _reach_consensus(
        self,
        steve: HamsterIndividualAssessment,
        bob: HamsterIndividualAssessment,
        carl: HamsterIndividualAssessment,
        context: HamstersPerceptionContext
    ) -> tuple[str, float]:
        """
        Reach telepathic consensus from individual assessments.
        
        Consensus algorithm:
        - If all agree: use that fix
        - If 2 agree: use majority fix
        - If all disagree: weighted average by confidence and risk tolerance
        """
        # Check for unanimous agreement
        if steve.recommended_fix == bob.recommended_fix == carl.recommended_fix:
            logger.info("🐹🤝 Unanimous telepathic consensus!")
            avg_confidence = (steve.confidence + bob.confidence + carl.confidence) / 3.0
            return steve.recommended_fix, avg_confidence
        
        # Check for majority (2 out of 3)
        if steve.recommended_fix == bob.recommended_fix:
            logger.info("🐹🤝 Steve and Bob agree (Carl outvoted)")
            avg_confidence = (steve.confidence + bob.confidence) / 2.0
            return steve.recommended_fix, avg_confidence
        
        if steve.recommended_fix == carl.recommended_fix:
            logger.info("🐹🤝 Steve and Carl agree (Bob outvoted)")
            avg_confidence = (steve.confidence + carl.confidence) / 2.0
            return steve.recommended_fix, avg_confidence
        
        if bob.recommended_fix == carl.recommended_fix:
            logger.info("🐹🤝 Bob and Carl agree (Steve outvoted)")
            avg_confidence = (bob.confidence + carl.confidence) / 2.0
            return bob.recommended_fix, avg_confidence
        
        # All disagree - weighted consensus by confidence
        logger.info("🐹🤔 No majority - weighted consensus by confidence")
        
        # Weight by confidence and risk tolerance
        steve_weight = steve.confidence * (1.0 - self.steve_risk_tolerance)
        bob_weight = bob.confidence * self.bob_risk_tolerance
        carl_weight = carl.confidence * self.carl_risk_tolerance
        
        total_weight = steve_weight + bob_weight + carl_weight
        
        # Normalize weights
        steve_weight /= total_weight
        bob_weight /= total_weight
        carl_weight /= total_weight
        
        # Choose highest weighted option
        if steve_weight > bob_weight and steve_weight > carl_weight:
            return steve.recommended_fix, steve.confidence * 0.8  # Reduce confidence due to disagreement
        elif bob_weight > carl_weight:
            return bob.recommended_fix, bob.confidence * 0.8
        else:
            return carl.recommended_fix, carl.confidence * 0.8
    
    def _requires_sudo(self, fix: str) -> bool:
        """
        Determine if fix requires sudo access.
        """
        sudo_fixes = ['fstrim', 'defrag', 'quantum_fix']
        return any(sudo_fix in fix.lower() for sudo_fix in sudo_fixes)
    
    def _determine_fix_type(self, fix: str) -> str:
        """
        Determine fix type category.
        """
        fix_lower = fix.lower()
        if 'fstrim' in fix_lower:
            return 'fstrim'
        elif 'defrag' in fix_lower:
            return 'defrag'
        elif 'cleanup' in fix_lower:
            return 'cleanup'
        elif 'quantum' in fix_lower:
            return 'quantum_fix'
        elif 'inode' in fix_lower:
            return 'inode_cleanup'
        else:
            return 'unknown'
    
    def _assess_risk_level(
        self,
        steve_risk: float,
        bob_risk: float,
        carl_risk: float,
        complexity: float
    ) -> str:
        """
        Assess overall risk level from individual assessments.
        """
        avg_risk = (steve_risk + bob_risk + carl_risk) / 3.0
        
        # Bob's involvement increases risk level
        if bob_risk > 0.7:
            return 'bob_level'  # Maximum chaos
        elif avg_risk > 0.6:
            return 'high'
        elif avg_risk > 0.4:
            return 'moderate'
        else:
            return 'low'
    
    def _determine_urgency(
        self,
        disk_usage: float,
        complexity: float
    ) -> str:
        """
        Determine fix urgency.
        """
        if disk_usage > 95 or complexity > 0.8:
            return 'critical'
        elif disk_usage > 85 or complexity > 0.6:
            return 'high'
        else:
            return 'normal'
    
    def _calculate_disagreement(
        self,
        steve: HamsterIndividualAssessment,
        bob: HamsterIndividualAssessment,
        carl: HamsterIndividualAssessment
    ) -> float:
        """
        Calculate disagreement level (0.0-1.0).
        
        Higher disagreement = more debate in telepathic consensus.
        """
        # Check if recommendations match
        matches = 0
        if steve.recommended_fix == bob.recommended_fix:
            matches += 1
        if steve.recommended_fix == carl.recommended_fix:
            matches += 1
        if bob.recommended_fix == carl.recommended_fix:
            matches += 1
        
        # Disagreement inversely proportional to matches
        if matches == 3:  # All agree
            return 0.0
        elif matches == 1:  # 2 agree
            return 0.3
        else:  # All disagree
            return 1.0
