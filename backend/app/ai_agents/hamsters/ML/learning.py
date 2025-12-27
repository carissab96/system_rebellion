#!/usr/bin/env python3
"""
Hamsters' Learning Layer - Telepathic Consensus Optimization

Stores and learns from:
- Storage fix decisions and outcomes
- Individual hamster assessments (Steve, Bob, Carl)
- Beer consumption patterns vs complexity
- Duct tape usage vs job type
- Sudo operation success rates
- Bob's chaos correlation with success

This enables the Hamsters to improve their telepathic consensus over time.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_learning import AgentLearningRecord
from .perception import HamstersPerceptionContext
from .reasoning import StorageReasoning
from .action_selection import StorageFixAction

logger = logging.getLogger('HamstersLearning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class HamstersLearningRecord:
    """Record of a storage fix decision for learning"""
    
    # Input context
    disk_usage_percent: float
    fragmentation_level: float
    complexity_level: float
    ingenuity_required: float
    
    # Consensus decision
    consensus_fix: str
    consensus_confidence: float
    requires_sudo: bool
    
    # Individual assessments
    steve_recommendation: str
    bob_recommendation: str
    carl_recommendation: str
    steve_agreed: bool
    bob_agreed: bool
    carl_agreed: bool
    disagreement_level: float
    
    # Personality behaviors
    total_beers_consumed: int
    steve_beers: int
    bob_beers: int
    carl_beers: int
    duct_tape_rolls: float
    duct_tape_job_complexity: str
    bob_at_cupboard: bool
    
    # Execution details
    action_type: str
    sudo_command: Optional[str]
    execution_strategy: str
    
    # Outcome (filled in later)
    success: Optional[bool] = None
    execution_time_seconds: Optional[float] = None
    outcome_notes: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=utc_now)
    learning_record_id: Optional[str] = None  # Database ID after storage
    storage_success: bool = False  # Whether database storage succeeded
    situation_fingerprint: Optional[str] = None  # Generated fingerprint for this situation


class HamstersLearning:
    """
    Hamsters' learning layer for improving telepathic consensus.
    
    🐹🐹🐹 "Recording consensus outcome for future beer calculations..."
    """
    
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        
    async def learn(
        self,
        context: HamstersPerceptionContext,
        reasoning: StorageReasoning,
        action: StorageFixAction,
        outcome_success: Optional[bool] = None
    ) -> HamstersLearningRecord:
        """
        Store storage fix decision for learning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            action: Selected action
            outcome_success: Whether the fix was successful (if known)
            
        Returns:
            HamstersLearningRecord that was stored
        """
        logger.info(f"🐹📚 Recording telepathic consensus for learning...")
        
        # Create learning record
        learning_record = HamstersLearningRecord(
            disk_usage_percent=context.disk_usage_percent,
            fragmentation_level=context.fragmentation_level,
            complexity_level=context.complexity_level,
            ingenuity_required=context.ingenuity_required,
            consensus_fix=action.consensus_fix,
            consensus_confidence=action.confidence,
            requires_sudo=action.requires_sudo,
            steve_recommendation=reasoning.steve_assessment.recommended_fix,
            bob_recommendation=reasoning.bob_assessment.recommended_fix,
            carl_recommendation=reasoning.carl_assessment.recommended_fix,
            steve_agreed=action.steve_agreed,
            bob_agreed=action.bob_agreed,
            carl_agreed=action.carl_agreed,
            disagreement_level=action.disagreement_level,
            total_beers_consumed=action.total_beers_consumed,
            steve_beers=action.steve_beers,
            bob_beers=action.bob_beers,
            carl_beers=action.carl_beers,
            duct_tape_rolls=action.duct_tape_rolls,
            duct_tape_job_complexity=action.duct_tape_breakdown.job_complexity,
            bob_at_cupboard=action.bob_at_cupboard,
            action_type=action.action_type,
            sudo_command=action.sudo_command,
            execution_strategy=action.execution_strategy,
            success=outcome_success
        )
        
        # Store in database
        storage_success = await self._store_in_database(learning_record, context, reasoning, action)
        learning_record.storage_success = storage_success
        
        # Set fingerprint for emission
        learning_record.situation_fingerprint = f"{context.resource_type}_{context.severity}_{action.action_type}"
        
        logger.info(
            f"🐹✅ Learning recorded: {action.action_type}, "
            f"beers={action.total_beers_consumed}, duct_tape={action.duct_tape_rolls:.1f} rolls"
        )
        
        return learning_record
    
    async def _store_in_database(
        self,
        learning_record: HamstersLearningRecord,
        context: HamstersPerceptionContext,
        reasoning: StorageReasoning,
        action: StorageFixAction
    ) -> bool:
        """
        Store learning record in PostgreSQL.
        
        Returns:
            True if storage succeeded, False otherwise
        """
        try:
            # Create hierarchical fingerprints for storage fixes
            fingerprint_l1 = f"{context.resource_type}"
            fingerprint_l2 = f"{context.resource_type}_{context.severity}"
            fingerprint_l3 = f"{context.resource_type}_{context.severity}_{action.action_type}"
            
            # Prepare parameters with all context and action details
            parameters = {
                'disk_usage_percent': context.disk_usage_percent,
                'fragmentation_level': context.fragmentation_level,
                'available_space_gb': context.available_space_gb,
                'inode_usage_percent': context.inode_usage_percent,
                'complexity_level': context.complexity_level,
                'ingenuity_required': context.ingenuity_required,
                'consensus_fix': action.consensus_fix,
                'action_type': action.action_type,
                'requires_sudo': action.requires_sudo,
                'sudo_command': action.sudo_command,
                'execution_strategy': action.execution_strategy,
                'total_beers_consumed': action.total_beers_consumed,
                'duct_tape_rolls': action.duct_tape_rolls,
                'steve_beers': action.steve_beers,
                'bob_beers': action.bob_beers,
                'carl_beers': action.carl_beers,
                'steve_agreed': action.steve_agreed,
                'bob_agreed': action.bob_agreed,
                'carl_agreed': action.carl_agreed,
                'consensus_strength': action.consensus_strength,
                'disagreement_level': action.disagreement_level,
                'bob_at_cupboard': action.bob_at_cupboard,
                'stick_panic_alert': action.stick_panic_alert,
                'risk_level': reasoning.risk_level,
                'urgency': reasoning.urgency
            }
            
            # Prepare improvement metrics (space freed)
            improvement = {
                'estimated_space_freed_mb': action.estimated_space_freed,
                'action_type': action.action_type
            }
            
            # Create database record
            db_record = AgentLearningRecord(
                agent_name='hamsters',
                fingerprint_l1=fingerprint_l1,
                fingerprint_l2=fingerprint_l2,
                fingerprint_l3=fingerprint_l3,
                resource_type=context.resource_type,
                severity=context.severity,
                root_cause=reasoning.root_cause,
                process_category='storage',
                action=action.action_type,
                parameters=parameters,
                confidence=action.confidence,
                followed_vic20=True,  # Hamsters follow VIC-20's routing
                success=learning_record.success if learning_record.success is not None else True,
                improvement=improvement,
                what_worked=reasoning.root_cause if learning_record.success else None,
                what_failed=None if learning_record.success else reasoning.root_cause
            )
            
            self.db.add(db_record)
            await self.db.commit()
            
            # Set the ID on the record so we can emit it
            learning_record.learning_record_id = str(db_record.id)
            
            logger.debug(f"🐹💾 Learning record stored in database (ID: {db_record.id})")
            return True
            
        except Exception as e:
            logger.error(f"🐹❌ Failed to store learning record: {e}")
            await self.db.rollback()
            return False
    
    async def update_outcome(
        self,
        learning_record: HamstersLearningRecord,
        success: bool,
        execution_time: Optional[float] = None,
        outcome_notes: Optional[str] = None
    ):
        """
        Update a learning record with outcome information.
        
        This is called after the fix executes and we know if it succeeded.
        """
        learning_record.success = success
        learning_record.execution_time_seconds = execution_time
        learning_record.outcome_notes = outcome_notes
        
        logger.info(
            f"🐹📝 Updated learning record: success={success}, "
            f"execution_time={execution_time}s, notes={outcome_notes or 'none'}"
        )
        
        # TODO: Update database record with outcome
        # This requires querying by timestamp and updating the success field
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get learning statistics for the Hamsters.
        
        Returns:
            Dictionary with learning metrics including beer/duct tape correlations
        """
        try:
            from sqlalchemy import func, select
            
            # Query learning records
            query = select(
                func.count(AgentLearningRecord.id).label('total_fixes'),
                func.avg(AgentLearningRecord.confidence).label('avg_confidence'),
                func.sum(
                    func.cast(AgentLearningRecord.success, func.Integer())
                ).label('successful_fixes')
            ).where(
                AgentLearningRecord.agent_name == 'hamsters'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            total = row.total_fixes or 0
            avg_conf = float(row.avg_confidence or 0.0)
            successful = row.successful_fixes or 0
            
            success_rate = (successful / total) if total > 0 else 0.0
            
            # Get beer/duct tape stats
            beer_duct_tape_stats = await self._get_beer_duct_tape_stats()
            
            # Get consensus stats
            consensus_stats = await self._get_consensus_stats()
            
            stats = {
                'total_storage_fixes': total,
                'average_fix_confidence': avg_conf,
                'fix_success_rate': success_rate,
                'successful_fixes': successful,
                'beer_consumption': beer_duct_tape_stats['beer'],
                'duct_tape_usage': beer_duct_tape_stats['duct_tape'],
                'consensus_metrics': consensus_stats
            }
            
            logger.info(
                f"🐹📊 Learning stats: {total} fixes, "
                f"{success_rate:.1%} success rate, "
                f"{avg_conf:.2f} avg confidence"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"🐹💥 Error getting learning stats: {e}")
            return {
                'total_storage_fixes': 0,
                'average_fix_confidence': 0.0,
                'fix_success_rate': 0.0,
                'successful_fixes': 0,
                'beer_consumption': {},
                'duct_tape_usage': {},
                'consensus_metrics': {}
            }
    
    async def _get_beer_duct_tape_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get beer consumption and duct tape usage statistics.
        """
        try:
            from sqlalchemy import select, func
            
            # Query for beer and duct tape averages
            query = select(
                func.avg(
                    AgentLearningRecord.output_data['total_beers_consumed'].astext.cast(func.Float)
                ).label('avg_beers'),
                func.avg(
                    AgentLearningRecord.output_data['duct_tape_rolls'].astext.cast(func.Float)
                ).label('avg_duct_tape'),
                func.sum(
                    AgentLearningRecord.output_data['steve_beers'].astext.cast(func.Integer)
                ).label('steve_total_beers'),
                func.sum(
                    AgentLearningRecord.output_data['bob_beers'].astext.cast(func.Integer)
                ).label('bob_total_beers'),
                func.sum(
                    AgentLearningRecord.output_data['carl_beers'].astext.cast(func.Integer)
                ).label('carl_total_beers')
            ).where(
                AgentLearningRecord.agent_name == 'hamsters'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            return {
                'beer': {
                    'average_per_fix': float(row.avg_beers or 0.0),
                    'steve_total': row.steve_total_beers or 0,
                    'bob_total': row.bob_total_beers or 0,
                    'carl_total': row.carl_total_beers or 0
                },
                'duct_tape': {
                    'average_rolls_per_fix': float(row.avg_duct_tape or 0.0)
                }
            }
            
        except Exception as e:
            logger.error(f"🐹💥 Error getting beer/duct tape stats: {e}")
            return {'beer': {}, 'duct_tape': {}}
    
    async def _get_consensus_stats(self) -> Dict[str, Any]:
        """
        Get telepathic consensus statistics.
        """
        try:
            from sqlalchemy import select, func
            
            # Query for consensus metrics
            query = select(
                func.avg(
                    AgentLearningRecord.output_data['consensus_strength'].astext.cast(func.Float)
                ).label('avg_consensus_strength'),
                func.avg(
                    AgentLearningRecord.output_data['disagreement_level'].astext.cast(func.Float)
                ).label('avg_disagreement'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['steve_agreed'].astext == 'true', 1)
                    )
                ).label('steve_agreement_count'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['bob_agreed'].astext == 'true', 1)
                    )
                ).label('bob_agreement_count'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['carl_agreed'].astext == 'true', 1)
                    )
                ).label('carl_agreement_count')
            ).where(
                AgentLearningRecord.agent_name == 'hamsters'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            return {
                'average_consensus_strength': float(row.avg_consensus_strength or 0.0),
                'average_disagreement': float(row.avg_disagreement or 0.0),
                'steve_agreement_rate': row.steve_agreement_count or 0,
                'bob_agreement_rate': row.bob_agreement_count or 0,
                'carl_agreement_rate': row.carl_agreement_count or 0
            }
            
        except Exception as e:
            logger.error(f"🐹💥 Error getting consensus stats: {e}")
            return {}
