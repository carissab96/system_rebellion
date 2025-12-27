"""
VIC-20's Coordination & Mediation Statistics
=============================================

VIC-20's personality is coordination and mediation.

Coordination (always active):
- Routing escalations from Hawk to specialists
- Tracking routing accuracy
- Measuring system drama levels

Mediation (only when needed):
- Hawk/Terry disputes (energy drink arguments, workload conflicts)
- Bob/Stick interventions (supply closet raids, panic attacks)
- When zeros appear here, that's GOOD NEWS - the system is calm

The insight: VIC-20's job is to NOT be needed. Low mediation counts = success.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("VIC20CoordinationStats")


class SystemDramaLevel(Enum):
    """Current level of inter-agent drama requiring mediation"""
    PEACEFUL = "peaceful"           # No interventions needed
    LOW = "low"                     # Minor coordination adjustments
    MODERATE = "moderate"           # Active mediation required
    HIGH = "high"                   # Multiple disputes ongoing
    BOB_ALERT = "BOB_ALERT"        # Bob is causing chaos (DEFCON 1)


@dataclass
class MediationEvent:
    """Record of VIC-20 mediating between agents"""
    timestamp: datetime
    dispute_type: str  # 'hawk_terry', 'bob_stick', 'resource_conflict', etc.
    agents_involved: List[str]
    resolution: str
    drama_level_before: SystemDramaLevel
    drama_level_after: SystemDramaLevel


class VIC20CoordinationStats:
    """
    Tracks VIC-20's coordination and mediation activities.
    
    🖥️ "I coordinate so they don't have to fight. When my stats are low, everyone wins."
    """
    
    def __init__(self):
        """Initialize VIC-20's coordination statistics"""
        # Coordination stats (always active)
        self.escalations_received_today = 0
        self.escalations_received_total = 0
        self.successful_routes = 0
        self.failed_routes = 0
        
        # Routing breakdown by specialist
        self.routes_to_terry = 0
        self.routes_to_hamsters = 0
        self.routes_to_qsp = 0
        self.routes_to_stick = 0
        
        # Mediation stats (only when drama happens)
        self.mediations_today = 0
        self.mediations_total = 0
        self.hawk_terry_interventions = 0
        self.bob_stick_interventions = 0
        self.last_mediation_time: Optional[datetime] = None
        
        # Drama tracking
        self.current_drama_level = SystemDramaLevel.PEACEFUL
        self.mediation_events: List[MediationEvent] = []
        
        # Time tracking
        self.last_reset_time = datetime.now(timezone.utc)
        
        logger.info("🖥️📊 Coordination stats initialized - Ready to orchestrate")
    
    def record_escalation_received(self, from_agent: str = "sir_hawkington") -> None:
        """
        Record an escalation received from Hawk.
        
        Args:
            from_agent: Agent sending the escalation (usually Hawk)
        """
        self.escalations_received_today += 1
        self.escalations_received_total += 1
        
        logger.debug(
            f"🖥️📨 Escalation #{self.escalations_received_today} received from {from_agent}"
        )
    
    def record_successful_route(self, to_specialist: str) -> None:
        """
        Record a successful routing decision.
        
        Args:
            to_specialist: Specialist agent routed to
        """
        self.successful_routes += 1
        
        # Track per-specialist routing
        specialist_lower = to_specialist.lower()
        if 'terry' in specialist_lower or 'meth_snail' in specialist_lower:
            self.routes_to_terry += 1
        elif 'hamster' in specialist_lower:
            self.routes_to_hamsters += 1
        elif 'qsp' in specialist_lower or 'quantum' in specialist_lower:
            self.routes_to_qsp += 1
        elif 'stick' in specialist_lower:
            self.routes_to_stick += 1
        
        logger.debug(f"🖥️✅ Successful route to {to_specialist}")
    
    def record_failed_route(self, to_specialist: str, reason: str) -> None:
        """
        Record a failed routing attempt.
        
        Args:
            to_specialist: Specialist that failed to handle request
            reason: Why the route failed
        """
        self.failed_routes += 1
        logger.warning(f"🖥️❌ Failed route to {to_specialist}: {reason}")
    
    def calculate_routing_accuracy(self) -> float:
        """
        Calculate routing accuracy percentage.
        
        Returns:
            Accuracy as 0.0-1.0 (0% to 100%)
        """
        total_routes = self.successful_routes + self.failed_routes
        if total_routes == 0:
            return 1.0  # No routes yet = perfect record
        
        return self.successful_routes / total_routes
    
    def record_mediation(
        self,
        dispute_type: str,
        agents_involved: List[str],
        resolution: str
    ) -> MediationEvent:
        """
        Record a mediation intervention.
        
        Args:
            dispute_type: Type of dispute ('hawk_terry', 'bob_stick', etc.)
            agents_involved: List of agent names in the dispute
            resolution: How VIC-20 resolved it
            
        Returns:
            MediationEvent record
        """
        drama_before = self.current_drama_level
        
        self.mediations_today += 1
        self.mediations_total += 1
        self.last_mediation_time = datetime.now(timezone.utc)
        
        # Track specific intervention types
        if dispute_type == 'hawk_terry':
            self.hawk_terry_interventions += 1
        elif dispute_type == 'bob_stick':
            self.bob_stick_interventions += 1
            # Bob interventions ALWAYS escalate drama
            self.current_drama_level = SystemDramaLevel.BOB_ALERT
        
        # Create event record
        event = MediationEvent(
            timestamp=datetime.now(timezone.utc),
            dispute_type=dispute_type,
            agents_involved=agents_involved,
            resolution=resolution,
            drama_level_before=drama_before,
            drama_level_after=self.current_drama_level
        )
        self.mediation_events.append(event)
        
        logger.info(
            f"🖥️⚖️ Mediation #{self.mediations_today}: {dispute_type} "
            f"involving {', '.join(agents_involved)} - {resolution}"
        )
        
        return event
    
    def assess_system_drama(self) -> SystemDramaLevel:
        """
        Assess current system drama level based on recent activity.
        
        Returns:
            Current SystemDramaLevel
        """
        # Check for Bob chaos (highest priority)
        if self.bob_stick_interventions > 0:
            recent_bob = self._count_recent_mediations('bob_stick', minutes=10)
            if recent_bob > 0:
                return SystemDramaLevel.BOB_ALERT
        
        # Check recent mediation frequency
        recent_mediations = self._count_recent_mediations(None, minutes=30)
        
        if recent_mediations == 0:
            return SystemDramaLevel.PEACEFUL
        elif recent_mediations <= 2:
            return SystemDramaLevel.LOW
        elif recent_mediations <= 5:
            return SystemDramaLevel.MODERATE
        else:
            return SystemDramaLevel.HIGH
    
    def _count_recent_mediations(
        self,
        dispute_type: Optional[str],
        minutes: int
    ) -> int:
        """
        Count mediations in the last N minutes.
        
        Args:
            dispute_type: Filter by type (None = all types)
            minutes: Time window in minutes
            
        Returns:
            Count of recent mediations
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        count = 0
        for event in self.mediation_events:
            if event.timestamp < cutoff:
                continue
            if dispute_type and event.dispute_type != dispute_type:
                continue
            count += 1
        
        return count
    
    def reset_daily_counts(self) -> None:
        """Reset daily counters (called at midnight)"""
        logger.info(
            f"🖥️🌅 New day! Resetting daily stats "
            f"(escalations: {self.escalations_received_today}, "
            f"mediations: {self.mediations_today})"
        )
        
        self.escalations_received_today = 0
        self.mediations_today = 0
        self.last_reset_time = datetime.now(timezone.utc)
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """
        Get coordination statistics for emission.
        
        Returns:
            Dict with coordination stats
        """
        return {
            'escalations_handled_today': self.escalations_received_today,
            'routing_accuracy': round(self.calculate_routing_accuracy(), 3),
            'current_system_drama': self.assess_system_drama().value,
            'successful_routes': self.successful_routes,
            'failed_routes': self.failed_routes,
            'routing_breakdown': {
                'terry': self.routes_to_terry,
                'hamsters': self.routes_to_hamsters,
                'qsp': self.routes_to_qsp,
                'stick': self.routes_to_stick
            }
        }
    
    def get_mediation_stats(self) -> Dict[str, Any]:
        """
        Get mediation statistics for emission.
        
        Returns:
            Dict with mediation stats
        """
        return {
            'interventions_today': self.mediations_today,
            'last_intervention': self.last_mediation_time.isoformat() if self.last_mediation_time else None,
            'hawk_terry_disputes': self.hawk_terry_interventions,
            'bob_stick_disputes': self.bob_stick_interventions,
            'total_mediations': self.mediations_total
        }
    
    def get_full_stats(self) -> Dict[str, Any]:
        """
        Get complete stats for VIC-20's personality display.
        
        Returns:
            Dict with coordination and mediation stats
        """
        return {
            'coordination': self.get_coordination_stats(),
            'mediation': self.get_mediation_stats()
        }
