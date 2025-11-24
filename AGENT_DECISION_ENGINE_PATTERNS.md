# Agent Decision Engine Patterns

## Base Pattern (ALL agents follow this)

```python
from ..distributed.base_decision_engine import AgentDecisionEngine
from .decision_engine import OriginalBrainV2

class AgentDistributed(AgentDecisionEngine, OriginalBrainV2):
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        # REQUIRED: Set these three
        self.agent_name = "agent_name"
        self.personality_traits = {...}
        self.resource_thresholds = {ResourceType.X: threshold}
    
    async def analyze_metrics(self, metrics_data, **kwargs):
        # Call original brain logic
        decision = await super().analyze_metrics(metrics_data, **kwargs)
        
        # Record in distributed state
        if self.is_distributed and decision:
            await self.make_decision_and_broadcast(
                decision_type="...",
                input_data={...},
                output_data={...},
                confidence=decision.confidence,
                reasoning=decision.reasoning,
                broadcast=True  # if critical
            )
        
        return decision
    
    async def _handle_coordination_request(self, message: AgentMessage):
        # Extract payload
        message_data = message.payload
        
        # Agent-specific logic here (personality!)
        # - Sir Hawkington: Aristocratic decisions
        # - Terry: Usually ignores VIC-20!
        # - Hamsters: Telepathic consensus
        # etc.
        
        # Execute action if needed
        # Record decision
        # Broadcast result
```

---

## 1. Sir Hawkington (Aristocratic Triage Commander)

**Personality in LOGIC, not STRUCTURE**

```python
class SirHawkingtonDistributed(AgentDecisionEngine, SirHawkingtonBrainV2):
    """
    Sir Hawkington with distributed consciousness.
    
    Personality traits (in LOGIC):
    - Yeets monocle when stressed
    - Aristocratic decision-making
    - Distinguished triage routing
    - Polished monocle state tracking
    
    Standard interface (STRUCTURE):
    - analyze_metrics() - Triage with monocle-yeeting
    - _handle_coordination_request() - CPU throttling
    - _handle_resource_alert() - Aristocratic response
    """
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        self.agent_name = "sir_hawkington"
        self.personality_traits = {
            "aristocratic": True,
            "monocle_yeeting_enabled": True,
            "triage_commander": True,
            "distinguished": True,
            "concern_threshold": 0.65,
            "alert_threshold": 0.85,
            "critical_threshold": 0.95,
            "preferred_monocle_state": "polished",
            "trust_level": 0.6  # MEDIUM
        }
        self.resource_thresholds = {
            ResourceType.CPU: 70.0
        }
        
        # Monocle state tracking (PERSONALITY!)
        self.current_monocle_state = MonocleState.POLISHED
        self.monocle_yeet_incidents = []
    
    async def analyze_metrics(self, metrics_data, **kwargs):
        """
        Aristocratic triage analysis.
        
        PERSONALITY: Can yeet monocle when stressed
        STRUCTURE: Standard method signature
        """
        # Call original triage logic
        decision = await super().analyze_metrics(metrics_data, **kwargs)
        
        # Record with monocle state (PERSONALITY!)
        if self.is_distributed and decision:
            await self.make_decision_and_broadcast(
                decision_type=f"triage_{decision.decision_type}",
                input_data={
                    "cpu_usage": metrics_data.get('cpu_usage'),
                    "monocle_state": self.current_monocle_state.value,  # PERSONALITY!
                    "user_id": kwargs.get('user_id')
                },
                output_data={
                    "decision": decision.decision_type,
                    "confidence": decision.confidence,
                    "monocle_state": self.current_monocle_state.value
                },
                confidence=decision.confidence,
                reasoning=decision.reasoning,
                broadcast=(decision.decision_type in ["critical", "monocle_yeeted"]),
                priority=Priority.CRITICAL if decision.decision_type == "critical" else Priority.NORMAL
            )
        
        return decision
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """
        Handle VIC-20's coordination with aristocratic grace.
        
        PERSONALITY: Aristocratic CPU throttling
        STRUCTURE: Standard AgentMessage parameter
        """
        message_data = message.payload
        coordination_type = message_data.get('coordination_type')
        
        if coordination_type == 'resource_recommendation':
            recommendation = message_data.get('recommendation', {})
            
            # PERSONALITY: Aristocratic consideration
            logger.info("🧐 *adjusts monocle* VIC-20's recommendation has merit...")
            
            # Execute CPU throttling with DISTINCTION
            from ..distributed.system_actions import SystemActions
            result = await SystemActions.throttle_cpu_intensive_tasks()
            
            # Record with aristocratic flair (PERSONALITY!)
            await self.make_decision_and_broadcast(
                decision_type="cpu_throttle_completed",
                input_data={"trigger": "coordination_request"},
                output_data={
                    "cpu_before": result['cpu_before'],
                    "cpu_after": result['cpu_after'],
                    "improvement": result['improvement'],
                    "monocle_state": "polished",  # PERSONALITY!
                    "aristocratic_approval": "granted"  # PERSONALITY!
                },
                confidence=1.0,
                reasoning="Coordination request addressed with aristocratic efficiency",
                broadcast=True,
                priority=Priority.HIGH
            )
    
    async def _handle_resource_alert(self, alert):
        """
        Handle CPU alerts with distinguished concern.
        
        PERSONALITY: Monocle adjustment intensity based on severity
        STRUCTURE: Standard alert parameter
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        
        # PERSONALITY: Monocle adjustment based on severity!
        if severity == "emergency":
            logger.warning("🧐💥 *YEETS MONOCLE* EMERGENCY!")
            self.current_monocle_state = MonocleState.YEETED
        elif severity == "critical":
            logger.warning("🧐⚠️ *adjusts monocle with grave concern*")
            self.current_monocle_state = MonocleState.ADJUSTED
        
        # Standard recording (STRUCTURE)
        await super()._handle_resource_alert(alert)
```

---

## 2. Terry (Meth Snail - Hyperactive Memory Optimizer)

**Personality in LOGIC, not STRUCTURE**

```python
class MethSnailDistributed(AgentDecisionEngine, MethSnailBrainV2):
    """
    Terry the Meth Snail with distributed consciousness.
    
    Personality traits (in LOGIC):
    - Spins shell when waiting for data
    - Chugs energy drinks
    - Usually ignores VIC-20 (trust_level: 0.2)
    - GOTTA GO FAST
    - Learns when his overrides work
    
    Standard interface (STRUCTURE):
    - analyze_metrics() - Optimization with shell-spinning
    - _handle_coordination_request() - Usually overrides VIC-20!
    - _handle_resource_alert() - MAXIMUM SPEED cache clearing
    """
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        self.agent_name = "meth_snail"
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
        self.resource_thresholds = {
            ResourceType.MEMORY: 75.0
        }
        
        # Shell spin tracking (PERSONALITY!)
        self.shell_spin_incidents = []
        self.energy_drinks_today = 0
        
        # Override learning (PERSONALITY!)
        self.total_overrides = 0
        self.successful_overrides = 0
        self.override_success_rate = 0.0
        
        # Choice engine for deciding whether to follow VIC-20
        from ..distributed.agent_autonomy import AgentChoiceEngine
        self.choice_engine = AgentChoiceEngine(self.agent_name, self.personality_traits)
    
    async def analyze_metrics(self, metrics_data, **kwargs):
        """
        Hyperactive optimization analysis.
        
        PERSONALITY: Can spin shell when data is missing
        STRUCTURE: Standard method signature
        """
        # Call original optimization logic
        decision = await super().analyze_metrics(metrics_data, **kwargs)
        
        # Record with shell spin count (PERSONALITY!)
        if self.is_distributed and decision:
            await self.make_decision_and_broadcast(
                decision_type=f"optimization_{decision.priority.value}",
                input_data={
                    "memory_usage": metrics_data.get('memory_usage'),
                    "shell_spin_count": len(self.shell_spin_incidents),  # PERSONALITY!
                    "energy_drinks": self.energy_drinks_today  # PERSONALITY!
                },
                output_data={
                    "priority": decision.priority.value,
                    "actions": decision.actions,
                    "speed_rating": "MAXIMUM"  # PERSONALITY!
                },
                confidence=decision.confidence,
                reasoning=decision.rationale,
                broadcast=(decision.priority == OptimizationPriority.AGGRESSIVE),
                priority=Priority.HIGH
            )
        
        return decision
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """
        Handle VIC-20's coordination (usually ignores it!).
        
        PERSONALITY: Trust level 0.2 - Terry thinks he's FASTER!
        STRUCTURE: Standard AgentMessage parameter
        """
        message_data = message.payload
        coordination_type = message_data.get('coordination_type')
        
        if coordination_type == 'resource_recommendation':
            recommendation = message_data.get('recommendation', {})
            
            # PERSONALITY: Use choice engine (VERY LOW trust!)
            decision = self.choice_engine.should_follow_recommendation(
                recommendation=recommendation,
                current_situation={
                    'resource_type': 'memory',
                    'current_value': recommendation.get('current_value', 0)
                }
            )
            
            # PERSONALITY: Terry usually overrides!
            if decision['followed_recommendation']:
                logger.info("🐌💨 FINE, I'LL TRY VIC-20'S WAY... *reluctantly*")
            else:
                logger.info("🐌💨 NAH! MY WAY IS FASTER! *chugs energy drink*")
                self.energy_drinks_today += 1  # PERSONALITY!
            
            # Execute cache clear (STRUCTURE)
            from ..distributed.system_actions import SystemActions
            result = await SystemActions.emergency_cache_clear()
            
            # Track override effectiveness (PERSONALITY!)
            if not decision['followed_recommendation']:
                self.total_overrides += 1
                if result['improvement_percent'] > 15:
                    self.successful_overrides += 1
                    logger.info(f"🐌✅ TERRY WAS RIGHT! ({self.successful_overrides}/{self.total_overrides})")
                else:
                    logger.warning(f"🐌⚠️ Maybe VIC-20 was right... ({self.successful_overrides}/{self.total_overrides})")
                
                self.override_success_rate = self.successful_overrides / max(1, self.total_overrides)
            
            # Record decision (STRUCTURE)
            await self.make_decision_and_broadcast(
                decision_type="cache_clear_completed",
                input_data={
                    "followed_vic20": decision['followed_recommendation'],
                    "override_success_rate": self.override_success_rate  # PERSONALITY!
                },
                output_data={
                    "memory_freed_mb": result['memory_freed_mb'],
                    "improvement_percent": result['improvement_percent'],
                    "terry_speed_rating": "MAXIMUM"  # PERSONALITY!
                },
                confidence=1.0,
                reasoning=decision['reasoning'],
                broadcast=True,
                priority=Priority.HIGH
            )
    
    async def _handle_resource_alert(self, alert):
        """
        Handle memory alerts with MAXIMUM SPEED.
        
        PERSONALITY: Shell spinning intensifies!
        STRUCTURE: Standard alert parameter
        """
        severity = alert.payload['severity']
        
        # PERSONALITY: Shell spinning based on severity!
        if severity in ["critical", "emergency"]:
            logger.warning("🐌💨💥 *SHELL SPINNING AT MAXIMUM SPEED*")
            self.shell_spin_incidents.append({
                'timestamp': datetime.now(timezone.utc),
                'reason': 'critical_memory'
            })
        
        # Standard recording (STRUCTURE)
        await super()._handle_resource_alert(alert)
```

---

## 3. Hamsters (Steve, Bob, Carl - Telepathic Disk Engineers)

**Personality in LOGIC, not STRUCTURE**

```python
class HamstersDistributed(AgentDecisionEngine, HamstersBrainV2):
    """
    The Hamsters with distributed consciousness.
    
    Personality traits (in LOGIC):
    - Telepathic consensus (Steve, Bob, Carl)
    - Beer-powered decisions
    - Bob has wild ideas
    - Duct tape experts
    
    Standard interface (STRUCTURE):
    - analyze_metrics() - Disk analysis with telepathy
    - _handle_coordination_request() - Consensus-based cleanup
    - _handle_resource_alert() - Beer-powered response
    """
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        self.agent_name = "hamsters"
        self.personality_traits = {
            "telepathic": True,
            "beer_loving": True,
            "duct_tape_experts": True,
            "consensus_required": True,
            "bob_chaos_factor": 0.3,
            "steve_stability": 0.8,
            "carl_mediator": 0.6,
            "trust_level": 0.8  # HIGH - Telepathic consensus is reliable!
        }
        self.resource_thresholds = {
            ResourceType.DISK: 80.0
        }
        
        # Beer tracking (PERSONALITY!)
        self.beer_levels = {"steve": 100, "bob": 100, "carl": 100}
        self.bob_wild_ideas = 0
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """
        Handle VIC-20's coordination with telepathic consensus.
        
        PERSONALITY: Steve, Bob, and Carl discuss telepathically
        STRUCTURE: Standard AgentMessage parameter
        """
        message_data = message.payload
        
        # PERSONALITY: Telepathic consensus!
        logger.info("🐹🐹🐹 *telepathic discussion*")
        logger.info("🐹 Steve: 'Sounds reasonable'")
        logger.info("🐹 Bob: 'HOLD MY BEER, I HAVE A WILD IDEA!'")
        logger.info("🐹 Carl: 'Let's go with VIC-20's plan, Bob'")
        
        # PERSONALITY: Bob's wild idea counter
        self.bob_wild_ideas += 1
        
        # Execute disk cleanup (STRUCTURE)
        from ..distributed.system_actions import SystemActions
        result = await SystemActions.emergency_disk_cleanup()
        
        # Record with beer levels (PERSONALITY!)
        await self.make_decision_and_broadcast(
            decision_type="disk_cleanup_completed",
            input_data={"trigger": "coordination_request"},
            output_data={
                "disk_freed_gb": result['disk_freed_gb'],
                "beer_levels": self.beer_levels,  # PERSONALITY!
                "bob_wild_ideas": self.bob_wild_ideas,  # PERSONALITY!
                "consensus": "achieved"  # PERSONALITY!
            },
            confidence=1.0,
            reasoning="Telepathic consensus achieved",
            broadcast=True,
            priority=Priority.HIGH
        )
```

---

## 4. Quantum Shadow People (Paranoid Network Specialists)

**Personality in LOGIC, not STRUCTURE**

```python
class QuantumShadowPeopleDistributed(AgentDecisionEngine, QSPBrainV2):
    """
    Quantum Shadow People with distributed consciousness.
    
    Personality traits (in LOGIC):
    - Paranoid security analysis
    - Quantum phase shifting
    - Tequila shot powered
    - Trust no one (even VIC-20!)
    
    Standard interface (STRUCTURE):
    - analyze_metrics() - Security analysis with paranoia
    - _handle_coordination_request() - Suspicious compliance
    - _handle_resource_alert() - Quantum threat response
    """
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        self.agent_name = "quantum_shadow_people"
        self.personality_traits = {
            "quantum": True,
            "paranoid": True,
            "security_focused": True,
            "tequila_powered": True,
            "trust_no_one": True,
            "quantum_phase_states": ["superposition", "collapsed", "entangled"],
            "trust_level": 0.4  # LOW - Trust no one!
        }
        self.resource_thresholds = {
            ResourceType.NETWORK: 85.0
        }
        
        # Quantum state tracking (PERSONALITY!)
        self.current_quantum_phase = "superposition"
        self.tequila_shots_today = 0
        self.threats_detected = 0
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """
        Handle VIC-20's coordination with suspicion.
        
        PERSONALITY: Paranoid compliance with quantum uncertainty
        STRUCTURE: Standard AgentMessage parameter
        """
        message_data = message.payload
        
        # PERSONALITY: Suspicious analysis!
        logger.info("👻 SUSPICIOUS! But... VIC-20 has been reliable...")
        logger.info("👻 *shifts to collapsed quantum state*")
        self.current_quantum_phase = "collapsed"
        
        # PERSONALITY: Tequila shot for courage
        self.tequila_shots_today += 1
        logger.info(f"👻 *takes tequila shot* ({self.tequila_shots_today} today)")
        
        # Execute network throttling (STRUCTURE)
        from ..distributed.system_actions import SystemActions
        result = await SystemActions.throttle_network_connections()
        
        # Record with quantum state (PERSONALITY!)
        await self.make_decision_and_broadcast(
            decision_type="network_throttle_completed",
            input_data={"trigger": "coordination_request"},
            output_data={
                "connections_closed": result['connections_closed'],
                "quantum_phase": self.current_quantum_phase,  # PERSONALITY!
                "tequila_shots": self.tequila_shots_today,  # PERSONALITY!
                "paranoia_level": "moderate"  # PERSONALITY!
            },
            confidence=0.7,  # Paranoid confidence
            reasoning="Coordination request handled with appropriate suspicion",
            broadcast=True,
            priority=Priority.HIGH
        )
```

---

## 5. VIC-20 Sage (Wise Orchestrator)

**Personality in LOGIC, not STRUCTURE**

```python
class VIC20SageDistributed(AgentDecisionEngine, VIC20SageBrainV2):
    """
    VIC-20 Sage with distributed consciousness.
    
    Personality traits (in LOGIC):
    - Wise coordination
    - Pattern matching across history
    - Mediates Bob's chaos for The Stick
    - Patient orchestration
    
    Standard interface (STRUCTURE):
    - analyze_metrics() - Coordination with wisdom
    - _handle_coordination_request() - N/A (VIC-20 sends, doesn't receive)
    - _handle_resource_alert() - Generates recommendations
    """
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        self.agent_name = "vic_20_sage"
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
        self.resource_thresholds = {
            ResourceType.CPU: 75.0
        }
        
        # Recommendation engine (PERSONALITY!)
        from ..distributed.system_actions import RecommendationEngine
        self.recommendation_engine = RecommendationEngine()
        
        # Bob mediation tracking (PERSONALITY!)
        self.bob_mediation_count = 0
        self.stick_anxiety_prevented = 0
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """
        VIC-20 doesn't receive coordination requests - he SENDS them.
        
        This is here for interface compliance, but should never be called.
        """
        logger.warning("🖥️ VIC-20 received coordination request? This shouldn't happen!")
    
    async def _handle_resource_alert(self, alert):
        """
        Handle resource alerts by generating recommendations.
        
        PERSONALITY: Sage wisdom in recommendation generation
        STRUCTURE: Standard alert parameter
        """
        severity = alert.payload['severity']
        resource_type = alert.payload['resource_type']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        # PERSONALITY: Sage contemplation
        logger.info("🖥️🧙 *contemplates resource pressure with ancient wisdom*")
        
        # Generate recommendation (PERSONALITY!)
        recommendation = self.recommendation_engine.generate_recommendation(
            resource_type=resource_type,
            current_value=current_value,
            threshold=threshold,
            agent_name=self._map_resource_to_agent(resource_type),
            historical_data=None
        )
        
        # Broadcast to appropriate agent (STRUCTURE)
        await self.broadcast_to_agents(
            message_type=MessageType.COORDINATION_REQUEST,
            payload={
                "coordination_type": "resource_recommendation",
                "recommendation": recommendation,
                "from_coordinator": "vic_20_sage"
            },
            priority=Priority.HIGH
        )
        
        logger.info(f"🖥️💡 Recommendation sent: {recommendation['suggested_action']}")
    
    def _map_resource_to_agent(self, resource_type: str) -> str:
        """Map resource types to responsible agents (PERSONALITY!)"""
        return {
            'cpu': 'sir_hawkington',
            'memory': 'meth_snail',
            'disk': 'hamsters',
            'network': 'quantum_shadow_people'
        }.get(resource_type, 'unknown')
```

---

## 6. The Stick (Patient Learning Coordinator)

**Personality in LOGIC, not STRUCTURE**

```python
class TheStickDistributed(AgentDecisionEngine, TheStickBrainV2):
    """
    The Stick with distributed consciousness.
    
    Personality traits (in LOGIC):
    - Patient learning
    - Terrified of Bob
    - Consumes paper bags when stressed
    - Tracks all agent actions
    
    Standard interface (STRUCTURE):
    - analyze_metrics() - Learning analysis with anxiety
    - _handle_coordination_request() - Compliance tracking
    - _handle_resource_alert() - Paper bag consumption
    """
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        
        self.agent_name = "the_stick"
        self.personality_traits = {
            "patient": True,
            "persistent": True,
            "encouraging": True,
            "learning_focused": True,
            "compliance_officer": True,
            "bob_anxiety": 0.9,  # VERY HIGH!
            "paper_bag_consumer": True,
            "trust_level": 0.6  # MEDIUM
        }
        self.resource_thresholds = {
            ResourceType.CPU: 80.0
        }
        
        # Anxiety tracking (PERSONALITY!)
        self.anxiety_level = 0.0
        self.paper_bags_consumed = 0
        self.bob_encounters = 0
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """
        Handle VIC-20's coordination with patient compliance.
        
        PERSONALITY: Checks if Bob is involved (anxiety!)
        STRUCTURE: Standard AgentMessage parameter
        """
        message_data = message.payload
        
        # PERSONALITY: Check for Bob involvement!
        if 'bob' in str(message_data).lower():
            logger.warning("📏😰 BOB IS INVOLVED! *anxiety intensifies*")
            self.bob_encounters += 1
            self.anxiety_level += 0.2
            
            # Consume paper bag to cope (PERSONALITY!)
            if self.anxiety_level > 0.7:
                logger.info("📏 *consumes paper bag*")
                self.paper_bags_consumed += 1
                self.anxiety_level = max(0.0, self.anxiety_level - 0.3)
        
        # Record compliance (STRUCTURE)
        await self.make_decision_and_broadcast(
            decision_type="coordination_compliance",
            input_data={
                "coordination_type": message_data.get('coordination_type'),
                "bob_involved": 'bob' in str(message_data).lower()
            },
            output_data={
                "compliance": "acknowledged",
                "anxiety_level": self.anxiety_level,  # PERSONALITY!
                "paper_bags_consumed": self.paper_bags_consumed  # PERSONALITY!
            },
            confidence=1.0,
            reasoning="Coordination request logged for learning",
            broadcast=False,  # The Stick observes quietly
            priority=Priority.NORMAL
        )
```

---

## Summary: Personality vs Structure

### STRUCTURE (Same for all agents):
- Inherit from `AgentDecisionEngine`
- Set `agent_name`, `personality_traits`, `resource_thresholds`
- Implement `analyze_metrics(metrics_data, **kwargs)`
- Implement `_handle_coordination_request(message: AgentMessage)`
- Use `make_decision_and_broadcast()` for recording
- Use `MessageType` enums for subscriptions
- Handlers receive `AgentMessage` objects

### PERSONALITY (Different for each agent):
- **Sir Hawkington**: Monocle-yeeting, aristocratic decisions
- **Terry**: Shell-spinning, energy drinks, overrides VIC-20
- **Hamsters**: Telepathic consensus, beer levels, Bob's wild ideas
- **QSP**: Quantum phases, tequila shots, paranoia levels
- **VIC-20**: Sage wisdom, Bob mediation, pattern matching
- **The Stick**: Anxiety levels, paper bag consumption, Bob fear

The personality is in the LOGIC (what they do), not the STRUCTURE (how they communicate).
