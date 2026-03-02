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
            resource_type = getattr(context, 'resource_type', 'logging')
            severity = getattr(context, 'severity', 'normal')

            # Hierarchical fingerprints
            fingerprint_l1 = resource_type
            fingerprint_l2 = f"{resource_type}_{severity}"
            fingerprint_l3 = f"{resource_type}_{severity}_{action.action_type}"

            # Parameters stored in the DB record
            parameters = {
                'action_type': action.action_type,
                'logging_strategy': getattr(action, 'logging_strategy', 'standard'),
                'priority': action.priority,
                'anxiety_level': context.anxiety_level,
                'anxiety_category': action.anxiety_level,
                'panic_attack_active': context.panic_attack_active,
                'paper_bags_consumed': action.paper_bags_consumed,
                'panic_attack_managed': getattr(action, 'panic_attack_managed', False),
                'bob_detected': action.bob_detected,
                'bob_avoidance_executed': getattr(action, 'bob_avoidance_executed', False),
                'hamster_messages_archived': getattr(action, 'hamster_messages_archived', 0),
                'log_retention_days': getattr(action, 'log_retention_days', 7),
                'compression_applied': getattr(action, 'compression_applied', False),
            }

            improvement = {
                'action_type': action.action_type,
                'anxiety_managed': getattr(action, 'panic_attack_managed', False),
            }

            # success=False at write time (placeholder — updated by update_outcome()).
            # DB column is NOT NULL so we cannot store None.
            db_record = AgentLearningRecord(
                agent_name='the_stick',
                fingerprint_l1=fingerprint_l1,
                fingerprint_l2=fingerprint_l2,
                fingerprint_l3=fingerprint_l3,
                resource_type=resource_type,
                severity=severity,
                root_cause=getattr(reasoning, 'root_cause', None),
                process_category='logging',
                action=action.action_type,
                parameters=parameters,
                confidence=action.confidence,
                followed_vic20=True,
                success=False,  # placeholder — updated by update_outcome()
                improvement=improvement,
                what_worked=None,
                what_failed=None,
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
    
    async def validate_cross_agent_learning(
        self,
        interaction,
        config=None
    ):
        """
        Validate a cross-agent learning interaction.
        
        The Stick's job: Ensure agents are learning CORRECTLY from each other.
        
        Args:
            interaction: AgentLearningInteractions instance to validate
            config: Optional ValidationConfig override (defaults to global VALIDATION_CONFIG)
            
        Returns:
            ValidationAuditEntry with validation decision and reasoning
        """
        from ..validation_config import VALIDATION_CONFIG
        from ..data_types import ValidationAuditEntry
        from app.models.agent_memory_banks import AgentLearningInteractions
        
        config = config or VALIDATION_CONFIG
        thresholds = config.get_active_thresholds()
        
        logger.info(f"📏🔍 Validating learning interaction {interaction.interaction_id}")
        logger.info(f"   Source: {interaction.source_agent} → Target: {interaction.target_agent}")
        logger.info(f"   Thresholds: {thresholds['threshold_state']}")
        
        # Calculate interaction age
        now = datetime.now(timezone.utc)
        age_delta = now - interaction.timestamp
        age_hours = age_delta.total_seconds() / 3600
        
        # Validation checks
        validation_failures = []
        
        # Check 1: Age
        if age_hours > thresholds['max_age_hours']:
            validation_failures.append(
                f"Interaction too old: {age_hours:.1f}h > {thresholds['max_age_hours']}h"
            )
        
        # Check 2: Effectiveness score
        if interaction.effectiveness_score is not None:
            if interaction.effectiveness_score < thresholds['min_effectiveness']:
                validation_failures.append(
                    f"Effectiveness too low: {interaction.effectiveness_score:.2f} < {thresholds['min_effectiveness']}"
                )
        else:
            validation_failures.append("No effectiveness score available")
        
        # Check 3: Success rate (if improvement_measured available)
        if interaction.improvement_measured is not None:
            # Treat improvement as proxy for success rate
            if interaction.improvement_measured < thresholds['min_success_rate']:
                validation_failures.append(
                    f"Success rate too low: {interaction.improvement_measured:.2f} < {thresholds['min_success_rate']}"
                )
        
        # Determine validation result
        validation_passed = len(validation_failures) == 0
        
        # Build reasoning
        if validation_passed:
            reasoning = (
                f"✅ Validation PASSED. "
                f"Effectiveness: {interaction.effectiveness_score:.2f}, "
                f"Age: {age_hours:.1f}h, "
                f"Thresholds: {thresholds['threshold_state']}"
            )
        else:
            reasoning = (
                f"❌ Validation FAILED. "
                f"Failures: {'; '.join(validation_failures)}"
            )
        
        # Check if this is a retry
        was_retry = interaction.cross_validation_count > 0
        
        # Create audit entry
        audit_entry = ValidationAuditEntry(
            timestamp=now,
            interaction_id=interaction.interaction_id,
            source_agent=interaction.source_agent,
            target_agent=interaction.target_agent,
            learning_type=interaction.learning_type,
            validation_result=validation_passed,
            reasoning=reasoning,
            thresholds_applied=thresholds,
            threshold_state=thresholds['threshold_state'],
            was_retry=was_retry,
            retry_count=interaction.cross_validation_count,
            effectiveness_score=interaction.effectiveness_score,
            success_rate=interaction.improvement_measured,
            interaction_age_hours=age_hours,
            stick_anxiety_level=self._calculate_validation_anxiety(validation_passed)
        )
        
        logger.info(f"📏✅ Validation result: {reasoning}")
        
        return audit_entry
    
    async def validate_unvalidated_interactions(
        self,
        max_age_days: int = 7,
        session=None  # OPUS 4.6 CHANGE: Accept optional session from caller
    ) -> Dict[str, Any]:
        """
        Sweep through unvalidated learning interactions and validate them.
        
        The Stick's anxiety-driven thoroughness ensures NO learning goes unvalidated.
        
        Args:
            max_age_days: Skip interactions older than this (default 7 days)
            session: Optional existing session from caller
            
        Returns:
            Statistics on validated interactions
        """
        logger.info("📏🔍 Starting validation sweep for unvalidated interactions...")
        
        from sqlalchemy import select, and_, or_
        from sqlalchemy.sql import func
        from datetime import timedelta
        from app.models.agent_memory_banks import AgentLearningInteractions
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        now = datetime.now(timezone.utc)
        
        try:
            active_session = session or self.db
            
            # OPUS 4.6 CHANGE: Added retry window filtering.
            # Previously: Query only checked validated_by_stick == False and age.
            # Problem: Failed validations stay validated_by_stick == False, so
            # the next sweep immediately re-validates them — ignoring the 24-hour
            # retry window specified in the failure metadata.
            # 
            # Now: We filter out interactions that have failed validation AND
            # haven't reached their retry_after window yet.
            #
            # NOTE: The JSON field query syntax below assumes PostgreSQL with JSONB.
            
            query = select(AgentLearningInteractions).where(
                and_(
                    AgentLearningInteractions.validated_by_stick == False,
                    AgentLearningInteractions.timestamp >= cutoff_date,
                    # Include interactions that either:
                    # 1. Have never been validated (cross_validation_count == 0), OR
                    # 2. Have been validated before but retry window has elapsed
                    or_(
                        AgentLearningInteractions.cross_validation_count == 0,
                        # Previously failed — check retry window
                        # This handles the case where adaptation_method contains
                        # retry_after timestamp from a previous failed validation
                        and_(
                            AgentLearningInteractions.cross_validation_count > 0,
                            # PostgreSQL JSONB syntax for retry window check
                            AgentLearningInteractions.adaptation_method['retry_after'].astext <= now.isoformat()
                        )
                    )
                )
            ).order_by(AgentLearningInteractions.timestamp.desc())
            
            result = await active_session.execute(query)
            interactions = result.scalars().all()
            
            logger.info(f"📏📊 Found {len(interactions)} unvalidated interactions")
            
            validated_count = 0
            failed_count = 0
            skipped_count = 0
            audit_entries = []
            
            for interaction in interactions:
                # Validate the interaction
                audit_entry = await self.validate_cross_agent_learning(interaction)
                audit_entries.append(audit_entry)
                
                # Note: record_validation will be called from distributed_stick.py
                # to avoid needing db_integration reference here
                
                if audit_entry.validation_result:
                    validated_count += 1
                else:
                    failed_count += 1
            
            stats = {
                'total_checked': len(interactions),
                'validated': validated_count,
                'failed': failed_count,
                'skipped': skipped_count,
                'validation_rate': (
                    validated_count / len(interactions) if interactions else 0.0
                ),
                'audit_entries': audit_entries,
                'interactions': interactions  # Return for caller to record
            }
            
            logger.info(
                f"📏✅ Validation sweep complete: "
                f"{validated_count} passed, {failed_count} failed, "
                f"{skipped_count} skipped (retry window)"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"📏💥 Error during validation sweep: {e}")
            return {
                'total_checked': 0,
                'validated': 0,
                'failed': 0,
                'skipped': 0,
                'validation_rate': 0.0,
                'error': str(e)
            }
    
    def _calculate_validation_anxiety(self, validation_passed: bool) -> float:
        """
        Calculate The Stick's anxiety level during validation.
        Failed validations increase anxiety.
        
        OPUS 4.6 NOTE: This is intentionally simple for Phase 1.
        Current behavior: binary 25.0 (pass) or 40.0 (fail).
        
        POST-LAUNCH ENHANCEMENT (flag for Phase 2+):
        Should factor in:
        - Failure RATE over rolling window (not just single result)
        - Consecutive failures (streak detection)
        - Ratio of validated to unvalidated interactions system-wide
        - Time since last successful validation
        - Agent-specific failure patterns (e.g., Terry always failing = 
          different anxiety profile than random failures across agents)
        
        Example future signature:
            def _calculate_validation_anxiety(
                self, 
                validation_passed: bool,
                recent_failure_rate: float,
                consecutive_failures: int,
                system_validation_ratio: float
            ) -> float:
        
        For now: simple binary is sufficient. The interface exists.
        The Stick will develop more nuanced anxiety when there's data to be anxious about.
        """
        base_anxiety = 25.0
        if not validation_passed:
            base_anxiety += 15.0  # Failed validation = more anxiety
        return min(base_anxiety, 100.0)
    
    def validate_learned_threshold(
        self,
        agent_name: str,
        metric_name: str,
        threshold_level: str,
        learned_value: float,
        default_value: float,
        sample_size: int,
        trigger_reason: str = None,
        config=None
    ):
        """
        Validate Terry's learned threshold.
        
        The Stick's job: Ensure Terry's ML learning produces REASONABLE thresholds.
        
        Validation checks:
        1. Sample size >= min_threshold_sample_size
        2. Shift magnitude <= max_threshold_shift_magnitude
        3. Direction consistency with trigger reason (catches learning logic errors)
        
        Args:
            agent_name: Agent that learned this threshold (e.g., 'meth_snail')
            metric_name: Metric being thresholded (e.g., 'memory_usage')
            threshold_level: Level being learned (e.g., 'warning', 'critical')
            learned_value: The threshold value Terry learned
            default_value: The default/baseline threshold
            sample_size: Number of learning records used
            trigger_reason: Why threshold was adjusted ('false_alarms', 'missed_actions', 'too_late')
            config: Optional ValidationConfig override
            
        Returns:
            ValidationAuditEntry with learning_type="threshold_adjustment"
        """
        from ..validation_config import VALIDATION_CONFIG
        from ..data_types import ValidationAuditEntry
        
        config = config or VALIDATION_CONFIG
        thresholds = config.get_active_thresholds()
        now = datetime.now(timezone.utc)
        
        logger.info(
            f"📏🔍 Validating learned threshold: {agent_name}.{metric_name}.{threshold_level} = {learned_value:.1f}"
        )
        
        # Calculate shift magnitude (as ratio of old threshold)
        shift_magnitude = abs(learned_value - default_value) / default_value if default_value != 0 else 0.0
        
        # Validation checks
        validation_failures = []
        
        # Check 1: Sample size
        if sample_size < thresholds['min_threshold_sample_size']:
            validation_failures.append(
                f"Insufficient data: {sample_size} samples < {thresholds['min_threshold_sample_size']} minimum"
            )
        
        # Check 2: Shift magnitude
        if shift_magnitude > thresholds['max_threshold_shift_magnitude']:
            validation_failures.append(
                f"Threshold shift too large: {shift_magnitude:.2f} > {thresholds['max_threshold_shift_magnitude']:.2f}"
            )
        
        # Check 3: Direction consistency with trigger reason
        # This catches actual learning errors - if Terry sees false alarms and lowers threshold (more sensitive),
        # something is broken in the learning logic
        if trigger_reason:
            threshold_went_up = learned_value > default_value
            threshold_went_down = learned_value < default_value
            
            if trigger_reason == "false_alarms":
                # False alarms mean threshold should go UP (less sensitive)
                if threshold_went_down:
                    validation_failures.append(
                        f"Direction inconsistent: false_alarms should move threshold UP (less sensitive), got DOWN"
                    )
            elif trigger_reason in ["missed_actions", "too_late"]:
                # Missed actions or acting too late means threshold should go DOWN (more sensitive)
                if threshold_went_up:
                    validation_failures.append(
                        f"Direction inconsistent: {trigger_reason} should move threshold DOWN (more sensitive), got UP"
                    )
        
        # Determine validation result
        validation_passed = len(validation_failures) == 0
        
        # Build reasoning
        if validation_passed:
            reasoning = (
                f"✅ Threshold VALIDATED. "
                f"Learned: {learned_value:.1f} (default: {default_value:.1f}, "
                f"shift: {shift_magnitude:.2f}), "
                f"samples: {sample_size}"
            )
            if trigger_reason:
                reasoning += f", trigger: {trigger_reason}"
        else:
            reasoning = (
                f"❌ Threshold REJECTED. "
                f"Failures: {'; '.join(validation_failures)}"
            )
        
        # Create audit entry using standard ValidationAuditEntry
        # learning_type="threshold_adjustment" discriminates this from cross-agent learning
        interaction_id = f"{agent_name}_{metric_name}_{threshold_level}_{now.isoformat()}"
        
        audit_entry = ValidationAuditEntry(
            timestamp=now,
            interaction_id=interaction_id,
            source_agent=agent_name,
            target_agent=agent_name,  # Terry validating Terry's own learning
            learning_type="threshold_adjustment",
            validation_result=validation_passed,
            reasoning=reasoning,
            thresholds_applied=thresholds,
            threshold_state=thresholds['threshold_state'],
            effectiveness_score=shift_magnitude,  # Reuse field: shift magnitude
            stick_anxiety_level=self._calculate_validation_anxiety(validation_passed)
        )
        
        logger.info(f"📏✅ Threshold validation result: {reasoning}")
        
        return audit_entry
    
    def validate_action_effectiveness(
        self,
        agent_name: str,
        action: str,
        metric_pattern: str,
        effectiveness_score: float,
        raw_success_rate: float,
        sample_size: int,
        previous_score: float = None,
        config=None
    ):
        """
        Validate Terry's learned action effectiveness.
        
        The Stick's job: Ensure Terry's ML learning produces RELIABLE action recommendations.
        
        Validation checks:
        1. Sample size >= min_action_sample_size
        2. Score volatility <= max_action_score_volatility (if previous score exists)
        3. Score consistency with raw data (catches model drift)
        
        Args:
            agent_name: Agent that learned this (e.g., 'meth_snail')
            action: Action being validated (e.g., 'restart_service')
            metric_pattern: Pattern fingerprint for this learning
            effectiveness_score: Learned effectiveness score from model (0.0-1.0)
            raw_success_rate: Raw success rate from outcomes (0.0-1.0)
            sample_size: Number of attempts
            previous_score: Previous effectiveness score for volatility check (optional)
            config: Optional ValidationConfig override
            
        Returns:
            ValidationAuditEntry with learning_type="action_effectiveness"
        """
        from ..validation_config import VALIDATION_CONFIG
        from ..data_types import ValidationAuditEntry
        
        config = config or VALIDATION_CONFIG
        thresholds = config.get_active_thresholds()
        now = datetime.now(timezone.utc)
        
        logger.info(
            f"📏🔍 Validating action effectiveness: {agent_name}.{action} "
            f"(score: {effectiveness_score:.2f}, raw_rate: {raw_success_rate:.2f}, samples: {sample_size})"
        )
        
        # Validation checks
        validation_failures = []
        
        # Check 1: Sample size
        if sample_size < thresholds['min_action_sample_size']:
            validation_failures.append(
                f"Insufficient data: {sample_size} outcomes < {thresholds['min_action_sample_size']} minimum"
            )
        
        # Check 2: Score volatility (if we have previous score)
        if previous_score is not None:
            score_delta = abs(effectiveness_score - previous_score)
            if score_delta > thresholds['max_action_score_volatility']:
                validation_failures.append(
                    f"Score volatility too high: {score_delta:.2f} > {thresholds['max_action_score_volatility']:.2f}"
                )
        
        # Check 3: Score consistency with raw data
        # This catches scoring model drift - if model says 0.9 but raw success is 0.4, model is wrong
        score_gap = abs(effectiveness_score - raw_success_rate)
        if score_gap > thresholds['min_action_consistency']:
            validation_failures.append(
                f"Score diverges from raw data: score={effectiveness_score:.2f}, raw_success_rate={raw_success_rate:.2f}, gap={score_gap:.2f} > {thresholds['min_action_consistency']:.2f}"
            )
        
        # Determine validation result
        validation_passed = len(validation_failures) == 0
        
        # Build reasoning
        if validation_passed:
            reasoning = (
                f"✅ Action VALIDATED. "
                f"Score: {effectiveness_score:.2f}, "
                f"raw rate: {raw_success_rate:.2f}, "
                f"samples: {sample_size}"
            )
            if previous_score is not None:
                reasoning += f", volatility: {abs(effectiveness_score - previous_score):.2f}"
        else:
            reasoning = (
                f"❌ Action REJECTED. "
                f"Failures: {'; '.join(validation_failures)}"
            )
        
        # Create audit entry using standard ValidationAuditEntry
        # learning_type="action_effectiveness" discriminates this from cross-agent learning
        interaction_id = f"{agent_name}_{action}_{metric_pattern[:16]}_{now.isoformat()}"
        
        audit_entry = ValidationAuditEntry(
            timestamp=now,
            interaction_id=interaction_id,
            source_agent=agent_name,
            target_agent=agent_name,  # Terry validating Terry's own learning
            learning_type="action_effectiveness",
            validation_result=validation_passed,
            reasoning=reasoning,
            thresholds_applied=thresholds,
            threshold_state=thresholds['threshold_state'],
            success_rate=raw_success_rate,  # Maps directly to raw success rate
            effectiveness_score=effectiveness_score,  # Learned score from model
            pattern_similarity=1.0 - score_gap,  # Reuse field: consistency (inverted gap)
            stick_anxiety_level=self._calculate_validation_anxiety(validation_passed)
        )
        
        logger.info(f"📏✅ Action validation result: {reasoning}")
        
        return audit_entry
