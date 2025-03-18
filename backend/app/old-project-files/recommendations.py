# core/recommendations.py
from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta
from .models import SystemMetrics, OptimizationProfile

class RecommendationsEngine:
    def __init__(self):
        self.threshold_configs = {
            'cpu': {
                'high': 80.0,
                'medium': 60.0,
                'low': 40.0
            },
            'memory': {
                'high': 85.0,
                'medium': 70.0,
                'low': 50.0
            },
            'disk': {
                'high': 90.0,
                'medium': 75.0,
                'low': 60.0
            }
        }

    def analyze_metrics(self, metrics: SystemMetrics) -> List[Dict]:
        """Analyze current metrics and generate recommendations"""
        recommendations = []

        # CPU Analysis
        if metrics.cpu_usage > self.threshold_configs['cpu']['high']:
            recommendations.append({
                'type': 'cpu',
                'severity': 'high',
                'title': 'High CPU Usage Detected',
                'description': 'System is experiencing heavy CPU load',
                'suggestion': 'Consider upgrading to full version for automatic process optimization',
                'potential_gain': f"Up to {self._calculate_potential_gain(metrics.cpu_usage, 'cpu')}% improvement"
            })

        # Memory Analysis
        if metrics.memory_usage > self.threshold_configs['memory']['medium']:
            recommendations.append({
                'type': 'memory',
                'severity': 'medium',
                'title': 'Memory Usage Optimization Available',
                'description': 'Memory usage could be optimized',
                'suggestion': 'Full version includes automatic memory management',
                'potential_gain': f"Up to {self._calculate_potential_gain(metrics.memory_usage, 'memory')}% improvement"
            })

        # Development Environment Detection
        if metrics.additional_metrics.get('active_python_processes', 0) > 5:
            recommendations.append({
                'type': 'development',
                'severity': 'info',
                'title': 'Development Environment Detected',
                'description': 'Multiple Python processes detected',
                'suggestion': 'Full version includes specialized development environment optimization',
                'potential_gain': 'Improved IDE performance and build times'
            })

        return recommendations

    def _calculate_potential_gain(self, current_usage: float, resource_type: str) -> int:
        """Calculate potential improvement percentage"""
        base_threshold = self.threshold_configs[resource_type]['low']
        if current_usage > self.threshold_configs[resource_type]['high']:
            return int((current_usage - base_threshold) * 0.4)
        return int((current_usage - base_threshold) * 0.25)

    def get_optimization_summary(self, metrics: SystemMetrics) -> Dict:
        """Generate overall optimization summary"""
        recommendations = self.analyze_metrics(metrics)
        
        # Calculate total potential gain
        total_potential_gain = 0
        for rec in recommendations:
            if 'potential_gain' in rec:
                gain_text = rec['potential_gain']
                if 'Up to' in gain_text:
                    # Handle "Up to X% improvement" format
                    gain = ''.join(filter(str.isdigit, gain_text.split('%')[0]))
                    if gain:
                        total_potential_gain += int(gain)
                # Skip non-numeric potential gains (like "Improved IDE performance")

        return {
            'total_recommendations': len(recommendations),
            'high_priority': sum(1 for r in recommendations if r['severity'] == 'high'),
            'potential_improvement': f"{total_potential_gain}%",
            'recommendations': recommendations
        }