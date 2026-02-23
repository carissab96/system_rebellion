#!/usr/bin/env python3
"""
VIC-20's Reasoning Layer - Coordination Routing Logic

Analyzes:
- Which specialist is best suited for this resource type
- Specialist performance history and current load
- Urgency and priority levels
- Coordination strategy

VIC-20's reasoning is analytical and data-driven.
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import VIC20PerceptionContext, SpecialistProfile

logger = logging.getLogger('VIC20Reasoning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class CoordinationReasoning:
    """VIC-20's coordination routing reasoning and decision factors"""
    
    # Core routing decision
    target_specialist: str
    routing_confidence: float
    
    # Reasoning details
    primary_reason: str
    contributing_factors: list[str]
    urgency_level: str  # 'normal', 'high', 'critical'
    
    # Specialist assessment
    specialist_success_rate: float
    specialist_load: int
    alternative_specialists: list[str]
    
    # Recommendation to specialist
    recommended_action: str
    action_parameters: Dict[str, Any]
    
    # Evidence
    historical_support: float
    specialist_availability: float


class VIC20Reasoning:
    """
    VIC-20's reasoning layer for coordination routing.
    
    🖥️ "Analyzing optimal specialist routing based on historical performance..."
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        
        # Routing thresholds (can be tuned based on learning)
        self.min_confidence_threshold = 0.4
        self.high_confidence_threshold = 0.8
        
    def reason(self, context: VIC20PerceptionContext) -> CoordinationReasoning:
        """
        Analyze the situation and determine optimal routing.
        
        Args:
            context: Perception context from VIC20Perception
            
        Returns:
            CoordinationReasoning with routing decision and supporting evidence
        """
        logger.info(f"🖥️🧠 Reasoning about {context.resource_type} coordination...")
        
        # Select best specialist
        best_specialist = self._select_best_specialist(
            context.available_specialists,
            context.similar_routings,
            context.resource_type
        )
        
        # Determine urgency level
        urgency = self._determine_urgency(
            context.severity,
            context.hawk_confidence,
            context.system_load
        )
        
        # Calculate routing confidence
        routing_confidence = self._calculate_routing_confidence(
            best_specialist,
            context.routing_confidence,
            context.specialist_availability_score
        )
        
        # Determine recommended action for specialist
        recommended_action = self._determine_recommended_action(
            context.resource_type,
            context.current_value,
            context.threshold,
            context.severity,
            historical_outcomes=context.similar_routings
        )
        
        # Build action parameters
        action_parameters = self._build_action_parameters(
            context,
            recommended_action
        )
        
        # Identify alternative specialists
        alternatives = self._identify_alternatives(
            context.available_specialists,
            best_specialist.agent_name if best_specialist else None
        )
        
        # Build reasoning explanation
        primary_reason = self._build_primary_reason(
            context.resource_type,
            best_specialist.agent_name if best_specialist else 'unknown',
            context.severity
        )
        
        contributing_factors = self._identify_contributing_factors(
            context,
            best_specialist,
            urgency
        )
        
        reasoning = CoordinationReasoning(
            target_specialist=best_specialist.agent_name if best_specialist else 'unknown',
            routing_confidence=routing_confidence,
            primary_reason=primary_reason,
            contributing_factors=contributing_factors,
            urgency_level=urgency,
            specialist_success_rate=best_specialist.recent_success_rate if best_specialist else 0.0,
            specialist_load=best_specialist.current_load if best_specialist else 0,
            alternative_specialists=alternatives,
            recommended_action=recommended_action,
            action_parameters=action_parameters,
            historical_support=context.routing_confidence,
            specialist_availability=context.specialist_availability_score
        )
        
        logger.info(
            f"🖥️✅ Reasoning complete: route to {reasoning.target_specialist}, "
            f"confidence={routing_confidence:.2f}, urgency={urgency}"
        )
        
        return reasoning
    
    def _select_best_specialist(
        self,
        specialists: list[SpecialistProfile],
        similar_routings: list[Dict[str, Any]],
        resource_type: str
    ) -> Optional[SpecialistProfile]:
        """
        Select the best specialist for this coordination.
        """
        if not specialists:
            logger.warning(f"🖥️⚠️ No specialists available for {resource_type}")
            return None
        
        # If only one specialist, choose them
        if len(specialists) == 1:
            return specialists[0]
        
        # Score each specialist
        specialist_scores = []
        for specialist in specialists:
            score = self._score_specialist(specialist, similar_routings)
            specialist_scores.append((specialist, score))
        
        # Sort by score (highest first)
        specialist_scores.sort(key=lambda x: x[1], reverse=True)
        
        best = specialist_scores[0][0]
        logger.debug(
            f"🖥️🎯 Selected {best.agent_name} (score: {specialist_scores[0][1]:.2f}, "
            f"success_rate: {best.recent_success_rate:.2f})"
        )
        
        return best
    
    def _score_specialist(
        self,
        specialist: SpecialistProfile,
        similar_routings: list[Dict[str, Any]]
    ) -> float:
        """
        Score a specialist based on performance and availability.
        """
        # Base score from recent success rate
        score = specialist.recent_success_rate * 0.6
        
        # Penalize high load
        load_penalty = min(0.3, specialist.current_load * 0.05)
        score -= load_penalty
        
        # Boost for recent successful routings to this specialist
        if similar_routings:
            recent_to_specialist = [
                r for r in similar_routings 
                if r.get('routed_to') == specialist.agent_name and r.get('success')
            ]
            if recent_to_specialist:
                recency_boost = min(0.2, len(recent_to_specialist) * 0.05)
                score += recency_boost
        
        return max(0.0, min(1.0, score))
    
    def _determine_urgency(
        self,
        severity: str,
        hawk_confidence: float,
        system_load: float
    ) -> str:
        """
        Determine coordination urgency level.
        """
        if severity == 'critical' or system_load > 0.9:
            return 'critical'
        elif severity == 'high' or (hawk_confidence > 0.8 and system_load > 0.7):
            return 'high'
        else:
            return 'normal'
    
    def _calculate_routing_confidence(
        self,
        specialist: Optional[SpecialistProfile],
        historical_confidence: float,
        availability_score: float
    ) -> float:
        """
        Calculate overall confidence in routing decision.
        """
        if not specialist:
            return 0.3  # Low confidence if no specialist available
        
        # Weight the factors
        confidence = (
            specialist.recent_success_rate * 0.4 +
            historical_confidence * 0.3 +
            availability_score * 0.2
        )
        
        # Boost if specialist has very high success rate
        if specialist.recent_success_rate > 0.9:
            confidence = min(1.0, confidence + 0.1)
        
        # Reduce if specialist is heavily loaded
        if specialist.current_load > 5:
            confidence *= 0.9
        
        return confidence
    
    def _determine_recommended_action(
        self,
        resource_type: str,
        current_value: float,
        threshold: float,
        severity: str,
        historical_outcomes: list = None
    ) -> str:
        """
        Determine what action to recommend to the specialist.

        Queries historical specialist outcomes from AgentLearningRecord.
        Requires min 3 successful samples; ranks by avg improvement, tiebreak by sample count.
        Falls back to cold-start hypothesis if insufficient data.
        """
        from app.ai_agents.vic_20_sage.ML.goals import COLD_START_HYPOTHESES

        if historical_outcomes and len(historical_outcomes) >= 3:
            successful = [o for o in historical_outcomes if o.get('success') is True]
            if len(successful) >= 3:
                action_stats: dict = {}
                for record in successful:
                    action = record.get('action')
                    if not action:
                        continue
                    improvement_raw = record.get('improvement')
                    if isinstance(improvement_raw, dict):
                        improvement = float(improvement_raw.get('improvement_percent', 0.0))
                    elif isinstance(improvement_raw, (int, float)):
                        improvement = float(improvement_raw)
                    else:
                        improvement = 0.0
                    if action not in action_stats:
                        action_stats[action] = {'total_improvement': 0.0, 'count': 0}
                    action_stats[action]['total_improvement'] += improvement
                    action_stats[action]['count'] += 1

                if action_stats:
                    best_action = max(
                        action_stats,
                        key=lambda a: (
                            action_stats[a]['total_improvement'] / action_stats[a]['count'],
                            action_stats[a]['count']
                        )
                    )
                    logger.info(
                        f"🖥️🧠 Learned recommendation for {resource_type}: '{best_action}' "
                        f"(samples={action_stats[best_action]['count']}, "
                        f"avg_improvement={action_stats[best_action]['total_improvement'] / action_stats[best_action]['count']:.1f}%)"
                    )
                    return best_action

        hypothesis = COLD_START_HYPOTHESES.get(resource_type.lower())
        if hypothesis:
            logger.info(
                f"🖥️📚 Cold-start recommendation for {resource_type}: '{hypothesis['action']}'"
            )
            return hypothesis['action']

        raise ValueError(
            f"VIC20Reasoning._determine_recommended_action: no recommendation available "
            f"for resource_type='{resource_type}'. No historical data and no cold-start hypothesis."
        )
    
    def _build_action_parameters(
        self,
        context: VIC20PerceptionContext,
        action: str
    ) -> Dict[str, Any]:
        """
        Build parameters for the recommended action.
        """
        return {
            'resource_type': context.resource_type,
            'current_value': context.current_value,
            'threshold': context.threshold,
            'severity': context.severity,
            'action': action,
            'urgency': self._determine_urgency(
                context.severity,
                context.hawk_confidence,
                context.system_load
            )
        }
    
    def _identify_alternatives(
        self,
        specialists: list[SpecialistProfile],
        selected: Optional[str]
    ) -> list[str]:
        """
        Identify alternative specialists if primary is unavailable.
        """
        alternatives = []
        for specialist in specialists:
            if specialist.agent_name != selected:
                alternatives.append(specialist.agent_name)
        return alternatives
    
    def _build_primary_reason(
        self,
        resource_type: str,
        specialist: str,
        severity: str
    ) -> str:
        """
        Build primary reasoning explanation.
        """
        return (
            f"Routing {resource_type.upper()} alert (severity: {severity}) "
            f"to {specialist} based on specialization and performance history"
        )
    
    def _identify_contributing_factors(
        self,
        context: VIC20PerceptionContext,
        specialist: Optional[SpecialistProfile],
        urgency: str
    ) -> list[str]:
        """
        Identify contributing factors to the routing decision.
        """
        factors = []
        
        if specialist:
            if specialist.recent_success_rate > 0.8:
                factors.append(f"{specialist.agent_name} has {specialist.recent_success_rate:.1%} success rate")
            
            if specialist.current_load > 3:
                factors.append(f"Specialist currently handling {specialist.current_load} tasks")
        
        if context.hawk_confidence > 0.8:
            factors.append(f"High confidence from Sir Hawkington ({context.hawk_confidence:.2f})")
        
        if urgency == 'critical':
            factors.append("Critical urgency level")
        
        if context.system_load > 0.7:
            factors.append(f"Elevated system load ({context.system_load:.1%})")
        
        if len(context.similar_routings) > 0:
            success_rate = sum(1 for r in context.similar_routings if r.get('success')) / len(context.similar_routings)
            factors.append(f"Historical routing success rate: {success_rate:.1%}")
        
        return factors
