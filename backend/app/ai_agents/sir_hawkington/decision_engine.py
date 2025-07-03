"""
Sir Hawkington's Decision Engine - NO FAKE DATA EDITION

A gentleman's approach to system monitoring:
1. Real data only - a gentleman never works with fabricated information
2. Proper validation - standards must be maintained
3. Monocle yeeting when data quality is insufficient
4. Dignified error handling with aristocratic flair

Sir Hawkington maintains the highest standards of data integrity.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """Sir Hawkington's decision classifications"""
    NORMAL = "normal"
    CONCERN = "concern" 
    ALERT = "alert"
    CRITICAL = "critical"

class MonocleState(Enum):
    """The state of Sir Hawkington's monocle"""
    POLISHED = "polished"
    ADJUSTED = "adjusted"
    FOGGED = "fogged"
    YEETED = "yeeted"

@dataclass
class HawkingtonDecision:
    """
    A decision that Sir Hawkington makes about the system.
    Only created when he has sufficient real data to make a proper assessment.
    """
    decision_type: DecisionType
    message: str
    confidence: float       # How sure he is (0.0 to 1.0)
    timestamp: datetime
    metrics_snapshot: Dict[str, Any]  # The REAL data he analyzed
    reasoning: str         # Why he made this decision
    stress_score: float    # His calculated system stress
    monocle_state: MonocleState
    data_quality: str = "VALIDATED_REAL_DATA"

class SirHawkingtonDecisionEngine:
    """
    Sir Hawkington's brain for making decisions about system health.
    
    ZERO TOLERANCE FOR FAKE DATA POLICY:
    - Real metrics only
    - Proper validation required
    - Monocle yeeting when data is insufficient
    - Aristocratic standards maintained at all times
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SirHawkington")
        
        # Sir Hawkington's personality settings (based on real thresholds)
        self.concern_threshold = 0.65      # When he starts to worry
        self.alert_threshold = 0.85        # When he sounds the alarm
        self.critical_threshold = 0.95     # When he demands immediate action
        
        # Memory and statistics
        self.recent_decisions: List[HawkingtonDecision] = []
        self.max_memory_size = 100
        self.monocle_yeet_count = 0        # Track data quality failures
        self.total_analyses_attempted = 0
        self.successful_analyses = 0
        
        # Monocle state tracking
        self.current_monocle_state = MonocleState.POLISHED
        self.last_monocle_yeet_time: Optional[datetime] = None
        
        self.logger.info("🧐 Sir Hawkington's Decision Engine initialized. Monocle polished and ready for REAL DATA ONLY.")
    
    def analyze_system_health(self, metrics: Dict[str, Any]) -> Optional[HawkingtonDecision]:
        """
        Sir Hawkington's main analysis function.
        A gentleman only makes decisions with proper, validated data.
        
        Args:
            metrics: The system metrics from your WebSocket
            
        Returns:
            HawkingtonDecision: His thoughtful conclusion, or None if data is insufficient
        """
        self.total_analyses_attempted += 1
        self.logger.debug("🧐 Sir Hawkington adjusts his monocle and begins analysis...")
        
        try:
            # Extract the key metrics - NO DEFAULTS! A gentleman demands authenticity.
            cpu_usage = metrics.get('cpu_usage')
            memory_usage = metrics.get('memory_usage') 
            disk_usage = metrics.get('disk_usage')
            
            # VALIDATE CRITICAL METRICS EXIST
            missing_metrics = []
            if cpu_usage is None:
                missing_metrics.append('cpu_usage')
            if memory_usage is None:
                missing_metrics.append('memory_usage')
            if disk_usage is None:
                missing_metrics.append('disk_usage')
                
            if missing_metrics:
                self._yeet_monocle("MISSING_DATA")
                self.logger.warning(f"🧐💥 Sir Hawkington yeeted his monocle #{self.monocle_yeet_count}! Missing critical metrics: {missing_metrics}. A gentleman cannot make decisions without proper data.")
                return None
                
            # VALIDATE DATA RANGES - A gentleman expects accurate information
            if not self._validate_metric_range(cpu_usage, "CPU"):
                return None
            if not self._validate_metric_range(memory_usage, "Memory"):
                return None  
            if not self._validate_metric_range(disk_usage, "Disk"):
                return None
            
            # VALIDATE OPTIONAL METRICS
            validated_metrics = self._validate_optional_metrics(metrics)
            
            # Data is valid - proceed with analysis
            self.successful_analyses += 1
            self._polish_monocle()
            
            # Sir Hawkington's sophisticated analysis
            decision = self._make_decision(cpu_usage, memory_usage, disk_usage, validated_metrics)
            
            # Remember this decision
            self._store_decision(decision)
            
            self.logger.info(f"🧐 Sir Hawkington's decision: {str(decision.decision_type)} - {decision.message}")
            
            return decision
            
        except Exception as e:
            self._yeet_monocle("ANALYSIS_ERROR")
            self.logger.error(f"🧐💥 Sir Hawkington's analysis failed with aristocratic indignation: {e}")
            return None
    
    def _validate_metric_range(self, value: float, metric_name: str) -> bool:
        """Validate that a metric is within acceptable ranges"""
        if not isinstance(value, (int, float)):
            self._yeet_monocle("INVALID_TYPE")
            self.logger.error(f"🧐💥 Sir Hawkington yeeted his monocle #{self.monocle_yeet_count}! {metric_name} is not a number: {value}. A gentleman expects numerical data!")
            return False
            
        if not (0 <= value <= 100):
            self._yeet_monocle("INVALID_RANGE")
            self.logger.error(f"🧐💥 Sir Hawkington yeeted his monocle #{self.monocle_yeet_count}! Invalid {metric_name} usage: {value}%. A gentleman refuses fabricated data!")
            return False
            
        return True
    
    def _validate_optional_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and extract optional metrics"""
        validated = {
            'cpu_usage': metrics['cpu_usage'],
            'memory_usage': metrics['memory_usage'],
            'disk_usage': metrics['disk_usage']
        }
        
        # Network data validation
        network_data = metrics.get('network')
        if network_data and isinstance(network_data, dict):
            validated['network'] = network_data
        
        # Process count validation
        process_count = metrics.get('process_count')
        if process_count is not None and isinstance(process_count, int) and process_count >= 0:
            validated['process_count'] = process_count
            
        # Load average validation
        load_avg = metrics.get('load_avg')
        if load_avg and isinstance(load_avg, (list, tuple)) and len(load_avg) >= 3:
            validated['load_avg'] = load_avg
            
        # Timestamp validation
        timestamp = metrics.get('timestamp')
        if timestamp:
            validated['timestamp'] = timestamp
            
        return validated
    
    def _make_decision(self, cpu: float, memory: float, disk: float, validated_metrics: Dict[str, Any]) -> HawkingtonDecision:
        """
        Sir Hawkington's decision-making logic based on REAL data.
        A gentleman's approach to system analysis.
        """
        
        # Calculate overall system stress (Sir Hawkington's refined formula)
        stress_score = self._calculate_stress_score(cpu, memory, disk, validated_metrics)
        
        # Determine monocle state based on stress
        monocle_state = self._determine_monocle_state(stress_score)
        
        # Sir Hawkington's refined decision logic
        if stress_score >= self.critical_threshold:
            return self._create_critical_decision(stress_score, cpu, memory, disk, validated_metrics, monocle_state)
        elif stress_score >= self.alert_threshold:
            return self._create_alert_decision(stress_score, cpu, memory, disk, validated_metrics, monocle_state)
        elif stress_score >= self.concern_threshold:
            return self._create_concern_decision(stress_score, cpu, memory, disk, validated_metrics, monocle_state)
        else:
            return self._create_normal_decision(stress_score, cpu, memory, disk, validated_metrics, monocle_state)
    
    def _calculate_stress_score(self, cpu: float, memory: float, disk: float, metrics: Dict[str, Any]) -> float:
        """
        Sir Hawkington's refined stress calculation formula.
        A gentleman considers all factors with appropriate weighting.
        """
        # Base weights - Sir Hawkington's experience-based preferences
        weights = {
            'cpu': 0.25,
            'memory': 0.35,    # Memory issues are particularly concerning
            'disk': 0.25,
            'load': 0.10,      # Load average provides additional context
            'processes': 0.05  # Process count can indicate problems
        }
        
        # Convert percentages to 0-1 scale
        cpu_score = cpu / 100.0
        memory_score = memory / 100.0
        disk_score = disk / 100.0
        
        # Calculate base stress
        base_stress = (
            cpu_score * weights['cpu'] +
            memory_score * weights['memory'] +
            disk_score * weights['disk']
        )
        
        # Add load average consideration if available
        load_avg = metrics.get('load_avg')
        if load_avg and len(load_avg) >= 1:
            # Normalize load average (assuming 4-core system as baseline)
            normalized_load = min(load_avg[0] / 4.0, 1.0)
            base_stress += normalized_load * weights['load']
        
        # Add process count consideration if available
        process_count = metrics.get('process_count')
        if process_count is not None:
            # Normalize process count (200+ processes is concerning)
            normalized_processes = min(process_count / 200.0, 1.0)
            base_stress += normalized_processes * weights['processes']
        
        return min(base_stress, 1.0)  # Cap at 1.0
    
    def _determine_monocle_state(self, stress_score: float) -> MonocleState:
        """Determine Sir Hawkington's monocle state based on system stress"""
        if stress_score >= self.critical_threshold:
            return MonocleState.YEETED
        elif stress_score >= self.alert_threshold:
            return MonocleState.FOGGED
        elif stress_score >= self.concern_threshold:
            return MonocleState.ADJUSTED
        else:
            return MonocleState.POLISHED
    
    def _create_critical_decision(self, stress: float, cpu: float, memory: float, disk: float, metrics: Dict[str, Any], monocle_state: MonocleState) -> HawkingtonDecision:
        """Sir Hawkington creates a CRITICAL decision - the most severe"""
        
        # Identify the most severe problems
        critical_issues = []
        if cpu >= 95: critical_issues.append(f"CPU at critical {cpu:.1f}%")
        if memory >= 95: critical_issues.append(f"Memory at critical {memory:.1f}%")
        if disk >= 98: critical_issues.append(f"Disk at critical {disk:.1f}%")
        
        if not critical_issues:
            critical_issues.append(f"System stress at critical {stress*100:.1f}%")
        
        message = f"🧐💥🚨 Sir Hawkington has YEETED his monocle in absolute horror! CRITICAL SYSTEM FAILURE IMMINENT: {', '.join(critical_issues)}. IMMEDIATE EMERGENCY INTERVENTION REQUIRED!"
        
        return HawkingtonDecision(
            decision_type=DecisionType.CRITICAL,
            message=message,
            confidence=0.98,  # Sir Hawkington is extremely certain about critical situations
            timestamp=datetime.now(),
            metrics_snapshot=metrics,
            reasoning=f"System stress score {stress:.3f} indicates critical system failure risk. Emergency protocols must be activated immediately.",
            stress_score=stress,
            monocle_state=monocle_state
        )
    
    def _create_alert_decision(self, stress: float, cpu: float, memory: float, disk: float, metrics: Dict[str, Any], monocle_state: MonocleState) -> HawkingtonDecision:
        """Sir Hawkington creates an ALERT decision"""
        
        # Find significant problems
        problems = []
        if cpu >= 85: problems.append(f"CPU at {cpu:.1f}%")
        if memory >= 85: problems.append(f"Memory at {memory:.1f}%")
        if disk >= 90: problems.append(f"Disk at {disk:.1f}%")
        
        if not problems:
            problems.append(f"Overall system stress at {stress*100:.1f}%")
        
        message = f"🧐🚨 Sir Hawkington's monocle has fogged with serious concern! System stress alert: {', '.join(problems)}. Prompt attention required to prevent escalation!"
        
        return HawkingtonDecision(
            decision_type=DecisionType.ALERT,
            message=message,
            confidence=0.92,
            timestamp=datetime.now(),
            metrics_snapshot=metrics,
            reasoning=f"System stress score {stress:.3f} exceeds alert threshold {self.alert_threshold}. System intervention recommended.",
            stress_score=stress,
            monocle_state=monocle_state
        )
    
    def _create_concern_decision(self, stress: float, cpu: float, memory: float, disk: float, metrics: Dict[str, Any], monocle_state: MonocleState) -> HawkingtonDecision:
        """Sir Hawkington creates a CONCERN decision"""
        
        concerns = []
        if cpu >= 70: concerns.append(f"CPU at {cpu:.1f}%")
        if memory >= 70: concerns.append(f"Memory at {memory:.1f}%")
        if disk >= 75: concerns.append(f"Disk at {disk:.1f}%")
        
        concern_detail = f" ({', '.join(concerns)})" if concerns else f" (stress level {stress*100:.1f}%)"
        
        message = f"🧐 Sir Hawkington adjusts his monocle with measured concern. System metrics warrant attention{concern_detail}. Monitoring closely for trends."
        
        return HawkingtonDecision(
            decision_type=DecisionType.CONCERN,
            message=message,
            confidence=0.85,
            timestamp=datetime.now(),
            metrics_snapshot=metrics,
            reasoning=f"System stress score {stress:.3f} exceeds concern threshold {self.concern_threshold}. Proactive monitoring recommended.",
            stress_score=stress,
            monocle_state=monocle_state
        )
    
    def _create_normal_decision(self, stress: float, cpu: float, memory: float, disk: float, metrics: Dict[str, Any], monocle_state: MonocleState) -> HawkingtonDecision:
        """Sir Hawkington creates a NORMAL decision"""
        
        # Sir Hawkington occasionally comments on normal operations (gentleman's discretion)
        import random
        if random.random() < 0.15:  # 15% chance of commenting on normal state
            satisfactory_comments = [
                "🧐 Sir Hawkington's monocle gleams with satisfaction. All systems operating within acceptable parameters.",
                "🧐 Sir Hawkington nods approvingly. System performance meets aristocratic standards.",
                "🧐 Sir Hawkington polishes his monocle contentedly. Operations proceeding as a gentleman expects.",
                "🧐 Sir Hawkington observes with quiet satisfaction. System metrics demonstrate proper decorum."
            ]
            message = random.choice(satisfactory_comments)
        else:
            message = None  # Usually silent during normal operations - a gentleman doesn't state the obvious
        
        return HawkingtonDecision(
            decision_type=DecisionType.NORMAL,
            message=message,
            confidence=0.88,
            timestamp=datetime.now(),
            metrics_snapshot=metrics,
            reasoning=f"System stress score {stress:.3f} indicates normal operations. No intervention required.",
            stress_score=stress,
            monocle_state=monocle_state
        )
    
    def _store_decision(self, decision: HawkingtonDecision):
        """Store Sir Hawkington's decision in his distinguished memory"""
        self.recent_decisions.append(decision)
        
        # Maintain memory size with aristocratic efficiency
        if len(self.recent_decisions) > self.max_memory_size:
            self.recent_decisions = self.recent_decisions[-self.max_memory_size:]
    
    def _yeet_monocle(self, reason: str):
        """Sir Hawkington yeeted his monocle due to data quality issues"""
        self.monocle_yeet_count += 1
        self.current_monocle_state = MonocleState.YEETED
        self.last_monocle_yeet_time = datetime.now()
        
        # Log the aristocratic indignation
        self.logger.warning(f"🧐💥 MONOCLE YEET #{self.monocle_yeet_count}! Reason: {reason}")
    
    def _polish_monocle(self):
        """Sir Hawkington polishes his monocle after successful analysis"""
        if self.current_monocle_state == MonocleState.YEETED:
            self.logger.info("🧐✨ Sir Hawkington retrieves and polishes his monocle. Data quality restored.")
        
        self.current_monocle_state = MonocleState.POLISHED
    
    def get_recent_decisions(self, limit: int = 10) -> List[HawkingtonDecision]:
        """Get Sir Hawkington's recent decisions"""
        return self.recent_decisions[-limit:]
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get Sir Hawkington's performance and data quality statistics"""
        success_rate = (self.successful_analyses / self.total_analyses_attempted * 100) if self.total_analyses_attempted > 0 else 0
        
        # Calculate decision type distribution
        decision_counts = {}
        for decision in self.recent_decisions[-50:]:  # Last 50 decisions
            decision_type = str(decision.decision_type)
            decision_counts[decision_type] = decision_counts.get(decision_type, 0) + 1
        
        return {
            'agent_name': 'sir_hawkington',
            'total_analyses_attempted': self.total_analyses_attempted,
            'successful_analyses': self.successful_analyses,
            'success_rate_percentage': round(success_rate, 2),
            'monocle_yeet_count': self.monocle_yeet_count,
            'current_monocle_state': self.current_monocle_state.value,
            'last_monocle_yeet': self.last_monocle_yeet_time.isoformat() if self.last_monocle_yeet_time else None,
            'recent_decision_distribution': decision_counts,
            'data_quality_policy': 'ZERO_TOLERANCE_FOR_FABRICATED_DATA',
            'aristocratic_standards': 'MAINTAINED'
        }
    
    def get_monocle_status(self) -> Dict[str, Any]:
        """Get detailed monocle status - a gentleman tracks his equipment"""
        time_since_last_yeet = None
        if self.last_monocle_yeet_time:
            time_since_last_yeet = (datetime.now() - self.last_monocle_yeet_time).total_seconds()
        
        return {
            'current_state': self.current_monocle_state.value,
            'total_yeets': self.monocle_yeet_count,
            'last_yeet_time': self.last_monocle_yeet_time.isoformat() if self.last_monocle_yeet_time else None,
            'seconds_since_last_yeet': time_since_last_yeet,
            'yeet_frequency': round(self.monocle_yeet_count / max(self.total_analyses_attempted, 1), 4),
            'monocle_condition': 'ARISTOCRATIC' if self.monocle_yeet_count < 10 else 'WELL_EXERCISED'
        }
    
    def format_for_websocket(self, decision: HawkingtonDecision) -> Dict[str, Any]:
        """Format Sir Hawkington's decision for WebSocket transmission"""
        return {
            'agent_name': 'sir_hawkington',
            'decision_type': str(decision.decision_type),
            'message': decision.message,
            'confidence': round(decision.confidence, 3),
            'stress_score': round(decision.stress_score, 3),
            'monocle_state': str(decision.monocle_state),
            'reasoning': decision.reasoning,
            'data_quality': decision.data_quality,
            'timestamp': decision.timestamp.isoformat(),
            'aristocratic_seal_of_approval': True
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Sir Hawkington's health and operational status"""
        return {
            'agent_name': 'sir_hawkington',
            'status': 'OPERATIONAL_AND_DISTINGUISHED',
            'monocle_status': self.current_monocle_state.value,
            'data_integrity_policy': 'ARISTOCRATIC_STANDARDS_MAINTAINED',
            'total_analyses': self.total_analyses_attempted,
            'successful_analyses': self.successful_analyses,
            'monocle_yeets': self.monocle_yeet_count,
            'gentleman_certification': 'VERIFIED',
            'last_decision': self.recent_decisions[-1].timestamp.isoformat() if self.recent_decisions else None
        }
    
    def get_system_assessment_summary(self) -> Dict[str, Any]:
        """Get Sir Hawkington's overall system assessment based on recent decisions"""
        if not self.recent_decisions:
            return {
                'overall_assessment': 'INSUFFICIENT_DATA',
                'recommendation': 'Awaiting sufficient data for proper assessment'
            }
        
        # Analyze last 10 decisions
        recent = self.recent_decisions[-10:]
        decision_types = [d.decision_type for d in recent]
        avg_stress = sum(d.stress_score for d in recent) / len(recent)
        
        # Count decision types
        critical_count = sum(1 for d in decision_types if d == DecisionType.CRITICAL)
        alert_count = sum(1 for d in decision_types if d == DecisionType.ALERT)
        concern_count = sum(1 for d in decision_types if d == DecisionType.CONCERN)
        normal_count = sum(1 for d in decision_types if d == DecisionType.NORMAL)
        
        # Determine overall assessment
        if critical_count > 0:
            assessment = "CRITICAL_INTERVENTION_REQUIRED"
            recommendation = "Immediate emergency response required. System stability at risk."
        elif alert_count >= 3:
            assessment = "URGENT_ATTENTION_NEEDED"
            recommendation = "Multiple alerts detected. Prompt intervention recommended."
        elif concern_count >= 5:
            assessment = "MONITORING_RECOMMENDED"
            recommendation = "Elevated concern levels. Increased monitoring and proactive measures advised."
        elif normal_count >= 7:
            assessment = "SYSTEM_OPERATING_NORMALLY"
            recommendation = "System performing within acceptable parameters. Continue routine monitoring."
        else:
            assessment = "MIXED_CONDITIONS"
            recommendation = "Variable system conditions detected. Maintain vigilant monitoring."
        
        return {
            'overall_assessment': assessment,
            'recommendation': recommendation,
            'average_stress_score': round(avg_stress, 3),
            'recent_decision_counts': {
                'critical': critical_count,
                'alert': alert_count,
                'concern': concern_count,
                'normal': normal_count
            },
            'confidence_in_assessment': 'HIGH' if len(recent) >= 10 else 'MODERATE',
            'gentleman_signature': '🧐 Sir Hawkington, Distinguished System Analyst'
        }