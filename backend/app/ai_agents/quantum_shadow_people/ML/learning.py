#!/usr/bin/env python3
"""
QSP (Quantum Shadow People) Learning Layer - Quantum Security Optimization

Stores and learns from:
- Security response decisions and outcomes
- Quantum state patterns vs threat types
- Existential dread correlation with accuracy
- Hamster communication effectiveness
- Threat detection accuracy

This enables QSP to improve quantum security assessment over time.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_learning import AgentLearningRecord
from .perception import QSPPerceptionContext
from .reasoning import SecurityReasoning
from .action_selection import SecurityResponseAction

logger = logging.getLogger('QSPLearning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class QSPLearningRecord:
    """Record of a security response decision for learning"""
    
    # Input context
    threat_count: int
    highest_severity: str
    threat_classification: str
    
    # Quantum state (personality)
    quantum_state: str
    existential_dread_level: float
    quantum_coherence: float
    
    # Decision
    response_type: str
    response_strategy: str
    confidence: float
    
    # Hamster communication
    quantum_messages_sent: int
    hamster_assistance_requested: bool
    
    # Risk assessment
    risk_level: str
    
    # Outcome (filled in later)
    success: Optional[bool] = None
    threat_resolved: Optional[bool] = None
    false_positive: Optional[bool] = None
    outcome_notes: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=utc_now)


class QSPLearning:
    """
    QSP's learning layer for improving quantum security assessment.
    
    👻 "Recording quantum observation for future pattern recognition..."
    """
    
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        
    async def learn(
        self,
        context: QSPPerceptionContext,
        reasoning: SecurityReasoning,
        action: SecurityResponseAction,
        outcome_success: Optional[bool] = None
    ) -> QSPLearningRecord:
        """
        Store security response decision for learning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            action: Selected action
            outcome_success: Whether the response was successful (if known)
            
        Returns:
            QSPLearningRecord that was stored
        """
        logger.info(f"👻📚 Recording quantum security response for learning...")
        
        # Create learning record
        learning_record = QSPLearningRecord(
            threat_count=context.threat_count,
            highest_severity=context.highest_severity,
            threat_classification=reasoning.threat_classification,
            quantum_state=action.quantum_state,
            existential_dread_level=action.existential_dread_level,
            quantum_coherence=action.quantum_coherence,
            response_type=action.action_type,
            response_strategy=action.response_strategy,
            confidence=action.confidence,
            quantum_messages_sent=action.quantum_messages_sent,
            hamster_assistance_requested=action.hamster_assistance_requested,
            risk_level=reasoning.risk_level,
            success=outcome_success
        )
        
        # Store in database
        await self._store_in_database(learning_record, context, reasoning, action)
        
        logger.info(
            f"👻✅ Learning recorded: {action.action_type}, "
            f"quantum_state={action.quantum_state}, dread={action.existential_dread_level:.2f}"
        )
        
        return learning_record
    
    async def _store_in_database(
        self,
        learning_record: QSPLearningRecord,
        context: QSPPerceptionContext,
        reasoning: SecurityReasoning,
        action: SecurityResponseAction
    ):
        """
        Store learning record in PostgreSQL.
        """
        try:
            # Create hierarchical fingerprints for security responses
            fingerprint_l1 = f"{context.resource_type}"
            fingerprint_l2 = f"{context.resource_type}_{context.severity}"
            fingerprint_l3 = f"{context.resource_type}_{context.severity}_{action.action_type}"
            
            # Prepare parameters with all context and action details
            parameters = {
                'threat_count': context.threat_count,
                'highest_severity': context.highest_severity,
                'network_anomalies': context.network_anomalies,
                'suspicious_connections': context.suspicious_connections,
                'failed_auth_attempts': context.failed_auth_attempts,
                'threat_assessment_confidence': context.threat_assessment_confidence,
                'response_urgency': context.response_urgency,
                'response_type': action.action_type,
                'response_strategy': action.response_strategy,
                'priority': action.priority,
                'quantum_state': action.quantum_state,
                'existential_dread_level': action.existential_dread_level,
                'quantum_coherence': action.quantum_coherence,
                'threat_classification': reasoning.threat_classification,
                'hamster_assistance_requested': action.hamster_assistance_requested,
                'requires_escalation': action.requires_escalation,
                'estimated_resolution_time': action.estimated_resolution_time,
                'threat_indicators': reasoning.threat_indicators,
                'historical_precedent': reasoning.historical_precedent,
                'similar_threat_count': reasoning.similar_threat_count
            }
            
            # Prepare improvement metrics
            improvement = {
                'action_type': action.action_type,
                'quantum_state': action.quantum_state
            }
            
            # Create database record
            db_record = AgentLearningRecord(
                agent_name='quantum_shadow_people',
                fingerprint_l1=fingerprint_l1,
                fingerprint_l2=fingerprint_l2,
                fingerprint_l3=fingerprint_l3,
                resource_type=context.resource_type,
                severity=context.severity,
                root_cause=reasoning.root_cause,
                process_category='security',
                action=action.action_type,
                parameters=parameters,
                confidence=action.confidence,
                followed_vic20=True,  # QSP follows VIC-20's routing
                success=learning_record.success if learning_record.success is not None else True,
                improvement=improvement,
                what_worked=reasoning.root_cause if learning_record.success else None,
                what_failed=None if learning_record.success else reasoning.root_cause
            )
            
            self.db.add(db_record)
            await self.db.commit()
            
            logger.debug("Learning record stored in database")
            
        except Exception as e:
            logger.error(f"👻💥 Error storing learning record: {e}")
            await self.db.rollback()
    
    async def update_outcome(
        self,
        learning_record: QSPLearningRecord,
        success: bool,
        threat_resolved: bool,
        false_positive: bool = False,
        outcome_notes: Optional[str] = None
    ):
        """
        Update a learning record with outcome information.
        
        This is called after the response executes and we know if it succeeded.
        """
        learning_record.success = success
        learning_record.threat_resolved = threat_resolved
        learning_record.false_positive = false_positive
        learning_record.outcome_notes = outcome_notes
        
        logger.info(
            f"👻📝 Updated learning record: success={success}, "
            f"resolved={threat_resolved}, false_positive={false_positive}"
        )
        
        # TODO: Update database record with outcome
        # This requires querying by timestamp and updating the success field
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get learning statistics for QSP.
        
        Returns:
            Dictionary with learning metrics including quantum state correlations
        """
        try:
            from sqlalchemy import func, select
            
            # Query learning records
            query = select(
                func.count(AgentLearningRecord.id).label('total_responses'),
                func.avg(AgentLearningRecord.confidence).label('avg_confidence'),
                func.sum(
                    func.cast(AgentLearningRecord.success, func.Integer())
                ).label('successful_responses')
            ).where(
                AgentLearningRecord.agent_name == 'quantum_shadow_people'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            total = row.total_responses or 0
            avg_conf = float(row.avg_confidence or 0.0)
            successful = row.successful_responses or 0
            
            success_rate = (successful / total) if total > 0 else 0.0
            
            # Get quantum state stats
            quantum_stats = await self._get_quantum_state_stats()
            
            # Get threat detection stats
            threat_stats = await self._get_threat_detection_stats()
            
            stats = {
                'total_security_responses': total,
                'average_response_confidence': avg_conf,
                'response_success_rate': success_rate,
                'successful_responses': successful,
                'quantum_state_metrics': quantum_stats,
                'threat_detection_metrics': threat_stats
            }
            
            logger.info(
                f"👻📊 Learning stats: {total} responses, "
                f"{success_rate:.1%} success rate, "
                f"{avg_conf:.2f} avg confidence"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"👻💥 Error getting learning stats: {e}")
            return {
                'total_security_responses': 0,
                'average_response_confidence': 0.0,
                'response_success_rate': 0.0,
                'successful_responses': 0,
                'quantum_state_metrics': {},
                'threat_detection_metrics': {}
            }
    
    async def _get_quantum_state_stats(self) -> Dict[str, Any]:
        """
        Get quantum state statistics (personality behavior tracking).
        """
        try:
            from sqlalchemy import select, func
            
            # Query for quantum state averages
            query = select(
                func.avg(
                    AgentLearningRecord.output_data['existential_dread_level'].astext.cast(func.Float)
                ).label('avg_dread'),
                func.avg(
                    AgentLearningRecord.output_data['quantum_coherence'].astext.cast(func.Float)
                ).label('avg_coherence'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['quantum_state'].astext == 'collapsed', 1)
                    )
                ).label('collapsed_count'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['quantum_state'].astext == 'fluctuating', 1)
                    )
                ).label('fluctuating_count'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['quantum_state'].astext == 'stable', 1)
                    )
                ).label('stable_count')
            ).where(
                AgentLearningRecord.agent_name == 'quantum_shadow_people'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            return {
                'average_existential_dread': float(row.avg_dread or 0.0),
                'average_quantum_coherence': float(row.avg_coherence or 0.0),
                'collapsed_state_count': row.collapsed_count or 0,
                'fluctuating_state_count': row.fluctuating_count or 0,
                'stable_state_count': row.stable_count or 0
            }
            
        except Exception as e:
            logger.error(f"👻💥 Error getting quantum state stats: {e}")
            return {}
    
    async def _get_threat_detection_stats(self) -> Dict[str, Any]:
        """
        Get threat detection statistics.
        """
        try:
            from sqlalchemy import select, func
            
            # Query for threat detection metrics
            query = select(
                func.avg(
                    AgentLearningRecord.input_data['threat_count'].astext.cast(func.Integer)
                ).label('avg_threats_per_incident'),
                func.count(
                    func.case(
                        (AgentLearningRecord.output_data['hamster_assistance_requested'].astext == 'true', 1)
                    )
                ).label('hamster_assistance_count')
            ).where(
                AgentLearningRecord.agent_name == 'quantum_shadow_people'
            )
            
            result = await self.db.execute(query)
            row = result.first()
            
            return {
                'average_threats_per_incident': float(row.avg_threats_per_incident or 0.0),
                'hamster_assistance_requests': row.hamster_assistance_count or 0
            }
            
        except Exception as e:
            logger.error(f"👻💥 Error getting threat detection stats: {e}")
            return {}
