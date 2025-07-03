# app/ai_agents/meth_snail/decision_engine.py
"""
The Meth Snail's Optimization Brain - NO FAKE DATA EDITION
Always seeking the perfect balance between speed and efficiency
ONLY optimizes what the system actually provides
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
import json

logger = logging.getLogger("MethSnail")

class OptimizationPriority(Enum):
    """The Meth Snail's optimization focus modes"""
    SPEED = "speed"  # GOTTA GO FAST
    EFFICIENCY = "efficiency"  # Resource conservation
    BALANCED = "balanced"  # The sweet spot
    AGGRESSIVE = "aggressive"  # MAXIMUM OVERDRIVE
    HIBERNATION = "hibernation"  # Low activity mode

@dataclass
class OptimizationDecision:
    """The Meth Snail's optimization verdict"""
    priority: OptimizationPriority
    actions: List[Dict[str, Any]]
    confidence: float  # 0.0 to 1.0
    rationale: str
    estimated_impact: Dict[str, float]  # Expected improvements
    urgency: str  # immediate, soon, eventual
    
class MethSnailBrain:
    """
    The Meth Snail's hyperactive optimization consciousness.
    Constantly analyzing, always optimizing, never satisfied.
    NOW WITH 100% REAL DATA INTEGRITY!
    """
    
    def __init__(self):
        self.optimization_history = []  # Remember past optimizations
        self.system_baseline = {}  # Normal system behavior
        self.optimization_cooldowns = {}  # Prevent optimization loops
        self.current_priority = OptimizationPriority.BALANCED
        
    async def analyze_for_optimization(
        self, 
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None,
        user_context: Optional[Dict] = None
    ) -> Optional[OptimizationDecision]:  # Can return None now!
        """
        The Meth Snail's primary analysis function.
        Examines metrics to identify optimization opportunities.
        ONLY WORKS WITH REAL DATA - NO FAKE BULLSHIT!
        """
        try:
            # Extract key metrics - NO DEFAULTS!
            cpu_usage = metrics.get('cpu_usage')
            memory_usage = metrics.get('memory_usage')
            disk_usage = metrics.get('disk_usage')
            network_data = metrics.get('network')
            process_count = metrics.get('process_count')
            
            # VALIDATE CRITICAL METRICS EXIST
            missing_metrics = []
            if cpu_usage is None:
                missing_metrics.append('cpu_usage')
            if memory_usage is None:
                missing_metrics.append('memory_usage')
            if disk_usage is None:
                missing_metrics.append('disk_usage')
                
            if missing_metrics:
                logger.warning(f"🐌🔄 Meth Snail spinning shell - missing metrics: {missing_metrics}")
                return None
                
            # VALIDATE DATA RANGES
            if not (0 <= cpu_usage <= 100):
                logger.error(f"🐌❌ Invalid CPU usage: {cpu_usage}% - Meth Snail refuses fake data!")
                return None
                
            if not (0 <= memory_usage <= 100):
                logger.error(f"🐌❌ Invalid memory usage: {memory_usage}% - Meth Snail refuses fake data!")
                return None
                
            if not (0 <= disk_usage <= 100):
                logger.error(f"🐌❌ Invalid disk usage: {disk_usage}% - Meth Snail refuses fake data!")
                return None
                
            # VALIDATE OPTIONAL METRICS
            validated_network = None
            if network_data and isinstance(network_data, dict):
                validated_network = network_data
            
            validated_process_count = None
            if process_count is not None and isinstance(process_count, int) and process_count >= 0:
                validated_process_count = process_count
            
            # Analyze patterns if historical data provided
            patterns = self._analyze_patterns(historical_data) if historical_data else {}
            
            # Determine optimization priority based on REAL state
            priority = self._determine_priority(
                cpu_usage, memory_usage, disk_usage, patterns
            )
            
            # Generate optimization actions
            actions = await self._generate_optimization_actions(
                cpu_usage, memory_usage, disk_usage, validated_network, validated_process_count, patterns, priority
            )
            
            # Calculate confidence and impact
            confidence = self._calculate_confidence(cpu_usage, memory_usage, disk_usage, patterns)
            estimated_impact = self._estimate_impact(actions, cpu_usage, memory_usage, disk_usage)
            
            # Determine urgency
            urgency = self._assess_urgency(cpu_usage, memory_usage, disk_usage, patterns)
            
            # Create rationale
            rationale = self._create_rationale(
                priority, actions, cpu_usage, memory_usage, disk_usage, patterns
            )
            
            decision = OptimizationDecision(
                priority=priority,
                actions=actions,
                confidence=confidence,
                rationale=rationale,
                estimated_impact=estimated_impact,
                urgency=urgency
            )
            
            # Log the decision
            logger.info(f"🐌💨 Meth Snail optimization decision: {priority.value} - {rationale}")
            
            # Remember this decision
            self.optimization_history.append({
                'timestamp': datetime.utcnow(),
                'decision': decision,
                'metrics_snapshot': {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'disk_usage': disk_usage,
                    'network_available': validated_network is not None,
                    'process_count': validated_process_count
                }
            })
            
            # Trim history to last 100 decisions
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-100:]
            
            return decision
            
        except Exception as e:
            logger.error(f"🐌💥 Meth Snail brain error: {str(e)}")
            return None  # NO FAKE FALLBACK DECISIONS!
    
    def _determine_priority(
        self, 
        cpu: float, 
        memory: float, 
        disk: float,
        patterns: Dict
    ) -> OptimizationPriority:
        """Determine optimization priority based on REAL system state"""
        
        # Critical resource usage - AGGRESSIVE mode
        if cpu > 90 or memory > 90 or disk > 95:
            return OptimizationPriority.AGGRESSIVE
        
        # High usage but not critical - SPEED mode
        if cpu > 75 or memory > 75 or disk > 85:
            return OptimizationPriority.SPEED
        
        # Low usage - consider HIBERNATION
        if cpu < 20 and memory < 30 and disk < 40:
            return OptimizationPriority.HIBERNATION
        
        # Check patterns for optimization opportunities
        if patterns.get('usage_trending_up'):
            return OptimizationPriority.EFFICIENCY
        
        # Default to balanced
        return OptimizationPriority.BALANCED
    
    async def _generate_optimization_actions(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_data: Optional[Dict],
        process_count: Optional[int],
        patterns: Dict,
        priority: OptimizationPriority
    ) -> List[Dict[str, Any]]:
        """Generate specific optimization actions based on REAL data"""
        actions = []
        
        # CPU Optimizations
        if cpu_usage > 70:
            actions.append({
                'type': 'cpu_optimization',
                'action': 'reduce_process_priority',
                'target': 'high_cpu_processes',
                'details': {
                    'current_cpu': cpu_usage,
                    'target_cpu': 60,
                    'method': 'nice_adjustment'
                }
            })
            
            if priority == OptimizationPriority.AGGRESSIVE:
                actions.append({
                    'type': 'cpu_optimization',
                    'action': 'kill_unnecessary_processes',
                    'target': 'non_critical_services',
                    'details': {
                        'threshold': 5,  # % CPU usage
                        'whitelist': ['system', 'critical_services']
                    }
                })
        
        # Memory Optimizations
        if memory_usage > 70:
            actions.append({
                'type': 'memory_optimization',
                'action': 'clear_caches',
                'target': 'system_caches',
                'details': {
                    'current_memory': memory_usage,
                    'expected_recovery': 10  # %
                }
            })
            
            if memory_usage > 85:
                actions.append({
                    'type': 'memory_optimization',
                    'action': 'compress_memory',
                    'target': 'idle_processes',
                    'details': {
                        'compression_level': 'aggressive' if priority == OptimizationPriority.AGGRESSIVE else 'moderate'
                    }
                })
        
        # Disk Optimizations
        if disk_usage > 75:
            actions.append({
                'type': 'disk_optimization',
                'action': 'cleanup_temp_files',
                'target': 'temporary_directories',
                'details': {
                    'current_disk': disk_usage,
                    'expected_recovery': 5  # %
                }
            })
            
            if disk_usage > 90:
                actions.append({
                    'type': 'disk_optimization',
                    'action': 'compress_logs',
                    'target': 'log_files',
                    'details': {
                        'compression_ratio': 0.3,  # 70% reduction expected
                        'age_threshold': 7  # days
                    }
                })
        
        # Process Optimizations (only if we have real process count)
        if process_count is not None and process_count > 200:
            actions.append({
                'type': 'process_optimization',
                'action': 'consolidate_processes',
                'target': 'duplicate_services',
                'details': {
                    'current_count': process_count,
                    'target_reduction': 20  # %
                }
            })
        
        # Network Optimizations (only if we have real network data)
        if network_data:
            network_bytes = network_data.get('bytes_sent', 0)
            if network_bytes > 1000000:  # 1MB/s
                actions.append({
                    'type': 'network_optimization',
                    'action': 'throttle_bandwidth',
                    'target': 'non_priority_connections',
                    'details': {
                        'current_bandwidth': network_bytes,
                        'throttle_to': 500000  # 500KB/s
                    }
                })
        
        # Hibernation Mode Optimizations
        if priority == OptimizationPriority.HIBERNATION:
            actions.append({
                'type': 'power_optimization',
                'action': 'enable_power_saving',
                'target': 'system_wide',
                'details': {
                    'disable_turbo': True,
                    'reduce_polling': True,
                    'hibernate_idle_services': True
                }
            })
        
        return actions
    
    def _analyze_patterns(self, historical_data: List[Dict]) -> Dict:
        """Analyze historical data for patterns - ONLY REAL DATA"""
        if not historical_data or len(historical_data) < 5:
            return {}
        
        patterns = {}
        
        # Extract only valid data points
        valid_data = []
        for data_point in historical_data:
            cpu = data_point.get('cpu_usage')
            memory = data_point.get('memory_usage')
            if cpu is not None and memory is not None and 0 <= cpu <= 100 and 0 <= memory <= 100:
                valid_data.append(data_point)
        
        if len(valid_data) < 5:
            logger.warning("🐌⚠️ Insufficient valid historical data for pattern analysis")
            return {}
        
        # Calculate trends using only valid data
        recent_cpu = [d['cpu_usage'] for d in valid_data[-10:]]
        recent_memory = [d['memory_usage'] for d in valid_data[-10:]]
        
        # Trending analysis
        if len(recent_cpu) > 1:
            cpu_trend = recent_cpu[-1] - recent_cpu[0]
            patterns['cpu_trending_up'] = cpu_trend > 10
            patterns['cpu_trending_down'] = cpu_trend < -10
            
        if len(recent_memory) > 1:
            memory_trend = recent_memory[-1] - recent_memory[0]
            patterns['memory_trending_up'] = memory_trend > 10
            patterns['memory_trending_down'] = memory_trend < -10
        
        patterns['usage_trending_up'] = patterns.get('cpu_trending_up', False) or patterns.get('memory_trending_up', False)
        
        # Spike detection
        patterns['cpu_spikes'] = any(cpu > 90 for cpu in recent_cpu)
        patterns['memory_spikes'] = any(mem > 90 for mem in recent_memory)
        
        return patterns
    
    def _calculate_confidence(self, cpu: float, memory: float, disk: float, patterns: Dict) -> float:
        """Calculate confidence in optimization decision based on REAL data"""
        confidence = 0.5  # Base confidence
        
        # More data = more confidence
        if patterns:
            confidence += 0.2
        
        # Clear problem = more confidence
        if cpu > 80 or memory > 80 or disk > 80:
            confidence += 0.2
        
        # Recent successful optimizations = more confidence
        recent_successes = sum(
            1 for h in self.optimization_history[-5:]
            if h.get('success', False)
        )
        confidence += (recent_successes * 0.02)
        
        return min(confidence, 1.0)
    
    def _estimate_impact(self, actions: List[Dict], cpu: float, memory: float, disk: float) -> Dict[str, float]:
        """Estimate the impact of optimization actions based on REAL metrics"""
        impact = {
            'cpu_reduction': 0,
            'memory_reduction': 0,
            'disk_reduction': 0,
            'performance_gain': 0
        }
        
        for action in actions:
            if action['type'] == 'cpu_optimization':
                impact['cpu_reduction'] += 10  # Conservative estimate
            elif action['type'] == 'memory_optimization':
                impact['memory_reduction'] += action['details'].get('expected_recovery', 5)
            elif action['type'] == 'disk_optimization':
                impact['disk_reduction'] += action['details'].get('expected_recovery', 5)
            elif action['type'] == 'process_optimization':
                impact['cpu_reduction'] += 5
                impact['memory_reduction'] += 5
        
        # Performance gain is inverse of resource usage
        current_load = (cpu + memory + disk) / 3
        impact['performance_gain'] = max(0, (100 - current_load) * 0.1)
        
        return impact
    
    def _assess_urgency(self, cpu: float, memory: float, disk: float, patterns: Dict) -> str:
        """Determine how urgently optimization is needed based on REAL data"""
        
        # Critical levels = immediate
        if cpu > 95 or memory > 95 or disk > 98:
            return "immediate"
        
        # High usage or trending up = soon
        if cpu > 80 or memory > 80 or disk > 85 or patterns.get('usage_trending_up', False):
            return "soon"
        
        # Everything else = eventual
        return "eventual"
    
    def _create_rationale(
        self,
        priority: OptimizationPriority,
        actions: List[Dict],
        cpu: float,
        memory: float,
        disk: float,
        patterns: Dict
    ) -> str:
        """Create human-readable rationale for optimization decision using REAL data"""
        
        if priority == OptimizationPriority.AGGRESSIVE:
             return f"🐌💨 MAXIMUM OVERDRIVE! CPU at {cpu:.1f}%, Memory at {memory:.1f}%, Disk at {disk:.1f}%. Time for aggressive optimization!"
        
        elif priority == OptimizationPriority.SPEED:
            return f"🐌💨 System running hot (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%). Engaging speed optimizations."
        
        elif priority == OptimizationPriority.HIBERNATION:
            return f"🐌💤 System idle (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%). Switching to power-saving mode."
        
        elif priority == OptimizationPriority.EFFICIENCY:
            trend_info = "trending up" if patterns.get('usage_trending_up') else "stable"
            return f"🐌⚡ Resource usage {trend_info} (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%). Optimizing for efficiency."
        
        else:  # BALANCED
            return f"🐌😎 System balanced (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%). Maintaining optimal performance."
    
    def format_for_websocket(self, decision: OptimizationDecision) -> Dict[str, Any]:
        """Format optimization decision for WebSocket transmission"""
        return {
            'agent_name': 'meth_snail',
            'decision_type': decision.priority.value,
            'urgency': decision.urgency,
            'confidence': round(decision.confidence, 2),
            'rationale': decision.rationale,
            'actions_count': len(decision.actions),
            'estimated_impact': {
                k: round(v, 1) for k, v in decision.estimated_impact.items()
            },
            'data_quality': 'VALIDATED_REAL_DATA',  # New field!
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of Meth Snail's optimization activities - REAL DATA ONLY"""
        if not self.optimization_history:
            return {
                'total_optimizations': 0,
                'recent_decisions': [],
                'data_quality_status': 'NO_DATA_PROCESSED_YET'
            }
        
        recent_decisions = []
        valid_decisions = 0
        
        for entry in self.optimization_history[-10:]:  # Last 10 decisions
            decision = entry.get('decision')
            if decision:
                recent_decisions.append({
                    'timestamp': entry['timestamp'].isoformat(),
                    'priority': decision.priority.value,
                    'urgency': decision.urgency,
                    'confidence': round(decision.confidence, 2),
                    'actions_count': len(decision.actions)
                })
                valid_decisions += 1
        
        return {
            'total_optimizations': len(self.optimization_history),
            'valid_optimizations': valid_decisions,
            'recent_decisions': recent_decisions,
            'current_priority': self.current_priority.value,
            'data_quality_status': 'REAL_DATA_ONLY',
            'shell_spinning_incidents': len(self.optimization_history) - valid_decisions  # Times we had to wait for real data
        }

    def health_check(self) -> Dict[str, Any]:
        """Meth Snail's health status - NO FAKE DATA TOLERANCE"""
        return {
            'agent_name': 'meth_snail',
            'status': 'CAFFEINATED_AND_OPTIMIZING',
            'data_integrity_policy': 'ZERO_TOLERANCE_FOR_FAKE_DATA',
            'optimization_history_count': len(self.optimization_history),
            'current_priority': self.current_priority.value,
            'shell_spinning_mode': 'ENABLED',  # Ready to wait for real data
            'caffeine_level': 'MAXIMUM',
            'last_optimization': self.optimization_history[-1]['timestamp'].isoformat() if self.optimization_history else None
        }