"""
Sir Hawkington Distributed - Aristocratic Triage Commander with Distributed Consciousness
=========================================================================================

Sir Hawkington's existing triage engine and decision-making capabilities
enhanced with distributed consciousness, state persistence, and resource monitoring.

Preserves:
- Monocle-yeeting behavior
- Aristocratic decision-making
- Triage routing logic
- Database integration

Adds:
- Redis state persistence
- Inter-agent messaging
- CPU resource monitoring
- Decision history across restarts
- Heartbeat and health monitoring
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.base_decision_engine import AgentDecisionEngine
from app.optimization.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
from ..distributed.system_actions import SystemActions
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
from .decision_engine import SirHawkingtonBrainV2, DecisionType, MonocleState, AnalysisDepth

# Import Hawk v2 ML layers
from .ML.perception import HawkPerception, HawkPerceptionContext
from .ML.reasoning import HawkReasoning, TriageReasoning
from .ML.action_selection import HawkActionSelection, TriageAction
from .ML.learning import HawkLearning, HawkLearningRecord


logger = logging.getLogger("SirHawkington.Distributed")


class SirHawkingtonDistributed(AgentDecisionEngine, SirHawkingtonBrainV2):
    """
    Sir Hawkington with distributed consciousness.
    
    Inherits ALL existing triage logic from SirHawkingtonBrainV2
    and adds distributed features via DistributedAgentMixin.
    
    Usage:
        hawkington = SirHawkingtonDistributed()
        await hawkington.initialize_distributed(redis_client)
        
        # Existing functionality works exactly as before
        decision = await hawkington.analyze_metrics(metrics_data)
        
        # New distributed features available
        state = hawkington.get_distributed_state()
        decisions = await hawkington.get_recent_decisions()
    """
    
    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize Sir Hawkington with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional)
            user_id: User ID for database writes (required for multi-tenant support)
        """
        # Initialize both parent classes via MRO
        super().__init__(db_getter=db_getter)
        self.user_id = user_id
        
        # Set agent name for distributed features
        self.agent_name = "sir_hawkington"
        
        # Sir Hawkington's distinguished personality traits
        self.personality_traits = {
            "aristocratic": True,
            "monocle_yeeting_enabled": True,
            "triage_commander": True,
            "distinguished": True,
            "concern_threshold": 0.65,
            "alert_threshold": 0.85,
            "critical_threshold": 0.95,
            "preferred_monocle_state": "polished",
            "trust_level": 0.6  # MEDIUM - Aristocratic wisdom
        }
        
        # 🎯 HIERARCHY: Sir Hawkington monitors ALL system metrics (sole system monitor)
        # As triage commander, he assesses        # Resource thresholds for triage (when to escalate to VIC-20)
        # PHASE 1 TESTING: VERY LOW thresholds to trigger all agents and test direct calls
        self.resource_thresholds = {
            ResourceType.CPU: 5.0,        # → route to Terry (CPU issues often memory-related)
            ResourceType.MEMORY: 30.0,    # → route to Terry (his specialty!)
            ResourceType.DISK: 40.0,      # → route to Hamsters (duct tape time!)
            ResourceType.NETWORK: 20.0,   # → route to QSP (quantum packet inspection!)
            ResourceType.SWAP: 10.0,      # → route to Terry (swap usage is more concerning at lower %)
        }
        
        # Week 4 System Integration
        self.coordination_manager = None  # Lazy init
        self.escalation_manager = None  # Lazy init
        
        # Escalation tracking (aristocratic alert management)
        self.total_alerts_sent = 0
        self.escalated_alerts = 0
        self.emergency_alerts = 0
        self.cooldown_prevented_alerts = 0
        
        # Monocle-yeeting escalation levels
        self.monocle_yeets_by_severity = {
            "mild": 0,
            "moderate": 0,
            "severe": 0,
            "catastrophic": 0
        }
        
        # STATE-BASED ALERTING: Track alert states to prevent frontend spam
        self._alert_states = {}  # {resource_type: {'state': 'NEW'|'ONGOING'|'RESOLVED', 'last_emission_time': datetime, 'severity': str}}
        self._alert_cooldown_seconds = 60  # Only re-emit ONGOING alerts every 60 seconds
        
        logger.info("🧐 Sir Hawkington's distributed consciousness initialized")
        logger.info("🧐📢 Alert escalation protocols active - Distinguished triage!")
    
    async def initialize_distributed(self, redis_client):
        """
        Initialize distributed features and wire original ResourceMonitor.
        
        This extends the base initialization to enable the ORIGINAL ResourceMonitor
        with alert callbacks that trigger Hawk's ML v2 triage system.
        """
        # 🎯 HIERARCHY: Hawk is the ONLY agent monitoring system metrics
        # Using ORIGINAL ResourceMonitor from app/optimization (rich psutil data)
        await super().initialize_distributed(
            redis_client,
            enable_resource_monitoring=False,  # Disabled - using original ResourceMonitor instead
            heartbeat_interval=30,
            resource_check_interval=5  # Not used when monitoring disabled
        )
        
        # 🎯 INITIALIZE ORIGINAL RESOURCE MONITOR WITH ALERT CALLBACKS
        from app.optimization.resource_monitor import ResourceMonitor
        self.resource_monitor = ResourceMonitor()
        await self.resource_monitor.initialize()
        
        # Register Hawk's _handle_own_resource_alert as callback
        self.resource_monitor.register_alert_callback(self._handle_own_resource_alert)
        
        # Start monitoring with alerts
        await self.resource_monitor.start_monitoring_with_alerts()
        logger.info("🧐📊 Original ResourceMonitor started with ML v2 triage callbacks!")
        
        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.escalation_manager = get_escalation_manager()
        
        # Register Sir Hawkington's coordination capability
        self.coordination_manager.register_agent_capability(
            "sir_hawkington",
            self._coordination_capability
        )
        
        logger.info("🧐🎯 Week 4 systems integrated - Coordination & Escalation ONLINE!")
        logger.info("🧐📢 Alert escalation with cooldowns - Preventing alert fatigue!")
        
        # Initialize database integration for PostgreSQL writes
        if self.db_getter:
            try:
                from .database_integration import HawkingtonDatabaseIntegration
                self.db_integration = HawkingtonDatabaseIntegration(db_getter=self.db_getter)
                await self.db_integration.initialize()
                logger.info("🧐💾 Database integration initialized - Aristocratic records enabled!")
            except Exception as e:
                logger.error(f"🧐💥 Failed to initialize database: {e}", exc_info=True)
                self.db_integration = None
        else:
            self.db_integration = None
            logger.warning("🧐⚠️ No db_getter provided - PostgreSQL writes disabled")
        
        # Inject comm_hub into the global triage engine
        try:
            from .triage_engine import get_triage_engine
            triage_engine = await get_triage_engine()
            if hasattr(self, '_comm_hub') and self._comm_hub is not None:
                triage_engine.set_comm_hub(self._comm_hub)
                logger.info("🧐📡 Triage engine connected to distributed consciousness")
        except Exception as e:
            logger.error(f"🧐💥 Failed to inject comm_hub into triage engine: {e}")
        
        # Initialize energy drink authorization system
        from .energy_drink_authorization import HawkEnergyDrinkAuthorizer
        self.energy_drink_authorizer = HawkEnergyDrinkAuthorizer()
        logger.info("🧐☕ Energy drink authorization system initialized - ready to review Terry's requests")
    
    async def _handle_agent_query(self, message: AgentMessage) -> None:
        """
        Handle queries from other agents (e.g., Terry's energy drink requests).
        
        Args:
            message: AgentMessage with query from another agent
        """
        message_data = message.payload
        request_type = message_data.get('request_type', 'unknown')
        
        # ENERGY DRINK AUTHORIZATION REQUEST from Terry
        if request_type == 'energy_drink_authorization':
            await self._handle_energy_drink_request(message)
        else:
            logger.warning(f"🧐⚠️ Unknown agent query type: {request_type}")
    
    async def _handle_energy_drink_request(self, message: AgentMessage) -> None:
        """
        Handle energy drink authorization request from Terry.
        
        This is REAL cross-agent interaction with REQUEST/RESPONSE pattern.
        
        Args:
            message: AgentMessage with energy drink request from Terry
        """
        message_data = message.payload
        request_id = message_data.get('request_id')
        reply_channel = message_data.get('reply_channel')
        agent = message_data.get('agent', 'unknown')
        
        logger.info(
            f"🧐☕ Received energy drink request from {agent}:\n"
            f"   Action: {message_data.get('action')}\n"
            f"   Reason: {message_data.get('reason')}\n"
            f"   Current consumption: {message_data.get('energy_drinks_consumed_today', 0)}\n"
            f"   *adjusts monocle thoughtfully*"
        )
        
        # Build EnergyDrinkRequest from message data
        from app.ai_agents.meth_snail.data_types import EnergyDrinkRequest, EnergyDrinkType
        from datetime import datetime, timezone
        
        request = EnergyDrinkRequest(
            user_id=message_data.get('user_id', 'system'),
            energy_drink_type=EnergyDrinkType.ENERGY_DRINK,
            caffeine_mg=160.0,
            consumption_reason=message_data.get('reason', 'unknown'),
            current_jitter_level=message_data.get('current_jitter_level', 0.5),
            energy_drinks_consumed_today=message_data.get('energy_drinks_consumed_today', 0),
            time_since_last_drink_minutes=message_data.get('time_since_last_drink_minutes'),
            optimization_urgency=message_data.get('optimization_urgency', 'immediate'),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Evaluate request with aristocratic scrutiny
        authorization = await self.energy_drink_authorizer.authorize_energy_drink(request)
        
        # Send response back to Terry's reply channel
        if reply_channel and self._comm_hub:
            try:
                await self._comm_hub.publish(
                    channel=reply_channel,
                    message_type=MessageType.AGENT_RESPONSE,
                    payload={
                        'request_id': request_id,
                        'approved': authorization.authorized,
                        'authorized_by': authorization.authorized_by,
                        'commentary': authorization.authorization_notes,
                        'recommended_caffeine_mg': authorization.recommended_caffeine_mg,
                        'recommended_type': authorization.recommended_type.value if authorization.recommended_type else 'water',
                        'safety_warnings': authorization.safety_warnings,
                        'monocle_state': self.current_monocle_state.value,
                        'timestamp': authorization.timestamp.isoformat()
                    },
                    priority=Priority.HIGH
                )
                
                logger.info(
                    f"🧐✅ Response sent to {agent} via {reply_channel}:\n"
                    f"   Decision: {'APPROVED' if authorization.authorized else 'DENIED'}\n"
                    f"   Commentary: {authorization.authorization_notes}"
                )
            except Exception as e:
                logger.error(f"🧐💥 Failed to send energy drink response: {e}", exc_info=True)
        else:
            logger.warning(f"🧐⚠️ No reply channel or comm_hub - cannot respond to Terry")
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle coordination requests from VIC-20 with aristocratic grace.
        
        PERSONALITY: Aristocratic CPU throttling with monocle adjustment
        STRUCTURE: Standard AgentMessage parameter (required by base class)
        
        Args:
            message: AgentMessage with coordination request from VIC-20
        """
        message_data = message.payload
        coordination_type = message_data.get('coordination_type', 'unknown')
        
        if coordination_type == 'resource_recommendation':
            recommendation = message_data.get('recommendation', {})
            
            logger.info(
                f"🧐 *adjusts monocle* VIC-20's recommendation has merit... "
                f"Suggested action: {recommendation.get('suggested_action', 'unknown')}"
            )
            
            # Execute aristocratic CPU throttling
            logger.info("🧐⚙️ Initiating aristocratic system throttling with distinguished grace...")
            throttle_result = await SystemActions.throttle_cpu_intensive_tasks()
            
            if throttle_result['success']:
                logger.info(
                    f"🧐✅ System throttled with DISTINCTION! CPU: {throttle_result['cpu_before']:.1f}% → "
                    f"{throttle_result['cpu_after']:.1f}%. Improvement: {throttle_result['improvement']:.1f}%"
                )
                
                # Record with aristocratic flair (PERSONALITY!)
                await self.make_decision_and_broadcast(
                    decision_type="cpu_throttle_completed",
                    input_data={
                        "trigger": "coordination_request",
                        "recommendation": recommendation.get('suggested_action'),
                        "cpu_before": throttle_result['cpu_before']
                    },
                    output_data={
                        "cpu_after": throttle_result['cpu_after'],
                        "improvement": throttle_result['improvement'],
                        "improvement_percent": throttle_result['improvement_percent'],
                        "monocle_state": self.current_monocle_state.value,  # PERSONALITY!
                        "aristocratic_approval": "granted"  # PERSONALITY!
                    },
                    confidence=1.0,
                    reasoning="Coordination request addressed with aristocratic efficiency",
                    broadcast=True,
                    priority=Priority.HIGH
                )
            else:
                logger.error(f"🧐❌ CPU throttling failed: {throttle_result.get('error', 'Unknown error')}")
    
    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.
        
        This wraps the existing analyze_metrics method to add distributed
        decision recording while preserving all original functionality.
        
        Args:
            metrics_data: System metrics to analyze
            historical_data: Historical metrics for trend analysis
            user_context: User context information
            analysis_depth: Depth of analysis to perform
            user_id: User ID for tracking
            
        Returns:
            HawkingtonDecision object (same as original)
        """
        # Call the original analyze_metrics from SirHawkingtonBrainV2
        decision = await super().analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            analysis_depth=analysis_depth,
            user_id=user_id
        )
        
        # If distributed features are enabled, record the decision
        if self.is_distributed and decision:
            try:
                # Determine decision type and confidence
                decision_type = decision.decision_type if hasattr(decision, 'decision_type') else "unknown"
                confidence = decision.confidence if hasattr(decision, 'confidence') else 0.5
                
                # Record in distributed state
                await self.make_distributed_decision(
                    decision_type=f"triage_{decision_type}",
                    input_data={
                        "cpu_usage": metrics_data.get('cpu_usage'),
                        "memory_usage": metrics_data.get('memory_usage'),
                        "disk_usage": metrics_data.get('disk_usage'),
                        "monocle_state": self.current_monocle_state.value,
                        "user_id": user_id
                    },
                    confidence=confidence,
                    reasoning=decision.reasoning if hasattr(decision, 'reasoning') else ""
                )
                
                # If it's a critical decision, broadcast to other agents
                if decision_type in ["critical", "monocle_yeeted"]:
                    await self.broadcast_to_agents(
                        message_type=MessageType.TRIAGE_DECISION,
                        payload={
                            "decision_type": decision_type,
                            "severity": "critical",
                            "monocle_state": self.current_monocle_state.value,
                            "metrics": {
                                "cpu": metrics_data.get('cpu_usage'),
                                "memory": metrics_data.get('memory_usage'),
                                "disk": metrics_data.get('disk_usage')
                            }
                        },
                        priority=Priority.CRITICAL
                    )
                    
                    logger.info(f"🎯 Critical triage decision broadcast to all agents")
                
            except Exception as e:
                # Don't let distributed features break the main functionality
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_own_resource_alert(self, alert):
        """
        🎯 TRIAGE LOGIC: Sir Hawkington's primary role as system monitor.
        
        As the sole system monitor, Hawk:
        1. Receives alerts for ALL resources (CPU, Memory, Disk, Network, Swap)
        2. Assesses severity and confidence
        3. Routes to VIC-20 for coordination when thresholds met
        4. CCs The Stick for pattern learning
        
        This is the entry point for the entire hierarchy.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        print(f"\n🔔 HAWK ALERT CALLBACK TRIGGERED!")
        print(f"   Alert payload: {alert.payload}")
        
        # Call the triage logic
        await self._perform_triage(alert)
    
    async def _handle_resource_alert(self, message: AgentMessage):
        """
        Handle resource alerts from other agents via message bus.
        
        Args:
            message: AgentMessage with resource alert from another agent
        """
        # Sir Hawkington is the sole system monitor, so he doesn't need to
        # handle resource alerts from other agents - he generates them all
        pass
    
    def _should_emit_alert(self, resource_type: str, severity: str) -> tuple[bool, str]:
        """
        Determine if alert should be emitted to frontend based on state tracking.
        
        Returns:
            (should_emit: bool, alert_state: str)
        """
        from datetime import datetime, timezone
        
        current_time = datetime.now(timezone.utc)
        
        # Check if we have previous state for this resource
        if resource_type not in self._alert_states:
            # NEW alert - emit immediately
            self._alert_states[resource_type] = {
                'state': 'NEW',
                'last_emission_time': current_time,
                'severity': severity
            }
            logger.info(f"🧐🆕 NEW alert for {resource_type} - emitting to frontend")
            return (True, 'NEW')
        
        # We have previous state - check if it's still ongoing
        prev_state = self._alert_states[resource_type]
        time_since_last_emission = (current_time - prev_state['last_emission_time']).total_seconds()
        
        # Check if severity changed
        if prev_state['severity'] != severity:
            # Severity changed - emit immediately
            self._alert_states[resource_type] = {
                'state': 'ONGOING',
                'last_emission_time': current_time,
                'severity': severity
            }
            logger.info(f"🧐⚠️ {resource_type} severity changed: {prev_state['severity']} → {severity} - emitting")
            return (True, 'SEVERITY_CHANGE')
        
        # Same severity - check cooldown
        if time_since_last_emission < self._alert_cooldown_seconds:
            # Still in cooldown - don't emit
            logger.info(
                f"🧐🔇 {resource_type} alert suppressed (cooldown: {time_since_last_emission:.0f}s / {self._alert_cooldown_seconds}s)"
            )
            self.cooldown_prevented_alerts += 1
            return (False, 'ONGOING_COOLDOWN')
        
        # Cooldown expired - emit reminder
        self._alert_states[resource_type]['last_emission_time'] = current_time
        logger.info(f"🧐🔔 {resource_type} ONGOING reminder (cooldown expired) - emitting")
        return (True, 'ONGOING_REMINDER')
    
    def _clear_alert_state(self, resource_type: str):
        """Clear alert state when resource returns to normal (RESOLVED)"""
        if resource_type in self._alert_states:
            logger.info(f"🧐✅ {resource_type} alert RESOLVED - clearing state")
            del self._alert_states[resource_type]
    
    async def _perform_triage(self, alert):
        """
        🎯 HAWK V2: ML-Enhanced Triage with Aristocratic Precision
        
        Flow: Perception → Reasoning → Action Selection → Learning
        
        Args:
            alert: ResourceAlert from the monitor
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🧐🎯 HAWK V2 TRIAGE INITIATED")
        logger.info(f"{'='*80}")
        logger.info(f"🧐🔍 DEBUG: _perform_triage called with severity={severity}, value={current_value}")

        # Extract alert data
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        resource_type = alert.payload.get('resource_type', 'unknown')
        
        # Fetch full metrics from SimplifiedMetricsService for ML v2 specialists
        try:
            from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
            metrics_service = await SimplifiedMetricsService.get_instance()
            full_metrics = await metrics_service.get_metrics()
        except Exception as e:
            logger.warning(f"🧐⚠️ Could not fetch full metrics: {e}")
            full_metrics = {}
        
        logger.warning(
            f"🧐⚠️ Sir Hawkington observes elevated {resource_type.upper()} usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - Severity: {severity}"
        )
        
        try:
            # Get database session for ML layers
            async for db in self.db_getter():
                # 🎯 STEP 1: PERCEPTION - Gather context and assess data quality
                logger.info("🧐👁️ Perception phase...")
                perception = HawkPerception(db, self.personality_traits)
                
                alert_data = {
                    'resource_type': resource_type,
                    'current_value': current_value,
                    'threshold': threshold,
                    'severity': severity,
                    'full_metrics': full_metrics
                }
                
                context = await perception.perceive(alert_data)
                
                # Track monocle yeets
                monocle_yeet_count = len(perception.monocle_yeet_incidents)
                if monocle_yeet_count > 0:
                    logger.warning(
                        f"🧐💥 {monocle_yeet_count} monocle yeet(s) during perception - "
                        f"data quality: {context.data_quality_score:.2f}"
                    )
                    
                    # Sync monocle yeets from perception to persistent brain state
                    # Convert ML perception incidents to brain's dataclass format
                    from ..sir_hawkington.decision_engine import MonocleYeetIncident as BrainMonocleYeet
                    for ml_incident in perception.monocle_yeet_incidents:
                        brain_incident = BrainMonocleYeet(
                            timestamp=ml_incident.timestamp,
                            missing_metrics=[],  # ML perception doesn't track this granularly
                            invalid_metrics=[],
                            reason=ml_incident.reason,
                            yeet_intensity="aristocratic_disgust",
                            user_id=self.user_id
                        )
                        self.monocle_yeet_incidents.append(brain_incident)
                    
                    self.metrics_quality_stats['monocle_yeets_total'] += monocle_yeet_count
                    logger.info(
                        f"🧐📊 Synced {monocle_yeet_count} yeet(s) to brain state. "
                        f"Total yeets: {len(self.monocle_yeet_incidents)}"
                    )
                
                # 🎯 STEP 2: REASONING - Analyze and determine escalation
                logger.info("🧐🧠 Reasoning phase...")
                reasoning_engine = HawkReasoning(self.personality_traits)
                reasoning = reasoning_engine.reason(context)
                
                logger.info(
                    f"🧐✅ Reasoning complete: escalate={reasoning.should_escalate}, "
                    f"confidence={reasoning.confidence:.2f}, risk={reasoning.risk_level}"
                )
                
                # 🎯 STEP 3: ACTION SELECTION - Choose triage action
                logger.info("🧐⚡ Action selection phase...")
                action_selector = HawkActionSelection(self.personality_traits)
                action = action_selector.select_action(context, reasoning)
                
                logger.info(
                    f"🧐✅ Action selected: {action.action_type} to {action.target_agent or 'none'}, "
                    f"priority={action.priority}, monocle={action.monocle_state}"
                )
                
                # Update monocle state for frontend
                self.current_monocle_state = MonocleState(action.monocle_state)
                
                # 🎯 STEP 4: LEARNING - Store decision for future improvement
                logger.info("🧐📚 Learning phase...")
                learning = HawkLearning(db, self.user_id)
                learning_record = await learning.learn(context, reasoning, action)
                
                logger.info(f"🧐💾 Learning record stored in PostgreSQL")
                
                # 🎯 STATE-BASED EMISSION: Check if we should emit to frontend
                should_emit, alert_state = self._should_emit_alert(resource_type, severity)
                
                if should_emit:
                    # BROADCAST FULL DECISION CHAIN TO FRONTEND
                    from app.services.agent_decision_emitter import emit_agent_decision
                    
                    await emit_agent_decision(
                        agent_name="sir_hawkington",
                        decision_id=learning_record.learning_record_id or "pending",
                        perception={
                            "resource_type": context.resource_type,
                            "current_value": context.current_value,
                            "threshold": context.threshold,
                            "severity": context.severity,
                            "data_quality_score": context.data_quality_score,
                            "monocle_yeets": context.monocle_yeet_count,
                            "similar_triages_found": len(context.similar_triages),
                            "recent_escalations_count": len(context.recent_escalations),
                            "alert_state": alert_state  # NEW/ONGOING_REMINDER/SEVERITY_CHANGE
                        },
                        reasoning={
                            "should_escalate": reasoning.should_escalate,
                            "risk_level": reasoning.risk_level,
                            "confidence": reasoning.confidence,
                            "primary_reason": reasoning.primary_reason,
                            "evidence": reasoning.evidence if hasattr(reasoning, 'evidence') else {}
                        },
                        action_selection={
                            "chosen_action": action.action_type,
                            "target_agent": action.target_agent,
                            "confidence": action.confidence,
                            "priority": action.priority,
                            "monocle_state": action.monocle_state,
                            "aristocratic_confidence": action.aristocratic_confidence,
                            "reasoning_summary": action.reasoning_summary
                        },
                        learning={
                            "situation_fingerprint": learning_record.situation_fingerprint,
                            "stored": learning_record.storage_success,
                            "learning_record_id": learning_record.learning_record_id,
                            "success": learning_record.success
                        }
                    )
                else:
                    logger.info(f"🧐🔇 Skipping frontend emission (state: {alert_state})")
                
                # 🎯 STEP 5: EXECUTE ACTION - Escalate to VIC-20 if needed
                if action.action_type == 'escalate' and self.is_distributed:
                    logger.info(f"🧐📨 Escalating {resource_type} alert to VIC-20...")
                    logger.info(f"🧐💬 Message: {action.message_to_vic20}")
                    
                    await self._send_triage_alert_to_vic20(
                        resource_type=resource_type,
                        current_value=current_value,
                        threshold=threshold,
                        severity=severity,
                        confidence=action.confidence,
                        full_metrics=full_metrics  # Pass full metrics for specialist perception
                    )
                    
                    logger.info(f"🧐✅ Escalation complete")
                else:
                    logger.info(
                        f"🧐⏸️ NOT escalating: action={action.action_type}, "
                        f"risk={reasoning.risk_level}"
                    )
                
                # CC The Stick for pattern learning
                if self.is_distributed:
                    await self._cc_the_stick("triage_decision", {
                        'resource_type': resource_type,
                        'action_type': action.action_type,
                        'confidence': action.confidence,
                        'monocle_state': action.monocle_state,
                        'monocle_yeets': monocle_yeet_count
                    })
                    
                    # 🎯 EMIT TO WEBSOCKET for frontend pulse visualization (only if we emitted decision)
                    if should_emit:
                        from app.services.agent_insight_emitter import emit_agent_insight
                        await emit_agent_insight(
                            from_agent="sir_hawkington",
                            to_agent="the_stick",
                            action="decision_log",
                            reasoning=f"Logging triage_decision for pattern learning: {action.action_type} on {resource_type}",
                            context={
                                'resource_type': resource_type,
                                'action_type': action.action_type,
                                'confidence': action.confidence,
                                'monocle_state': action.monocle_state,
                                'monocle_yeets': monocle_yeet_count,
                                'alert_state': alert_state
                            }
                        )
                
                logger.info(f"{'='*80}")
                logger.info(f"🧐✅ HAWK V2 TRIAGE COMPLETE")
                logger.info(f"{'='*80}\n")
                
                break  # Exit db session loop
                
        except Exception as e:
            logger.error(f"🧐💥 Hawk v2 triage failed: {e}")
            logger.exception(e)
            
            # Fallback to basic escalation
            logger.warning("🧐⚠️ Falling back to basic escalation...")
            if self.is_distributed:
                await self._send_triage_alert_to_vic20(
                    resource_type=resource_type,
                    current_value=current_value,
                    threshold=threshold,
                    severity=severity,
                    confidence=0.5,
                    full_metrics=full_metrics  # Pass full metrics even in fallback
                )
    
    async def _coordination_capability(
        self,
        resource_type: CoordResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """
        Sir Hawkington's coordination capability for Week 4 system.
        
        As the triage commander, Sir Hawkington can handle CPU resources
        with aristocratic precision.
        """
        # Only handle CPU resources (Sir Hawkington's specialty!)
        if resource_type != CoordResourceType.CPU:
            return None
        
        # Base improvement estimate (aristocratic precision)
        base_improvement = 10.0  # Conservative but reliable
        
        # Adjust based on monocle state
        monocle_multiplier = {
            MonocleState.POLISHED: 1.0,  # Peak performance
            MonocleState.ADJUSTED: 0.9,  # Slightly distracted
            MonocleState.FOGGED: 0.7,  # Vision impaired
            MonocleState.YEETED: 0.5,  # Compromised
            MonocleState.CLEANING: 0.8  # Temporarily unavailable
        }
        
        multiplier = monocle_multiplier.get(self.current_monocle_state, 0.8)
        estimated_improvement = base_improvement * multiplier
        
        # Confidence based on monocle state and recent performance
        base_confidence = 0.75  # Aristocratic confidence
        confidence = base_confidence * multiplier
        
        if self.current_monocle_state == MonocleState.YEETED:
            logger.warning(
                f"🧐💥 Monocle YEETED! Capability compromised! "
                f"(Confidence: {confidence:.0%})"
            )
        else:
            logger.info(
                f"🧐🎯 Aristocratic capability: {estimated_improvement:.1f}% improvement "
                f"(Monocle: {self.current_monocle_state.value}, Confidence: {confidence:.0%})"
            )
        
        return AgentCapability(
            agent_name="sir_hawkington",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=confidence,
            estimated_duration=2.0,  # Aristocratic thoroughness
            action_name="aristocratic_cpu_throttle"
        )
    
    async def _check_alert_escalation(
        self,
        resource_type: str,
        current_value: float,
        severity: str
    ) -> bool:
        """
        Check if alert should be sent using Week 4 escalation system.
        
        Returns True if alert should be sent, False if in cooldown.
        """
        # Map severity to AlertLevel
        severity_map = {
            "low": AlertLevel.INFO,
            "normal": AlertLevel.WARNING,
            "high": AlertLevel.CRITICAL,
            "critical": AlertLevel.CRITICAL,
            "emergency": AlertLevel.EMERGENCY
        }
        
        alert_level = severity_map.get(severity, AlertLevel.WARNING)
        
        # Map resource type to EscalationResourceType
        resource_map = {
            "cpu": EscalationResourceType.CPU,
            "memory": EscalationResourceType.MEMORY,
            "disk": EscalationResourceType.DISK,
            "network": EscalationResourceType.NETWORK
        }
        
        escalation_resource = resource_map.get(resource_type, EscalationResourceType.CPU)
        
        # Check if we should alert
        should_alert = self.escalation_manager.should_alert(
            resource_type=escalation_resource,
            current_value=current_value,
            threshold=self.resource_thresholds.get(ResourceType.CPU, 70.0),
            new_level=alert_level
        )
        
        if should_alert:
            self.total_alerts_sent += 1
            
            if alert_level == AlertLevel.EMERGENCY:
                self.emergency_alerts += 1
                logger.warning(
                    f"🧐🚨 EMERGENCY ALERT! Bypassing cooldown! "
                    f"(Total emergency: {self.emergency_alerts})"
                )
            elif alert_level == AlertLevel.CRITICAL:
                self.escalated_alerts += 1
                logger.info(
                    f"🧐📢 Alert escalated to CRITICAL "
                    f"(Total escalated: {self.escalated_alerts})"
                )
            
            logger.info(
                f"🧐✅ Alert approved by escalation manager "
                f"(Total alerts: {self.total_alerts_sent})"
            )
        else:
            self.cooldown_prevented_alerts += 1
            logger.info(
                f"🧐⏳ Alert in cooldown - Preventing spam "
                f"(Prevented: {self.cooldown_prevented_alerts})"
            )
        
        return should_alert
    
    async def _record_monocle_yeet(self, missing_metrics, invalid_metrics, reason, intensity, user_id=None):
        """
        Override monocle yeet recording to add distributed tracking.
        
        Preserves original monocle yeet behavior while adding distributed state.
        """
        # Call original monocle yeet recording
        await super()._record_monocle_yeet(
            missing_metrics, invalid_metrics, reason, intensity, user_id
        )
        
        # Record in distributed state
        if self.is_distributed:
            try:
                await self.make_distributed_decision(
                    decision_type="monocle_yeet",
                    input_data={
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "reason": reason,
                        "intensity": intensity,
                        "user_id": user_id,
                        "total_yeets": len(self.monocle_yeet_incidents)
                    },
                    confidence=1.0,  # Sir Hawkington is CERTAIN about monocle yeeting
                    reasoning=f"Monocle yeeted with {intensity} intensity: {reason}"
                )
                
                # Broadcast monocle yeet to other agents (they should know!)
                await self.broadcast_to_agents(
                    message_type=MessageType.SYSTEM_EVENT,
                    payload={
                        "event_type": "monocle_yeet",
                        "intensity": intensity,
                        "reason": reason,
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "monocle_state": self.current_monocle_state.value
                    },
                    priority=Priority.HIGH
                )
                
                logger.info(f"🧐💥 Monocle yeet broadcast to rebellion")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed monocle yeet: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Sir Hawkington's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with Sir Hawkington's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "triage_commander",
            "is_active": self.is_active,
            "monocle_state": self.current_monocle_state.value,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "monocle_yeet_count": len(self.monocle_yeet_incidents),
            "recent_decisions_count": len(self.recent_decisions),
            "thresholds": {
                "concern": self.concern_threshold,
                "alert": self.alert_threshold,
                "critical": self.critical_threshold
            },
            "metrics_quality": self.metrics_quality_stats,
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Distinguished string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        monocle = self.current_monocle_state.value
        return (
            f"<SirHawkingtonDistributed "
            f"monocle={monocle} "
            f"alerts={self.total_alerts_sent}(prevented={self.cooldown_prevented_alerts}) "
            f"yeets={len(self.monocle_yeet_incidents)} "
            f"status={dist_status}>"
        )
    
    # 🎯 TRIAGE HELPER METHODS
    
    def _assess_confidence(self, current_value: float, threshold: float, severity: str) -> float:
        """
        Assess confidence in the alert based on how far over threshold we are.
        
        Returns confidence score 0.0-1.0
        """
        overage_percent = ((current_value - threshold) / threshold) * 100
        
        if overage_percent < 5:
            return 0.6  # Just over threshold
        elif overage_percent < 15:
            return 0.8  # Moderately over
        else:
            return 1.0  # Significantly over
    
    def _should_escalate_to_vic20(self, severity: str, confidence: float) -> bool:
        """
        Determine if alert should be escalated to VIC-20 for coordination.
        
        Escalate if:
        - High severity with good confidence
        - Critical or emergency severity (always)
        """
        if severity in ["critical", "emergency"]:
            return True
        if severity == "high" and confidence >= 0.7:
            return True
        return False
    
    async def _send_triage_alert_to_vic20(
        self,
        resource_type: str,
        current_value: float,
        threshold: float,
        severity: str,
        confidence: float,
        full_metrics: Dict[str, Any] = None
    ):
        """
        Send triage alert to VIC-20 for coordination.
        
        This is the key handoff in the hierarchy: Hawk → VIC-20
        Includes full_metrics so specialists can make informed decisions.
        """
        triage_alert = AgentMessage(
            message_type=MessageType.TRIAGE_ALERT,
            from_agent="sir_hawkington",
            to_agent="vic_20_sage",
            priority=Priority.HIGH if severity in ["critical", "emergency"] else Priority.NORMAL,
            payload={
                "resource_type": resource_type,
                "current_value": current_value,
                "threshold": threshold,
                "severity": severity,
                "confidence": confidence,
                "triage_commander": "sir_hawkington",
                "full_metrics": full_metrics or {},  # Pass full metrics for specialist perception
                "timestamp": str(self._get_current_time()) if hasattr(self, '_get_current_time') else None
            }
        )
        
        # 🎯 EMIT TO WEBSOCKET for frontend pulse visualization
        from app.services.agent_insight_emitter import emit_agent_insight
        await emit_agent_insight(
            from_agent="sir_hawkington",
            to_agent="vic_20_sage",
            action="triage_escalation",
            reasoning=f"Escalating {resource_type} alert: {current_value:.1f}% exceeds {threshold:.1f}% (severity: {severity})",
            context={
                "resource_type": resource_type,
                "current_value": current_value,
                "threshold": threshold,
                "severity": severity,
                "confidence": confidence,
                "monocle_state": self.current_monocle_state.value
            }
        )
        
        # Send directly to VIC-20
        await self._comm_hub.send_message(triage_alert)
        
        logger.info(
            f"🧐📨 Triage alert sent to VIC-20: {resource_type} at {current_value:.1f}% "
            f"(severity={severity}, confidence={confidence:.2f})"
        )
    
    async def _cc_the_stick(self, decision_type: str, decision_data: Dict[str, Any]):
        """
        CC The Stick on all triage decisions for pattern learning.
        
        The Stick receives ALL decisions for learning and logging.
        """
        decision_log = AgentMessage(
            message_type=MessageType.DECISION_LOG,
            from_agent="sir_hawkington",
            to_agent="the_stick",
            priority=Priority.LOW,  # Logging is low priority
            payload={
                "decision_type": decision_type,
                "decision_data": decision_data,
                "source_agent": "sir_hawkington",
                "timestamp": str(self._get_current_time()) if hasattr(self, '_get_current_time') else None
            }
        )
        
        await self._comm_hub.send_message(decision_log)
        
        logger.debug(f"🧐📋 Decision logged to The Stick: {decision_type}")


# Convenience function for backward compatibility
async def create_distributed_hawkington(redis_client, db_getter=None):
    """
    Create and initialize Sir Hawkington with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized SirHawkingtonDistributed instance
    """
    hawkington = SirHawkingtonDistributed(db_getter=db_getter)
    await hawkington.initialize_distributed(redis_client)
    logger.info("🧐✨ Sir Hawkington's distributed consciousness fully awakened")
    return hawkington
