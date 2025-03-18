from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np

class PatternValidator:
    def __init__(self):
        self.validation_window = timedelta(hours=24)
        self.confidence_threshold = 0.85
        self.min_samples = 5
        self.validated_patterns = {}

    async def validate_pattern(self, pattern: Dict, metrics: Dict) -> Dict:
        """Validate pattern against historical data and current metrics"""
        pattern_id = self._generate_pattern_id(pattern)
        
        if pattern_id not in self.validated_patterns:
            self.validated_patterns[pattern_id] = {
                'pattern': pattern,
                'samples': [],
                'confidence': 0.0,
                'last_validated': None
            }

        validation_result = await self._calculate_validation_score(
            pattern_id, metrics
        )

        return {
            'pattern_id': pattern_id,
            'is_valid': validation_result['confidence'] >= self.confidence_threshold,
            'confidence': validation_result['confidence'],
            'validation_metrics': validation_result['metrics']
        }

    async def _calculate_validation_score(self, pattern_id: str, metrics: Dict) -> Dict:
        """Calculate validation score for pattern"""
        pattern_data = self.validated_patterns[pattern_id]
        
        # Add new sample
        pattern_data['samples'].append({
            'metrics': metrics,
            'timestamp': datetime.now()
        })

        # Remove old samples
        self._clean_old_samples(pattern_data)

        # Calculate confidence
        if len(pattern_data['samples']) >= self.min_samples:
            confidence = self._calculate_confidence(pattern_data)
        else:
            confidence = 0.0

        pattern_data['confidence'] = confidence
        pattern_data['last_validated'] = datetime.now()

        return {
            'confidence': confidence,
            'metrics': {
                'sample_count': len(pattern_data['samples']),
                'time_span': self._get_time_span(pattern_data),
                'variance': self._calculate_variance(pattern_data)
            }
        }

    def _generate_pattern_id(self, pattern: Dict) -> str:
        """Generate unique identifier for pattern"""
        metrics = pattern.get('metrics', {})
        return f"pattern_{hash(frozenset(metrics.items()))}"

    def _clean_old_samples(self, pattern_data: Dict):
        """Remove samples outside validation window"""
        cutoff_time = datetime.now() - self.validation_window
        pattern_data['samples'] = [
            sample for sample in pattern_data['samples']
            if sample['timestamp'] > cutoff_time
        ]

    def _calculate_confidence(self, pattern_data: Dict) -> float:
        """Calculate confidence score for pattern"""
        if not pattern_data['samples']:
            return 0.0

        variances = self._calculate_variance(pattern_data)
        time_span = self._get_time_span(pattern_data)
        sample_count = len(pattern_data['samples'])

        # Weighted confidence calculation
        confidence = (
            (1.0 - variances['total']) * 0.4 +
            min(time_span / self.validation_window.total_seconds(), 1.0) * 0.3 +
            min(sample_count / self.min_samples, 1.0) * 0.3
        )

        return round(confidence, 3)

    def _calculate_variance(self, pattern_data: Dict) -> Dict:
        """Calculate variance in pattern metrics"""
        metrics = [sample['metrics'] for sample in pattern_data['samples']]
        
        variances = {
            'cpu': np.var([m['cpu_usage'] for m in metrics]) / 100,
            'memory': np.var([m['memory_usage'] for m in metrics]) / 100,
            'disk': np.var([m['disk_usage'] for m in metrics]) / 100
        }
        
        variances['total'] = sum(variances.values()) / len(variances)
        return variances

    def _get_time_span(self, pattern_data: Dict) -> float:
        """Calculate time span of pattern samples"""
        if not pattern_data['samples']:
            return 0.0
            
        timestamps = [s['timestamp'] for s in pattern_data['samples']]
        return (max(timestamps) - min(timestamps)).total_seconds()