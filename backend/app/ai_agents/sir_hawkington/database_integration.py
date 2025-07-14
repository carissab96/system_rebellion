# /agents/sir_hawkington/database_integration.py
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc
from app.models.sir_hawkington_model import HawkingtonDecisionLog, HawkingtonMonitoringStats
from .data_types import HawkingtonDecision

class HawkingtonDatabaseIntegration:
    """Database integration for Sir Hawkington's aristocratic monitoring"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection with aristocratic dignity"""
        self.engine = create_async_engine(self.database_url)
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def store_metrics(self, user_id: str, metrics: Dict[str, Any]):
        """Store system metrics (Sir Hawkington uses main system_metrics table)"""
        # Sir Hawkington doesn't store separate metrics
        # He uses the main system_metrics table for analysis
        # This method exists for interface consistency
        pass
    
    async def store_decision(self, user_id: str, decision: HawkingtonDecision):
        """Store Sir Hawkington's aristocratic decision"""
        
        async with self.session_factory() as session:
            try:
                decision_log = HawkingtonDecisionLog(
                    user_id=user_id,
                    decision_type=decision.decision_type.value,
                    monocle_state=decision.monocle_state.value,
                    monitoring_target="system_performance",
                    alert_parameters={
                        'stress_score': decision.stress_score,
                        'estimated_impact': decision.estimated_impact,
                        'urgency': decision.urgency,
                        'analysis_depth': decision.analysis_depth.value
                    },
                    monocle_yeet_required=(decision.monocle_state.value == 'yeeted'),
                    aristocratic_explanation=decision.message,
                    technical_details={
                        'confidence': decision.confidence,
                        'data_quality_score': decision.data_quality_score,
                        'monocle_yeet_count': decision.monocle_yeet_count,
                        'reasoning': decision.reasoning
                    },
                    severity_level=decision.urgency,
                    confidence_level=decision.confidence,
                    alert_sent=(decision.message is not None),
                    timestamp=decision.timestamp
                )
                
                session.add(decision_log)
                await session.commit()
                
                return decision_log.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to store Hawkington decision: {str(e)}")
    
    async def get_historical_decisions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get Sir Hawkington's historical decisions for pattern analysis"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                query = select(HawkingtonDecisionLog).where(
                    HawkingtonDecisionLog.user_id == user_id,
                    HawkingtonDecisionLog.timestamp >= cutoff_date
                ).order_by(desc(HawkingtonDecisionLog.timestamp))
                
                result = await session.execute(query)
                decisions = result.scalars().all()
                
                return [
                    {
                        'timestamp': decision.timestamp,
                        'decision_type': decision.decision_type,
                        'monocle_state': decision.monocle_state,
                        'confidence_level': decision.confidence_level,
                        'alert_parameters': decision.alert_parameters,
                        'technical_details': decision.technical_details,
                        'severity_level': decision.severity_level,
                        'user_acknowledged': decision.user_acknowledged,
                        'issue_resolved': decision.issue_resolved
                    }
                    for decision in decisions
                ]
                
            except Exception as e:
                raise Exception(f"Failed to get historical decisions: {str(e)}")
    
    async def store_monitoring_stats(self, user_id: str, stats: Dict[str, Any]):
        """Store Sir Hawkington's monitoring performance statistics"""
        
        async with self.session_factory() as session:
            try:
                monitoring_stats = HawkingtonMonitoringStats(
                    user_id=user_id,
                    alerts_generated=stats.get('alerts_generated', 0),
                    monocle_yeets_performed=stats.get('monocle_yeets_performed', 0),
                    critical_issues_detected=stats.get('critical_issues_detected', 0),
                    monitoring_precision=stats.get('monitoring_precision'),
                    alert_accuracy_rate=stats.get('alert_accuracy_rate'),
                    user_response_time=stats.get('user_response_time'),
                    raw_stats=stats
                )
                
                session.add(monitoring_stats)
                await session.commit()
                
                return monitoring_stats.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to store monitoring stats: {str(e)}")
    
    async def get_hawkington_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get Sir Hawkington's performance metrics for monitoring"""
        
        async with self.session_factory() as session:
            try:
                # Get latest stats
                latest_stats = await session.execute(
                    select(HawkingtonMonitoringStats).where(
                        HawkingtonMonitoringStats.user_id == user_id
                    ).order_by(desc(HawkingtonMonitoringStats.timestamp)).limit(1)
                )
                
                stats = latest_stats.scalar_one_or_none()
                
                if not stats:
                    return {'status': 'no_data'}
                
                # Get decision success rate
                total_decisions = await session.execute(
                    select(func.count(HawkingtonDecisionLog.id)).where(
                        HawkingtonDecisionLog.user_id == user_id
                    )
                )
                
                resolved_issues = await session.execute(
                    select(func.count(HawkingtonDecisionLog.id)).where(
                        HawkingtonDecisionLog.user_id == user_id,
                        HawkingtonDecisionLog.issue_resolved == True
                    )
                )
                
                total_count = total_decisions.scalar() or 0
                resolved_count = resolved_issues.scalar() or 0
                
                return {
                    'alerts_generated': stats.alerts_generated,
                    'monocle_yeets_performed': stats.monocle_yeets_performed,
                    'critical_issues_detected': stats.critical_issues_detected,
                    'monitoring_precision': stats.monitoring_precision,
                    'alert_accuracy_rate': stats.alert_accuracy_rate,
                    'total_decisions': total_count,
                    'resolved_issues': resolved_count,
                    'resolution_rate': resolved_count / total_count if total_count > 0 else 0,
                    'last_updated': stats.timestamp
                }
                
            except Exception as e:
                raise Exception(f"Failed to get Hawkington performance metrics: {str(e)}")
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old Hawkington data with aristocratic precision"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Keep decision logs longer for audit trail (only clean very old ones)
                very_old_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
                
                await session.execute(
                    select(HawkingtonDecisionLog).where(
                        HawkingtonDecisionLog.timestamp < very_old_cutoff
                    ).delete()
                )
                
                # Clean up old monitoring stats
                await session.execute(
                    select(HawkingtonMonitoringStats).where(
                        HawkingtonMonitoringStats.timestamp < cutoff_date
                    ).delete()
                )
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to cleanup old Hawkington data: {str(e)}")