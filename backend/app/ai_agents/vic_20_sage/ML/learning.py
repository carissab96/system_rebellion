#!/usr/bin/env python3
"""
VIC-20's Learning Layer - Coordination Routing Optimization

Stores and learns from:
- Routing decisions and outcomes
- Specialist performance by resource type
- Coordination success rates
- Response times and effectiveness

This enables VIC-20 to improve routing accuracy over time.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_learning import AgentLearningRecord
from .perception import VIC20PerceptionContext
from .reasoning import CoordinationReasoning
from .action_selection import CoordinationAction

logger = logging.getLogger('VIC20Learning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class VIC20LearningRecord:
    """Record of a coordination routing decision for learning"""
    
    # Input context
    resource_type: str
    current_value: float
    threshold: float
    severity: str
    hawk_confidence: float
    
    # Routing decision
    target_specialist: str
    routing_confidence: float
    recommended_action: str
    
    # Reasoning
    urgency_level: str
    specialist_success_rate: float
    primary_reason: str
    
    # Coordination details
    coordination_strategy: str
    fallback_specialists: list[str]
    
    # Outcome (filled in later)
    success: Optional[bool] = None
    specialist_response_time: Optional[float] = None
    outcome_notes: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=utc_now)


class VIC20Learning:
    """
    VIC-20's learning layer for improving coordination routing.
    
    🖥️ "Recording coordination outcome for future optimization..."
    """
    
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        
    async def learn(
        self,
        context: VIC20PerceptionContext,
        reasoning: CoordinationReasoning,
        action: CoordinationAction,
        outcome_success: Optional[bool] = None
    ) -> VIC20LearningRecord:
        """
        Store coordination routing decision for learning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            action: Selected action
            outcome_success: Whether the coordination was successful (if known)
            
        Returns:
            VIC20LearningRecord that was stored
        """
        logger.info(f"🖥️📚 Recording coordination routing for learning...")
        
        # Create learning record
        learning_record = VIC20LearningRecord(
            resource_type=context.resource_type,
            current_value=context.current_value,
            threshold=context.threshold,
            severity=context.severity,
            hawk_confidence=context.hawk_confidence,
            target_specialist=action.target_specialist,
            routing_confidence=action.confidence,
            recommended_action=action.recommended_action,
            urgency_level=reasoning.urgency_level,
            specialist_success_rate=reasoning.specialist_success_rate,
            primary_reason=reasoning.primary_reason,
            coordination_strategy=action.coordination_strategy,
            fallback_specialists=action.fallback_specialists,
            success=outcome_success
        )
        
        # Store in database
        await self._store_in_database(learning_record, context, reasoning, action)
        
        logger.info(
            f"🖥️✅ Learning recorded: routed to {action.target_specialist}, "
            f"confidence={action.confidence:.2f}"
        )
        
        return learning_record
    
    async def _store_in_database(
        self,
        learning_record: VIC20LearningRecord,
        context: VIC20PerceptionContext,
        reasoning: CoordinationReasoning,
        action: CoordinationAction
    ):
        """
        Store learning record in PostgreSQL.
        """
        try:
            # Create hierarchical fingerprints for coordination routing
            fingerprint_l1 = f"{context.resource_type}"
            fingerprint_l2 = f"{context.resource_type}_{context.severity}"
            fingerprint_l3 = f"{context.resource_type}_{context.severity}_{action.target_specialist}"
            
            # Prepare parameters with all context
            parameters = {
                'current_value': context.current_value,
                'threshold': context.threshold,
                'hawk_confidence': context.hawk_confidence,
                'system_load': context.system_load,
                'active_alerts': context.active_alerts,
                'available_specialists_count': len(context.available_specialists),
                'target_specialist': action.target_specialist,
                'routing_confidence': action.confidence,
                'recommended_action': action.recommended_action,
                'urgency_level': reasoning.urgency_level,
                'coordination_strategy': action.coordination_strategy,
                'fallback_specialists': action.fallback_specialists,
                'specialist_success_rate': reasoning.specialist_success_rate,
                'specialist_load': reasoning.specialist_load
            }
            
            # Prepare improvement metrics (will be filled in when outcome is known)
            improvement = {
                'routed_to': action.target_specialist,
                'routing_confidence': action.confidence
            }
            
            # Create database record
            db_record = AgentLearningRecord(
                agent_name='vic20_sage',
                fingerprint_l1=fingerprint_l1,
                fingerprint_l2=fingerprint_l2,
                fingerprint_l3=fingerprint_l3,
                resource_type=context.resource_type,
                severity=context.severity,
                root_cause=reasoning.primary_reason,
                process_category='coordination',
                action=action.target_specialist,
                parameters=parameters,
                confidence=action.confidence,
                followed_vic20=False,  # VIC-20 IS the coordinator
                success=learning_record.success if learning_record.success is not None else True,
                improvement=improvement,
                what_worked=reasoning.primary_reason if learning_record.success else None,
                what_failed=None if learning_record.success else reasoning.primary_reason
            )
            
            self.db.add(db_record)
            await self.db.commit()
            
            logger.debug("🖥️💾 Learning record stored in database")
            
        except Exception as e:
            logger.error(f"🖥️💥 Error storing learning record: {e}")
            await self.db.rollback()
    
    async def update_outcome(
        self,
        learning_record: VIC20LearningRecord,
        success: bool,
        response_time: Optional[float] = None,
        outcome_notes: Optional[str] = None
    ):
        """
        Update a learning record with outcome information.
        
        This is called after the specialist responds and we know if it succeeded.
        """
        learning_record.success = success
        learning_record.specialist_response_time = response_time
        learning_record.outcome_notes = outcome_notes
        
        logger.info(
            f"🖥️📝 Updated learning record: success={success}, "
            f"response_time={response_time}s, notes={outcome_notes or 'none'}"
        )
        
        # TODO: Update database record with outcome
        # This requires querying by timestamp and updating the success field
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get learning statistics for VIC-20.
        
        Returns:
            Dictionary with learning metrics
        """
        try:
            from sqlalchemy import func, select
            
            # Query learning records
            query = select(
                func.count(AgentLearningRecord.id).label('total_routings'),
                func.avg(AgentLearningRecord.confidence).label('avg_confidence'),
                func.sum(
                    func.cast(AgentLearningRecord.success, func.Integer())
                ).label('successful_routings')
            ).where(
                AgentLearningRecord.agent_name == 'vic20_sage'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            total = row.total_routings or 0
            avg_conf = float(row.avg_confidence or 0.0)
            successful = row.successful_routings or 0
            
            success_rate = (successful / total) if total > 0 else 0.0
            
            # Get specialist-specific stats
            specialist_stats = await self._get_specialist_stats()
            
            stats = {
                'total_coordination_routings': total,
                'average_routing_confidence': avg_conf,
                'routing_success_rate': success_rate,
                'successful_routings': successful,
                'specialist_performance': specialist_stats
            }
            
            logger.info(
                f"🖥️📊 Learning stats: {total} routings, "
                f"{success_rate:.1%} success rate, "
                f"{avg_conf:.2f} avg confidence"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"🖥️💥 Error getting learning stats: {e}")
            return {
                'total_coordination_routings': 0,
                'average_routing_confidence': 0.0,
                'routing_success_rate': 0.0,
                'successful_routings': 0,
                'specialist_performance': {}
            }
    
    async def _get_specialist_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance stats for each specialist.
        """
        try:
            from sqlalchemy import select, func
            
            # Query routings grouped by specialist
            query = select(
                AgentLearningRecord.output_data['target_specialist'].label('specialist'),
                func.count(AgentLearningRecord.id).label('total'),
                func.sum(
                    func.cast(AgentLearningRecord.success, func.Integer())
                ).label('successful'),
                func.avg(AgentLearningRecord.confidence).label('avg_confidence')
            ).where(
                AgentLearningRecord.agent_name == 'vic20_sage'
            ).group_by(
                AgentLearningRecord.output_data['target_specialist']
            )
            
            result = await self.db.execute(query)
            rows = result.all()
            
            specialist_stats = {}
            for row in rows:
                specialist = row.specialist
                if specialist:
                    total = row.total or 0
                    successful = row.successful or 0
                    success_rate = (successful / total) if total > 0 else 0.0
                    
                    specialist_stats[specialist] = {
                        'total_routings': total,
                        'successful_routings': successful,
                        'success_rate': success_rate,
                        'avg_confidence': float(row.avg_confidence or 0.0)
                    }
            
            return specialist_stats
            
        except Exception as e:
            logger.error(f"🖥️💥 Error getting specialist stats: {e}")
            return {}
