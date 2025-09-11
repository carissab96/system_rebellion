# app/ai_agents/sir_hawkington/database_integration.py
"""
Sir Hawkington Von Monitorious III Database Integration
Full 5-Table Architecture while preserving existing functionality
"""

import asyncio
import os
import json
import uuid
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc, and_, delete, text
import logging

from app.models.agent_memory_banks import CentralMemoryBank
from app.core.learning_helpers import (
    GlobalPattern, UserLearningPattern, LearningInteraction, PinnedMemory,
    upsert_global_pattern, upsert_user_pattern, record_learning_interaction,
    pin_memory, get_user_patterns, get_global_patterns, check_and_promote_pattern,
    get_pinned_memories, LearningTypes, MemoryTypes
)

from app.ai_agents.constants import AgentNames, PRIORITY_MAP
from app.ai_agents.sir_hawkington.data_types import HawkingtonDecision
from app.ai_agents.sir_hawkington.constants import AGENT_NAME, HawkingtonEventTypes
from app.utils.json_safety import to_json_safe
logger = logging.getLogger("SirHawkington.Database")

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO format string"""
    return dt.isoformat() if dt else None

class HawkingtonDatabaseIntegration:
    """
    Database integration for Sir Hawkington with full 5-table architecture
    Preserves existing functionality while adding pattern learning
    """
    
    def __init__(self, db_getter=None):
        self.engine = None
        self.session_factory = None
        self._initialized = False
        self.db_getter = db_getter
    
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
        if self._initialized:
            return
            
        config = self._get_database_config()
    
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
        
        self._initialized = True

    # === KEEP EXISTING CMB OPERATIONS AS-IS ===
    
    async def store_metrics(self, user_id: str, metrics: Dict[str, Any]):
        """Sir Hawkington doesn't store metrics - he analyzes them"""
        pass
    
    async def store_decision(self, user_id: str, decision: HawkingtonDecision) -> str:
        """Store Sir Hawkington's aristocratic decision in central memory bank"""
        async with self.session_factory() as session:
            try:
                memory_id = str(uuid.uuid4())
                
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.ARISTOCRATIC_DECISION.value,  # Add .value!
                    occurred_at=decision.timestamp,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    subject_kind="system_analysis",
                    subject_id=decision.decision_id,
                    details={
                        'decision_type': decision.decision_type,
                        'confidence': decision.confidence,
                        'reasoning': decision.reasoning,
                        'metrics': decision.metrics,
                        'system_impact': decision.system_impact
                    },
                    metadata_={  # Use metadata_ not metadata!
                        'aristocratic_seal': True,
                        'decision_quality': 'distinguished',
                        'monocle_state': 'polished'
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
                
                # Pin critical decisions
                if decision.decision_type in ['critical', 'alert']:
                    await self._pin_critical_decision(user_id, decision, memory_id)
                
                return memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Failed to store aristocratic decision: {str(e)}")
    
    async def store_monocle_yeet_incident(self, user_id: str, incident_data: Dict[str, Any]) -> str:
        """Store monocle yeet incident - Sir Hawkington's data quality rage"""
        async with self.session_factory() as session:
            try:
                memory_id = str(uuid.uuid4())
                
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.MONOCLE_YEET.value,  # Add .value!
                    occurred_at=incident_data.get('timestamp', datetime.now(timezone.utc)),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    subject_kind="data_quality_failure",
                    details={
                        'missing_metrics': incident_data.get('missing_metrics', []),
                        'invalid_metrics': incident_data.get('invalid_metrics', []),
                        'reason': incident_data.get('reason'),
                        'yeet_intensity': incident_data.get('yeet_intensity')
                    },
                    metadata_={  # Use metadata_ not metadata!
                        'monocle_state': 'yeeted',
                        'aristocratic_horror': True,
                        'data_integrity_enforced': True
                    },
                    string_value=incident_data.get('yeet_intensity', 'concerned'),
                    priority=10,  # MAXIMUM - data quality is serious
                    never_forget=True,
                    agent_metadata={
                        'monocle_state': 'yeeted',
                        'aristocratic_horror': True,
                        'data_integrity_enforced': True
                    }
                )
                
                session.add(memory_entry)
                await session.commit()
                
                # Always pin monocle yeets - they're important!
                await self._pin_monocle_yeet(user_id, incident_data, memory_id)
                
                return memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Failed to store monocle yeet: {str(e)}")
    
       
    async def store_triage_decision(self, user_id: str, triage_data: Dict[str, Any]) -> str:
        """Store triage decision in central memory bank (JSON-safe blobs; real datetimes)."""
        async with self.session_factory() as session:
            try:
                memory_id = str(uuid.uuid4())
                
                def _coerce_dt(v: Any) -> datetime:
                    """Return a timezone-aware datetime (UTC) from various inputs; never returns a string."""
                    if isinstance(v, datetime):
                        # normalize to aware UTC
                        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
                    if isinstance(v, (int, float)):
                        # epoch seconds
                        return datetime.fromtimestamp(float(v), tz=timezone.utc)
                    if isinstance(v, str):
                        s = v.strip()
                        try:
                            # handle trailing Z
                            if s.endswith("Z"):
                                s = s[:-1] + "+00:00"
                            return datetime.fromisoformat(s)
                        except Exception:
                            # last resort: now
                            return datetime.now(timezone.utc)
                    # last resort: now
                    return datetime.now(timezone.utc)
                # --- DateTimes: must be real datetime objects for DB DateTime columns
                occurred_at_dt = _coerce_dt(triage_data.get("timestamp"))
                now_dt = datetime.now(timezone.utc)

                # --- Numeric value: only store finite numbers; else None (no fake data)
                conf = triage_data.get("confidence")
                numeric_value = float(conf) if isinstance(conf, (int, float)) and math.isfinite(float(conf)) else None

                # --- Priority derived from severity (your helper)
                priority_val = self._get_priority_for_triage(triage_data.get("triage_severity"))

                # --- JSON fields: sanitize ONLY the JSON blobs
                details_safe = to_json_safe(triage_data)
                metadata_safe = to_json_safe({
                    "triage_commander": True,
                    "routing_decision": triage_data.get("routing_decision"),
                    "monocle_yeeted": triage_data.get("monocle_yeeted", False),
                })
                agent_metadata_safe = to_json_safe({
                    "triage_commander": True,
                    "routing_decision": triage_data.get("routing_decision"),
                    "monocle_yeeted": triage_data.get("monocle_yeeted", False),
                })

                # relevant_agents should be a JSON array (list), not a JSON string
                agents_val = triage_data.get("target_agents", [])
                if isinstance(agents_val, (list, tuple, set)):
                    agents_list = list(agents_val)
                elif isinstance(agents_val, str):
                    agents_list = [agents_val]
                else:
                    agents_list = []
                relevant_agents_json = json.dumps(to_json_safe(agents_list))

                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.TRIAGE_DECISION.value,
                    occurred_at=occurred_at_dt,    # REAL datetime
                    created_at=now_dt,             # REAL datetime
                    updated_at=now_dt,             # REAL datetime
                    subject_kind="system_triage",

                    # JSON columns (sanitized)
                    details=details_safe,
                    metadata_=metadata_safe,       # NOTE: metadata_ not metadata
                    agent_metadata=agent_metadata_safe,
                    relevant_agents=relevant_agents_json,

                    numeric_value=numeric_value,   # float or None
                    string_value=triage_data.get("triage_severity") or None,
                    priority=priority_val,
                    never_forget=(triage_data.get("triage_severity") in ("emergency", "high")),
                )

                session.add(memory_entry)
                await session.commit()

                # Optional follow-ups (unchanged semantics)
                if triage_data.get("triage_severity") in ("emergency", "high"):
                    await self._pin_triage_decision(user_id, triage_data, memory_id)

                await self.record_triage_learning(
                    user_id,
                    triage_data,
                    triage_data.get("success", 1.0),
                    memory_id,
                )

                return memory_id
            
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Failed to store triage decision: {str(e)}")
    
    # Add this missing method for the websocket handler
    async def store_hawkington_decision(self, user_id: str, decision: HawkingtonDecision) -> str:
        """Alias for store_decision to match websocket expectations"""
        return await self.store_decision(user_id, decision)
    
    # === KEEP EXISTING RETRIEVAL METHODS ===
    
    async def get_historical_decisions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get Sir Hawkington's historical decisions from central memory bank"""
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == HawkingtonEventTypes.ARISTOCRATIC_DECISION.value,
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
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == HawkingtonEventTypes.TRIAGE_DECISION.value,
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
                            CentralMemoryBank.event_type == HawkingtonEventTypes.ARISTOCRATIC_DECISION.value
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
                            CentralMemoryBank.event_type == HawkingtonEventTypes.MONOCLE_YEET.value
                        )
                    )
                )
                
                # Get triage decisions
                triage_count = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == HawkingtonEventTypes.TRIAGE_DECISION.value
                        )
                    )
                )
                
                # Get observation count for pattern learning
                observation_count = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == HawkingtonEventTypes.BEHAVIOR_OBSERVED.value
                        )
                    )
                )
                
                return {
                    'total_decisions': sum(decision_breakdown.values()),
                    'decision_breakdown': decision_breakdown,
                    'monocle_yeets': yeet_count.scalar() or 0,
                    'triage_decisions': triage_count.scalar() or 0,
                    'observation_count': observation_count.scalar() or 0,
                    'aristocratic_effectiveness': self._calculate_effectiveness(decision_breakdown),
                    'hawkington_status': 'DISTINGUISHED_AND_OPERATIONAL'
                }
                
            except Exception as e:
                raise Exception(f"🧐💥 Failed to get performance metrics: {str(e)}")
    
    # === NEW PATTERN LEARNING OPERATIONS ===
    
    async def store_user_behavior_observation(
        self, 
        user_id: str, 
        observation_data: Dict[str, Any]
    ) -> None:
        """Store user behavior observation for pattern learning"""
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.BEHAVIOR_OBSERVED.value,
                    occurred_at=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    subject_kind="behavior_observation",
                    details=observation_data,
                    metadata_={
                        'observation_type': 'triage_behavior',
                        'learning_eligible': True
                    },
                    priority=1,  # Routine observation
                    tags=json.dumps(["observation", "learning"])
                )
                
                session.add(memory_entry)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to store observation: {str(e)}")
    
    async def analyze_and_learn_patterns(
        self,
        user_id: str,
        min_observations: int = 25  # Lower for Hawkington since triage is less frequent
    ) -> Optional[Dict[str, Any]]:
        """Analyze triage patterns and learn user preferences"""
        async with self.session_factory() as session:
            try:
                cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                
                # Get observations
                result = await session.execute(
                    select(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == HawkingtonEventTypes.BEHAVIOR_OBSERVED.value,
                            CentralMemoryBank.occurred_at >= cutoff
                        )
                    ).order_by(desc(CentralMemoryBank.occurred_at)).limit(min_observations * 2)
                )
                
                observations = result.scalars().all()
                
                if len(observations) < min_observations:
                    return None
                
                # Analyze patterns
                pattern_analysis = self._analyze_triage_patterns(observations)
                
                if pattern_analysis["confidence"] > 0.7:
                    # Create pattern
                    pattern = UserLearningPattern(
                        user_id=user_id,
                        pattern_id=f"{user_id}_hawkington_pattern_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
                        timestamp=datetime.now(timezone.utc),
                        interaction_pattern={
                            "preferred_triage_categories": pattern_analysis["preferred_categories"],
                            "typical_issue_severity": pattern_analysis["avg_severity"],
                            "monocle_yeet_triggers": pattern_analysis["yeet_triggers"]
                        },
                        learning_preference={
                            "response_style": "aristocratic",
                            "detail_level": pattern_analysis["detail_preference"]
                        },
                        response_patterns={
                            "avg_confidence": pattern_analysis["avg_confidence"],
                            "decision_distribution": pattern_analysis["decision_types"]
                        },
                        most_effective_agent=AGENT_NAME,
                        complexity_tolerance=pattern_analysis["complexity_score"]
                    )
                    
                    await upsert_user_pattern(self.engine, pattern)
                    
                    # Check promotion
                    if pattern_analysis["confidence"] > 0.9:
                                                await check_and_promote_pattern(
                            self.engine,
                            pattern.pattern_id,
                            confidence_threshold=0.9,
                            cross_validation_count=5
                        )
                    
                    return pattern_analysis
                
                return None
                
            except Exception as e:
                logger.error(f"Pattern learning failed: {str(e)}")
                return None
    
    async def check_pattern_match(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check if current context matches known patterns"""
        # Get user patterns
        user_patterns = await get_user_patterns(self.engine, user_id)
        
        # Get global patterns
        global_patterns = await get_global_patterns(self.engine)
        
        best_match = None
        highest_confidence = 0.0
        
        # Check user patterns first
        for pattern in user_patterns:
            if pattern.get("most_effective_agent") == AGENT_NAME:
                match_score = self._calculate_pattern_match_score(
                    context,
                    pattern.get("interaction_pattern", {})
                )
                
                if match_score > highest_confidence:
                    highest_confidence = match_score
                    best_match = {
                        "pattern_type": "user",
                        "pattern_id": pattern["pattern_id"],
                        "confidence": match_score,
                        "recommendations": self._generate_pattern_recommendations(pattern)
                    }
        
        # Check global patterns if no strong user match
        if highest_confidence < 0.8:
            for pattern_key, pattern_data in global_patterns.items():
                if "hawkington" in pattern_key.lower():
                    pattern_value = pattern_data.get("value", {})
                    match_score = self._calculate_pattern_match_score(context, pattern_value)
                    
                    if match_score > highest_confidence:
                        highest_confidence = match_score
                        best_match = {
                            "pattern_type": "global",
                            "pattern_key": pattern_key,
                            "confidence": match_score,
                            "recommendations": self._generate_pattern_recommendations(pattern_value)
                        }
        
        return best_match if highest_confidence > 0.6 else None
    
    # === CROSS-AGENT LEARNING OPERATIONS ===
    
    async def share_triage_wisdom(
        self,
        target_agent: str,
        wisdom_type: str,
        wisdom_data: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Share triage wisdom with other agents"""
        interaction = LearningInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            source_agent=AGENT_NAME,
            target_agent=target_agent,
            source_memory_id=source_memory_id,
            learning_type="triage_expertise",
            adaptation_method={
                "wisdom_type": wisdom_type,
                "triage_approach": wisdom_data.get("approach"),
                "severity_thresholds": wisdom_data.get("thresholds")
            },
            application_context={
                "sharing_reason": wisdom_data.get("reason"),
                "expected_benefit": "improved_triage_accuracy"
            },
            transfer_success=None,
            effectiveness_score=None
        )
        
        await record_learning_interaction(self.engine, interaction)
    
    async def record_triage_learning(
        self,
        user_id: str,
        triage_data: Dict[str, Any],
        effectiveness: float,
        source_memory_id: str
    ) -> None:
        """Record learning from triage decisions"""
        interaction = LearningInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            source_agent=AGENT_NAME,
            target_agent="all_agents",
            source_memory_id=source_memory_id,
            learning_type="triage_pattern",
            adaptation_method={
                "severity": triage_data.get("triage_severity"),
                "routing": triage_data.get("routing_decision"),
                "confidence": triage_data.get("confidence")
            },
            application_context={
                "system_state": triage_data.get("system_state"),
                "triage_reasoning": triage_data.get("reasoning")
            },
            transfer_success=effectiveness > 0.7,
            effectiveness_score=effectiveness,
            validated_by_stick=False,
            cross_validation_count=1
        )
        
        await record_learning_interaction(self.engine, interaction)
    
    # === PINNED MEMORY OPERATIONS ===
    
    async def _pin_critical_decision(
        self,
        user_id: str,
        decision: HawkingtonDecision,
        source_memory_id: str
    ) -> None:
        """Pin critical triage decisions"""
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type="critical_triage",
            content={
                "decision_type": decision.decision_type,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "metrics": decision.metrics,
                "system_impact": decision.system_impact
            },
            importance=5 if decision.decision_type == "critical" else 4,
            timestamp=decision.timestamp,
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    async def _pin_monocle_yeet(
        self,
        user_id: str,
        incident_data: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Pin monocle yeet incidents - they're important!"""
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type="monocle_yeet",
            content={
                "reason": incident_data.get("reason"),
                "missing_metrics": incident_data.get("missing_metrics", []),
                "invalid_metrics": incident_data.get("invalid_metrics", []),
                "yeet_intensity": incident_data.get("yeet_intensity")
            },
            importance=5,  # Always high importance
            timestamp=incident_data.get("timestamp", datetime.now(timezone.utc)),
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    async def _pin_triage_decision(
        self,
        user_id: str,
        triage_data: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Pin important triage decisions"""
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type="triage_decision",
            content={
                "severity": triage_data.get("triage_severity"),
                "routing": triage_data.get("routing_decision"),
                "target_agents": triage_data.get("target_agents"),
                "reasoning": triage_data.get("reasoning"),
                "confidence": triage_data.get("confidence")
            },
            importance=4,
            timestamp=triage_data.get("timestamp", datetime.now(timezone.utc)),
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    # === METADATA CONTRIBUTION ===
    
    async def contribute_to_metadata_rollup(self) -> Dict[str, int]:
        """Contribute Hawkington's memory counts for metadata rollup"""
        async with self.session_factory() as session:
            # Count recent memories
            result = await session.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM central_memory_bank
                    WHERE agent_name = :agent_name
                        AND occurred_at >= :cutoff
                """),
                {
                    "agent_name": AGENT_NAME,
                    "cutoff": datetime.now(timezone.utc) - timedelta(minutes=5)
                }
            )
            
            count = result.scalar() or 0
            
            return {
                "hawkington_memories": count,
                "triage_events": count
            }
    
    # === HELPER METHODS ===
    
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
    
    def _analyze_triage_patterns(
        self,
        observations: List[Any]
    ) -> Dict[str, Any]:
        """Analyze observations for triage patterns"""
        import statistics
        
        analysis = {
            "observation_count": len(observations),
            "confidence": 0.0,
            "preferred_categories": [],
            "avg_severity": 0.0,
            "yeet_triggers": [],
            "avg_confidence": 0.0,
            "decision_types": {},
            "detail_preference": "aristocratic",
            "complexity_score": 0.7
        }
        
        if not observations:
            return analysis
        
        # Analyze patterns
        severities = []
        confidences = []
        categories = {}
        yeet_count = 0
        
        for obs in observations:
            details = obs.details or {}
            metadata = obs.metadata_ or {}
            
            # Track severities
            severity = details.get("severity", "normal")
            severities.append({"normal": 1, "medium": 2, "high": 3, "emergency": 4}.get(severity, 1))
            
            # Track confidence
            confidence = obs.numeric_value or 0.5
            confidences.append(confidence)
            
            # Track categories
            category = details.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
            
            # Track yeets
            if metadata.get("monocle_yeeted"):
                yeet_count += 1
        
        # Calculate analysis
        if observations:
            analysis["avg_severity"] = sum(severities) / len(severities)
            analysis["avg_confidence"] = sum(confidences) / len(confidences)
            analysis["preferred_categories"] = [
                cat for cat, count in categories.items()
                if count > len(observations) * 0.2
            ]
            
            if yeet_count > 0:
                analysis["yeet_triggers"] = ["data_quality_issues"]
            
            # Confidence based on consistency
            severity_variance = statistics.variance(severities) if len(severities) > 1 else 0
            analysis["confidence"] = 0.9 - (severity_variance * 0.2)
            analysis["confidence"] = max(0.5, min(1.0, analysis["confidence"]))
        
        return analysis
    
    def _calculate_pattern_match_score(
        self,
        context: Dict[str, Any],
        pattern: Dict[str, Any]
    ) -> float:
        """Calculate pattern match score"""
        score = 0.0
        factors = 0
        
        # Check severity match
        if "severity" in context and "typical_issue_severity" in pattern:
            severity_diff = abs(context["severity"] - pattern["typical_issue_severity"])
            score += (1 - severity_diff / 4) * 0.3
            factors += 0.3
        
        # Check metric ranges
        if "metrics" in context and "metric_thresholds" in pattern:
            matching_thresholds = 0
            total_thresholds = 0
            
            for metric, value in context["metrics"].items():
                if metric in pattern["metric_thresholds"]:
                    threshold = pattern["metric_thresholds"][metric]
                    if value >= threshold["min"] and value <= threshold["max"]:
                        matching_thresholds += 1
                    total_thresholds += 1
            
            if total_thresholds > 0:
                score += (matching_thresholds / total_thresholds) * 0.4
            factors += 0.4
        
        # Check time patterns
        if "time_of_day" in context and "peak_hours" in pattern:
            hour = context["time_of_day"]
            if hour in pattern["peak_hours"]:
                score += 0.3
            factors += 0.3
        
        return score / factors if factors > 0 else 0.0
    
    def _generate_pattern_recommendations(
        self,
        pattern: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on pattern"""
        recommendations = []
        
        if "preferred_categories" in pattern:
            recommendations.append(
                f"Focus on {', '.join(pattern['preferred_categories'])} issues"
            )
        
        if "typical_issue_severity" in pattern:
            severity = pattern["typical_issue_severity"]
            if severity > 2.5:
                recommendations.append("🧐 Prepare for high-severity triage decisions")
            elif severity < 1.5:
                recommendations.append("🧐 Expect routine operations")
        
        if "monocle_yeet_triggers" in pattern and pattern["monocle_yeet_triggers"]:
            recommendations.append("🧐 Ensure data quality to prevent monocle yeeting")
        
        return recommendations
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data with aristocratic precision - keep important memories"""
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
                
                # Only clean up low-priority, non-critical memories
                await session.execute(
                    delete(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.occurred_at < cutoff_date,
                            CentralMemoryBank.priority < 5,  # Only low priority
                            CentralMemoryBank.never_forget.is_(False),
                            CentralMemoryBank.event_type.notin_([
                                HawkingtonEventTypes.MONOCLE_YEET.value,  # Keep all yeets
                                HawkingtonEventTypes.TRIAGE_DECISION.value  # Keep triage decisions
                            ])
                        )
                    )
                )
                
                await session.commit()
                logger.info(f"🧐 Cleaned up old memories with aristocratic precision")
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"🧐💥 Memory cleanup failed: {str(e)}")
    
    async def get_database_health(self) -> Dict[str, Any]:
        """Get database health status"""
        try:
            async with self.session_factory() as session:
                # Simple health check query
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                return {
                    "status": "healthy",
                    "connection": "active",
                    "initialized": self._initialized
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self._initialized
            }