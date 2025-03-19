from typing import Dict, List, Tuple
import numpy as np
#from sklearn.ensemble import IsolationForest
#from sklearn.preprocessing import StandardScaler
#import tensorflow as tf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AdvancedPatternDetector:
    """Advanced pattern detection using multiple ML techniques"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self._build_sequence_model()
        
    def _build_sequence_model(self):
        """Build LSTM model for sequence prediction"""
        self.sequence_model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, input_shape=(None, 10)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        self.sequence_model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
    
    def detect_anomalies(self, data: np.ndarray) -> List[bool]:
        """Detect anomalous patterns in data"""
        scaled_data = self.scaler.fit_transform(data)
        return self.anomaly_detector.fit_predict(scaled_data) == -1
    
    def predict_sequence(self, 
                        sequence: np.ndarray,
                        horizon: int = 5) -> np.ndarray:
        """Predict future sequence values"""
        scaled_seq = self.scaler.fit_transform(sequence)
        predictions = []
        
        for _ in range(horizon):
            pred = self.sequence_model.predict(
                scaled_seq[-10:].reshape(1, -1, 10)
            )
            predictions.append(pred[0, 0])
            scaled_seq = np.append(scaled_seq, pred)
            
        return self.scaler.inverse_transform(
            np.array(predictions).reshape(-1, 1)
        )

class WorkloadPredictor:
    """Predicts system workload patterns"""
    
    def __init__(self):
        self.pattern_detector = AdvancedPatternDetector()
        self._activity_cache: Dict[str, List[Tuple[datetime, str]]] = {}
        self._resource_cache: Dict[str, List[Tuple[datetime, Dict]]] = {}
    
    def add_observation(self, 
                       user_id: str,
                       timestamp: datetime,
                       activity: str,
                       resources: Dict[str, float]):
        """Add new observation to prediction model"""
        # Update activity cache
        if user_id not in self._activity_cache:
            self._activity_cache[user_id] = []
        self._activity_cache[user_id].append((timestamp, activity))
        
        # Update resource cache
        if user_id not in self._resource_cache:
            self._resource_cache[user_id] = []
        self._resource_cache[user_id].append((timestamp, resources))
        
        # Maintain cache size (keep last 7 days)
        week_ago = timestamp - timedelta(days=7)
        self._activity_cache[user_id] = [
            (t, a) for t, a in self._activity_cache[user_id]
            if t > week_ago
        ]
        self._resource_cache[user_id] = [
            (t, r) for t, r in self._resource_cache[user_id]
            if t > week_ago
        ]
    
    def predict_workload(self, 
                        user_id: str,
                        future_hours: int = 24) -> Dict:
        """Predict future workload patterns"""
        if user_id not in self._resource_cache:
            return {}
            
        # Extract resource usage sequences
        timestamps, resources = zip(*self._resource_cache[user_id])
        cpu_usage = np.array([r.get('cpu', 0) for r in resources])
        memory_usage = np.array([r.get('memory', 0) for r in resources])
        
        # Detect anomalies
        cpu_anomalies = self.pattern_detector.detect_anomalies(
            cpu_usage.reshape(-1, 1)
        )
        memory_anomalies = self.pattern_detector.detect_anomalies(
            memory_usage.reshape(-1, 1)
        )
        
        # Predict future usage
        future_cpu = self.pattern_detector.predict_sequence(
            cpu_usage.reshape(-1, 1)
        )
        future_memory = self.pattern_detector.predict_sequence(
            memory_usage.reshape(-1, 1)
        )
        
        # Analyze activity patterns
        activity_patterns = self._analyze_activity_patterns(user_id)
        
        return {
            'current_anomalies': {
                'cpu': bool(cpu_anomalies[-1]),
                'memory': bool(memory_anomalies[-1])
            },
            'predictions': {
                'cpu': future_cpu.flatten().tolist(),
                'memory': future_memory.flatten().tolist()
            },
            'activity_patterns': activity_patterns
        }
    
    def _analyze_activity_patterns(self, user_id: str) -> Dict:
        """Analyze user activity patterns"""
        if user_id not in self._activity_cache:
            return {}
            
        activities = {}
        hour_patterns = {}
        
        for timestamp, activity in self._activity_cache[user_id]:
            # Activity frequency
            activities[activity] = activities.get(activity, 0) + 1
            
            # Hour patterns
            hour = timestamp.hour
            if hour not in hour_patterns:
                hour_patterns[hour] = {}
            hour_patterns[hour][activity] = \
                hour_patterns[hour].get(activity, 0) + 1
        
        # Normalize frequencies
        total = sum(activities.values())
        activities = {k: v/total for k, v in activities.items()}
        
        # Find peak hours for each activity
        peak_hours = {}
        for activity in activities:
            activity_hours = {
                h: patterns.get(activity, 0)
                for h, patterns in hour_patterns.items()
            }
            if activity_hours:
                peak_hours[activity] = max(
                    activity_hours.items(),
                    key=lambda x: x[1]
                )[0]
        
        return {
            'activity_frequencies': activities,
            'peak_hours': peak_hours
        }

class OptimizationPlanner:
    """Plans optimizations based on predictions"""
    
    def __init__(self):
        self.workload_predictor = WorkloadPredictor()
    
    def plan_optimizations(self, 
                          user_id: str,
                          current_context: Dict) -> Dict:
        """Plan optimizations based on predictions and current context"""
        # Add current observation
        self.workload_predictor.add_observation(
            user_id=user_id,
            timestamp=datetime.now(),
            activity=current_context.get('current_activity', 'unknown'),
            resources={
                'cpu': np.mean(current_context.get('cpu_usage', [0])),
                'memory': np.mean(current_context.get('memory_usage', [0]))
            }
        )
        
        # Get predictions
        predictions = self.workload_predictor.predict_workload(user_id)
        
        # Plan optimizations
        optimizations = []
        
        # Handle anomalies
        if predictions.get('current_anomalies', {}).get('cpu', False):
            optimizations.append({
                'type': 'immediate',
                'resource': 'cpu',
                'action': 'investigate_cpu_spike',
                'priority': 'high'
            })
            
        if predictions.get('current_anomalies', {}).get('memory', False):
            optimizations.append({
                'type': 'immediate',
                'resource': 'memory',
                'action': 'investigate_memory_spike',
                'priority': 'high'
            })
        
        # Plan based on activity patterns
        activity_patterns = predictions.get('activity_patterns', {})
        for activity, peak_hour in activity_patterns.get('peak_hours', {}).items():
            current_hour = datetime.now().hour
            if abs(current_hour - peak_hour) <= 2:  # Near peak hour
                optimizations.append({
                    'type': 'scheduled',
                    'activity': activity,
                    'action': 'prepare_resources',
                    'priority': 'medium'
                })
        
        # Predictive optimizations
        future_cpu = predictions.get('predictions', {}).get('cpu', [])
        future_memory = predictions.get('predictions', {}).get('memory', [])
        
        if future_cpu and max(future_cpu) > 0.8:
            optimizations.append({
                'type': 'predictive',
                'resource': 'cpu',
                'action': 'prepare_cpu_scaling',
                'priority': 'medium'
            })
            
        if future_memory and max(future_memory) > 0.8:
            optimizations.append({
                'type': 'predictive',
                'resource': 'memory',
                'action': 'prepare_memory_scaling',
                'priority': 'medium'
            })
        
        return {
            'predictions': predictions,
            'optimizations': optimizations
        }


