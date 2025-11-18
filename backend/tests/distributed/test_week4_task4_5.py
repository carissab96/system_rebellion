"""
Tests for Week 4 Task 4.5: Resource Prediction System

Tests the prediction system that forecasts future resource usage.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ai_agents.distributed.resource_prediction import (
    ResourcePredictor,
    ResourceType,
    TrendDirection,
    DataPoint,
    Prediction,
    get_resource_predictor
)


class TestDataPoint:
    """Test data point functionality"""
    
    def test_create_data_point(self):
        """Test creating a data point"""
        now = datetime.now()
        point = DataPoint(timestamp=now, value=75.0)
        
        assert point.timestamp == now
        assert point.value == 75.0
    
    def test_age_calculation(self):
        """Test age calculation"""
        old_time = datetime.now() - timedelta(seconds=30)
        point = DataPoint(timestamp=old_time, value=80.0)
        
        age = point.age_seconds()
        assert 29 <= age <= 31  # Allow small timing variance


class TestResourcePredictor:
    """Test resource predictor"""
    
    def test_initialization(self):
        """Test predictor initialization"""
        predictor = ResourcePredictor(history_size=50)
        
        assert len(predictor.history) == 4  # 4 resource types
        assert predictor.min_data_points == 5
    
    def test_add_measurement(self):
        """Test adding measurements"""
        predictor = ResourcePredictor()
        
        predictor.add_measurement(ResourceType.CPU, 75.0)
        predictor.add_measurement(ResourceType.CPU, 76.0)
        
        assert len(predictor.history[ResourceType.CPU]) == 2
    
    def test_insufficient_data(self):
        """Test prediction with insufficient data"""
        predictor = ResourcePredictor()
        
        # Add only 2 points (need 5)
        predictor.add_measurement(ResourceType.MEMORY, 70.0)
        predictor.add_measurement(ResourceType.MEMORY, 71.0)
        
        prediction = predictor.predict(ResourceType.MEMORY)
        
        assert prediction is None  # Not enough data
    
    def test_increasing_trend(self):
        """Test prediction with increasing trend"""
        predictor = ResourcePredictor()
        
        # Add increasing values
        base_time = datetime.now() - timedelta(minutes=5)
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 0.5)
            value = 70.0 + (i * 2.0)  # Increasing by 2% every 0.5 min = 4%/min
            predictor.add_measurement(ResourceType.CPU, value, timestamp)
        
        prediction = predictor.predict(ResourceType.CPU)
        
        assert prediction is not None
        assert prediction.trend_direction == TrendDirection.INCREASING
        assert prediction.trend_rate > 0
        assert prediction.predicted_value > prediction.current_value
    
    def test_decreasing_trend(self):
        """Test prediction with decreasing trend"""
        predictor = ResourcePredictor()
        
        # Add decreasing values
        base_time = datetime.now() - timedelta(minutes=5)
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 0.5)
            value = 90.0 - (i * 2.0)  # Decreasing by 2% every 0.5 min = -4%/min
            predictor.add_measurement(ResourceType.MEMORY, value, timestamp)
        
        prediction = predictor.predict(ResourceType.MEMORY)
        
        assert prediction is not None
        assert prediction.trend_direction == TrendDirection.DECREASING
        assert prediction.trend_rate < 0
        assert prediction.predicted_value < prediction.current_value
    
    def test_stable_trend(self):
        """Test prediction with stable trend"""
        predictor = ResourcePredictor()
        
        # Add stable values (small variations)
        base_time = datetime.now() - timedelta(minutes=5)
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 0.5)
            value = 75.0 + (i % 2) * 0.2  # Very small variations
            predictor.add_measurement(ResourceType.DISK, value, timestamp)
        
        prediction = predictor.predict(ResourceType.DISK)
        
        assert prediction is not None
        assert prediction.trend_direction == TrendDirection.STABLE
        assert abs(prediction.trend_rate) < 0.5
    
    def test_threshold_prediction(self):
        """Test threshold crossing prediction"""
        predictor = ResourcePredictor()
        
        # Add increasing values that will cross threshold
        base_time = datetime.now() - timedelta(minutes=5)
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 0.5)
            value = 70.0 + (i * 2.0)  # Will reach 85% soon
            predictor.add_measurement(ResourceType.MEMORY, value, timestamp)
        
        # Current value should be around 88%
        # Trend rate should be around 4%/min
        # Should predict crossing 90% threshold
        
        prediction = predictor.predict(ResourceType.MEMORY, threshold=90.0)
        
        assert prediction is not None
        assert prediction.will_exceed_threshold is True
        assert prediction.time_to_threshold is not None
        assert prediction.time_to_threshold < 10.0  # Within prediction window
    
    def test_no_threshold_crossing(self):
        """Test when threshold won't be crossed"""
        predictor = ResourcePredictor()
        
        # Add stable values well below threshold
        base_time = datetime.now() - timedelta(minutes=5)
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 0.5)
            value = 50.0 + (i % 2) * 0.5  # Stable around 50%
            predictor.add_measurement(ResourceType.CPU, value, timestamp)
        
        prediction = predictor.predict(ResourceType.CPU, threshold=80.0)
        
        assert prediction is not None
        assert prediction.will_exceed_threshold is False
    
    def test_confidence_calculation(self):
        """Test confidence scoring"""
        predictor = ResourcePredictor()
        
        # Add many consistent data points
        base_time = datetime.now() - timedelta(minutes=10)
        for i in range(30):
            timestamp = base_time + timedelta(minutes=i * 0.33)
            value = 70.0 + (i * 0.5)  # Very consistent increase
            predictor.add_measurement(ResourceType.MEMORY, value, timestamp)
        
        prediction = predictor.predict(ResourceType.MEMORY)
        
        assert prediction is not None
        # Should have high confidence with lots of consistent data
        assert prediction.confidence > 0.6
    
    def test_get_all_predictions(self):
        """Test getting predictions for all resources"""
        predictor = ResourcePredictor()
        
        # Add data for multiple resources
        base_time = datetime.now() - timedelta(minutes=5)
        for resource in [ResourceType.CPU, ResourceType.MEMORY]:
            for i in range(10):
                timestamp = base_time + timedelta(minutes=i * 0.5)
                value = 70.0 + (i * 1.0)
                predictor.add_measurement(resource, value, timestamp)
        
        predictions = predictor.get_all_predictions()
        
        assert len(predictions) == 4  # All 4 resource types
        assert predictions[ResourceType.CPU] is not None
        assert predictions[ResourceType.MEMORY] is not None
        assert predictions[ResourceType.DISK] is None  # No data
        assert predictions[ResourceType.NETWORK] is None  # No data
    
    def test_proactive_alerts(self):
        """Test getting proactive alerts"""
        predictor = ResourcePredictor()
        
        # Add data that will trigger alerts
        base_time = datetime.now() - timedelta(minutes=5)
        
        # CPU: increasing, will hit threshold
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 0.5)
            value = 75.0 + (i * 2.0)  # Will hit 85% threshold
            predictor.add_measurement(ResourceType.CPU, value, timestamp)
        
        # Memory: stable, won't hit threshold
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 0.5)
            value = 50.0
            predictor.add_measurement(ResourceType.MEMORY, value, timestamp)
        
        thresholds = {
            ResourceType.CPU: 85.0,
            ResourceType.MEMORY: 85.0,
            ResourceType.DISK: 90.0,
            ResourceType.NETWORK: 80.0
        }
        
        alerts = predictor.get_proactive_alerts(thresholds)
        
        # Should get alert for CPU only
        assert len(alerts) >= 1
        assert alerts[0].resource_type == ResourceType.CPU
        assert alerts[0].will_exceed_threshold is True
    
    def test_prediction_validation(self):
        """Test prediction validation"""
        predictor = ResourcePredictor()
        
        # Accurate prediction
        predictor.validate_prediction(ResourceType.CPU, 80.0, 82.0)  # Within 5%
        
        # Inaccurate prediction
        predictor.validate_prediction(ResourceType.CPU, 80.0, 92.0)  # More than 5%
        
        # Note: validate_prediction doesn't increment total_predictions
        # It only tracks accuracy of validations
        assert predictor.accurate_predictions == 1
    
    def test_clear_history(self):
        """Test clearing history"""
        predictor = ResourcePredictor()
        
        # Add data
        for i in range(10):
            predictor.add_measurement(ResourceType.CPU, 70.0 + i)
            predictor.add_measurement(ResourceType.MEMORY, 60.0 + i)
        
        assert len(predictor.history[ResourceType.CPU]) == 10
        assert len(predictor.history[ResourceType.MEMORY]) == 10
        
        # Clear CPU only
        predictor.clear_history(ResourceType.CPU)
        
        assert len(predictor.history[ResourceType.CPU]) == 0
        assert len(predictor.history[ResourceType.MEMORY]) == 10
        
        # Clear all
        predictor.clear_history()
        
        assert len(predictor.history[ResourceType.MEMORY]) == 0


class TestGlobalSingleton:
    """Test global predictor singleton"""
    
    def test_singleton_returns_same_instance(self):
        """Test that get_resource_predictor returns singleton"""
        predictor1 = get_resource_predictor()
        predictor2 = get_resource_predictor()
        
        assert predictor1 is predictor2


class TestPredictionString:
    """Test prediction string representation"""
    
    def test_prediction_with_threshold(self):
        """Test string for prediction with threshold crossing"""
        prediction = Prediction(
            resource_type=ResourceType.MEMORY,
            current_value=85.0,
            predicted_value=92.0,
            prediction_time=datetime.now() + timedelta(minutes=5),
            confidence=0.85,
            trend_direction=TrendDirection.INCREASING,
            trend_rate=1.4,
            will_exceed_threshold=True,
            time_to_threshold=5.0,
            threshold_value=90.0
        )
        
        string = str(prediction)
        assert "MEMORY" in string
        assert "85.0%" in string
        assert "92.0%" in string
        assert "5.0m" in string
        assert "85%" in string  # confidence
    
    def test_prediction_without_threshold(self):
        """Test string for prediction without threshold"""
        prediction = Prediction(
            resource_type=ResourceType.CPU,
            current_value=70.0,
            predicted_value=72.0,
            prediction_time=datetime.now() + timedelta(minutes=10),
            confidence=0.75,
            trend_direction=TrendDirection.STABLE,
            trend_rate=0.2
        )
        
        string = str(prediction)
        assert "CPU" in string
        assert "70.0%" in string
        assert "stable" in string


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
