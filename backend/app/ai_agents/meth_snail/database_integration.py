"""
Meth Snail Database Integration - Optimized for Speed and Reliability

Handles all database operations with zero tolerance for fake data.
Follows the same pattern as VIC-20 Sage for consistency.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union

from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models.agent_decision_models import MethSnailDecisionLog
from app.models.meth_snail_model import MethSnailOptimizationStats, MethSnailJitterLevels
from .data_types import OptimizationDecision, JitterLevel

logger = logging.getLogger("MethSnail.Database")

class MethSnailDatabaseIntegration:
    """
    Database integration for Meth Snail's optimization engine.
    
    Handles all database operations with the same pattern as VIC-20 Sage.
    No fallback behavior - operations either succeed or fail gracefully.
    """
    
    def __init__(self, db_getter=None):
        """Initialize with an optional database getter function"""
        self.db_getter = db_getter
        self.engine = None
        self.session_factory = None
        self._initialized = False
        self.logger = logging.getLogger("MethSnail.Database.Integration")

    async def initialize(self):
        """Initialize database connection with optimization precision"""
        if self._initialized:
            return
            
        if self.db_getter:
            # Use the provided database getter
            self.engine = await self.db_getter()
        else:
            # Fallback to direct engine creation (for testing/backward compatibility)
            from app.core.database import DATABASE_URL
            self.engine = create_async_engine(DATABASE_URL)
        
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self._initialized = True
        self.logger.info("Database integration initialized")

    async def store_optimization_metrics(self, user_id: int, metrics_data: dict) -> int:
        """
        Store optimization metrics with full context.
        Returns the ID of the created record.
        """
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
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
                await session.rollback()
                self.logger.error(f"Failed to store optimization metrics: {e}")
                raise

    async def get_historical_performance(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get historical performance data for the specified user.
        Returns a dictionary with status and data.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
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
                        'message': "No historical data available",
                        'data': []
                    }
                
                return {
                    'status': 'success',
                    'data': [
                        {
                            'timestamp': record.timestamp,
                            'cpu_improvement': record.cpu_usage_before - record.cpu_usage_after 
                                if record.cpu_usage_before and record.cpu_usage_after else None,
                            'memory_improvement': record.memory_usage_before - record.memory_usage_after 
                                if record.memory_usage_before and record.memory_usage_after else None,
                            'optimization_success': record.optimization_success,
                            'energy_drink_level': record.energy_drink_level,
                            'shell_spin_count': record.shell_spin_count
                        } for record in historical_data
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get historical performance: {e}")
            raise

    async def store_decision(self, user_id: int, decision_data: dict) -> int:
        """
        Store an optimization decision with full context.
        Returns the ID of the created decision log.
        """
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
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
                await session.rollback()
                self.logger.error(f"Failed to store decision: {e}")
                raise

    async def increment_shell_spin_count(self, user_id: int) -> None:
        """
        Increment the shell spin count for the given user.
        """
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                # Get or create stats for the user
                result = await session.execute(
                    select(MethSnailOptimizationStats)
                    .where(MethSnailOptimizationStats.user_id == user_id)
                    .order_by(desc(MethSnailOptimizationStats.timestamp))
                    .limit(1)
                )
                
                stats = result.scalar_one_or_none()
                
                if stats is None:
                    # Create new stats record if none exists
                    stats = MethSnailOptimizationStats(
                        user_id=user_id,
                        shell_spins_executed=1
                    )
                    session.add(stats)
                else:
                    # Increment existing count
                    stats.shell_spins_executed = (stats.shell_spins_executed or 0) + 1
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to increment shell spin count: {e}")
                raise

    async def get_jitter_levels(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent jitter level history for a user.
        Returns a list of jitter level records.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
                result = await session.execute(
                    select(MethSnailJitterLevels)
                    .where(MethSnailJitterLevels.user_id == user_id)
                    .order_by(desc(MethSnailJitterLevels.timestamp))
                    .limit(limit)
                )
                
                jitter_levels = result.scalars().all()
                return [
                    {
                        'timestamp': j.timestamp,
                        'current_jitter_level': j.current_jitter_level,
                        'caffeine_level_mg': j.caffeine_level_mg,
                        'focus_level': j.focus_level,
                        'energy_source': j.energy_source,
                        'jitter_trend': j.jitter_trend
                    } for j in jitter_levels
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get jitter levels: {e}")
            raise
            
    async def update_jitter_levels(self, user_id: int, jitter_data: Dict[str, Any]) -> int:
        """
        Update jitter levels and caffeine effects for a user.
        Returns the ID of the created record.
        """
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                jitter_level = MethSnailJitterLevels(
                    user_id=user_id,
                    current_jitter_level=jitter_data.get('current_jitter_level', 0.0),
                    peak_jitter_level=jitter_data.get('peak_jitter_level', 0.0),
                    baseline_jitter_level=jitter_data.get('baseline_jitter_level', 0.1),
                    caffeine_level_mg=jitter_data.get('caffeine_level_mg', 0.0),
                    is_decaffeinated=jitter_data.get('is_decaffeinated', False),
                    time_since_caffeine_minutes=jitter_data.get('time_since_caffeine_minutes'),
                    shell_spin_probability=jitter_data.get('shell_spin_probability', 0.05),
                    optimization_effectiveness=jitter_data.get('optimization_effectiveness'),
                    focus_level=jitter_data.get('focus_level', 0.5),
                    hypercaffeinated=jitter_data.get('hypercaffeinated', False),
                    requires_stick_intervention=jitter_data.get('requires_stick_intervention', False),
                    vic20_mediation_requested=jitter_data.get('vic20_mediation_requested', False),
                    energy_source=jitter_data.get('energy_source'),
                    jitter_trend=jitter_data.get('jitter_trend'),
                    raw_jitter_data=jitter_data.get('raw_jitter_data')
                )
                
                session.add(jitter_level)
                await session.commit()
                return jitter_level.id
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to update jitter levels: {e}")
                raise

    async def get_optimization_history(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent optimization history for a user.
        Returns a list of decision dictionaries.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
                result = await session.execute(
                    select(MethSnailDecisionLog)
                    .where(MethSnailDecisionLog.user_id == user_id)
                    .order_by(desc(MethSnailDecisionLog.timestamp))
                    .limit(limit)
                )
                
                decisions = result.scalars().all()
                return [
                    {
                        'id': d.id,
                        'timestamp': d.timestamp,
                        'decision_type': d.decision_type,
                        'confidence_level': d.confidence_level,
                        'optimization_applied': d.optimization_applied,
                        'shell_spinning_triggered': d.shell_spinning_triggered
                    } for d in decisions
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get optimization history: {e}")
            raise
