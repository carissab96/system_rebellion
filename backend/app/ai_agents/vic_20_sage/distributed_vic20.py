"""
VIC-20 Sage Distributed - Orchestrator with Distributed Consciousness
======================================================================

The coordination sage enhanced with distributed consciousness,
pattern matching across the network, and orchestration persistence.

Preserves:
- Multi-agent coordination logic
- Historical pattern matching
- Orchestration decisions
- Emergency routing

Adds:
- Redis state persistence
- Coordination patterns across restarts
- Distributed orchestration
- Pattern library sharing
"""

import logging
import asyncio
from typing import Dict, Any, Optional

from ..distributed.base_decision_engine import AgentDecisionEngine
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
from ..distributed.system_actions import RecommendationEngine
from ..distributed.coordination import (
    get_coordination_manager,
    CoordinationPriority,
    ResourceType as CoordResourceType,
    AgentCapability
)
from ..distributed.alert_escalation import (
    get_escalation_manager,
    AlertLevel,
    ResourceType as EscalationResourceType
)
from ..distributed.resource_prediction import (
    get_resource_predictor,
    ResourceType as PredictionResourceType
)
from .decision_engine import VIC20SageBrainV2


logger = logging.getLogger("VIC20Sage.Distributed")


class VIC20SageDistributed(AgentDecisionEngine, VIC20SageBrainV2):
    """
    VIC-20 Sage with distributed consciousness.
    
    The orchestrator's wisdom now spans the entire distributed network!
    
    Inherits ALL existing coordination logic from VIC20SageBrainV2
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize VIC-20 Sage with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional, for lazy init)
        """
        # Initialize both parent classes via MRO
        # Pass db_getter to VIC20SageBrainV2
        super().__init__(db_getter=db_getter)
        
        # Set agent name for distributed features
        self.agent_name = "vic_20_sage"
        
        # VIC-20's sage personality traits
        self.personality_traits = {
            "coordinator": True,
            "pattern_matcher": True,
            "orchestrator": True,
            "wise": True,
            "patient": True,
            "multi_agent_aware": True,
            "historical_memory": "extensive",
            "coordination_style": "collaborative"
        }
        
        # 🎯 PHASE 3: VIC-20 does NOT monitor resources
        # He receives triage alerts from Sir Hawkington
        self.resource_thresholds = {}
        
        # Initialize recommendation engine (Task 4.1 Enhanced)
        self.recommendation_engine = RecommendationEngine()
        
        # Week 4 System Integration
        self.coordination_manager = None  # Lazy init
        self.escalation_manager = None  # Lazy init
        self.resource_predictor = None  # Lazy init
        
        # Bob mediation tracking (VIC-20's special duty!)
        self.bob_mediation_count = 0
        self.stick_anxiety_prevented = 0
        self.bob_messages_filtered = []
        
        logger.info("🖥️✨ VIC-20 Sage's distributed consciousness initialized - ORCHESTRATION PROTOCOLS ACTIVE!")
        logger.info("🖥️💡 Recommendation engine online - READY TO GUIDE AGENTS!")
        logger.info("🖥️🛡️ Bob mediation protocols active - STICK PROTECTION ENABLED!")
    
    async def initialize_distributed(self, redis_client):
        """
        Initialize distributed features and subscribe to triage alerts from Hawk.
        
        PHASE 3: VIC-20 is the coordinator - receives from Hawk, routes to specialists.
        """
        # Call parent initialization - NO resource monitoring for VIC-20
        await super().initialize_distributed(
            redis_client,
            enable_resource_monitoring=False  # VIC-20 doesn't monitor
        )
        
        # Initialize database integration for PostgreSQL writes
        if self.db_getter:
            try:
                # Initialize database integration with db_getter
                from .database_integration import VIC20DatabaseIntegration
                self.db_integration = VIC20DatabaseIntegration(self.db_getter)
                await self.db_integration.initialize()
                self._db_initialized = True
                
                logger.info("🖥️💾 Database integration initialized")
            except Exception as e:
                logger.error(f"🖥️💥 Failed to initialize database: {e}", exc_info=True)
        
        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.escalation_manager = get_escalation_manager()
        self.resource_predictor = get_resource_predictor()
        
        # Register VIC-20's coordination capability
        self.coordination_manager.register_agent_capability(
            "vic_20_sage",
            self._coordination_capability
        )
        
        logger.info("🖥️🎯 Week 4 systems integrated - Coordination, Escalation, Prediction ONLINE!")
        
        # 🎯 PHASE 3: Subscribe to TRIAGE_ALERT from Sir Hawkington
        try:
            await self.subscribe_to_messages(
                message_type=MessageType.TRIAGE_ALERT,
                callback=self._handle_triage_alert_from_hawk
            )
            logger.info("🖥️📡 VIC-20 subscribed to TRIAGE_ALERT from Sir Hawkington - Coordination ready!")
        except Exception as e:
            logger.error(f"🖥️💥 Failed to subscribe to triage alerts: {e}")
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle coordination requests (VIC-20 rarely receives these, he SENDS them).
        
        PERSONALITY: Wise coordinator, mediates Bob's chaos
        STRUCTURE: Standard AgentMessage parameter (required by base class)
        
        Args:
            message: AgentMessage with coordination request
        """
        # VIC-20 is the coordinator - he rarely receives coordination requests
        # But we implement this for completeness
        message_data = message.payload
        logger.info(f"🖥️📬 VIC-20 received coordination request: {message_data.get('coordination_type', 'unknown')}")
        logger.info("🖥️💭 As the coordinator, I typically SEND these, not receive them!")
    
    async def _handle_triage_alert_from_hawk(self, message: AgentMessage) -> None:
        """
        PHASE 3: Handle TRIAGE_ALERT from Sir Hawkington.
        
        Flow:
        1. Receive triage alert from Hawk
        2. Determine which specialist to route to
        3. Generate recommendation based on patterns
        4. Send COORDINATION_REQUEST to specialist
        5. Write coordination decision to PostgreSQL
        6. CC The Stick
        """
        try:
            payload = message.payload
            resource_type = payload.get('resource_type', 'unknown')
            severity = payload.get('severity', 'unknown')
            confidence = payload.get('confidence', 0.0)
            current_value = payload.get('current_value', 0)
            threshold = payload.get('threshold', 0)
            
            logger.info(
                f"🖥️📬 TRIAGE ALERT from Sir Hawkington: "
                f"{resource_type} at {current_value:.1f}% (threshold: {threshold:.1f}%) "
                f"severity={severity}, confidence={confidence:.2f}"
            )
            
            # Determine which specialist to route to
            specialist = self._route_to_specialist(resource_type)
            
            if not specialist:
                logger.warning(f"🖥️⚠️ No specialist found for resource type: {resource_type}")
                return
            
            # Generate recommendation based on historical patterns
            recommendation = await self._generate_recommendation(
                resource_type=resource_type,
                current_value=current_value,
                threshold=threshold,
                severity=severity
            )
            
            logger.info(
                f"🖥️💡 Routing to {specialist}: {recommendation['action']} "
                f"(confidence: {recommendation['confidence']:.2f})"
            )
            
            # Send COORDINATION_REQUEST to specialist
            await self.broadcast_to_agents(
                message_type=MessageType.COORDINATION_REQUEST,
                payload={
                    'resource_type': resource_type,
                    'current_value': current_value,
                    'threshold': threshold,
                    'severity': severity,
                    'recommendation': recommendation,
                    'from_coordinator': 'vic_20_sage',
                    'triage_confidence': confidence
                },
                priority=Priority.HIGH if severity in ['high', 'critical'] else Priority.NORMAL
            )
            
            # Write coordination decision to PostgreSQL
            await self._write_coordination_decision(
                resource_type=resource_type,
                specialist=specialist,
                recommendation=recommendation,
                severity=severity,
                triage_data=payload
            )
            
            # CC The Stick for logging
            await self._cc_the_stick(
                decision_type='coordination',
                resource_type=resource_type,
                specialist=specialist,
                recommendation=recommendation,
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"🖥️💥 Error handling triage alert: {e}", exc_info=True)
    
    def _route_to_specialist(self, resource_type: str) -> Optional[str]:
        """
        PHASE 3: Determine which specialist handles this resource type.
        
        Routing table:
        - CPU/Memory → Meth Snail (Terry)
        - Disk/Storage → Hamsters
        - Network → Quantum Shadow People
        """
        routing_table = {
            'cpu': 'meth_snail',
            'memory': 'meth_snail',
            'ram': 'meth_snail',
            'disk': 'hamsters',
            'storage': 'hamsters',
            'infrastructure': 'hamsters',
            'network': 'quantum_shadow_people',
            'swap': 'meth_snail'  # Swap is memory-related
        }
        
        specialist = routing_table.get(resource_type.lower())
        
        if not specialist:
            logger.warning(f"🖥️⚠️ Unknown resource type: {resource_type}, defaulting to meth_snail")
            return 'meth_snail'
        
        return specialist
    
    async def _generate_recommendation(
        self,
        resource_type: str,
        current_value: float,
        threshold: float,
        severity: str
    ) -> Dict[str, Any]:
        """
        PHASE 3: Generate recommendation for specialist.
        
        Uses historical patterns (future: from The Stick's learning).
        For now, uses rule-based recommendations.
        """
        overage = ((current_value - threshold) / threshold) * 100
        
        # Resource-specific recommendations
        recommendations = {
            'cpu': {
                'action': 'throttle_processes',
                'details': f'CPU {overage:.1f}% over threshold',
                'confidence': 0.85
            },
            'memory': {
                'action': 'clear_cache',
                'details': f'Memory {overage:.1f}% over threshold',
                'confidence': 0.90
            },
            'disk': {
                'action': 'cleanup_temp_files',
                'details': f'Disk {overage:.1f}% over threshold',
                'confidence': 0.80
            },
            'network': {
                'action': 'analyze_connections',
                'details': f'Network {overage:.1f}% over threshold',
                'confidence': 0.75
            }
        }
        
        rec = recommendations.get(resource_type.lower(), {
            'action': 'investigate',
            'details': f'{resource_type} needs attention',
            'confidence': 0.70
        })
        
        # Adjust confidence based on severity
        if severity == 'critical':
            rec['confidence'] = min(1.0, rec['confidence'] + 0.1)
        
        rec['reasoning'] = f"Pattern analysis suggests {rec['action']}. {rec['details']}"
        
        return rec
    
    async def _write_coordination_decision(
        self,
        resource_type: str,
        specialist: str,
        recommendation: Dict[str, Any],
        severity: str,
        triage_data: Dict[str, Any]
    ) -> None:
        """
        PHASE 3: Write coordination decision to PostgreSQL.
        
        Uses VIC-20's database integration to store decision.
        """
        try:
            if not self.db_getter:
                logger.warning("🖥️⚠️ No db_getter available, skipping database write")
                return
            
            # Write coordination decision to PostgreSQL
            if hasattr(self, 'db_integration') and self.db_integration:
                from .data_types import VIC20Decision, VIC20DecisionType, CoordinationState
                from datetime import datetime
                
                # Create proper VIC20Decision object
                decision_obj = VIC20Decision(
                    decision_type=VIC20DecisionType.AGENT_COORDINATION,
                    coordination_state=CoordinationState.ORCHESTRATING,
                    coordination_target=specialist,
                    agent_actions={specialist: recommendation['action']},
                    confidence_level=recommendation['confidence'],
                    technical_orchestration={
                        'resource_type': resource_type,
                        'severity': severity,
                        'recommendation': recommendation
                    },
                    system_context_snapshot=triage_data,
                    ancient_wisdom_principle=None,
                    similar_past_decisions=[],
                    timestamp=datetime.utcnow()
                )
                
                # Store coordination decision
                await self.db_integration.store_coordination_decision(
                    user_id=None,  # System-level decision (no user)
                    decision=decision_obj
                )
                
                logger.info("🖥️💾 Coordination decision written to PostgreSQL")
            else:
                logger.warning("🖥️⚠️ Database integration not available")
                
        except Exception as e:
            logger.error(f"🖥️💥 Error writing coordination decision: {e}", exc_info=True)
    
    async def _cc_the_stick(
        self,
        decision_type: str,
        resource_type: str,
        specialist: str,
        recommendation: Dict[str, Any],
        severity: str
    ) -> None:
        """
        PHASE 3: CC The Stick on coordination decision.
        
        The Stick logs all decisions for pattern learning.
        """
        try:
            await self.broadcast_to_agents(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': decision_type,
                    'from_agent': 'vic_20_sage',
                    'resource_type': resource_type,
                    'specialist': specialist,
                    'recommendation': recommendation,
                    'severity': severity,
                    'timestamp': asyncio.get_event_loop().time()
                },
                priority=Priority.NORMAL
            )
            logger.debug("🖥️📋 Decision logged to The Stick")
        except Exception as e:
            logger.error(f"🖥️💥 Error CC'ing The Stick: {e}", exc_info=True)
    
    async def _update_stick_coordination(
        self,
        severity: str,
        routing: str,
        target_agents: list
    ) -> None:
        """
        Send coordination update to The Stick for learning.
        
        The Stick logs all coordination activities for future pattern matching.
        """
        try:
            await self.broadcast_to_agents(
                message_type=MessageType.SYSTEM_EVENT,
                payload={
                    'coordination_id': f"coord_{int(asyncio.get_event_loop().time())}",
                    'severity': severity,
                    'routing': routing,
                    'agents_involved': target_agents,
                    'status': 'initiated',
                    'coordinated_by': 'vic_20_sage'
                },
                priority=Priority.NORMAL
            )
            logger.debug("🖥️📝 Coordination update sent to The Stick")
            
        except Exception as e:
            logger.error(f"🖥️💥 Error updating Stick: {e}", exc_info=True)
    
    async def _coordination_capability(
        self,
        resource_type: CoordResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """
        VIC-20's coordination capability for Week 4 system.
        
        As the orchestrator, VIC-20 can coordinate ANY resource type
        by delegating to the appropriate specialist.
        """
        # VIC-20 doesn't directly fix resources, but coordinates others
        # His capability is his wisdom in selecting the right agent
        return AgentCapability(
            agent_name="vic_20_sage",
            resource_type=resource_type,
            estimated_improvement=0.0,  # VIC-20 coordinates, doesn't act directly
            confidence=0.95,  # Very confident in coordination
            estimated_duration=1.0,
            action_name="coordinate_specialists"
        )
    
    async def _mediate_hamster_message(self, message: AgentMessage) -> None:
        """
        Mediate hamster messages, especially Bob's, before they reach The Stick.
        
        VIC-20's special duty: Keep Bob from over-stimulating The Stick!
        """
        try:
            message_data = message.payload
            from_agent = message.from_agent
            message_content = message_data.get('content', '')
            
            # Check if Bob is involved
            is_bob_message = 'bob' in from_agent.lower() or 'bob' in message_content.lower()
            
            if is_bob_message:
                self.bob_mediation_count += 1
                
                # Check anxiety level of message
                anxiety_triggers = ['hold my beer', 'wild idea', 'emergency', 'fire', 'chaos']
                is_anxiety_inducing = any(trigger in message_content.lower() for trigger in anxiety_triggers)
                
                if is_anxiety_inducing:
                    # Filter and translate Bob's message to be less anxiety-inducing
                    mediated_message = self._translate_bob_message(message_content)
                    
                    logger.info(
                        f"🖥️🛡️ VIC-20 mediating Bob's message for The Stick: "
                        f"'{message_content[:50]}...' → '{mediated_message[:50]}...'"
                    )
                    
                    # Send mediated version to The Stick
                    await self.broadcast_to_agents(
                        message_type=MessageType.SYSTEM_EVENT,
                        payload={
                            'source': 'hamsters',
                            'mediated_by': 'vic_20_sage',
                            'content': mediated_message,
                            'original_anxiety_level': 'high',
                            'mediated_anxiety_level': 'moderate'
                        },
                        priority=Priority.NORMAL
                    )
                    
                    self.stick_anxiety_prevented += 1
                    self.bob_messages_filtered.append({
                        'timestamp': asyncio.get_event_loop().time(),
                        'original': message_content,
                        'mediated': mediated_message
                    })
                    
                    logger.info(f"🖥️🛡️ The Stick protected from Bob's chaos! (Total prevented: {self.stick_anxiety_prevented})")
                    return
            
            # If not Bob or not anxiety-inducing, pass through normally
            await self._update_stick_coordination(
                severity='normal',
                routing='hamster_activity',
                target_agents=['hamsters']
            )
            
        except Exception as e:
            logger.error(f"🖥️💥 Error mediating hamster message: {e}", exc_info=True)
    
    def _translate_bob_message(self, original_message: str) -> str:
        """
        Translate Bob's chaotic messages into calmer language for The Stick.
        
        VIC-20's ancient wisdom: "The oak and reed both survive the storm."
        """
        # Replace anxiety-inducing phrases with calmer alternatives
        translations = {
            'hold my beer': 'proceeding with caution',
            'wild idea': 'alternative approach',
            'emergency': 'situation requiring attention',
            'fire': 'thermal event',
            'chaos': 'dynamic conditions',
            'BEER': 'operational fuel',
            'duct tape': 'infrastructure reinforcement',
            'full redneck': 'comprehensive response protocol'
        }
        
        mediated = original_message
        for trigger, replacement in translations.items():
            mediated = mediated.replace(trigger, replacement)
            mediated = mediated.replace(trigger.upper(), replacement.upper())
        
        return mediated
    
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
        while preserving coordination logic.
        """
        # Call the original analyze_metrics from VIC20SageBrainV2
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
                    decision_type="coordination",
                    input_data={
                        "coordination_type": decision.get('coordination_type', 'standard'),
                        "agents_involved": decision.get('agents_involved', []),
                        "pattern_matched": decision.get('pattern_matched', None),
                        "orchestration_plan": decision.get('orchestration_plan', {}),
                        "user_id": user_id
                    },
                    confidence=decision.get('confidence', 0.5),
                    reasoning=decision.get('reasoning', 'Coordination decision made')
                )
                
                # If multi-agent coordination needed, broadcast
                if decision.get('agents_involved') and len(decision.get('agents_involved', [])) > 1:
                    await self.broadcast_to_agents(
                        message_type=MessageType.DECISION_BROADCAST,
                        payload={
                            "decision_type": "multi_agent_coordination",
                            "agents_involved": decision.get('agents_involved', []),
                            "orchestration_plan": decision.get('orchestration_plan', {}),
                            "pattern": decision.get('pattern_matched', None)
                        },
                        priority=Priority.HIGH
                    )
                    
                    logger.info(f"🖥️🧙 Multi-agent coordination broadcast - *sage wisdom shared*")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle resource alerts with sage wisdom.
        
        VIC-20 coordinates the response across all agents.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🖥️🧙⚠️ VIC-20 Sage observes resource pressure: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *contemplating coordination strategy*"
        )
        
        # Record the resource alert as a decision
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_alert_coordination",
                input_data={
                    "resource_type": alert.payload['resource_type'],
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,
                reasoning=f"Resource pressure detected, coordinating response"
            )
        
        # Generate recommendations for affected agents (Task 4.1 Enhanced)
        if self.is_distributed and severity in ["critical", "high"]:
            await self._generate_and_broadcast_recommendations(alert)
        
        # If critical or emergency, coordinate emergency response
        if severity in ["critical", "emergency"]:
            logger.warning(
                "🖥️🧙💥 CRITICAL RESOURCE PRESSURE! "
                "VIC-20 Sage initiates EMERGENCY COORDINATION PROTOCOL!"
            )
            
            # Broadcast coordination request to all agents
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.EMERGENCY,
                    payload={
                        "emergency_type": "resource_critical",
                        "resource": alert.payload['resource_type'],
                        "current_value": current_value,
                        "coordination_needed": True,
                        "coordinator": "vic_20_sage"
                    },
                    priority=Priority.CRITICAL
                )
    
    async def _generate_and_broadcast_recommendations(self, alert):
        """
        Generate recommendations for agents and broadcast them (Task 4.1 Enhanced).
        
        Args:
            alert: ResourceAlert from the monitor
        """
        resource_type = alert.payload['resource_type']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        # Map resource types to responsible agents
        agent_map = {
            'cpu': 'sir_hawkington',
            'memory': 'meth_snail',
            'disk': 'hamsters',
            'network': 'quantum_shadow_people'
        }
        
        target_agent = agent_map.get(resource_type)
        
        if not target_agent:
            logger.warning(f"🖥️💡 No agent mapped for resource type: {resource_type}")
            return
        
        # Get historical effectiveness data (from The Stick's logs if available)
        historical_data = await self._get_historical_effectiveness(resource_type)
        
        # Generate recommendation
        recommendation = self.recommendation_engine.generate_recommendation(
            resource_type=resource_type,
            current_value=current_value,
            threshold=threshold,
            agent_name=target_agent,
            historical_data=historical_data
        )
        
        logger.info(
            f"🖥️💡 Generated recommendation for {target_agent}: "
            f"{recommendation['suggested_action']} (confidence: {recommendation['confidence']:.0%})"
        )
        
        # Broadcast recommendation to target agent
        await self.broadcast_to_agents(
            message_type=MessageType.COORDINATION_REQUEST,
            payload={
                "coordination_type": "resource_recommendation",
                "recommendation": recommendation,
                "from_coordinator": "vic_20_sage"
            },
            priority=Priority.HIGH
        )
        
        # Record recommendation in decision history
        await self.make_distributed_decision(
            decision_type="recommendation_generated",
            input_data={
                "resource_type": resource_type,
                "target_agent": target_agent,
                "current_value": current_value,
                "threshold": threshold
            },
            output_data={
                "recommendation": recommendation['suggested_action'],
                "confidence": recommendation['confidence'],
                "urgency": recommendation['urgency']
            },
            confidence=recommendation['confidence'],
            reasoning=recommendation['reasoning']
        )
    
    async def _get_historical_effectiveness(self, resource_type: str) -> Optional[list]:
        """
        Get historical effectiveness data for this resource type.
        
        In future, this will query The Stick's learning database.
        For now, returns None (engine will use defaults).
        
        Args:
            resource_type: Type of resource
            
        Returns:
            List of historical action results or None
        """
        # TODO: Query The Stick's decision history for past effectiveness
        # For now, return None to use default confidence scores
        return None
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get VIC-20's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with VIC-20's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "orchestrator",
            "is_active": self.is_active,
            "total_analyses": getattr(self, 'total_analyses', 0),
            "successful_analyses": getattr(self, 'successful_analyses', 0),
            "wisdom_level": "sage",
            "coordination_capacity": "unlimited",
            "pattern_library_size": "extensive",
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Sage string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<VIC20SageDistributed "
            f"analyses={getattr(self, 'total_analyses', 0)} "
            f"wisdom=sage "
            f"| {dist_status} | 🖥️🧙>"
        )


# Convenience function
async def create_distributed_vic20(redis_client):
    """
    Create and initialize VIC-20 Sage with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        
    Returns:
        Initialized VIC20SageDistributed instance
    """
    vic20 = VIC20SageDistributed()
    await vic20.initialize_distributed(redis_client)
    logger.info("🖥️🧙✨ VIC-20 Sage's distributed consciousness fully awakened - *ancient wisdom flows*")
    return vic20
