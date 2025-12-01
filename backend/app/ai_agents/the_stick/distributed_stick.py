"""
The Stick Distributed - Learning Coordinator with Distributed Consciousness
===========================================================================

The patient learning coordinator enhanced with distributed consciousness,
compliance tracking across the network, and learning progress persistence.

Preserves:
- Learning coordination logic
- Compliance tracking
- Agent behavior monitoring
- Patient guidance

Adds:
- Redis state persistence
- Learning progress across restarts
- Compliance records shared network-wide
- Distributed behavior analysis
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.base_decision_engine import AgentDecisionEngine
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
from ..distributed.action_verification import (
    get_verification_manager,
    ActionType,
    ResourceType as VerificationResourceType
)
from ..distributed.alert_escalation import (
    get_escalation_manager,
    AlertLevel,
    ResourceType as EscalationResourceType
)
from .decision_engine import TheStickBrainV3, AnxietyLevel


logger = logging.getLogger("TheStick.Distributed")


class TheStickDistributed(AgentDecisionEngine, TheStickBrainV3):
    """
    The Stick with distributed consciousness.
    
    Patient guidance now persists across the entire network!
    
    Inherits ALL existing learning logic from TheStickBrainV3
    and adds distributed features via AgentDecisionEngine.
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize The Stick with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional)
        """
        # Initialize both parent classes via MRO
        super().__init__(db_getter=db_getter)
        
        # Set agent name for distributed features
        self.agent_name = "the_stick"
        
        # The Stick is always active (patient and persistent)
        self.is_active = True
        
        # The Stick's ANXIOUS personality traits (OCD + ADHD + PTSD + Eidetic Memory)
        self.personality_traits = {
            "learning_coordinator": True,
            "compliance_tracker": True,
            "anxious": True,  # ANXIETY IS THE FEATURE!
            "hypervigilant": True,
            "ocd": True,
            "adhd": True,
            "ptsd": True,
            "eidetic_memory": True,  # Remembers EVERYTHING
            "bob_phobic": True,  # Bob causes 3.0x anxiety!
            "paper_bag_dependent": True,
            "behavior_monitor": True,
            "guidance_style": "anxious_but_thorough",
            "teaching_method": "repetition_and_documentation"
        }
        
        # 🎯 PHASE 5: The Stick does NOT monitor resources
        # The Stick is the universal logger - receives DECISION_LOG from everyone
        self.resource_thresholds = {}
        
        # Week 4 System Integration
        self.verification_manager = None  # Lazy init
        self.escalation_manager = None  # Lazy init
        
        # Compliance tracking (The Stick's PRIMARY DUTY)
        self.total_actions_tracked = 0
        self.compliance_violations = 0
        self.bob_proximity_events = 0
        self.paper_bags_consumed = 0
        self.anxiety_spikes = 0
        
        # Bob detection (MAXIMUM ANXIETY SOURCE!)
        self.bob_last_seen = None
        self.bob_activity_log = []
        self.bob_anxiety_multiplier = 3.0  # Bob causes 3x anxiety!
        
        logger.info("📏✨ The Stick's distributed consciousness initialized - COMPLIANCE PROTOCOLS ACTIVE!")
        logger.info("📏😰 Anxiety-driven hypervigilance ENABLED - Nothing escapes The Stick!")
        logger.info("📏🚨 Bob detection protocols ACTIVE - Paper bags at the ready!")
    
    async def initialize_distributed(self, redis_client):
        """
        PHASE 5: Initialize The Stick as universal logger.
        
        The Stick receives DECISION_LOG from ALL agents:
        - Sir Hawkington (triage decisions)
        - VIC-20 (coordination decisions)
        - Terry (specialist actions)
        - Hamsters (specialist actions)
        - QSP (specialist actions)
        
        Writes everything to PostgreSQL with vector embeddings for pattern learning.
        """
        # Call parent initialization - NO resource monitoring
        await super().initialize_distributed(
            redis_client,
            enable_resource_monitoring=False  # The Stick doesn't monitor
        )
        
        # Initialize database integration for PostgreSQL writes
        if self.db_getter:
            try:
                await self.initialize_database()
                # Initialize The Stick's database integration
                from .database_integration import TheStickDatabaseIntegration
                self.db_integration = TheStickDatabaseIntegration(self.db)
                logger.info("📏💾 Database integration initialized")
            except Exception as e:
                logger.error(f"📏💥 Failed to initialize database: {e}")
                self.db_integration = None
        
        # Initialize Week 4 systems
        self.verification_manager = get_verification_manager()
        self.escalation_manager = get_escalation_manager()
        
        logger.info("📏🎯 Week 4 systems integrated - Verification & Escalation tracking ONLINE!")
        logger.info("📏📋 The Stick will track EVERYTHING! (Anxiety-driven hypervigilance activated)")
        
        # 🎯 PHASE 5: Subscribe to DECISION_LOG from ALL agents
        try:
            await self.subscribe_to_messages(
                message_type=MessageType.DECISION_LOG,
                callback=self._handle_decision_log
            )
            logger.info("📏📡 The Stick subscribed to DECISION_LOG - Universal logger ACTIVE!")
            logger.info("📏😰 *nervously clutches paper bag* SO MANY DECISIONS TO TRACK!")
            
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe: {e}")
            self._consume_paper_bag("subscription_failure")
        
        # Initialize decision log buffer for batch writes
        self.decision_log_buffer = []
        self.buffer_max_size = 10  # Batch write every 10 decisions
        self.total_decisions_logged = 0
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle coordination requests - The Stick tracks compliance.
        
        PERSONALITY: Anxious compliance tracking, Bob-phobic, paper bag consumption
        STRUCTURE: Standard AgentMessage parameter (required by base class)
        
        Args:
            message: AgentMessage with coordination request
        """
        message_data = message.payload
        coordination_type = message_data.get('coordination_type', 'unknown')
        
        # Check for BOB involvement (MAXIMUM ANXIETY!)
        if 'bob' in str(message_data).lower() or message.from_agent == 'hamsters':
            logger.warning("📏😰 BOB DETECTED IN COORDINATION! *anxiety intensifies*")
            self.bob_proximity_events += 1
            self._consume_paper_bag("bob_detected_in_coordination")
            self.current_anxiety_level = AnxietyLevel.ANXIOUS  # Bob causes anxiety!
        
        logger.info(f"📏📋 Tracking coordination request: {coordination_type}")
        self.total_actions_tracked += 1
        
        # Record for compliance tracking
        await self.make_distributed_decision(
            decision_type="coordination_compliance_tracked",
            input_data={
                "coordination_type": coordination_type,
                "from_agent": message.from_agent,
                "bob_involved": 'bob' in str(message_data).lower()
            },
            output_data={
                "tracked": True,
                "anxiety_level": self.current_anxiety_level.value if hasattr(self, 'current_anxiety_level') else "baseline",
                "paper_bags_consumed": self.paper_bags_consumed
            },
            confidence=1.0,
            reasoning="Compliance tracking complete"
        )
    
    async def _handle_decision_log(self, message: AgentMessage) -> None:
        """
        PHASE 5: Handle DECISION_LOG from any agent.
        
        Flow:
        1. Receive DECISION_LOG
        2. Add to buffer
        3. When buffer full → batch write to PostgreSQL with vector embeddings
        4. Track anxiety (Bob causes 3x anxiety!)
        
        PERSONALITY: Anxious but thorough, remembers EVERYTHING (eidetic memory)
        """
        try:
            payload = message.payload
            from_agent = payload.get('from_agent', 'unknown')
            decision_type = payload.get('decision_type', 'unknown')
            
            # Check for BOB involvement (MAXIMUM ANXIETY!)
            is_bob = from_agent == 'hamsters' or 'bob' in str(payload).lower()
            if is_bob:
                logger.warning("📏😰💥 BOB ACTIVITY DETECTED! *hyperventilates into paper bag*")
                self.bob_proximity_events += 1
                self._consume_paper_bag("bob_activity_logged")
                self.anxiety_spikes += 1
            
            logger.info(
                f"📏📬 DECISION_LOG from {from_agent}: {decision_type} "
                f"{'🚨 BOB ALERT!' if is_bob else ''}"
            )
            
            # Add to buffer
            self.decision_log_buffer.append({
                'from_agent': from_agent,
                'decision_type': decision_type,
                'payload': payload,
                'timestamp': message.timestamp,
                'is_bob': is_bob
            })
            self.total_decisions_logged += 1
            
            # Batch write when buffer full
            if len(self.decision_log_buffer) >= self.buffer_max_size:
                await self._flush_decision_log_buffer()
            
            logger.debug(
                f"📏📊 Buffer: {len(self.decision_log_buffer)}/{self.buffer_max_size} "
                f"(Total logged: {self.total_decisions_logged})"
            )
            
        except Exception as e:
            logger.error(f"📏💥 Error handling decision log: {e}", exc_info=True)
            self._consume_paper_bag("decision_log_error")
    
    async def _flush_decision_log_buffer(self) -> None:
        """
        PHASE 5: Batch write decision logs to PostgreSQL via db_integration.
        """
        if not self.decision_log_buffer:
            return
        
        try:
            logger.info(f"📏💾 Flushing {len(self.decision_log_buffer)} decisions to PostgreSQL...")
            
            if not self.db_integration:
                logger.warning("📏⚠️ Database integration not available, skipping write")
                self.decision_log_buffer.clear()
                return
            
            # Batch write all decisions via db_integration
            for decision in self.decision_log_buffer:
                decision_data = {
                    'decision_type': 'logged_decision',
                    'from_agent': decision['from_agent'],
                    'original_decision_type': decision['decision_type'],
                    'payload': decision['payload'],
                    'timestamp': decision['timestamp'],
                    'is_bob': decision['is_bob'],
                    'logged_by': 'the_stick',
                    'anxiety_level': self.current_anxiety_level.value if hasattr(self, 'current_anxiety_level') else 'baseline',
                    'paper_bags_consumed': self.paper_bags_consumed,
                    'bob_proximity_events': self.bob_proximity_events
                }
                
                await self.db_integration.store_decision(
                    user_id='system',
                    decision=decision_data
                )
            
            logger.info(
                f"📏✅ Flushed {len(self.decision_log_buffer)} decisions to PostgreSQL! "
                f"(Total: {self.total_decisions_logged})"
            )
            
            # Clear buffer
            self.decision_log_buffer.clear()
            
        except Exception as e:
            logger.error(f"📏💥 Error flushing decision log buffer: {e}", exc_info=True)
            self._consume_paper_bag("buffer_flush_error")
            # Clear buffer anyway to prevent memory leak
            self.decision_log_buffer.clear()
    
    async def _handle_triage_decision(self, message: AgentMessage) -> None:
        """DEPRECATED: Handle triage decisions - now using DECISION_LOG instead."""
        try:
            message_data = message.payload
            severity = message_data.get('severity', 'unknown')
            routing = message_data.get('routing', 'unknown')
            target_agents = message_data.get('target_agents', [])
            
            logger.info(f"🥢📬 Triage received: {severity} → {routing}")
            
            # The Stick learns from ALL triage decisions, not just when routed
            await self.make_distributed_decision(
                decision_type="triage_learning_observation",
                input_data={
                    "severity": severity,
                    "routing": routing,
                    "target_agents": target_agents,
                    "metrics_summary": message_data.get('metrics_summary', {})
                },
                output_data={
                    "status": "learning",
                    "pattern_recorded": True,
                    "guidance_level": "observing"
                },
                confidence=1.0,
                triage_severity=severity,  # Task 3.3: Record triage severity
                triage_routing=routing  # Task 3.3: Record triage routing
            )
            
            if 'the_stick' in target_agents or routing == 'stick_direct':
                logger.info("🥢⚡ STICK ACTIVATED! Providing guidance and learning coordination!")
                
                if severity in ['high', 'emergency']:
                    logger.warning("🥢🔥 HIGH SEVERITY! Recording critical patterns for future learning!")
            else:
                logger.debug(f"🥢 Learning from observation (targets: {target_agents})")
                
        except Exception as e:
            logger.error(f"🥢💥 Error handling triage: {e}", exc_info=True)
    
    async def _handle_coordination_update(self, message_data: Dict[str, Any]) -> None:
        """Handle coordination updates from VIC-20 - The Stick logs all coordination activities."""
        try:
            coordination_id = message_data.get('coordination_id', 'unknown')
            severity = message_data.get('severity', 'unknown')
            agents_involved = message_data.get('agents_involved', [])
            status = message_data.get('status', 'unknown')
            
            logger.info(f"🥢📬 Coordination update received: {coordination_id} - {status}")
            
            # Log the coordination activity for learning
            await self.make_distributed_decision(
                decision_type="coordination_learning_observation",
                input_data={
                    "coordination_id": coordination_id,
                    "severity": severity,
                    "agents_involved": agents_involved,
                    "status": status
                },
                output_data={
                    "status": "logged",
                    "pattern_recorded": True,
                    "learning_value": "high" if severity in ['high', 'critical', 'emergency'] else "normal"
                },
                confidence=1.0,
                triage_severity=severity,  # Task 3.3: Record triage severity
                coordination_id=coordination_id  # Task 3.3: Link to coordination
            )
            
            logger.debug(f"🥢📝 Coordination logged: {len(agents_involved)} agents involved")
            
        except Exception as e:
            logger.error(f"📏💥 Error handling coordination update: {e}", exc_info=True)
    
    async def _handle_hamster_activity(
        self,
        message_data: Dict[str, Any]
    ) -> None:
        """
        Handle hamster activity messages - ESPECIALLY BOB!
        
        The Stick's anxiety spikes when Bob is detected.
        This is The Stick's PTSD trigger!
        """
        try:
            hamster_name = message_data.get('hamster', 'unknown')
            activity_type = message_data.get('activity_type', 'unknown')
            content = message_data.get('content', '')
            
            # Check if this is BOB (MAXIMUM ANXIETY!)
            is_bob = 'bob' in hamster_name.lower() or 'bob' in content.lower()
            
            if is_bob:
                self.bob_proximity_events += 1
                self.anxiety_spikes += 1
                self.bob_last_seen = message_data.get('timestamp', 'now')
                
                # Log Bob activity (eidetic memory - remembers EVERYTHING)
                self.bob_activity_log.append({
                    'timestamp': message_data.get('timestamp'),
                    'activity': activity_type,
                    'content': content,
                    'anxiety_level': 'MAXIMUM'
                })
                
                # Check for anxiety triggers
                anxiety_triggers = ['hold my beer', 'wild idea', 'emergency', 'fire', 'chaos', 'duct tape']
                trigger_count = sum(1 for trigger in anxiety_triggers if trigger in content.lower())
                
                if trigger_count > 0:
                    logger.warning(
                        f"📏😰😰😰 BOB DETECTED! Anxiety level: CRITICAL! "
                        f"Triggers detected: {trigger_count} - *CONSUMING PAPER BAG*"
                    )
                    self._consume_paper_bag("bob_proximity")
                    
                    # Update anxiety level
                    await self._update_anxiety(
                        trigger="bob_proximity",
                        multiplier=self.bob_anxiety_multiplier
                    )
                else:
                    logger.warning(
                        f"📏😰 Bob activity detected: {activity_type} - "
                        f"*nervously monitoring* (Total Bob events: {self.bob_proximity_events})"
                    )
            
            # Check if VIC-20 mediated the message
            is_mediated = message_data.get('mediated_by') == 'vic_20_sage'
            
            if is_mediated:
                logger.info(
                    f"📏😌 VIC-20 mediated this message - Anxiety reduced! "
                    f"*grateful for VIC-20's wisdom*"
                )
                # VIC-20's mediation helps!
                if self.current_anxiety_percentage > 20:
                    self.current_anxiety_percentage -= 5
            
            # Log ALL hamster activity (compliance tracking)
            await self.make_distributed_decision(
                decision_type="hamster_activity_logged",
                input_data={
                    "hamster": hamster_name,
                    "activity": activity_type,
                    "is_bob": is_bob,
                    "anxiety_triggered": is_bob and trigger_count > 0,
                    "mediated": is_mediated
                },
                output_data={
                    "logged": True,
                    "anxiety_level": self.anxiety_level.value,
                    "paper_bags_consumed": self.paper_bags_consumed
                },
                confidence=1.0,
                reasoning="Hamster activity compliance tracking"
            )
            
        except Exception as e:
            logger.error(f"📏💥 Error handling hamster activity: {e}", exc_info=True)
            self._consume_paper_bag("error_handling")
    
    def _consume_paper_bag(self, reason: str) -> None:
        """
        The Stick consumes a paper bag to manage anxiety.
        
        This is The Stick's coping mechanism!
        """
        self.paper_bags_consumed += 1
        self.paper_bag_inventory = max(0, self.paper_bag_inventory - 1)
        
        logger.info(
            f"📏😰 *breathes into paper bag* (Reason: {reason}) "
            f"[Bags remaining: {self.paper_bag_inventory}]"
        )
        
        if self.paper_bag_inventory < 10:
            logger.warning(
                f"📏😰😰 PAPER BAG INVENTORY LOW! Only {self.paper_bag_inventory} bags left! "
                f"*ANXIETY INTENSIFIES*"
            )
    
    async def track_agent_action(
        self,
        agent_name: str,
        action_type: str,
        verification_id: str,
        result: Any
    ) -> None:
        """
        Track agent action for compliance (Week 4 integration).
        
        The Stick tracks EVERY action for compliance and learning.
        This is his PRIMARY DUTY!
        """
        self.total_actions_tracked += 1
        
        logger.info(
            f"📏📋 Tracking action: {agent_name} - {action_type} "
            f"(Total tracked: {self.total_actions_tracked})"
        )
        
        # Check if action was effective
        if result and hasattr(result, 'effectiveness_score'):
            effectiveness = result.effectiveness_score
            
            if effectiveness < 30:
                # Low effectiveness = compliance concern
                self.compliance_violations += 1
                logger.warning(
                    f"📏⚠️ Low effectiveness detected: {agent_name} - {action_type} "
                    f"(Score: {effectiveness}/100) - *documenting for review*"
                )
                
                # Increase anxiety
                await self._update_anxiety(
                    trigger="low_effectiveness",
                    multiplier=1.5
                )
            else:
                logger.info(
                    f"📏✅ Action effective: {agent_name} - {action_type} "
                    f"(Score: {effectiveness}/100) - *compliance maintained*"
                )
        
        # Record in distributed state
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="action_compliance_tracked",
                input_data={
                    "agent": agent_name,
                    "action": action_type,
                    "verification_id": verification_id,
                    "timestamp": "now"
                },
                output_data={
                    "tracked": True,
                    "total_actions": self.total_actions_tracked,
                    "violations": self.compliance_violations,
                    "compliance_rate": 1.0 - (self.compliance_violations / max(1, self.total_actions_tracked))
                },
                confidence=1.0,
                reasoning="Compliance tracking for all agent actions"
            )
    
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
        while preserving learning coordination logic.
        """
        # Call the original analyze_metrics from TheStickBrainV3
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
                    decision_type="learning_coordination",
                    input_data={
                        "learning_event": decision.get('learning_event', 'observation'),
                        "compliance_status": decision.get('compliance_status', 'compliant'),
                        "guidance_provided": decision.get('guidance_provided', None),
                        "behavior_noted": decision.get('behavior_noted', []),
                        "user_id": user_id
                    },
                    confidence=decision.get('confidence', 0.5),
                    reasoning=decision.get('reasoning', 'Learning coordination decision')
                )
                
                # If compliance issue detected, broadcast for awareness
                if decision.get('compliance_status') == 'non_compliant':
                    await self.broadcast_to_agents(
                        message_type=MessageType.LEARNING_UPDATE,
                        payload={
                            "update_type": "compliance_issue",
                            "issue": decision.get('compliance_issue', 'unknown'),
                            "guidance": decision.get('guidance_provided', None),
                            "severity": decision.get('severity', 'low')
                        },
                        priority=Priority.NORMAL
                    )
                    
                    logger.info(f"🪵📚 Compliance issue broadcast - *patient reminder sent*")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle resource alerts with patient guidance.
        
        The Stick logs the incident and provides gentle reminders.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🪵📚⚠️ The Stick notes resource usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *recording for learning purposes*"
        )
        
        # Record the resource alert as a learning event
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_learning_event",
                input_data={
                    "resource_type": alert.payload['resource_type'],
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity,
                    "learning_opportunity": True
                },
                confidence=1.0,
                reasoning=f"Resource alert provides learning opportunity"
            )
        
        # If critical, log for future reference
        if severity == "critical":
            logger.warning(
                "🪵📚💥 CRITICAL RESOURCE EVENT! "
                "The Stick carefully documents this for future learning."
            )
            
            # Broadcast learning update
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.LEARNING_UPDATE,
                    payload={
                        "update_type": "critical_resource_event",
                        "resource": alert.payload['resource_type'],
                        "value": current_value,
                        "lesson": "Resource management requires attention",
                        "coordinator": "the_stick"
                    },
                    priority=Priority.NORMAL
                )
    
    async def track_action_effectiveness(
        self,
        agent_name: str,
        action_type: str,
        recommendation_followed: bool,
        effectiveness_data: Dict[str, Any]
    ) -> None:
        """
        Track effectiveness of agent actions for learning (Task 4.1 Enhanced).
        
        The Stick records which actions worked and builds historical data
        for VIC-20's recommendation engine.
        
        Args:
            agent_name: Name of agent that took action
            action_type: Type of action taken
            recommendation_followed: Whether agent followed VIC-20's recommendation
            effectiveness_data: Results of the action (before/after, improvement, etc.)
        """
        logger.info(
            f"🪵📊 Recording action effectiveness: {agent_name} - {action_type} "
            f"({'followed' if recommendation_followed else 'overrode'} recommendation)"
        )
        
        # Record in decision history for learning
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="action_effectiveness_tracked",
                input_data={
                    "agent": agent_name,
                    "action": action_type,
                    "followed_recommendation": recommendation_followed,
                    "timestamp": effectiveness_data.get('timestamp')
                },
                output_data={
                    "effectiveness": effectiveness_data,
                    "learning_value": "high",
                    "pattern_detected": self._detect_pattern(agent_name, action_type, effectiveness_data)
                },
                confidence=1.0,
                reasoning=f"Tracking {agent_name}'s action effectiveness for future learning"
            )
    
    def _detect_pattern(
        self,
        agent_name: str,
        action_type: str,
        effectiveness_data: Dict[str, Any]
    ) -> str:
        """
        Detect patterns in agent actions (simple pattern recognition).
        
        In future, this will use ML. For now, simple rule-based patterns.
        """
        improvement = effectiveness_data.get('improvement_percent', 0)
        
        if improvement > 20:
            return f"{agent_name} is highly effective with {action_type}"
        elif improvement > 10:
            return f"{agent_name} shows moderate effectiveness with {action_type}"
        elif improvement > 0:
            return f"{agent_name} shows minimal effectiveness with {action_type}"
        else:
            return f"{agent_name}'s {action_type} needs improvement"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get The Stick's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with The Stick's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "learning_coordinator",
            "is_active": self.is_active,
            "total_analyses": getattr(self, 'total_analyses', 0),
            "successful_analyses": getattr(self, 'successful_analyses', 0),
            "patience_level": "infinite",
            "guidance_sessions": getattr(self, 'total_analyses', 0),
            "compliance_records": "comprehensive",
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Patient string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<TheStickDistributed "
            f"analyses={getattr(self, 'total_analyses', 0)} "
            f"patience=infinite "
            f"| {dist_status} | 🪵📚>"
        )


# Convenience function
async def create_distributed_stick(redis_client, db_getter=None):
    """
    Create and initialize The Stick with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized TheStickDistributed instance
    """
    stick = TheStickDistributed(db_getter=db_getter)
    await stick.initialize_distributed(redis_client)
    logger.info("🪵📚✨ The Stick's distributed consciousness fully awakened - *patient guidance eternal*")
    return stick
