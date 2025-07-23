# /agents/qsp/database_integration.py
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc
from models.qsp_model import QSPNetworkMetrics, QSPDecisionLog, QSPQuantumStats, QSPNetworkPatterns
from .data_types import QSPDecision

class QSPDatabaseIntegration:
    """Database integration for QSP quantum network optimization"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.engine = create_async_engine()
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def store_network_metrics(self, user_id: str, metrics: Dict[str, Any]):
        """Store network metrics for quantum analysis"""
        
        async with self.session_factory() as session:
            try:
                network_metric = QSPNetworkMetrics(
                    user_id=user_id,
                    latency=metrics.get('latency'),
                    bandwidth_utilization=metrics.get('bandwidth_utilization'),
                    packet_loss=metrics.get('packet_loss'),
                    jitter=metrics.get('jitter'),
                    download_speed=metrics.get('download_speed'),
                    upload_speed=metrics.get('upload_speed'),
                    connection_type=metrics.get('connection_type'),
                    raw_metrics=metrics
                )
                
                session.add(network_metric)
                await session.commit()
                
                return network_metric.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to store network metrics: {str(e)}")
    
    async def store_qsp_decision(self, user_id: str, decision: QSPDecision):
        """Store QSP quantum decision"""
        
        async with self.session_factory() as session:
            try:
                decision_log = QSPDecisionLog(
                    user_id=user_id,
                    decision_type=decision.decision_type.value,
                    quantum_state=decision.quantum_state.value,
                    network_target=decision.network_target,
                    optimization_parameters=decision.optimization_parameters,
                    tequila_jello_shots_required=decision.tequila_jello_shots_required,
                    mysterious_explanation=decision.mysterious_explanation,
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
                raise Exception(f"Failed to store QSP decision: {str(e)}")
    
    async def get_historical_network_metrics(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical network metrics for pattern analysis"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                query = select(QSPNetworkMetrics).where(
                    QSPNetworkMetrics.user_id == user_id,
                    QSPNetworkMetrics.timestamp >= cutoff_date
                ).order_by(desc(QSPNetworkMetrics.timestamp))
                
                result = await session.execute(query)
                metrics = result.scalars().all()
                
                return [
                    {
                        'timestamp': metric.timestamp,
                        'latency': metric.latency,
                        'bandwidth_utilization': metric.bandwidth_utilization,
                        'packet_loss': metric.packet_loss,
                        'jitter': metric.jitter,
                        'download_speed': metric.download_speed,
                        'upload_speed': metric.upload_speed,
                        'connection_type': metric.connection_type,
                        'raw_metrics': metric.raw_metrics
                    }
                    for metric in metrics
                ]
                
            except Exception as e:
                raise Exception(f"Failed to get historical metrics: {str(e)}")
    async def store_quantum_stats(self, user_id: str, stats: Dict[str, Any]):
        """Store QSP quantum performance statistics"""
        
        async with self.session_factory() as session:
            try:
                quantum_stats = QSPQuantumStats(
                    user_id=user_id,
                    quantum_fixes_applied=stats.get('quantum_fixes_applied', 0),
                    tequila_jello_shots_consumed=stats.get('tequila_jello_shots_consumed', 0),
                    dimensional_shifts_performed=stats.get('dimensional_shifts_performed', 0),
                    average_latency_improvement=stats.get('average_latency_improvement'),
                    average_bandwidth_improvement=stats.get('average_bandwidth_improvement'),
                    packet_loss_reductions=stats.get('packet_loss_reductions', 0),
                    network_patterns_learned=stats.get('network_patterns_learned', 0),
                    optimization_success_rate=stats.get('optimization_success_rate'),
                    raw_stats=stats
                )
                
                session.add(quantum_stats)
                await session.commit()
                
                return quantum_stats.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to store quantum stats: {str(e)}")
    
    async def store_network_pattern(self, user_id: str, pattern_type: str, pattern_data: Dict[str, Any]):
        """Store learned network pattern"""
        
        async with self.session_factory() as session:
            try:
                # Check if pattern already exists
                existing_pattern = await session.execute(
                    select(QSPNetworkPatterns).where(
                        QSPNetworkPatterns.user_id == user_id,
                        QSPNetworkPatterns.pattern_type == pattern_type
                    )
                )
                
                pattern = existing_pattern.scalar_one_or_none()
                
                if pattern:
                    # Update existing pattern
                    pattern.pattern_data = pattern_data
                    pattern.last_updated = datetime.now()
                    pattern.optimization_count += 1
                else:
                    # Create new pattern
                    pattern = QSPNetworkPatterns(
                        user_id=user_id,
                        pattern_type=pattern_type,
                        pattern_data=pattern_data,
                        confidence_score=pattern_data.get('confidence', 0.5),
                        optimization_count=1
                    )
                    session.add(pattern)
                
                await session.commit()
                return pattern.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to store network pattern: {str(e)}")
    
    async def get_qsp_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get QSP performance metrics for monitoring"""
        
        async with self.session_factory() as session:
            try:
                # Get latest stats
                latest_stats = await session.execute(
                    select(QSPQuantumStats).where(
                        QSPQuantumStats.user_id == user_id
                    ).order_by(desc(QSPQuantumStats.timestamp)).limit(1)
                )
                
                stats = latest_stats.scalar_one_or_none()
                
                if not stats:
                    return {'status': 'no_data'}
                
                # Get decision success rate
                decision_count = await session.execute(
                    select(QSPDecisionLog).where(
                        QSPDecisionLog.user_id == user_id
                    ).count()
                )
                
                successful_decisions = await session.execute(
                    select(QSPDecisionLog).where(
                        QSPDecisionLog.user_id == user_id,
                        QSPDecisionLog.success_verified == True
                    ).count()
                )
                
                return {
                    'quantum_fixes_applied': stats.quantum_fixes_applied,
                    'tequila_jello_shots_consumed': stats.tequila_jello_shots_consumed,
                    'dimensional_shifts_performed': stats.dimensional_shifts_performed,
                    'total_decisions': decision_count,
                    'successful_decisions': successful_decisions,
                    'success_rate': successful_decisions / decision_count if decision_count > 0 else 0,
                    'average_latency_improvement': stats.average_latency_improvement,
                    'average_bandwidth_improvement': stats.average_bandwidth_improvement,
                    'last_updated': stats.timestamp
                }
                
            except Exception as e:
                raise Exception(f"Failed to get QSP performance metrics: {str(e)}")
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old QSP data"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Clean up old metrics
                await session.execute(
                    delete(QSPNetworkMetrics).where(
                        QSPNetworkMetrics.timestamp < cutoff_date
                    )
                )
                
                # Clean up old decisions (keep for audit trail)
                # Only clean up very old decisions
                old_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
                await session.execute(
                    delete(QSPDecisionLog).where(
                        QSPDecisionLog.timestamp < old_cutoff
                    )
                )
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to cleanup old data: {str(e)}")