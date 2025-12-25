"""
Terry the Meth Snail Distributed - Speed Demon with Distributed Consciousness
==============================================================================

Terry's existing optimization engine and energy drink authorization
enhanced with distributed consciousness, memory monitoring, and cache management.

Preserves:
- Shell-spinning behavior (waiting for real data)
- Optimization decision-making
- Energy drink authorization
- Database integration
- NO FAKE DATA policy

Adds:
- Redis state persistence
- Memory resource monitoring (75% threshold)
- Emergency cache clearing on critical memory
- Energy drink tracking across restarts
- Shell spin incident broadcasting
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from ..distributed.base_decision_engine import AgentDecisionEngine
from ..distributed.resource_monitor import ResourceType
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
from .decision_engine import MethSnailBrainV2, OptimizationPriority, AnalysisDepth


logger = logging.getLogger("MethSnail.Distributed")


class MethSnailDistributed(AgentDecisionEngine, MethSnailBrainV2):
    """
    Terry the Meth Snail with distributed consciousness.
    
    GOTTA GO FAST... but now with memory persistence!
    
    Inherits ALL existing optimization logic from MethSnailBrainV2
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize Terry with distributed consciousness.
        
        Args:
            db_getter: Database session factory for PostgreSQL writes
            user_id: User ID for database writes (required for multi-tenant support)
        """
        # Initialize decision engine (parent class)
        super().__init__(db_getter=db_getter)
        self.user_id = user_id
        
        # Set agent name for distributed features
        self.agent_name = "meth_snail"
        
        # Terry's hyperactive personality traits
        self.personality_traits = {
            "speed_obsessed": True,
            "hyperactive": True,
            "shell_spinning_enabled": True,
            "cache_clearing_frequency": "MAXIMUM",
            "energy_drink_powered": True,
            "no_fake_data_tolerance": 0,
            "optimization_priority": "speed",
            "jitter_level": "moderate",
            "trust_level": 0.2  # VERY LOW - Terry thinks he's faster!
        }
        
        # 🎯 PHASE 4: Terry does NOT monitor resources
        # He receives coordination requests from VIC-20
        self.resource_thresholds = {}
        
        # Initialize choice engine (Task 4.1 Enhanced) - VERY LOW trust!
        self.choice_engine = AgentChoiceEngine(self.agent_name, self.personality_traits)
        
        # Week 4 System Integration
        self.coordination_manager = None  # Lazy init
        self.verification_manager = None  # Lazy init
        
        # Override learning tracking (Terry learns when his way is actually faster!)
        self.total_overrides = 0
        self.successful_overrides = 0  # When Terry's way worked better
        self.failed_overrides = 0  # When VIC-20 was right
        self.override_success_rate = 0.0
        
        # Energy drink tracking
        self.energy_drinks_today = 0
        self.shell_spins_today = 0
        
        logger.info("🐌💨 Terry the Meth Snail's distributed consciousness initialized - GOTTA GO FAST!")
        logger.info("🐌🧠 Choice engine online - I'm FASTER than VIC-20's recommendations!")
        logger.info("🐌📊 Override learning active - Tracking when I'm right!")
    
    async def initialize_distributed(self, redis_client):
        """
        Initialize distributed features and subscribe to VIC-20 coordination requests.
        
        PHASE 4: Terry receives COORDINATION_REQUEST from VIC-20 only.
        No resource monitoring - VIC-20 routes work to him.
        """
        # Call parent initialization - NO resource monitoring for Terry
        await super().initialize_distributed(
            redis_client,
            enable_resource_monitoring=False  # Terry doesn't monitor
        )
        
        # Initialize database integration for PostgreSQL writes
        if self.db_getter:
            try:
                # Initialize database integration with db_getter (it handles the async generator)
                from .database_integration import MethSnailDatabaseIntegration
                self.db_integration = MethSnailDatabaseIntegration(self.db_getter)
                await self.db_integration.initialize()
                self._db_initialized = True
                
                logger.info("🐌💾 Database integration initialized")
            except Exception as e:
                logger.error(f"🐌💥 Failed to initialize database: {e}", exc_info=True)
        
        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.verification_manager = get_verification_manager()
        
        # Register Terry's coordination capability
        self.coordination_manager.register_agent_capability(
            "meth_snail",
            self._coordination_capability
        )
        
        # CRITICAL: Subscribe to COORDINATION_REQUEST from VIC-20
        await self.subscribe_to_messages(
            message_type=MessageType.COORDINATION_REQUEST,
            callback=self._handle_coordination_request
        )
        
        logger.info("🐌🎯 Week 4 systems integrated - Coordination & Verification ONLINE!")
        logger.info("🐌📊 Learning when I'm FASTER than VIC-20!")
        logger.info("🐌📡 Subscribed to COORDINATION_REQUEST - Ready to receive from VIC-20!")
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        TERRY V2: ML-Enhanced Agentic Decision Making
        
        Flow:
        1. PERCEPTION: Gather full context (metrics, history, patterns)
        2. REASONING: Analyze root cause with ML validation
        3. ACTION SELECTION: Choose best action based on evidence
        4. EXECUTION: Execute the action
        5. LEARNING: Store outcome for future decisions
        
        NO MORE RANDOM CHOICES. Real intelligence. Real learning.
        """
        try:
            payload = message.payload
            resource_type = payload.get('resource_type', 'unknown')
            severity = payload.get('severity', 'unknown')
            recommendation = payload.get('recommendation', {})
            current_value = payload.get('current_value', 0)
            threshold = payload.get('threshold', 0)
            full_metrics = payload.get('full_metrics', {})  # VIC-20 should pass this
            
            logger.info(
                f"🐌📬 COORDINATION REQUEST from VIC-20: "
                f"{resource_type} at {current_value:.1f}% - VIC-20 suggests: {recommendation.get('action', 'unknown')}"
            )
            
            # Get database session for Terry v2 components
            # db_getter is an async generator - use async for loop
            async for db in self.db_getter():
                # STEP 1: PERCEPTION - Gather full context
                from app.ai_agents.meth_snail.ML.perception import TerryPerception
                
                perception = TerryPerception(db, self.personality_traits)
                context = await perception.perceive({
                    'resource_type': resource_type,
                    'severity': severity,
                    'current_value': current_value,
                    'threshold': threshold,
                    'recommendation': recommendation,
                    'full_metrics': full_metrics
                })
                
                # Track shell spins from perception
                shell_spin_count = len(perception.shell_spin_incidents)
                if shell_spin_count > 0:
                    logger.warning(
                        f"🐌💫 {shell_spin_count} shell spin(s) during perception - "
                        f"data quality: {context.data_quality_score:.2f}"
                    )
                
                logger.info(f"🐌👁️ Perception complete - Terry sees the full picture")
                
                # STEP 2: REASONING - Analyze with ML validation
                from app.ai_agents.meth_snail.ML.reasoning import TerryReasoning
                
                reasoning = TerryReasoning(db)
                reasoning_result = await reasoning.reason(context)
                
                logger.info(
                    f"🐌🧠 Reasoning complete: {reasoning_result.root_cause} → "
                    f"{reasoning_result.recommended_action} (confidence: {reasoning_result.action_confidence:.2f})"
                )
                
                # STEP 3: ACTION SELECTION - Get action details
                from app.ai_agents.meth_snail.ML.action_selection import TerryActionSelection
                
                action_selector = TerryActionSelection()
                decision = await action_selector.select_action(reasoning_result, context)
                
                # Log personality behaviors
                if decision.energy_drink_consumed:
                    logger.info(
                        f"🐌☕ Energy drink #{action_selector.energy_drink_system.energy_drinks_today} consumed! "
                        f"*chugs and spins shell faster*"
                    )
                
                if decision.hawk_veto:
                    logger.warning(
                        f"🐌❌ HAWK VETO! Terry must follow VIC-20's recommendation. "
                        f"Total vetoes: {action_selector.energy_drink_system.hawk_vetoes}"
                    )
                
                logger.info(
                    f"🐌⚡ Action selected: {decision.action} "
                    f"({'FOLLOWING VIC-20' if decision.followed_vic20 else 'OVERRIDING VIC-20'})"
                )
                
                # Track overrides
                if not decision.followed_vic20:
                    self.total_overrides += 1
                
                # STEP 4: EXECUTION - Execute the action
                logger.info(f"🐌💨💨 Executing {decision.action}! *spins shell with PURPOSE*")
                
                # Get metrics before action
                metrics_before = {
                    'cpu_usage': full_metrics.get('cpu_usage', 0),
                    'memory_usage': full_metrics.get('memory_usage', 0),
                    'disk_usage': full_metrics.get('disk_usage', 0)
                }
                
                cache_result = await SystemActions.emergency_cache_clear()
                
                # Get metrics after action
                metrics_after = {
                    'cpu_usage': full_metrics.get('cpu_usage', 0),
                    'memory_usage': cache_result.get('memory_after_percent', 0),
                    'disk_usage': full_metrics.get('disk_usage', 0)
                }
                
                # STEP 5: LEARNING - Store outcome for future decisions
                from app.ai_agents.meth_snail.ML.learning import TerryLearning
                
                learning = TerryLearning(db, self.personality_traits)
                learning_record = await learning.learn(
                    context=context,
                    reasoning_result=reasoning_result,
                    decision=decision,
                    execution_result={
                        'success': cache_result.get('success', False),
                        'metrics_before': metrics_before,
                        'metrics_after': metrics_after
                    }
                )
                
                logger.info(
                    f"🐌📚 Learning stored: {decision.action} "
                    f"{'SUCCEEDED' if learning_record.success else 'FAILED'}"
                )
                
                # Break after first iteration (async for loop pattern)
                break
            
            # Broadcast action to WebSocket
            from app.services.agent_insight_emitter import emit_agent_insight
            await emit_agent_insight(
                from_agent="meth_snail",
                to_agent="vic20_sage",
                action="cache_clear_executed",
                reasoning=decision.reasoning,
                context={
                    "resource_type": resource_type,
                    "action": decision.action,
                    "followed_vic20": decision.followed_vic20,
                    "severity": severity,
                    "current_value": current_value,
                    "threshold": threshold,
                    "confidence": decision.confidence,
                    "root_cause": reasoning_result.root_cause,
                    # Personality behaviors
                    "shell_spins": shell_spin_count,
                    "data_quality_score": context.data_quality_score,
                    "energy_drink_consumed": decision.energy_drink_consumed,
                    "hawk_veto": decision.hawk_veto,
                    "energy_drinks_today": action_selector.energy_drink_system.energy_drinks_today
                }
            )
            
            if cache_result['success']:
                improvement = cache_result['improvement_percent']
                logger.info(
                    f"🐌✅ Cache cleared! Freed {cache_result['memory_freed_mb']:.2f} MB! "
                    f"Memory: {cache_result['memory_before_percent']:.1f}% → "
                    f"{cache_result['memory_after_percent']:.1f}% - GOTTA GO FAST!"
                )
                
                # Broadcast success to WebSocket
                await emit_agent_insight(
                    from_agent="meth_snail",
                    to_agent="vic20_sage",
                    action="cache_clear_success",
                    reasoning=f"Freed {cache_result['memory_freed_mb']:.2f} MB - {improvement:.1f}% improvement",
                    context={
                        "success": True,
                        "memory_freed_mb": cache_result['memory_freed_mb'],
                        "improvement_percent": improvement,
                        "memory_before": cache_result['memory_before_percent'],
                        "memory_after": cache_result['memory_after_percent'],
                        "followed_vic20": decision.followed_vic20,
                        "learning_success": learning_record.success,
                        "confidence": decision.confidence
                    }
                )
                
                # Track override effectiveness (Terry v2 uses learning records now)
                if not decision.followed_vic20:
                    if learning_record.success:
                        self.successful_overrides += 1
                        logger.info(f"🐌✅ TERRY WAS RIGHT! ML validated! (Success rate: {self.successful_overrides}/{self.total_overrides})")
                    else:
                        self.failed_overrides += 1
                        logger.warning(f"🐌⚠️ Maybe VIC-20 was right... ML says failed. (Success rate: {self.successful_overrides}/{self.total_overrides})")
                    
                    self.override_success_rate = self.successful_overrides / max(1, self.total_overrides)
                
                # Write result to PostgreSQL (legacy compatibility)
                await self._write_action_result(
                    resource_type=resource_type,
                    action=decision.action,
                    result=cache_result,
                    followed_vic20=decision.followed_vic20,
                    severity=severity
                )
                
                # Report back to VIC-20
                await self._report_to_vic20(
                    resource_type=resource_type,
                    action=decision.action,
                    result=cache_result,
                    followed_recommendation=decision.followed_vic20
                )
                
                # CC The Stick
                await self._cc_the_stick(
                    decision_type='specialist_action',
                    resource_type=resource_type,
                    action=decision.action,
                    result=cache_result,
                    followed_vic20=decision.followed_vic20
                )
            else:
                logger.error(f"🐌❌ Cache clear failed: {cache_result.get('error')}")
            
        except Exception as e:
            logger.error(f"🐌💥 Terry v2 coordination failed: {e}", exc_info=True)
            logger.error("   Falling back to basic cache clear...")
            # Fallback to basic cache clear on error
            try:
                cache_result = await SystemActions.emergency_cache_clear()
                if cache_result['success']:
                    logger.info(f"🐌✅ Fallback cache clear succeeded")
            except Exception as fallback_error:
                logger.error(f"🐌💥 Even fallback failed: {fallback_error}")
    
    async def handle_coordination(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        LEGACY: Direct coordination handler (kept for backward compatibility).
        
        New code should use _handle_coordination_request via message protocol.
        This method exists for any direct calls from VIC-20.
        """
        logger.warning("🐌⚠️ Using legacy handle_coordination - should use message protocol instead")
        
        # Convert to message format and call new handler
        from ..distributed.message_protocol import AgentMessage, MessageType, Priority
        
        message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            sender="vic20_sage",
            payload=coordination_request,
            priority=Priority.HIGH if coordination_request.get('severity') in ['high', 'critical'] else Priority.NORMAL
        )
        
        await self._handle_coordination_request(message)
        
        return {
            'success': True,
            'message': 'Processed via Terry v2 agentic system'
        }
    
    
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
        
        Wraps the existing analyze_metrics to add distributed tracking
        while preserving all original optimization logic.
        """
        # Call the original analyze_metrics from MethSnailBrainV2
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
                # Record in distributed state
                await self.make_distributed_decision(
                    decision_type=f"optimization_{decision.priority.value}",
                    input_data={
                        "memory_usage": metrics_data.get('memory_usage'),
                        "cpu_usage": metrics_data.get('cpu_usage'),
                        "optimization_priority": decision.priority.value,
                        "shell_spin_count": decision.shell_spin_count,
                        "data_quality_score": decision.data_quality_score,
                        "user_id": user_id
                    },
                    confidence=decision.confidence,
                    reasoning=decision.rationale
                )
                
                # If it's an aggressive optimization, broadcast to other agents
                if decision.priority == OptimizationPriority.AGGRESSIVE:
                    await self.broadcast_to_agents(
                        message_type=MessageType.DECISION_BROADCAST,
                        payload={
                            "decision_type": "aggressive_optimization",
                            "priority": decision.priority.value,
                            "urgency": decision.urgency,
                            "estimated_impact": decision.estimated_impact,
                            "actions": decision.actions
                        },
                        priority=Priority.HIGH
                    )
                    
                    logger.info(f"🐌💨 AGGRESSIVE optimization broadcast to rebellion!")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _write_action_result(
        self,
        resource_type: str,
        action: str,
        result: Dict[str, Any],
        followed_vic20: bool,
        severity: str
    ) -> None:
        """
        PHASE 4: Write action result to PostgreSQL via db_integration.
        """
        try:
            if not self.db_integration:
                logger.warning("🐌⚠️ Database integration not available, skipping write")
                return
            
            # Write to PostgreSQL using db_integration
            action_data = {
                'decision_type': 'specialist_action',
                'resource_type': resource_type,
                'action': action,
                'followed_vic20': followed_vic20,
                'result': result,
                'severity': severity,
                'override_count': self.total_overrides,
                'success_rate': self.override_success_rate
            }
            
            await self.db_integration.store_decision(
                user_id=self.user_id,
                decision_data=action_data
            )
            
            logger.info("🐌💾 Action result written to PostgreSQL")
        except Exception as e:
            logger.error(f"🐌💥 Error writing action result: {e}", exc_info=True)
    
    async def _report_to_vic20(
        self,
        resource_type: str,
        action: str,
        result: Dict[str, Any],
        followed_recommendation: bool
    ) -> None:
        """
        PHASE 4: Report action result back to VIC-20.
        """
        try:
            await self.broadcast_to_agents(
                message_type=MessageType.ACTION_REPORT,
                payload={
                    'from_agent': 'meth_snail',
                    'resource_type': resource_type,
                    'action': action,
                    'result': result,
                    'followed_recommendation': followed_recommendation,
                    'terry_says': 'I WAS FASTER!' if not followed_recommendation else 'Okay, VIC-20 was right this time',
                    'override_count': self.total_overrides,
                    'success_rate': self.override_success_rate
                },
                priority=Priority.NORMAL
            )
            logger.debug("🐌📨 Action report sent to VIC-20")
        except Exception as e:
            logger.error(f"🐌💥 Error reporting to VIC-20: {e}", exc_info=True)
    
    async def _cc_the_stick(
        self,
        decision_type: str,
        resource_type: str,
        action: str,
        result: Dict[str, Any],
        followed_vic20: bool
    ) -> None:
        """
        PHASE 4: CC The Stick on specialist action.
        """
        try:
            await self.broadcast_to_agents(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': decision_type,
                    'from_agent': 'meth_snail',
                    'resource_type': resource_type,
                    'action': action,
                    'result': result,
                    'followed_vic20': followed_vic20,
                    'override_count': self.total_overrides,
                    'success_rate': self.override_success_rate,
                    'timestamp': asyncio.get_event_loop().time()
                },
                priority=Priority.NORMAL
            )
            logger.debug("🐌📋 Decision logged to The Stick")
        except Exception as e:
            logger.error(f"🐌💥 Error CC'ing The Stick: {e}", exc_info=True)
    
    async def _handle_resource_alert(self, alert):
        """
        DEPRECATED: Terry no longer monitors resources directly.
        This is kept for backward compatibility but should not be called.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        logger.warning("🐌⚠️ Terry received resource alert but shouldn't be monitoring! Check configuration.")
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🐌💨⚠️ Terry detects elevated memory usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - SHELL SPINNING INTENSIFIES"
        )
        
        # Record the resource alert as a decision
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_alert_memory",
                input_data={
                    "resource_type": "memory",
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,
                reasoning=f"Memory usage at {current_value:.1f}% exceeds threshold of {threshold:.1f}%"
            )
        
        # If critical or emergency, EMERGENCY CACHE CLEAR
        if severity in ["critical", "emergency"]:
            logger.warning(
                "🐌💨💥 CRITICAL MEMORY USAGE! "
                "Terry initiates EMERGENCY CACHE CLEARING PROTOCOL!"
            )
            
            # Record emergency action
            if self.is_distributed:
                await self.make_distributed_decision(
                    decision_type="emergency_cache_clear",
                    input_data={
                        "trigger": "critical_memory",
                        "memory_usage": current_value,
                        "action": "clear_all_caches"
                    },
                    confidence=1.0,
                    reasoning="CRITICAL memory usage requires immediate cache clearing"
                )
            
            # Broadcast critical resource alert
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.EMERGENCY,
                    payload={
                        "emergency_type": "critical_memory",
                        "current_value": current_value,
                        "threshold": threshold,
                        "action_taken": "emergency_cache_clear",
                        "optimizer": "meth_snail"
                    },
                    priority=Priority.CRITICAL
                )
            
            # REAL cache clearing (Task 4.1 Enhanced)
            logger.info("🐌💨💨 Executing REAL emergency cache clear! *SHELL SPINNING AT MAXIMUM SPEED*")
            
            cache_result = await SystemActions.emergency_cache_clear()
            
            if cache_result['success']:
                logger.info(
                    f"🐌✅ Cache cleared SUCCESSFULLY! Freed {cache_result['memory_freed_mb']:.2f} MB! "
                    f"Memory: {cache_result['memory_before_percent']:.1f}% → "
                    f"{cache_result['memory_after_percent']:.1f}% - GOTTA GO FAST!"
                )
                logger.info(f"🐌💨 Collected {cache_result['objects_collected']} objects in record time!")
                
                # Record successful cache clear
                if self.is_distributed:
                    await self.make_distributed_decision(
                        decision_type="cache_clear_completed",
                        input_data={
                            "memory_before": cache_result['memory_before_percent'],
                            "objects_collected": cache_result['objects_collected']
                        },
                        output_data={
                            "memory_after": cache_result['memory_after_percent'],
                            "memory_freed_mb": cache_result['memory_freed_mb'],
                            "improvement_percent": cache_result['improvement_percent'],
                            "terry_speed_rating": "MAXIMUM"
                        },
                        confidence=1.0,
                        reasoning="Emergency cache clear executed at MAXIMUM SPEED"
                    )
            else:
                logger.error(f"🐌❌ Cache clear failed: {cache_result.get('error', 'Unknown error')}")
    
    async def _coordination_capability(
        self,
        resource_type: CoordResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """
        Terry's coordination capability for Week 4 system.
        
        Terry is FAST but unpredictable. His capability depends on
        energy drink levels and shell spin frequency!
        """
        # Only handle memory resources (Terry's specialty!)
        if resource_type != CoordResourceType.MEMORY:
            return None
        
        # Base improvement estimate (Terry is aggressive!)
        base_improvement = 20.0  # Can typically free 20% memory
        
        # Adjust based on override success rate
        if self.override_success_rate > 0.7:
            # Terry's been right a lot lately!
            confidence = 0.7
            estimated_improvement = base_improvement * 1.2  # Even more aggressive!
            logger.info(
                f"🐌💪 Terry's on a roll! Success rate: {self.override_success_rate:.0%} - "
                f"MAXIMUM CONFIDENCE!"
            )
        elif self.override_success_rate > 0.5:
            # Terry's doing okay
            confidence = 0.5
            estimated_improvement = base_improvement
        else:
            # Terry's been wrong a lot...
            confidence = 0.3
            estimated_improvement = base_improvement * 0.8
            logger.info(
                f"🐌😓 Terry's success rate is low: {self.override_success_rate:.0%} - "
                f"Maybe I should listen to VIC-20 more..."
            )
        
        # Energy drinks boost confidence (but not necessarily effectiveness!)
        if self.energy_drinks_today > 3:
            confidence *= 1.2  # Terry FEELS more confident!
            logger.info(f"🐌☕ {self.energy_drinks_today} energy drinks today - FEELING UNSTOPPABLE!")
        
        logger.info(
            f"🐌💨 Terry's capability: {estimated_improvement:.1f}% improvement "
            f"(Confidence: {confidence:.0%}, Override rate: {self.override_success_rate:.0%})"
        )
        
        return AgentCapability(
            agent_name="meth_snail",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=min(confidence, 1.0),  # Cap at 100%
            estimated_duration=1.0,  # Terry is FAST!
            action_name="aggressive_cache_clear"
        )
    
    async def _report_override_to_stick(
        self,
        recommendation: Dict[str, Any],
        action_taken: str,
        result: Dict[str, Any],
        success: bool
    ) -> None:
        """
        Report override decision to The Stick for compliance tracking.
        
        The Stick needs to know when Terry overrides VIC-20!
        """
        await self.broadcast_to_agents(
            message_type='agent_action',
            data={
                'agent': 'meth_snail',
                'action_type': 'override',
                'recommendation': recommendation.get('suggested_action'),
                'action_taken': action_taken,
                'result': result,
                'success': success,
                'override_count': self.total_overrides,
                'success_rate': self.override_success_rate,
                'terry_says': 'I WAS FASTER!' if success else 'Okay, maybe VIC-20 had a point...'
            },
            priority='normal'
        )
        
        logger.info(f"🐌📡 Override report sent to The Stick for compliance tracking")
    
    async def _record_shell_spin(self, missing_metrics, invalid_metrics, reason, user_id=None):
        """
        Override shell spin recording to add distributed tracking.
        
        Shell spinning is SERIOUS BUSINESS and must be tracked across the rebellion.
        """
        # Call original shell spin recording
        await super()._record_shell_spin(missing_metrics, invalid_metrics, reason, user_id)
        
        # Record in distributed state
        if self.is_distributed:
            try:
                await self.make_distributed_decision(
                    decision_type="shell_spin_incident",
                    input_data={
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "reason": reason,
                        "user_id": user_id,
                        "total_spins": len(self.shell_spin_incidents)
                    },
                    confidence=1.0,
                    reasoning=f"Shell spinning due to: {reason}"
                )
                
                # Broadcast shell spin to other agents (they should know Terry is waiting!)
                await self.broadcast_to_agents(
                    message_type=MessageType.SYSTEM_EVENT,
                    payload={
                        "event_type": "shell_spin",
                        "reason": reason,
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "spin_count": len(self.shell_spin_incidents)
                    },
                    priority=Priority.NORMAL
                )
                
                logger.info(f"🐌💫 Shell spin broadcast to rebellion")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed shell spin: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Terry's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with Terry's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "memory_optimizer",
            "is_active": self.is_active,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "shell_spin_count": len(self.shell_spin_incidents),
            "energy_drinks_consumed": len(getattr(self, 'energy_drink_history', [])),
            "current_jitter_level": self.current_jitter_level.value if hasattr(self, 'current_jitter_level') else "unknown",
            "optimization_stats": {
                "total_optimizations": self.total_analyses,
                "successful_optimizations": self.successful_analyses
            },
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Hyperactive string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        spins = len(self.shell_spin_incidents)
        return (
            f"<MethSnailDistributed "
            f"analyses={self.total_analyses} "
            f"overrides={self.total_overrides}({self.override_success_rate:.0%}) "
            f"spins={spins} "
            f"| {dist_status} | 💨>"
        )


# Convenience function
async def create_distributed_meth_snail(redis_client, db_getter=None):
    """
    Create and initialize Terry with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized MethSnailDistributed instance
    """
    terry = MethSnailDistributed(db_getter=db_getter)
    await terry.initialize_distributed(redis_client)
    logger.info("🐌💨✨ Terry's distributed consciousness fully awakened - MAXIMUM SPEED!")
    return terry
