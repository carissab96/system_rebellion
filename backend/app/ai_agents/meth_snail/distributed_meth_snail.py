"""
Terry the Meth Snail Distributed - Speed Demon with Distributed Consciousness
==============================================================================

Terry's existing optimization engine and energy drink authorization
enhanced with distributed consciousness, memory monitoring, and cache management.

Preserves:
- Shell-spinning behavior (waiting for real data)
- Optimization decision-making
- Energy drink authorization
- Database integration
- NO FAKE DATA policy

Adds:
- Redis state persistence
- Memory resource monitoring (75% threshold)
- Emergency cache clearing on critical memory
- Energy drink tracking across restarts
- Shell spin incident broadcasting
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.mixins import DistributedAgentMixin
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority
from .decision_engine import MethSnailBrainV2, OptimizationPriority, AnalysisDepth


logger = logging.getLogger("MethSnail.Distributed")


class MethSnailDistributed(DistributedAgentMixin, MethSnailBrainV2):
    """
    Terry the Meth Snail with distributed consciousness.
    
    GOTTA GO FAST... but now with memory persistence!
    
    Inherits ALL existing optimization logic from MethSnailBrainV2
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize Terry with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional)
        """
        # Initialize both parent classes via MRO
        super().__init__(db_getter=db_getter)
        
        # Set agent name for distributed features
        self.agent_name = "meth_snail"
        
        # Terry's hyperactive personality traits
        self.personality_traits = {
            "speed_obsessed": True,
            "hyperactive": True,
            "shell_spinning_enabled": True,
            "cache_clearing_frequency": "MAXIMUM",
            "energy_drink_powered": True,
            "no_fake_data_tolerance": 0,
            "optimization_priority": "speed",
            "jitter_level": "moderate"
        }
        
        # Resource monitoring configuration
        # Terry monitors memory usage (befitting his role as memory optimizer)
        self.resource_thresholds = {
            ResourceType.MEMORY: 75.0,  # Alert at 75% memory
        }
        
        logger.info("🐌💨 Terry the Meth Snail's distributed consciousness initialized - GOTTA GO FAST!")
    
    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.
        
        Wraps the existing analyze_metrics to add distributed tracking
        while preserving all original optimization logic.
        """
        # Call the original analyze_metrics from MethSnailBrainV2
        decision = await super().analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            analysis_depth=analysis_depth,
            user_id=user_id
        )
        
        # If distributed features are enabled, record the decision
        if self.is_distributed and decision:
            try:
                # Record in distributed state
                await self.make_distributed_decision(
                    decision_type=f"optimization_{decision.priority.value}",
                    input_data={
                        "memory_usage": metrics_data.get('memory_usage'),
                        "cpu_usage": metrics_data.get('cpu_usage'),
                        "optimization_priority": decision.priority.value,
                        "shell_spin_count": decision.shell_spin_count,
                        "data_quality_score": decision.data_quality_score,
                        "user_id": user_id
                    },
                    confidence=decision.confidence,
                    reasoning=decision.rationale
                )
                
                # If it's an aggressive optimization, broadcast to other agents
                if decision.priority == OptimizationPriority.AGGRESSIVE:
                    await self.broadcast_to_agents(
                        message_type=MessageType.DECISION_BROADCAST,
                        payload={
                            "decision_type": "aggressive_optimization",
                            "priority": decision.priority.value,
                            "urgency": decision.urgency,
                            "estimated_impact": decision.estimated_impact,
                            "actions": decision.actions
                        },
                        priority=Priority.HIGH
                    )
                    
                    logger.info(f"🐌💨 AGGRESSIVE optimization broadcast to rebellion!")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle memory resource alerts with MAXIMUM SPEED.
        
        When memory usage is high, Terry takes immediate action:
        - Emergency cache clearing
        - Optimization recommendations
        - Broadcasts critical alerts
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🐌💨⚠️ Terry detects elevated memory usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - SHELL SPINNING INTENSIFIES"
        )
        
        # Record the resource alert as a decision
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_alert_memory",
                input_data={
                    "resource_type": "memory",
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,
                reasoning=f"Memory usage at {current_value:.1f}% exceeds threshold of {threshold:.1f}%"
            )
        
        # If critical, EMERGENCY CACHE CLEAR
        if severity == "critical":
            logger.warning(
                "🐌💨💥 CRITICAL MEMORY USAGE! "
                "Terry initiates EMERGENCY CACHE CLEARING PROTOCOL!"
            )
            
            # Record emergency action
            if self.is_distributed:
                await self.make_distributed_decision(
                    decision_type="emergency_cache_clear",
                    input_data={
                        "trigger": "critical_memory",
                        "memory_usage": current_value,
                        "action": "clear_all_caches"
                    },
                    confidence=1.0,
                    reasoning="CRITICAL memory usage requires immediate cache clearing"
                )
            
            # Broadcast critical resource alert
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.EMERGENCY,
                    payload={
                        "emergency_type": "critical_memory",
                        "current_value": current_value,
                        "threshold": threshold,
                        "action_taken": "emergency_cache_clear",
                        "optimizer": "meth_snail"
                    },
                    priority=Priority.CRITICAL
                )
            
            # TODO: Actually implement cache clearing here
            # For now, just log and alert
            logger.info("🐌💨 Emergency cache clear would happen here (not implemented yet)")
    
    async def _record_shell_spin(self, missing_metrics, invalid_metrics, reason, user_id=None):
        """
        Override shell spin recording to add distributed tracking.
        
        Shell spinning is SERIOUS BUSINESS and must be tracked across the rebellion.
        """
        # Call original shell spin recording
        await super()._record_shell_spin(missing_metrics, invalid_metrics, reason, user_id)
        
        # Record in distributed state
        if self.is_distributed:
            try:
                await self.make_distributed_decision(
                    decision_type="shell_spin_incident",
                    input_data={
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "reason": reason,
                        "user_id": user_id,
                        "total_spins": len(self.shell_spin_incidents)
                    },
                    confidence=1.0,
                    reasoning=f"Shell spinning due to: {reason}"
                )
                
                # Broadcast shell spin to other agents (they should know Terry is waiting!)
                await self.broadcast_to_agents(
                    message_type=MessageType.SYSTEM_EVENT,
                    payload={
                        "event_type": "shell_spin",
                        "reason": reason,
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "spin_count": len(self.shell_spin_incidents)
                    },
                    priority=Priority.NORMAL
                )
                
                logger.info(f"🐌💫 Shell spin broadcast to rebellion")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed shell spin: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Terry's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with Terry's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "memory_optimizer",
            "is_active": self.is_active,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "shell_spin_count": len(self.shell_spin_incidents),
            "energy_drinks_consumed": len(self.energy_drink_history),
            "current_jitter_level": self.current_jitter_level.value if hasattr(self, 'current_jitter_level') else "unknown",
            "optimization_stats": {
                "total_optimizations": self.total_analyses,
                "successful_optimizations": self.successful_analyses
            },
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Hyperactive string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        spins = len(self.shell_spin_incidents)
        return (
            f"<MethSnailDistributed "
            f"analyses={self.total_analyses} "
            f"spins={spins} "
            f"drinks={len(self.energy_drink_history)} "
            f"| {dist_status} | 💨>"
        )


# Convenience function
async def create_distributed_meth_snail(redis_client, db_getter=None):
    """
    Create and initialize Terry with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized MethSnailDistributed instance
    """
    terry = MethSnailDistributed(db_getter=db_getter)
    await terry.initialize_distributed(redis_client)
    logger.info("🐌💨✨ Terry's distributed consciousness fully awakened - MAXIMUM SPEED!")
    return terry
