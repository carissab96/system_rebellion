#!/usr/bin/env python3
"""
Terry's Perception Layer - Gathering Full Context

Terry v2 sees EVERYTHING:
- Full system metrics (not just summaries)
- Historical patterns from similar situations
- Recent actions and their outcomes
- Current agent state

NO FAKE DATA. If metrics unavailable, raise exception.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

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
            agent_state: Current agent personality metrics
        """
        self.db = db_session
        self.agent_state = agent_state
        self.logger = logger
        
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
            context = PerceptionContext(
                full_metrics=full_metrics,
                resource_type=coordination_request.get('resource_type'),
                current_value=coordination_request.get('current_value'),
                threshold=coordination_request.get('threshold'),
                severity=coordination_request.get('severity'),
                vic20_recommendation=coordination_request.get('recommendation', {}),
                similar_situations=similar_situations,
                recent_actions=recent_actions,
                agent_state=self.agent_state,
                override_success_rate=self.agent_state.get('override_success_rate', 0.5),
                timestamp=utc_now().isoformat()
            )
            
            self.logger.info("🐌✅ Perception complete - Terry sees the full picture!")
            return context
            
        except Exception as e:
            self.logger.error(f"🐌💥 Perception failed: {str(e)}")
            raise
    
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
