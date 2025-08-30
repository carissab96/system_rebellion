# app/ai_agents/sir_hawkington/database_integration.py
import asyncio
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc, and_, delete
import uuid
import logging

from app.models.agent_memory_banks import CentralMemoryBank
from .data_types import HawkingtonDecision
from .constants import AGENT_NAME, HawkingtonEventTypes

logger = logging.getLogger("SirHawkington.Database")

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

class HawkingtonDatabaseIntegration:
    """Database integration for Sir Hawkington's aristocratic central memory bank"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
    
    def _get_database_config(self) -> dict:
        """Get database configuration based on environment"""
        env = os.getenv('ENV', 'development').lower()
        
        if env == 'production':
            return {
                'url': os.getenv('DATABASE_URL'),
                'echo': False,
                'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
                'pool_pre_ping': True
            }
        elif env == 'test':
            return {
                'url': 'sqlite+aiosqlite:///:memory:',
                'echo': False,
                'connect_args': {"check_same_thread": False}
            }
        else:  # development
            return {
                'url': 'sqlite+aiosqlite:///./system_rebellion.db',
                'echo': True,
                'connect_args': {"check_same_thread": False}
            }
    
    async def initialize(self):
        """Initialize Sir Hawkington's distinguished database connection"""
        config = self._get_database_config()
    
        # Build engine kwargs based on what's in config
        engine_kwargs = {
            'echo': config.get('echo', False)
        }
    
        # Only add pool settings if they exist (PostgreSQL only)
        if 'pool_size' in config:
            engine_kwargs['pool_size'] = config['pool_size']
        if 'max_overflow' in config:
            engine_kwargs['max_overflow'] = config['max_overflow']
        if 'pool_recycle' in config:
            engine_kwargs['pool_recycle'] = config['pool_recycle']
        if 'pool_pre_ping' in config:
            engine_kwargs['pool_pre_ping'] = config['pool_pre_ping']
        if 'connect_args' in config:
            engine_kwargs['connect_args'] = config['connect_args']
    
        self.engine = create_async_engine(
            config['url'],
            **engine_kwargs
        )
    
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def store_metrics(self, user_id: str, metrics: Dict[str, Any]):
        """Sir Hawkington doesn't store metrics - he analyzes them"""
        pass
    
    async def store_decision(self, user_id: str, decision: HawkingtonDecision) -> str:
        """Store Sir Hawkington's aristocratic decision in central memory bank"""
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.ARISTOCRATIC_DECISION,
                    occurred_at=decision.timestamp,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="system_analysis",
                    subject_id=decision.decision_id,
                    details={
                        'decision_type': decision.decision_type,
                        'confidence': decision.confidence,
                        'reasoning': decision.reasoning,
                        'metrics': decision.metrics,
                        'system_impact': decision.system_impact
                    },
                    numeric_value=decision.confidence,
                    string_value=decision.decision_type,
                    priority=self._get_priority_for_decision(decision.decision_type),
                    never_forget=(decision.decision_type in ['critical', 'alert']),
                    agent_metadata={
                        'aristocratic_seal': True,
                        'decision_quality': 'distinguished',
                        'monocle_state': 'polished'
                    }
                )
                
                session.add(memory_entry)
                await session.commit()
                await session.refresh(memory_entry)
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Failed to store aristocratic decision: {str(e)}")
    
    async def store_monocle_yeet_incident(self, user_id: str, incident_data: Dict[str, Any]) -> str:
        """Store monocle yeet incident - Sir Hawkington's data quality rage"""
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.MONOCLE_YEET,
                    occurred_at=incident_data.get('timestamp', utc_now()),
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="data_quality_failure",
                    details={
                        'missing_metrics': incident_data.get('missing_metrics', []),
                        'invalid_metrics': incident_data.get('invalid_metrics', []),
                        'reason': incident_data.get('reason'),
                        'yeet_intensity': incident_data.get('yeet_intensity')
                    },
                    string_value=incident_data.get('yeet_intensity', 'concerned'),
                    priority=10,  # MAXIMUM - data quality is serious
                    never_forget=True,  # Never forget data quality failures
                    agent_metadata={
                        'monocle_state': 'yeeted',
                        'aristocratic_horror': True,
                        'data_integrity_enforced': True
                    }
                )
                
                session.add(memory_entry)
                await session.commit()
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Failed to store monocle yeet: {str(e)}")
    
    async def store_triage_decision(self, user_id: str, triage_data: Dict[str, Any]) -> str:
        """Store triage decision in central memory bank"""
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.TRIAGE_DECISION,
                    occurred_at=triage_data.get('timestamp', utc_now()),
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="system_triage",
                    details=triage_data,
                    numeric_value=triage_data.get('confidence', 0.0),
                    string_value=triage_data.get('triage_severity', 'normal'),
                    priority=self._get_priority_for_triage(triage_data.get('triage_severity')),
                    relevant_agents=','.join(triage_data.get('target_agents', [])),
                    never_forget=(triage_data.get('triage_severity') == 'emergency'),
                    agent_metadata={
                        'triage_commander': True,
                        'routing_decision': triage_data.get('routing_decision'),
                        'monocle_yeeted': triage_data.get('monocle_yeeted', False)
                    }
                )
                
                session.add(memory_entry)
                await session.commit()
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Failed to store triage decision: {str(e)}")
    
    async def get_historical_decisions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get Sir Hawkington's historical decisions from central memory bank"""
        async with self.session_factory() as session:
            try:
                cutoff_date = utc_now() - timedelta(days=days)
                
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == HawkingtonEventTypes.ARISTOCRATIC_DECISION,
                        CentralMemoryBank.occurred_at >= cutoff_date
                    )
                ).order_by(desc(CentralMemoryBank.occurred_at))
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                return [
                    {
                        'timestamp': memory.occurred_at,
                        'decision_type': memory.details.get('decision_type'),
                        'confidence_level': memory.details.get('confidence'),
                        'alert_parameters': {
                            'stress_score': memory.details.get('metrics', {}).get('stress_score', 0)
                        },
                        'technical_details': memory.details,
                        'user_acknowledged': False,
                        'issue_resolved': False
                    }
                    for memory in memories
                ]
                
            except Exception as e:
                raise Exception(f"🧐💥 Failed to get historical decisions: {str(e)}")
    
    async def get_triage_statistics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get triage statistics from central memory bank"""
        async with self.session_factory() as session:
            try:
                cutoff_date = utc_now() - timedelta(days=days)
                
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == HawkingtonEventTypes.TRIAGE_DECISION,
                        CentralMemoryBank.occurred_at >= cutoff_date
                    )
                ).order_by(desc(CentralMemoryBank.occurred_at))
                
                result = await session.execute(query)
                triage_decisions = result.scalars().all()
                
                if not triage_decisions:
                    return {'status': 'no_data', 'period_days': days}
                
                # Calculate statistics
                total_decisions = len(triage_decisions)
                successful_decisions = len([
                    d for d in triage_decisions 
                    if d.details.get('success', True)
                ])
                monocle_yeets = len([
                    d for d in triage_decisions 
                    if d.agent_metadata.get('monocle_yeeted', False)
                ])
                
                # Routing distribution
                routing_counts = {}
                severity_counts = {}
                confidence_values = []
                processing_times = []
                
                for decision in triage_decisions:
                    # Count routing types
                    routing = decision.agent_metadata.get('routing_decision', 'unknown')
                    routing_counts[routing] = routing_counts.get(routing, 0) + 1
                    
                    # Count severities
                    severity = decision.string_value
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    # Collect metrics
                    confidence = decision.numeric_value
                    if confidence:
                        confidence_values.append(confidence)
                    
                    processing_time = decision.details.get('processing_time')
                    if processing_time:
                        processing_times.append(processing_time)
                
                # Calculate averages
                avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
                avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
                
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
                    'latest_decision': triage_decisions[0].occurred_at.isoformat() if triage_decisions else None,
                    'aristocratic_status': 'DISTINGUISHED'
                }
                
            except Exception as e:
                raise Exception(f"🧐💥 Failed to get triage statistics: {str(e)}")
    
    async def get_hawkington_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get Sir Hawkington's performance metrics from central memory bank"""
        async with self.session_factory() as session:
            try:
                # Get decision count by type
                decisions = await session.execute(
                    select(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == HawkingtonEventTypes.ARISTOCRATIC_DECISION
                        )
                    )
                )
                
                decision_list = decisions.scalars().all()
                decision_breakdown = {}
                
                for decision in decision_list:
                    decision_type = decision.string_value
                    decision_breakdown[decision_type] = decision_breakdown.get(decision_type, 0) + 1
                
                # Get monocle yeet count
                yeet_count = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == HawkingtonEventTypes.MONOCLE_YEET
                        )
                    )
                )
                
                # Get triage decisions
                triage_count = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == HawkingtonEventTypes.TRIAGE_DECISION
                        )
                    )
                )
                
                return {
                    'total_decisions': sum(decision_breakdown.values()),
                    'decision_breakdown': decision_breakdown,
                    'monocle_yeets': yeet_count.scalar() or 0,
                    'triage_decisions': triage_count.scalar() or 0,
                    'aristocratic_effectiveness': self._calculate_effectiveness(decision_breakdown),
                    'hawkington_status': 'DISTINGUISHED_AND_OPERATIONAL'
                }
                
            except Exception as e:
                raise Exception(f"🧐💥 Failed to get performance metrics: {str(e)}")
    
    def _calculate_effectiveness(self, decision_breakdown: Dict[str, int]) -> float:
        """Calculate aristocratic effectiveness"""
        if not decision_breakdown:
            return 0.0
        
        # Weight decisions by severity
        effectiveness_weights = {
            'normal': 0.7,
            'concern': 0.8,
            'alert': 0.9,
            'critical': 1.0,
            'monocle_yeeted': 0.5  # Less effective when yeeting
        }
        
        total_weighted = sum(
            decision_breakdown.get(level, 0) * effectiveness_weights.get(level, 0.5)
            for level in decision_breakdown.keys()
        )
        total_decisions = sum(decision_breakdown.values())
        
        return total_weighted / total_decisions if total_decisions > 0 else 0.7
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data with aristocratic precision - keep important memories"""
        async with self.session_factory() as session:
            try:
                cutoff_date = utc_now() - timedelta(days=days_to_keep)
                
                # Only clean up low-priority, non-critical memories
                await session.execute(
                    delete(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.occurred_at < cutoff_date,
                            CentralMemoryBank.priority < 5,  # Only low priority
                            CentralMemoryBank.never_forget.is_(False),  # Proper boolean check
                            CentralMemoryBank.event_type.notin_([
                                HawkingtonEventTypes.MONOCLE_YEET,  # Keep all yeets
                                HawkingtonEventTypes.TRIAGE_DECISION  # Keep triage decisions
                            ])
                        )
                    )
                )
                
                await session.commit()
                logger.info(f"🧐 Cleaned up old memories with aristocratic precision")
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Memory cleanup failed: {str(e)}")
    
    def _get_priority_for_decision(self, decision_type: str) -> int:
        """Determine priority based on decision type"""
        priority_map = {
            'critical': 10,
            'alert': 8,
            'concern': 6,
            'normal': 4,
            'monocle_yeeted': 10  # Max priority for yeets
        }
        return priority_map.get(decision_type, 5)
    
    def _get_priority_for_triage(self, severity: str) -> int:
        """Determine priority based on triage severity"""
        priority_map = {
            'emergency': 10,
            'high': 8,
            'medium': 6,
            'normal': 4
        }
        return priority_map.get(severity, 5)