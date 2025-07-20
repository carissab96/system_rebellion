# agents/hamsters/hamsters_database_integration.py
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_decision_models import HamstersDecisionLog
from app.models.hamsters_model import HamstersEngineeringStats

class HamstersDatabaseIntegration:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
    async def store_engineering_metrics(self, user_id: int, metrics_data: dict):
        """Store engineering metrics - real data only"""
        try:
            async with self.db_manager.get_session() as session:
                engineering_stats = HamstersEngineeringStats(
                    user_id=user_id,
                    problem_type=metrics_data.get('problem_type'),
                    severity_level=metrics_data.get('severity_level'),
                    response_time_seconds=metrics_data.get('response_time_seconds'),
                    solution_applied=metrics_data.get('solution_applied'),
                    beer_consumption_ml=metrics_data.get('beer_consumption_ml', 0),
                    quantum_tape_used_meters=metrics_data.get('quantum_tape_used_meters', 0),
                    engineering_success=metrics_data.get('engineering_success', False),
                    raw_metrics=metrics_data
                )
                
                session.add(engineering_stats)
                await session.commit()
                return engineering_stats.id
                
        except Exception as e:
            self.logger.error(f"Failed to store engineering metrics: {e}")
            raise
    
    async def get_historical_engineering_data(self, user_id: int, days: int = 30):
        """Get historical engineering data - no bullshit"""
        try:
            async with self.db_manager.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                result = await session.execute(
                    select(HamstersEngineeringStats)
                    .where(HamstersEngineeringStats.user_id == user_id)
                    .where(HamstersEngineeringStats.timestamp >= cutoff_date)
                    .order_by(desc(HamstersEngineeringStats.timestamp))
                )
                
                historical_data = result.scalars().all()
                
                if not historical_data:
                    return {
                        'status': 'no_data',
                        'message': "No engineering data available - these hamsters haven't had problems to solve yet!"
                    }
                
                return {
                    'status': 'success',
                    'data': [
                        {
                            'timestamp': record.timestamp,
                            'problem_type': record.problem_type,
                            'severity_level': record.severity_level,
                            'response_time_seconds': record.response_time_seconds,
                            'solution_applied': record.solution_applied,
                            'beer_consumption_ml': record.beer_consumption_ml,
                            'quantum_tape_used_meters': record.quantum_tape_used_meters,
                            'engineering_success': record.engineering_success
                        } for record in historical_data
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get historical engineering data: {e}")
            raise
    
    async def store_decision(self, user_id: int, decision_data: dict):
        """Store engineering decision with full context"""
        try:
            async with self.db_manager.get_session() as session:
                decision = HamstersDecisionLog(
                    user_id=user_id,
                    decision_type=decision_data.get('decision_type'),
                    decision_context=decision_data.get('context'),
                    decision_result=decision_data.get('result'),
                    confidence_level=decision_data.get('confidence_level'),
                    beer_required=decision_data.get('beer_required', False),
                    quantum_tape_required=decision_data.get('quantum_tape_required', False),
                    emergency_response=decision_data.get('emergency_response', False),
                    raw_decision_data=decision_data
                )
                
                session.add(decision)
                await session.commit()
                return decision.id
                
        except Exception as e:
            self.logger.error(f"Failed to store decision: {e}")
            raise