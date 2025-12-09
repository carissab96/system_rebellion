# app/core/learning_helpers.py
"""
System Rebellion - Learning and Pattern Helpers
Central utilities for pattern learning, cross-agent interactions, and memory management
"""

from __future__ import annotations

import asyncio
import json  # Add this for JSON serialization
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, List
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

UTC = timezone.utc

# --- Value Objects for Pattern Management -------------------------------------

@dataclass
class GlobalPattern:
    """Global patterns that apply to all users and agents"""
    pattern_key: str
    value: Dict[str, Any]
    id: Optional[str] = None  # defaults to pattern_key if omitted
    updated_at: Optional[datetime] = None

@dataclass
class UserLearningPattern:
    """Per-user learned preferences and behavior patterns"""
    user_id: str
    pattern_id: str  # unique
    timestamp: Optional[datetime] = None
    interaction_pattern: Optional[Dict[str, Any]] = None
    learning_preference: Optional[Dict[str, Any]] = None
    response_patterns: Optional[Dict[str, Any]] = None
    most_effective_agent: Optional[str] = None
    communication_style_preference: Optional[Dict[str, Any]] = None
    complexity_tolerance: Optional[float] = None
    skill_improvement_areas: Optional[Dict[str, Any]] = None
    knowledge_gaps: Optional[Dict[str, Any]] = None
    success_patterns: Optional[Dict[str, Any]] = None
    agent_effectiveness_ranking: Optional[Dict[str, Any]] = None
    collaborative_preferences: Optional[Dict[str, Any]] = None

@dataclass
class LearningInteraction:
    """Cross-agent learning provenance and effectiveness tracking"""
    interaction_id: str  # unique
    timestamp: datetime
    source_agent: str
    target_agent: str
    source_memory_id: str
    learning_type: str
    adaptation_method: Optional[Dict[str, Any]] = None
    application_context: Optional[Dict[str, Any]] = None
    transfer_success: Optional[bool] = None
    effectiveness_score: Optional[float] = None
    improvement_measured: Optional[float] = None
    validated_by_stick: Optional[bool] = None
    cross_validation_count: Optional[int] = None

@dataclass
class PinnedMemory:
    """High-value memory for fast agent-specific retrieval"""
    user_id: str
    agent_name: str
    memory_type: str
    content: Dict[str, Any]
    importance: Optional[int] = None
    timestamp: Optional[datetime] = None
    source_memory_id: Optional[str] = None  # Link back to CMB

# --- Pattern Management Functions ---------------------------------------------

async def upsert_global_pattern(
    engine: AsyncEngine, 
    pattern: GlobalPattern
) -> None:
    """
    Upsert a global pattern that applies to all users
    
    Examples:
    - "When CPU > 85% and Bob is active, pre-warm resupply"
    - "Hamster infrastructure modifications require immediate backup"
    """
    now = pattern.updated_at or datetime.now(UTC)
    pid = pattern.id or pattern.pattern_key
    
    stmt = text("""
        INSERT INTO agent_global_patterns (id, pattern_key, value, updated_at)
        VALUES (:id, :pattern_key, :value, :updated_at)
        ON CONFLICT (id) DO UPDATE
          SET value = EXCLUDED.value,
              pattern_key = EXCLUDED.pattern_key,
              updated_at = EXCLUDED.updated_at
    """)
    
    async with engine.begin() as conn:
        await conn.execute(stmt, {
            "id": pid,
            "pattern_key": pattern.pattern_key,
            "value": json.dumps(pattern.value),  # Serialize for SQLite
            "updated_at": now,
        })

async def _store_pattern_vector_if_available(
    pattern: UserLearningPattern,
    agent_name: str
) -> None:
    """
    Fire-and-forget: Store pattern vector embedding for semantic search.
    Silently fails if embedding service unavailable.
    """
    try:
        from app.services.vector_storage import get_vector_storage
        from app.services.embedding_service import get_embedding_service
        
        # Build searchable text from pattern
        pattern_text_parts = []
        if pattern.interaction_pattern:
            pattern_text_parts.append(f"Pattern: {json.dumps(pattern.interaction_pattern)[:300]}")
        if pattern.learning_preference:
            pattern_text_parts.append(f"Preference: {json.dumps(pattern.learning_preference)[:200]}")
        if pattern.success_patterns:
            pattern_text_parts.append(f"Success: {json.dumps(pattern.success_patterns)[:200]}")
        
        if not pattern_text_parts:
            return
        
        pattern_text = " | ".join(pattern_text_parts)
        
        # Generate embedding
        embedding_service = get_embedding_service()
        embedding = await embedding_service.generate_embedding_async(pattern_text)
        
        if not embedding:
            return
        
        # Determine pattern type from interaction_pattern
        pattern_type = "user_learning"
        if pattern.interaction_pattern and isinstance(pattern.interaction_pattern, dict):
            pattern_type = pattern.interaction_pattern.get("pattern_type", "user_learning")
        
        # Store the vector
        now = datetime.now(UTC)
        vector_storage = get_vector_storage()
        await vector_storage.store_pattern_vector(
            agent_name=agent_name,
            pattern_type=pattern_type,
            pattern_text=pattern_text,
            embedding=embedding,
            first_observed=pattern.timestamp or now,
            last_observed=now,
            user_id=pattern.user_id,
            metadata={
                "pattern_id": pattern.pattern_id,
                "most_effective_agent": pattern.most_effective_agent,
                "complexity_tolerance": pattern.complexity_tolerance
            },
            confidence_score=pattern.complexity_tolerance,  # Use as proxy
            pattern_summary=f"{pattern_type} pattern for {pattern.user_id}",
            sql_pattern_id=pattern.pattern_id
        )
        
    except Exception as e:
        # Fire-and-forget - don't let vector storage failures affect pattern storage
        import logging
        logger = logging.getLogger("learning_helpers")
        logger.debug(f"Failed to store pattern vector: {e}")


async def upsert_user_pattern(
    engine: AsyncEngine,
    pattern: UserLearningPattern,
    agent_name: str = "system"
) -> None:
    """
    Upsert a user-specific learned pattern
    
    Called after analyzing sufficient observations (e.g., every 50 CMB entries)
    Also stores a vector embedding for semantic pattern search.
    """
    ts = pattern.timestamp or datetime.now(UTC)
    
    # Serialize all JSON fields
    def serialize_field(field):
        if field is None:
            return None
        return json.dumps(field) if isinstance(field, (dict, list)) else field
    
    stmt = text("""
        INSERT INTO user_learning_patterns (
          pattern_id, user_id, timestamp,
          interaction_pattern, learning_preference, response_patterns,
          most_effective_agent, communication_style_preference, complexity_tolerance,
          skill_improvement_areas, knowledge_gaps, success_patterns,
          agent_effectiveness_ranking, collaborative_preferences
        ) VALUES (
          :pattern_id, :user_id, :timestamp,
          :interaction_pattern, :learning_preference, :response_patterns,
          :most_effective_agent, :communication_style_preference, :complexity_tolerance,
          :skill_improvement_areas, :knowledge_gaps, :success_patterns,
          :agent_effectiveness_ranking, :collaborative_preferences
        )
        ON CONFLICT (pattern_id) DO UPDATE SET
          user_id = EXCLUDED.user_id,
          timestamp = EXCLUDED.timestamp,
          interaction_pattern = EXCLUDED.interaction_pattern,
          learning_preference = EXCLUDED.learning_preference,
          response_patterns = EXCLUDED.response_patterns,
          most_effective_agent = EXCLUDED.most_effective_agent,
          communication_style_preference = EXCLUDED.communication_style_preference,
          complexity_tolerance = EXCLUDED.complexity_tolerance,
          skill_improvement_areas = EXCLUDED.skill_improvement_areas,
          knowledge_gaps = EXCLUDED.knowledge_gaps,
          success_patterns = EXCLUDED.success_patterns,
          agent_effectiveness_ranking = EXCLUDED.agent_effectiveness_ranking,
          collaborative_preferences = EXCLUDED.collaborative_preferences
    """)
    
    async with engine.begin() as conn:
        await conn.execute(stmt, {
            "pattern_id": pattern.pattern_id,
            "user_id": pattern.user_id,
            "timestamp": ts,
            "interaction_pattern": serialize_field(pattern.interaction_pattern),
            "learning_preference": serialize_field(pattern.learning_preference),
            "response_patterns": serialize_field(pattern.response_patterns),
            "most_effective_agent": pattern.most_effective_agent,
            "communication_style_preference": serialize_field(pattern.communication_style_preference),
            "complexity_tolerance": pattern.complexity_tolerance,
            "skill_improvement_areas": serialize_field(pattern.skill_improvement_areas),
            "knowledge_gaps": serialize_field(pattern.knowledge_gaps),
            "success_patterns": serialize_field(pattern.success_patterns),
            "agent_effectiveness_ranking": serialize_field(pattern.agent_effectiveness_ranking),
            "collaborative_preferences": serialize_field(pattern.collaborative_preferences),
        })
    
    # Fire-and-forget: Store pattern vector for semantic search
    asyncio.create_task(_store_pattern_vector_if_available(pattern, agent_name))


async def record_learning_interaction(
    engine: AsyncEngine,
    interaction: LearningInteraction
) -> None:
    """
    Record when one agent learns from another
    
    This creates the provenance graph showing how knowledge flows through the system
    """
    stmt = text("""
        INSERT INTO agent_learning_interactions (
          interaction_id, timestamp, source_agent, target_agent,
          source_memory_id, learning_type, adaptation_method, application_context,
          transfer_success, effectiveness_score, improvement_measured,
          validated_by_stick, cross_validation_count
        ) VALUES (
          :interaction_id, :timestamp, :source_agent, :target_agent,
          :source_memory_id, :learning_type, :adaptation_method, :application_context,
          :transfer_success, :effectiveness_score, :improvement_measured,
          :validated_by_stick, :cross_validation_count
        )
        ON CONFLICT (interaction_id) DO UPDATE SET
          timestamp = EXCLUDED.timestamp,
          source_agent = EXCLUDED.source_agent,
          target_agent = EXCLUDED.target_agent,
          source_memory_id = EXCLUDED.source_memory_id,
          learning_type = EXCLUDED.learning_type,
          adaptation_method = EXCLUDED.adaptation_method,
          application_context = EXCLUDED.application_context,
          transfer_success = EXCLUDED.transfer_success,
          effectiveness_score = EXCLUDED.effectiveness_score,
          improvement_measured = EXCLUDED.improvement_measured,
          validated_by_stick = EXCLUDED.validated_by_stick,
                    cross_validation_count = EXCLUDED.cross_validation_count
    """)
    
    async with engine.begin() as conn:
        await conn.execute(stmt, {
            "interaction_id": interaction.interaction_id,
            "timestamp": interaction.timestamp,
            "source_agent": interaction.source_agent,
            "target_agent": interaction.target_agent,
            "source_memory_id": interaction.source_memory_id,
            "learning_type": interaction.learning_type,
            "adaptation_method": json.dumps(interaction.adaptation_method) if interaction.adaptation_method else None,
            "application_context": json.dumps(interaction.application_context) if interaction.application_context else None,
            "transfer_success": interaction.transfer_success,
            "effectiveness_score": interaction.effectiveness_score,
            "improvement_measured": interaction.improvement_measured,
            "validated_by_stick": interaction.validated_by_stick,
            "cross_validation_count": interaction.cross_validation_count
        })

async def pin_memory(
    engine: AsyncEngine,
    memory: PinnedMemory
) -> str:
    """
    Pin a high-value memory for fast agent-specific retrieval
    
    Returns the generated UUID for linking back to CMB entries
    """
    mem_id = str(uuid.uuid4())
    ts = memory.timestamp or datetime.now(UTC)
    
    stmt = text("""
        INSERT INTO agent_memories (
            id, user_id, agent_name, memory_type, content,
            importance, timestamp, last_accessed, access_count
        )
        VALUES (
            :id, :user_id, :agent_name, :memory_type, :content,
            :importance, :timestamp, :last_accessed, :access_count
        )
    """)
    
    async with engine.begin() as conn:
        await conn.execute(stmt, {
            "id": mem_id,
            "user_id": memory.user_id,
            "agent_name": memory.agent_name,
            "memory_type": memory.memory_type,
            "content": json.dumps(memory.content),  # Serialize for SQLite
            "importance": memory.importance,
            "timestamp": ts,
            "last_accessed": ts,
            "access_count": 0,
        })
    
    return mem_id

# --- Pattern Retrieval Functions ----------------------------------------------

async def get_user_patterns(
    engine: AsyncEngine,
    user_id: str,
    min_confidence: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Get all patterns for a user, optionally filtered by confidence"""
    query = text("""
        SELECT 
            pattern_id,
            interaction_pattern,
            learning_preference,
            response_patterns,
            most_effective_agent,
            communication_style_preference,
            complexity_tolerance,
            success_patterns,
            agent_effectiveness_ranking
        FROM user_learning_patterns
        WHERE user_id = :user_id
        ORDER BY timestamp DESC
    """)
    
    async with engine.begin() as conn:
        result = await conn.execute(query, {"user_id": user_id})
        patterns = []
        
        for row in result.mappings():
            pattern = dict(row)
            
            # Deserialize JSON fields
            for field in ['interaction_pattern', 'learning_preference', 'response_patterns', 
                         'communication_style_preference', 'success_patterns', 'agent_effectiveness_ranking']:
                if pattern.get(field) and isinstance(pattern[field], str):
                    try:
                        pattern[field] = json.loads(pattern[field])
                    except:
                        pass
            
            # Apply confidence filter if requested
            if min_confidence and pattern.get('success_patterns'):
                avg_confidence = pattern['success_patterns'].get('average_confidence', 0)
                if avg_confidence < min_confidence:
                    continue
            
            patterns.append(pattern)
        
        return patterns

async def get_global_patterns(
    engine: AsyncEngine,
    pattern_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get global patterns, optionally filtered by keys"""
    if pattern_keys:
        query = text("""
            SELECT pattern_key, value, updated_at
            FROM agent_global_patterns
            WHERE pattern_key = ANY(:keys)
            ORDER BY updated_at DESC
        """)
        params = {"keys": pattern_keys}
    else:
        query = text("""
            SELECT pattern_key, value, updated_at
            FROM agent_global_patterns
            ORDER BY updated_at DESC
        """)
        params = {}
    
    async with engine.begin() as conn:
        result = await conn.execute(query, params)
        return {
            row['pattern_key']: {
                'value': row['value'],
                'updated_at': row['updated_at']
            }
            for row in result.mappings()
        }

# --- Learning Analytics Functions ---------------------------------------------

async def get_learning_effectiveness(
    engine: AsyncEngine,
    agent_name: Optional[str] = None,
    days: int = 7
) -> Dict[str, Any]:
    """Analyze learning effectiveness for an agent or the whole system"""
    since = datetime.now(UTC) - timedelta(days=days)
    
    if agent_name:
        query = text("""
            SELECT 
                COUNT(*) as total_interactions,
                COUNT(*) FILTER (WHERE transfer_success = true) as successful_transfers,
                AVG(effectiveness_score) as avg_effectiveness,
                AVG(improvement_measured) as avg_improvement,
                COUNT(DISTINCT source_agent) as learned_from_agents,
                COUNT(DISTINCT learning_type) as learning_types_used
            FROM agent_learning_interactions
            WHERE target_agent = :agent_name
                AND timestamp >= :since
        """)
        params = {"agent_name": agent_name, "since": since}
    else:
        query = text("""
            SELECT 
                target_agent,
                COUNT(*) as total_interactions,
                COUNT(*) FILTER (WHERE transfer_success = true) as successful_transfers,
                AVG(effectiveness_score) as avg_effectiveness,
                AVG(improvement_measured) as avg_improvement
            FROM agent_learning_interactions
            WHERE timestamp >= :since
            GROUP BY target_agent
            ORDER BY avg_effectiveness DESC NULLS LAST
        """)
        params = {"since": since}
    
    async with engine.begin() as conn:
        result = await conn.execute(query, params)
        
        if agent_name:
            row = result.mappings().one_or_none()
            if not row:
                return {
                    "agent_name": agent_name,
                    "total_interactions": 0,
                    "successful_transfers": 0,
                    "success_rate": 0.0,
                    "avg_effectiveness": 0.0,
                    "avg_improvement": 0.0,
                    "learned_from_agents": 0,
                    "learning_types_used": 0
                }
            
            data = dict(row)
            total = data['total_interactions']
            data['success_rate'] = (
                data['successful_transfers'] / total if total > 0 else 0.0
            )
            data['agent_name'] = agent_name
            return data
        else:
            results = []
            for row in result.mappings():
                data = dict(row)
                total = data['total_interactions']
                data['success_rate'] = (
                    data['successful_transfers'] / total if total > 0 else 0.0
                )
                results.append(data)
            return {"agents": results, "period_days": days}
# --- Metadata Rollup Functions ------------------------------------------------

AGENT_COLUMN_MAP = {
    # central_memory_bank.agent_name -> memory_bank_metadata column
    "hawkington": "hawkington_memories",
    "meth_snail": "snail_memories",
    "hamsters": "hamsters_memories",
    "quantum_shadow_people": "qsp_memories",
    "vic_20_sage": "vic20_memories",
    "the_stick": "stick_memories",
}

async def hydrate_memory_bank_metadata(
    engine: AsyncEngine,
    window_minutes: int = 5
) -> None:
    """
    Insert one roll-up row into memory_bank_metadata for the recent window
    Uses occurred_at/timestamp windows to keep work bounded
    """
    now = datetime.now(UTC)
    start = now - timedelta(minutes=window_minutes)

    # 1) Totals from central_memory_bank
    total_q = text("""
        SELECT COUNT(*) AS total
        FROM central_memory_bank
        WHERE occurred_at >= :start AND occurred_at < :end
    """)

    per_agent_q = text("""
        SELECT agent_name, COUNT(*) AS c
        FROM central_memory_bank
        WHERE occurred_at >= :start AND occurred_at < :end
        GROUP BY agent_name
    """)

    # 2) Learning stats from agent_learning_interactions
    li_q = text("""
        SELECT
          COUNT(*) FILTER (WHERE transfer_success IS TRUE) AS succ,
          COUNT(*) FILTER (WHERE transfer_success IS FALSE) AS fail,
          AVG(effectiveness_score) AS avg_eff
        FROM agent_learning_interactions
        WHERE timestamp >= :start AND timestamp < :end
    """)

    # 3) Stick anxiety snapshot from CMB
    anxiety_q = text("""
        SELECT AVG(CAST(details->>'current_anxiety' AS FLOAT)) AS avg_anx
        FROM central_memory_bank
        WHERE agent_name = 'the_stick'
          AND occurred_at >= :start AND occurred_at < :end
          AND details->>'current_anxiety' IS NOT NULL
    """)

    async with engine.begin() as conn: 
        total = (await conn.execute(total_q, {'start': start, 'end': now})).scalar() or 0
        per_agent_rows = (await conn.execute(per_agent_q, {'start': start, 'end': now})).mappings().all()
        li_result = (await conn.execute(li_q, {'start': start, 'end': now})).mappings().first()
        li_row = li_result if li_result else {"succ": 0, "fail": 0, "avg_eff": 0.0}
        anx = (await conn.execute(anxiety_q, {'start': start, 'end': now})).scalar()

        # Map per-agent counts into the metadata columns
        per_agent_counts: Dict[str, int] = {row["agent_name"]: int(row["c"]) for row in per_agent_rows}
        meta_cols: Dict[str, Any] = {col: 0 for col in AGENT_COLUMN_MAP.values()}
        for agent, col in AGENT_COLUMN_MAP.items():
            meta_cols[col] = per_agent_counts.get(agent, 0)

        succ = int(li_row.get("succ") or 0)
        fail = int(li_row.get("fail") or 0)
        avg_eff = float(li_row.get("avg_eff") or 0.0)

        # Simple health heuristic
        denom = succ + fail
        success_rate = (succ / denom) if denom else None
        eff_norm = None
        if avg_eff:
            eff_norm = avg_eff if avg_eff <= 1 else min(avg_eff / 100.0, 1.0)
        health = None
        if success_rate is not None and eff_norm is not None:
            health = round((success_rate * 0.5 + eff_norm * 0.5), 4)

        insert_stmt = text("""
            INSERT INTO memory_bank_metadata (
              timestamp,
              total_memories,
              central_bank_memories,
              cross_agent_learnings,
              hawkington_memories,
              snail_memories,
              hamsters_memories,
              qsp_memories,
              vic20_memories,
              stick_memories,
              successful_transfers,
              failed_transfers,
              average_effectiveness_score,
              memory_bank_health_score,
              stick_anxiety_level,
              memory_retrieval_speed_ms,
              cross_agent_query_speed_ms,
              learning_application_success_rate
            ) VALUES (
              :timestamp,
              :total_memories,
              :central_bank_memories,
              :cross_agent_learnings,
              :hawkington_memories,
              :snail_memories,
              :hamsters_memories,
              :qsp_memories,
              :vic20_memories,
              :stick_memories,
              :successful_transfers,
              :failed_transfers,
              :average_effectiveness_score,
              :memory_bank_health_score,
              :stick_anxiety_level,
              :memory_retrieval_speed_ms,
              :cross_agent_query_speed_ms,
              :learning_application_success_rate
            )
        """)

        payload = {
            "timestamp": now,
            "total_memories": total,
            "central_bank_memories": total,
            "cross_agent_learnings": denom,
            **meta_cols,
            "successful_transfers": succ,
            "failed_transfers": fail,
            "average_effectiveness_score": avg_eff if denom else None,
            "memory_bank_health_score": health,
            "stick_anxiety_level": float(anx) if anx is not None else None,
            "memory_retrieval_speed_ms": None,  # To be implemented with timing
            "cross_agent_query_speed_ms": None,  # To be implemented with timing
            "learning_application_success_rate": success_rate,
        }

        await conn.execute(insert_stmt, payload)

# --- Scheduler for Automated Rollups ------------------------------------------

async def run_metadata_scheduler(
    engine: AsyncEngine,
    every_seconds: int = 300
) -> None:
    """
    Fire-and-forget loop for metadata rollups
    Call with asyncio.create_task(...) on startup
    """
    interval = max(60, every_seconds)
    while True:
        try:
            await hydrate_memory_bank_metadata(engine)
        except Exception as e:
            # Log but don't crash the scheduler
            import logging
            logger = logging.getLogger("learning_helpers.scheduler")
            logger.error(f"Metadata rollup failed: {e}")
        await asyncio.sleep(interval)

# --- Helper Functions for Common Patterns -------------------------------------

async def check_and_promote_pattern(
    engine: AsyncEngine,
    user_pattern_id: str,
    confidence_threshold: float = 0.9,
    cross_validation_count: int = 5
) -> bool:
    """
    Check if a user pattern should be promoted to a global pattern
    
    Returns True if pattern was promoted
    """
    # Get the user pattern
    query = text("""
        SELECT 
            ulp.*,
            COUNT(DISTINCT ali.source_agent) as validation_sources
        FROM user_learning_patterns ulp
        LEFT JOIN agent_learning_interactions ali 
            ON ali.adaptation_method->>'pattern_id' = ulp.pattern_id
            AND ali.transfer_success = true
        WHERE ulp.pattern_id = :pattern_id
        GROUP BY ulp.pattern_id
    """)
    
    async with engine.begin() as conn:
        result = await conn.execute(query, {"pattern_id": user_pattern_id})
        row = result.mappings().one_or_none()
        
        if not row:
            return False
        
        # Check promotion criteria
        success_patterns = row.get('success_patterns', {})
        avg_confidence = success_patterns.get('average_confidence', 0)
        validation_sources = row['validation_sources']
        
        if avg_confidence >= confidence_threshold and validation_sources >= cross_validation_count:
            # Promote to global pattern
            global_pattern = GlobalPattern(
                pattern_key=f"promoted.{user_pattern_id}",
                value={
                    'original_pattern_id': user_pattern_id,
                    'interaction_pattern': row['interaction_pattern'],
                    'success_patterns': success_patterns,
                    'promoted_at': datetime.now(UTC).isoformat(),
                    'confidence': avg_confidence,
                    'validation_count': validation_sources
                }
            )
            
            await upsert_global_pattern(engine, global_pattern)
            return True
    
    return False

async def get_pinned_memories(
    engine: AsyncEngine,
    user_id: str,
    agent_name: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get pinned memories for a user, optionally filtered by agent or type"""
    query_parts = ["SELECT * FROM agent_memories WHERE user_id = :user_id"]
    params = {"user_id": user_id, "limit": limit}
    
    if agent_name:
        query_parts.append("AND agent_name = :agent_name")
        params["agent_name"] = agent_name
    
    if memory_type:
        query_parts.append("AND memory_type = :memory_type")
        params["memory_type"] = memory_type
    
    query_parts.append("ORDER BY importance DESC, timestamp DESC")
    query_parts.append("LIMIT :limit")
    
    query = text(" ".join(query_parts))
    
    async with engine.begin() as conn:
        result = await conn.execute(query, params)
        memories = []
        
        for row in result.mappings():
            memory = dict(row)
            # Update access tracking
            update_q = text("""
                UPDATE agent_memories 
                SET last_accessed = :now, access_count = access_count + 1
                WHERE id = :id
            """)
            await conn.execute(update_q, {"now": datetime.now(UTC), "id": memory['id']})
            memories.append(memory)
        
        return memories

# --- Constants for Learning Types ---------------------------------------------

class LearningTypes:
    """Standard learning types for consistency across agents"""
    PATTERN_GENERALIZATION = "pattern_generalization"
    BEHAVIOR_ADAPTATION = "behavior_adaptation"
    THRESHOLD_ADJUSTMENT = "threshold_adjustment"
    STRATEGY_TRANSFER = "strategy_transfer"
    ERROR_CORRECTION = "error_correction"
    COLLABORATIVE_INSIGHT = "collaborative_insight"
    EMERGENCY_RESPONSE = "emergency_response"
    OPTIMIZATION_TECHNIQUE = "optimization_technique"

class MemoryTypes:
    """Standard memory types for pinned memories"""
    CRITICAL_DECISION = "critical_decision"
    PATTERN_DISCOVERY = "pattern_discovery"
    USER_PREFERENCE = "user_preference"
    SYSTEM_ANOMALY = "system_anomaly"
    SUCCESSFUL_INTERVENTION = "successful_intervention"
    LEARNING_MILESTONE = "learning_milestone"
    COLLECTIVE_INSIGHT = "collective_insight"