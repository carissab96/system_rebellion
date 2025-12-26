#!/usr/bin/env python3
"""
VIC-20's Perception Layer - Coordination Context Assessment

Collects:
- Triage alert details from Sir Hawkington
- Specialist availability and current load
- Historical routing success rates
- Recent coordination outcomes
- System-wide resource state

VIC-20 doesn't have dramatic personality behaviors like monocle yeets or shell spins.
He's the calm, analytical coordinator. His "personality" is in his routing wisdom.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.agent_learning import AgentLearningRecord

logger = logging.getLogger('VIC20Perception')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class SpecialistProfile:
    """Profile of a specialist agent for routing decisions"""
    agent_name: str
    specialties: List[str]
    recent_success_rate: float
    average_response_time: float
    current_load: int  # Number of active tasks
    last_coordination: Optional[datetime]


@dataclass
class VIC20PerceptionContext:
    """Everything VIC-20 needs to perceive for coordination routing"""
    
    # Triage alert context
    resource_type: str
    current_value: float
    threshold: float
    severity: str
    hawk_confidence: float
    
    # Specialist profiles
    available_specialists: List[SpecialistProfile] = field(default_factory=list)
    
    # Historical routing patterns
    similar_routings: List[Dict[str, Any]] = field(default_factory=list)
    recent_coordination_outcomes: List[Dict[str, Any]] = field(default_factory=list)
    
    # System state
    system_load: float = 0.0
    active_alerts: int = 0
    
    # Confidence factors
    routing_confidence: float = 0.5
    specialist_availability_score: float = 1.0


class VIC20Perception:
    """
    VIC-20's perception layer for coordination routing.
    
    🖥️ "Analyzing specialist capabilities and system state..."
    """
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any]):
        self.db = db
        self.personality_traits = personality_traits
        
    async def perceive(self, triage_alert: Dict[str, Any]) -> VIC20PerceptionContext:
        """
        Gather full context for coordination routing decision.
        
        Args:
            triage_alert: Triage alert from Sir Hawkington
            
        Returns:
            VIC20PerceptionContext with all relevant information
        """
        resource_type = triage_alert.get('resource_type', 'unknown')
        current_value = triage_alert.get('current_value', 0.0)
        threshold = triage_alert.get('threshold', 0.0)
        severity = triage_alert.get('severity', 'low')
        hawk_confidence = triage_alert.get('triage_confidence', 0.5)
        
        logger.info(
            f"🖥️👁️ Perceiving coordination context for {resource_type} alert "
            f"(severity: {severity}, Hawk confidence: {hawk_confidence:.2f})"
        )
        
        # Get specialist profiles
        available_specialists = await self._get_specialist_profiles(resource_type)
        
        # Retrieve historical routing patterns
        similar_routings = await self._get_similar_routings(resource_type, current_value)
        recent_outcomes = await self._get_recent_coordination_outcomes()
        
        # Assess system state
        system_load = self._assess_system_load(triage_alert)
        active_alerts = len(recent_outcomes)
        
        # Calculate routing confidence from historical data
        routing_confidence = self._calculate_routing_confidence(
            similar_routings,
            available_specialists
        )
        
        # Calculate specialist availability score
        availability_score = self._calculate_availability_score(available_specialists)
        
        context = VIC20PerceptionContext(
            resource_type=resource_type,
            current_value=current_value,
            threshold=threshold,
            severity=severity,
            hawk_confidence=hawk_confidence,
            available_specialists=available_specialists,
            similar_routings=similar_routings,
            recent_coordination_outcomes=recent_outcomes,
            system_load=system_load,
            active_alerts=active_alerts,
            routing_confidence=routing_confidence,
            specialist_availability_score=availability_score
        )
        
        logger.info(
            f"🖥️✅ Perception complete: {len(available_specialists)} specialists available, "
            f"routing_confidence={routing_confidence:.2f}, system_load={system_load:.2f}"
        )
        
        return context
    
    async def _get_specialist_profiles(
        self, 
        resource_type: str
    ) -> List[SpecialistProfile]:
        """
        Get profiles of specialists who can handle this resource type.
        """
        # Define specialist capabilities
        specialist_map = {
            'cpu': ['meth_snail'],
            'memory': ['meth_snail'],
            'swap': ['meth_snail'],
            'disk': ['hamsters'],
            'network': ['quantum_shadow_people']
        }
        
        candidates = specialist_map.get(resource_type.lower(), [])
        profiles = []
        
        for agent_name in candidates:
            profile = await self._build_specialist_profile(agent_name, resource_type)
            profiles.append(profile)
        
        logger.debug(f"🖥️📊 Found {len(profiles)} specialist(s) for {resource_type}")
        return profiles
    
    async def _build_specialist_profile(
        self,
        agent_name: str,
        resource_type: str
    ) -> SpecialistProfile:
        """
        Build a profile for a specialist based on historical performance.
        """
        try:
            # Query recent coordination outcomes for this specialist
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == agent_name)
                .where(AgentLearningRecord.resource_type == resource_type)
                .order_by(desc(AgentLearningRecord.created_at))
                .limit(20)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            # Calculate success rate
            if records:
                successful = sum(1 for r in records if r.success)
                success_rate = successful / len(records)
                
                # Get last coordination time
                last_coord = records[0].created_at if records else None
            else:
                success_rate = 0.5  # Neutral if no history
                last_coord = None
            
            # Estimate current load (simplified - could query active tasks)
            current_load = 0
            
            profile = SpecialistProfile(
                agent_name=agent_name,
                specialties=[resource_type],
                recent_success_rate=success_rate,
                average_response_time=2.0,  # Simplified
                current_load=current_load,
                last_coordination=last_coord
            )
            
            logger.debug(
                f"🖥️📋 {agent_name} profile: success_rate={success_rate:.2f}, "
                f"load={current_load}"
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"🖥️💥 Error building specialist profile for {agent_name}: {e}")
            # Return default profile
            return SpecialistProfile(
                agent_name=agent_name,
                specialties=[resource_type],
                recent_success_rate=0.5,
                average_response_time=2.0,
                current_load=0,
                last_coordination=None
            )
    
    async def _get_similar_routings(
        self,
        resource_type: str,
        current_value: float
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar routing decisions from learning history.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'vic20_sage')
                .where(AgentLearningRecord.resource_type == resource_type)
                .order_by(desc(AgentLearningRecord.created_at))
                .limit(10)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            similar = []
            for record in records:
                similar.append({
                    'resource_value': record.parameters.get('current_value') if record.parameters else None,
                    'routed_to': record.action,
                    'success': record.success,
                    'confidence': record.confidence,
                    'timestamp': record.created_at
                })
            
            logger.debug(f"🖥️📚 Found {len(similar)} similar routing decisions")
            return similar
            
        except Exception as e:
            logger.error(f"🖥️💥 Error retrieving similar routings: {e}")
            return []
    
    async def _get_recent_coordination_outcomes(self) -> List[Dict[str, Any]]:
        """
        Retrieve recent coordination outcomes across all specialists.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'vic20_sage')
                .order_by(desc(AgentLearningRecord.created_at))
                .limit(20)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            outcomes = []
            for record in records:
                outcomes.append({
                    'resource_type': record.resource_type,
                    'specialist': record.action,
                    'success': record.success,
                    'timestamp': record.created_at
                })
            
            logger.debug(f"🖥️📚 Found {len(outcomes)} recent coordination outcomes")
            return outcomes
            
        except Exception as e:
            logger.error(f"🖥️💥 Error retrieving recent outcomes: {e}")
            return []
    
    def _assess_system_load(self, triage_alert: Dict[str, Any]) -> float:
        """
        Assess current system load based on alert severity and metrics.
        """
        # Simplified system load assessment
        # In production, this would aggregate multiple resource metrics
        severity = triage_alert.get('severity', 'low')
        current_value = triage_alert.get('current_value', 0.0)
        
        if severity == 'critical':
            return min(1.0, current_value / 100.0 * 1.2)
        elif severity == 'high':
            return min(1.0, current_value / 100.0)
        else:
            return min(1.0, current_value / 100.0 * 0.8)
    
    def _calculate_routing_confidence(
        self,
        similar_routings: List[Dict[str, Any]],
        specialists: List[SpecialistProfile]
    ) -> float:
        """
        Calculate confidence in routing decision based on historical success.
        """
        if not similar_routings:
            return 0.5  # Neutral confidence with no history
        
        # Calculate success rate from similar routings
        successful = sum(1 for r in similar_routings if r.get('success', False))
        historical_confidence = successful / len(similar_routings)
        
        # Boost confidence if we have high-performing specialists
        if specialists:
            avg_specialist_success = sum(s.recent_success_rate for s in specialists) / len(specialists)
            combined_confidence = (historical_confidence * 0.6) + (avg_specialist_success * 0.4)
        else:
            combined_confidence = historical_confidence
        
        return combined_confidence
    
    def _calculate_availability_score(
        self,
        specialists: List[SpecialistProfile]
    ) -> float:
        """
        Calculate specialist availability score.
        """
        if not specialists:
            return 0.0
        
        # Score based on load and recent activity
        scores = []
        for specialist in specialists:
            # Lower load = higher score
            load_score = max(0.0, 1.0 - (specialist.current_load / 10.0))
            
            # Recent activity is good (shows they're responsive)
            if specialist.last_coordination:
                time_since = (utc_now() - specialist.last_coordination).total_seconds()
                recency_score = 1.0 if time_since < 300 else 0.5  # 5 minutes
            else:
                recency_score = 0.5
            
            specialist_score = (load_score * 0.7) + (recency_score * 0.3)
            scores.append(specialist_score)
        
        return sum(scores) / len(scores)
