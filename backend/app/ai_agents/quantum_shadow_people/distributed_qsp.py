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

from ..distributed.base_decision_engine import AgentDecisionEngine
from app.optimization.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
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
from .data_types import QSPDecision, QSPDecisionType, QuantumPhaseState


logger = logging.getLogger("QuantumShadowPeople.Distributed")


class QuantumShadowPeopleDistributed(AgentDecisionEngine, QuantumShadowPeopleBrainV2):
    """
    Quantum Shadow People with distributed consciousness.
    
    Quantum coherence now maintained across the distributed network!
    
    Inherits ALL existing network analysis logic from QuantumShadowPeopleBrainV2
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize QSP with distributed consciousness.
        
        Args:
            db_getter: Database session factory for PostgreSQL writes
            user_id: User ID for database writes (required for multi-tenant support)
        """
        # Initialize decision engine (parent class)
        super().__init__(db_getter=db_getter)
        self.user_id = user_id
        
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
        
        QSP waits for VIC-20's coordination, not direct triage decisions.
        Base class handles standard subscriptions (COORDINATION_REQUEST, EMERGENCY).
        """
        # Call parent initialization (subscribes to standard channels)
        await super().initialize_distributed(redis_client)
        
        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.verification_manager = get_verification_manager()
        
        # Register QSP's coordination capability
        self.coordination_manager.register_agent_capability(
            "quantum_shadow_people",
            self._coordination_capability
        )
        
        # CRITICAL: Subscribe to COORDINATION_REQUEST from VIC-20
        await self.subscribe_to_messages(
            message_type=MessageType.COORDINATION_REQUEST,
            callback=self._handle_coordination_request
        )
        
        logger.info("👻🎯 Week 4 systems integrated - Coordination & Verification ONLINE!")
        logger.info("👻🕵️ Paranoia levels optimal - Trust no one!")
        logger.info("👻📡 Subscribed to COORDINATION_REQUEST - Ready to receive from VIC-20!")
        
        # Initialize database integration for PostgreSQL writes
        if self.db_getter:
            try:
                from .database_integration import QSPDatabaseIntegration
                self.db_integration = QSPDatabaseIntegration(db_getter=self.db_getter)
                await self.db_integration.initialize()
                logger.info("👻💾 Database integration initialized - Paranoid records enabled!")
            except Exception as e:
                logger.error(f"👻💥 Failed to initialize database: {e}", exc_info=True)
                self.db_integration = None
        else:
            self.db_integration = None
            logger.warning("👻⚠️ No db_getter provided - PostgreSQL writes disabled")
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        👻 QSP V2: ML-Enhanced Quantum Security Analysis
        
        PERSONALITY: Paranoid network security with quantum state tracking
        ARCHITECTURE: Perception → Reasoning → Action Selection → Learning
        
        Args:
            message: AgentMessage with coordination request from VIC-20
        """
        try:
            # Extract payload
            payload = message.payload
            resource_type = payload.get('resource_type', 'unknown')
            severity = payload.get('severity', 'unknown')
            recommendation = payload.get('recommendation', {})
            current_value = payload.get('current_value', 0)
            threshold = payload.get('threshold', 0)
            full_metrics = payload.get('full_metrics', {})
            
            logger.info(
                f"👻📬 COORDINATION REQUEST from VIC-20: "
                f"{resource_type} at {current_value:.1f}% - VIC-20 suggests: {recommendation.get('action', 'unknown')}"
            )
            
            # Get database session for QSP v2 ML components
            db_gen = self.db_getter()
            async for db in db_gen:
                # STEP 1: PERCEPTION - Quantum security assessment
                from app.ai_agents.quantum_shadow_people.ML.perception import QSPPerception
                
                perception = QSPPerception(db, self.personality_traits)
                context = await perception.perceive({
                    'resource_type': resource_type,
                    'severity': severity,
                    'current_value': current_value,
                    'threshold': threshold,
                    'recommendation': recommendation,
                    'full_metrics': full_metrics
                })
                
                logger.info(
                    f"👻👁️ Quantum perception complete - "
                    f"threat_level: {context.threat_level}, quantum_state: {context.quantum_state.state}"
                )
                
                # STEP 2: REASONING - Quantum threat analysis
                from app.ai_agents.quantum_shadow_people.ML.reasoning import QSPReasoning

                reasoning = QSPReasoning(self.personality_traits, db, self.system_id)
                reasoning_result = await reasoning.reason(context)
                
                logger.info(
                    f"👻🧠 Quantum reasoning complete: {reasoning_result.threat_classification} → "
                    f"{reasoning_result.recommended_response} (confidence: {reasoning_result.confidence:.2f})"
                )
                
                # STEP 3: ACTION SELECTION - Quantum security response
                from app.ai_agents.quantum_shadow_people.ML.action_selection import QSPActionSelection
                
                action_selector = QSPActionSelection(self.personality_traits, db, self.system_id)
                decision = await action_selector.select_action(context, reasoning_result)
                
                logger.info(
                    f"👻⚡ Action selected: {decision.action_type} "
                    f"(quantum_state: {decision.quantum_state})"
                )
                
                # STEP 4: EXECUTION - Execute via planner + primitives
                logger.info(f"👻🔒 EXECUTING QUANTUM ACTION: {decision.action_type}")

                from app.ai_agents.quantum_shadow_people.ML.primitives import QSPPrimitiveExecutor
                from app.ai_agents.quantum_shadow_people.ML.execution_planner import QSPExecutionPlanner
                import asyncio

                primitive_executor = QSPPrimitiveExecutor()
                planner = QSPExecutionPlanner(
                    primitive_executor=primitive_executor,
                    effectiveness_model=action_selector.action_effectiveness,
                    learned_thresholds=action_selector.learned_thresholds,
                )

                # Root cause IS the goal — flows directly from reasoning
                goal = reasoning_result.root_cause

                plan = await planner.compose_plan(
                    goal=goal,
                    severity=decision.severity_score,
                    trend='rising' if decision.severity_score >= 0.5 else 'stable',
                    context={},
                )

                execution_result = await planner.execute_plan(plan, context={})

                # Build pre/post metric dicts from primitive results
                metrics_before = execution_result.primitive_results[0].pre_metrics if execution_result.primitive_results else {}
                metrics_after  = execution_result.primitive_results[-1].post_metrics if execution_result.primitive_results else {}
                network_result = {
                    'success':    execution_result.overall_success,
                    'improvement': execution_result.overall_improvement,
                    'plan_source': plan.source.value,
                    'steps_completed': execution_result.steps_completed,
                    'aborted': execution_result.was_aborted,
                    'abort_reason': execution_result.abort_reason,
                }
                
                # STEP 5: LEARNING - Store quantum decision outcome
                from app.ai_agents.quantum_shadow_people.ML.learning import QSPLearning
                
                learning = QSPLearning(db, self.user_id)
                learning_record = await learning.learn(
                    context=context,
                    reasoning=reasoning_result,
                    action=decision,
                    outcome_success=network_result.get('success', False)
                )
                
                if network_result['success']:
                    logger.info(
                        f"👻✅ Network secured! Plan: {network_result['plan_source']}, "
                        f"steps: {network_result['steps_completed']}, "
                        f"improvement: {network_result['improvement']:.3f}, "
                        f"quantum_state: {decision.quantum_state}"
                    )

                    # BROADCAST FULL DECISION CHAIN TO FRONTEND
                    from app.services.agent_decision_emitter import emit_agent_decision
                    
                    await emit_agent_decision(
                        agent_name="quantum_shadow_people",
                        decision_id=learning_record.learning_record_id,
                        perception={
                            "threat_level": context.threat_level,
                            "quantum_state": context.quantum_state.state if context.quantum_state else 'stable',
                            "existential_dread": context.existential_dread,
                            "total_connections": context.total_connections,
                            "suspicious_connections": context.suspicious_connections,
                            "network_anomalies": context.network_anomalies,
                            "failed_auth_attempts": context.failed_auth_attempts,
                            "recv_rate_bps": context.recv_rate_bps,
                            "tequila_system": {
                                "shots_today": self.tequila_shots_today,
                                "paranoia_level": self.paranoia_level,
                                "threats_detected": self.threats_detected,
                                "false_alarms": self.false_alarms
                            }
                        },
                        reasoning={
                            "threat_classification": reasoning_result.threat_classification,
                            "root_cause": reasoning_result.root_cause,
                            "confidence": reasoning_result.confidence,
                            "severity_score": reasoning_result.severity_score,
                            "risk_level": reasoning_result.risk_level,
                            "situation_description": reasoning_result.situation_description,
                        },
                        action_selection={
                            "chosen_action": decision.action_type,
                            "alternatives_considered": decision.alternatives_considered,
                            "confidence": decision.confidence,
                            "priority": decision.priority,
                            "quantum_state": decision.quantum_state,
                            "severity_score": decision.severity_score,
                            "plan_source": network_result['plan_source'],
                            "steps_completed": network_result['steps_completed'],
                        },
                        execution={
                            "metrics_before": metrics_before,
                            "metrics_after": metrics_after,
                            "success": network_result['success'],
                            "improvement": network_result['improvement'],
                            "aborted": network_result['aborted'],
                            "abort_reason": network_result['abort_reason'],
                        },
                        learning={
                            "situation_fingerprint": learning_record.situation_fingerprint,
                            "stored": learning_record.storage_success,
                            "learning_record_id": learning_record.learning_record_id,
                            "success": learning_record.success
                        }
                    )
                    
                    # Broadcast to WebSocket (legacy - keeping for backwards compatibility)
                    from app.services.agent_insight_emitter import emit_agent_insight
                    await emit_agent_insight(
                        from_agent="quantum_shadow_people",
                        to_agent="vic20_sage",
                        action="security_scan_success",
                        reasoning=f"Quantum security protocol executed: {reasoning_result.threat_classification}",
                        context={
                            "success": True,
                            "connections_reduced": network_result['connections_reduced'],
                            "quantum_state": decision.quantum_state,
                            "threat_level": context.threat_level
                        }
                    )
                    # Update learning record with success and metrics
                    pre_metrics_dict = {
                        'total_connections':      float(context.total_connections),
                        'suspicious_connections': float(context.suspicious_connections),
                        'network_anomalies':      float(context.network_anomalies),
                        'failed_auth_attempts':   float(context.failed_auth_attempts),
                        'recv_rate_bps':          float(context.recv_rate_bps),
                    }
                    post_metrics_dict = dict(metrics_after) if metrics_after and not metrics_after.get('collection_failed') else pre_metrics_dict
                    
                    # Determine if this was a false positive or false negative
                    # False positive: escalated a non-threat
                    # False negative: missed a real threat (would be detected after the fact)
                    false_positive = False  # TODO: Implement false positive detection
                    false_negative = False  # TODO: Implement false negative detection
                    
                    await learning.update_outcome(
                        learning_record,
                        success=True,
                        threat_resolved=True,
                        false_positive=False,
                        false_negative=False,
                        outcome_notes=f"Plan '{plan.source.value}' completed {network_result['steps_completed']} steps",
                        pre_metrics=pre_metrics_dict,
                        post_metrics=post_metrics_dict
                    )

                    # Validate action effectiveness with The Stick
                    from app.core.database import get_async_db
                    try:
                        pattern = learning.action_effectiveness._create_metric_pattern(
                            pre_metrics_dict, decision.severity_score
                        )
                        await learning.action_effectiveness.request_stick_validation(
                            action=decision.action_type,
                            metric_pattern=pattern,
                            db_getter=get_async_db
                        )
                        logger.info("👻📏 Validation request sent to The Stick")
                    except Exception as e:
                        logger.error(f"👻⚠️ Validation request failed: {e}")
                else:
                    logger.error(
                        f"👻❌ Execution failed: "
                        f"abort={network_result['aborted']}, reason={network_result['abort_reason']}"
                    )

                    pre_metrics_dict = {
                        'total_connections':      float(context.total_connections),
                        'suspicious_connections': float(context.suspicious_connections),
                        'network_anomalies':      float(context.network_anomalies),
                        'failed_auth_attempts':   float(context.failed_auth_attempts),
                        'recv_rate_bps':          float(context.recv_rate_bps),
                    }

                    await learning.update_outcome(
                        learning_record,
                        success=False,
                        threat_resolved=False,
                        false_positive=False,
                        false_negative=False,
                        outcome_notes=network_result.get('abort_reason', 'Execution failed'),
                        pre_metrics=pre_metrics_dict,
                        post_metrics=pre_metrics_dict,
                    )
                
                # ML v2 execution complete
                logger.info("👻� ML v2 execution complete")
                
        except Exception as e:
            logger.error(f"👻💥 QSP ML PIPELINE FAILED: {e}", exc_info=True)
            logger.error(
                "   ML-informed decision UNAVAILABLE. "
                "   Checking if emergency action needed to prevent security breach."
            )
            
            # Import emergency action utilities
            from app.services.system_failure_emitter import emit_system_failure_event, record_emergency_action
            
            # Emit failure event - EVERYONE sees this
            await emit_system_failure_event(
                agent_name="quantum_shadow_people",
                failure_type="ML_PIPELINE_FAILURE",
                error=str(e),
                emergency_action_taken=False,  # Will update if we take action
                context={
                    "resource_type": resource_type,
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                }
            )
            
            # Emergency action ONLY if there's an active critical threat
            # Check for: high suspicious connections, failed auth attempts, or critical severity
            threat_indicators = {
                'suspicious_connections': full_metrics.get('suspicious_connections', 0),
                'failed_auth_attempts': full_metrics.get('failed_auth_attempts', 0),
                'network_anomalies': full_metrics.get('network_anomalies', 0)
            }
            
            is_critical_threat = (
                severity in ["critical", "emergency"] or
                threat_indicators['suspicious_connections'] > 50 or
                threat_indicators['failed_auth_attempts'] > 20 or
                threat_indicators['network_anomalies'] > 10
            )
            
            if is_critical_threat:
                logger.error(
                    f"🚨 ACTIVE CRITICAL THREAT + ML DOWN: "
                    f"Emergency block to prevent security breach"
                )
                logger.error(f"   Threat indicators: {threat_indicators}")
                
                # Emergency network throttle/block
                from app.ai_agents.distributed.system_actions import SystemActions
                block_result = await SystemActions.throttle_network_operations()
                
                # Record emergency action with proper flagging
                await record_emergency_action(
                    agent="quantum_shadow_people",
                    action="emergency_network_throttle",
                    reason=f"ML_PIPELINE_FAILURE + active_critical_threat (severity={severity})",
                    ml_informed=False,  # THIS IS KEY - not a learned decision
                    metrics_before={"threat_indicators": threat_indicators},
                    metrics_after={"connections_throttled": block_result.get('connections_reduced', 0)},
                    success=block_result.get('success', False)
                )
                
                if block_result['success']:
                    logger.error(
                        f"🚨 Emergency throttle succeeded. "
                        f"Connections reduced: {block_result.get('connections_reduced', 0)}"
                    )
                    logger.error("   ⚠️ THIS WAS NOT ML-INFORMED. FIX THE ML PIPELINE. ⚠️")
                else:
                    logger.error(f"🚨 Emergency throttle FAILED: {block_result.get('error')}")
            else:
                # No critical threat - safe to fail without action
                logger.error(
                    f"   No active critical threat detected. "
                    f"   Threat indicators: {threat_indicators}"
                )
                logger.error("   No emergency action needed. FIX THE ML PIPELINE.")
                
                # Re-raise to make failure visible up the chain
                from app.ai_agents.exceptions import MLPipelineFailure
                raise MLPipelineFailure(f"QSP ML pipeline failed: {e}") from e
    
    async def handle_coordination(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        PHASE 1 REFACTOR: Accept coordination request directly from VIC-20 (not via Redis).
        
        This is the new direct communication path:
        VIC-20 calls this method directly and gets an immediate response.
        
        Flow:
        1. Receive coordination request directly from VIC-20
        2. Quantum analysis with paranoid security assessment (trust: 0.4)
        3. Execute network security action
        4. Return result to VIC-20
        5. Still broadcast to Redis for frontend observability
        
        Args:
            coordination_request: Dict containing resource_type, recommendation, severity, etc.
        
        Returns:
            Dict containing action result with success status and details
        """
        try:
            resource_type = coordination_request.get('resource_type', 'unknown')
            severity = coordination_request.get('severity', 'unknown')
            recommendation = coordination_request.get('recommendation', {})
            current_value = coordination_request.get('current_value', 0)
            threshold = coordination_request.get('threshold', 0)
            
            logger.info("=" * 80)
            logger.info(f"👻📞 DIRECT CALL RECEIVED: VIC-20 → QSP (Quantum Shadow People)")
            logger.info(f"    Resource: {resource_type} at {current_value:.1f}%")
            logger.info(f"    VIC-20 suggests: {recommendation.get('action', 'unknown')}")
            logger.info("=" * 80)
            
            # Use choice engine to decide (QSP has LOW trust - paranoid!)
            decision = self.choice_engine.should_follow_recommendation(
                recommendation=recommendation,
                current_situation={
                    'resource_type': resource_type,
                    'current_value': current_value,
                    'threshold': threshold,
                    'security_threat': True  # QSP always assumes threat
                }
            )
            
            logger.info(
                f"👻🔮 Quantum analysis complete: "
                f"{'ACCEPTABLE' if legacy_decision['followed_recommendation'] else 'SUSPICIOUS - USING OWN PROTOCOL'}"
            )
            logger.info(f"👻💭 {legacy_decision['reasoning']}")
            
            # Execute network throttle (QSP's specialty)
            action = legacy_decision['final_action']
            logger.info("👻🔒 EXECUTING QUANTUM NETWORK LOCKDOWN! *paranoid analysis intensifies*")
            
            # Broadcast action to WebSocket
            from app.services.agent_insight_emitter import emit_agent_insight
            await emit_agent_insight(
                from_agent="quantum_shadow_people",
                to_agent="vic20_sage",
                action="security_scan_executed",
                reasoning=f"{'Following VIC-20 recommendation' if legacy_decision['followed_recommendation'] else 'SUSPICIOUS - Using own protocol!'} - {resource_type} security lockdown",
                context={
                    "resource_type": resource_type,
                    "action": action,
                    "followed_vic20": legacy_decision['followed_recommendation'],
                    "severity": severity,
                    "current_value": current_value,
                    "threshold": threshold,
                    "paranoia_justified": True,
                    "quantum_state": "analyzing"
                }
            )
            
            network_result = await SystemActions.throttle_network_operations()
            
            if network_result['success']:
                logger.info(
                    f"👻✅ Network throttled! Connections: {network_result['connections_before']} → "
                    f"{network_result['connections_after']}. Quantum phase secured!"
                )
                
                # Broadcast success to WebSocket
                await emit_agent_insight(
                    from_agent="quantum_shadow_people",
                    to_agent="vic20_sage",
                    action="security_scan_success",
                    reasoning=f"Network secured: {network_result['connections_reduced']} connections reduced - Quantum phase stable",
                    context={
                        "success": True,
                        "connections_before": network_result['connections_before'],
                        "connections_after": network_result['connections_after'],
                        "connections_reduced": network_result['connections_reduced'],
                        "followed_vic20": legacy_decision['followed_recommendation']
                    }
                )
                
                # Write to PostgreSQL
                if self.db_integration and self.user_id:
                    try:
                        from datetime import datetime, timezone
                        quantum_decision = QSPDecision(
                            decision_type=QSPDecisionType.INTERDIMENSIONAL_SECURITY,
                            quantum_state=QuantumPhaseState.CORPOREAL,
                            network_target=f"network_security_{severity}",
                            optimization_parameters={
                                'action_taken': action,
                                'connections_reduced': network_result['connections_reduced'],
                                'threat_level': severity
                            },
                            tequila_jello_shots_required=2,
                            mysterious_explanation=legacy_decision['reasoning'],
                            technical_details={
                                'connections_before': network_result.get('connections_before', 0),
                                'connections_after': network_result.get('connections_after', 0),
                                'paranoia_justified': True
                            },
                            expected_improvement=float(network_result.get('connections_reduced', 0)),
                            confidence_level=legacy_decision['decision_score'],
                            timestamp=datetime.now(timezone.utc)
                        )
                        await self.db_integration.store_decision(self.user_id, quantum_decision)
                        logger.info(f"👻💾 Quantum decision written to PostgreSQL")
                    except Exception as e:
                        logger.error(f"👻💥 Failed to write to PostgreSQL: {e}")
                
                # Return result to VIC-20
                return {
                    'success': True,
                    'action': action,
                    'followed_vic20': legacy_decision['followed_recommendation'],
                    'connections_before': network_result['connections_before'],
                    'connections_after': network_result['connections_after'],
                    'connections_reduced': network_result['connections_reduced'],
                    'paranoia_justified': True,
                    'quantum_state': 'secured'
                }
            else:
                logger.error(f"👻❌ Network throttle failed: {network_result.get('error')}")
                return {
                    'success': False,
                    'error': network_result.get('error', 'Unknown error'),
                    'action': action,
                    'followed_vic20': legacy_decision['followed_recommendation']
                }
                
        except Exception as e:
            logger.error(f"👻💥 Error in direct coordination: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
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
        # Call the original analyze_network_metrics from QuantumShadowPeopleBrainV2
        decision = await self.analyze_network_metrics(
            network_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context
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
        
        # If critical or emergency, initiate deep scan
        if severity in ["critical", "emergency"]:
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
            "tequila_jello_shots": self.tequila_shots_today,
            "paranoia_level": self.paranoia_level,
            "threats_detected": self.threats_detected,
            "false_alarms": self.false_alarms,
            "quantum_phase_shifts": self.quantum_phase_shifts,
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
