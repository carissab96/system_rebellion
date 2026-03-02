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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_learning import AgentLearningRecord
from .perception import QSPPerceptionContext
from .reasoning import SecurityReasoning
from .action_selection import SecurityResponseAction
from .situation_fingerprint import QSPSituationFingerprint

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
    severity_score: float = 0.0

    # Outcome (filled in later)
    success: Optional[bool] = None
    threat_resolved: Optional[bool] = None
    false_positive: Optional[bool] = None
    outcome_notes: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=utc_now)
    learning_record_id: Optional[str] = None  # Database ID after storage
    storage_success: bool = False  # Whether database storage succeeded
    situation_fingerprint: Optional[str] = None  # Generated fingerprint for this situation


class QSPLearning:
    """
    QSP's learning layer for improving quantum security assessment.
    
    👻 "Recording quantum observation for future pattern recognition..."
    """
    
    def __init__(self, db: AsyncSession, user_id: str, system_id: str = "default"):
        self.db = db
        self.user_id = user_id
        self.system_id = system_id
        
        # Initialize learned thresholds and action effectiveness
        from .learned_thresholds import LearnedThresholds
        from .action_effectiveness import ActionEffectivenessModel
        
        self.learned_thresholds = LearnedThresholds(db, system_id)
        self.action_effectiveness = ActionEffectivenessModel(db, system_id)
        
        logger.info("👻🧠 QSP learning with adaptive thresholds enabled!")
        
    async def learn(
        self,
        context: QSPPerceptionContext,
        reasoning: SecurityReasoning,
        action: SecurityResponseAction,
        outcome_success: Optional[bool] = None,
    ) -> QSPLearningRecord:
        """
        Store security response decision for learning.

        Args:
            context:        Perception context
            reasoning:      Reasoning analysis
            action:         Selected action
            outcome_success: Whether the response was successful (if known)

        Returns:
            QSPLearningRecord that was stored
        """
        logger.info("👻📚 Recording quantum security response for learning...")

        fingerprinter = QSPSituationFingerprint()
        fingerprints = fingerprinter.generate(
            resource_type=context.resource_type,
            severity=reasoning.severity_score,
            root_cause=reasoning.root_cause,
        )

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
            severity_score=reasoning.severity_score,
            success=outcome_success,
            situation_fingerprint=fingerprints['l3'],
        )

        storage_success = await self._store_in_database(
            learning_record, context, reasoning, action, fingerprints
        )
        learning_record.storage_success = storage_success

        logger.info(
            f"👻✅ Learning recorded: {action.action_type}, "
            f"severity={reasoning.severity_score:.2f}, fingerprint={fingerprints['l3'][:40]}..."
        )

        return learning_record
    
    async def _store_in_database(
        self,
        learning_record: QSPLearningRecord,
        context: QSPPerceptionContext,
        reasoning: SecurityReasoning,
        action: SecurityResponseAction,
        fingerprints: Dict[str, str],
    ) -> bool:
        """
        Store learning record in PostgreSQL using hierarchical fingerprints.

        Returns:
            True if storage succeeded, False otherwise
        """
        try:
            parameters = {
                'threat_count':                  context.threat_count,
                'highest_severity':              context.highest_severity,
                'network_anomalies':             context.network_anomalies,
                'suspicious_connections':        context.suspicious_connections,
                'failed_auth_attempts':          context.failed_auth_attempts,
                'threat_assessment_confidence':  context.threat_assessment_confidence,
                'response_urgency':              context.response_urgency,
                'response_type':                 action.action_type,
                'response_strategy':             action.response_strategy,
                'priority':                      action.priority,
                'quantum_state':                 action.quantum_state,
                'existential_dread_level':       action.existential_dread_level,
                'quantum_coherence':             action.quantum_coherence,
                'threat_classification':         reasoning.threat_classification,
                'hamster_assistance_requested':  action.hamster_assistance_requested,
                'requires_escalation':           action.requires_escalation,
                'threat_indicators':             reasoning.threat_indicators,
                'historical_precedent':          reasoning.historical_precedent,
                'similar_threat_count':          reasoning.similar_threat_count,
                'severity_score':                reasoning.severity_score,
                'primary_metric':                reasoning.primary_metric,
            }

            improvement = {
                'action_type':   action.action_type,
                'quantum_state': action.quantum_state,
            }

            db_record = AgentLearningRecord(
                agent_name='quantum_shadow_people',
                fingerprint_l1=fingerprints['l1'],
                fingerprint_l2=fingerprints['l2'],
                fingerprint_l3=fingerprints['l3'],
                resource_type=context.resource_type,
                severity=reasoning.severity_score,
                root_cause=reasoning.root_cause,
                process_category='security',
                action=action.action_type,
                parameters=parameters,
                confidence=action.confidence,
                followed_vic20=True,
                success=learning_record.success if learning_record.success is not None else True,
                improvement=improvement,
                what_worked=reasoning.root_cause if learning_record.success else None,
                what_failed=None if learning_record.success else reasoning.root_cause,
            )

            self.db.add(db_record)
            await self.db.flush()

            learning_record.learning_record_id = str(db_record.id)

            logger.debug(f"👻💾 Learning record stored (ID: {db_record.id}, fingerprint={fingerprints['l3'][:32]}...)")
            return True

        except Exception as e:
            logger.error(f"👻💥 LEARNING STORAGE FAILED: {e}", exc_info=True)
            await self.db.rollback()
            return False
    
    async def update_outcome(
        self,
        learning_record: QSPLearningRecord,
        success: bool,
        threat_resolved: bool,
        false_positive: bool = False,
        false_negative: bool = False,
        outcome_notes: Optional[str] = None,
        pre_metrics: Optional[Dict[str, float]] = None,
        post_metrics: Optional[Dict[str, float]] = None
    ):
        """
        Update a learning record with outcome information.
        
        This is called after the response executes and we know if it succeeded.
        Records outcomes in both learned thresholds and action effectiveness.
        
        CRITICAL: false_positive and false_negative are tracked separately.
        """
        learning_record.success = success
        learning_record.threat_resolved = threat_resolved
        learning_record.false_positive = false_positive
        learning_record.outcome_notes = outcome_notes
        
        if false_negative:
            logger.error(
                f"👻🚨 FALSE NEGATIVE: Updated learning record - MISSED THREAT "
                f"(success={success}, resolved={threat_resolved})"
            )
        else:
            logger.info(
                f"👻📝 Updated learning record: success={success}, "
                f"resolved={threat_resolved}, false_positive={false_positive}"
            )

        # Record in learned thresholds for each relevant metric
        if pre_metrics:
            for metric_name in ('suspicious_connections', 'network_anomalies', 'total_connections', 'failed_auth_attempts'):
                value = pre_metrics.get(metric_name)
                if value is None:
                    continue
                warning_threshold = await self.learned_thresholds.get_threshold(metric_name, 'warning')
                critical_threshold = await self.learned_thresholds.get_threshold(metric_name, 'critical')
                level = 'critical' if value >= critical_threshold else 'warning'
                await self.learned_thresholds.record_outcome(
                    metric_name=metric_name,
                    metric_value=value,
                    threshold_level=level,
                    was_successful=success,
                    was_false_positive=false_positive,
                    was_false_negative=false_negative,
                    outcome_notes=outcome_notes,
                )

        # Record in action effectiveness using severity_score from the learning record
        if pre_metrics and post_metrics:
            primary_metric = max(pre_metrics, key=lambda k: abs(pre_metrics[k]))
            await self.action_effectiveness.record_outcome(
                action=learning_record.response_type,
                current_metrics=pre_metrics,
                severity=learning_record.severity_score,
                primary_metric=primary_metric,
                pre_metrics=pre_metrics,
                post_metrics=post_metrics,
                success=success,
                other_actions_considered=[],
            )
    
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
