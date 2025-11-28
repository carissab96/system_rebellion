"""
Embedding Service - Vector Generation for Semantic Search
==========================================================

Provides embedding generation for agent decisions, patterns, and interactions.
Uses sentence-transformers for CPU-based inference (~38ms per embedding).

This service is the bridge between agent intelligence and vector storage.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from functools import lru_cache

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Singleton service for generating embeddings from text.
    
    Uses all-MiniLM-L6-v2 model:
    - 384 dimensions
    - ~38ms per embedding on CPU
    - Optimized for semantic similarity
    """
    
    _instance: Optional['EmbeddingService'] = None
    _model: Optional[SentenceTransformer] = None
    _model_name: str = "all-MiniLM-L6-v2"
    _dimensions: int = 384
    
    def __new__(cls):
        """Singleton pattern - only one model instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding model (lazy loading)."""
        if self._model is None:
            logger.info(f"🔮 Loading embedding model: {self._model_name}")
            start = datetime.now()
            self._model = SentenceTransformer(self._model_name)
            load_time = (datetime.now() - start).total_seconds()
            logger.info(f"✅ Embedding model loaded in {load_time:.2f}s")
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self._model_name
    
    @property
    def dimensions(self) -> int:
        """Get the embedding dimensions."""
        return self._dimensions
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats (384 dimensions)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self._dimensions
        
        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return [0.0] * self._dimensions
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [[0.0] * self._dimensions] * len(texts)
    
    async def generate_embedding_async(self, text: str) -> List[float]:
        """
        Generate embedding asynchronously (non-blocking).
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats (384 dimensions)
        """
        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_embedding, text)
    
    async def generate_embeddings_batch_async(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts asynchronously.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_embeddings_batch, texts)


# Helper functions for common embedding patterns

def create_decision_text(
    agent_name: str,
    decision_type: str,
    description: str,
    reasoning: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create searchable text for a decision embedding.
    
    Format optimized for semantic similarity:
    - Agent identity
    - Decision type
    - Description
    - Reasoning
    - Relevant context
    """
    parts = [
        f"Agent: {agent_name}",
        f"Decision Type: {decision_type}",
        f"Description: {description}",
        f"Reasoning: {reasoning}"
    ]
    
    if context:
        # Add relevant context fields
        if "priority" in context:
            parts.append(f"Priority: {context['priority']}")
        if "event_type" in context:
            parts.append(f"Event: {context['event_type']}")
        if "affected_agents" in context:
            parts.append(f"Affected Agents: {', '.join(context['affected_agents'])}")
    
    return " | ".join(parts)


def create_pattern_text(
    agent_name: str,
    pattern_type: str,
    pattern_name: str,
    description: str,
    success_rate: Optional[float] = None
) -> str:
    """
    Create searchable text for a pattern embedding.
    """
    parts = [
        f"Agent: {agent_name}",
        f"Pattern Type: {pattern_type}",
        f"Pattern: {pattern_name}",
        f"Description: {description}"
    ]
    
    if success_rate is not None:
        parts.append(f"Success Rate: {success_rate:.2%}")
    
    return " | ".join(parts)


def create_interaction_text(
    from_agent: str,
    to_agent: Optional[str],
    interaction_type: str,
    content: str,
    priority: Optional[int] = None
) -> str:
    """
    Create searchable text for an interaction embedding.
    """
    target = to_agent if to_agent else "broadcast"
    
    parts = [
        f"From: {from_agent}",
        f"To: {target}",
        f"Type: {interaction_type}",
        f"Content: {content}"
    ]
    
    if priority is not None:
        parts.append(f"Priority: {priority}")
    
    return " | ".join(parts)


# Global singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the global embedding service instance.
    
    Returns:
        EmbeddingService singleton
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
