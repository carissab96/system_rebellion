# tests/test_pattern_recognition.py

import pytest
from datetime import datetime, timedelta
import numpy as np
from core.ml.pattern_recognition.pattern_analyzer import PatternAnalyzer
from core.ml.pattern_recognition.pattern_matcher import PatternMatcher
from core.ml.pattern_recognition.pattern_validator import PatternValidator
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()

class TestPatternRecognition:
    @pytest.fixture
    def sample_metrics(self):
        return {
            'cpu_usage': 75.0,
            'memory_usage': 80.0,
            'disk_usage': 65.0,
            'timestamp': datetime.now()
        }

    @pytest.mark.asyncio
    async def test_pattern_analyzer(self, sample_metrics):
        analyzer = PatternAnalyzer()
        
        # Test single pattern
        result = await analyzer.analyze_metrics(sample_metrics)
        assert result is None  # First occurrence
        
        # Test pattern recognition
        for _ in range(3):  # Create multiple occurrences
            result = await analyzer.analyze_metrics(sample_metrics)
        
        assert result is not None
        assert result['occurrences'] >= 3

    @pytest.mark.asyncio
    async def test_pattern_matcher(self, sample_metrics):
        matcher = PatternMatcher()
        
        # Test similar states
        similar_metrics = {
            'cpu_usage': 73.0,  # Similar to sample
            'memory_usage': 82.0,
            'disk_usage': 64.0
        }
        
        # Generate embeddings and test matching
        embedding1 = matcher._generate_embedding(sample_metrics)
        embedding2 = matcher._generate_embedding(similar_metrics)
        
        similarity = matcher._calculate_similarity(embedding1, embedding2)
        assert similarity > 0.8  # Should be similar

    @pytest.mark.asyncio
    async def test_pattern_validator(self, sample_metrics):
        validator = PatternValidator()
        
        # Create pattern
        pattern = {
            'metrics': sample_metrics,
            'timestamp': datetime.now()
        }
        
        # Test validation
        result = await validator.validate_pattern(pattern, sample_metrics)
        assert 'confidence' in result
        assert 'is_valid' in result
        assert 'validation_metrics' in result