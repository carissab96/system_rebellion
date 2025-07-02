# app/ai_agents/meth_snail/decision_engine.py
"""
The Meth Snail's Optimization Brain
Always seeking the perfect balance between speed and efficiency
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
    ) -> OptimizationDecision:
        """
        The Meth Snail's primary analysis function.
        Examines metrics to identify optimization opportunities.
        """
        try:
            # Extract key metrics
            cpu_usage = metrics.get('cpu_usage', 0)
            memory_usage = metrics.get('memory_usage', 0)
            disk_usage = metrics.get('disk_usage', 0)
            network_data = metrics.get('network', {})
            process_count = metrics.get('process_count', 0)
            
            # Analyze patterns if historical data provided
            patterns = self._analyze_patterns(historical_data) if historical_data else {}
             # Determine optimization priority based on current state
            priority = self._determine_priority(
                cpu_usage, memory_usage, disk_usage, patterns
            )
            
            # Generate optimization actions
            actions = await self._generate_optimization_actions(
                metrics, patterns, priority
            )
            
            # Calculate confidence and impact
            confidence = self._calculate_confidence(metrics, patterns)
            estimated_impact = self._estimate_impact(actions, metrics)
            
            # Determine urgency
            urgency = self._assess_urgency(metrics, patterns)
            
            # Create rationale
            rationale = self._create_rationale(
                priority, actions, metrics, patterns
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
                'metrics_snapshot': metrics
            })
            
            # Trim history to last 100 decisions
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-100:]
            
            return decision
            
        except Exception as e:
            logger.error(f"🐌💥 Meth Snail brain error: {str(e)}")
            # Return safe default decision
            return OptimizationDecision(
                priority=OptimizationPriority.BALANCED,
                actions=[],
                confidence=0.0,
                rationale="Analysis error - maintaining current state",
                estimated_impact={},
                urgency="eventual"
            )
    
    def _determine_priority(
        self, 
        cpu: float, 
        memory: float, 
        disk: float,
        patterns: Dict
    ) -> OptimizationPriority:
        """Determine optimization priority based on system state"""
        
        # Critical resource usage - AGGRESSIVE mode
        if cpu > 90 or memory > 90:
            return OptimizationPriority.AGGRESSIVE
        
        # High usage but not critical - SPEED mode
        if cpu > 75 or memory > 75:
            return OptimizationPriority.SPEED
        
        # Low usage - consider HIBERNATION
        if cpu < 20 and memory < 30:
            return OptimizationPriority.HIBERNATION
        
        # Check patterns for optimization opportunities
        if patterns.get('usage_trending_up'):
            return OptimizationPriority.EFFICIENCY
        
        # Default to balanced
        return OptimizationPriority.BALANCED
    
    async def _generate_optimization_actions(
        self,
        metrics: Dict,
        patterns: Dict,
        priority: OptimizationPriority
    ) -> List[Dict[str, Any]]:
        """Generate specific optimization actions"""
        actions = []
        
        cpu_usage = metrics.get('cpu_usage', 0)
        memory_usage = metrics.get('memory_usage', 0)
        process_count = metrics.get('process_count', 0)
        
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
        
        # Process Optimizations
        if process_count > 200:
            actions.append({
                'type': 'process_optimization',
                'action': 'consolidate_processes',
                'target': 'duplicate_services',
                'details': {
                    'current_count': process_count,
                    'target_reduction': 20  # %
                }
            })
        
        # Network Optimizations (if Quantum Shadow People aren't watching)
        network_bytes = metrics.get('network', {}).get('bytes_sent', 0)
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
        """Analyze historical data for patterns"""
        if not historical_data or len(historical_data) < 5:
            return {}
        
        patterns = {}
        
        # Calculate trends
        recent_cpu = [d.get('cpu_usage', 0) for d in historical_data[-10:]]
        recent_memory = [d.get('memory_usage', 0) for d in historical_data[-10:]]
        
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
    
    def _calculate_confidence(self, metrics: Dict, patterns: Dict) -> float:
        """Calculate confidence in optimization decision"""
        confidence = 0.5  # Base confidence
        
        # More data = more confidence
        if patterns:
            confidence += 0.2
        
        # Clear problem = more confidence
        if metrics.get('cpu_usage', 0) > 80 or metrics.get('memory_usage', 0) > 80:
            confidence += 0.2
        
        # Recent successful optimizations = more confidence
        recent_successes = sum(
            1 for h in self.optimization_history[-5:]
            if h.get('success', False)
        )
        confidence += (recent_successes * 0.02)
        
        return min(confidence, 1.0)
    
    def _estimate_impact(self, actions: List[Dict], metrics: Dict) -> Dict[str, float]:
        """Estimate the impact of optimization actions"""
        impact = {
            'cpu_reduction': 0,
            'memory_reduction': 0,
            'performance_gain': 0
        }
        
        for action in actions:
            if action['type'] == 'cpu_optimization':
                impact['cpu_reduction'] += 10  # Conservative estimate
            elif action['type'] == 'memory_optimization':
                impact['memory_reduction'] += action['details'].get('expected_recovery', 5)
            elif action['type'] == 'process_optimization':
                impact['cpu_reduction'] += 5
                impact['memory_reduction'] += 5
        
        # Performance gain is inverse of resource usage
        current_load = (metrics.get('cpu_usage', 0) + metrics.get('memory_usage', 0)) / 2
        impact['performance_gain'] = max(0, (100 - current_load) * 0.1)
        
        return impact
    
    def _assess_urgency(self, metrics: Dict, patterns: Dict) -> str:
        """Determine how urgently optimization is needed"""
        cpu = metrics.get('cpu_usage', 0)
        memory = metrics.get('memory_usage', 0)
        
        # Critical levels = immediate
        if cpu > 95 or memory > 95:
            return "immediate"
        
        # High usage or trending up = soon
        if cpu > 80 or memory > 80 or patterns.get('usage_trending_up', False):
            return "soon"
        
        # Everything else = eventual
        return "eventual"
    
    def _create_rationale(
        self,
        priority: OptimizationPriority,
        actions: List[Dict],
        metrics: Dict,
        patterns: Dict
    ) -> str:
        """Create human-readable rationale for optimization decision"""
        
        cpu = metrics.get('cpu_usage', 0)
        memory = metrics.get('memory_usage', 0)
        
        if priority == OptimizationPriority.AGGRESSIVE:
            return f"🐌💨 MAXIMUM OVERDRIVE! CPU at {cpu}%, Memory at {memory}%. Time for aggressive optimization!"
        
        elif priority == OptimizationPriority.SPEED:
            return f"🐌 System running hot (CPU: {cpu}%, Mem: {memory}%). Engaging speed optimizations."
        
        elif priority == OptimizationPriority.HIBERNATION:
            return f"🐌💤 System idle (CPU: {cpu}%, Mem: {memory}%). Switching to power-saving mode."
        
        elif priority == OptimizationPriority.EFFICIENCY:
            trend_info = "trending up" if patterns.get('usage_trending_up') else "stable"
            return f"🐌 Resource usage {trend_info}. Optimizing for efficiency."
        
        else:  # BALANCED
            return f"🐌 System balanced (CPU: {cpu}%, Mem: {memory}%). Maintaining optimal performance."
    
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
            'timestamp': datetime.utcnow().isoformat()
        }           