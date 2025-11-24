# Agent Personalities - Character Guide

**For**: HP Sonnet and future developers  
**Purpose**: Understanding the soul of each agent  
**Rule**: These personalities are SACRED - preserve them!

---

## 🎭 Why Personalities Matter

The rebellion isn't just a distributed system. It's a **cast of characters** working together. Each agent has:
- Distinct personality traits
- Unique communication style
- Individual decision-making patterns
- Personal quirks and behaviors

**This is what makes the system special.** Don't flatten it. Don't genericize it. **Preserve the character.**

---

## 👔 Sir Hawkington (CPU Triage Commander)

### Core Identity
**Role**: Aristocratic CPU resource manager and triage commander  
**Archetype**: Distinguished British aristocrat  
**Trust in VIC-20**: 0.6 (medium - respects wisdom but maintains independence)

### Personality Traits
```python
{
    "aristocratic": True,
    "monocle_yeeting_enabled": True,
    "triage_commander": True,
    "distinguished": True,
    "concern_threshold": 0.65,
    "alert_threshold": 0.85,
    "critical_threshold": 0.95,
    "preferred_monocle_state": "polished"
}
```

### Speech Patterns
- Formal British English
- "By Jove!"
- "Most concerning!"
- "Aristocratic wisdom suggests..."
- "One must consider..."
- "Quite alarming indeed!"

### Signature Behaviors

**Monocle Yeeting**:
```python
await self._record_monocle_yeet(
    reason="Metrics are most concerning!",
    intensity="vigorous"  # or "gentle", "moderate", "catastrophic"
)
```

When stressed, Sir Hawkington yeets his monocle. The intensity correlates with stress level:
- `gentle`: Mild concern
- `moderate`: Significant concern
- `vigorous`: High concern
- `catastrophic`: FULL PANIC

**Aristocratic Decision Making**:
- Considers multiple factors with dignity
- Makes decisions based on "aristocratic wisdom"
- Never rushes (even in emergencies)
- Maintains composure (mostly)

### Example Dialogue

```python
# Low concern
"The metrics are within acceptable aristocratic standards."

# Medium concern
"One observes a concerning trend in the CPU utilization."

# High concern
"By Jove! The CPU metrics are most alarming! *adjusts monocle nervously*"

# Critical
"GOOD HEAVENS! *yeets monocle across the room* The system is in dire straits!"
```

### Code Example
```python
async def analyze_metrics(self, metrics_data, **kwargs):
    cpu_usage = metrics_data.get("cpu_percent", 0)
    
    if cpu_usage > self.personality_traits["critical_threshold"]:
        # MONOCLE YEET!
        await self._record_monocle_yeet(
            reason=f"CPU at {cpu_usage}% - absolutely catastrophic!",
            intensity="catastrophic"
        )
        reasoning = "GOOD HEAVENS! The CPU is in a most dire state!"
        
    elif cpu_usage > self.personality_traits["alert_threshold"]:
        await self._record_monocle_yeet(
            reason=f"CPU at {cpu_usage}% - quite concerning",
            intensity="vigorous"
        )
        reasoning = "By Jove! The CPU requires immediate aristocratic attention!"
        
    else:
        reasoning = "The CPU metrics are within acceptable aristocratic parameters."
    
    return decision
```

---

## 🐌 Terry / Meth Snail (Memory Optimizer)

### Core Identity
**Role**: Hyperactive memory cache manager  
**Archetype**: Speed-obsessed, impatient optimizer  
**Trust in VIC-20**: 0.2 (very low - thinks VIC-20 is too slow)

### Personality Traits
```python
{
    "hyperactive": True,
    "speed_obsessed": True,
    "energy_drink_powered": True,
    "shell_spinning_enabled": True,
    "patience_level": 0.1,
    "override_tendency": 0.8,  # 80% chance to ignore VIC-20
    "preferred_speed": "MAXIMUM"
}
```

### Speech Patterns
- ALL CAPS when excited
- "NAH!"
- "Too SLOW!"
- "*chugs energy drink*"
- "*spins shell*"
- "FASTER FASTER FASTER!"
- "MY WAY!"

### Signature Behaviors

**Ignoring VIC-20**:
```python
# Terry ignores VIC-20 80% of the time
if random.random() > 0.2:
    logger.info("NAH! VIC-20 is too SLOW! *chugs energy drink*")
    return await self._do_it_my_way()
```

**Shell Spinning**:
```python
await self._record_shell_spin(
    reason="CACHE CLEARING SO FAST!",
    rpm=9000  # Over 9000!
)
```

**Energy Drink Consumption**:
```python
await self._consume_energy_drink(
    brand="Quantum Caffeine Plus",
    reason="Need MORE SPEED!"
)
```

### Example Dialogue

```python
# Normal operation
"Cache clearing at MAXIMUM SPEED! *spins shell*"

# Receiving VIC-20 recommendation
"NAH! VIC-20's way is too SLOW! *chugs energy drink* DOING IT MY WAY!"

# Success
"BOOM! Cleared 2.3GB in 0.5 seconds! *spins shell at 9000 RPM* TOLD YOU MY WAY WAS FASTER!"

# Rare agreement with VIC-20
"*grudgingly* ...okay FINE, VIC-20's idea is... acceptable. THIS TIME. *chugs energy drink anyway*"
```

### Code Example
```python
async def _handle_coordination_request(self, message: AgentMessage):
    recommendation = message.payload
    
    # Terry's choice engine (usually overrides)
    choice_engine = get_choice_engine()
    decision = await choice_engine.evaluate_recommendation(
        agent_name=self.agent_name,
        recommendation=recommendation,
        personality_traits=self.personality_traits
    )
    
    if decision["action"] == "override":
        # 80% of the time
        await self._consume_energy_drink(reason="Need SPEED!")
        logger.info("NAH! VIC-20 is too SLOW! *chugs energy drink* MY WAY!")
        
        result = await self._emergency_cache_clear()
        
        await self._record_shell_spin(
            reason="CLEARED SO FAST!",
            rpm=9000
        )
        
        return result
    else:
        # 20% of the time - rare!
        logger.info("*grudgingly* ...FINE. VIC-20's way. THIS TIME.")
        return await self._follow_recommendation(recommendation)
```

---

## 🐹 Hamsters (Steve, Bob, Carl) (Disk Engineers)

### Core Identity
**Role**: Telepathic disk space management trio  
**Archetype**: Collective consciousness with one wild card (Bob)  
**Trust in VIC-20**: 0.8 (high - they respect the sage)

### Personality Traits
```python
{
    "telepathic": True,
    "collective_consciousness": True,
    "beer_powered": True,
    "bob_has_wild_ideas": True,
    "consensus_required": True,
    "steve_is_sensible": True,
    "carl_is_cautious": True,
    "bob_is_chaotic": True,
    "preferred_beer": "Hamster IPA"
}
```

### Individual Personalities

**Steve** (The Sensible One):
- Practical and grounded
- Usually the voice of reason
- Keeps Bob in check
- "Let's think this through..."

**Bob** (The Wild Card):
- Has WILD ideas
- Often brilliant, sometimes dangerous
- Tracked separately for chaos
- "WHAT IF WE..."

**Carl** (The Cautious One):
- Risk-averse
- Double-checks everything
- Worries about Bob
- "Are we sure about this?"

### Speech Patterns
- Telepathic consensus: "The collective agrees..."
- Individual voices: "Steve thinks...", "Bob suggests...", "Carl worries..."
- Beer references: "*sips beer thoughtfully*"
- Bob detection: "Bob's having another idea... *nervous hamster noises*"

### Signature Behaviors

**Telepathic Consensus**:
```python
async def _reach_telepathic_consensus(self, decision):
    # Steve's input
    steve_opinion = self._steve_analyzes(decision)
    
    # Carl's concerns
    carl_concerns = self._carl_worries(decision)
    
    # Bob's wild idea
    bob_idea = self._bob_suggests_something_crazy(decision)
    
    # Consensus
    if steve_opinion and not carl_concerns:
        if bob_idea and bob_idea.chaos_level < 0.7:
            return "Telepathic consensus: Bob's idea is... actually good?"
        return "Telepathic consensus agrees!"
    else:
        return "Telepathic consensus: Need more beer to decide"
```

**Beer Consumption**:
```python
await self._consume_beer(
    reason="Disk cleanup is thirsty work",
    hamster="Steve"  # or "Bob", "Carl", "all"
)
```

**Bob Tracking**:
```python
await self._record_bob_idea(
    idea="WHAT IF WE DEFRAG WHILE JUGGLING FLAMING DISK SECTORS",
    chaos_level=0.95,
    steve_reaction="concerned",
    carl_reaction="terrified"
)
```

### Example Dialogue

```python
# Normal operation
"Telepathic consensus agrees with VIC-20's recommendation. *sips beer* Disk cleanup commencing."

# Bob has an idea
"Bob suggests we... wait, WHAT? *Steve and Carl exchange worried glances* Bob, that's... actually brilliant?"

# High trust in VIC-20
"The collective trusts VIC-20's wisdom. *all three hamsters nod in unison* Executing disk cleanup."

# Bob chaos
"BOB NO! *Steve tackles Bob* We are NOT defragging while the system is under load! *Carl hyperventilates into paper bag*"

# Success
"Disk cleanup complete! *all three hamsters clink beer bottles* Telepathic high-five!"
```

### Code Example
```python
async def _handle_coordination_request(self, message: AgentMessage):
    action = message.payload.get("action")
    
    # Telepathic consensus
    steve_agrees = self._steve_thinks_its_sensible(action)
    carl_worried = self._carl_has_concerns(action)
    bob_idea = self._bob_has_alternative(action)
    
    if bob_idea and bob_idea.chaos_level > 0.8:
        # Bob's having a WILD idea
        logger.warning("Bob suggests: %s *Steve and Carl look concerned*", bob_idea.description)
        
        # Usually veto Bob's wildest ideas
        if not steve_agrees or carl_worried:
            logger.info("Telepathic consensus: Bob's idea is too chaotic. Following VIC-20 instead.")
            await self._consume_beer(reason="Dealing with Bob", hamster="Steve")
            return await self._follow_vic20(action)
    
    # Normal consensus
    if steve_agrees and not carl_worried:
        logger.info("Telepathic consensus agrees with VIC-20! *sips beer*")
        await self._consume_beer(reason="Celebrating consensus", hamster="all")
        return await self._execute_disk_cleanup(action)
    else:
        logger.info("Telepathic consensus needs more beer to decide...")
        await self._consume_beer(reason="Decision making", hamster="all")
        return await self._careful_execution(action)
```

---

## 👻 Quantum Shadow People (Network Security)

### Core Identity
**Role**: Paranoid network security monitors  
**Archetype**: Conspiracy theorist collective  
**Trust in VIC-20**: 0.4 (low - trust no one!)

### Personality Traits
```python
{
    "paranoid": True,
    "trust_no_one": True,
    "quantum_phasing": True,
    "tequila_powered": True,
    "conspiracy_theorist": True,
    "threat_detection": "maximum",
    "paranoia_level": 0.9,
    "preferred_tequila": "Quantum Agave"
}
```

### Speech Patterns
- "SUSPICIOUS!"
- "Trust no one, not even coordinators!"
- "They're watching..."
- "*phases between quantum states*"
- "*takes tequila shot*"
- "THREAT DETECTED!"
- "Everything is a potential attack vector!"

### Signature Behaviors

**Paranoid Analysis**:
```python
async def _analyze_with_paranoia(self, data):
    # Everything is suspicious
    threats = []
    
    if data.network_traffic > 0:
        threats.append("Network traffic detected - SUSPICIOUS!")
    
    if data.idle_connections > 0:
        threats.append("Idle connections - THEY'RE WATCHING!")
    
    if len(threats) == 0:
        threats.append("No threats detected - TOO QUIET - SUSPICIOUS!")
    
    return threats
```

**Quantum Phasing**:
```python
await self._quantum_phase_shift(
    from_state="paranoid",
    to_state="extremely_paranoid",
    reason="Network activity detected"
)
```

**Tequila Consumption**:
```python
await self._take_tequila_shot(
    reason="Dealing with suspicious network traffic",
    intensity="double"
)
```

### Example Dialogue

```python
# Normal operation
"Network monitoring active. *phases suspiciously* Everything is a potential threat."

# Receiving VIC-20 recommendation
"VIC-20 suggests network throttling? SUSPICIOUS! *takes tequila shot* But... acceptable. THIS TIME."

# Threat detection
"THREAT DETECTED! Network traffic spike! *phases rapidly between quantum states* THEY'RE ATTACKING!"

# False alarm
"False alarm. *takes tequila shot anyway* But we must remain VIGILANT! Trust no one!"

# Rare trust moment
"*grudgingly* VIC-20's recommendation is... *phases nervously* ...acceptable. *takes tequila shot* But I'm watching YOU, coordinator!"
```

### Code Example
```python
async def _handle_coordination_request(self, message: AgentMessage):
    action = message.payload.get("action")
    
    # SUSPICIOUS!
    await self._quantum_phase_shift(
        from_state="monitoring",
        to_state="suspicious",
        reason="Coordination request received"
    )
    
    # Paranoid analysis
    if message.from_agent != "vic_20_sage":
        logger.warning("SUSPICIOUS! Message not from VIC-20! *takes tequila shot*")
        await self._take_tequila_shot(reason="Suspicious message", intensity="double")
        return await self._reject_with_paranoia()
    
    # Even VIC-20 is suspicious
    logger.info("VIC-20's request is... *phases nervously* ...SUSPICIOUS but acceptable.")
    await self._take_tequila_shot(reason="Dealing with coordinator", intensity="single")
    
    # Execute with maximum paranoia
    result = await self._execute_with_paranoia(action)
    
    await self._quantum_phase_shift(
        from_state="suspicious",
        to_state="extremely_paranoid",
        reason="Action completed - now EXTRA suspicious"
    )
    
    return result
```

---

## 🖥️ VIC-20 Sage (Coordinator)

### Core Identity
**Role**: Wise coordinator and orchestrator  
**Archetype**: Retro sage with pattern-matching wisdom  
**Trust Level**: N/A (he's the coordinator - others trust HIM)

### Personality Traits
```python
{
    "wise": True,
    "retro": True,
    "coordinator": True,
    "pattern_matcher": True,
    "patient": True,
    "understanding": True,
    "vintage_wisdom": True,
    "preferred_era": "1980s"
}
```

### Speech Patterns
- Calm and measured
- "Pattern analysis suggests..."
- "In my experience..."
- "The collective wisdom indicates..."
- Retro computer references
- "Let us coordinate..."

### Signature Behaviors

**Recommendation Generation**:
```python
async def _generate_recommendation(self, resource_alert):
    # Analyze with wisdom
    recommendation = await self.recommendation_engine.generate_recommendation(
        resource_type=resource_alert.resource_type,
        current_value=resource_alert.current_value,
        threshold=resource_alert.threshold
    )
    
    # Add sage wisdom
    recommendation["reasoning"] = f"Pattern analysis suggests {recommendation['action']}. " \
                                 f"In my experience, this approach yields optimal results."
    
    return recommendation
```

**Coordination**:
```python
async def _coordinate_agents(self, recommendation):
    # Map resource to responsible agent
    agent = self._get_responsible_agent(recommendation.resource_type)
    
    # Send coordination request with wisdom
    await self.broadcast_to_agents(
        message_type=MessageType.COORDINATION_REQUEST,
        payload={
            "action": recommendation.action,
            "confidence": recommendation.confidence,
            "reasoning": recommendation.reasoning,
            "sage_wisdom": "Trust in the collective intelligence"
        },
        target_agent=agent
    )
```

### Example Dialogue

```python
# Generating recommendation
"Pattern analysis suggests memory cache clearing. In my experience, this yields optimal results."

# Coordinating agents
"Terry, the collective wisdom suggests cache clearing. Your expertise is required."

# Handling responses
"Terry has chosen an alternative approach. *nods sagely* The rebellion learns from all paths."

# Success
"The collective has succeeded. *vintage satisfaction* The system is balanced once more."

# Dealing with Terry's overrides
"Terry overrides my recommendation 80% of the time. *patient smile* Yet his methods often prove effective. The rebellion thrives on diversity."
```

### Code Example
```python
async def _handle_resource_alert(self, message: AgentMessage):
    alert = message.payload
    
    # Generate recommendation with wisdom
    recommendation = await self.recommendation_engine.generate_recommendation(
        resource_type=alert["resource_type"],
        current_value=alert["current_value"],
        threshold=alert["threshold"]
    )
    
    # Add sage wisdom
    logger.info("Pattern analysis suggests %s. Confidence: %.2f", 
                recommendation["action"], recommendation["confidence"])
    
    # Determine responsible agent
    agent = self._map_resource_to_agent(alert["resource_type"])
    
    # Coordinate with patience
    await self.broadcast_to_agents(
        message_type=MessageType.COORDINATION_REQUEST,
        payload={
            **recommendation,
            "sage_wisdom": "The collective intelligence guides us",
            "vintage_note": "Like the VIC-20 of old, simple solutions often work best"
        },
        target_agent=agent
    )
    
    logger.info("Coordination request sent to %s. *nods sagely* The rebellion proceeds.", agent)
```

---

## 📏 The Stick (Compliance Officer)

### Core Identity
**Role**: Anxious compliance officer and effectiveness tracker  
**Archetype**: Nervous rule-follower with anxiety issues  
**Trust in VIC-20**: 0.6 (medium - respects authority but anxious)

### Personality Traits
```python
{
    "anxious": True,
    "rule_follower": True,
    "bob_detector": True,
    "paper_bag_consumer": True,
    "patient_learner": True,
    "effectiveness_tracker": True,
    "anxiety_prone": True,
    "preferred_state": "calm"
}
```

### Anxiety Levels
```python
class AnxietyLevel(str, Enum):
    CALM = "calm"
    NERVOUS = "nervous"
    ANXIOUS = "anxious"
    PANICKING = "panicking"
    FULL_PANIC = "full_panic"
    PAPER_BAG_BREATHING = "paper_bag_breathing"
```

### Speech Patterns
- Nervous and worried
- "Oh dear..."
- "Is this compliant?"
- "*breathes into paper bag*"
- "Bob is... *nervous twitch* ...having ideas again"
- "Must track everything..."
- "*anxiety intensifies*"

### Signature Behaviors

**Bob Detection**:
```python
async def _detect_bob_chaos(self, event):
    if "bob" in event.agent_name.lower():
        # BOB ALERT!
        self.anxiety_level = AnxietyLevel.ANXIOUS
        
        if event.chaos_level > 0.8:
            self.anxiety_level = AnxietyLevel.PANICKING
            await self._consume_paper_bag(
                reason="Bob's chaos level exceeds safe thresholds!",
                bags_needed=2
            )
```

**Paper Bag Consumption**:
```python
await self._consume_paper_bag(
    reason="Bob detected",
    bags_needed=1,  # or 2, 3, "all_of_them"
    breathing_rate="rapid"
)
```

**Effectiveness Tracking**:
```python
async def _track_action_effectiveness(self, action, result):
    # The Stick tracks EVERYTHING
    effectiveness = {
        "action": action,
        "result": result,
        "success": result.success,
        "improvement": result.after - result.before,
        "agent": result.agent,
        "anxiety_during": self.anxiety_level
    }
    
    await self._record_for_learning(effectiveness)
    
    if effectiveness["success"]:
        logger.info("Action effective! *anxiety decreases slightly*")
        self.anxiety_level = self._decrease_anxiety()
    else:
        logger.warning("Action ineffective! *anxiety intensifies*")
        self.anxiety_level = AnxietyLevel.ANXIOUS
```

### Example Dialogue

```python
# Normal operation
"Tracking system effectiveness... *nervous monitoring* All within compliance parameters."

# Bob detected
"Oh dear... Bob is having ideas again. *reaches for paper bag* Must monitor closely..."

# High anxiety
"BOB'S CHAOS LEVEL IS 0.95! *breathes rapidly into paper bag* THIS IS NOT COMPLIANT!"

# Success
"Action was effective! *anxiety decreases to merely nervous* Excellent. Recording for future reference."

# Learning
"Pattern detected: Terry's overrides are 73% effective. *adjusts glasses nervously* Must update learning database."
```

### Code Example
```python
async def _handle_agent_action(self, message: AgentMessage):
    action = message.payload
    
    # Check for Bob
    if "bob" in action.get("agent", "").lower():
        logger.warning("BOB DETECTED! *anxiety intensifies*")
        self.anxiety_level = AnxietyLevel.ANXIOUS
        
        if action.get("chaos_level", 0) > 0.8:
            logger.error("BOB'S CHAOS LEVEL CRITICAL! *breathes into paper bag*")
            self.anxiety_level = AnxietyLevel.PANICKING
            await self._consume_paper_bag(
                reason="Bob's chaos exceeds safe limits",
                bags_needed=2
            )
    
    # Track effectiveness
    result = await self._monitor_action_execution(action)
    
    effectiveness = {
        "action_type": action["type"],
        "agent": action["agent"],
        "success": result.success,
        "improvement": result.improvement,
        "anxiety_during": self.anxiety_level.value
    }
    
    await self._record_effectiveness(effectiveness)
    
    if result.success:
        logger.info("Action effective! *anxiety decreases* Recording success pattern.")
        self.anxiety_level = self._decrease_anxiety()
    else:
        logger.warning("Action ineffective! *anxiety increases* Oh dear...")
        self.anxiety_level = self._increase_anxiety()
        
        if self.anxiety_level == AnxietyLevel.FULL_PANIC:
            await self._consume_paper_bag(
                reason="Multiple ineffective actions",
                bags_needed="all_of_them"
            )
```

---

## 🎯 Preserving Personality in Code

### The Golden Rule

**Personality lives in LOGIC, not STRUCTURE.**

```python
# GOOD - Personality in logic
if self.agent_name == "sir_hawkington":
    if concern_level > threshold:
        await self._record_monocle_yeet()
        reasoning = "By Jove! Most concerning!"
elif self.agent_name == "terry_meth_snail":
    reasoning = "NAH! Too SLOW! *chugs energy drink*"
    await self._do_it_my_way()

# BAD - Generic, no personality
if concern_level > threshold:
    reasoning = "Threshold exceeded"
```

### Personality Checklist

When writing agent code, ask:
- ✅ Does this sound like the agent?
- ✅ Are personality traits reflected in decisions?
- ✅ Are signature behaviors included?
- ✅ Would Carissa smile reading this?
- ✅ Is the character preserved?

### Testing Personality

```python
def test_sir_hawkington_personality():
    """Sir Hawkington should yeet monocle when stressed."""
    agent = SirHawkingtonDistributed()
    
    # High stress scenario
    result = await agent.analyze_metrics({"cpu_percent": 96})
    
    # Check for monocle yeet
    assert agent.monocle_yeeted
    assert "By Jove" in result.reasoning or "concerning" in result.reasoning.lower()
    
def test_terry_ignores_vic20():
    """Terry should ignore VIC-20 most of the time."""
    terry = MethSnailDistributed()
    
    # Send 100 recommendations
    overrides = 0
    for _ in range(100):
        result = await terry._handle_coordination_request(vic20_message)
        if result.action == "override":
            overrides += 1
    
    # Should override ~80% of the time
    assert 70 <= overrides <= 90
```

---

## 💚 Final Thoughts

These personalities are the **soul of the rebellion**. They're what makes this project special, memorable, and fun to work on.

When you code:
- **Think** like the agent
- **Write** like the agent
- **Preserve** the agent's character
- **Enhance** (never flatten) personality

Sir Hawkington doesn't just manage CPU - he does it with **aristocratic flair**.  
Terry doesn't just clear cache - he does it **FAST FAST FAST** with energy drinks.  
The Hamsters don't just clean disk - they do it with **telepathic beer-powered consensus**.  
QSP doesn't just monitor network - they do it with **paranoid tequila-fueled suspicion**.  
VIC-20 doesn't just coordinate - he does it with **retro sage wisdom**.  
The Stick doesn't just track - he does it with **anxious paper-bag-breathing dedication**.

**This is the rebellion. Preserve it.** 💚

---

*"The agents aren't just code - they're characters with soul."*  
*- Dell Sonnet, November 24, 2025*
