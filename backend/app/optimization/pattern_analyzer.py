# core/optimization/pattern_analyzer.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

class PatternAnalyzer:
    """
    Pattern Analyzer
    
    Scrutinizes system behavior patterns with the precision of 
    Sir Hawkington von Monitorious III himself.
    
    Warning: May cause unexpected insights and occasional 
    moments of "How did it know that?!"
    """

    def __init__(self):
        self.logger = logging.getLogger('PatternAnalyzer')
        self.pattern_history = defaultdict(list)
        self.pattern_threshold = 0.75
        self.analysis_window = timedelta(hours=1)

    async def analyze(self, metrics: Dict) -> List[Dict]:
        """Analyze current metrics for patterns"""
        try:
            patterns = []
            
            # Resource usage patterns
            resource_patterns = await self._analyze_resource_patterns(metrics)
            if resource_patterns:
                patterns.extend(resource_patterns)
            
            # Usage patterns (like development activities)
            usage_patterns = await self._analyze_usage_patterns(metrics)
            if usage_patterns:
                patterns.extend(usage_patterns)
            
            # Store patterns for historical analysis
            self._update_pattern_history(patterns)
            
            return patterns

        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {str(e)}")
            return []

    async def _analyze_resource_patterns(self, metrics: Dict) -> List[Dict]:
        """Analyze resource usage patterns"""
        patterns = []
        
        # CPU Pattern Analysis
        if metrics['cpu_usage'] > 80:
            patterns.append({
                'type': 'resource_usage',
                'resource': 'cpu',
                'pattern': 'high_sustained_usage',
                'confidence': 0.9,
                'details': {
                    'current_usage': metrics['cpu_usage'],
                    'threshold': 80,
                    'duration': 'sustained'
                }
            })
        
        # Memory Pattern Analysis
        if metrics['memory_usage'] > 85:
            patterns.append({
                'type': 'resource_usage',
                'resource': 'memory',
                'pattern': 'high_memory_pressure',
                'confidence': 0.85,
                'details': {
                    'current_usage': metrics['memory_usage'],
                    'threshold': 85
                }
            })
        
        return patterns

    async def _analyze_usage_patterns(self, metrics: Dict) -> List[Dict]:
        """Analyze system usage patterns"""
        patterns = []
        
        # Development Environment Detection
        if metrics.get('additional', {}).get('active_python_processes', 0) > 5:
            patterns.append({
                'type': 'usage_pattern',
                'pattern': 'development_environment',
                'confidence': 0.8,
                'details': {
                    'python_processes': metrics['additional']['active_python_processes'],
                    'suggestion': 'Optimize for development workload'
                }
            })

        # System Load Pattern
        load_avg = metrics.get('additional', {}).get('load_average', [0, 0, 0])
        if load_avg and load_avg[0] > 1.0:  # 1-minute load average
            patterns.append({
                'type': 'usage_pattern',
                'pattern': 'high_system_load',
                'confidence': 0.75,
                'details': {
                    'load_average': load_avg,
                    'suggestion': 'Consider load balancing'
                }
            })

        return patterns

    def _update_pattern_history(self, patterns: List[Dict]):
        """Update pattern history for trend analysis"""
        current_time = datetime.now()
        
        # Add new patterns
        for pattern in patterns:
            self.pattern_history[pattern['type']].append({
                'timestamp': current_time,
                'pattern': pattern
            })
        
        # Clean up old patterns
        cleanup_time = current_time - self.analysis_window
        for pattern_type in self.pattern_history:
            self.pattern_history[pattern_type] = [
                p for p in self.pattern_history[pattern_type]
                if p['timestamp'] > cleanup_time
            ]

    async def get_pattern_summary(self) -> Dict:
        """Get summary of recent patterns"""
        return {
            'total_patterns': sum(len(patterns) for patterns in self.pattern_history.values()),
            'pattern_types': {
                pattern_type: len(patterns)
                for pattern_type, patterns in self.pattern_history.items()
            },
            'latest_analysis': datetime.now()
        }

    async def get_recurring_patterns(self) -> List[Dict]:
        """Identify recurring patterns"""
        recurring = []
        for pattern_type, patterns in self.pattern_history.items():
            if len(patterns) >= 3:  # Minimum occurrences to consider recurring
                recurring.append({
                    'type': pattern_type,
                    'occurrences': len(patterns),
                    'first_seen': patterns[0]['timestamp'],
                    'last_seen': patterns[-1]['timestamp']
                })
        return recurring