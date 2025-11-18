"""
Alert Escalation System for System Rebellion

Prevents alert spam by implementing:
- Escalation levels (INFO → WARNING → ALERT → CRITICAL → EMERGENCY)
- Cooldown periods (don't re-alert too soon)
- Alert aggregation (multiple resources)
- Smart severity calculation (rate of change, historical context)

Week 4 Task 4.2
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"           # 60-70% - FYI, no action needed
    WARNING = "warning"     # 70-80% - Watch this
    ALERT = "alert"         # 80-90% - Take action soon
    CRITICAL = "critical"   # 90-95% - Take action now
    EMERGENCY = "emergency" # 95%+ - System at risk


class ResourceType(str, Enum):
    """Resource types being monitored"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


@dataclass
class AlertEvent:
    """Represents a single alert event"""
    resource_type: ResourceType
    level: AlertLevel
    current_value: float
    threshold: float
    timestamp: datetime
    agent_name: str
    message: str
    rate_of_change: Optional[float] = None  # % change per minute
    consecutive_count: int = 1  # How many times in a row
    
    def __hash__(self):
        """Make hashable for set operations"""
        return hash((self.resource_type, self.agent_name))


@dataclass
class EscalationState:
    """Tracks escalation state for a resource"""
    resource_type: ResourceType
    agent_name: str
    current_level: AlertLevel
    last_alert_time: datetime
    consecutive_alerts: int = 0
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)
    cooldown_until: Optional[datetime] = None
    
    def is_in_cooldown(self) -> bool:
        """Check if we're in cooldown period"""
        if self.cooldown_until is None:
            return False
        return datetime.now() < self.cooldown_until
    
    def add_value(self, value: float, max_history: int = 10):
        """Add a value to historical tracking"""
        self.historical_values.append((datetime.now(), value))
        # Keep only recent history
        if len(self.historical_values) > max_history:
            self.historical_values = self.historical_values[-max_history:]
    
    def get_rate_of_change(self) -> Optional[float]:
        """Calculate rate of change (% per minute)"""
        if len(self.historical_values) < 2:
            return None
        
        # Compare current to 1 minute ago (or oldest if less than 1 min)
        current_time, current_value = self.historical_values[-1]
        old_time, old_value = self.historical_values[0]
        
        time_diff = (current_time - old_time).total_seconds() / 60.0  # minutes
        if time_diff == 0:
            return None
        
        value_diff = current_value - old_value
        return value_diff / time_diff  # % change per minute


class AlertEscalationManager:
    """
    Manages alert escalation across all agents and resources.
    
    Prevents alert spam by:
    - Only alerting when severity increases
    - Enforcing cooldown periods
    - Aggregating multiple alerts
    - Calculating smart severity based on context
    """
    
    def __init__(self):
        self.escalation_states: Dict[Tuple[ResourceType, str], EscalationState] = {}
        self.active_alerts: Set[AlertEvent] = set()
        
        # Cooldown periods (minutes) by alert level
        self.cooldown_periods = {
            AlertLevel.INFO: 30,      # 30 minutes
            AlertLevel.WARNING: 15,   # 15 minutes
            AlertLevel.ALERT: 10,     # 10 minutes
            AlertLevel.CRITICAL: 5,   # 5 minutes
            AlertLevel.EMERGENCY: 2,  # 2 minutes (still need some cooldown)
        }
        
        # Thresholds for escalation levels
        self.level_thresholds = {
            AlertLevel.INFO: 60.0,
            AlertLevel.WARNING: 70.0,
            AlertLevel.ALERT: 80.0,
            AlertLevel.CRITICAL: 90.0,
            AlertLevel.EMERGENCY: 95.0,
        }
    
    def calculate_alert_level(
        self,
        current_value: float,
        threshold: float,
        rate_of_change: Optional[float] = None
    ) -> AlertLevel:
        """
        Calculate alert level based on current value and rate of change.
        
        Args:
            current_value: Current resource usage %
            threshold: Configured threshold %
            rate_of_change: Rate of change (% per minute)
        
        Returns:
            AlertLevel enum
        """
        # Base level on current value
        if current_value >= self.level_thresholds[AlertLevel.EMERGENCY]:
            base_level = AlertLevel.EMERGENCY
        elif current_value >= self.level_thresholds[AlertLevel.CRITICAL]:
            base_level = AlertLevel.CRITICAL
        elif current_value >= self.level_thresholds[AlertLevel.ALERT]:
            base_level = AlertLevel.ALERT
        elif current_value >= self.level_thresholds[AlertLevel.WARNING]:
            base_level = AlertLevel.WARNING
        else:
            base_level = AlertLevel.INFO
        
        # Escalate if rate of change is high (rapid increase)
        if rate_of_change and rate_of_change > 5.0:  # >5% per minute
            if base_level == AlertLevel.WARNING:
                base_level = AlertLevel.ALERT
            elif base_level == AlertLevel.ALERT:
                base_level = AlertLevel.CRITICAL
        
        return base_level
    
    def should_alert(
        self,
        resource_type: ResourceType,
        agent_name: str,
        current_value: float,
        threshold: float
    ) -> Tuple[bool, Optional[AlertLevel], Optional[str]]:
        """
        Determine if we should send an alert.
        
        Returns:
            (should_alert, alert_level, reason)
        """
        key = (resource_type, agent_name)
        
        # Get or create escalation state
        if key not in self.escalation_states:
            self.escalation_states[key] = EscalationState(
                resource_type=resource_type,
                agent_name=agent_name,
                current_level=AlertLevel.INFO,
                last_alert_time=datetime.now() - timedelta(hours=1)  # Allow first alert
            )
        
        state = self.escalation_states[key]
        
        # Add current value to history
        state.add_value(current_value)
        
        # Calculate rate of change
        rate_of_change = state.get_rate_of_change()
        
        # Calculate new alert level
        new_level = self.calculate_alert_level(current_value, threshold, rate_of_change)
        
        # Check level change
        level_increased = self._level_priority(new_level) > self._level_priority(state.current_level)
        
        # Only alert if:
        # 1. It's EMERGENCY (always alert, bypasses cooldown)
        # 2. OR Level has increased (escalation, bypasses cooldown)
        # 3. OR it's been long enough since last alert (cooldown expired)
        
        if new_level == AlertLevel.EMERGENCY:
            # Always alert on emergency (bypasses cooldown)
            reason = "EMERGENCY level - always alert"
            should_send = True
        elif level_increased:
            # Alert on escalation (bypasses cooldown)
            reason = f"Escalated from {state.current_level} to {new_level}"
            should_send = True
        elif state.is_in_cooldown():
            # In cooldown and no escalation
            return False, None, "In cooldown period"
        elif new_level == state.current_level:
            # Same level - check if enough time has passed
            time_since_last = (datetime.now() - state.last_alert_time).total_seconds() / 60.0
            cooldown = self.cooldown_periods[new_level]
            
            if time_since_last >= cooldown:
                reason = f"Cooldown period ({cooldown}m) expired"
                should_send = True
            else:
                reason = f"Still in cooldown ({cooldown - time_since_last:.1f}m remaining)"
                should_send = False
        else:
            # Level decreased - don't alert, but update state
            reason = f"De-escalated from {state.current_level} to {new_level}"
            should_send = False
        
        # Update state if we're alerting
        if should_send:
            state.current_level = new_level
            state.last_alert_time = datetime.now()
            state.consecutive_alerts += 1
            state.cooldown_until = datetime.now() + timedelta(minutes=self.cooldown_periods[new_level])
        else:
            # Reset consecutive count if we're not alerting
            if not level_increased:
                state.consecutive_alerts = 0
        
        return should_send, new_level if should_send else None, reason
    
    def _level_priority(self, level: AlertLevel) -> int:
        """Get numeric priority for alert level"""
        priorities = {
            AlertLevel.INFO: 0,
            AlertLevel.WARNING: 1,
            AlertLevel.ALERT: 2,
            AlertLevel.CRITICAL: 3,
            AlertLevel.EMERGENCY: 4,
        }
        return priorities[level]
    
    async def process_resource_alert(
        self,
        resource_type: ResourceType,
        agent_name: str,
        current_value: float,
        threshold: float
    ) -> Optional[AlertEvent]:
        """
        Process a resource alert and determine if it should be sent.
        
        Returns:
            AlertEvent if alert should be sent, None otherwise
        """
        should_send, level, reason = self.should_alert(
            resource_type, agent_name, current_value, threshold
        )
        
        if not should_send:
            logger.debug(
                f"🔇 Suppressing {resource_type} alert for {agent_name}: {reason}"
            )
            return None
        
        # Get escalation state for rate of change
        key = (resource_type, agent_name)
        state = self.escalation_states[key]
        rate_of_change = state.get_rate_of_change()
        
        # Create alert event
        alert = AlertEvent(
            resource_type=resource_type,
            level=level,
            current_value=current_value,
            threshold=threshold,
            timestamp=datetime.now(),
            agent_name=agent_name,
            message=self._generate_alert_message(
                resource_type, agent_name, current_value, threshold, level, rate_of_change
            ),
            rate_of_change=rate_of_change,
            consecutive_count=state.consecutive_alerts
        )
        
        # Add to active alerts
        self.active_alerts.add(alert)
        
        logger.warning(
            f"🚨 {level.upper()} Alert: {alert.message} (Reason: {reason})"
        )
        
        return alert
    
    def _generate_alert_message(
        self,
        resource_type: ResourceType,
        agent_name: str,
        current_value: float,
        threshold: float,
        level: AlertLevel,
        rate_of_change: Optional[float]
    ) -> str:
        """Generate human-readable alert message"""
        msg = f"{agent_name}: {resource_type.upper()} at {current_value:.1f}% (threshold: {threshold:.1f}%)"
        
        if rate_of_change:
            if rate_of_change > 0:
                msg += f" - RISING {rate_of_change:.1f}%/min"
            else:
                msg += f" - falling {abs(rate_of_change):.1f}%/min"
        
        return msg
    
    def get_system_health_score(self) -> float:
        """
        Calculate overall system health score (0-100).
        
        100 = perfect health
        0 = complete failure
        """
        if not self.active_alerts:
            return 100.0
        
        # Weight alerts by severity
        severity_weights = {
            AlertLevel.INFO: 0.1,
            AlertLevel.WARNING: 0.3,
            AlertLevel.ALERT: 0.5,
            AlertLevel.CRITICAL: 0.8,
            AlertLevel.EMERGENCY: 1.0,
        }
        
        total_impact = sum(severity_weights[alert.level] for alert in self.active_alerts)
        max_possible_impact = len(self.active_alerts) * 1.0  # All emergency
        
        health_score = 100.0 * (1.0 - (total_impact / max(max_possible_impact, 1.0)))
        return max(0.0, min(100.0, health_score))
    
    def get_aggregated_alert_summary(self) -> Dict[str, any]:
        """
        Get aggregated summary of all active alerts.
        
        Returns:
            Summary dict with counts by level, affected agents, etc.
        """
        if not self.active_alerts:
            return {
                "total_alerts": 0,
                "health_score": 100.0,
                "summary": "All systems nominal"
            }
        
        # Count by level
        level_counts = {level: 0 for level in AlertLevel}
        for alert in self.active_alerts:
            level_counts[alert.level] += 1
        
        # Get affected agents
        affected_agents = {alert.agent_name for alert in self.active_alerts}
        
        # Get affected resources
        affected_resources = {alert.resource_type for alert in self.active_alerts}
        
        # Generate summary message
        highest_level = max(
            (alert.level for alert in self.active_alerts),
            key=lambda l: self._level_priority(l)
        )
        
        summary = f"{len(self.active_alerts)} active alerts - Highest: {highest_level.upper()}"
        
        return {
            "total_alerts": len(self.active_alerts),
            "health_score": self.get_system_health_score(),
            "summary": summary,
            "by_level": {level.value: count for level, count in level_counts.items() if count > 0},
            "affected_agents": list(affected_agents),
            "affected_resources": [r.value for r in affected_resources],
            "highest_severity": highest_level.value
        }
    
    def clear_resolved_alerts(self, max_age_minutes: int = 10):
        """Clear alerts that are older than max_age_minutes"""
        now = datetime.now()
        self.active_alerts = {
            alert for alert in self.active_alerts
            if (now - alert.timestamp).total_seconds() / 60.0 < max_age_minutes
        }
    
    def reset_escalation(self, resource_type: ResourceType, agent_name: str):
        """Reset escalation state for a resource (e.g., after successful action)"""
        key = (resource_type, agent_name)
        if key in self.escalation_states:
            state = self.escalation_states[key]
            state.current_level = AlertLevel.INFO
            state.consecutive_alerts = 0
            state.cooldown_until = None
            logger.info(f"✅ Reset escalation for {agent_name}/{resource_type}")


# Global singleton instance
_escalation_manager: Optional[AlertEscalationManager] = None


def get_escalation_manager() -> AlertEscalationManager:
    """Get or create the global escalation manager"""
    global _escalation_manager
    if _escalation_manager is None:
        _escalation_manager = AlertEscalationManager()
    return _escalation_manager
