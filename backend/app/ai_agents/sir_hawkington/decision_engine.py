"""
Sir Hawkington's Decision Engine - Version 1: The Basics

This is Sir Hawkington's brain. He looks at system metrics and decides:
1. Is everything normal? (Say nothing)
2. Is something concerning? (Gentle notification)  
3. Is something broken? (Alert the human!)

We start simple and make him smarter over time.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HawkingtonDecision:
    """
    A decision that Sir Hawkington makes about the system.
    Like a note he writes to himself (and the human).
    """
    decision_type: str  # "normal", "concern", "alert"
    message: str        # What he wants to tell the human
    confidence: float   # How sure he is (0.0 to 1.0)
    timestamp: datetime
    metrics_snapshot: Dict[str, Any]  # The data he looked at
    reasoning: str      # Why he made this decision

class SirHawkingtonDecisionEngine:
    """
    Sir Hawkington's brain for making decisions about system health.
    
    Version 1: Simple rule-based decisions
    Version 2: We'll add machine learning later
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SirHawkington")
        
        # Sir Hawkington's personality settings
        self.concern_threshold = 0.65    # When he starts to worry
        self.alert_threshold = 0.85      # When he sounds the alarm
        self.monocle_adjustment_frequency = 0.05  # How often his monocle needs adjusting
        
        # Keep track of recent decisions (his memory)
        self.recent_decisions: List[HawkingtonDecision] = []
        self.max_memory_size = 100
        
        self.logger.info("🧐 Sir Hawkington's Decision Engine initialized. Monocle polished and ready.")
    
    def analyze_system_health(self, metrics: Dict[str, Any]) -> HawkingtonDecision:
        """
        Sir Hawkington's main analysis function.
        He looks at the metrics and makes a decision.
        
        Args:
            metrics: The system metrics from your WebSocket
            
        Returns:
            HawkingtonDecision: His thoughtful conclusion
        """
        self.logger.debug("🧐 Sir Hawkington adjusts his monocle and begins analysis...")
        
        # Extract the key metrics (with safe defaults)
        cpu_usage = metrics.get('cpu_usage', 0)
        memory_usage = metrics.get('memory_usage', 0) 
        disk_usage = metrics.get('disk_usage', 0)
        
        # Sir Hawkington's simple but effective analysis
        decision = self._make_decision(cpu_usage, memory_usage, disk_usage, metrics)
        
        # Remember this decision
        self._store_decision(decision)
        
        self.logger.info(f"🧐 Sir Hawkington's decision: {decision.decision_type} - {decision.message}")
        
        return decision
    
    def _make_decision(self, cpu: float, memory: float, disk: float, full_metrics: Dict[str, Any]) -> HawkingtonDecision:
        """
        Sir Hawkington's decision-making logic.
        Start simple, make it smarter later.
        """
        
        # Calculate overall system stress (Sir Hawkington's secret formula)
        stress_score = self._calculate_stress_score(cpu, memory, disk)
        
        # Sir Hawkington's decision logic
        if stress_score >= self.alert_threshold:
            return self._create_alert_decision(stress_score, cpu, memory, disk, full_metrics)
        elif stress_score >= self.concern_threshold:
            return self._create_concern_decision(stress_score, cpu, memory, disk, full_metrics)
        else:
            return self._create_normal_decision(stress_score, cpu, memory, disk, full_metrics)
    
    def _calculate_stress_score(self, cpu: float, memory: float, disk: float) -> float:
        """
        Sir Hawkington's stress calculation formula.
        He's particularly concerned about memory (from experience).
        """
        # Weighted average - Sir Hawkington thinks memory is most important
        weights = {
            'cpu': 0.3,
            'memory': 0.4,  # Memory problems are the worst
            'disk': 0.3
        }
        
        # Convert percentages to 0-1 scale
        cpu_score = cpu / 100.0
        memory_score = memory / 100.0  
        disk_score = disk / 100.0
        
        # Sir Hawkington's weighted formula
        stress_score = (
            cpu_score * weights['cpu'] +
            memory_score * weights['memory'] +
            disk_score * weights['disk']
        )
        
        return min(stress_score, 1.0)  # Cap at 1.0
    
    def _create_alert_decision(self, stress: float, cpu: float, memory: float, disk: float, metrics: Dict[str, Any]) -> HawkingtonDecision:
        """Sir Hawkington creates an ALERT decision"""
        
        # Find the biggest problem
        problems = []
        if cpu > 90: problems.append(f"CPU at {cpu:.1f}%")
        if memory > 90: problems.append(f"Memory at {memory:.1f}%") 
        if disk > 90: problems.append(f"Disk at {disk:.1f}%")
        
        message = f"🚨 Sir Hawkington's monocle has POPPED OUT! Critical system stress detected: {', '.join(problems)}. Immediate attention required!"
        
        return HawkingtonDecision(
            decision_type="alert",
            message=message,
            confidence=0.95,  # Sir Hawkington is very sure about alerts
            timestamp=datetime.now(),
            metrics_snapshot=metrics,
            reasoning=f"System stress score {stress:.2f} exceeds alert threshold {self.alert_threshold}"
        )
    
    def _create_concern_decision(self, stress: float, cpu: float, memory: float, disk: float, metrics: Dict[str, Any]) -> HawkingtonDecision:
        """Sir Hawkington creates a CONCERN decision"""
        
        message = f"🧐 Sir Hawkington adjusts his monocle with concern. System stress elevated (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%). Monitoring closely."
        
        return HawkingtonDecision(
            decision_type="concern", 
            message=message,
            confidence=0.8,
            timestamp=datetime.now(),
            metrics_snapshot=metrics,
            reasoning=f"System stress score {stress:.2f} exceeds concern threshold {self.concern_threshold}"
        )
    
    def _create_normal_decision(self, stress: float, cpu: float, memory: float, disk: float, metrics: Dict[str, Any]) -> HawkingtonDecision:
        """Sir Hawkington creates a NORMAL decision"""
        
        # Sir Hawkington only occasionally mentions when things are normal
        import random
        if random.random() < 0.1:  # 10% chance of a normal comment
            message = "🧐 Sir Hawkington's monocle gleams with satisfaction. All systems operating within acceptable parameters."
        else:
            message = None  # Usually he says nothing when things are fine
        
        return HawkingtonDecision(
            decision_type="normal",
            message=message,
            confidence=0.9,
            timestamp=datetime.now(), 
            metrics_snapshot=metrics,
            reasoning=f"System stress score {stress:.2f} is within normal operating parameters"
        )
    
    def _store_decision(self, decision: HawkingtonDecision):
        """Store Sir Hawkington's decision in his memory"""
        self.recent_decisions.append(decision)
        
        # Keep memory size manageable
        if len(self.recent_decisions) > self.max_memory_size:
            self.recent_decisions = self.recent_decisions[-self.max_memory_size:]
    
    def get_recent_decisions(self, limit: int = 10) -> List[HawkingtonDecision]:
        """Get Sir Hawkington's recent decisions"""
        return self.recent_decisions[-limit:]