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
                            :metadata::jsonb, :confidence_score, :embedding_model
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
                "embedding": query_embedding,
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
        pattern_description: str,
        embedding: List[float],
        pattern_data: Dict[str, Any],
        first_observed: datetime,
        last_observed: datetime,
        pattern_name: Optional[str] = None,
        user_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
        success_rate: Optional[float] = None,
        observation_count: int = 1,
        application_count: int = 0
    ) -> Optional[str]:
        """Store a pattern vector."""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        INSERT INTO agent_pattern_vectors (
                            vector_id, agent_name, user_id, pattern_type,
                            pattern_name, pattern_description, first_observed,
                            last_observed, observation_count, embedding,
                            confidence_score, success_rate, application_count,
                            pattern_data, embedding_model
                        ) VALUES (
                            gen_random_uuid(), :agent_name, :user_id, :pattern_type,
                            :pattern_name, :pattern_description, :first_observed,
                            :last_observed, :observation_count, :embedding,
                            :confidence_score, :success_rate, :application_count,
                            :pattern_data, :embedding_model
                        )
                        RETURNING vector_id
                    """),
                    {
                        "agent_name": agent_name,
                        "user_id": user_id,
                        "pattern_type": pattern_type,
                        "pattern_name": pattern_name,
                        "pattern_description": pattern_description,
                        "first_observed": first_observed,
                        "last_observed": last_observed,
                        "observation_count": observation_count,
                        "embedding": embedding,
                        "confidence_score": confidence_score,
                        "success_rate": success_rate,
                        "application_count": application_count,
                        "pattern_data": pattern_data,
                        "embedding_model": "all-MiniLM-L6-v2"
                    }
                )
                row = result.fetchone()
                return str(row[0]) if row else None
                
        except Exception as e:
            logger.error(f"❌ Failed to store pattern vector: {e}")
            return None
    
    # ========================================================================
    # INTERACTION VECTORS
    # ========================================================================
    
    async def store_interaction_vector(
        self,
        from_agent: str,
        interaction_type: str,
        interaction_text: str,
        embedding: List[float],
        occurred_at: datetime,
        to_agent: Optional[str] = None,
        priority: int = 2,
        metadata: Optional[Dict[str, Any]] = None,
        interaction_summary: Optional[str] = None
    ) -> Optional[str]:
        """Store an interaction vector."""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        INSERT INTO agent_interaction_vectors (
                            vector_id, from_agent, to_agent, interaction_type,
                            occurred_at, embedding, interaction_text,
                            interaction_summary, metadata, priority, embedding_model
                        ) VALUES (
                            gen_random_uuid(), :from_agent, :to_agent, :interaction_type,
                            :occurred_at, :embedding, :interaction_text,
                            :interaction_summary, :metadata, :priority, :embedding_model
                        )
                        RETURNING vector_id
                    """),
                    {
                        "from_agent": from_agent,
                        "to_agent": to_agent,
                        "interaction_type": interaction_type,
                        "occurred_at": occurred_at,
                        "embedding": embedding,
                        "interaction_text": interaction_text,
                        "interaction_summary": interaction_summary,
                        "metadata": metadata,
                        "priority": priority,
                        "embedding_model": "all-MiniLM-L6-v2"
                    }
                )
                row = result.fetchone()
                return str(row[0]) if row else None
                
        except Exception as e:
            logger.error(f"❌ Failed to store interaction vector: {e}")
            return None


# Global singleton instance
_vector_storage: Optional[VectorStorageService] = None


def get_vector_storage() -> VectorStorageService:
    """Get the global vector storage service instance."""
    global _vector_storage
    if _vector_storage is None:
        _vector_storage = VectorStorageService()
    return _vector_storage
