# app/ai_agents/sir_hawkington/decision_engine_v2.py
"""
Sir Hawkington's Unified Decision Engine - ARISTOCRATIC STANDARDS EDITION
One method to rule them all, one monocle to find them,
One analysis to bring them all, and in the monitoring bind them.

NO FAKE DATA TOLERANCE: ABSOLUTE
Monocle yeeting incidents: METICULOUSLY TRACKED
Pure aristocratic thinking: MAINTAINED
Database integration: DISTINGUISHED

🧐 "A gentleman never compromises on data quality" - Sir Hawkington
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
from .data_types import HawkingtonDecision

logger = logging.getLogger("SirHawkington")

class DecisionType(Enum):
    """Sir Hawkington's decision classifications"""
    NORMAL = "normal"
    CONCERN = "concern" 
    ALERT = "alert"
    CRITICAL = "critical"
    MONOCLE_YEETED = "monocle_yeeted"  # When data quality is insufficient

class MonocleState(Enum):
    """The distinguished state of Sir Hawkington's monocle"""
    POLISHED = "polished"           # All is well
    ADJUSTED = "adjusted"           # Mild concern
    FOGGED = "fogged"              # Significant concern
    YEETED = "yeeted"              # Data quality failure
    CLEANING = "cleaning"          # Recovering from yeet

class AnalysisDepth(Enum):
    """How thoroughly should Sir Hawkington analyze?"""
    BASIC = "basic"           # Quick analysis with minimal data
    STANDARD = "standard"     # Normal depth analysis
    THOROUGH = "thorough"     # Full analysis with historical patterns

@dataclass
class MonocleYeetIncident:
    """Track when Sir Hawkington yeeted his monocle due to data quality issues"""
    timestamp: datetime
    missing_metrics: List[str]
    invalid_metrics: List[str]
    reason: str
    yeet_intensity: str  # 'polite', 'concerned', 'alarmed', 'utterly_appalled'
    user_id: Optional[str] = None

@dataclass
class HawkingtonDecision:
    """
    Sir Hawkington's distinguished decision about system health.
    Only created when sufficient real data permits proper aristocratic assessment.
    """
    decision_type: DecisionType
    message: Optional[str]          # None for silent normal operations
    confidence: float               # 0.0 to 1.0
    stress_score: float            # Sir Hawkington's calculated system stress
    monocle_state: MonocleState
    reasoning: str
    estimated_impact: Dict[str, float]  # Expected system improvements needed
    urgency: str                   # 'immediate', 'soon', 'eventual'
    analysis_depth: AnalysisDepth
    monocle_yeet_count: int       # How many times monocle was yeeted
    data_quality_score: float     # 0.0 to 1.0
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Sir Hawkington's decision to a dictionary for JSON serialization.
        Essential for aristocratic data transmission to frontend peasants.
        """
        return {
            'decision_type': self.decision_type.value if hasattr(self.decision_type, 'value') else str(self.decision_type),
            'message': self.message,
            'confidence': self.confidence,
            'stress_score': self.stress_score,
            'monocle_state': self.monocle_state.value if hasattr(self.monocle_state, 'value') else str(self.monocle_state),
            'reasoning': self.reasoning,
            'estimated_impact': self.estimated_impact,
            'urgency': self.urgency,
            'analysis_depth': self.analysis_depth.value if hasattr(self.analysis_depth, 'value') else str(self.analysis_depth),
            'monocle_yeet_count': self.monocle_yeet_count,
            'data_quality_score': self.data_quality_score,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class SirHawkingtonBrainV2:
    """
    Sir Hawkington's unified aristocratic consciousness.
    One brain, one method, pure distinguished decisions only.
    ABSOLUTE INTOLERANCE FOR FABRICATED DATA.
    """
    
    @property
    def is_active(self) -> bool:
        """Sir Hawkington is always active and ready for aristocratic analysis"""
        return True
        
    def activate(self):
        """Sir Hawkington cannot be deactivated -  he's always vigilant"""
        pass
        
    def deactivate(self):
        """Sir Hawkington refuses to be deactivated - aristrocraticc duty never sleeps"""
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
            
        # Metrics tracking for database storage
        self.metrics_quality_stats = {
            'cpu_missing_count': 0,
            'memory_missing_count': 0,
            'disk_missing_count': 0,
            'network_missing_count': 0,
            'process_missing_count': 0,
            'invalid_data_count': 0,
            'monocle_yeets_total': 0
        }
            
        # System baseline for pattern recognition
        self.system_baseline: Dict[str, float] = {}
            
        self.logger.info("🧐 Sir Hawkington's distinguished brain initialized. Monocle polished to aristocratic perfection.")
    
    def initialize_database(self):
        """Initialize database connection with aristocratic dignity"""
        if self.db is None:
            from .database_integration import HawkingtonDatabaseIntegration
            self.db = HawkingtonDatabaseIntegration(self.db_getter)
            self.db.initialize()

    async def analyze_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        historical_data: Optional[List[Dict]] = None,
        user_context: Optional[Dict] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[HawkingtonDecision]:
        """
        THE ONE METHOD TO RULE THEM ALL - ARISTOCRATIC EDITION WITH DATABASE
        
        Sir Hawkington's unified analysis with absolute intolerance for fake data.
        Returns None if data quality is beneath aristocratic standards.
        
        Args:
            metrics_data: The system metrics (MUST BE AUTHENTIC)
            historical_data: Optional historical context for pattern analysis
            user_context: Optional user information
            analysis_depth: How thorough should the analysis be
            user_id: For tracking monocle yeets per user
            
        Returns:
            HawkingtonDecision or None if data quality is insufficient
        """
        
        # Store incoming metrics in database
        if self.db and user_id:
            self.db.store_metrics(user_id, metrics_data)
        
        # Get historical data from database if not provided
        if not historical_data and self.db and user_id:
            historical_data = self.db.get_historical_decisions(user_id, days=7)
        
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
            
            # Check for missing critical metrics - A gentleman demands completeness
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
                self._record_monocle_yeet(
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
                self._record_monocle_yeet(
                    [], invalid_metrics,
                    f"Invalid metric ranges: {', '.join(invalid_metrics)}",
                    "utterly_appalled", user_id
                )
                self.metrics_quality_stats['invalid_data_count'] += 1
                self.logger.error(f"🧐💥 Monocle yeeted with utter indignation - invalid data: {invalid_metrics}")
                return None
            
            # === OPTIONAL METRICS VALIDATION ===
            network_data = self._validate_network_data(metrics_data.get('network'))
            process_count = self._validate_process_count(metrics_data.get('process_count'))
            load_avg = self._validate_load_average(metrics_data.get('load_avg'))
            
            if metrics_data.get('network') is not None and network_data is None:
                self.metrics_quality_stats['network_missing_count'] += 1
                
            if metrics_data.get('process_count') is not None and process_count is None:
                self.metrics_quality_stats['process_missing_count'] += 1
            
            # === CALCULATE DATA QUALITY SCORE ===
            data_quality_score = self._calculate_data_quality_score(
                cpu_usage, memory_usage, disk_usage, network_data, process_count, load_avg
            )
            
            # === ANALYSIS DEPTH BRANCHING ===
            if analysis_depth == AnalysisDepth.BASIC:
                decision = self._basic_analysis(
                    cpu_usage, memory_usage, disk_usage, 
                    monocle_yeet_count, data_quality_score
                )
            elif analysis_depth == AnalysisDepth.THOROUGH:
                decision = self._thorough_analysis(
                    cpu_usage, memory_usage, disk_usage,
                    network_data, process_count, load_avg, historical_data,
                    monocle_yeet_count, data_quality_score
                )
            else:  # STANDARD
                decision = self._standard_analysis(
                    cpu_usage, memory_usage, disk_usage,
                    network_data, process_count, load_avg,
                    monocle_yeet_count, data_quality_score
                )
            
            if decision:
                self.successful_analyses += 1
                self._polish_monocle()
                
                # Store decision in database
                if self.db and user_id:
                    self.db.store_decision(user_id, decision)
                
                # Record decision in history
                self.recent_decisions.append({
                    'timestamp': decision.timestamp,
                    'decision': decision.to_dict(),
                    'metrics_snapshot': {
                        'cpu_usage': cpu_usage,
                        'memory_usage': memory_usage,
                        'disk_usage': disk_usage,
                        'network_available': network_data is not None,
                        'process_count': process_count,
                        'load_avg': load_avg,
                        'data_quality_score': data_quality_score
                    },
                    'analysis_depth': analysis_depth.value,
                    'user_id': user_id
                })
                
                # Trim history to last 100 decisions
                if len(self.recent_decisions) > 100:
                    self.recent_decisions = self.recent_decisions[-100:]
                
                self.logger.info(f"🧐 Sir Hawkington's decision: {decision.decision_type.value} - {decision.message}")
                
            return decision
            
        except Exception as e:
            self.logger.error(f"🧐💥 Sir Hawkington's analysis failed with aristocratic horror: {str(e)}")
            self._record_monocle_yeet(
                [], [], f"Analysis error: {str(e)}", "alarmed", user_id
            )
            return None
    
    def _basic_analysis(
            self, 
            cpu: float, 
            memory: float, 
            disk: float,
            monocle_yeet_count: int,
            data_quality_score: float
        ) -> HawkingtonDecision:
        """Quick aristocratic analysis with minimal data requirements"""
        
        stress_score = self._calculate_basic_stress_score(cpu, memory, disk)
        monocle_state = self._determine_monocle_state(stress_score)
        decision_type = self._determine_decision_type(stress_score)
        
        confidence = self._calculate_basic_confidence(cpu, memory, disk)
        urgency = self._assess_urgency_basic(cpu, memory, disk)
        message = self._create_basic_message(decision_type, stress_score, cpu, memory, disk)
        reasoning = self._create_basic_reasoning(decision_type, stress_score, cpu, memory, disk)
        estimated_impact = self._estimate_basic_impact(decision_type, cpu, memory, disk)
        
        return HawkingtonDecision(
            decision_type=decision_type,
            message=message,
            confidence=confidence,
            stress_score=stress_score,
            monocle_state=monocle_state,
            reasoning=reasoning,
            estimated_impact=estimated_impact,
            urgency=urgency,
            analysis_depth=AnalysisDepth.BASIC,
            monocle_yeet_count=monocle_yeet_count,
            data_quality_score=data_quality_score,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _standard_analysis(
            self, 
            cpu: float, 
            memory: float, 
            disk: float,
            network_data: Optional[Dict],
            process_count: Optional[int],
            load_avg: Optional[List[float]],
            monocle_yeet_count: int,
            data_quality_score: float
        ) -> HawkingtonDecision:
        """Standard aristocratic analysis with optional metrics"""
        
        stress_score = self._calculate_standard_stress_score(cpu, memory, disk, network_data, process_count, load_avg)
        monocle_state = self._determine_monocle_state(stress_score)
        decision_type = self._determine_decision_type(stress_score)
        
        confidence = self._calculate_standard_confidence(cpu, memory, disk, network_data, process_count)
        urgency = self._assess_urgency_standard(cpu, memory, disk, network_data, load_avg)
        message = self._create_standard_message(decision_type, stress_score, cpu, memory, disk, network_data, process_count)
        reasoning = self._create_standard_reasoning(decision_type, stress_score, cpu, memory, disk, network_data, process_count)
        estimated_impact = self._estimate_standard_impact(decision_type, cpu, memory, disk, network_data, process_count)
        
        return HawkingtonDecision(
            decision_type=decision_type,
            message=message,
            confidence=confidence,
            stress_score=stress_score,
            monocle_state=monocle_state,
            reasoning=reasoning,
            estimated_impact=estimated_impact,
            urgency=urgency,
            analysis_depth=AnalysisDepth.STANDARD,
            monocle_yeet_count=monocle_yeet_count,
            data_quality_score=data_quality_score,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _thorough_analysis(
            self, 
            cpu: float, 
            memory: float, 
            disk: float,
            network_data: Optional[Dict],
            process_count: Optional[int],
            load_avg: Optional[List[float]],
            historical_data: Optional[List[Dict]],
            monocle_yeet_count: int,
            data_quality_score: float
        ) -> HawkingtonDecision:
        """Thorough aristocratic analysis with historical pattern recognition"""
        
        # Analyze patterns from historical data
        patterns = self._analyze_patterns(historical_data) if historical_data else {}
        
        stress_score = self._calculate_thorough_stress_score(cpu, memory, disk, network_data, process_count, load_avg, patterns)
        monocle_state = self._determine_monocle_state(stress_score)
        decision_type = self._determine_decision_type(stress_score)
        
        confidence = self._calculate_thorough_confidence(cpu, memory, disk, network_data, process_count, patterns)
        urgency = self._assess_urgency_thorough(cpu, memory, disk, network_data, load_avg, patterns)
        message = self._create_thorough_message(decision_type, stress_score, cpu, memory, disk, network_data, process_count, patterns)
        reasoning = self._create_thorough_reasoning(decision_type, stress_score, cpu, memory, disk, network_data, process_count, patterns)
        estimated_impact = self._estimate_thorough_impact(decision_type, cpu, memory, disk, network_data, process_count, patterns)
        
        return HawkingtonDecision(
            decision_type=decision_type,
            message=message,
            confidence=confidence,
            stress_score=stress_score,
            monocle_state=monocle_state,
            reasoning=reasoning,
            estimated_impact=estimated_impact,
            urgency=urgency,
            analysis_depth=AnalysisDepth.THOROUGH,
            monocle_yeet_count=monocle_yeet_count,
            data_quality_score=data_quality_score,
            timestamp=datetime.now(timezone.utc)
        )
    
    # === VALIDATION HELPERS ===
    
    def _validate_metric_range(self, value: float, metric_name: str) -> bool:
        """Validate metric with aristocratic standards"""
        if not isinstance(value, (int, float)):
            return False
        return 0 <= value <= 100
    
    def _validate_network_data(self, network_data: Any) -> Optional[Dict]:
        """Validate network data with gentleman's discretion"""
        if not isinstance(network_data, dict):
            return None
        
        bytes_sent = network_data.get('bytes_sent')
        bytes_recv = network_data.get('bytes_recv')
        
        if bytes_sent is not None and (not isinstance(bytes_sent, (int, float)) or bytes_sent < 0):
            return None
        if bytes_recv is not None and (not isinstance(bytes_recv, (int, float)) or bytes_recv < 0):
            return None
            
        return network_data
    
    def _validate_process_count(self, process_count: Any) -> Optional[int]:
        """Validate process count with aristocratic precision"""
        if not isinstance(process_count, int):
            return None
        if process_count < 0 or process_count > 10000:
            return None
        return process_count
    
    def _validate_load_average(self, load_avg: Any) -> Optional[List[float]]:
        """Validate load average with distinguished care"""
        if not isinstance(load_avg, (list, tuple)):
            return None
        if len(load_avg) < 3:
            return None
        
        try:
            return [float(x) for x in load_avg[:3]]
        except (ValueError, TypeError):
            return None
    
    def _calculate_data_quality_score(
        self, 
        cpu: float, 
        memory: float, 
        disk: float, 
        network_data: Optional[Dict], 
        process_count: Optional[int],
        load_avg: Optional[List[float]]
    ) -> float:
        """Calculate data quality score with aristocratic precision"""
        score = 0.6  # Base score for critical metrics
        
        if network_data is not None:
            score += 0.15
        if process_count is not None:
            score += 0.15
        if load_avg is not None:
            score += 0.10
        
        return min(score, 1.0)
    
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
            timestamp=datetime.now(timezone.utc),
            missing_metrics=missing_metrics,
            invalid_metrics=invalid_metrics,
            reason=reason,
            yeet_intensity=intensity,
            user_id=user_id
        )
        
        self.monocle_yeet_incidents.append(incident)
        self.metrics_quality_stats['monocle_yeets_total'] += 1
        self.current_monocle_state = MonocleState.YEETED
        
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
    
    # === STRESS CALCULATION METHODS ===
    
    def _calculate_basic_stress_score(self, cpu: float, memory: float, disk: float) -> float:
        """Basic stress calculation for quick analysis"""
        weights = {'cpu': 0.25, 'memory': 0.35, 'disk': 0.40}
        
        return (
            (cpu / 100.0) * weights['cpu'] +
            (memory / 100.0) * weights['memory'] +
            (disk / 100.0) * weights['disk']
        )
    
    def _calculate_standard_stress_score(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], load_avg: Optional[List[float]]
    ) -> float:
        """Standard stress calculation with additional metrics"""
        base_stress = self._calculate_basic_stress_score(cpu, memory, disk)
        
        # Add load average consideration
        if load_avg:
            normalized_load = min(load_avg[0] / 4.0, 1.0)  # Assume 4-core baseline
            base_stress += normalized_load * 0.10
        
        # Add process count consideration
        if process_count:
            normalized_processes = min(process_count / 200.0, 1.0)
            base_stress += normalized_processes * 0.05
        
        return min(base_stress, 1.0)
    
    def _calculate_thorough_stress_score(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], 
        load_avg: Optional[List[float]], patterns: Dict
    ) -> float:
        """Thorough stress calculation with pattern analysis"""
        base_stress = self._calculate_standard_stress_score(cpu, memory, disk, network_data, process_count, load_avg)
        
        # Pattern-based adjustments
        if patterns.get('stress_trending_up'):
            base_stress *= 1.1  # Increase stress for upward trends
        
        if patterns.get('critical_spikes'):
            base_stress *= 1.2  # Increase stress for spike patterns
        
        return min(base_stress, 1.0)
    
    # === DECISION DETERMINATION ===
    
    def _determine_monocle_state(self, stress_score: float) -> MonocleState:
        """Determine monocle state based on stress"""
        if stress_score >= self.critical_threshold:
            return MonocleState.YEETED
        elif stress_score >= self.alert_threshold:
            return MonocleState.FOGGED
        elif stress_score >= self.concern_threshold:
            return MonocleState.ADJUSTED
        else:
            return MonocleState.POLISHED
    
    def _determine_decision_type(self, stress_score: float) -> DecisionType:
        """Determine decision type based on stress"""
        if stress_score >= self.critical_threshold:
            return DecisionType.CRITICAL
        elif stress_score >= self.alert_threshold:
            return DecisionType.ALERT
        elif stress_score >= self.concern_threshold:
            return DecisionType.CONCERN
        else:
            return DecisionType.NORMAL
    
    # === CONFIDENCE CALCULATIONS ===
    
    def _calculate_basic_confidence(self, cpu: float, memory: float, disk: float) -> float:
        """Basic confidence calculation"""
        if cpu > 80 or memory > 80 or disk > 80:
            return 0.95  # High confidence for clear problems
        elif cpu > 60 or memory > 60 or disk > 60:
            return 0.85  # Medium confidence
        else:
            return 0.75  # Lower confidence for normal systems
    
    def _calculate_standard_confidence(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int]
    ) -> float:
        """Standard confidence with additional data"""
        base_confidence = self._calculate_basic_confidence(cpu, memory, disk)
        
        # More data = more confidence
        if network_data:
            base_confidence += 0.05
        if process_count:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _calculate_thorough_confidence(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], patterns: Dict
    ) -> float:
        """Thorough confidence with patterns"""
        base_confidence = self._calculate_standard_confidence(cpu, memory, disk, network_data, process_count)
        
        # Patterns increase confidence
        if patterns:
            base_confidence += 0.10
        
        # Historical success rate
        if len(self.recent_decisions) > 5:
            recent_success_rate = len(self.recent_decisions) / max(self.total_analyses, 1)
            base_confidence += (recent_success_rate * 0.05)
        
        return min(base_confidence, 1.0)
    
    # === URGENCY ASSESSMENT ===
    
    def _assess_urgency_basic(self, cpu: float, memory: float, disk: float) -> str:
        """Basic urgency assessment"""
        if cpu > 95 or memory > 95 or disk > 98:
            return "immediate"
        elif cpu > 80 or memory > 80 or disk > 85:
            return "soon"
        else:
            return "eventual"
    
    def _assess_urgency_standard(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], load_avg: Optional[List[float]]
    ) -> str:
        """Standard urgency with additional metrics"""
        base_urgency = self._assess_urgency_basic(cpu, memory, disk)
        
        # Load average can escalate urgency
        if load_avg and load_avg[0] > 8.0 and base_urgency == "eventual":
            return "soon"
        
        return base_urgency
    
    def _assess_urgency_thorough(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], load_avg: Optional[List[float]], patterns: Dict
    ) -> str:
        """Thorough urgency with patterns"""
        base_urgency = self._assess_urgency_standard(cpu, memory, disk, network_data, load_avg)
        
        # Patterns can escalate urgency
        if patterns.get('stress_trending_up') and base_urgency == "eventual":
            return "soon"
        
        if patterns.get('critical_spikes'):
            if base_urgency == "eventual":
                return "soon"
            elif base_urgency == "soon":
                return "immediate"
        
        return base_urgency
    
    # === MESSAGE CREATION ===
    
    def _create_basic_message(self, decision_type: DecisionType, stress_score: float, cpu: float, memory: float, disk: float) -> Optional[str]:
        """Create basic message"""
        if decision_type == DecisionType.CRITICAL:
            return f"🧐🚨 Sir Hawkington has YEETED his monocle in aristocratic horror! CRITICAL SYSTEM FAILURE IMMINENT (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%)"
        elif decision_type == DecisionType.ALERT:
            return f"🧐⚠️ Sir Hawkington's monocle has fogged with serious concern! System stress alert (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%)"
        elif decision_type == DecisionType.CONCERN:
            return f"🧐 Sir Hawkington adjusts his monocle with measured concern (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%)"
        else:
            # Silent during normal operations - a gentleman doesn't state the obvious
            import random
            if random.random() < 0.10:  # 10% chance
                return f"🧐 Sir Hawkington's monocle gleams with aristocratic satisfaction"
            return None
    
    def _create_standard_message(self, decision_type: DecisionType, stress_score: float, cpu: float, memory: float, disk: float, network_data: Optional[Dict], process_count: Optional[int]) -> Optional[str]:
        """Create standard message with additional context"""
        base_message = self._create_basic_message(decision_type, stress_score, cpu, memory, disk)
        
        if base_message and (network_data or process_count):
            context_parts = []
            if process_count and process_count > 300:
                context_parts.append(f"Processes: {process_count}")
            
            if context_parts:
                base_message += f" [{', '.join(context_parts)}]"
        
        return base_message
    
    def _create_thorough_message(self, decision_type: DecisionType, stress_score: float, cpu: float, memory: float, disk: float, network_data: Optional[Dict], process_count: Optional[int], patterns: Dict) -> Optional[str]:
        """Create thorough message with pattern insights"""
        base_message = self._create_standard_message(decision_type, stress_score, cpu, memory, disk, network_data, process_count)
        
        if base_message and patterns:
            pattern_insights = []
            if patterns.get('stress_trending_up'):
                pattern_insights.append("trending up")
            if patterns.get('critical_spikes'):
                pattern_insights.append("spike patterns detected")
            
            if pattern_insights:
                base_message += f" [Patterns: {', '.join(pattern_insights)}]"
        
        return base_message
    
    # === REASONING CREATION ===
    
    def _create_basic_reasoning(self, decision_type: DecisionType, stress_score: float, cpu: float, memory: float, disk: float) -> str:
        """Create basic reasoning"""
        return f"System stress score {stress_score:.3f} indicates {decision_type.value} conditions. Aristocratic analysis based on CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%"
    
    def _create_standard_reasoning(self, decision_type: DecisionType, stress_score: float, cpu: float, memory: float, disk: float, network_data: Optional[Dict], process_count: Optional[int]) -> str:
        """Create standard reasoning"""
        base_reasoning = self._create_basic_reasoning(decision_type, stress_score, cpu, memory, disk)
        
        additional_factors = []
        if network_data:
            additional_factors.append("network metrics")
        if process_count:
            additional_factors.append(f"process count ({process_count})")
        
        if additional_factors:
            base_reasoning += f" Additional factors: {', '.join(additional_factors)}"
        
        return base_reasoning
    
    def _create_thorough_reasoning(self, decision_type: DecisionType, stress_score: float, cpu: float, memory: float, disk: float, network_data: Optional[Dict], process_count: Optional[int], patterns: Dict) -> str:
        """Create thorough reasoning with patterns"""
        base_reasoning = self._create_standard_reasoning(decision_type, stress_score, cpu, memory, disk, network_data, process_count)
        
        if patterns:
            pattern_analysis = []
            if patterns.get('stress_trending_up'):
                pattern_analysis.append("stress trending upward")
            if patterns.get('critical_spikes'):
                pattern_analysis.append("critical spike patterns")
            
            if pattern_analysis:
                base_reasoning += f" Historical patterns: {', '.join(pattern_analysis)}"
        
        return base_reasoning
    
    # === IMPACT ESTIMATION ===
    
    async def _estimate_basic_impact(self, decision_type: DecisionType, cpu: float, memory: float, disk: float) -> Dict[str, float]:
        """Estimate basic impact"""
        impact = {
            'cpu_attention_needed': 0,
             'memory_attention_needed': 0,
            'disk_attention_needed': 0,
            'overall_system_health': 0
        }
        
        if decision_type == DecisionType.CRITICAL:
            impact['cpu_attention_needed'] = 95 if cpu > 95 else 0
            impact['memory_attention_needed'] = 95 if memory > 95 else 0
            impact['disk_attention_needed'] = 95 if disk > 95 else 0
            impact['overall_system_health'] = 95
        elif decision_type == DecisionType.ALERT:
            impact['cpu_attention_needed'] = 80 if cpu > 80 else 0
            impact['memory_attention_needed'] = 80 if memory > 80 else 0
            impact['disk_attention_needed'] = 80 if disk > 80 else 0
            impact['overall_system_health'] = 80
        elif decision_type == DecisionType.CONCERN:
            impact['cpu_attention_needed'] = 60 if cpu > 60 else 0
            impact['memory_attention_needed'] = 60 if memory > 60 else 0
            impact['disk_attention_needed'] = 60 if disk > 60 else 0
            impact['overall_system_health'] = 60
        else:
            impact['overall_system_health'] = 10  # Normal maintenance
        
        return impact
    
    async def _estimate_standard_impact(self, decision_type: DecisionType, cpu: float, memory: float, disk: float, network_data: Optional[Dict], process_count: Optional[int]) -> Dict[str, float]:
        """Estimate standard impact"""
        impact = self._estimate_basic_impact(decision_type, cpu, memory, disk)
        
        # Add network and process considerations
        if network_data:
            impact['network_optimization_needed'] = 30 if decision_type in [DecisionType.ALERT, DecisionType.CRITICAL] else 0
        
        if process_count and process_count > 300:
            impact['process_management_needed'] = 40 if decision_type in [DecisionType.ALERT, DecisionType.CRITICAL] else 20
        
        return impact
    
    async def _estimate_thorough_impact(self, decision_type: DecisionType, cpu: float, memory: float, disk: float, network_data: Optional[Dict], process_count: Optional[int], patterns: Dict) -> Dict[str, float]:
        """Estimate thorough impact with patterns"""
        impact = self._estimate_standard_impact(decision_type, cpu, memory, disk, network_data, process_count)
        
        # Pattern-based impact adjustments
        if patterns.get('stress_trending_up'):
            impact['predictive_intervention_needed'] = 50
        
        if patterns.get('critical_spikes'):
            impact['spike_prevention_needed'] = 60
        
        return impact
    
    async def _analyze_patterns(self, historical_data: List[Dict]) -> Dict:
        """Analyze historical patterns with aristocratic precision"""
        if not historical_data or len(historical_data) < 5:
            return {}
        
        patterns = {}
        
        # Extract valid data points
        valid_data = []
        for data_point in historical_data:
            # Handle different data structures from database
            if 'alert_parameters' in data_point and data_point['alert_parameters']:
                stress_score = data_point['alert_parameters'].get('stress_score', 0)
                if 0 <= stress_score <= 1:
                    valid_data.append({'stress_score': stress_score})
        
        if len(valid_data) < 5:
            return {}
        
        # Calculate stress trends
        recent_stress = [data['stress_score'] for data in valid_data[-10:]]
        
        # Trend analysis
        if len(recent_stress) > 1:
            stress_trend = recent_stress[-1] - recent_stress[0]
            patterns['stress_trending_up'] = stress_trend > 0.1
            patterns['stress_trending_down'] = stress_trend < -0.1
        
        # Spike detection
        patterns['critical_spikes'] = any(stress > 0.95 for stress in recent_stress)
        patterns['alert_spikes'] = any(stress > 0.85 for stress in recent_stress)
        
        return patterns
    
    # === UTILITY METHODS ===
    
    def get_monocle_yeet_stats(self) -> Dict[str, Any]:
        """Get monocle yeeting statistics for database storage"""
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
            decision_data = entry.get('decision', {})
            recent_decisions.append({
                'timestamp': entry.get('timestamp', '').isoformat() if hasattr(entry.get('timestamp', ''), 'isoformat') else str(entry.get('timestamp', '')),
                'decision_type': decision_data.get('decision_type', 'unknown'),
                'urgency': decision_data.get('urgency', 'unknown'),
                'confidence': decision_data.get('confidence', 0.0),
                'stress_score': decision_data.get('stress_score', 0.0),
                'monocle_state': decision_data.get('monocle_state', 'unknown'),
                'monocle_yeet_count': decision_data.get('monocle_yeet_count', 0),
                'data_quality_score': decision_data.get('data_quality_score', 0.0),
                'analysis_depth': decision_data.get('analysis_depth', 'unknown')
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
            'agent_name': 'sir_hawkington',
            'status': 'DISTINGUISHED_AND_OPERATIONAL',
            'brain_version': '2.0.0',
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
            'data_quality_enforcement': 'ABSOLUTE'
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

# === CONVENIENCE FUNCTIONS FOR DIFFERENT USE CASES ===

async def analyze_for_monitoring(
    metrics_data: Dict[str, Any], 
    historical_data: Optional[List[Dict]] = None,
    user_context: Optional[Dict] = None,
    user_id: Optional[str] = None
) -> Optional[HawkingtonDecision]:
    """Convenience function for background monitoring - thorough analysis"""
    return await sir_hawkington_brain.analyze_metrics(
        metrics_data, 
        historical_data=historical_data,
        user_context=user_context,
        analysis_depth=AnalysisDepth.THOROUGH,
        user_id=user_id
    )

async def analyze_standard(
    metrics_data: Dict[str, Any], 
    user_id: Optional[str] = None
) -> Optional[HawkingtonDecision]:
    """Convenience function for standard analysis"""
    return await sir_hawkington_brain.analyze_metrics(
        metrics_data, 
        analysis_depth=AnalysisDepth.STANDARD,
        user_id=user_id
    )

# === MONOCLE YEET TRACKING FOR DATABASE ===

def get_monocle_yeet_incidents_for_db() -> List[Dict[str, Any]]:
    """Get monocle yeet incidents in database-ready format"""
    return [
        {
            'timestamp': incident.timestamp,
            'missing_metrics': incident.missing_metrics,
            'invalid_metrics': incident.invalid_metrics,
            'reason': incident.reason,
            'yeet_intensity': incident.yeet_intensity,
            'user_id': incident.user_id,
            'agent_name': 'sir_hawkington'
        }
        for incident in sir_hawkington_brain.monocle_yeet_incidents
    ]

def get_monocle_yeet_stats() -> Dict[str, Any]:
    """Get monocle yeet statistics for database storage"""
    return sir_hawkington_brain.get_monocle_yeet_stats()

def get_data_quality_report() -> Dict[str, Any]:
    """Get comprehensive data quality report"""
    total_requests = sir_hawkington_brain.total_analyses
    if total_requests == 0:
        return {'status': 'NO_DATA', 'message': 'No analysis requests processed yet'}
    
    stats = sir_hawkington_brain.metrics_quality_stats
    
    return {
        'total_analysis_requests': total_requests,
        'successful_analyses': sir_hawkington_brain.successful_analyses,
        'failed_analyses': total_requests - sir_hawkington_brain.successful_analyses,
        'success_rate_percentage': (sir_hawkington_brain.successful_analyses / total_requests) * 100,
        'data_quality_issues': {
            'cpu_missing_rate': (stats['cpu_missing_count'] / total_requests) * 100,
            'memory_missing_rate': (stats['memory_missing_count'] / total_requests) * 100,
            'disk_missing_rate': (stats['disk_missing_count'] / total_requests) * 100,
            'network_missing_rate': (stats['network_missing_count'] / total_requests) * 100,
            'process_missing_rate': (stats['process_missing_count'] / total_requests) * 100,
            'invalid_data_rate': (stats['invalid_data_count'] / total_requests) * 100
        },
        'monocle_yeet_analysis': {
            'total_monocle_yeets': stats['monocle_yeets_total'],
            'monocle_yeet_rate': (stats['monocle_yeets_total'] / total_requests) * 100,
            'most_recent_incidents': [
                {
                    'timestamp': incident.timestamp.isoformat(),
                    'reason': incident.reason,
                    'yeet_intensity': incident.yeet_intensity,
                    'missing_metrics': incident.missing_metrics,
                    'invalid_metrics': incident.invalid_metrics
                }
                for incident in sir_hawkington_brain.monocle_yeet_incidents[-5:]
            ]
        },
        'data_integrity_status': 'ENFORCED' if stats['monocle_yeets_total'] > 0 else 'PERFECT',
        'aristocratic_recommendation': _generate_aristocratic_recommendation()
    }

def _generate_aristocratic_recommendation() -> str:
    """Generate aristocratic recommendation based on data quality"""
    stats = sir_hawkington_brain.metrics_quality_stats
    total = sir_hawkington_brain.total_analyses
    
    if total == 0:
        return "🧐 Awaiting data for proper aristocratic assessment"
    
    # Check for high missing data rates
    cpu_missing_rate = (stats['cpu_missing_count'] / total) * 100
    memory_missing_rate = (stats['memory_missing_count'] / total) * 100
    disk_missing_rate = (stats['disk_missing_count'] / total) * 100
    
    if cpu_missing_rate > 20 or memory_missing_rate > 20 or disk_missing_rate > 20:
        return "🧐💥 UNACCEPTABLE DATA QUALITY: Immediate review of metrics collection system required"
    
    if stats['invalid_data_count'] > (total * 0.1):
        return "🧐⚠️ INVALID DATA DETECTED: Metrics source validation urgently needed"
    
    if stats['monocle_yeets_total'] == 0:
        return "🧐✨ EXEMPLARY DATA QUALITY: Aristocratic standards fully maintained"
    
    if stats['monocle_yeets_total'] < (total * 0.05):
        return "🧐😌 ACCEPTABLE DATA QUALITY: Minor refinements would be appreciated"
    
    return "🧐🔍 MODERATE DATA QUALITY: Systematic improvement recommended for aristocratic standards"

# === BRAIN HEALTH CHECK ===

def health_check() -> Dict[str, Any]:
    """Check the health of Sir Hawkington's aristocratic brain"""
    return sir_hawkington_brain.health_check()

# === RESET FUNCTION FOR TESTING ===

def reset_brain_for_testing():
    """Reset the brain state for testing purposes"""
    sir_hawkington_brain.reset_stats()
    return