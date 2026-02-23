#!/usr/bin/env python3
"""
Sir Hawkington's Learning Layer - Aristocratic Pattern Recognition

Stores and learns from:
- Triage decisions and outcomes
- Escalation success rates
- Data quality patterns
- Monocle yeet incidents
- Specialist routing effectiveness

This enables Sir Hawkington to improve his triage accuracy over time.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_learning import AgentLearningRecord
from .perception import HawkPerceptionContext
from .reasoning import TriageReasoning
from .action_selection import TriageAction

logger = logging.getLogger('HawkLearning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class HawkLearningRecord:
    """Record of a triage decision for learning"""
    
    # Input context
    resource_type: str
    current_value: float
    threshold: float
    severity: str
    data_quality_score: float
    
    # Decision details
    action_type: str
    should_escalate: bool
    target_specialist: Optional[str]
    confidence: float
    
    # Reasoning
    risk_level: str
    primary_reason: str
    
    # Personality behaviors
    monocle_yeets: int
    monocle_state: str
    aristocratic_confidence: float
    
    # Outcome (filled in later)
    success: Optional[bool] = None
    outcome_notes: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=utc_now)
    learning_record_id: Optional[str] = None
    storage_success: bool = False
    situation_fingerprint: Optional[str] = None


class HawkLearning:
    """
    Sir Hawkington's learning layer for improving triage decisions.
    
    🧐 "One must learn from one's experiences to maintain aristocratic excellence!"
    """
    
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        
    async def learn(
        self,
        context: HawkPerceptionContext,
        reasoning: TriageReasoning,
        action: TriageAction,
        outcome_success: Optional[bool] = None
    ) -> HawkLearningRecord:
        """
        Store triage decision for learning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            action: Selected action
            outcome_success: Whether the action was successful (if known)
            
        Returns:
            HawkLearningRecord that was stored
        """
        logger.info(f"🧐📚 Recording triage decision for learning...")
        
        # Create learning record
        learning_record = HawkLearningRecord(
            resource_type=context.resource_type,
            current_value=context.current_value,
            threshold=context.threshold,
            severity=context.severity,
            data_quality_score=context.data_quality_score,
            action_type=action.action_type,
            should_escalate=reasoning.should_escalate,
            target_specialist=action.target_agent,
            confidence=action.confidence,
            risk_level=reasoning.risk_level,
            primary_reason=reasoning.primary_reason,
            monocle_yeets=context.monocle_yeet_count,
            monocle_state=action.monocle_state,
            aristocratic_confidence=action.aristocratic_confidence,
            success=outcome_success
        )
        
        # Store in database
        storage_success = await self._store_in_database(learning_record, context, reasoning, action)
        learning_record.storage_success = storage_success
        learning_record.situation_fingerprint = f"{context.resource_type}_{context.severity}_{action.action_type}"
        
        logger.info(
            f"🧐✅ Learning recorded: {action.action_type} for {context.resource_type}, "
            f"confidence={action.confidence:.2f}"
        )
        
        return learning_record
    
    async def _store_in_database(
        self,
        learning_record: HawkLearningRecord,
        context: HawkPerceptionContext,
        reasoning: TriageReasoning,
        action: TriageAction
    ) -> bool:
        """
        Store learning record in PostgreSQL.
        
        Returns:
            True if storage succeeded, False otherwise
        """
        try:
            # Prepare input data
            input_data = {
                'resource_type': context.resource_type,
                'current_value': context.current_value,
                'threshold': context.threshold,
                'severity': context.severity,
                'data_quality_score': context.data_quality_score,
                'monocle_yeets': context.monocle_yeet_count,
                'similar_triages_count': len(context.similar_triages),
                'recent_escalations_count': len(context.recent_escalations)
            }
            
            # Prepare output data
            output_data = {
                'action_type': action.action_type,
                'should_escalate': reasoning.should_escalate,
                'target_specialist': action.target_agent,
                'risk_level': reasoning.risk_level,
                'priority': action.priority,
                'monocle_state': action.monocle_state,
                'aristocratic_confidence': action.aristocratic_confidence,
                'reasoning_summary': action.reasoning_summary
            }
            
            # Create database record — only columns that exist in the live DB schema
            db_record = AgentLearningRecord(
                agent_name='sir_hawkington',
                fingerprint_l1=context.resource_type,
                fingerprint_l2=f"{context.resource_type}_{context.severity}",
                fingerprint_l3=f"{context.resource_type}_{context.severity}_{action.action_type}",
                resource_type=context.resource_type,
                severity=context.severity,
                action=action.action_type,
                parameters=output_data,
                confidence=action.confidence,
                success=learning_record.success if learning_record.success is not None else False,
                root_cause=reasoning.primary_reason
            )
            
            self.db.add(db_record)
            await self.db.commit()
            
            learning_record.learning_record_id = str(db_record.id)
            logger.debug(f"🧐💾 Learning record stored in database (ID: {db_record.id})")
            return True
            
        except Exception as e:
            logger.error(f"🧐💥 Error storing learning record: {e}")
            await self.db.rollback()
            return False
    
    async def update_outcome(
        self,
        learning_record: HawkLearningRecord,
        success: bool,
        outcome_notes: Optional[str] = None
    ):
        """
        Update a learning record with outcome information.
        
        This is called after the action has been executed and we know if it succeeded.
        """
        learning_record.success = success
        learning_record.outcome_notes = outcome_notes
        
        logger.info(
            f"🧐📝 Updated learning record: success={success}, "
            f"notes={outcome_notes or 'none'}"
        )
        
        # TODO: Update database record with outcome
        # This requires querying by timestamp and updating the success field
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get learning statistics for Sir Hawkington.
        
        Returns:
            Dictionary with learning metrics
        """
        try:
            from sqlalchemy import func, select
            
            # Query learning records
            query = select(
                func.count(AgentLearningRecord.id).label('total_decisions'),
                func.avg(AgentLearningRecord.confidence).label('avg_confidence'),
                func.sum(
                    func.cast(AgentLearningRecord.success, func.Integer())
                ).label('successful_decisions')
            ).where(
                AgentLearningRecord.agent_name == 'sir_hawkington'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            total = row.total_decisions or 0
            avg_conf = float(row.avg_confidence or 0.0)
            successful = row.successful_decisions or 0
            
            success_rate = (successful / total) if total > 0 else 0.0
            
            stats = {
                'total_triage_decisions': total,
                'average_confidence': avg_conf,
                'success_rate': success_rate,
                'successful_decisions': successful
            }
            
            logger.info(
                f"🧐📊 Learning stats: {total} decisions, "
                f"{success_rate:.1%} success rate, "
                f"{avg_conf:.2f} avg confidence"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"🧐💥 Error getting learning stats: {e}")
            return {
                'total_triage_decisions': 0,
                'average_confidence': 0.0,
                'success_rate': 0.0,
                'successful_decisions': 0
            }
