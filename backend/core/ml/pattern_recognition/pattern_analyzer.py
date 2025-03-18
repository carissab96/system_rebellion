from typing import Dict, List, Optional
import numpy as np
from datetime import datetime

class PatternAnalyzer:
    def __init__(self):
        self.patterns = {}
        self.threshold = 0.75
        self.min_occurrences = 3

    async def analyze_metrics(self, metrics: Dict) -> Optional[Dict]:
        """Analyze system metrics for patterns"""
        timestamp = datetime.now()
        pattern_key = self._generate_pattern_key(metrics)
        
        if pattern_key in self.patterns:
            self.patterns[pattern_key]['occurrences'] += 1
            self.patterns[pattern_key]['last_seen'] = timestamp
        else:
            self.patterns[pattern_key] = {
                'metrics': metrics,
                'occurrences': 1,
                'first_seen': timestamp,
                'last_seen': timestamp
            }

        return self._evaluate_pattern(pattern_key)

    def _generate_pattern_key(self, metrics: Dict) -> str:
        """Generate unique key for pattern"""
        return f"{metrics['cpu_usage']:.0f}_{metrics['memory_usage']:.0f}_{metrics['disk_usage']:.0f}"

    def _evaluate_pattern(self, pattern_key: str) -> Optional[Dict]:
        """Evaluate if pattern is significant"""
        pattern = self.patterns[pattern_key]
        if pattern['occurrences'] >= self.min_occurrences:
            return {
                'pattern': pattern['metrics'],
                'occurrences': pattern['occurrences'],
                'duration': (pattern['last_seen'] - pattern['first_seen']).total_seconds()
            }
        return None