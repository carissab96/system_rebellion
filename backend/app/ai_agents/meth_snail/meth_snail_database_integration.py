# agents/meth_snail/meth_snail_database_integration.py
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_decision_models import MethSnailDecisionLog
from app.models.meth_snail_model import MethSnailOptimizationStats
from app.ai_agents.meth_snail.data_types import OptimizationDecision

class MethSnailDatabaseIntegration:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
    async def store_optimization_metrics(self, user_id: int, metrics_data: dict):
        """Store optimization metrics - no fake fucking data"""
        try:
            async with self.db_manager.get_session() as session:
                optimization_stats = MethSnailOptimizationStats(
                    user_id=user_id,
                    cpu_usage_before=metrics_data.get('cpu_usage_before'),
                    cpu_usage_after=metrics_data.get('cpu_usage_after'),
                    memory_usage_before=metrics_data.get('memory_usage_before'),
                    memory_usage_after=metrics_data.get('memory_usage_after'),
                    optimization_success=metrics_data.get('optimization_success', False),
                    energy_drink_level=metrics_data.get('energy_drink_level', 0),
                    shell_spin_count=metrics_data.get('shell_spin_count', 0),
                    raw_metrics=metrics_data
                )
                
                session.add(optimization_stats)
                await session.commit()
                return optimization_stats.id
                
        except Exception as e:
            self.logger.error(f"Failed to store optimization metrics: {e}")
            raise
    
    async def get_historical_performance(self, user_id: int, days: int = 30):
        """Get historical performance - if no data, we fucking say so"""
        try:
            async with self.db_manager.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                result = await session.execute(
                    select(MethSnailOptimizationStats)
                    .where(MethSnailOptimizationStats.user_id == user_id)
                    .where(MethSnailOptimizationStats.timestamp >= cutoff_date)
                    .order_by(desc(MethSnailOptimizationStats.timestamp))
                )
                
                historical_data = result.scalars().all()
                
                if not historical_data:
                    return {
                        'status': 'no_data',
                        'message': "No fucking historical data available - this snail needs time to build optimization history!",
                        'data': []
                    }
                
                return {
                    'status': 'success',
                    'data': [
                        {
                            'timestamp': record.timestamp,
                            'cpu_improvement': record.cpu_usage_before - record.cpu_usage_after if record.cpu_usage_before and record.cpu_usage_after else None,
                            'memory_improvement': record.memory_usage_before - record.memory_usage_after if record.memory_usage_before and record.memory_usage_after else None,
                            'optimization_success': record.optimization_success,
                            'energy_drink_level': record.energy_drink_level,
                            'shell_spin_count': record.shell_spin_count
                        } for record in historical_data
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get historical performance: {e}")
            raise
    
    async def store_decision(self, user_id: int, decision_data: dict):
        """Store optimization decision with full context"""
        try:
            async with self.db_manager.get_session() as session:
                decision = MethSnailDecisionLog(
                    user_id=user_id,
                    decision_type=decision_data.get('decision_type'),
                    decision_context=decision_data.get('context'),
                    decision_result=decision_data.get('result'),
                    confidence_level=decision_data.get('confidence_level'),
                    energy_drink_consumed=decision_data.get('energy_drink_consumed', False),
                    optimization_applied=decision_data.get('optimization_applied', False),
                    shell_spinning_triggered=decision_data.get('shell_spinning_triggered', False),
                    raw_decision_data=decision_data
                )
                
                session.add(decision)
                await session.commit()
                return decision.id
                
        except Exception as e:
            self.logger.error(f"Failed to store decision: {e}")
            raise
    
    async def get_optimization_success_rate(self, user_id: int, days: int = 7):
        """Get optimization success rate - real fucking data only"""
        try:
            async with self.db_manager.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Get total optimizations
                total_result = await session.execute(
                    select(func.count(MethSnailOptimizationStats.id))
                    .where(MethSnailOptimizationStats.user_id == user_id)
                    .where(MethSnailOptimizationStats.timestamp >= cutoff_date)
                )
                total_optimizations = total_result.scalar()
                
                if total_optimizations == 0:
                    return {
                        'status': 'no_data',
                        'message': "No optimization data available - this snail hasn't had a chance to optimize shit yet!",
                        'success_rate': 0.0
                    }
                
                # Get successful optimizations
                success_result = await session.execute(
                    select(func.count(MethSnailOptimizationStats.id))
                    .where(MethSnailOptimizationStats.user_id == user_id)
                    .where(MethSnailOptimizationStats.timestamp >= cutoff_date)
                    .where(MethSnailOptimizationStats.optimization_success == True)
                )
                successful_optimizations = success_result.scalar()
                
                success_rate = (successful_optimizations / total_optimizations) * 100
                
                return {
                    'status': 'success',
                    'success_rate': success_rate,
                    'total_optimizations': total_optimizations,
                    'successful_optimizations': successful_optimizations,
                    'message': f"Success rate: {success_rate:.1f}% - not bad for a caffeinated fucking snail!"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get success rate: {e}")
            raise
    
    async def get_energy_drink_consumption(self, user_id: int, days: int = 7):
        """Get energy drink consumption stats - because priorities"""
        try:
            async with self.db_manager.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                result = await session.execute(
                    select(func.sum(MethSnailOptimizationStats.energy_drink_level))
                    .where(MethSnailOptimizationStats.user_id == user_id)
                    .where(MethSnailOptimizationStats.timestamp >= cutoff_date)
                )
                total_energy_drinks = result.scalar() or 0
                
                if total_energy_drinks == 0:
                    return {
                        'status': 'no_data',
                        'message': "No energy drink data - this snail must be fucking exhausted!",
                        'total_consumed': 0
                    }
                
                return {
                    'status': 'success',
                    'total_consumed': total_energy_drinks,
                    'message': f"Total energy drinks consumed: {total_energy_drinks} - this snail is WIRED!"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get energy drink consumption: {e}")
            raise
    
    async def get_shell_spin_statistics(self, user_id: int, days: int = 7):
        """Get shell spinning statistics - for when data is bad"""
        try:
            async with self.db_manager.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                result = await session.execute(
                    select(func.sum(MethSnailOptimizationStats.shell_spin_count))
                    .where(MethSnailOptimizationStats.user_id == user_id)
                    .where(MethSnailOptimizationStats.timestamp >= cutoff_date)
                )
                total_spins = result.scalar() or 0
                
                if total_spins == 0:
                    return {
                        'status': 'no_data',
                        'message': "No shell spinning data - this snail has been getting good data!",
                        'total_spins': 0
                    }
                
                return {
                    'status': 'success',
                    'total_spins': total_spins,
                    'message': f"Total shell spins: {total_spins} - this snail has seen some shit data!"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get shell spin statistics: {e}")
            raise