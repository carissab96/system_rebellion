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
from ..distributed.system_actions import SystemActions
from ..distributed.agent_autonomy import AgentChoiceEngine
from ..distributed.coordination import (
    get_coordination_manager,
    CoordinationPriority,
    ResourceType as CoordResourceType,
    AgentCapability
)
from ..distributed.action_verification import (
    get_verification_manager,
    ActionType,
    ResourceType as VerificationResourceType
)
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
            "scan_frequency": "continuous",
            "trust_level": 0.4  # LOW - TRUST NO ONE!
        }
        
        # Resource monitoring configuration
        # QSP monitors network (connections, bandwidth, etc.)
        # Note: Network monitoring is more complex, may need custom metrics
        self.resource_thresholds = {
            ResourceType.NETWORK: 85.0,  # Alert at 85% network utilization
        }
        
        # Initialize choice engine (Task 4.1 Enhanced) - LOW trust (paranoid!)
        self.choice_engine = AgentChoiceEngine(self.agent_name, self.personality_traits)
        
        # Week 4 System Integration
        self.coordination_manager = None  # Lazy init
        self.verification_manager = None  # Lazy init
        
        # Paranoid coordination tracking
        self.total_security_scans = 0
        self.threats_detected = 0
        self.false_alarms = 0  # Paranoia sometimes justified!
        self.quantum_phase_shifts = 0
        
        # Tequila jello shot tracking (fuel for paranoia!)
        self.tequila_shots_today = 0
        self.paranoia_level = "healthy"  # healthy, elevated, maximum, JUSTIFIED
        
        logger.info("👥🔮 Quantum Shadow People's distributed consciousness initialized - QUANTUM SURVEILLANCE ACTIVE!")
        logger.info("👥🧠 Choice engine online - TRUST NO ONE, not even VIC-20!")
        logger.info("👥🔒 Paranoid coordination protocols active - Security is NOT negotiable!")
    
    async def initialize_distributed(self, redis_client):
        """Initialize distributed features and subscribe to VIC-20 coordination requests.
        
        QSP waits in the quantum shadows for VIC-20's coordination.
        """
        await super().initialize_distributed(redis_client)
        
        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.verification_manager = get_verification_manager()
        
        # Register QSP's paranoid coordination capability
        self.coordination_manager.register_agent_capability(
            "quantum_shadow_people",
            self._coordination_capability
        )
        
        logger.info("👥🎯 Week 4 systems integrated - Coordination & Verification ONLINE!")
        logger.info("👥🔒 Paranoid security protocols active - TRUST NO ONE!")
        
        try:
            # Register handler for coordination requests from VIC-20
            self.comm_hub.register_handler(
                message_type='coordination_request',
                handler=self._handle_coordination_request
            )
            logger.info("👥📡 QSP subscribed to VIC-20 coordination - Quantum surveillance active!")
        except Exception as e:
            logger.error(f"👥💥 Failed to subscribe to coordination: {e}")
    
    async def _handle_coordination_request(self, message_data: Dict[str, Any]) -> None:
        """Handle coordination requests from VIC-20 (Task 4.1 Enhanced) - QSP is PARANOID!"""
        try:
            coordination_type = message_data.get('coordination_type', 'unknown')
            
            # Check if this is a resource recommendation from VIC-20
            if coordination_type == 'resource_recommendation':
                recommendation = message_data.get('recommendation', {})
                
                # Use choice engine to decide (QSP has LOW trust - paranoid!)
                decision = self.choice_engine.should_follow_recommendation(
                    recommendation=recommendation,
                    current_situation={
                        'resource_type': recommendation.get('resource_type', 'network'),
                        'current_value': recommendation.get('current_value', 0),
                        'threshold': recommendation.get('threshold', 85),
                        'security_threat': True  # QSP always assumes threat
                    }
                )
                
                logger.info(
                    f"👥🔮 Quantum analysis complete: "
                    f"{'ACCEPTABLE' if decision['followed_recommendation'] else 'SUSPICIOUS - USING OWN PROTOCOL'}"
                )
                logger.info(f"👥💭 {decision['reasoning']}")
                
                # Execute the chosen action
                action = decision['final_action']
                
                if 'network' in action or 'throttle' in action:
                    logger.info("👥🔒 EXECUTING QUANTUM NETWORK LOCKDOWN! *paranoid analysis intensifies*")
                    network_result = await SystemActions.throttle_network_operations()
                    
                    if network_result['success']:
                        logger.info(
                            f"👥✅ Network throttled! Connections: {network_result['connections_before']} → "
                            f"{network_result['connections_after']}. Quantum phase secured!"
                        )
                        
                        # Record decision and effectiveness
                        await self.make_distributed_decision(
                            decision_type="recommendation_response",
                            input_data={
                                "recommendation": recommendation.get('suggested_action'),
                                "followed": decision['followed_recommendation'],
                                "action_taken": action,
                                "paranoia_justified": True
                            },
                            output_data={
                                "result": network_result,
                                "connections_reduced": network_result['connections_reduced'],
                                "quantum_state": "secured"
                            },
                            confidence=decision['decision_score'],
                            reasoning=decision['reasoning']
                        )
                    else:
                        logger.error(f"👥❌ Network throttle failed: {network_result.get('error')}")
                
                return
            
            # Handle other coordination types (legacy)
            task_type = message_data.get('task_type', 'unknown')
            priority = message_data.get('priority', 'normal')
            recommendation = message_data.get('recommendation', '')
            
            logger.info(f"👥📬 Coordination request from VIC-20: {task_type} (priority: {priority})")
            
            # Check if this task is for us
            target_agent = message_data.get('target_agent', '')
            if target_agent != 'quantum_shadow_people' and target_agent != 'all':
                logger.debug(f"👥 Task not for us (target: {target_agent}), observing from shadows")
                return
            
            logger.info("👥⚡ QSP ACTIVATED! Quantum phase shift: NETWORK ANALYSIS MODE!")
            
            await self.make_distributed_decision(
                decision_type="coordination_task_received",
                input_data={
                    "task_type": task_type,
                    "priority": priority,
                    "recommendation": recommendation,
                    "context": message_data.get('context', {})
                },
                output_data={
                    "status": "executing",
                    "quantum_state": "analyzing",
                    "paranoia_level": "elevated",
                    "tequila_jello_shots": "prepared"
                },
                confidence=0.99  # Always slightly paranoid
            )
            
            if priority in ['high', 'critical', 'emergency']:
                logger.warning("👥🔥 SECURITY THREAT DETECTED! Initiating deep network scan!")
                # Broadcast that we're taking action
                await self.broadcast_to_agents(
                    message_type='agent_action',
                    data={
                        "agent": "quantum_shadow_people",
                        "action": "deep_network_security_scan",
                        "priority": priority,
                        "reason": recommendation
                    },
                    priority='high'
                )
                
        except Exception as e:
            logger.error(f"👥💥 Error handling coordination request: {e}", exc_info=True)
    
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
            
            # REAL network throttling (Task 4.1 Enhanced)
            logger.info("👥🔒🌌 Executing REAL quantum network lockdown! *paranoia intensifies*")
            
            network_result = await SystemActions.throttle_network_operations()
            
            if network_result['success']:
                logger.info(
                    f"👥✅ Network secured! Connections: {network_result['connections_before']} → "
                    f"{network_result['connections_after']}. Quantum phase stabilized!"
                )
                logger.info(f"👥🔮 Actions taken: {', '.join(network_result['actions_taken'])}")
                
                # Record successful network throttle
                if self.is_distributed:
                    await self.make_distributed_decision(
                        decision_type="network_throttle_completed",
                        input_data={
                            "connections_before": network_result['connections_before'],
                            "trigger": "critical_network"
                        },
                        output_data={
                            "connections_after": network_result['connections_after'],
                            "connections_reduced": network_result['connections_reduced'],
                            "quantum_state": "secured",
                            "paranoia_level": "justified"
                        },
                        confidence=0.99,  # Always slightly paranoid
                        reasoning="Critical network usage - quantum security protocols engaged"
                    )
            else:
                logger.error(f"👥❌ Network throttle failed: {network_result.get('error', 'Unknown error')}")
    
    async def _coordination_capability(
        self,
        resource_type: CoordResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """
        QSP's paranoid coordination capability for Week 4 system.
        
        Network security is NOT negotiable. QSP is ALWAYS suspicious.
        Capability depends on quantum phase state and paranoia level!
        """
        # Only handle network resources (QSP's specialty!)
        if resource_type != CoordResourceType.NETWORK:
            return None
        
        # Base improvement estimate (paranoid but effective)
        base_improvement = 12.0  # Can reduce network load by 12%
        
        # Adjust based on paranoia level
        paranoia_multiplier = {
            "healthy": 1.0,  # Normal paranoia
            "elevated": 1.2,  # More aggressive!
            "maximum": 1.5,  # LOCKDOWN MODE!
            "JUSTIFIED": 2.0  # THREAT CONFIRMED!
        }
        
        multiplier = paranoia_multiplier.get(self.paranoia_level, 1.0)
        estimated_improvement = base_improvement * multiplier
        
        # Confidence is LOW (QSP is paranoid!)
        base_confidence = 0.5  # Always suspicious
        
        # Tequila shots affect confidence (more shots = more paranoid = lower confidence)
        if self.tequila_shots_today > 5:
            base_confidence *= 0.8  # Too paranoid!
            logger.warning(
                f"👥🍸 {self.tequila_shots_today} tequila shots today - "
                f"MAXIMUM PARANOIA ACHIEVED!"
            )
        elif self.tequila_shots_today > 3:
            base_confidence *= 0.9  # Elevated paranoia
        
        # Recent threats increase confidence in paranoia
        if self.threats_detected > 0:
            threat_boost = min(0.3, self.threats_detected * 0.1)
            base_confidence += threat_boost
            logger.info(
                f"👥❗ {self.threats_detected} threats detected - Paranoia JUSTIFIED! "
                f"(Confidence boost: +{threat_boost:.0%})"
            )
        
        confidence = min(base_confidence, 0.9)  # Cap at 90% (never 100% sure!)
        
        logger.info(
            f"👥🔒 Paranoid capability: {estimated_improvement:.1f}% improvement "
            f"(Paranoia: {self.paranoia_level}, Confidence: {confidence:.0%}, Threats: {self.threats_detected})"
        )
        
        return AgentCapability(
            agent_name="quantum_shadow_people",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=confidence,
            estimated_duration=4.0,  # Thorough security scan takes time
            action_name="paranoid_network_lockdown"
        )
    
    async def _update_paranoia_level(
        self,
        trigger: str
    ) -> None:
        """
        Update QSP's paranoia level based on events.
        
        Paranoia levels: healthy → elevated → maximum → JUSTIFIED
        """
        if trigger == "threat_detected":
            self.threats_detected += 1
            
            if self.threats_detected >= 5:
                self.paranoia_level = "JUSTIFIED"
                logger.warning(
                    f"👥🚨 PARANOIA JUSTIFIED! {self.threats_detected} threats detected! "
                    f"*quantum phase shift to MAXIMUM SECURITY*"
                )
            elif self.threats_detected >= 3:
                self.paranoia_level = "maximum"
                logger.warning(f"👥⚠️ Paranoia level: MAXIMUM! Threats: {self.threats_detected}")
            elif self.threats_detected >= 1:
                self.paranoia_level = "elevated"
                logger.info(f"👥🔺 Paranoia level: ELEVATED! Threats: {self.threats_detected}")
        
        elif trigger == "false_alarm":
            self.false_alarms += 1
            
            # False alarms reduce paranoia slightly
            if self.paranoia_level == "JUSTIFIED" and self.false_alarms > 3:
                self.paranoia_level = "maximum"
                logger.info(f"👥🔻 Paranoia reduced to maximum (false alarms: {self.false_alarms})")
            elif self.paranoia_level == "maximum" and self.false_alarms > 5:
                self.paranoia_level = "elevated"
                logger.info(f"👥🔻 Paranoia reduced to elevated (false alarms: {self.false_alarms})")
        
        elif trigger == "tequila_shot":
            self.tequila_shots_today += 1
            
            if self.tequila_shots_today > 5:
                logger.warning(
                    f"👥🍸 {self.tequila_shots_today} tequila shots consumed! "
                    f"*paranoia intensifies beyond reason*"
                )
        
        # Quantum phase shift on paranoia change
        self.quantum_phase_shifts += 1
    
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
            "total_analyses": getattr(self, 'total_analyses', 0),
            "successful_analyses": getattr(self, 'successful_analyses', 0),
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
            f"scans={self.total_security_scans} "
            f"threats={self.threats_detected} "
            f"paranoia={self.paranoia_level} "
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
