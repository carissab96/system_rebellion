# app/ai_agents/sir_hawkington/database_integration.py
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc
from app.models.agent_memory_banks import CentralMemoryBank
from app.schemas.agent_memory import MemoryType, MemoryPriority
from .data_types import HawkingtonDecision
import inspect

class HawkingtonDatabaseIntegration:
    """Database integration for Sir Hawkington's aristocratic monitoring"""
    
    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter

        self.engine = None
        self.session_factory = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self):
        """Initialize database connection with aristocratic dignity."""
        if not callable(self.db_getter):
            raise ValueError("db_getter must be a callable that returns the database URL.")

        try:
            if inspect.iscoroutinefunction(self.db_getter):
                db_url = await self.db_getter()
            else:
                db_url = self.db_getter()
        except Exception as e:
            raise RuntimeError(f"Failed to obtain database URL from db_getter: {e}") from e

        if not isinstance(db_url, str) or not db_url.strip():
            raise ValueError(f"Invalid database URL returned by db_getter: {db_url!r}")

        try:
            self.engine = create_async_engine(
                db_url,
                future=True
            )

            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            self.logger.info("Database engine and session factory initialized successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database engine or session factory: {e}") from e

    async def dispose(self):
        """Dispose of the database engine and close all connections."""
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database engine disposed and connections closed.")

    
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
    
    async def store_triage_decision(
        self, 
        user_id: str, 
        triage_data: Dict[str, Any]
    ) -> int:
        """Store Sir Hawkington's triage decision - SIMPLIFIED VERSION"""
        
        # For now, we'll store triage decisions as special HawkingtonDecisionLog entries
        # This avoids creating new tables and keeps everything working
        
        async with self.session_factory() as session:
            try:
                triage_log = HawkingtonDecisionLog(
                    user_id=user_id,
                    decision_type="triage_decision",
                    monocle_state=triage_data.get('monocle_state', 'polished'),
                    monitoring_target="system_triage",
                    alert_parameters={
                        'triage_severity': triage_data.get('triage_severity'),
                        'routing_decision': triage_data.get('routing_decision'),
                        'target_agents': triage_data.get('target_agents', []),
                        'processing_time': triage_data.get('processing_time'),
                        'confidence': triage_data.get('confidence')
                    },
                    monocle_yeet_required=triage_data.get('monocle_yeeted', False),
                    aristocratic_explanation=triage_data.get('reasoning', 'Triage decision'),
                    technical_details={
                        'routing_results': triage_data.get('routing_results'),
                        'success': triage_data.get('success', True),
                        'hawkington_decision_id': triage_data.get('hawkington_decision_id')
                    },
                    severity_level=triage_data.get('triage_severity', 'normal'),
                    confidence_level=triage_data.get('confidence', 0.0),
                    alert_sent=True,
                    timestamp=triage_data.get('timestamp', datetime.now())
                )
                
                session.add(triage_log)
                await session.commit()
                
                return triage_log.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to store triage decision: {str(e)}")
    
    async def get_triage_statistics(
        self, 
        user_id: str, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get triage statistics for the user"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get recent triage decisions (stored as special HawkingtonDecisionLog entries)
                query = select(HawkingtonDecisionLog).where(
                    HawkingtonDecisionLog.user_id == user_id,
                    HawkingtonDecisionLog.monitoring_target == "system_triage",
                    HawkingtonDecisionLog.timestamp >= cutoff_date
                ).order_by(desc(HawkingtonDecisionLog.timestamp))
                
                result = await session.execute(query)
                decisions = result.scalars().all()
                
                if not decisions:
                    return {'status': 'no_data'}
                
                # Calculate statistics
                total_decisions = len(decisions)
                successful_decisions = len([d for d in decisions if d.technical_details.get('success', True)])
                monocle_yeets = len([d for d in decisions if d.monocle_yeet_required])
                
                routing_counts = {}
                severity_counts = {}
                
                for decision in decisions:
                    # Count routing decisions
                    routing = decision.alert_parameters.get('routing_decision', 'unknown')
                    routing_counts[routing] = routing_counts.get(routing, 0) + 1
                    
                    # Count severity levels
                    severity = decision.alert_parameters.get('triage_severity', 'unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Calculate averages
                avg_confidence = sum(d.confidence_level for d in decisions) / total_decisions
                avg_processing_time = sum(d.alert_parameters.get('processing_time', 0) for d in decisions) / total_decisions
                
                return {
                    'total_decisions': total_decisions,
                    'successful_decisions': successful_decisions,
                    'success_rate': successful_decisions / total_decisions,
                    'monocle_yeet_count': monocle_yeets,
                    'monocle_yeet_rate': monocle_yeets / total_decisions,
                    'routing_distribution': routing_counts,
                    'severity_distribution': severity_counts,
                    'average_confidence': avg_confidence,
                    'average_processing_time': avg_processing_time,
                    'period_days': days,
                    'latest_decision': decisions[0].timestamp if decisions else None
                }
                
            except Exception as e:
                raise Exception(f"Failed to get triage statistics: {str(e)}")
    
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
                
                # Delete very old decision logs
                old_decisions = await session.execute(
                    select(HawkingtonDecisionLog).where(
                        HawkingtonDecisionLog.timestamp < very_old_cutoff
                    )
                )
                decisions_to_delete = old_decisions.scalars().all()
                
                for decision in decisions_to_delete:
                    await session.delete(decision)
                
                # Delete old monitoring stats
                old_stats = await session.execute(
                    select(HawkingtonMonitoringStats).where(
                        HawkingtonMonitoringStats.timestamp < cutoff_date
                    )
                )
                stats_to_delete = old_stats.scalars().all()
                
                for stat in stats_to_delete:
                    await session.delete(stat)
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to cleanup old Hawkington data: {str(e)}")