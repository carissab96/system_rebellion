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
        
        # Initialize choice engine (Task 4.1 Enhanced) - LOW trust (paranoid!)
        self.choice_engine = AgentChoiceEngine(self.agent_name, self.personality_traits)
        
        logger.info("👥🔮 Quantum Shadow People's distributed consciousness initialized - QUANTUM SURVEILLANCE ACTIVE!")
        logger.info("👥🧠 Choice engine online - TRUST NO ONE, not even VIC-20!")
    
    async def initialize_distributed(self, redis_client):
        """Initialize distributed features and subscribe to VIC-20 coordination requests.
        
        QSP waits in the quantum shadows for VIC-20's coordination.
        """
        await super().initialize_distributed(redis_client)
        
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
            f"analyses={getattr(self, 'total_analyses', 0)} "
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
