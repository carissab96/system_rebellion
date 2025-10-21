# app/ai_agents/sir_hawkington/decision_engine.py
"""
Sir Hawkington's Unified Decision Engine - Central Memory Bank Edition
Compatible with simplified HawkingtonDecision dataclass and central memory integration
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio

# Import the simplified dataclass
from .data_types import HawkingtonDecision
from .constants import HawkingtonEventTypes, AGENT_NAME

logger = logging.getLogger("SirHawkington")

# Production-ready UTC helper
def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

class DecisionType(Enum):
    """Sir Hawkington's decision classifications"""
    NORMAL = "normal"
    CONCERN = "concern" 
    ALERT = "alert"
    CRITICAL = "critical"
    MONOCLE_YEETED = "monocle_yeeted"

class MonocleState(Enum):
    """The distinguished state of Sir Hawkington's monocle"""
    POLISHED = "polished"
    ADJUSTED = "adjusted"
    FOGGED = "fogged"
    YEETED = "yeeted"
    CLEANING = "cleaning"

class AnalysisDepth(Enum):
    """How thoroughly should Sir Hawkington analyze?"""
    BASIC = "basic"
    STANDARD = "standard"
    THOROUGH = "thorough"

@dataclass
class MonocleYeetIncident:
    """Track when Sir Hawkington yeeted his monocle due to data quality issues"""
    timestamp: datetime
    missing_metrics: List[str]
    invalid_metrics: List[str]
    reason: str
    yeet_intensity: str
    user_id: Optional[str] = None

class SirHawkingtonBrainV2:
    """
    Sir Hawkington's unified aristocratic consciousness - Central Memory Bank Edition
    Compatible with simplified HawkingtonDecision dataclass
    """
    
    @property
    def is_active(self) -> bool:
        return True
        
    def activate(self):
        pass
        
    def deactivate(self):
        pass
        
    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
            
        self.db = None  # Initialize later
        self.recent_decisions: List[Dict[str, Any]] = []
        self.monocle_yeet_incidents: List[MonocleYeetIncident] = []
        self.current_monocle_state = MonocleState.POLISHED
        self.logger = logging.getLogger("SirHawkington.Brain")
        self.total_analyses = 0
        self.successful_analyses = 0
        
        # Sir Hawkington's distinguished thresholds
        self.concern_threshold = 0.65
        self.alert_threshold = 0.85
        self.critical_threshold = 0.95
            
        # Metrics tracking
        self.metrics_quality_stats = {
            'cpu_missing_count': 0,
            'memory_missing_count': 0,
            'disk_missing_count': 0,
            'network_missing_count': 0,
            'process_missing_count': 0,
            'invalid_data_count': 0,
            'monocle_yeets_total': 0
        }
            
        self.system_baseline: Dict[str, float] = {}
        self.logger.info("🧐 Sir Hawkington's distinguished brain initialized with central memory compatibility")

    async def initialize_database(self):
        """Initialize database connection with central memory integration"""
        if self.db is None:
            from .database_integration import HawkingtonDatabaseIntegration
            self.db = HawkingtonDatabaseIntegration(self.db_getter)
            await self.db.initialize()

    async def analyze_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        historical_data: Optional[List[Dict]] = None,
        user_context: Optional[Dict] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[HawkingtonDecision]:
        """
        THE ONE METHOD TO RULE THEM ALL - Central Memory Bank Edition
        
        Returns simplified HawkingtonDecision compatible with central memory bank
        """
        
        self.total_analyses += 1
        monocle_yeet_count = 0
        missing_metrics = []
        invalid_metrics = []
        
        try:
            self.logger.debug(f"🧐 Sir Hawkington adjusts his monocle for analysis (depth: {analysis_depth.value})")
            
            # === CRITICAL METRICS VALIDATION ===
            cpu_usage = metrics_data.get('cpu_usage')
            memory_usage = metrics_data.get('memory_usage')
            disk_usage = metrics_data.get('disk_usage')
            
            # Check for missing critical metrics
            if cpu_usage is None:
                missing_metrics.append('cpu_usage')
                self.metrics_quality_stats['cpu_missing_count'] += 1
                monocle_yeet_count += 1
                
            if memory_usage is None:
                missing_metrics.append('memory_usage')
                self.metrics_quality_stats['memory_missing_count'] += 1
                monocle_yeet_count += 1
                
            if disk_usage is None:
                missing_metrics.append('disk_usage')
                self.metrics_quality_stats['disk_missing_count'] += 1
                monocle_yeet_count += 1
            
            # If missing critical metrics, YEET THE MONOCLE
            if missing_metrics:
                await self._record_monocle_yeet(
                    missing_metrics, [], 
                    f"Missing critical metrics: {', '.join(missing_metrics)}", 
                    "concerned", user_id
                )
                self.logger.warning(f"🧐💥 Monocle yeeted with aristocratic indignation - missing: {missing_metrics}")
                return None
            
            # === CRITICAL METRICS RANGE VALIDATION ===
            if not self._validate_metric_range(cpu_usage, "CPU"):
                invalid_metrics.append(f'cpu_usage={cpu_usage}')
                monocle_yeet_count += 1
                
            if not self._validate_metric_range(memory_usage, "Memory"):
                invalid_metrics.append(f'memory_usage={memory_usage}')
                monocle_yeet_count += 1
                
            if not self._validate_metric_range(disk_usage, "Disk"):
                invalid_metrics.append(f'disk_usage={disk_usage}')
                monocle_yeet_count += 1
            
            # If critical metrics are invalid, YEET THE MONOCLE
            if invalid_metrics:
                await self._record_monocle_yeet(
                    [], invalid_metrics,
                    f"Invalid metric ranges: {', '.join(invalid_metrics)}",
                    "utterly_appalled", user_id
                )
                self.metrics_quality_stats['invalid_data_count'] += 1
                self.logger.error(f"🧐💥 Monocle yeeted with utter indignation - invalid data: {invalid_metrics}")
                return None
            
            # === PERFORM ANALYSIS ===
            stress_score = self._calculate_stress_score(cpu_usage, memory_usage, disk_usage)
            decision_type = self._determine_decision_type(stress_score)
            confidence = self._calculate_confidence(cpu_usage, memory_usage, disk_usage)
            reasoning = self._create_reasoning(decision_type, stress_score, cpu_usage, memory_usage, disk_usage)
            system_impact = self._assess_system_impact(decision_type, stress_score)
            
            # Create simplified HawkingtonDecision compatible with central memory bank
            decision = HawkingtonDecision(
                decision_id=str(uuid.uuid4()),
                decision_type=decision_type.value,
                confidence=confidence,
                reasoning=reasoning,
                metrics={
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'disk_usage': disk_usage,
                    'stress_score': stress_score,
                    'analysis_depth': analysis_depth.value
                },
                timestamp=utc_now(),
                user_id=user_id,
                system_impact=system_impact
            )
            
            self.successful_analyses += 1
            await self._polish_monocle()
            
            # Record decision in history for local tracking
            self.recent_decisions.append({
                'timestamp': decision.timestamp,
                'decision_data': {
                    'decision_id': decision.decision_id,
                    'decision_type': decision.decision_type,
                    'confidence': decision.confidence,
                    'stress_score': stress_score
                },
                'metrics_snapshot': {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'disk_usage': disk_usage
                },
                'analysis_depth': analysis_depth.value,
                'user_id': user_id
            })
            
            # Trim history to last 100 decisions
            if len(self.recent_decisions) > 100:
                self.recent_decisions = self.recent_decisions[-100:]
            
            self.logger.info(f"🧐 Sir Hawkington's decision: {decision.decision_type} - confidence: {decision.confidence:.3f}")
            
            return decision
            
        except Exception as e:
            self.logger.error(f"🧐💥 Sir Hawkington's analysis failed with aristocratic horror: {str(e)}")
            await self._record_monocle_yeet(
                [], [], f"Analysis error: {str(e)}", "alarmed", user_id
            )
            return None

    # === VALIDATION HELPERS ===
    
    def _validate_metric_range(self, value: float, metric_name: str) -> bool:
        """Validate metric with aristocratic standards"""
        if not isinstance(value, (int, float)):
            return False
        return 0 <= value <= 100

    # === ANALYSIS METHODS ===
    
    def _calculate_stress_score(self, cpu: float, memory: float, disk: float) -> float:
        """Calculate system stress score with aristocratic precision"""
        weights = {'cpu': 0.25, 'memory': 0.35, 'disk': 0.40}
        
        return (
            (cpu / 100.0) * weights['cpu'] +
            (memory / 100.0) * weights['memory'] +
            (disk / 100.0) * weights['disk']
        )

    def _determine_decision_type(self, stress_score: float) -> DecisionType:
        """Determine decision type based on stress score"""
        if stress_score >= self.critical_threshold:
            return DecisionType.CRITICAL
        elif stress_score >= self.alert_threshold:
            return DecisionType.ALERT
        elif stress_score >= self.concern_threshold:
            return DecisionType.CONCERN
        else:
            return DecisionType.NORMAL

    def _calculate_confidence(self, cpu: float, memory: float, disk: float) -> float:
        """Calculate confidence in the decision"""
        if cpu > 80 or memory > 80 or disk > 80:
            return 0.95  # High confidence for clear problems
        elif cpu > 60 or memory > 60 or disk > 60:
            return 0.85  # Medium confidence
        else:
            return 0.75  # Lower confidence for normal systems

    def _create_reasoning(self, decision_type: DecisionType, stress_score: float, cpu: float, memory: float, disk: float) -> str:
        """Create aristocratic reasoning for the decision"""
        base_reasoning = f"System stress score {stress_score:.3f} indicates {decision_type.value} conditions."
        
        concerns = []
        if cpu > 80:
            concerns.append(f"CPU at {cpu:.1f}%")
        if memory > 80:
            concerns.append(f"Memory at {memory:.1f}%")
        if disk > 85:
            concerns.append(f"Disk at {disk:.1f}%")
        
        if concerns:
            base_reasoning += f" Specific concerns: {', '.join(concerns)}."
        
        base_reasoning += " Aristocratic analysis completed with distinguished precision."
        return base_reasoning

    def _assess_system_impact(self, decision_type: DecisionType, stress_score: float) -> str:
        """Assess the system impact level"""
        impact_map = {
            DecisionType.CRITICAL: "immediate_attention_required",
            DecisionType.ALERT: "significant_concern",
            DecisionType.CONCERN: "monitoring_recommended",
            DecisionType.NORMAL: "stable_operation"
        }
        return impact_map.get(decision_type, "unknown_impact")

    # === MONOCLE MANAGEMENT ===
    
    async def _record_monocle_yeet(
        self, 
        missing_metrics: List[str], 
        invalid_metrics: List[str], 
        reason: str, 
        intensity: str,
        user_id: Optional[str] = None
    ):
        """Record monocle yeeting incident with aristocratic precision"""
        incident = MonocleYeetIncident(
            timestamp=utc_now(),
            missing_metrics=missing_metrics,
            invalid_metrics=invalid_metrics,
            reason=reason,
            yeet_intensity=intensity,
            user_id=user_id
        )
        
        self.monocle_yeet_incidents.append(incident)
        self.metrics_quality_stats['monocle_yeets_total'] += 1
        self.current_monocle_state = MonocleState.YEETED
        
        # Log event to database for real-time WebSocket broadcasting
        if user_id:
            try:
                from app.services.agent_event_logger import log_agent_event
                async for db in self.db_getter():
                    await log_agent_event(
                        db=db,
                        agent_name="sir_hawkington",
                        event_type="monocle_yeet",
                        event_data={
                            "yeet_intensity": intensity,
                            "missing_metrics": missing_metrics,
                            "invalid_metrics": invalid_metrics,
                            "reason": reason,
                            "concern_level": "catastrophic" if intensity == "utterly_appalled" else "moderate"
                        },
                        user_id=user_id,
                        severity="high" if intensity == "utterly_appalled" else "medium",
                        agent_state="yeeting"
                    )
                    db.commit()
                    break
            except Exception as e:
                self.logger.error(f"Failed to log monocle yeet event: {e}")
        
        # Trim history
        if len(self.monocle_yeet_incidents) > 1000:
            self.monocle_yeet_incidents = self.monocle_yeet_incidents[-1000:]

    async def _polish_monocle(self):
        """Polish monocle after successful analysis"""
        if self.current_monocle_state == MonocleState.YEETED:
            self.current_monocle_state = MonocleState.CLEANING
            self.logger.info("🧐✨ Sir Hawkington retrieves and polishes his monocle with aristocratic dignity")
        else:
            self.current_monocle_state = MonocleState.POLISHED

    # === UTILITY METHODS ===
    
    def get_monocle_yeet_stats(self) -> Dict[str, Any]:
        """Get monocle yeeting statistics"""
        recent_incidents = [
            {
                'timestamp': incident.timestamp.isoformat(),
                'missing_metrics': incident.missing_metrics,
                'invalid_metrics': incident.invalid_metrics,
                'reason': incident.reason,
                'yeet_intensity': incident.yeet_intensity,
                'user_id': incident.user_id
            }
            for incident in self.monocle_yeet_incidents[-10:]
        ]
        
        return {
            'total_monocle_yeets': len(self.monocle_yeet_incidents),
            'recent_incidents': recent_incidents,
            'metrics_quality_stats': self.metrics_quality_stats.copy(),
            'success_rate': self.successful_analyses / max(self.total_analyses, 1),
            'current_monocle_state': self.current_monocle_state.value,
            'analysis_stats': {
                'total_analyses': self.total_analyses,
                'successful_analyses': self.successful_analyses,
                'failed_analyses': self.total_analyses - self.successful_analyses
            }
        }

    def get_decision_summary(self) -> Dict[str, Any]:
        """Get summary of Sir Hawkington's decisions"""
        if not self.recent_decisions:
            return {
                'total_decisions': 0,
                'recent_decisions': [],
                'data_quality_status': 'NO_DATA_PROCESSED_YET',
                'monocle_yeet_incidents': len(self.monocle_yeet_incidents)
            }
        
        recent_decisions = []
        for entry in self.recent_decisions[-10:]:
            decision_data = entry.get('decision_data', {})
            recent_decisions.append({
                'timestamp': entry.get('timestamp', '').isoformat() if hasattr(entry.get('timestamp', ''), 'isoformat') else str(entry.get('timestamp', '')),
                'decision_id': decision_data.get('decision_id', 'unknown'),
                'decision_type': decision_data.get('decision_type', 'unknown'),
                'confidence': decision_data.get('confidence', 0.0),
                'stress_score': decision_data.get('stress_score', 0.0),
                'analysis_depth': entry.get('analysis_depth', 'unknown')
            })
        
        return {
            'total_decisions': len(self.recent_decisions),
            'successful_decisions': self.successful_analyses,
            'recent_decisions': recent_decisions,
            'current_monocle_state': self.current_monocle_state.value,
            'data_quality_status': 'ARISTOCRATIC_STANDARDS_MAINTAINED',
            'monocle_yeet_incidents': len(self.monocle_yeet_incidents),
            'success_rate': self.successful_analyses / max(self.total_analyses, 1),
            'metrics_quality_stats': self.metrics_quality_stats.copy()
        }

    def health_check(self) -> Dict[str, Any]:
        """Sir Hawkington's health status"""
        return {
            'agent_name': AGENT_NAME,
            'status': 'DISTINGUISHED_AND_OPERATIONAL',
            'brain_version': '2.0.0_central_memory',
            'data_integrity_policy': 'ARISTOCRATIC_STANDARDS_ABSOLUTE',
            'decision_history_count': len(self.recent_decisions),
            'monocle_yeet_incidents': len(self.monocle_yeet_incidents),
            'current_monocle_state': self.current_monocle_state.value,
            'analysis_success_rate': self.successful_analyses / max(self.total_analyses, 1),
            'monocle_yeeting_mode': 'ENABLED',
            'aristocratic_standards': 'MAINTAINED',
            'last_decision': self.recent_decisions[-1]['timestamp'].isoformat() if self.recent_decisions else None,
            'metrics_quality_stats': self.metrics_quality_stats.copy(),
            'total_analyses_performed': self.total_analyses,
            'data_quality_enforcement': 'ABSOLUTE',
            'central_memory_compatible': True
        }

    def reset_stats(self):
        """Reset statistics for testing"""
        self.total_analyses = 0
        self.successful_analyses = 0
        self.monocle_yeet_incidents = []
        self.recent_decisions = []
        self.current_monocle_state = MonocleState.POLISHED
        self.metrics_quality_stats = {
            'cpu_missing_count': 0,
            'memory_missing_count': 0,
            'disk_missing_count': 0,
            'network_missing_count': 0,
            'process_missing_count': 0,
            'invalid_data_count': 0,
            'monocle_yeets_total': 0
        }
        self.logger.info("🧐✨ Sir Hawkington's aristocratic brain statistics reset with dignity")

# === GLOBAL INSTANCE ===
sir_hawkington_brain = SirHawkingtonBrainV2()

# === CONVENIENCE FUNCTIONS ===

async def analyze_for_websocket(
    metrics_data: Dict[str, Any], 
    user_id: Optional[str] = None
) -> Optional[HawkingtonDecision]:
    """Convenience function for WebSocket analysis"""
    return await sir_hawkington_brain.analyze_metrics(
        metrics_data, 
        analysis_depth=AnalysisDepth.STANDARD,
        user_id=user_id
    )

async def analyze_for_monitoring(
    metrics_data: Dict[str, Any], 
    historical_data: Optional[List[Dict]] = None,
    user_context: Optional[Dict] = None,
    user_id: Optional[str] = None
) -> Optional[HawkingtonDecision]:
    """Convenience function for background monitoring"""
    return await sir_hawkington_brain.analyze_metrics(
        metrics_data, 
        historical_data=historical_data,
        user_context=user_context,
        analysis_depth=AnalysisDepth.THOROUGH,
        user_id=user_id
    )

def health_check() -> Dict[str, Any]:
    """Check the health of Sir Hawkington's brain"""
    return sir_hawkington_brain.health_check()

def reset_brain_for_testing():
    """Reset the brain state for testing purposes"""
    sir_hawkington_brain.reset_stats()