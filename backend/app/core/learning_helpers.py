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

async def upsert_user_pattern(
    engine: AsyncEngine,
    pattern: UserLearningPattern
) -> None:
    """
    Upsert a user-specific learned pattern
    
    Called after analyzing sufficient observations (e.g., every 50 CMB entries)
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

# ... (rest of the functions remain the same)

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