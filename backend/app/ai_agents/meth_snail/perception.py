#!/usr/bin/env python3
"""
Terry's Perception Layer - Gathering Full System Context

Collects:
- Current system metrics (CPU, memory, disk, network)
- Historical patterns from database
- Recent actions and their outcomes
- VIC-20's recommendation and reasoning

Personality Behaviors:
- Shell spins when data is missing or invalid (NO FAKE DATA)
- Tracks data quality for decision confidence
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.agent_learning import AgentLearningRecord
from .situation_fingerprint import SituationFingerprint
from .data_types import ShellSpinIncident

logger = logging.getLogger('TerryPerception')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class PerceptionContext:
    """Everything Terry needs to perceive the situation"""
    
    # Full system metrics
    full_metrics: Dict[str, Any]
    
    # Coordination request context
    resource_type: str
    current_value: float
    threshold: float
    severity: str
    vic20_recommendation: Dict[str, Any]
    
    # Historical context
    similar_situations: List[Dict[str, Any]] = field(default_factory=list)
    recent_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Agent state
    agent_state: Dict[str, Any] = field(default_factory=dict)
    override_success_rate: float = 0.5
    
    # Timestamp
    timestamp: str = field(default_factory=lambda: utc_now().isoformat())


class TerryPerception:
    """
    Terry's perception system - gathering all context for decision-making.
    
    🐌💨 "I SEE EVERYTHING NOW! Not just 'CPU high' but WHY it's high!"
    """
    
    def __init__(self, db_session, agent_state: Dict[str, Any]):
        """
        Initialize perception system.
        
        Args:
            db_session: AsyncSession for database queries
            agent_state: Current agent personality metrics (includes shell_spin tracking)
        """
        self.db = db_session
        self.agent_state = agent_state
        self.logger = logger
        self.shell_spin_incidents: List[ShellSpinIncident] = []
        
        self.logger.info("🐌👁️ Terry's perception system initialized - ready to see EVERYTHING")
    
    async def perceive(
        self,
        coordination_request: Dict[str, Any]
    ) -> PerceptionContext:
        """
        Gather full context for decision-making.
        
        This is where Terry goes from seeing:
            "CPU is at 85%"
        
        To seeing:
            "CPU is at 85% because Python process is using 8GB RAM,
             swap is at 90%, disk I/O is 500MB/s, and last time this
             happened, restarting the service worked better than cache clear"
        
        Args:
            coordination_request: Request from VIC-20 with basic info
            
        Returns:
            PerceptionContext with full situational awareness
            
        Raises:
            Exception: If critical metrics are unavailable (NO FAKE DATA)
        """
        self.logger.info("🐌🔍 Terry perceiving situation...")
        self.logger.debug(f"   Coordination request: {coordination_request.get('resource_type')} at {coordination_request.get('current_value')}")
        
        try:
            # 1. GET FULL SYSTEM METRICS
            full_metrics = await self._get_full_metrics(coordination_request)
            
            if not full_metrics:
                raise Exception("Full metrics unavailable - cannot make informed decision")
            
            self.logger.info(f"   ✓ Got full metrics: {len(str(full_metrics))} chars of data")
            
            # 2. QUERY HISTORICAL PATTERNS
            similar_situations = await self._find_similar_situations(
                resource_type=coordination_request.get('resource_type'),
                severity=coordination_request.get('severity')
            )
            
            self.logger.info(f"   ✓ Found {len(similar_situations)} similar past situations")
            
            # 3. GET RECENT ACTIONS
            recent_actions = await self._get_recent_actions(limit=10)
            
            self.logger.info(f"   ✓ Retrieved {len(recent_actions)} recent actions")
            
            # 4. BUILD CONTEXT
            # Extract basic info from coordination request
            resource_type = coordination_request.get('resource_type', 'unknown')
            severity = coordination_request.get('severity', 'unknown')
            current_value = coordination_request.get('current_value', 0)
            threshold = coordination_request.get('threshold', 0)
            vic20_recommendation = coordination_request.get('recommendation', {})
            full_metrics = coordination_request.get('full_metrics', {})
            
            # Check data quality - shell spin if bad data (NO FAKE DATA)
            missing_metrics = []
            invalid_metrics = []
            
            if not full_metrics:
                missing_metrics.append('full_metrics')
            else:
                # Validate critical metrics exist
                required = ['cpu_usage', 'memory_usage', 'disk_usage']
                for metric in required:
                    if metric not in full_metrics:
                        missing_metrics.append(metric)
                    elif full_metrics[metric] is None or full_metrics[metric] < 0:
                        invalid_metrics.append(metric)
            
            # SHELL SPIN if data is bad
            if missing_metrics or invalid_metrics:
                await self._trigger_shell_spin(
                    missing_metrics=missing_metrics,
                    invalid_metrics=invalid_metrics,
                    reason=f"Bad data in coordination request: missing={missing_metrics}, invalid={invalid_metrics}"
                )
            
            # Continue with degraded data - Terry will note low confidence
            context = PerceptionContext(
                full_metrics=full_metrics,
                resource_type=resource_type,
                current_value=current_value,
                threshold=threshold,
                severity=severity,
                vic20_recommendation=vic20_recommendation,
                similar_situations=similar_situations,
                recent_actions=recent_actions,
                agent_state=self.agent_state,
                override_success_rate=self.agent_state.get('override_success_rate', 0.5),
                timestamp=utc_now().isoformat(),
                shell_spin_count=len(self.shell_spin_incidents),
                data_quality_score=self._calculate_data_quality(
                    missing_metrics=missing_metrics,
                    invalid_metrics=invalid_metrics
                )
            )
            
            self.logger.info("🐌✅ Perception complete - Terry sees the full picture!")
            return context
            
        except Exception as e:
            self.logger.error(f"🐌💥 Perception failed: {e}", exc_info=True)
            raise
    
    async def _trigger_shell_spin(
        self,
        missing_metrics: List[str],
        invalid_metrics: List[str],
        reason: str
    ) -> None:
        """
        🐌💫 SHELL SPIN - Terry's reaction to bad data.
        
        NO FAKE DATA: When metrics are missing or invalid, Terry spins his shell
        and waits. This is tracked and visible in logs/database.
        """
        incident = ShellSpinIncident(
            timestamp=utc_now(),
            missing_metrics=missing_metrics,
            invalid_metrics=invalid_metrics,
            reason=reason,
            user_id=None  # Will be set by caller if available
        )
        
        self.shell_spin_incidents.append(incident)
        
        self.logger.warning(
            f"🐌💫 SHELL SPIN #{len(self.shell_spin_incidents)}: {reason}\n"
            f"   Missing: {missing_metrics}\n"
            f"   Invalid: {invalid_metrics}"
        )
        
        # Store in database for learning
        try:
            from .database_integration import MethSnailDatabaseIntegration
            db_integration = MethSnailDatabaseIntegration(lambda: self.db)
            await db_integration.store_shell_spin_incident(
                user_id="system",  # TODO: Get real user_id
                incident=incident
            )
        except Exception as e:
            self.logger.error(f"🐌💥 Failed to store shell spin: {e}")
    
    def _calculate_data_quality(
        self,
        missing_metrics: List[str],
        invalid_metrics: List[str]
    ) -> float:
        """
        Calculate data quality score (0.0 to 1.0).
        
        Perfect data = 1.0
        Missing/invalid metrics = penalties
        """
        total_expected = 10  # Rough estimate of expected metrics
        penalties = len(missing_metrics) + len(invalid_metrics)
        
        quality = max(0.0, 1.0 - (penalties / total_expected))
        
        return quality
    
    async def _get_full_metrics(
        self,
        coordination_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get full system metrics from SimplifiedMetricsService.
        
        VIC-20 should pass these in the coordination request.
        If not, we need to fetch them ourselves.
        
        Returns:
            Full metrics dictionary with CPU, memory, disk, network data
            
        Raises:
            Exception: If metrics unavailable
        """
        # Check if VIC-20 passed full metrics
        if 'full_metrics' in coordination_request:
            self.logger.debug("   📦 Using full metrics from VIC-20")
            return coordination_request['full_metrics']
        
        # Otherwise, fetch from SimplifiedMetricsService
        self.logger.debug("   🔄 Fetching metrics from SimplifiedMetricsService")
        
        try:
            from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
            
            metrics_service = await SimplifiedMetricsService.get_instance()
            full_metrics = await metrics_service.get_metrics()
            
            if not full_metrics:
                raise Exception("SimplifiedMetricsService returned no data")
            
            return full_metrics
            
        except Exception as e:
            self.logger.error(f"   💥 Failed to fetch metrics: {str(e)}")
            raise Exception(f"Cannot get full metrics: {str(e)}")
    
    async def _find_similar_situations(
        self,
        resource_type: str,
        severity: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Query historical learning records for similar situations.
        
        This will use hierarchical fingerprinting once we have learning data.
        For now, query by resource_type and severity.
        
        Args:
            resource_type: 'cpu', 'memory', 'disk', 'network'
            severity: 'low', 'medium', 'high', 'critical'
            limit: Max records to return
            
        Returns:
            List of similar past situations with outcomes
        """
        try:
            from sqlalchemy import select, and_
            from app.models.agent_learning import AgentLearningRecord
            
            # Query for similar situations
            # Start broad (Level 1 fingerprint equivalent)
            query = select(AgentLearningRecord).where(
                and_(
                    AgentLearningRecord.agent_name == 'meth_snail',
                    AgentLearningRecord.resource_type == resource_type,
                    AgentLearningRecord.severity == severity
                )
            ).order_by(
                AgentLearningRecord.created_at.desc()
            ).limit(limit)
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            # Convert to dictionaries
            similar = []
            for record in records:
                similar.append({
                    'fingerprint_l1': record.fingerprint_l1,
                    'fingerprint_l2': record.fingerprint_l2,
                    'fingerprint_l3': record.fingerprint_l3,
                    'root_cause': record.root_cause,
                    'action': record.action,
                    'success': record.success,
                    'confidence': record.confidence,
                    'improvement': record.improvement,
                    'created_at': record.created_at.isoformat()
                })
            
            return similar
            
        except ImportError:
            # Model doesn't exist yet - return empty list
            self.logger.debug("   ⚠️ AgentLearningRecord model not yet available")
            return []
        except Exception as e:
            self.logger.warning(f"   ⚠️ Failed to query similar situations: {str(e)}")
            return []
    
    async def _get_recent_actions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get Terry's recent actions from coordination_decisions table.
        
        Args:
            limit: Number of recent actions to retrieve
            
        Returns:
            List of recent actions with outcomes
        """
        try:
            from sqlalchemy import select
            from app.models.coordination import CoordinationDecision
            
            query = select(CoordinationDecision).where(
                CoordinationDecision.agent_name == 'meth_snail'
            ).order_by(
                CoordinationDecision.created_at.desc()
            ).limit(limit)
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            recent = []
            for record in records:
                recent.append({
                    'action': record.action_taken,
                    'resource_type': record.resource_type,
                    'success': record.success,
                    'created_at': record.created_at.isoformat()
                })
            
            return recent
            
        except Exception as e:
            self.logger.warning(f"   ⚠️ Failed to query recent actions: {str(e)}")
            return []
    
    def summarize_perception(self, context: PerceptionContext) -> str:
        """
        Generate human-readable summary of what Terry perceives.
        
        Useful for logging and debugging.
        
        Args:
            context: PerceptionContext to summarize
            
        Returns:
            Natural language summary
        """
        metrics = context.full_metrics
        
        summary_parts = [
            f"🐌👁️ TERRY'S PERCEPTION:",
            f"",
            f"SITUATION:",
            f"  {context.resource_type.upper()} at {context.current_value:.1f} (threshold: {context.threshold})",
            f"  Severity: {context.severity}",
            f"",
            f"SYSTEM STATE:"
        ]
        
        # CPU details
        if 'cpu' in metrics:
            cpu = metrics['cpu']
            summary_parts.append(f"  CPU: {cpu.get('usage_percent', 0):.1f}%")
            top_procs = cpu.get('top_processes', [])
            if top_procs:
                top = top_procs[0]
                summary_parts.append(f"    Top process: {top.get('name')} using {top.get('cpu_percent', 0):.1f}% CPU")
        
        # Memory details
        if 'memory' in metrics:
            mem = metrics['memory']
            summary_parts.append(f"  Memory: {mem.get('percent', 0):.1f}%")
            swap = mem.get('swap_percent', 0)
            if swap > 0:
                summary_parts.append(f"    Swap: {swap:.1f}% (⚠️ THRASHING!)")
        
        # Disk details
        if 'disk' in metrics:
            disk = metrics['disk']
            summary_parts.append(f"  Disk: {disk.get('percent', 0):.1f}%")
            io = disk.get('read_bytes', 0) + disk.get('write_bytes', 0)
            if io > 1000000000:  # > 1GB
                summary_parts.append(f"    I/O: {io / 1000000000:.2f} GB (⚠️ HIGH!)")
        
        # Historical context
        summary_parts.append(f"")
        summary_parts.append(f"HISTORICAL CONTEXT:")
        summary_parts.append(f"  Similar situations seen: {len(context.similar_situations)}")
        summary_parts.append(f"  Recent actions taken: {len(context.recent_actions)}")
        
        # VIC-20's recommendation
        summary_parts.append(f"")
        summary_parts.append(f"VIC-20 RECOMMENDS:")
        summary_parts.append(f"  {context.vic20_recommendation.get('action', 'unknown')}")
        summary_parts.append(f"  Confidence: {context.vic20_recommendation.get('confidence', 0):.2f}")
        
        return "\n".join(summary_parts)
