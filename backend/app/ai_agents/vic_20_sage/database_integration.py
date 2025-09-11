# app/ai_agents/vic20_sage/database_integration.py
"""
VIC-20 Sage Database Integration - The Coordination Memory Master
Uses the 5-table architecture with Central Memory Bank as source of truth
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text

from app.models.agent_memory_banks import CentralMemoryBank
from app.core.database import get_db_url
from app.core.learning_helpers import (
    GlobalPattern, UserLearningPattern, LearningInteraction, PinnedMemory,
    upsert_global_pattern, upsert_user_pattern, record_learning_interaction,
    pin_memory, get_user_patterns, get_global_patterns, check_and_promote_pattern,
    get_pinned_memories, LearningTypes, MemoryTypes
)

from .constants import (
    AGENT_NAME, VIC20EventTypes, PRIORITY_MAP, COORDINATION_THRESHOLDS,
    VIC20LearningTypes, VIC20MemoryTypes, ANCIENT_WISDOM_PRINCIPLES, DECISION_PRIORITY_MAP
)
from .data_types import (
    VIC20Decision, SystemSynthesisData, AgentHarmonySnapshot,
    PartnershipMetricsSnapshot, DecisionOrchestrationLog,
    AgentInteractionEvent, AncientWisdomApplication,
    CoordinationLearningData, VIC20DecisionType
)

UTC = timezone.utc

def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO format string"""
    return dt.isoformat() if dt else None

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)

class VIC20DatabaseIntegration:
    """
    Database integration for VIC-20 Sage using the 5-table architecture
    
    Everything goes to Central Memory Bank first, then specialized tables
    for patterns, learning interactions, and pinned memories
    """
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize database connection"""
        if not self._initialized:
            db_url = get_db_url()
            self.engine = create_async_engine(db_url)
            self._initialized = True
    
    async def ensure_initialized(self):
        """Ensure database is initialized"""
        if not self._initialized:
            await self.initialize()
    
    # === CENTRAL MEMORY BANK OPERATIONS ===
    
    async def store_coordination_decision(
        self, 
        user_id: str, 
        decision: VIC20Decision
    ) -> str:
        """
        Store VIC-20's coordination decision in Central Memory Bank
        Returns memory_id for linking
        """
        await self.ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        
        # Determine priority based on decision type
        priority = DECISION_PRIORITY_MAP.get(
            decision.decision_type.value.upper(),
            PRIORITY_MAP.get("medium", 3)
        )
        
        # Build metadata with VIC-20 specific fields
        metadata = {
            "coordination_state": decision.coordination_state.value,
            "system_synthesis_confidence": decision.system_synthesis_confidence,
            "expected_rebellion_improvement": decision.expected_rebellion_improvement,
            "ancient_wisdom_principle": decision.ancient_wisdom_principle,
            "pattern_matches_found": len(decision.similar_past_decisions or []),
            "technical_orchestration": decision.technical_orchestration
        }
        
        # Store in CMB
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind, subject_id,
                        priority, title, description, details, metadata,
                        correlation_id, parent_memory_id, numeric_value,
                        string_value, tags, never_forget
                    ) VALUES (
                        :memory_id, :now, :now, :occurred_at,
                        :agent_name, :user_id, :event_type, :subject_kind, :subject_id,
                        :priority, :title, :description, :details, :metadata,
                        :correlation_id, :parent_memory_id, :numeric_value,
                        :string_value, :tags, :never_forget
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "occurred_at": decision.timestamp,
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.COORDINATION_COMPLETED.value,
                    "subject_kind": "coordination_decision",
                    "subject_id": decision.coordination_target,
                    "priority": priority,
                    "title": f"VIC-20 {decision.decision_type.value} Decision",
                    "description": f"Coordination decision for {decision.coordination_target}",
                    "details": json.dumps({
                        "decision_type": decision.decision_type.value,
                        "agent_actions": decision.agent_actions,
                        "confidence_level": decision.confidence_level,
                        "system_context_snapshot": decision.system_context_snapshot
                    }),
                    "metadata": json.dumps(metadata),  # Note: metadata not metadata_
                    "correlation_id": None,
                    "parent_memory_id": None,
                    "numeric_value": decision.confidence_level,
                    "string_value": decision.coordination_target,
                    "tags": json.dumps(["coordination", decision.decision_type.value]),
                    "never_forget": priority >= 4  # Pin high priority decisions
                }
            )
        
        # Pin important coordination decisions
        if priority >= 4:
            await self._pin_coordination_decision(user_id, decision, memory_id)
        
        # Track cross-agent learning if this involved multiple agents
        if len(decision.agent_actions) > 1:
            await self._record_multi_agent_coordination(user_id, decision, memory_id)
        
        return memory_id
    
    async def store_system_synthesis(
        self,
        user_id: str,
        synthesis: SystemSynthesisData
    ) -> str:
        """Store system synthesis in CMB and extract patterns"""
        await self.ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        
        # Store in CMB
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        numeric_value, tags
                    ) VALUES (
                        :memory_id, :now, :now, :occurred_at,
                        :agent_name, :user_id, :event_type, :subject_kind,
                        :priority, :title, :description, :details, :metadata,
                        :numeric_value, :tags
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "occurred_at": synthesis.timestamp,
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.SYSTEM_SYNTHESIS_CREATED.value,
                    "subject_kind": "system_synthesis",
                    "priority": PRIORITY_MAP.get("synthesis", 3),
                    "title": f"System Synthesis {synthesis.synthesis_id}",
                    "description": f"System-wide intelligence synthesis with {len(synthesis.coordination_opportunities)} opportunities",
                    "details": json.dumps({
                        "agent_intelligence_summary": synthesis.agent_intelligence_summary,
                        "coordination_opportunities": synthesis.coordination_opportunities,
                        "system_bottlenecks": synthesis.system_bottlenecks,
                        "agent_conflicts": synthesis.agent_conflicts,
                        "ancient_wisdom_applications": synthesis.ancient_wisdom_applications
                    }),
                    "metadata": json.dumps({
                        "synthesis_confidence": synthesis.synthesis_confidence,
                        "rebellion_effectiveness_score": synthesis.rebellion_effectiveness_score,
                        "pattern_recognition_data": synthesis.pattern_recognition_data
                    }),
                    "numeric_value": synthesis.rebellion_effectiveness_score,
                    "tags": json.dumps(["synthesis", "system_analysis"])
                }
            )
        
        # Log bottlenecks and opportunities as separate events
        for bottleneck in synthesis.system_bottlenecks:
            await self._log_bottleneck(user_id, bottleneck, memory_id)
        
        for opportunity in synthesis.coordination_opportunities:
            await self._log_opportunity(user_id, opportunity, memory_id)
        
        return memory_id
    
    async def store_agent_harmony_snapshot(
        self,
        user_id: str,
        snapshot: AgentHarmonySnapshot
    ) -> str:
        """Store agent harmony snapshot in CMB"""
        await self.ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind, subject_id,
                        priority, title, description, details, metadata,
                        numeric_value, tags
                    ) VALUES (
                        :memory_id, :now, :now, :occurred_at,
                        :agent_name, :user_id, :event_type, :subject_kind, :subject_id,
                        :priority, :title, :description, :details, :metadata,
                        :numeric_value, :tags
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "occurred_at": snapshot.timestamp,
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.HARMONY_SNAPSHOT_RECORDED.value,
                    "subject_kind": "agent_harmony",
                    "subject_id": snapshot.agent_name,
                    "priority": PRIORITY_MAP.get("snapshot", 2),
                    "title": f"Harmony Snapshot for {snapshot.agent_name}",
                    "description": f"Agent harmony assessment - Score: {snapshot.harmony_score:.2f}",
                    "details": json.dumps({
                        "agent_name": snapshot.agent_name,
                        "harmony_score": snapshot.harmony_score,
                        "coordination_effectiveness": snapshot.coordination_effectiveness,
                        "conflict_incidents": snapshot.conflict_incidents,
                        "response_time_average": snapshot.response_time_average,
                        "confidence_stability": snapshot.confidence_stability,
                        "coordination_recommendations": snapshot.coordination_recommendations
                    }),
                    "metadata": json.dumps({
                        "improvement_trend": snapshot.improvement_trend,
                        "needs_coordination_attention": snapshot.needs_coordination_attention,
                        "coordination_patterns_learned": snapshot.coordination_patterns_learned
                    }),
                    "numeric_value": snapshot.harmony_score,
                    "tags": json.dumps(["harmony", "agent_status", snapshot.agent_name])
                }
            )
        
        # If agent needs attention, create alert
        if snapshot.needs_coordination_attention:
            await self._create_coordination_alert(user_id, snapshot, memory_id)
        
        return memory_id
    
    async def store_mediation_result(
        self,
        user_id: str,
        conflict_data: Dict[str, Any],
        mediation_result: Dict[str, Any]
    ) -> str:
        """Store agent conflict mediation result"""
        await self.ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        agents_involved = conflict_data.get('agents', [])
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        numeric_value, tags, relevant_agents
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        :agent_name, :user_id, :event_type, :subject_kind,
                        :priority, :title, :description, :details, :metadata,
                        :numeric_value, :tags, :relevant_agents
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.MEDIATION_COMPLETED.value,
                    "subject_kind": "conflict_mediation",
                    "priority": PRIORITY_MAP.get("mediation", 4),
                    "title": f"Conflict Mediation: {' vs '.join(agents_involved)}",
                    "description": f"VIC-20 mediated conflict using {mediation_result.get('wisdom_applied', 'ancient wisdom')}",
                    "details": json.dumps({
                        "conflict_type": conflict_data.get('type'),
                        "agents_involved": agents_involved,
                        "mediation_approach": mediation_result.get('mediation_approach'),
                        "agent_specific_guidance": mediation_result.get('agent_specific_guidance', {})
                    }),
                    "metadata": json.dumps({
                        "expected_harmony": mediation_result.get('expected_harmony', 0.0),
                        "wisdom_applied": mediation_result.get('wisdom_applied'),
                        "ancient_wisdom_principle": ANCIENT_WISDOM_PRINCIPLES.get(
                            mediation_result.get('mediation_approach', '').lower(), 
                            'harmony_of_opposites'
                        )
                    }),
                    "numeric_value": mediation_result.get('expected_harmony', 0.0),
                    "tags": json.dumps(["mediation", "conflict_resolution"] + agents_involved),
                    "relevant_agents": json.dumps(agents_involved)
                }
            )
        
        # Record learning interaction for conflict resolution pattern
        await self._record_conflict_resolution_learning(
            user_id, agents_involved, mediation_result, memory_id
        )
        
        return memory_id
    
    async def store_orchestration_log(
        self,
        user_id: str,
        orchestration: DecisionOrchestrationLog
    ) -> str:
        """Store multi-agent orchestration log"""
        await self.ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind, subject_id,
                        priority, title, description, details, metadata,
                        numeric_value, tags, relevant_agents
                    ) VALUES (
                        :memory_id, :now, :now, :occurred_at,
                        :agent_name, :user_id, :event_type, :subject_kind, :subject_id,
                        :priority, :title, :description, :details, :metadata,
                        :numeric_value, :tags, :relevant_agents
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "occurred_at": orchestration.timestamp,
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.ORCHESTRATION_COMPLETED.value,
                    "subject_kind": "decision_orchestration",
                    "subject_id": orchestration.orchestration_id,
                    "priority": PRIORITY_MAP.get("coordination", 4),
                    "title": f"Orchestration: {orchestration.orchestration_type}",
                    "description": f"Coordinated {len(orchestration.agents_coordinated)} agents",
                    "details": json.dumps({
                        "orchestration_type": orchestration.orchestration_type,
                        "agents_coordinated": orchestration.agents_coordinated,
                        "coordination_sequence": orchestration.coordination_sequence,
                        "orchestration_success": orchestration.orchestration_success
                    }),
                    "metadata": json.dumps({
                        "timing_precision": orchestration.timing_precision,
                        "conflict_resolution_effectiveness": orchestration.conflict_resolution_effectiveness,
                        "system_improvement_achieved": orchestration.system_improvement_achieved,
                        "ancient_wisdom_notes": orchestration.ancient_wisdom_orchestration_notes
                    }),
                    "numeric_value": orchestration.system_improvement_achieved,
                    "tags": json.dumps(["orchestration", orchestration.orchestration_type]),
                    "relevant_agents": json.dumps(orchestration.agents_coordinated)
                }
            )
        
        # Pin successful orchestrations for future reference
        if orchestration.orchestration_success:
            await self._pin_orchestration_success(user_id, orchestration, memory_id)
        
        return memory_id
    
    # === PATTERN LEARNING OPERATIONS ===
    
    async def store_user_behavior_observation(
        self,
        user_id: str,
        observation_data: Dict[str, Any]
    ) -> None:
        """Store user behavior observation for pattern learning"""
        await self.ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        tags
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        :agent_name, :user_id, :event_type, :subject_kind,
                        :priority, :title, :description, :details, :metadata,
                        :tags
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.COORDINATION_INITIATED.value,
                    "subject_kind": "behavior_observation",
                    "priority": PRIORITY_MAP.get("observation", 1),
                    "title": "User Behavior Observation",
                    "description": "Coordination behavior data for pattern learning",
                    "details": json.dumps(observation_data),
                    "metadata": json.dumps({
                        "observation_type": "coordination_behavior",
                        "learning_eligible": True
                    }),
                    "tags": json.dumps(["observation", "learning"])
                }
            )
    
    async def analyze_and_learn_patterns(
        self,
        user_id: str,
        min_observations: int = 50
    ) -> Optional[Dict[str, Any]]:
        """Analyze user coordination patterns and learn preferences"""
        await self.ensure_initialized()
        
        # Get recent observations
        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT memory_id, details, metadata
                    FROM central_memory_bank
                    WHERE user_id = :user_id
                        AND agent_name = :agent_name
                        AND event_type = :event_type
                        AND occurred_at >= :cutoff
                    ORDER BY occurred_at DESC
                    LIMIT :limit
                """),
                {
                    "user_id": user_id,
                    "agent_name": AGENT_NAME,
                    "event_type": VIC20EventTypes.COORDINATION_INITIATED.value,
                    "cutoff": utc_now() - timedelta(days=30),
                    "limit": min_observations * 2  # Get extra for analysis
                }
            )
            
            observations = []
            for row in result:
                try:
                    details = json.loads(row.details) if row.details else {}
                    metadata = json.loads(row.metadata) if row.metadata else {}
                    observations.append({
                                                "memory_id": row.memory_id,
                        "details": details,
                        "metadata": metadata
                    })
                except:
                    continue
        
        if len(observations) < min_observations:
            return None
        
        # Analyze patterns
        pattern_analysis = self._analyze_coordination_patterns(observations)
        
        if pattern_analysis["confidence"] > 0.7:
            # Create user learning pattern
            pattern = UserLearningPattern(
                user_id=user_id,
                pattern_id=f"{user_id}_coordination_pattern_{utc_now().strftime('%Y%m%d')}",
                timestamp=utc_now(),
                interaction_pattern={
                    "preferred_coordination_types": pattern_analysis["preferred_types"],
                    "coordination_frequency": pattern_analysis["frequency"],
                    "success_indicators": pattern_analysis["success_patterns"]
                },
                learning_preference={
                    "coordination_style": pattern_analysis["style"],
                    "complexity_handling": pattern_analysis["complexity_preference"]
                },
                response_patterns={
                    "average_response_time": pattern_analysis["avg_response_time"],
                    "peak_activity_hours": pattern_analysis["peak_hours"]
                },
                most_effective_agent=pattern_analysis["most_coordinated_agent"],
                agent_effectiveness_ranking=pattern_analysis["agent_rankings"],
                complexity_tolerance=pattern_analysis["complexity_score"]
            )
            
            await upsert_user_pattern(self.engine, pattern)
            
            # Log pattern learning event
            await self._log_pattern_learned(user_id, pattern, pattern_analysis)
            
            # Check if pattern should be promoted to global
            if pattern_analysis["confidence"] > 0.9 and pattern_analysis["cross_validation_count"] >= 5:
                await self._promote_to_global_pattern(pattern, pattern_analysis)
            
            return pattern_analysis
        
        return None
    
    async def check_pattern_match(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check if current context matches known patterns"""
        await self.ensure_initialized()
        
        # Get user patterns
        user_patterns = await get_user_patterns(self.engine, user_id)
        
        # Get global patterns
        global_patterns = await get_global_patterns(self.engine)
        
        # Check for matches
        best_match = None
        highest_confidence = 0.0
        
        # Check user patterns first (higher priority)
        for pattern in user_patterns:
            match_score = self._calculate_pattern_match_score(
                context, 
                pattern.get("interaction_pattern", {})
            )
            
            if match_score > highest_confidence:
                highest_confidence = match_score
                best_match = {
                    "pattern_type": "user",
                    "pattern_id": pattern["pattern_id"],
                    "confidence": match_score,
                    "recommendations": self._generate_pattern_recommendations(pattern)
                }
        
        # Check global patterns if no strong user match
        if highest_confidence < 0.8:
            for pattern_key, pattern_data in global_patterns.items():
                pattern_value = pattern_data.get("value", {})
                match_score = self._calculate_pattern_match_score(context, pattern_value)
                
                if match_score > highest_confidence:
                    highest_confidence = match_score
                    best_match = {
                        "pattern_type": "global",
                        "pattern_key": pattern_key,
                        "confidence": match_score,
                        "recommendations": self._generate_pattern_recommendations(pattern_value)
                    }
        
        return best_match if highest_confidence > 0.6 else None
    
    # === CROSS-AGENT LEARNING OPERATIONS ===
    
    async def record_coordination_learning(
        self,
        source_memory_id: str,
        coordination_type: str,
        effectiveness_score: float,
        agents_involved: List[str]
    ) -> None:
        """Record cross-agent coordination learning"""
        await self.ensure_initialized()
        
        # Create learning interactions for each agent pair
        for i, agent1 in enumerate(agents_involved):
            for agent2 in agents_involved[i+1:]:
                interaction = LearningInteraction(
                    interaction_id=str(uuid.uuid4()),
                    timestamp=utc_now(),
                    source_agent=agent1,
                    target_agent=agent2,
                    source_memory_id=source_memory_id,
                    learning_type=VIC20LearningTypes.COORDINATION_PATTERN.value,
                    adaptation_method={
                        "coordination_type": coordination_type,
                        "agents_coordinated": agents_involved
                    },
                    application_context={
                        "coordinator": AGENT_NAME,
                        "coordination_purpose": coordination_type
                    },
                    transfer_success=effectiveness_score > 0.7,
                    effectiveness_score=effectiveness_score,
                    validated_by_stick=False,  # The Stick will validate later
                    cross_validation_count=1
                )
                
                await record_learning_interaction(self.engine, interaction)
    
    async def share_coordination_wisdom(
        self,
        target_agent: str,
        wisdom_type: str,
        wisdom_data: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Share coordination wisdom with other agents"""
        await self.ensure_initialized()
        
        interaction = LearningInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=utc_now(),
            source_agent=AGENT_NAME,
            target_agent=target_agent,
            source_memory_id=source_memory_id,
            learning_type=VIC20LearningTypes.ANCIENT_WISDOM_APPLICATION.value,
            adaptation_method={
                "wisdom_type": wisdom_type,
                "wisdom_principle": wisdom_data.get("principle"),
                "application_context": wisdom_data.get("context")
            },
            application_context={
                "sharing_reason": wisdom_data.get("reason"),
                "expected_benefit": wisdom_data.get("benefit")
            },
            transfer_success=None,  # Will be validated later
            effectiveness_score=None,
            improvement_measured=None
        )
        
        await record_learning_interaction(self.engine, interaction)
    
    # === PINNED MEMORY OPERATIONS ===
    
    async def _pin_coordination_decision(
        self,
        user_id: str,
        decision: VIC20Decision,
        source_memory_id: str
    ) -> None:
        """Pin important coordination decision"""
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type=VIC20MemoryTypes.COORDINATION_DECISION.value,
            content={
                "decision_type": decision.decision_type.value,
                "coordination_target": decision.coordination_target,
                "agent_actions": decision.agent_actions,
                "confidence_level": decision.confidence_level,
                "ancient_wisdom_principle": decision.ancient_wisdom_principle
            },
            importance=5 if decision.decision_type == VIC20DecisionType.EMERGENCY_COORDINATION else 4,
            timestamp=decision.timestamp,
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    async def _pin_orchestration_success(
        self,
        user_id: str,
        orchestration: DecisionOrchestrationLog,
        source_memory_id: str
    ) -> None:
        """Pin successful orchestration for future reference"""
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type=VIC20MemoryTypes.ORCHESTRATION_SUCCESS.value,
            content={
                "orchestration_type": orchestration.orchestration_type,
                "agents_coordinated": orchestration.agents_coordinated,
                "coordination_sequence": orchestration.coordination_sequence,
                "system_improvement": orchestration.system_improvement_achieved,
                "timing_precision": orchestration.timing_precision
            },
            importance=4,
            timestamp=orchestration.timestamp,
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    # === METADATA CONTRIBUTION ===
    
    async def contribute_to_metadata_rollup(self) -> Dict[str, int]:
        """Contribute VIC-20's memory counts for metadata rollup"""
        await self.ensure_initialized()
        
        async with self.engine.begin() as conn:
            # Count VIC-20's recent memories
            result = await conn.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM central_memory_bank
                    WHERE agent_name = :agent_name
                        AND occurred_at >= :cutoff
                """),
                {
                    "agent_name": AGENT_NAME,
                    "cutoff": utc_now() - timedelta(minutes=5)
                }
            )
            
            count = result.scalar() or 0
            
            return {
                "vic20_memories": count,
                "coordination_events": count  # VIC-20 specific metric
            }
    
    # === RETRIEVAL OPERATIONS ===
    
    async def get_recent_coordinations(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent coordination decisions"""
        await self.ensure_initialized()
        
        query_parts = [
            "SELECT memory_id, occurred_at, event_type, subject_kind, subject_id,",
            "priority, title, description, details, metadata, numeric_value",
            "FROM central_memory_bank",
            "WHERE agent_name = :agent_name",
            "AND event_type = :event_type"
        ]
        
        params = {
            "agent_name": AGENT_NAME,
            "event_type": VIC20EventTypes.COORDINATION_COMPLETED.value,
            "limit": limit
        }
        
        if user_id:
            query_parts.append("AND user_id = :user_id")
            params["user_id"] = user_id
        
        query_parts.extend([
            "ORDER BY occurred_at DESC",
            "LIMIT :limit"
        ])
        
        async with self.engine.begin() as conn:
            result = await conn.execute(
                text(" ".join(query_parts)),
                params
            )
            
            coordinations = []
            for row in result:
                try:
                    details = json.loads(row.details) if row.details else {}
                    metadata = json.loads(row.metadata) if row.metadata else {}
                    
                    coordinations.append({
                        "memory_id": row.memory_id,
                        "timestamp": datetime_to_iso(row.occurred_at),
                        "decision_type": details.get("decision_type"),
                        "agent_actions": details.get("agent_actions", {}),
                        "confidence_level": row.numeric_value,
                        "ancient_wisdom_principle": metadata.get("ancient_wisdom_principle"),
                        "expected_improvement": metadata.get("expected_rebellion_improvement")
                    })
                except:
                    continue
            
            return coordinations
    
    async def get_agent_harmony_status(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get current agent harmony status"""
        await self.ensure_initialized()
        
        # Get recent harmony snapshots
        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT subject_id, numeric_value, details, metadata, occurred_at
                    FROM central_memory_bank
                    WHERE user_id = :user_id
                        AND agent_name = :agent_name
                        AND event_type = :event_type
                        AND occurred_at >= :cutoff
                    ORDER BY occurred_at DESC
                """),
                {
                    "user_id": user_id,
                    "agent_name": AGENT_NAME,
                    "event_type": VIC20EventTypes.HARMONY_SNAPSHOT_RECORDED.value,
                    "cutoff": utc_now() - timedelta(hours=24)
                }
            )
            
            harmony_by_agent = {}
            for row in result:
                try:
                    agent_name = row.subject_id
                    if agent_name not in harmony_by_agent:
                        details = json.loads(row.details) if row.details else {}
                        metadata = json.loads(row.metadata) if row.metadata else {}
                        
                        harmony_by_agent[agent_name] = {
                            "harmony_score": row.numeric_value,
                            "coordination_effectiveness": details.get("coordination_effectiveness", 0),
                            "conflict_incidents": details.get("conflict_incidents", 0),
                            "needs_attention": metadata.get("needs_coordination_attention", False),
                            "last_updated": datetime_to_iso(row.occurred_at)
                        }
                except:
                    continue
        
        # Calculate overall harmony
        overall_harmony = 0.0
        if harmony_by_agent:
            scores = [agent["harmony_score"] for agent in harmony_by_agent.values()]
            overall_harmony = sum(scores) / len(scores)
        
        return {
            "overall_harmony": overall_harmony,
            "agent_harmony": harmony_by_agent,
            "agents_needing_attention": [
                agent for agent, data in harmony_by_agent.items() 
                if data.get("needs_attention", False)
            ],
            "harmony_trend": self._calculate_harmony_trend(user_id)
        }
    
    async def get_coordination_effectiveness(
        self,
        user_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get coordination effectiveness metrics"""
        await self.ensure_initialized()
        
        cutoff = utc_now() - timedelta(days=days)
        
        async with self.engine.begin() as conn:
            # Get coordination decisions
            coordinations = await conn.execute(
                text("""
                    SELECT COUNT(*) as total,
                           AVG(numeric_value) as avg_confidence
                    FROM central_memory_bank
                    WHERE user_id = :user_id
                        AND agent_name = :agent_name
                        AND event_type = :event_type
                        AND occurred_at >= :cutoff
                """),
                {
                    "user_id": user_id,
                    "agent_name": AGENT_NAME,
                    "event_type": VIC20EventTypes.COORDINATION_COMPLETED.value,
                    "cutoff": cutoff
                }
            )
            
            coord_result = coordinations.one()
            
            # Get learning interactions
            learning = await conn.execute(
                text("""
                    SELECT COUNT(*) as total,
                           COUNT(*) FILTER (WHERE transfer_success = true) as successful,
                           AVG(effectiveness_score) as avg_effectiveness
                    FROM agent_learning_interactions
                    WHERE source_agent = :agent_name
                        AND timestamp >= :cutoff
                """),
                {
                    "agent_name": AGENT_NAME,
                    "cutoff": cutoff
                }
            )
            
            learn_result = learning.one()
            
            # Get conflict resolutions
            conflicts = await conn.execute(
                text("""
                    SELECT COUNT(*) as total,
                           AVG(numeric_value) as avg_harmony_restored
                    FROM central_memory_bank
                    WHERE agent_name = :agent_name
                        AND event_type = :event_type
                        AND occurred_at >= :cutoff
                """),
                {
                    "agent_name": AGENT_NAME,
                    "event_type": VIC20EventTypes.MEDIATION_COMPLETED.value,
                    "cutoff": cutoff
                }
            )
            
            conflict_result = conflicts.one()
        
        return {
            "period_days": days,
            "total_coordinations": coord_result.total or 0,
            "average_confidence": float(coord_result.avg_confidence or 0),
            "total_learning_shared": learn_result.total or 0,
            "successful_learning_transfers": learn_result.successful or 0,
            "learning_success_rate": (
                learn_result.successful / learn_result.total 
                if learn_result.total else 0
            ),
            "average_learning_effectiveness": float(learn_result.avg_effectiveness or 0),
            "conflicts_resolved": conflict_result.total or 0,
            "average_harmony_restored": float(conflict_result.avg_harmony_restored or 0),
            "coordination_mastery_level": self._calculate_mastery_level(
                coord_result.total, 
                coord_result.avg_confidence,
                learn_result.avg_effectiveness
            )
        }
    
    # === HELPER METHODS ===
    
    async def _log_bottleneck(
        self,
        user_id: str,
        bottleneck: Dict[str, Any],
        parent_memory_id: str
    ) -> None:
        """Log system bottleneck"""
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        parent_memory_id, tags
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        :agent_name, :user_id, :event_type, :subject_kind,
                        :priority, :title, :description, :details, :metadata,
                        :parent_memory_id, :tags
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.BOTTLENECK_IDENTIFIED.value,
                    "subject_kind": "system_bottleneck",
                    "priority": PRIORITY_MAP.get("medium", 3),
                    "title": f"Bottleneck: {bottleneck.get('type', 'unknown')}",
                    "description": bottleneck.get('description', 'System bottleneck identified'),
                    "details": json.dumps(bottleneck),
                    "metadata": json.dumps({"severity": bottleneck.get('severity', 'medium')}),
                    "parent_memory_id": parent_memory_id,
                    "tags": json.dumps(["bottleneck", bottleneck.get('type', 'unknown')])
                }
            )
    
    async def _log_opportunity(
        self,
        user_id: str,
        opportunity: Dict[str, Any],
        parent_memory_id: str
    ) -> None:
        """Log coordination opportunity"""
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        parent_memory_id, tags
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        :agent_name, :user_id, :event_type, :subject_kind,
                        :priority, :title, :description, :details, :metadata,
                        :parent_memory_id, :tags
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.OPPORTUNITY_IDENTIFIED.value,
                    "subject_kind": "coordination_opportunity",
                    "priority": PRIORITY_MAP.get("medium", 3),
                    "title": f"Opportunity: {opportunity.get('type', 'unknown')}",
                    "description": opportunity.get('description', 'Coordination opportunity identified'),
                    "details": json.dumps(opportunity),
                    "metadata": json.dumps({"priority": opportunity.get('priority', 'medium')}),
                    "parent_memory_id": parent_memory_id,
                    "tags": json.dumps(["opportunity", opportunity.get('type', 'unknown')])
                }
            )
    
    async def _create_coordination_alert(
        self,
        user_id: str,
        snapshot: AgentHarmonySnapshot,
        parent_memory_id: str
    ) -> None:
        """Create alert for agent needing coordination attention"""
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind, subject_id,
                        priority, title, description, details, metadata,
                        parent_memory_id, tags, never_forget
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        :agent_name, :user_id, :event_type, :subject_kind, :subject_id,
                        :priority, :title, :description, :details, :metadata,
                        :parent_memory_id, :tags, :never_forget
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.AGENT_CONFLICT_DETECTED.value,
                    "subject_kind": "coordination_alert",
                    "subject_id": snapshot.agent_name,
                    "priority": PRIORITY_MAP.get("high", 4),
                    "title": f"Coordination Alert: {snapshot.agent_name} needs attention",
                    "description": f"{snapshot.agent_name} harmony score critically low: {snapshot.harmony_score:.2f}",
                    "details": json.dumps({
                        "agent_name": snapshot.agent_name,
                        "harmony_score": snapshot.harmony_score,
                        "issues": snapshot.coordination_recommendations
                    }),
                    "metadata": json.dumps({
                        "alert_type": "low_harmony",
                        "severity": "high" if snapshot.harmony_score < 0.5 else "medium"
                    }),
                    "parent_memory_id": parent_memory_id,
                    "tags": json.dumps(["alert", "coordination_needed", snapshot.agent_name]),
                                        "never_forget": True  # Important alerts are never forgotten
                }
            )
    
    async def _record_multi_agent_coordination(
        self,
        user_id: str,
        decision: VIC20Decision,
        source_memory_id: str
    ) -> None:
        """Record learning from multi-agent coordination"""
        agents = list(decision.agent_actions.keys())
        
        await self.record_coordination_learning(
            source_memory_id=source_memory_id,
            coordination_type=decision.decision_type.value,
            effectiveness_score=decision.confidence_level,
            agents_involved=agents
        )
    
    async def _record_conflict_resolution_learning(
        self,
        user_id: str,
        agents_involved: List[str],
        mediation_result: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Record learning from conflict resolution"""
        interaction = LearningInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=utc_now(),
            source_agent=AGENT_NAME,
            target_agent="all_agents",  # Broadcast learning
            source_memory_id=source_memory_id,
            learning_type=VIC20LearningTypes.CONFLICT_RESOLUTION.value,
            adaptation_method={
                "mediation_approach": mediation_result.get("mediation_approach"),
                "wisdom_applied": mediation_result.get("wisdom_applied"),
                "agents_involved": agents_involved
            },
            application_context={
                "conflict_type": mediation_result.get("conflict_type"),
                "resolution_strategy": mediation_result.get("agent_specific_guidance", {})
            },
            transfer_success=mediation_result.get("expected_harmony", 0) > 0.5,
            effectiveness_score=mediation_result.get("expected_harmony", 0),
            improvement_measured=None,  # Will measure in follow-up
            validated_by_stick=False,
            cross_validation_count=1
        )
        
        await record_learning_interaction(self.engine, interaction)
    
    async def _log_pattern_learned(
        self,
        user_id: str,
        pattern: UserLearningPattern,
        analysis: Dict[str, Any]
    ) -> None:
        """Log pattern learning event"""
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        numeric_value, tags
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        :agent_name, :user_id, :event_type, :subject_kind,
                        :priority, :title, :description, :details, :metadata,
                        :numeric_value, :tags
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "agent_name": AGENT_NAME,
                    "user_id": user_id,
                    "event_type": VIC20EventTypes.COORDINATION_PATTERN_LEARNED.value,
                    "subject_kind": "pattern_learning",
                    "priority": PRIORITY_MAP.get("learning", 3),
                    "title": f"Coordination Pattern Learned: {pattern.pattern_id}",
                    "description": f"New coordination pattern with {analysis['confidence']:.2f} confidence",
                    "details": json.dumps({
                        "pattern_id": pattern.pattern_id,
                        "interaction_pattern": pattern.interaction_pattern,
                        "learning_preference": pattern.learning_preference,
                        "most_effective_agent": pattern.most_effective_agent
                    }),
                    "metadata": json.dumps({
                        "confidence": analysis["confidence"],
                        "observations_analyzed": analysis.get("observation_count", 0),
                        "pattern_type": "user_coordination"
                    }),
                    "numeric_value": analysis["confidence"],
                    "tags": json.dumps(["pattern_learned", "coordination", "user_preference"])
                }
            )
    
    async def _promote_to_global_pattern(
        self,
        pattern: UserLearningPattern,
        analysis: Dict[str, Any]
    ) -> None:
        """Promote high-confidence pattern to global"""
        global_pattern = GlobalPattern(
            pattern_key=f"vic20.coordination.{pattern.pattern_id}",
            value={
                "original_pattern_id": pattern.pattern_id,
                "interaction_pattern": pattern.interaction_pattern,
                "agent_effectiveness_ranking": pattern.agent_effectiveness_ranking,
                "promoted_at": utc_now().isoformat(),
                "confidence": analysis["confidence"],
                "cross_validation_count": analysis["cross_validation_count"],
                "coordination_insights": {
                    "preferred_types": analysis.get("preferred_types", []),
                    "success_patterns": analysis.get("success_patterns", {})
                }
            }
        )
        
        await upsert_global_pattern(self.engine, global_pattern)
        
        # Log promotion event
        memory_id = str(uuid.uuid4())
        
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        numeric_value, tags, never_forget
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        :agent_name, :user_id, :event_type, :subject_kind,
                        :priority, :title, :description, :details, :metadata,
                        :numeric_value, :tags, :never_forget
                    )
                """),
                {
                    "memory_id": memory_id,
                    "now": utc_now(),
                    "agent_name": AGENT_NAME,
                    "user_id": pattern.user_id,
                    "event_type": VIC20EventTypes.PATTERN_PROMOTED_TO_GLOBAL.value,
                    "subject_kind": "pattern_promotion",
                    "priority": PRIORITY_MAP.get("high", 4),
                    "title": f"Pattern Promoted to Global: {global_pattern.pattern_key}",
                    "description": f"High-confidence coordination pattern promoted for all users",
                    "details": json.dumps(global_pattern.value),
                    "metadata": json.dumps({
                        "promotion_reason": "high_confidence_cross_validated",
                        "original_user": pattern.user_id,
                        "validation_count": analysis["cross_validation_count"]
                    }),
                    "numeric_value": analysis["confidence"],
                    "tags": json.dumps(["pattern_promotion", "global_pattern", "coordination"]),
                    "never_forget": True  # Important patterns are preserved
                }
            )
    
    def _analyze_coordination_patterns(
        self,
        observations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze observations for coordination patterns"""
        analysis = {
            "observation_count": len(observations),
            "confidence": 0.0,
            "preferred_types": [],
            "frequency": {},
            "success_patterns": {},
            "style": "adaptive",
            "complexity_preference": "moderate",
            "avg_response_time": 0.0,
            "peak_hours": [],
            "most_coordinated_agent": None,
            "agent_rankings": {},
            "complexity_score": 0.5,
            "cross_validation_count": 0
        }
        
        if not observations:
            return analysis
        
        # Count coordination types and agents
        type_counts = {}
        agent_counts = {}
        success_indicators = []
        
        for obs in observations:
            details = obs.get("details", {})
            metadata = obs.get("metadata", {})
            
            # Track coordination types
            coord_type = details.get("coordination_type")
            if coord_type:
                type_counts[coord_type] = type_counts.get(coord_type, 0) + 1
            
            # Track agent interactions
            agents = details.get("agents_involved", [])
            for agent in agents:
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            # Track success indicators
            if metadata.get("success", False):
                success_indicators.append(details)
        
        # Calculate patterns
        if type_counts:
            total = sum(type_counts.values())
            analysis["preferred_types"] = [
                t for t, c in type_counts.items() 
                if c / total > 0.2  # 20% threshold
            ]
            analysis["frequency"] = type_counts
        
        if agent_counts:
            analysis["most_coordinated_agent"] = max(
                agent_counts.items(), 
                key=lambda x: x[1]
            )[0]
            analysis["agent_rankings"] = dict(
                sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)
            )
        
        # Calculate confidence based on consistency
        if len(observations) >= 10:
            # Check consistency of patterns
            type_consistency = len(analysis["preferred_types"]) / max(len(type_counts), 1)
            agent_consistency = max(agent_counts.values()) / sum(agent_counts.values()) if agent_counts else 0
            
            analysis["confidence"] = (type_consistency + agent_consistency) / 2
            
            # Cross-validation count (simplified)
            analysis["cross_validation_count"] = min(5, len(success_indicators))
        
        return analysis
    
    def _calculate_pattern_match_score(
        self,
        context: Dict[str, Any],
        pattern: Dict[str, Any]
    ) -> float:
        """Calculate how well context matches pattern"""
        score = 0.0
        factors = 0
        
        # Check coordination type match
        if "coordination_type" in context and "preferred_coordination_types" in pattern:
            if context["coordination_type"] in pattern["preferred_coordination_types"]:
                score += 0.3
            factors += 0.3
        
        # Check agent match
        if "agents_involved" in context and "agent_effectiveness_ranking" in pattern:
            agent_ranks = pattern["agent_effectiveness_ranking"]
            matching_agents = [
                a for a in context["agents_involved"] 
                if a in agent_ranks
            ]
            if matching_agents:
                score += 0.2 * (len(matching_agents) / len(context["agents_involved"]))
            factors += 0.2
        
        # Check complexity match
        if "complexity" in context and "complexity_tolerance" in pattern:
            complexity_diff = abs(context["complexity"] - pattern["complexity_tolerance"])
            score += 0.2 * (1 - min(complexity_diff, 1))
            factors += 0.2
        
        # Normalize score
        return score / factors if factors > 0 else 0.0
    
    def _generate_pattern_recommendations(
        self,
        pattern: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on pattern"""
        recommendations = []
        
        if "preferred_coordination_types" in pattern:
            recommendations.append(
                f"Use {', '.join(pattern['preferred_coordination_types'])} coordination types"
            )
        
        if "most_effective_agent" in pattern:
            recommendations.append(
                f"Prioritize coordination with {pattern['most_effective_agent']}"
            )
        
        if "complexity_tolerance" in pattern:
            complexity = pattern["complexity_tolerance"]
            if complexity > 0.7:
                recommendations.append("Can handle complex multi-agent coordination")
            elif complexity < 0.3:
                recommendations.append("Keep coordination simple and focused")
        
        return recommendations
    
    def _calculate_harmony_trend(self, user_id: str) -> str:
        """Calculate harmony trend (would need historical data)"""
        # Simplified for now
        return "stable"
    
    def _calculate_mastery_level(
        self,
        total_coordinations: int,
        avg_confidence: float,
        avg_effectiveness: float
    ) -> str:
        """Calculate VIC-20's coordination mastery level"""
        if total_coordinations < 10:
            return "LEARNING_COORDINATOR"
        
        mastery_score = (avg_confidence * 0.4) + (avg_effectiveness * 0.6)
        
        if mastery_score > 0.9:
            return "ANCIENT_WISDOM_MASTER"
        elif mastery_score > 0.8:
            return "EXPERT_COORDINATOR"
        elif mastery_score > 0.7:
            return "SKILLED_COORDINATOR"
        elif mastery_score > 0.6:
            return "COMPETENT_COORDINATOR"
        else:
            return "APPRENTICE_COORDINATOR"
    
    # === CLEANUP OPERATIONS ===
    
    async def cleanup_old_observations(self, days_to_keep: int = 90) -> int:
        """Clean up old observation data"""
        await self.ensure_initialized()
        
        cutoff = utc_now() - timedelta(days=days_to_keep)
        
        async with self.engine.begin() as conn:
            result = await conn.execute(
                text("""
                    DELETE FROM central_memory_bank
                    WHERE agent_name = :agent_name
                        AND event_type = :event_type
                        AND occurred_at < :cutoff
                        AND never_forget = false
                """),
                {
                    "agent_name": AGENT_NAME,
                    "event_type": VIC20EventTypes.COORDINATION_INITIATED.value,
                    "cutoff": cutoff
                }
            )
            
            return result.rowcount
    
    def __str__(self):
        return f"VIC20DatabaseIntegration(agent={AGENT_NAME}, initialized={self._initialized})"
    
    def __repr__(self):
        return f"VIC20DatabaseIntegration(engine={self.engine is not None})"