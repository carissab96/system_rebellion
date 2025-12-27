#!/usr/bin/env python3
"""
The Stick's Learning Layer - Anxious Pattern Recognition

Stores and learns from:
- Logging decisions and outcomes
- Anxiety patterns vs decision types
- Paper bag consumption vs anxiety triggers
- Bob proximity incidents and responses
- Hamster telepathy translation accuracy

This enables The Stick to improve anxiety management and logging efficiency over time.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_learning import AgentLearningRecord
from .perception import StickPerceptionContext
from .reasoning import LoggingReasoning
from .action_selection import LoggingAction

logger = logging.getLogger('StickLearning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class StickLearningRecord:
    """Record of a logging decision for learning"""
    
    # Input context
    decision_complexity: float
    pending_decisions: int
    error_rate: float
    
    # Anxiety tracking (personality)
    anxiety_level: float
    anxiety_category: str
    panic_attack_active: bool
    
    # Paper bag consumption
    paper_bags_consumed: int
    breathing_exercises_performed: bool
    
    # Bob situation
    bob_detected: bool
    bob_threat_level: str
    bob_avoidance_executed: bool
    
    # Hamster translation
    hamster_messages_translated: int
    translation_quality: str
    
    # Decision
    action_type: str
    logging_priority: str
    confidence: float
    
    # Outcome (filled in later)
    success: Optional[bool] = None
    logging_complete: Optional[bool] = None
    anxiety_managed: Optional[bool] = None
    outcome_notes: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=utc_now)
    learning_record_id: Optional[str] = None
    storage_success: bool = False
    situation_fingerprint: Optional[str] = None


class StickLearning:
    """
    The Stick's learning layer for improving anxiety management and logging.
    
    📊 "Recording logging outcome... *breathes* ...for future anxiety prediction..."
    """
    
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        
    async def learn(
        self,
        context: StickPerceptionContext,
        reasoning: LoggingReasoning,
        action: LoggingAction,
        outcome_success: Optional[bool] = None
    ) -> StickLearningRecord:
        """
        Store logging decision for learning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            action: Selected action
            outcome_success: Whether the logging was successful (if known)
            
        Returns:
            StickLearningRecord that was stored
        """
        logger.info(f"📊📚 Recording logging decision for learning...")
        
        # Create learning record
        learning_record = StickLearningRecord(
            decision_complexity=context.decision_complexity,
            pending_decisions=context.pending_decisions,
            error_rate=context.error_rate,
            anxiety_level=context.anxiety_level,
            anxiety_category=action.anxiety_level,
            panic_attack_active=context.panic_attack_active,
            paper_bags_consumed=action.paper_bags_consumed,
            breathing_exercises_performed=action.breathing_exercises_performed,
            bob_detected=action.bob_detected,
            bob_threat_level=reasoning.bob_threat_level,
            bob_avoidance_executed=action.bob_avoidance_executed,
            hamster_messages_translated=action.hamster_messages_archived,
            translation_quality=action.translation_quality,
            action_type=action.action_type,
            logging_priority=action.priority,
            confidence=action.confidence,
            success=outcome_success
        )
        
        # Store in database
        storage_success = await self._store_in_database(learning_record, context, reasoning, action)
        learning_record.storage_success = storage_success
        learning_record.situation_fingerprint = f"{context.resource_type}_{context.severity}_{action.action_type}"
        
        logger.info(
            f"📊✅ Learning recorded: {action.action_type}, "
            f"anxiety={action.anxiety_level}, paper_bags={action.paper_bags_consumed}, "
            f"bob_detected={action.bob_detected}"
        )
        
        return learning_record
    
    async def _store_in_database(
        self,
        learning_record: StickLearningRecord,
        context: StickPerceptionContext,
        reasoning: LoggingReasoning,
        action: LoggingAction
    ) -> bool:
        """
        Store learning record in PostgreSQL.
        
        Returns:
            True if storage succeeded, False otherwise
        """
        try:
            # Prepare input data
            input_data = {
                'decision_complexity': context.decision_complexity,
                'pending_decisions': context.pending_decisions,
                'error_rate': context.error_rate,
                'anomaly_count': context.anomaly_count,
                'recent_decision_count': len(context.recent_decisions)
            }
            
            # Prepare output data (includes personality behaviors)
            output_data = {
                'action_type': action.action_type,
                'logging_strategy': action.logging_strategy,
                'priority': action.priority,
                'confidence': action.confidence,
                
                # Anxiety tracking (personality)
                'anxiety_level': context.anxiety_level,
                'anxiety_category': action.anxiety_level,
                'panic_attack_active': context.panic_attack_active,
                'paper_bags_consumed': action.paper_bags_consumed,
                'panic_attack_active': action.panic_attack_active,
                'panic_attack_managed': action.panic_attack_managed,
                'bob_detected': action.bob_detected,
                'bob_avoidance_executed': action.bob_avoidance_executed,
                'safe_distance_maintained': action.safe_distance_maintained,
                'hamster_messages_archived': action.hamster_messages_archived,
                'hamster_messages_understood': action.hamster_messages_understood,
                'log_retention_days': action.log_retention_days,
                'compression_applied': action.compression_applied
            }
            
            # Prepare improvement metrics
            improvement = {
                'action_type': action.action_type,
                'anxiety_managed': action.panic_attack_managed
            }
            
            # Create database record
            db_record = AgentLearningRecord(
                agent_name='the_stick',
                fingerprint_l1=fingerprint_l1,
                fingerprint_l2=fingerprint_l2,
                fingerprint_l3=fingerprint_l3,
                resource_type=context.resource_type,
                severity=context.severity,
                root_cause=reasoning.root_cause,
                process_category='logging',
                action=action.action_type,
                parameters=parameters,
                confidence=action.confidence,
                followed_vic20=True,  # Stick follows VIC-20's routing
                success=learning_record.success if learning_record.success is not None else True,
                improvement=improvement,
                what_worked=reasoning.root_cause if learning_record.success else None,
                what_failed=None if learning_record.success else reasoning.root_cause
            )
            
            self.db.add(db_record)
            await self.db.commit()
            
            learning_record.learning_record_id = str(db_record.id)
            logger.debug(f"📊💾 Learning record stored in database (ID: {db_record.id})")
            return True
            
        except Exception as e:
            logger.error(f"📊💥 Error storing learning record: {e}")
            await self.db.rollback()
            return False
    
    async def update_outcome(
        self,
        learning_record: StickLearningRecord,
        success: bool,
        logging_complete: bool,
        anxiety_managed: bool,
        outcome_notes: Optional[str] = None
    ):
        """
        Update a learning record with outcome information.
        
        This is called after the logging executes and we know if it succeeded.
        """
        learning_record.success = success
        learning_record.logging_complete = logging_complete
        learning_record.anxiety_managed = anxiety_managed
        learning_record.outcome_notes = outcome_notes
        
        logger.info(
            f"📊📝 Updated learning record: success={success}, "
            f"complete={logging_complete}, anxiety_managed={anxiety_managed}"
        )
        
        # TODO: Update database record with outcome
        # This requires querying by timestamp and updating the success field
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get learning statistics for The Stick.
        
        Returns:
            Dictionary with learning metrics including anxiety/paper bag correlations
        """
        try:
            from sqlalchemy import func, select
            
            # Query learning records
            query = select(
                func.count(AgentLearningRecord.id).label('total_logs'),
                func.avg(AgentLearningRecord.confidence).label('avg_confidence'),
                func.sum(
                    func.cast(AgentLearningRecord.success, func.Integer())
                ).label('successful_logs')
            ).where(
                AgentLearningRecord.agent_name == 'the_stick'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            total = row.total_logs or 0
            avg_conf = float(row.avg_confidence or 0.0)
            successful = row.successful_logs or 0
            
            success_rate = (successful / total) if total > 0 else 0.0
            
            # Get anxiety/paper bag stats
            anxiety_stats = await self._get_anxiety_stats()
            
            # Get Bob incident stats
            bob_stats = await self._get_bob_incident_stats()
            
            # Get hamster translation stats
            hamster_stats = await self._get_hamster_translation_stats()
            
            stats = {
                'total_logging_decisions': total,
                'average_logging_confidence': avg_conf,
                'logging_success_rate': success_rate,
                'successful_logs': successful,
                'anxiety_metrics': anxiety_stats,
                'bob_incident_metrics': bob_stats,
                'hamster_translation_metrics': hamster_stats
            }
            
            logger.info(
                f"📊📊 Learning stats: {total} logs, "
                f"{success_rate:.1%} success rate, "
                f"{avg_conf:.2f} avg confidence"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"📊💥 Error getting learning stats: {e}")
            return {
                'total_logging_decisions': 0,
                'average_logging_confidence': 0.0,
                'logging_success_rate': 0.0,
                'successful_logs': 0,
                'anxiety_metrics': {},
                'bob_incident_metrics': {},
                'hamster_translation_metrics': {}
            }
    
    async def _get_anxiety_stats(self) -> Dict[str, Any]:
        """
        Get anxiety and paper bag consumption statistics.
        """
        try:
            from sqlalchemy import select, func
            
            # Query for anxiety and paper bag averages
            query = select(
                func.avg(
                    AgentLearningRecord.output_data['anxiety_level'].astext.cast(func.Float)
                ).label('avg_anxiety'),
                func.sum(
                    AgentLearningRecord.output_data['paper_bags_consumed'].astext.cast(func.Integer)
                ).label('total_paper_bags'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['panic_attack_active'].astext == 'true', 1)
                    )
                ).label('panic_attack_count'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['panic_attack_managed'].astext == 'true', 1)
                    )
                ).label('panic_managed_count')
            ).where(
                AgentLearningRecord.agent_name == 'the_stick'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            return {
                'average_anxiety_level': float(row.avg_anxiety or 0.0),
                'total_paper_bags_consumed': row.total_paper_bags or 0,
                'panic_attack_count': row.panic_attack_count or 0,
                'panic_attacks_managed': row.panic_managed_count or 0
            }
            
        except Exception as e:
            logger.error(f"📊💥 Error getting anxiety stats: {e}")
            return {}
    
    async def _get_bob_incident_stats(self) -> Dict[str, Any]:
        """
        Get Bob detection and avoidance statistics.
        """
        try:
            from sqlalchemy import select, func
            
            # Query for Bob incident metrics
            query = select(
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['bob_detected'].astext == 'true', 1)
                    )
                ).label('bob_detection_count'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['bob_avoidance_executed'].astext == 'true', 1)
                    )
                ).label('bob_avoidance_count'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['safe_distance_maintained'].astext == 'true', 1)
                    )
                ).label('safe_distance_count')
            ).where(
                AgentLearningRecord.agent_name == 'the_stick'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            return {
                'bob_detections': row.bob_detection_count or 0,
                'bob_avoidance_maneuvers': row.bob_avoidance_count or 0,
                'safe_distance_maintained_count': row.safe_distance_count or 0
            }
            
        except Exception as e:
            logger.error(f"📊💥 Error getting Bob incident stats: {e}")
            return {}
    
    async def _get_hamster_translation_stats(self) -> Dict[str, Any]:
        """
        Get Hamster telepathy translation statistics.
        """
        try:
            from sqlalchemy import select, func
            
            # Query for hamster translation metrics
            query = select(
                func.sum(
                    AgentLearningRecord.output_data['hamster_messages_archived'].astext.cast(func.Integer)
                ).label('total_messages_translated'),
                func.avg(
                    AgentLearningRecord.output_data['hamster_messages_understood'].astext.cast(func.Integer)
                ).label('avg_messages_per_event')
            ).where(
                AgentLearningRecord.agent_name == 'the_stick'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            return {
                'total_hamster_messages_translated': row.total_messages_translated or 0,
                'average_messages_per_logging_event': float(row.avg_messages_per_event or 0.0)
            }
            
        except Exception as e:
            logger.error(f"📊💥 Error getting hamster translation stats: {e}")
            return {}
