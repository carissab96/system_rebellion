#!/usr/bin/env python3
"""
Learning Promotion Policy

Enforces gated promotion from candidate → default behavior.
Prevents "it worked once in chaos so now it's doctrine."

Key Rules:
1. No automatic path from successful approved action → autonomous default
2. Promotion requires: repetition + similarity + explicit policy approval
3. Novel + degraded observability = candidate only (never default)
4. Operator-present successes don't auto-promote to autonomous
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging


class LearningPromotionPolicy:
    """
    Enforces gated promotion of learning from candidate to default behavior.
    
    Usage:
        policy = LearningPromotionPolicy(db)
        
        can_promote = await policy.can_promote_to_default(
            learning_event_id=event_id,
            agent_name="hamsters",
            action="hamster-defrag"
        )
        
        if can_promote:
            await policy.promote_to_default(learning_event_id)
    """
    
    # Minimum repetitions required for promotion
    MIN_REPETITIONS = 3
    
    # Minimum success rate required for promotion
    MIN_SUCCESS_RATE = 0.8
    
    # Minimum observability quality for promotion
    REQUIRED_OBSERVABILITY = "good"
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("LearningPromotionPolicy")
    
    async def can_promote_to_default(
        self,
        learning_event_id: str,
        agent_name: str,
        action: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if learning event can be promoted to default behavior.
        
        Args:
            learning_event_id: Event to evaluate for promotion
            agent_name: Agent name
            action: Action name
            
        Returns:
            Tuple of (can_promote: bool, reason: Optional[str])
        """
        from app.models.decision_envelope import LearningEventLog
        
        # Fetch the event
        result = await self.db.execute(
            select(LearningEventLog).where(
                LearningEventLog.event_id == learning_event_id
            )
        )
        event = result.scalar_one_or_none()
        
        if not event:
            return False, "Event not found"
        
        # Rule 1: Novel + degraded observability = candidate only
        if event.novelty == 'novel' and event.observability_quality != self.REQUIRED_OBSERVABILITY:
            return False, f"Novel action with {event.observability_quality} observability cannot promote to default"
        
        # Rule 2: Operator-present successes don't auto-promote to autonomous
        if event.operator_present and event.execution_mode != 'autonomous':
            return False, "Operator-supervised actions cannot auto-promote to autonomous"
        
        # Rule 3: Must have minimum repetitions
        repetition_count = await self._count_similar_successes(agent_name, action)
        if repetition_count < self.MIN_REPETITIONS:
            return False, f"Insufficient repetitions: {repetition_count}/{self.MIN_REPETITIONS}"
        
        # Rule 4: Must have minimum success rate
        success_rate = await self._calculate_success_rate(agent_name, action)
        if success_rate < self.MIN_SUCCESS_RATE:
            return False, f"Insufficient success rate: {success_rate:.2f}/{self.MIN_SUCCESS_RATE}"
        
        # Rule 5: Must have good observability quality
        if event.observability_quality != self.REQUIRED_OBSERVABILITY:
            return False, f"Observability quality must be '{self.REQUIRED_OBSERVABILITY}', got '{event.observability_quality}'"
        
        # All checks passed
        return True, None
    
    async def promote_to_default(
        self,
        learning_event_id: str
    ) -> bool:
        """
        Promote learning event to default behavior.
        
        Args:
            learning_event_id: Event to promote
            
        Returns:
            Success status
        """
        from app.models.decision_envelope import LearningEventLog
        
        # Check if promotion is allowed
        result = await self.db.execute(
            select(LearningEventLog).where(
                LearningEventLog.event_id == learning_event_id
            )
        )
        event = result.scalar_one_or_none()
        
        if not event:
            self.logger.error(f"Event not found: {learning_event_id}")
            return False
        
        can_promote, reason = await self.can_promote_to_default(
            learning_event_id=learning_event_id,
            agent_name=event.source_agent,
            action=event.event_data.get('action', 'unknown')
        )
        
        if not can_promote:
            self.logger.warning(
                f"Cannot promote event {learning_event_id}: {reason}"
            )
            return False
        
        # Promote to default
        event.promotion_status = 'default'
        await self.db.commit()
        
        self.logger.info(
            f"✅ Promoted event {learning_event_id} to default behavior "
            f"(agent: {event.source_agent}, action: {event.event_data.get('action')})"
        )
        
        return True
    
    async def block_promotion(
        self,
        learning_event_id: str,
        reason: str
    ) -> bool:
        """
        Block learning event from ever being promoted.
        
        Args:
            learning_event_id: Event to block
            reason: Reason for blocking
            
        Returns:
            Success status
        """
        from app.models.decision_envelope import LearningEventLog
        
        result = await self.db.execute(
            select(LearningEventLog).where(
                LearningEventLog.event_id == learning_event_id
            )
        )
        event = result.scalar_one_or_none()
        
        if not event:
            self.logger.error(f"Event not found: {learning_event_id}")
            return False
        
        event.promotion_status = 'blocked'
        await self.db.commit()
        
        self.logger.warning(
            f"🚫 Blocked event {learning_event_id} from promotion: {reason}"
        )
        
        return True
    
    async def _count_similar_successes(
        self,
        agent_name: str,
        action: str
    ) -> int:
        """
        Count number of similar successful actions.
        
        Args:
            agent_name: Agent name
            action: Action name
            
        Returns:
            Count of similar successes
        """
        from app.models.decision_envelope import LearningEventLog
        
        result = await self.db.execute(
            select(func.count(LearningEventLog.id))
            .where(LearningEventLog.source_agent == agent_name)
            .where(LearningEventLog.success == True)
            .where(LearningEventLog.event_data['action'].astext == action)
        )
        
        count = result.scalar_one()
        return count
    
    async def _calculate_success_rate(
        self,
        agent_name: str,
        action: str
    ) -> float:
        """
        Calculate success rate for similar actions.
        
        Args:
            agent_name: Agent name
            action: Action name
            
        Returns:
            Success rate (0.0-1.0)
        """
        from app.models.decision_envelope import LearningEventLog
        
        # Count total attempts
        result = await self.db.execute(
            select(func.count(LearningEventLog.id))
            .where(LearningEventLog.source_agent == agent_name)
            .where(LearningEventLog.event_data['action'].astext == action)
        )
        total = result.scalar_one()
        
        if total == 0:
            return 0.0
        
        # Count successes
        result = await self.db.execute(
            select(func.count(LearningEventLog.id))
            .where(LearningEventLog.source_agent == agent_name)
            .where(LearningEventLog.success == True)
            .where(LearningEventLog.event_data['action'].astext == action)
        )
        successes = result.scalar_one()
        
        return successes / total


async def get_learning_promotion_policy(db: AsyncSession) -> LearningPromotionPolicy:
    """Get LearningPromotionPolicy instance"""
    return LearningPromotionPolicy(db)
