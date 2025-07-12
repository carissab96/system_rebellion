from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import json
from datetime import datetime, timedelta
import statistics
from .data_types import StickDecision, ComplianceState, StickDecisionType

class ComplianceState(Enum):
    COMPLIANT = "compliant"
    MINOR_VIOLATION = "minor_violation"
    MAJOR_VIOLATION = "major_violation"
    CRITICAL_VIOLATION = "critical_violation"
    OPTIMIZING = "optimizing"
    LEARNING = "learning"

class StickDecisionType(Enum):
    USER_PATTERN_OPTIMIZATION = "user_pattern_optimization"
    CONFIGURATION_PROFILE_SWITCH = "configuration_profile_switch"
    COMPLIANCE_ENFORCEMENT = "compliance_enforcement"
    PREDICTIVE_CONFIGURATION = "predictive_configuration"
    BEHAVIOR_ANOMALY_DETECTION = "behavior_anomaly_detection"
    SYSTEM_PREPARATION = "system_preparation"

@dataclass
class StickDecision:
    decision_type: StickDecisionType
    compliance_state: ComplianceState
    configuration_target: str
    optimization_parameters: Dict[str, Any]
    user_pattern_confidence: float
    compliance_explanation: str
    technical_details: Dict[str, Any]
    expected_improvement: float
    confidence_level: float
    timestamp: datetime

class TheStickBrainV2:
    """
    The Stick: Compliance and Configuration Master
    Analyzes user behavior patterns and ensures optimal system configurations
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._db = None
        self.compliance_state = ComplianceState.LEARNING
        self.user_patterns = {}
        self.configuration_profiles = {}
        self.compliance_violations = 0
        self.optimizations_applied = 0
        self.pattern_learning_sessions = 0
        
        # User behavior intelligence patterns
        self.activity_patterns = {
            'gaming': {
                'cpu_governor': 'performance',
                'gpu_power_limit': 100,
                'network_priority': 'gaming',
                'audio_profile': 'surround',
                'rgb_lighting': 'gaming_mode'
            },
            'coding': {
                'cpu_governor': 'powersave',
                'display_brightness': 80,
                'blue_light_filter': True,
                'notification_mode': 'focused',
                'audio_profile': 'minimal'
            },
            'streaming': {
                'cpu_governor': 'performance',
                'network_priority': 'streaming',
                'audio_profile': 'broadcast',
                'camera_settings': 'optimized',
                'background_apps': 'minimal'
            },
            'design': {
                'display_profile': 'color_accurate',
                'gpu_power_limit': 100,
                'memory_priority': 'creative_apps',
                'storage_optimization': 'large_files'
            }
        }
        
        # Compliance thresholds
        self.compliance_thresholds = {
            'cpu_usage': {'max': 85, 'sustained_max': 75},
            'memory_usage': {'max': 90, 'sustained_max': 80},
            'temperature': {'max': 80, 'critical': 85},
            'power_consumption': {'max': 95, 'efficiency_target': 70}
        }
        
        self.time_based_patterns = {}
        self.application_usage_patterns = {}

    async def initialize_database(self):
        """Initialize database connection"""
        if self._db is None:
            from .database_integration import StickDatabaseIntegration
            self._db = StickDatabaseIntegration(self.database_url)
            await self._db.initialize()
    
    async def analyze_user_behavior(
        self, 
        system_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None,
        user_id: Optional[str] = None
    ) -> Optional[StickDecision]:
        """
        Analyze user behavior patterns and system compliance
        Predict user needs and optimize configurations
        """
        
        # Enter learning mode
        await self._enter_learning_mode()
        
        try:
            # Analyze current system state
            behavior_analysis = await self._analyze_current_behavior(system_metrics)
            
            # Learn from historical patterns
            if historical_data:
                pattern_analysis = await self._analyze_historical_patterns(historical_data, user_id)
                behavior_analysis.update(pattern_analysis)
            
            # Determine if configuration optimization is needed
            decision = await self._determine_configuration_optimization(behavior_analysis, user_id)
            
            if decision:
                # Apply configuration optimization
                await self._apply_configuration_optimization(decision)
                
            return decision
            
        except Exception as e:
            # Even The Stick needs debugging
            await self._exit_learning_mode()
            raise Exception(f"User behavior analysis failed: {str(e)}")
        
        finally:
            await self._exit_learning_mode()
    
    async def _enter_learning_mode(self):
        """Enter user pattern learning mode"""
        self.compliance_state = ComplianceState.LEARNING
        self.pattern_learning_sessions += 1
        await asyncio.sleep(0.001)  # Brief learning initialization
        
    async def _exit_learning_mode(self):
        """Exit learning mode and return to compliance monitoring"""
        self.compliance_state = ComplianceState.COMPLIANT
        await asyncio.sleep(0.001)
    
    async def _analyze_current_behavior(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current user behavior and system state"""
        
        analysis = {
            'current_activity': 'unknown',
            'compliance_violations': [],
            'performance_patterns': {},
            'configuration_recommendations': [],
            'user_context': {}
        }
        
        # Detect current user activity based on system metrics
        current_activity = await self._detect_current_activity(system_metrics)
        analysis['current_activity'] = current_activity
        
        # Check compliance violations
        compliance_check = await self._check_compliance_violations(system_metrics)
        analysis['compliance_violations'] = compliance_check
        
        # Analyze performance patterns
        performance_analysis = await self._analyze_performance_patterns(system_metrics)
        analysis['performance_patterns'] = performance_analysis
        
        # Determine user context (time of day, day of week, etc.)
        user_context = await self._determine_user_context()
        analysis['user_context'] = user_context
        
        return analysis
    
    async def _detect_current_activity(self, system_metrics: Dict[str, Any]) -> str:
        """Detect current user activity based on system metrics"""
        
        cpu_usage = system_metrics.get('cpu_usage', 0)
        memory_usage = system_metrics.get('memory_usage', 0)
        network_activity = system_metrics.get('network', {}).get('sent_rate', 0)
        
        # Gaming detection
        if cpu_usage > 60 and memory_usage > 50:
            return 'gaming'
        
        # Streaming detection
        if network_activity > 1000000:  # 1MB/s upload
            return 'streaming'
        
        # Design work detection
        if memory_usage > 70 and cpu_usage > 40:
            return 'design'
        
        # Coding detection (moderate CPU, low network)
        if 20 < cpu_usage < 50 and network_activity < 100000:
            return 'coding'
        
        # Idle detection
        if cpu_usage < 10 and memory_usage < 30:
            return 'idle'
        
        return 'general'
    
    async def _check_compliance_violations(self, system_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for system compliance violations"""
        
        violations = []
        
        # Check CPU usage compliance
        cpu_usage = system_metrics.get('cpu_usage', 0)
        if cpu_usage > self.compliance_thresholds['cpu_usage']['max']:
            violations.append({
                'type': 'cpu_overload',
                'current': cpu_usage,
                'threshold': self.compliance_thresholds['cpu_usage']['max'],
                'severity': 'critical' if cpu_usage > 95 else 'high',
                'recommendation': 'reduce_background_processes'
            })
        
        # Check memory usage compliance
        memory_usage = system_metrics.get('memory_usage', 0)
        if memory_usage > self.compliance_thresholds['memory_usage']['max']:
            violations.append({
                'type': 'memory_overload',
                'current': memory_usage,
                'threshold': self.compliance_thresholds['memory_usage']['max'],
                'severity': 'critical' if memory_usage > 95 else 'high',
                'recommendation': 'optimize_memory_usage'
            })
        
        # Check temperature compliance (if available)
        if 'temperature' in system_metrics:
            temp = system_metrics['temperature']
            if temp > self.compliance_thresholds['temperature']['max']:
                violations.append({
                    'type': 'thermal_violation',
                    'current': temp,
                    'threshold': self.compliance_thresholds['temperature']['max'],
                    'severity': 'critical' if temp > self.compliance_thresholds['temperature']['critical'] else 'high',
                    'recommendation': 'thermal_management'
                })
        
        return violations
    
    async def _analyze_performance_patterns(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system performance patterns"""
        
        patterns = {
            'cpu_efficiency': 0.0,
            'memory_efficiency': 0.0,
            'power_efficiency': 0.0,
            'optimization_opportunities': []
        }
        
        cpu_usage = system_metrics.get('cpu_usage', 0)
        memory_usage = system_metrics.get('memory_usage', 0)
        
        # Calculate efficiency scores
        patterns['cpu_efficiency'] = max(0, 100 - cpu_usage) / 100
        patterns['memory_efficiency'] = max(0, 100 - memory_usage) / 100
        
        # Identify optimization opportunities
        if cpu_usage > 80:
            patterns['optimization_opportunities'].append({
                'type': 'cpu_optimization',
                'potential_improvement': 0.2,
                'method': 'process_prioritization'
            })
        
        if memory_usage > 75:
            patterns['optimization_opportunities'].append({
                'type': 'memory_optimization',
                'potential_improvement': 0.15,
                'method': 'memory_cleanup'
            })
        
        return patterns
    
    async def _determine_user_context(self) -> Dict[str, Any]:
        """Determine current user context"""
        
        now = datetime.now()
        
        context = {
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'is_weekend': now.weekday() >= 5,
            'time_period': 'morning' if 6 <= now.hour < 12 else 
                          'afternoon' if 12 <= now.hour < 18 else 
                          'evening' if 18 <= now.hour < 22 else 'night',
            'work_hours': 9 <= now.hour < 17 and now.weekday() < 5
        }
        
        return context
    
    async def _analyze_historical_patterns(self, historical_data: List[Dict], user_id: str) -> Dict[str, Any]:
        """Learn from historical user behavior patterns"""
        
        if not historical_data:
            return {}
        
        pattern_analysis = {
            'recurring_activities': [],
            'time_based_patterns': {},
            'performance_trends': {},
            'learned_optimizations': {}
        }
        
        # Analyze activity patterns by time
        time_activities = {}
        for data in historical_data:
            hour = datetime.fromisoformat(data['timestamp']).hour
            activity = data.get('detected_activity', 'unknown')
            
            if hour not in time_activities:
                time_activities[hour] = []
            time_activities[hour].append(activity)
        
        # Find recurring patterns
        for hour, activities in time_activities.items():
            if len(activities) > 1:
                most_common = max(set(activities), key=activities.count)
                confidence = activities.count(most_common) / len(activities)
                
                if confidence > 0.6:  # 60% confidence threshold
                    pattern_analysis['time_based_patterns'][hour] = {
                        'activity': most_common,
                        'confidence': confidence,
                        'occurrences': activities.count(most_common)
                    }
        
        # Analyze performance trends
        cpu_values = [d.get('cpu_usage', 0) for d in historical_data]
        memory_values = [d.get('memory_usage', 0) for d in historical_data]
        
        if cpu_values:
            pattern_analysis['performance_trends']['cpu'] = {
                'average': statistics.mean(cpu_values),
                'trend': self._calculate_trend(cpu_values),
                'peak_usage': max(cpu_values)
            }
        
        if memory_values:
            pattern_analysis['performance_trends']['memory'] = {
                'average': statistics.mean(memory_values),
                'trend': self._calculate_trend(memory_values),
                'peak_usage': max(memory_values)
            }
        
        # Store patterns for future use
        if user_id:
            self.user_patterns[user_id] = pattern_analysis
        
        return pattern_analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'insufficient_data'
        
        recent_avg = statistics.mean(values[-5:])
        historical_avg = statistics.mean(values[:-5])
        
        if recent_avg > historical_avg * 1.1:
            return 'increasing'
        elif recent_avg < historical_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    async def _determine_configuration_optimization(self, analysis: Dict[str, Any], user_id: str) -> Optional[StickDecision]:
        """Only optimize based on ACTUAL learned patterns - no assumptions"""
        
        # Check compliance violations (measurable, real data)
        if analysis.get('compliance_violations'):
            for violation in analysis['compliance_violations']:
                if violation['severity'] == 'critical':
                    return await self._create_compliance_enforcement(violation, user_id)
        
        # Check if we have ACTUAL learned patterns for this user
        if user_id in self.user_patterns:
            user_pattern = self.user_patterns[user_id]
            
            # The Stick's OCD kicks in - only act on HIGH confidence patterns
            if user_pattern.get('confidence', 0) > 0.85:  # 85% confidence from REAL data
                return await self._create_pattern_based_optimization(user_pattern, user_id)
        
        # No sufficient patterns? The Stick waits, learns, remembers EVERYTHING
        return None
    
    async def _create_compliance_enforcement(self, violation: Dict[str, Any], user_id: str) -> StickDecision:
        """Create compliance enforcement based on MEASURED violations"""
        
        self.compliance_violations += 1
        
        return StickDecision(
            decision_type=StickDecisionType.COMPLIANCE_ENFORCEMENT,
            compliance_state=ComplianceState.MAJOR_VIOLATION,
            configuration_target=violation['type'],
            optimization_parameters={
                'violation_type': violation['type'],
                'measured_value': violation['current'],
                'threshold_exceeded': violation['threshold'],
                'enforcement_action': violation['recommendation'],
                'urgency_level': violation['severity']
            },
            user_pattern_confidence=1.0,  # Compliance is measured, not predicted
            compliance_explanation=f"MEASURED violation: {violation['type']} at {violation['current']}% exceeds threshold of {violation['threshold']}%. The Stick's OCD cannot tolerate this deviation from acceptable parameters.",
            technical_details={
                'measured_value': violation['current'],
                'threshold': violation['threshold'],
                'severity': violation['severity'],
                'enforcement_method': violation['recommendation'],
                'stick_confidence': 1.0  # The Stick is certain about measured data
            },
            expected_improvement=0.3,  # Based on compliance restoration
            confidence_level=1.0,  # 100% confidence in measured violations
            timestamp=datetime.now()
        )
    
    async def _create_pattern_based_optimization(self, user_pattern: Dict[str, Any], user_id: str) -> StickDecision:
        """Create optimization based on LEARNED patterns - The Stick's eidetic memory"""
        
        self.optimizations_applied += 1
        
        # The Stick's eidetic memory recalls the exact pattern
        pattern_details = user_pattern.get('time_based_patterns', {})
        current_hour = datetime.now().hour
        
        if current_hour in pattern_details:
            learned_pattern = pattern_details[current_hour]
            
            return StickDecision(
                decision_type=StickDecisionType.PREDICTIVE_CONFIGURATION,
                compliance_state=ComplianceState.OPTIMIZING,
                configuration_target="user_environment",
                optimization_parameters={
                    'learned_activity': learned_pattern['activity'],
                    'pattern_confidence': learned_pattern['confidence'],
                    'historical_occurrences': learned_pattern['occurrences'],
                    'hour_of_day': current_hour,
                    'optimization_method': 'eidetic_memory_recall'
                },
                user_pattern_confidence=learned_pattern['confidence'],
                compliance_explanation=f"The Stick's eidetic memory recalls: At {current_hour}:00, you typically engage in '{learned_pattern['activity']}' with {learned_pattern['confidence']:.1%} consistency over {learned_pattern['occurrences']} observed sessions. Preparing optimal configuration based on ACTUAL usage patterns.",
                technical_details={
                    'activity': learned_pattern['activity'],
                    'confidence': learned_pattern['confidence'],
                    'sample_size': learned_pattern['occurrences'],
                    'time_pattern': f"hour_{current_hour}",
                    'memory_type': 'eidetic_recall'
                },
                expected_improvement=learned_pattern['confidence'] * 0.4,  # Improvement based on pattern strength
                confidence_level=learned_pattern['confidence'],
                timestamp=datetime.now()
            )
        
        return None
    
    async def _apply_configuration_optimization(self, decision: StickDecision):
        """Apply the configuration optimization - The Stick's precision execution"""
        
        self.optimizations_applied += 1
        
        # In real implementation, this would interface with system configuration
        # The Stick remembers EVERY configuration change made
        
        optimization_log = {
            'timestamp': decision.timestamp.isoformat(),
            'decision_type': decision.decision_type.value,
            'compliance_state': decision.compliance_state.value,
            'configuration_target': decision.configuration_target,
            'pattern_confidence': decision.user_pattern_confidence,
            'expected_improvement': decision.expected_improvement,
            'stick_memory_entry': decision.compliance_explanation,
            'technical_execution': decision.technical_details
        }
        
        # The Stick's OCD - must log everything for future recall
        return optimization_log
    
    def get_stick_stats(self) -> Dict[str, Any]:
        """Get The Stick's performance statistics - his obsessive tracking"""
        return {
            'compliance_state': self.compliance_state.value,
            'compliance_violations_detected': self.compliance_violations,
            'optimizations_applied': self.optimizations_applied,
            'pattern_learning_sessions': self.pattern_learning_sessions,
            'users_with_learned_patterns': len(self.user_patterns),
            'eidetic_memory_entries': sum(len(patterns.get('time_based_patterns', {})) for patterns in self.user_patterns.values()),
            'stick_personality': 'ocd_adhd_ptsd_eidetic_memory',
            'learning_approach': 'pure_observation_no_assumptions',
            'status': 'observing_and_remembering_everything'
        }
    
    async def get_user_memory_recall(self, user_id: str, specific_time: Optional[datetime] = None) -> Dict[str, Any]:
        """The Stick's eidetic memory - recall ANY user pattern"""
        
        if user_id not in self.user_patterns:
            return {
                'memory_status': 'insufficient_data',
                'message': 'The Stick is still learning your patterns. More observation time required.'
            }
        
        user_pattern = self.user_patterns[user_id]
        
        if specific_time:
            # The Stick remembers EXACTLY what happened at specific times
            hour = specific_time.hour
            if hour in user_pattern.get('time_based_patterns', {}):
                pattern = user_pattern['time_based_patterns'][hour]
                return {
                    'memory_status': 'eidetic_recall',
                    'timestamp': specific_time.isoformat(),
                    'recalled_activity': pattern['activity'],
                    'confidence': pattern['confidence'],
                    'occurrences': pattern['occurrences'],
                    'stick_memory': f"At {specific_time.strftime('%I:%M %p on %A, %B %d, %Y')}, you were {pattern['activity']} with {pattern['confidence']:.1%} consistency based on {pattern['occurrences']} observed sessions."
                }
        
        # Return full pattern memory
        return {
            'memory_status': 'complete_pattern_recall',
            'total_patterns': len(user_pattern.get('time_based_patterns', {})),
            'pattern_details': user_pattern,
            'stick_memory': f"The Stick remembers {len(user_pattern.get('time_based_patterns', {}))} distinct time-based patterns for your usage."
        }