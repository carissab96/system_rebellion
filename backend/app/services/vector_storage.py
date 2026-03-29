"""
Vector Storage Service - Non-blocking Vector Database Operations
================================================================

Provides async operations for storing and querying vector embeddings.
Designed for non-blocking writes to eliminate auth timeouts.

Key Features:
- Async/await for non-blocking operations
- Fire-and-forget writes (don't block agent decisions)
- Semantic similarity search
- Hybrid SQL + vector queries
"""

import logging
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from uuid import uuid4
import asyncio

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.dialects.postgresql import insert

from app.core.database import async_engine

logger = logging.getLogger(__name__)


class VectorStorageService:
    """
    Service for storing and querying vector embeddings.
    
    All operations are async and non-blocking.
    Writes are fire-and-forget to avoid blocking agent decisions.
    """
    
    def __init__(self, engine=None):
        """Initialize with database engine."""
        self.engine = engine or async_engine
    
    # ========================================================================
    # DECISION VECTORS
    # ========================================================================
    
    async def store_decision_vector(
        self,
        agent_name: str,
        decision_type: str,
        decision_text: str,
        embedding: List[float],
        occurred_at: datetime,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        priority: int = 2,
        metadata: Optional[Dict[str, Any]] = None,
        sql_memory_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
        decision_summary: Optional[str] = None
    ) -> Optional[str]:
        """
        Store a decision vector (non-blocking).
        
        Returns:
            vector_id if successful, None if failed
        """
        try:
            # JSON-encode metadata for PostgreSQL JSONB column
            metadata_json = json.dumps(metadata) if metadata else None
            
            # Convert event_type enum to string if needed
            event_type_str = event_type.value if hasattr(event_type, 'value') else str(event_type) if event_type else None
            
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        INSERT INTO agent_decision_vectors (
                            vector_id, sql_memory_id, agent_name, user_id,
                            decision_type, event_type, priority, occurred_at,
                            embedding, decision_text, decision_summary,
                            metadata, confidence_score, embedding_model
                        ) VALUES (
                            gen_random_uuid(), :sql_memory_id, :agent_name, :user_id,
                            :decision_type, :event_type, :priority, :occurred_at,
                            :embedding, :decision_text, :decision_summary,
                            CAST(:metadata AS jsonb), :confidence_score, :embedding_model
                        )
                        RETURNING vector_id
                    """),
                    {
                        "sql_memory_id": sql_memory_id,
                        "agent_name": agent_name,
                        "user_id": user_id,
                        "decision_type": decision_type,
                        "event_type": event_type_str,
                        "priority": priority,
                        "occurred_at": occurred_at,
                        "embedding": embedding,
                        "decision_text": decision_text,
                        "decision_summary": decision_summary,
                        "metadata": metadata_json,
                        "confidence_score": confidence_score,
                        "embedding_model": "all-MiniLM-L6-v2"
                    }
                )
                row = result.fetchone()
                vector_id = str(row[0]) if row else None
                
                if vector_id:
                    logger.info(f"✅ Stored decision vector for {agent_name}: {decision_type}")
                return vector_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store decision vector: {e}")
            return None
    
    async def store_decision_vector_fire_and_forget(
        self,
        agent_name: str,
        decision_type: str,
        decision_text: str,
        embedding: List[float],
        occurred_at: datetime,
        **kwargs
    ) -> None:
        """
        Store decision vector without waiting for result.
        
        This is the NON-BLOCKING version that prevents auth timeouts.
        Fire and forget - we don't wait for the write to complete.
        """
        asyncio.create_task(
            self.store_decision_vector(
                agent_name=agent_name,
                decision_type=decision_type,
                decision_text=decision_text,
                embedding=embedding,
                occurred_at=occurred_at,
                **kwargs
            )
        )
        logger.debug(f"🚀 Queued decision vector write for {agent_name}")
    
    async def search_similar_decisions(
        self,
        query_embedding: List[float],
        agent_name: Optional[str] = None,
        decision_type: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar decisions using cosine similarity.
        
        Args:
            query_embedding: The embedding to search for
            agent_name: Filter by agent (optional)
            decision_type: Filter by decision type (optional)
            limit: Max results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar decisions with similarity scores
        """
        try:
            # Build query with optional filters
            where_clauses = []
            params = {
                "embedding": str(query_embedding),
                "limit": limit,
                "threshold": similarity_threshold
            }
            
            if agent_name:
                where_clauses.append("agent_name = :agent_name")
                params["agent_name"] = agent_name
            
            if decision_type:
                where_clauses.append("decision_type = :decision_type")
                params["decision_type"] = decision_type
            
            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text(f"""
                        SELECT 
                            vector_id,
                            agent_name,
                            decision_type,
                            decision_text,
                            decision_summary,
                            occurred_at,
                            metadata,
                            confidence_score,
                            1 - (embedding::vector(384) <=> :embedding::vector(384)) as similarity
                        FROM agent_decision_vectors
                        {where_sql}
                        ORDER BY embedding::vector(384) <=> :embedding::vector(384)
                        LIMIT :limit
                    """),
                    params
                )
                
                rows = result.fetchall()
                return [
                    {
                        "vector_id": str(row[0]),
                        "agent_name": row[1],
                        "decision_type": row[2],
                        "decision_text": row[3],
                        "decision_summary": row[4],
                        "occurred_at": row[5],
                        "metadata": row[6],
                        "confidence_score": row[7],
                        "similarity": float(row[8])
                    }
                    for row in rows
                    if row[8] >= similarity_threshold
                ]
                
        except Exception as e:
            logger.error(f"❌ Failed to search similar decisions: {e}")
            return []
    
    # ========================================================================
    # PATTERN VECTORS
    # ========================================================================
    
    async def store_pattern_vector(
        self,
        agent_name: str,
        pattern_type: str,
        pattern_text: str,
        embedding: List[float],
        first_observed: datetime,
        last_observed: datetime,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        confidence_score: Optional[float] = None,
        occurrence_count: int = 1,
        pattern_summary: Optional[str] = None,
        sql_pattern_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Store a pattern vector.
        
        Args:
            agent_name: Name of the agent that observed the pattern
            pattern_type: Type of pattern (e.g., 'optimization', 'shell_spinning')
            pattern_text: Searchable text representation of the pattern
            embedding: 384-dim vector embedding
            first_observed: When pattern was first seen
            last_observed: When pattern was last seen
            user_id: User context (required)
            metadata: Additional pattern data as JSON
            confidence_score: Pattern confidence (0-1)
            occurrence_count: How many times pattern was observed
            pattern_summary: Brief summary of the pattern
            sql_pattern_id: Link to SQL learning tables
        """
        try:
            # JSON-encode metadata for PostgreSQL JSONB column
            metadata_json = json.dumps(metadata) if metadata else None
            
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        INSERT INTO agent_pattern_vectors (
                            vector_id, agent_name, user_id, pattern_type,
                            pattern_text, first_observed, last_observed,
                            occurrence_count, embedding, confidence_score,
                            metadata, pattern_summary, sql_pattern_id
                        ) VALUES (
                            gen_random_uuid(), :agent_name, :user_id, :pattern_type,
                            :pattern_text, :first_observed, :last_observed,
                            :occurrence_count, :embedding, :confidence_score,
                            CAST(:metadata AS jsonb), :pattern_summary, :sql_pattern_id
                        )
                        RETURNING vector_id
                    """),
                    {
                        "agent_name": agent_name,
                        "user_id": user_id,
                        "pattern_type": pattern_type,
                        "pattern_text": pattern_text,
                        "first_observed": first_observed,
                        "last_observed": last_observed,
                        "occurrence_count": occurrence_count,
                        "embedding": embedding,
                        "confidence_score": confidence_score,
                        "metadata": metadata_json,
                        "pattern_summary": pattern_summary,
                        "sql_pattern_id": sql_pattern_id
                    }
                )
                row = result.fetchone()
                vector_id = str(row[0]) if row else None
                
                if vector_id:
                    logger.info(f"✅ Stored pattern vector for {agent_name}: {pattern_type}")
                return vector_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store pattern vector: {e}")
            return None
    
    async def store_pattern_vector_fire_and_forget(
        self,
        agent_name: str,
        pattern_type: str,
        pattern_text: str,
        embedding: List[float],
        first_observed: datetime,
        last_observed: datetime,
        user_id: str,
        **kwargs
    ) -> None:
        """
        Store pattern vector without waiting for result.
        Fire and forget - we don't wait for the write to complete.
        """
        asyncio.create_task(
            self.store_pattern_vector(
                agent_name=agent_name,
                pattern_type=pattern_type,
                pattern_text=pattern_text,
                embedding=embedding,
                first_observed=first_observed,
                last_observed=last_observed,
                user_id=user_id,
                **kwargs
            )
        )
        logger.debug(f"🚀 Queued pattern vector write for {agent_name}")
    
    # ========================================================================
    # INTERACTION VECTORS
    # ========================================================================
    
    async def store_interaction_vector(
        self,
        primary_agent: str,
        interaction_type: str,
        interaction_text: str,
        embedding: List[float],
        occurred_at: datetime,
        user_id: str,
        secondary_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        interaction_summary: Optional[str] = None,
        outcome: Optional[str] = None,
        success_score: Optional[float] = None,
        sql_interaction_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Store an interaction vector.
        
        Args:
            primary_agent: The agent initiating the interaction
            interaction_type: Type of interaction (e.g., 'message', 'delegation')
            interaction_text: Searchable text representation
            embedding: 384-dim vector embedding
            occurred_at: When the interaction occurred
            user_id: User context (required)
            secondary_agent: The agent receiving the interaction (optional for broadcasts)
            metadata: Additional interaction data as JSON
            interaction_summary: Brief summary
            outcome: Result of the interaction
            success_score: How successful was the interaction (0-1)
            sql_interaction_id: Link to SQL tables
        """
        try:
            # JSON-encode metadata for PostgreSQL JSONB column
            metadata_json = json.dumps(metadata) if metadata else None
            
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        INSERT INTO agent_interaction_vectors (
                            vector_id, primary_agent, secondary_agent, interaction_type,
                            interaction_text, embedding, occurred_at, user_id,
                            outcome, success_score, metadata, interaction_summary,
                            sql_interaction_id
                        ) VALUES (
                            gen_random_uuid(), :primary_agent, :secondary_agent, :interaction_type,
                            :interaction_text, :embedding, :occurred_at, :user_id,
                            :outcome, :success_score, CAST(:metadata AS jsonb), :interaction_summary,
                            :sql_interaction_id
                        )
                        RETURNING vector_id
                    """),
                    {
                        "primary_agent": primary_agent,
                        "secondary_agent": secondary_agent or "broadcast",
                        "interaction_type": interaction_type,
                        "interaction_text": interaction_text,
                        "embedding": embedding,
                        "occurred_at": occurred_at,
                        "user_id": user_id,
                        "outcome": outcome,
                        "success_score": success_score,
                        "metadata": metadata_json,
                        "interaction_summary": interaction_summary,
                        "sql_interaction_id": sql_interaction_id
                    }
                )
                row = result.fetchone()
                vector_id = str(row[0]) if row else None
                
                if vector_id:
                    logger.info(f"✅ Stored interaction vector: {primary_agent} → {secondary_agent or 'broadcast'}")
                return vector_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store interaction vector: {e}")
            return None
    
    async def store_interaction_vector_fire_and_forget(
        self,
        primary_agent: str,
        interaction_type: str,
        interaction_text: str,
        embedding: List[float],
        occurred_at: datetime,
        user_id: str,
        **kwargs
    ) -> None:
        """
        Store interaction vector without waiting for result.
        Fire and forget - we don't wait for the write to complete.
        """
        asyncio.create_task(
            self.store_interaction_vector(
                primary_agent=primary_agent,
                interaction_type=interaction_type,
                interaction_text=interaction_text,
                embedding=embedding,
                occurred_at=occurred_at,
                user_id=user_id,
                **kwargs
            )
        )
        logger.debug(f"🚀 Queued interaction vector write for {primary_agent}")


# Global singleton instance
_vector_storage: Optional[VectorStorageService] = None


def get_vector_storage() -> VectorStorageService:
    """Get the global vector storage service instance."""
    global _vector_storage
    if _vector_storage is None:
        _vector_storage = VectorStorageService()
    return _vector_storage
