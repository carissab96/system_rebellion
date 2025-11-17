"""
Agent Autonomy and Choice Engine (Task 4.1 Enhanced)
====================================================

Gives agents the ability to CHOOSE whether to follow VIC-20's recommendations
or develop their own fixes based on personality and trust levels.
"""

import logging
import random
from typing import Dict, Any, Optional
from enum import Enum


logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """How much an agent trusts VIC-20's recommendations"""
    VERY_LOW = 0.2    # "I know better!" - Terry
    LOW = 0.4         # "Hmm, not sure..." - QSP
    MEDIUM = 0.6      # "Reasonable suggestion"
    HIGH = 0.8        # "VIC-20 knows best" - Hamsters
    VERY_HIGH = 0.95  # "Always trust the coordinator"


class AgentChoiceEngine:
    """
    Enables agents to make autonomous choices about following recommendations.
    
    Each agent has personality-based trust levels and decision-making logic.
    """
    
    def __init__(self, agent_name: str, personality_traits: Dict[str, Any]):
        self.agent_name = agent_name
        self.personality = personality_traits
        self.logger = logging.getLogger(f"ChoiceEngine.{agent_name}")
        
        # Set trust level based on agent personality
        self.vic20_trust_level = self._determine_trust_level()
        
        # Track decision history
        self.decisions_made = []
        self.recommendations_followed = 0
        self.own_solutions_used = 0
    
    def _determine_trust_level(self) -> TrustLevel:
        """Determine trust level based on agent personality"""
        
        # Meth Snail (Terry) - Very low trust, hyperactive, does own thing
        if self.agent_name == "meth_snail":
            return TrustLevel.VERY_LOW
        
        # Hamsters - High trust, telepathic consensus, team players
        elif self.agent_name == "hamsters":
            return TrustLevel.HIGH
        
        # QSP - Low trust, paranoid, questions everything
        elif self.agent_name == "quantum_shadow_people":
            return TrustLevel.LOW
        
        # VIC-20 - Doesn't receive recommendations from himself
        elif self.agent_name == "vic_20_sage":
            return TrustLevel.VERY_HIGH
        
        # The Stick - Medium trust, learning-focused
        elif self.agent_name == "the_stick":
            return TrustLevel.MEDIUM
        
        # Sir Hawkington - Medium trust, but aristocratic independence
        elif self.agent_name == "sir_hawkington":
            return TrustLevel.MEDIUM
        
        else:
            return TrustLevel.MEDIUM
    
    def should_follow_recommendation(
        self,
        recommendation: Dict[str, Any],
        current_situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Decide whether to follow VIC-20's recommendation or develop own solution.
        
        Args:
            recommendation: VIC-20's recommendation dict
            current_situation: Current resource situation
            
        Returns:
            Decision dict with choice, reasoning, and action to take
        """
        confidence = recommendation.get('confidence', 0.5)
        urgency = recommendation.get('urgency', 'medium')
        suggested_action = recommendation.get('suggested_action', 'monitor_and_wait')
        
        # Calculate decision score
        decision_score = self._calculate_decision_score(
            confidence,
            urgency,
            current_situation
        )
        
        # Make the choice
        follow_recommendation = decision_score >= self.vic20_trust_level.value
        
        # Generate reasoning based on personality
        reasoning = self._generate_reasoning(
            follow_recommendation,
            confidence,
            urgency,
            suggested_action
        )
        
        # Determine final action
        if follow_recommendation:
            final_action = suggested_action
            self.recommendations_followed += 1
        else:
            final_action = self._develop_own_solution(current_situation)
            self.own_solutions_used += 1
        
        decision = {
            "agent": self.agent_name,
            "recommendation_received": suggested_action,
            "recommendation_confidence": confidence,
            "urgency": urgency,
            "trust_level": self.vic20_trust_level.value,
            "decision_score": decision_score,
            "followed_recommendation": follow_recommendation,
            "final_action": final_action,
            "reasoning": reasoning,
            "personality_influence": self._get_personality_influence()
        }
        
        self.decisions_made.append(decision)
        
        self.logger.info(
            f"{'✅' if follow_recommendation else '🔧'} {self.agent_name}: "
            f"{'Following' if follow_recommendation else 'Overriding'} VIC-20's recommendation "
            f"({suggested_action} → {final_action})"
        )
        self.logger.debug(f"Reasoning: {reasoning}")
        
        return decision
    
    def _calculate_decision_score(
        self,
        confidence: float,
        urgency: str,
        current_situation: Dict[str, Any]
    ) -> float:
        """
        Calculate a score to determine if recommendation should be followed.
        
        Higher score = more likely to follow recommendation
        """
        base_score = confidence
        
        # Urgency modifier
        urgency_modifiers = {
            'critical': 0.3,    # More likely to follow in critical situations
            'high': 0.2,
            'medium': 0.1,
            'low': 0.0
        }
        base_score += urgency_modifiers.get(urgency, 0.0)
        
        # Personality modifiers
        if self.agent_name == "meth_snail":
            # Terry is impulsive and doesn't trust recommendations
            base_score -= 0.3
            # But if it's REALLY critical, even Terry listens
            if urgency == 'critical':
                base_score += 0.2
        
        elif self.agent_name == "hamsters":
            # Hamsters trust the team
            base_score += 0.2
            # Telepathic consensus always agrees with VIC-20
            if confidence > 0.7:
                base_score += 0.1
        
        elif self.agent_name == "quantum_shadow_people":
            # QSP is paranoid and questions everything
            base_score -= 0.2
            # But security threats override paranoia
            if current_situation.get('security_threat'):
                base_score += 0.3
        
        elif self.agent_name == "sir_hawkington":
            # Aristocratic independence
            base_score -= 0.1
            # But respects VIC-20's wisdom
            if confidence > 0.8:
                base_score += 0.15
        
        # Clamp to 0-1 range
        return max(0.0, min(1.0, base_score))
    
    def _generate_reasoning(
        self,
        following: bool,
        confidence: float,
        urgency: str,
        action: str
    ) -> str:
        """Generate personality-appropriate reasoning"""
        
        if self.agent_name == "meth_snail":
            if following:
                return (
                    f"🐌💨 FINE! VIC-20's {action} might work, but I could do it FASTER! "
                    f"Urgency is {urgency} so I'll try it... *spins shell nervously*"
                )
            else:
                return (
                    f"🐌💨 NAH! VIC-20 is too SLOW! I've got a BETTER idea that's "
                    f"MUCH FASTER! *chugs energy drink* LET'S GOOOOO!"
                )
        
        elif self.agent_name == "hamsters":
            if following:
                return (
                    f"🐹🐹🐹 Steve, Bob, and Carl reached telepathic consensus: "
                    f"VIC-20's {action} is solid. Beer-fueled wisdom agrees! "
                    f"Confidence {confidence:.0%} is good enough for us."
                )
            else:
                return (
                    f"🐹🐹🐹 Telepathic consensus says we know a better way! "
                    f"We've been fixing disks since before VIC-20 was cool. "
                    f"*cracks open beer* Let's do this OUR way!"
                )
        
        elif self.agent_name == "quantum_shadow_people":
            if following:
                return (
                    f"🔮 After quantum phase analysis and 3 tequila jello shots, "
                    f"we've determined VIC-20's {action} is... acceptable. "
                    f"Urgency {urgency} warrants action. Proceeding with caution."
                )
            else:
                return (
                    f"🔮 SUSPICIOUS! VIC-20's recommendation doesn't align with our "
                    f"quantum security protocols. We've detected a better approach "
                    f"through paranoid analysis. Trust no one, not even coordinators!"
                )
        
        elif self.agent_name == "sir_hawkington":
            if following:
                return (
                    f"🧐 VIC-20's {action} recommendation is... acceptable. "
                    f"With confidence of {confidence:.0%}, it meets aristocratic standards. "
                    f"*adjusts monocle approvingly* Proceed with distinguished grace."
                )
            else:
                return (
                    f"🧐 While VIC-20's suggestion has merit, Sir Hawkington's "
                    f"aristocratic wisdom suggests a superior approach. "
                    f"*polishes monocle* One must maintain standards, after all."
                )
        
        elif self.agent_name == "the_stick":
            if following:
                return (
                    f"🥢 VIC-20's {action} aligns with learned patterns. "
                    f"Historical data supports this approach. Proceeding patiently "
                    f"and recording results for future learning."
                )
            else:
                return (
                    f"🥢 While respecting VIC-20's recommendation, historical patterns "
                    f"suggest an alternative approach may be more effective. "
                    f"Learning opportunity detected!"
                )
        
        else:
            if following:
                return f"Following VIC-20's recommendation: {action} (confidence: {confidence:.0%})"
            else:
                return f"Developing own solution based on agent expertise"
    
    def _develop_own_solution(self, current_situation: Dict[str, Any]) -> str:
        """
        Develop agent's own solution when not following recommendation.
        
        Based on agent personality and expertise.
        """
        resource_type = current_situation.get('resource_type', 'unknown')
        
        # Agent-specific solutions
        if self.agent_name == "meth_snail":
            # Terry's solutions are aggressive and fast
            return "aggressive_cache_purge_with_shell_spin"
        
        elif self.agent_name == "hamsters":
            # Hamsters' solutions involve beer and duct tape
            return "telepathic_disk_optimization_with_beer"
        
        elif self.agent_name == "quantum_shadow_people":
            # QSP's solutions are paranoid and thorough
            return "quantum_network_lockdown_with_tequila"
        
        elif self.agent_name == "sir_hawkington":
            # Hawkington's solutions are aristocratic and measured
            return "distinguished_system_throttle_with_monocle_adjustment"
        
        elif self.agent_name == "the_stick":
            # The Stick's solutions are patient and learning-focused
            return "patient_resource_monitoring_with_pattern_analysis"
        
        else:
            return "agent_specific_solution"
    
    def _get_personality_influence(self) -> str:
        """Get description of how personality influenced decision"""
        
        influences = {
            "meth_snail": "Hyperactive, speed-obsessed, low trust in slow coordinators",
            "hamsters": "Telepathic consensus, beer-fueled wisdom, high team trust",
            "quantum_shadow_people": "Paranoid, security-focused, questions authority",
            "sir_hawkington": "Aristocratic independence, respects wisdom but maintains standards",
            "the_stick": "Patient learning, historical pattern analysis, balanced judgment"
        }
        
        return influences.get(self.agent_name, "Standard agent decision-making")
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get statistics about agent's decision-making"""
        total_decisions = len(self.decisions_made)
        
        if total_decisions == 0:
            follow_rate = 0.0
        else:
            follow_rate = self.recommendations_followed / total_decisions
        
        return {
            "agent": self.agent_name,
            "trust_level": self.vic20_trust_level.value,
            "total_decisions": total_decisions,
            "recommendations_followed": self.recommendations_followed,
            "own_solutions_used": self.own_solutions_used,
            "follow_rate": follow_rate,
            "personality_influence": self._get_personality_influence()
        }
