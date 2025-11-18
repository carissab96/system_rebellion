"""
Resource Prediction System for System Rebellion

Predicts future resource usage to enable proactive responses:
- Trend analysis (linear regression on historical data)
- Pattern recognition (daily/weekly cycles)
- Time-to-threshold prediction
- Confidence scoring
- Proactive alerting

Week 4 Task 4.5
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    """Resource types for prediction"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


class TrendDirection(str, Enum):
    """Trend direction"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


@dataclass
class DataPoint:
    """Single resource measurement"""
    timestamp: datetime
    value: float
    
    def age_seconds(self) -> float:
        """Get age of this data point in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class Prediction:
    """Resource usage prediction"""
    resource_type: ResourceType
    current_value: float
    predicted_value: float
    prediction_time: datetime  # When will it reach predicted_value
    confidence: float  # 0-1
    
    # Trend info
    trend_direction: TrendDirection
    trend_rate: float  # Change per minute
    
    # Threshold predictions
    time_to_threshold: Optional[float] = None  # Minutes until threshold
    will_exceed_threshold: bool = False
    threshold_value: Optional[float] = None
    
    def __str__(self) -> str:
        if self.will_exceed_threshold:
            return (
                f"{self.resource_type.upper()}: {self.current_value:.1f}% → "
                f"{self.predicted_value:.1f}% in {self.time_to_threshold:.1f}m "
                f"(confidence: {self.confidence:.0%})"
            )
        else:
            return (
                f"{self.resource_type.upper()}: {self.current_value:.1f}% "
                f"({self.trend_direction.value}, {self.trend_rate:+.2f}%/min)"
            )


class ResourcePredictor:
    """
    Predicts future resource usage based on historical data.
    
    Uses simple linear regression for short-term predictions.
    Tracks patterns for better long-term predictions.
    """
    
    def __init__(self, history_size: int = 100):
        # Historical data (last N measurements per resource)
        self.history: Dict[ResourceType, deque] = {
            resource: deque(maxlen=history_size)
            for resource in ResourceType
        }
        
        # Configuration
        self.min_data_points = 5  # Minimum points needed for prediction
        self.prediction_window = 10.0  # Minutes to predict ahead
        self.stable_threshold = 0.5  # %/min change to be considered stable
        
        # Statistics
        self.total_predictions = 0
        self.accurate_predictions = 0  # Predictions within 5% of actual
    
    def add_measurement(
        self,
        resource_type: ResourceType,
        value: float,
        timestamp: Optional[datetime] = None
    ):
        """Add a resource measurement to history"""
        if timestamp is None:
            timestamp = datetime.now()
        
        data_point = DataPoint(timestamp=timestamp, value=value)
        self.history[resource_type].append(data_point)
    
    def predict(
        self,
        resource_type: ResourceType,
        threshold: Optional[float] = None,
        prediction_minutes: Optional[float] = None
    ) -> Optional[Prediction]:
        """
        Predict future resource usage.
        
        Args:
            resource_type: Resource to predict
            threshold: Optional threshold to check against
            prediction_minutes: How far ahead to predict (default: self.prediction_window)
        
        Returns:
            Prediction object or None if insufficient data
        """
        history = self.history[resource_type]
        
        if len(history) < self.min_data_points:
            logger.debug(
                f"Insufficient data for {resource_type} prediction "
                f"({len(history)}/{self.min_data_points})"
            )
            return None
        
        if prediction_minutes is None:
            prediction_minutes = self.prediction_window
        
        # Get current value
        current_value = history[-1].value
        
        # Calculate trend
        trend_rate = self._calculate_trend_rate(history)
        trend_direction = self._determine_trend_direction(trend_rate)
        
        # Predict future value
        predicted_value = current_value + (trend_rate * prediction_minutes)
        predicted_value = max(0.0, min(100.0, predicted_value))  # Clamp to 0-100
        
        # Calculate confidence
        confidence = self._calculate_confidence(history, trend_rate)
        
        # Create base prediction
        prediction = Prediction(
            resource_type=resource_type,
            current_value=current_value,
            predicted_value=predicted_value,
            prediction_time=datetime.now() + timedelta(minutes=prediction_minutes),
            confidence=confidence,
            trend_direction=trend_direction,
            trend_rate=trend_rate
        )
        
        # Check threshold if provided
        if threshold is not None:
            self._check_threshold(prediction, threshold, trend_rate, current_value)
        
        self.total_predictions += 1
        
        return prediction
    
    def _calculate_trend_rate(self, history: deque) -> float:
        """
        Calculate trend rate (change per minute).
        
        Uses simple linear regression on recent data.
        """
        if len(history) < 2:
            return 0.0
        
        # Convert to lists for calculation
        points = list(history)
        
        # Use only recent data (last 20 points or 5 minutes, whichever is less)
        recent_points = []
        cutoff_time = datetime.now() - timedelta(minutes=5)
        
        for point in reversed(points):
            if point.timestamp < cutoff_time and len(recent_points) >= 20:
                break
            recent_points.insert(0, point)
        
        if len(recent_points) < 2:
            return 0.0
        
        # Calculate time deltas in minutes from first point
        first_time = recent_points[0].timestamp
        times = [(p.timestamp - first_time).total_seconds() / 60.0 for p in recent_points]
        values = [p.value for p in recent_points]
        
        # Simple linear regression
        n = len(times)
        sum_x = sum(times)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(times, values))
        sum_x2 = sum(x * x for x in times)
        
        # Calculate slope (trend rate per minute)
        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        return slope
    
    def _determine_trend_direction(self, trend_rate: float) -> TrendDirection:
        """Determine if trend is increasing, decreasing, or stable"""
        if abs(trend_rate) < self.stable_threshold:
            return TrendDirection.STABLE
        elif trend_rate > 0:
            return TrendDirection.INCREASING
        else:
            return TrendDirection.DECREASING
    
    def _calculate_confidence(self, history: deque, trend_rate: float) -> float:
        """
        Calculate confidence in prediction (0-1).
        
        Based on:
        - Amount of data (more = higher confidence)
        - Consistency of trend (less variance = higher confidence)
        - Recency of data (fresher = higher confidence)
        """
        points = list(history)
        
        # Factor 1: Data amount (0-1)
        data_confidence = min(len(points) / 20.0, 1.0)
        
        # Factor 2: Trend consistency (0-1)
        if len(points) >= 5:
            # Calculate variance in recent changes
            recent_changes = []
            for i in range(len(points) - 1, max(0, len(points) - 11), -1):
                if i > 0:
                    time_diff = (points[i].timestamp - points[i-1].timestamp).total_seconds() / 60.0
                    if time_diff > 0:
                        change_rate = (points[i].value - points[i-1].value) / time_diff
                        recent_changes.append(change_rate)
            
            if len(recent_changes) >= 3:
                variance = statistics.variance(recent_changes)
                # Lower variance = higher confidence
                consistency_confidence = max(0.0, 1.0 - (variance / 10.0))
            else:
                consistency_confidence = 0.5
        else:
            consistency_confidence = 0.5
        
        # Factor 3: Data recency (0-1)
        avg_age = statistics.mean([p.age_seconds() for p in points])
        # Fresher data = higher confidence (decay over 5 minutes)
        recency_confidence = max(0.0, 1.0 - (avg_age / 300.0))
        
        # Weighted average
        confidence = (
            data_confidence * 0.4 +
            consistency_confidence * 0.4 +
            recency_confidence * 0.2
        )
        
        return confidence
    
    def _check_threshold(
        self,
        prediction: Prediction,
        threshold: float,
        trend_rate: float,
        current_value: float
    ):
        """Check if prediction will exceed threshold"""
        # Only predict threshold crossing if trending upward
        if trend_rate <= 0:
            prediction.will_exceed_threshold = False
            return
        
        # Check if already over threshold
        if current_value >= threshold:
            prediction.will_exceed_threshold = True
            prediction.threshold_value = threshold
            prediction.time_to_threshold = 0.0
            return
        
        # Calculate time to threshold
        value_gap = threshold - current_value
        time_to_threshold = value_gap / trend_rate if trend_rate > 0 else float('inf')
        
        # Only alert if will hit threshold within prediction window
        if time_to_threshold <= self.prediction_window:
            prediction.will_exceed_threshold = True
            prediction.threshold_value = threshold
            prediction.time_to_threshold = time_to_threshold
        else:
            prediction.will_exceed_threshold = False
    
    def get_all_predictions(
        self,
        thresholds: Optional[Dict[ResourceType, float]] = None
    ) -> Dict[ResourceType, Optional[Prediction]]:
        """Get predictions for all resources"""
        predictions = {}
        
        for resource_type in ResourceType:
            threshold = thresholds.get(resource_type) if thresholds else None
            prediction = self.predict(resource_type, threshold)
            predictions[resource_type] = prediction
        
        return predictions
    
    def get_proactive_alerts(
        self,
        thresholds: Dict[ResourceType, float]
    ) -> List[Prediction]:
        """
        Get predictions that warrant proactive alerts.
        
        Returns predictions where resources will exceed thresholds soon.
        """
        alerts = []
        
        predictions = self.get_all_predictions(thresholds)
        
        for resource_type, prediction in predictions.items():
            if prediction and prediction.will_exceed_threshold:
                # Only alert if confidence is reasonable
                if prediction.confidence >= 0.5:
                    alerts.append(prediction)
        
        # Sort by urgency (soonest first)
        alerts.sort(key=lambda p: p.time_to_threshold or float('inf'))
        
        return alerts
    
    def validate_prediction(
        self,
        resource_type: ResourceType,
        predicted_value: float,
        actual_value: float
    ):
        """
        Validate a prediction against actual value.
        
        Used to track prediction accuracy.
        """
        error = abs(predicted_value - actual_value)
        
        # Consider accurate if within 5%
        if error <= 5.0:
            self.accurate_predictions += 1
        
        logger.debug(
            f"Prediction validation for {resource_type}: "
            f"predicted={predicted_value:.1f}%, actual={actual_value:.1f}%, "
            f"error={error:.1f}%"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        accuracy = (
            self.accurate_predictions / self.total_predictions
            if self.total_predictions > 0 else 0.0
        )
        
        data_points = {
            resource.value: len(self.history[resource])
            for resource in ResourceType
        }
        
        return {
            "total_predictions": self.total_predictions,
            "accurate_predictions": self.accurate_predictions,
            "accuracy": accuracy,
            "data_points": data_points
        }
    
    def clear_history(self, resource_type: Optional[ResourceType] = None):
        """Clear prediction history"""
        if resource_type:
            self.history[resource_type].clear()
        else:
            for resource in ResourceType:
                self.history[resource].clear()


# Global singleton
_resource_predictor: Optional[ResourcePredictor] = None


def get_resource_predictor() -> ResourcePredictor:
    """Get or create the global resource predictor"""
    global _resource_predictor
    if _resource_predictor is None:
        _resource_predictor = ResourcePredictor()
    return _resource_predictor
