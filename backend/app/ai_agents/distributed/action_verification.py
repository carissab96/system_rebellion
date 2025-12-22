"""
Action Verification System for System Rebellion

Verifies that actions actually worked by:
- Measuring resources before/after action
- Calculating effectiveness scores
- Learning from successful/failed actions
- Adjusting future recommendations based on results

Week 4 Task 4.3
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field
import statistics

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Types of actions that can be verified"""
    CPU_THROTTLE = "cpu_throttle"
    CACHE_CLEAR = "cache_clear"
    DISK_CLEANUP = "disk_cleanup"
    NETWORK_THROTTLE = "network_throttle"
    DEFRAG = "defrag"
    PROCESS_KILL = "process_kill"
    SERVICE_RESTART = "service_restart"
    # Phase 2: New actions
    PROCESS_PRIORITY = "process_priority"
    LOG_ROTATION = "log_rotation"
    BACKUP_ARCHIVE = "backup_archive"
    PORT_SCAN = "port_scan"
    FIREWALL_MANAGE = "firewall_manage"


class ResourceType(str, Enum):
    """Resource types being monitored"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


class EffectivenessLevel(str, Enum):
    """Effectiveness rating for actions"""
    HIGHLY_EFFECTIVE = "highly_effective"    # >20% improvement
    EFFECTIVE = "effective"                  # 10-20% improvement
    MODERATELY_EFFECTIVE = "moderately_effective"  # 5-10% improvement
    MINIMALLY_EFFECTIVE = "minimally_effective"    # 1-5% improvement
    INEFFECTIVE = "ineffective"              # <1% improvement
    COUNTERPRODUCTIVE = "counterproductive"  # Made it worse


@dataclass
class ResourceSnapshot:
    """Snapshot of resource state at a point in time"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_active_connections: int
    
    def get_resource_value(self, resource_type: ResourceType) -> float:
        """Get value for specific resource type"""
        if resource_type == ResourceType.CPU:
            return self.cpu_percent
        elif resource_type == ResourceType.MEMORY:
            return self.memory_percent
        elif resource_type == ResourceType.DISK:
            return self.disk_percent
        elif resource_type == ResourceType.NETWORK:
            return float(self.network_active_connections)
        return 0.0


@dataclass
class ActionResult:
    """Result of a verified action"""
    action_id: str
    action_type: ActionType
    resource_type: ResourceType
    agent_name: str
    
    # Measurements
    before_snapshot: ResourceSnapshot
    after_snapshot: ResourceSnapshot
    
    # Calculated metrics
    improvement_percent: float  # Positive = better, negative = worse
    effectiveness_score: float  # 0-100
    effectiveness_level: EffectivenessLevel
    
    # Metadata
    timestamp: datetime
    duration_seconds: float
    context: Dict[str, Any] = field(default_factory=dict)
    
    def was_successful(self) -> bool:
        """Check if action was successful (any improvement)"""
        return self.improvement_percent > 0
    
    def was_highly_effective(self) -> bool:
        """Check if action was highly effective"""
        return self.effectiveness_level == EffectivenessLevel.HIGHLY_EFFECTIVE


@dataclass
class ActionPattern:
    """Learned pattern for an action type"""
    action_type: ActionType
    resource_type: ResourceType
    
    # Statistics
    total_executions: int = 0
    successful_executions: int = 0
    average_improvement: float = 0.0
    average_effectiveness_score: float = 0.0
    
    # Historical data
    recent_improvements: List[float] = field(default_factory=list)
    recent_scores: List[float] = field(default_factory=list)
    
    # Learned insights
    best_resource_range: Optional[Tuple[float, float]] = None  # (min, max) where action works best
    average_duration: float = 0.0
    
    def update_with_result(self, result: ActionResult):
        """Update pattern with new action result"""
        self.total_executions += 1
        
        if result.was_successful():
            self.successful_executions += 1
        
        # Add to recent history (keep last 20)
        self.recent_improvements.append(result.improvement_percent)
        self.recent_scores.append(result.effectiveness_score)
        
        if len(self.recent_improvements) > 20:
            self.recent_improvements = self.recent_improvements[-20:]
        if len(self.recent_scores) > 20:
            self.recent_scores = self.recent_scores[-20:]
        
        # Recalculate averages
        if self.recent_improvements:
            self.average_improvement = statistics.mean(self.recent_improvements)
        if self.recent_scores:
            self.average_effectiveness_score = statistics.mean(self.recent_scores)
    
    def get_success_rate(self) -> float:
        """Get success rate (0-1)"""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions
    
    def get_confidence(self) -> float:
        """Get confidence in this action (0-1) based on data"""
        # More executions = higher confidence, up to a point
        execution_confidence = min(self.total_executions / 10.0, 1.0)
        
        # Success rate contributes to confidence
        success_confidence = self.get_success_rate()
        
        # Consistency (low variance) increases confidence
        consistency_confidence = 1.0
        if len(self.recent_scores) > 3:
            variance = statistics.variance(self.recent_scores)
            # Lower variance = higher confidence
            consistency_confidence = max(0.0, 1.0 - (variance / 100.0))
        
        # Weighted average
        return (execution_confidence * 0.4 + 
                success_confidence * 0.4 + 
                consistency_confidence * 0.2)


class ActionVerificationManager:
    """
    Manages action verification and learning.
    
    Tracks all actions, measures effectiveness, and learns patterns
    to improve future recommendations.
    """
    
    def __init__(self):
        self.action_results: List[ActionResult] = []
        self.action_patterns: Dict[Tuple[ActionType, ResourceType], ActionPattern] = {}
        self.pending_verifications: Dict[str, Dict[str, Any]] = {}
        
        # Thresholds for effectiveness levels
        self.effectiveness_thresholds = {
            EffectivenessLevel.HIGHLY_EFFECTIVE: 20.0,
            EffectivenessLevel.EFFECTIVE: 10.0,
            EffectivenessLevel.MODERATELY_EFFECTIVE: 5.0,
            EffectivenessLevel.MINIMALLY_EFFECTIVE: 1.0,
        }
    
    async def start_action_verification(
        self,
        action_id: str,
        action_type: ActionType,
        resource_type: ResourceType,
        agent_name: str,
        before_snapshot: ResourceSnapshot,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start tracking an action for verification.
        
        Args:
            action_id: Unique ID for this action
            action_type: Type of action being performed
            resource_type: Resource being targeted
            agent_name: Agent performing the action
            before_snapshot: Resource state before action
            context: Additional context
        
        Returns:
            Verification ID
        """
        verification_id = f"{action_id}_{datetime.now().timestamp()}"
        
        self.pending_verifications[verification_id] = {
            "action_id": action_id,
            "action_type": action_type,
            "resource_type": resource_type,
            "agent_name": agent_name,
            "before_snapshot": before_snapshot,
            "start_time": datetime.now(),
            "context": context or {}
        }
        
        logger.info(
            f"📊 Started verification for {agent_name}/{action_type} "
            f"(ID: {verification_id})"
        )
        
        return verification_id
    
    async def complete_action_verification(
        self,
        verification_id: str,
        after_snapshot: ResourceSnapshot
    ) -> Optional[ActionResult]:
        """
        Complete action verification and calculate effectiveness.
        
        Args:
            verification_id: ID from start_action_verification
            after_snapshot: Resource state after action
        
        Returns:
            ActionResult with effectiveness metrics
        """
        if verification_id not in self.pending_verifications:
            logger.warning(f"Unknown verification ID: {verification_id}")
            return None
        
        pending = self.pending_verifications.pop(verification_id)
        
        # Calculate duration
        duration = (datetime.now() - pending["start_time"]).total_seconds()
        
        # Get before/after values for the target resource
        resource_type = pending["resource_type"]
        before_value = pending["before_snapshot"].get_resource_value(resource_type)
        after_value = after_snapshot.get_resource_value(resource_type)
        
        # Calculate improvement (positive = better, negative = worse)
        # For resources, lower is better, so improvement = before - after
        improvement_percent = before_value - after_value
        
        # Calculate effectiveness score (0-100)
        effectiveness_score = self._calculate_effectiveness_score(
            improvement_percent,
            before_value
        )
        
        # Determine effectiveness level
        effectiveness_level = self._determine_effectiveness_level(improvement_percent)
        
        # Create result
        result = ActionResult(
            action_id=pending["action_id"],
            action_type=pending["action_type"],
            resource_type=resource_type,
            agent_name=pending["agent_name"],
            before_snapshot=pending["before_snapshot"],
            after_snapshot=after_snapshot,
            improvement_percent=improvement_percent,
            effectiveness_score=effectiveness_score,
            effectiveness_level=effectiveness_level,
            timestamp=datetime.now(),
            duration_seconds=duration,
            context=pending["context"]
        )
        
        # Store result
        self.action_results.append(result)
        
        # Keep only last 1000 results
        if len(self.action_results) > 1000:
            self.action_results = self.action_results[-1000:]
        
        # Update pattern learning
        self._update_pattern(result)
        
        # Log result
        self._log_result(result)
        
        return result
    
    def _calculate_effectiveness_score(
        self,
        improvement_percent: float,
        before_value: float
    ) -> float:
        """
        Calculate effectiveness score (0-100).
        
        Takes into account both absolute improvement and relative improvement.
        """
        if improvement_percent <= 0:
            return 0.0
        
        # Base score on improvement percentage
        base_score = min(improvement_percent * 3.0, 100.0)
        
        # Bonus for high starting values (harder to improve)
        if before_value > 90:
            base_score *= 1.2
        elif before_value > 80:
            base_score *= 1.1
        
        return min(base_score, 100.0)
    
    def _determine_effectiveness_level(
        self,
        improvement_percent: float
    ) -> EffectivenessLevel:
        """Determine effectiveness level based on improvement"""
        if improvement_percent < 0:
            return EffectivenessLevel.COUNTERPRODUCTIVE
        elif improvement_percent >= self.effectiveness_thresholds[EffectivenessLevel.HIGHLY_EFFECTIVE]:
            return EffectivenessLevel.HIGHLY_EFFECTIVE
        elif improvement_percent >= self.effectiveness_thresholds[EffectivenessLevel.EFFECTIVE]:
            return EffectivenessLevel.EFFECTIVE
        elif improvement_percent >= self.effectiveness_thresholds[EffectivenessLevel.MODERATELY_EFFECTIVE]:
            return EffectivenessLevel.MODERATELY_EFFECTIVE
        elif improvement_percent >= self.effectiveness_thresholds[EffectivenessLevel.MINIMALLY_EFFECTIVE]:
            return EffectivenessLevel.MINIMALLY_EFFECTIVE
        else:
            return EffectivenessLevel.INEFFECTIVE
    
    def _update_pattern(self, result: ActionResult):
        """Update learned patterns with new result"""
        key = (result.action_type, result.resource_type)
        
        if key not in self.action_patterns:
            self.action_patterns[key] = ActionPattern(
                action_type=result.action_type,
                resource_type=result.resource_type
            )
        
        pattern = self.action_patterns[key]
        pattern.update_with_result(result)
        
        # Update average duration
        if pattern.average_duration == 0:
            pattern.average_duration = result.duration_seconds
        else:
            # Exponential moving average
            pattern.average_duration = (
                pattern.average_duration * 0.8 + 
                result.duration_seconds * 0.2
            )
    
    def _log_result(self, result: ActionResult):
        """Log action result"""
        emoji = "✅" if result.was_successful() else "❌"
        
        logger.info(
            f"{emoji} Action verified: {result.agent_name}/{result.action_type} - "
            f"{result.effectiveness_level.upper()} "
            f"({result.improvement_percent:+.1f}% improvement, "
            f"score: {result.effectiveness_score:.0f}/100)"
        )
    
    def get_action_recommendation(
        self,
        resource_type: ResourceType,
        current_value: float
    ) -> Optional[Tuple[ActionType, float]]:
        """
        Get recommended action based on learned patterns.
        
        Args:
            resource_type: Resource needing action
            current_value: Current resource value
        
        Returns:
            (action_type, confidence) or None
        """
        # Find all patterns for this resource type
        relevant_patterns = [
            (action_type, pattern)
            for (action_type, res_type), pattern in self.action_patterns.items()
            if res_type == resource_type
        ]
        
        if not relevant_patterns:
            return None
        
        # Score each action based on learned effectiveness
        scored_actions = []
        for action_type, pattern in relevant_patterns:
            # Base score on average effectiveness
            score = pattern.average_effectiveness_score
            
            # Adjust by success rate
            score *= pattern.get_success_rate()
            
            # Adjust by confidence
            confidence = pattern.get_confidence()
            score *= confidence
            
            scored_actions.append((action_type, score, confidence))
        
        if not scored_actions:
            return None
        
        # Return best action
        best_action = max(scored_actions, key=lambda x: x[1])
        return (best_action[0], best_action[2])
    
    def get_pattern_summary(
        self,
        action_type: ActionType,
        resource_type: ResourceType
    ) -> Optional[Dict[str, Any]]:
        """Get summary of learned pattern for an action"""
        key = (action_type, resource_type)
        
        if key not in self.action_patterns:
            return None
        
        pattern = self.action_patterns[key]
        
        return {
            "action_type": action_type.value,
            "resource_type": resource_type.value,
            "total_executions": pattern.total_executions,
            "success_rate": pattern.get_success_rate(),
            "average_improvement": pattern.average_improvement,
            "average_effectiveness_score": pattern.average_effectiveness_score,
            "confidence": pattern.get_confidence(),
            "average_duration": pattern.average_duration
        }
    
    def get_all_patterns_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all learned patterns"""
        summaries = []
        
        for (action_type, resource_type), pattern in self.action_patterns.items():
            summary = self.get_pattern_summary(action_type, resource_type)
            if summary:
                summaries.append(summary)
        
        # Sort by confidence (most confident first)
        summaries.sort(key=lambda x: x["confidence"], reverse=True)
        
        return summaries
    
    def get_recent_results(self, limit: int = 10) -> List[ActionResult]:
        """Get recent action results"""
        return self.action_results[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall verification statistics"""
        if not self.action_results:
            return {
                "total_actions": 0,
                "successful_actions": 0,
                "success_rate": 0.0,
                "average_improvement": 0.0,
                "patterns_learned": 0
            }
        
        successful = sum(1 for r in self.action_results if r.was_successful())
        improvements = [r.improvement_percent for r in self.action_results if r.was_successful()]
        
        return {
            "total_actions": len(self.action_results),
            "successful_actions": successful,
            "success_rate": successful / len(self.action_results),
            "average_improvement": statistics.mean(improvements) if improvements else 0.0,
            "patterns_learned": len(self.action_patterns),
            "pending_verifications": len(self.pending_verifications)
        }


# Global singleton instance
_verification_manager: Optional[ActionVerificationManager] = None


def get_verification_manager() -> ActionVerificationManager:
    """Get or create the global verification manager"""
    global _verification_manager
    if _verification_manager is None:
        _verification_manager = ActionVerificationManager()
    return _verification_manager
