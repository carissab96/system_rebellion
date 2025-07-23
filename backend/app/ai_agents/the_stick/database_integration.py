import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc, and_
from models.stick_model import StickUserPatterns, StickDecisionLog, StickComplianceHistory, StickConfigurationProfiles
from .data_types import StickDecision, UserPattern, ComplianceViolation, ConfigurationProfile

class StickDatabaseIntegration:
    """Database integration for The Stick's eidetic memory and pattern learning"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize The Stick's database connection"""
        self.engine = create_async_engine()
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def store_user_behavior_observation(self, user_id: str, observation: Dict[str, Any]):
        """Store user behavior observation - The Stick's learning process"""
        
        async with self.session_factory() as session:
            try:
                # Check if user pattern exists
                existing_pattern = await session.execute(
                    select(StickUserPatterns).where(
                        StickUserPatterns.user_id == user_id
                    )
                )
                
                pattern = existing_pattern.scalar_one_or_none()
                
                if pattern:
                    # Update existing pattern with new observation
                    pattern.observation_count += 1
                    pattern.last_observation = datetime.now()
                    
                    # Update pattern data (The Stick's eidetic memory)
                    current_patterns = pattern.learned_patterns or {}
                    
                    # Add new observation to time-based patterns
                    hour = datetime.now().hour
                    if 'time_based' not in current_patterns:
                        current_patterns['time_based'] = {}
                    
                    if str(hour) not in current_patterns['time_based']:
                        current_patterns['time_based'][str(hour)] = {
                            'activities': [],
                            'metrics': [],
                            'count': 0
                        }
                    
                    current_patterns['time_based'][str(hour)]['activities'].append(observation.get('detected_activity', 'unknown'))
                    current_patterns['time_based'][str(hour)]['metrics'].append(observation.get('system_metrics', {}))
                    current_patterns['time_based'][str(hour)]['count'] += 1
                    
                    pattern.learned_patterns = current_patterns
                    pattern.confidence_score = self._calculate_pattern_confidence(current_patterns)
                    
                else:
                    # Create new pattern entry
                    pattern = StickUserPatterns(
                        user_id=user_id,
                        observation_count=1,
                        learned_patterns={
                            'time_based': {
                                str(datetime.now().hour): {
                                    'activities': [observation.get('detected_activity', 'unknown')],
                                    'metrics': [observation.get('system_metrics', {})],
                                    'count': 1
                                }
                            }
                        },
                        confidence_score=0.1,  # Low confidence with single observation
                        last_observation=datetime.now()
                    )
                    session.add(pattern)
                
                await session.commit()
                return pattern.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick failed to store behavior observation: {str(e)}")
    
    def _calculate_pattern_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate pattern confidence based on observation consistency"""
        
        if not patterns or 'time_based' not in patterns:
            return 0.0
        
        time_patterns = patterns['time_based']
        total_confidence = 0.0
        pattern_count = 0
        
        for hour, data in time_patterns.items():
            activities = data.get('activities', [])
            if len(activities) > 1:
                # Calculate consistency for this hour
                most_common = max(set(activities), key=activities.count)
                consistency = activities.count(most_common) / len(activities)
                total_confidence += consistency
                pattern_count += 1
        
        return total_confidence / pattern_count if pattern_count > 0 else 0.0
    
    async def store_stick_decision(self, user_id: str, decision: StickDecision):
        """Store The Stick's decision with complete audit trail"""
        
        async with self.session_factory() as session:
            try:
                decision_log = StickDecisionLog(
                    user_id=user_id,
                    decision_type=decision.decision_type.value,
                    compliance_state=decision.compliance_state.value,
                    configuration_target=decision.configuration_target,
                    optimization_parameters=decision.optimization_parameters,
                    user_pattern_confidence=decision.user_pattern_confidence,
                    compliance_explanation=decision.compliance_explanation,
                    technical_details=decision.technical_details,
                    expected_improvement=decision.expected_improvement,
                    confidence_level=decision.confidence_level,
                    timestamp=decision.timestamp
                )
                
                session.add(decision_log)
                await session.commit()
                
                return decision_log.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick failed to store decision: {str(e)}")
    
    async def store_compliance_violation(self, user_id: str, violation: ComplianceViolation):
        """Store compliance violation - The Stick's OCD tracking"""
        
        async with self.session_factory() as session:
            try:
                compliance_record = StickComplianceHistory(
                    user_id=user_id,
                    violation_type=violation.violation_type,
                    measured_value=violation.measured_value,
                    threshold_value=violation.threshold_value,
                    severity=violation.severity,
                    recommendation=violation.recommendation,
                    resolved=violation.resolved,
                    timestamp=violation.timestamp
                )
                
                session.add(compliance_record)
                await session.commit()
                
                return compliance_record.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick failed to store compliance violation: {str(e)}")
    
    async def get_user_learned_patterns(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user's learned patterns - The Stick's eidetic memory recall"""
        
        async with self.session_factory() as session:
            try:
                pattern = await session.execute(
                    select(StickUserPatterns).where(
                        StickUserPatterns.user_id == user_id
                    )
                )
                
                result = pattern.scalar_one_or_none()
                
                if not result:
                    return None
                
                return {
                    'user_id': result.user_id,
                    'observation_count': result.observation_count,
                    'learned_patterns': result.learned_patterns,
                    'confidence_score': result.confidence_score,
                    'last_observation': result.last_observation,
                    'stick_memory_status': 'eidetic_recall_available'
                }
                
            except Exception as e:
                raise Exception(f"The Stick's memory recall failed: {str(e)}")
    
    async def get_historical_behavior_data(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical behavior data for pattern analysis"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get decision logs as behavioral data
                query = select(StickDecisionLog).where(
                    and_(
                        StickDecisionLog.user_id == user_id,
                        StickDecisionLog.timestamp >= cutoff_date
                    )
                ).order_by(desc(StickDecisionLog.timestamp))
                
                result = await session.execute(query)
                decisions = result.scalars().all()
                
                return [
                    {
                        'timestamp': decision.timestamp.isoformat(),
                        'decision_type': decision.decision_type,
                        'compliance_state': decision.compliance_state,
                        'configuration_target': decision.configuration_target,
                        'pattern_confidence': decision.user_pattern_confidence,
                        'technical_details': decision.technical_details
                    }
                    for decision in decisions
                ]
                
            except Exception as e:
                raise Exception(f"The Stick failed to retrieve historical data: {str(e)}")
    
    async def get_compliance_history(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get compliance violation history"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                query = select(StickComplianceHistory).where(
                    and_(
                        StickComplianceHistory.user_id == user_id,
                        StickComplianceHistory.timestamp >= cutoff_date
                    )
                ).order_by(desc(StickComplianceHistory.timestamp))
                
                result = await session.execute(query)
                violations = result.scalars().all()
                
                return [
                    {
                        'violation_type': violation.violation_type,
                        'measured_value': violation.measured_value,
                        'threshold_value': violation.threshold_value,
                        'severity': violation.severity,
                        'recommendation': violation.recommendation,
                        'resolved': violation.resolved,
                        'timestamp': violation.timestamp.isoformat()
                    }
                    for violation in violations
                ]
                
            except Exception as e:
                raise Exception(f"The Stick failed to retrieve compliance history: {str(e)}")
    
    async def store_configuration_profile(self, user_id: str, profile: ConfigurationProfile):
        """Store learned configuration profile"""
        
        async with self.session_factory() as session:
            try:
                # Check if profile exists
                existing = await session.execute(
                    select(StickConfigurationProfiles).where(
                        and_(
                            StickConfigurationProfiles.user_id == user_id,
                            StickConfigurationProfiles.profile_name == profile.profile_name
                        )
                    )
                )
                
                existing_profile = existing.scalar_one_or_none()
                
                if existing_profile:
                    # Update existing profile
                    existing_profile.configuration_parameters = profile.configuration_parameters
                    existing_profile.usage_confidence = profile.usage_confidence
                    existing_profile.performance_metrics = profile.performance_metrics
                    existing_profile.times_applied += 1
                    existing_profile.last_used = profile.last_used
                    existing_profile.success_rate = profile.success_rate
                else:
                    # Create new profile
                    new_profile = StickConfigurationProfiles(
                        user_id=user_id,
                        profile_name=profile.profile_name,
                        activity_type=profile.activity_type,
                        configuration_parameters=profile.configuration_parameters,
                        usage_confidence=profile.usage_confidence,
                        performance_metrics=profile.performance_metrics,
                        created_from_pattern=profile.created_from_pattern,
                        times_applied=profile.times_applied,
                        success_rate=profile.success_rate,
                        last_used=profile.last_used
                    )
                    session.add(new_profile)
                
                await session.commit()
                return existing_profile.id if existing_profile else new_profile.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick failed to store configuration profile: {str(e)}")
    
    async def get_stick_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get The Stick's performance metrics for this user"""
        
        async with self.session_factory() as session:
            try:
                # Get decision count
                decision_count = await session.execute(
                    select(func.count(StickDecisionLog.id)).where(
                        StickDecisionLog.user_id == user_id
                    )
                )
                
                # Get compliance violations
                violation_count = await session.execute(
                    select(func.count(StickComplianceHistory.id)).where(
                        StickComplianceHistory.user_id == user_id
                    )
                )
                
                # Get pattern confidence
                pattern_data = await session.execute(
                    select(StickUserPatterns).where(
                        StickUserPatterns.user_id == user_id
                    )
                )
                
                pattern = pattern_data.scalar_one_or_none()
                
                return {
                    'total_decisions': decision_count.scalar(),
                    'compliance_violations': violation_count.scalar(),
                    'pattern_confidence': pattern.confidence_score if pattern else 0.0,
                    'observation_count': pattern.observation_count if pattern else 0,
                    'eidetic_memory_status': 'active' if pattern and pattern.confidence_score > 0.5 else 'learning',
                    'stick_intelligence_level': 'genius' if pattern and pattern.confidence_score > 0.8 else 'learning'
                }
                
            except Exception as e:
                raise Exception(f"The Stick failed to calculate performance metrics: {str(e)}")
    
    async def cleanup_old_observations(self, days_to_keep: int = 90):
        """Clean up old observations - The Stick's memory management"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Clean up very old decision logs (keep audit trail longer)
                old_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
                
                # The Stick keeps compliance history longer for pattern analysis
                await session.execute(
                    select(StickDecisionLog).where(
                        StickDecisionLog.timestamp < old_cutoff
                    ).limit(1000)  # Batch cleanup
                )
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick's memory cleanup failed: {str(e)}")