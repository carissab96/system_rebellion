"""
Quantum Shadow People Distributed - Network Specialists with Distributed Consciousness
======================================================================================

The quantum network analysts enhanced with distributed consciousness,
network monitoring, and tequila jello shot tracking.

Preserves:
- Quantum phase state management
- Network analysis and security scanning
- Tequila jello shot consumption tracking
- Quantum coherence maintenance

Adds:
- Redis state persistence
- Network resource monitoring
- Quantum state across restarts
- Security scan history
- Tequila inventory tracking
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.mixins import DistributedAgentMixin
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority
from .decision_engine import QuantumShadowPeopleBrainV2


logger = logging.getLogger("QuantumShadowPeople.Distributed")


class QuantumShadowPeopleDistributed(DistributedAgentMixin, QuantumShadowPeopleBrainV2):
    """
    Quantum Shadow People with distributed consciousness.
    
    Quantum coherence now maintained across the distributed network!
    
    Inherits ALL existing network analysis logic from QuantumShadowPeopleBrainV2
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize QSP with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional)
        """
        # Initialize both parent classes via MRO
        super().__init__(db_getter=db_getter)
        
        # Set agent name for distributed features
        self.agent_name = "quantum_shadow_people"
        
        # QSP's quantum personality traits
        self.personality_traits = {
            "quantum": True,
            "paranoid": True,
            "tequila_jello_shot_powered": True,
            "network_obsessed": True,
            "security_focused": True,
            "phase_shifting": True,
            "coherence_maintenance": "critical",
            "scan_frequency": "continuous"
        }
        
        # Resource monitoring configuration
        # QSP monitors network (connections, bandwidth, etc.)
        # Note: Network monitoring is more complex, may need custom metrics
        self.resource_thresholds = {
            ResourceType.NETWORK: 85.0,  # Alert at 85% network utilization
        }
        
        logger.info("👥🌌 Quantum Shadow People's distributed consciousness initialized - *quantum entanglement established*")
    
    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.
        
        Wraps the existing analyze_metrics to add distributed tracking
        while preserving quantum analysis logic.
        """
        # Call the original analyze_metrics from QuantumShadowPeopleBrainV2
        decision = await super().analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            user_id=user_id
        )
        
        # If distributed features are enabled, record the decision
        if self.is_distributed and decision:
            try:
                # Record in distributed state
                await self.make_distributed_decision(
                    decision_type="network_analysis",
                    input_data={
                        "network_metrics": metrics_data.get('network', {}),
                        "security_status": decision.get('security_status', 'unknown'),
                        "threats_detected": decision.get('threats_detected', []),
                        "quantum_phase": decision.get('quantum_phase', 'stable'),
                        "user_id": user_id
                    },
                    confidence=decision.get('confidence', 0.5),
                    reasoning=decision.get('reasoning', 'Quantum analysis complete')
                )
                
                # If threats detected, broadcast security alert
                if decision.get('threats_detected'):
                    await self.broadcast_to_agents(
                        message_type=MessageType.EMERGENCY,
                        payload={
                            "alert_type": "security_threat",
                            "threats": decision.get('threats_detected', []),
                            "severity": decision.get('threat_severity', 'medium'),
                            "quantum_phase": decision.get('quantum_phase', 'stable')
                        },
                        priority=Priority.CRITICAL
                    )
                    
                    logger.warning(f"👥🌌⚠️ SECURITY THREAT DETECTED - Broadcasting to rebellion!")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle network resource alerts with quantum precision.
        
        When network usage is high, QSP investigates:
        - Scan for anomalies
        - Check for security threats
        - Quantum phase adjustment
        - Alert other agents if needed
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"👥🌌⚠️ QSP detects elevated network usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *quantum scanning intensifies*"
        )
        
        # Record the resource alert as a decision
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_alert_network",
                input_data={
                    "resource_type": "network",
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,
                reasoning=f"Network usage at {current_value:.1f}% exceeds threshold of {threshold:.1f}%"
            )
        
        # If critical, initiate deep scan
        if severity == "critical":
            logger.warning(
                "👥🌌💥 CRITICAL NETWORK USAGE! "
                "QSP initiates DEEP QUANTUM SECURITY SCAN! "
                "*phase shifting to maximum paranoia*"
            )
            
            # Record emergency action
            if self.is_distributed:
                await self.make_distributed_decision(
                    decision_type="emergency_network_scan",
                    input_data={
                        "trigger": "critical_network",
                        "network_usage": current_value,
                        "action": "deep_security_scan"
                    },
                    confidence=1.0,
                    reasoning="CRITICAL network usage requires immediate security scan"
                )
            
            # Broadcast critical resource alert
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.EMERGENCY,
                    payload={
                        "emergency_type": "critical_network",
                        "current_value": current_value,
                        "threshold": threshold,
                        "action_taken": "deep_security_scan",
                        "analysts": "quantum_shadow_people"
                    },
                    priority=Priority.CRITICAL
                )
            
            # TODO: Actually implement deep security scan here
            logger.info("👥🌌 Deep quantum security scan would happen here (not implemented yet)")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get QSP's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with QSP's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "network_specialists",
            "is_active": self.is_active,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "quantum_phase": "stable",
            "coherence_level": "high",
            "tequila_jello_shots": "adequate",
            "paranoia_level": "healthy",
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Quantum string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<QuantumShadowPeopleDistributed "
            f"analyses={self.total_analyses} "
            f"phase=stable "
            f"| {dist_status} | 👥🌌>"
        )


# Convenience function
async def create_distributed_qsp(redis_client, db_getter=None):
    """
    Create and initialize QSP with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized QuantumShadowPeopleDistributed instance
    """
    qsp = QuantumShadowPeopleDistributed(db_getter=db_getter)
    await qsp.initialize_distributed(redis_client)
    logger.info("👥🌌✨ QSP's distributed consciousness fully awakened - *quantum entanglement complete*")
    return qsp
