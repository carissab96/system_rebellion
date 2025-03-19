from typing import List, Dict, Tuple
import numpy as np
#from sklearn.cluster import DBSCAN
#from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PatternLearner:
    """Advanced pattern learning for system optimization"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.clusterer = DBSCAN(eps=0.3, min_samples=3)
        self._pattern_cache: Dict[str, List[Tuple[datetime, np.ndarray]]] = {}
        
    def learn_temporal_patterns(self, user_id: str, context_vector: np.ndarray) -> Dict[str, float]:
        """Learn patterns from temporal context data"""
        now = datetime.now()
        
        # Add new observation to pattern cache
        if user_id not in self._pattern_cache:
            self._pattern_cache[user_id] = []
        self._pattern_cache[user_id].append((now, context_vector))
        
        # Remove old patterns (keep last 7 days)
        week_ago = now - timedelta(days=7)
        self._pattern_cache[user_id] = [
            (t, v) for t, v in self._pattern_cache[user_id]
            if t > week_ago
        ]
        
        # Extract temporal features
        patterns = {}
        if len(self._pattern_cache[user_id]) > 5:  # Need minimum samples
            timestamps, vectors = zip(*self._pattern_cache[user_id])
            
            # Create time-based features
            hour_features = np.array([t.hour / 24.0 for t in timestamps])
            day_features = np.array([t.weekday() / 7.0 for t in timestamps])
            
            # Combine with context vectors
            X = np.column_stack([
                np.array(vectors),
                hour_features.reshape(-1, 1),
                day_features.reshape(-1, 1)
            ])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Find clusters of similar patterns
            clusters = self.clusterer.fit_predict(X_scaled)
            
            # Analyze patterns in each cluster
            for cluster_id in set(clusters):
                if cluster_id == -1:  # Skip noise
                    continue
                    
                cluster_mask = clusters == cluster_id
                cluster_times = np.array(timestamps)[cluster_mask]
                
                # Calculate pattern confidence
                pattern_size = np.sum(cluster_mask)
                pattern_confidence = pattern_size / len(clusters)
                
                # Analyze temporal aspects
                hours = [t.hour for t in cluster_times]
                days = [t.weekday() for t in cluster_times]
                
                # Peak hours pattern
                if np.std(hours) < 3:  # Low standard deviation = consistent timing
                    peak_hour = np.mean(hours)
                    patterns[f'peak_hour_{cluster_id}'] = peak_hour / 24.0
                
                # Weekly pattern
                if np.std(days) < 2:
                    peak_day = np.mean(days)
                    patterns[f'peak_day_{cluster_id}'] = peak_day / 7.0
                
                # Pattern confidence
                patterns[f'pattern_confidence_{cluster_id}'] = pattern_confidence
        
        return patterns

class ResourceOptimizer:
    """Optimizes system resources based on learned patterns"""
    
    def __init__(self):
        self.resource_weights = {
            'cpu': 0.4,
            'memory': 0.4,
            'io': 0.2
        }
    
    def calculate_optimization_score(self, 
                                  patterns: Dict[str, float],
                                  current_usage: Dict[str, float]) -> float:
        """Calculate optimization score based on patterns and current usage"""
        score = 0.0
        
        # Base score on resource usage
        for resource, weight in self.resource_weights.items():
            if resource in current_usage:
                # Lower usage = higher score
                score += (1 - current_usage[resource]) * weight
        
        # Adjust score based on pattern confidence
        confidence_patterns = [v for k, v in patterns.items() 
                             if k.startswith('pattern_confidence')]
        if confidence_patterns:
            avg_confidence = np.mean(confidence_patterns)
            score *= (1 + avg_confidence)  # Boost score if patterns are confident
        
        return min(1.0, score)  # Normalize to [0, 1]
    
    def suggest_optimizations(self, 
                            patterns: Dict[str, float],
                            current_usage: Dict[str, float]) -> List[Dict]:
        """Suggest optimization actions based on patterns"""
        suggestions = []
        score = self.calculate_optimization_score(patterns, current_usage)
        
        # If score is low, suggest optimizations
        if score < 0.6:
            # Check for peak hour patterns
            peak_hours = [v for k, v in patterns.items() 
                        if k.startswith('peak_hour')]
            if peak_hours:
                suggestions.append({
                    'type': 'scheduling',
                    'action': 'defer_heavy_tasks',
                    'confidence': float(np.mean(peak_hours)),
                    'description': 'Defer resource-intensive tasks to off-peak hours'
                })
            
            # Resource-specific optimizations
            for resource, usage in current_usage.items():
                if usage > 0.8:  # High usage
                    suggestions.append({
                        'type': 'resource',
                        'resource': resource,
                        'action': 'optimize',
                        'confidence': float(usage),
                        'description': f'Optimize {resource} usage'
                    })
        
        return suggestions
