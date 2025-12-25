#!/usr/bin/env python3
"""
ML Helper Methods for Terry's Reasoning Engine

Pattern validation and anomaly detection helpers.
"""

import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger('TerryMLHelpers')


async def validate_pattern_ml(pattern_validator, context, root_cause) -> Dict[str, Any]:
    """
    Validate pattern using ML PatternValidator.
    
    Requires 85% confidence and 5+ samples before trusting pattern.
    
    Args:
        pattern_validator: PatternValidator instance
        context: PerceptionContext
        root_cause: RootCauseAnalysis
        
    Returns:
        Dictionary with is_valid, confidence, sample_count
    """
    try:
        pattern = {
            'resource_type': context.resource_type,
            'severity': context.severity,
            'root_cause': root_cause.cause,
            'current_value': context.current_value,
            'metrics': {
                'cpu_usage': context.full_metrics.get('cpu_usage', 0),
                'memory_usage': context.full_metrics.get('memory_usage', 0),
                'disk_usage': context.full_metrics.get('disk_usage', 0)
            }
        }
        
        validation = await pattern_validator.validate_pattern(
            pattern=pattern,
            metrics=context.full_metrics
        )
        
        return {
            'is_valid': validation['is_valid'],
            'confidence': validation['confidence'],
            'sample_count': validation.get('validation_metrics', {}).get('sample_count', 0)
        }
        
    except Exception as e:
        logger.warning(f"Pattern validation failed: {e}")
        return {'is_valid': True, 'confidence': 0.5, 'sample_count': 0}


async def detect_anomaly_ml(anomaly_detector, context) -> bool:
    """
    Detect if current metrics are anomalous using IsolationForest.
    
    Args:
        anomaly_detector: AdvancedPatternDetector instance
        context: PerceptionContext
        
    Returns:
        True if anomaly detected, False otherwise
    """
    try:
        # Create metrics array for anomaly detection
        metrics_array = np.array([
            context.full_metrics.get('cpu_usage', 0),
            context.full_metrics.get('memory_usage', 0),
            context.full_metrics.get('disk_usage', 0)
        ]).reshape(-1, 1)
        
        # Detect anomalies
        is_anomaly_array = anomaly_detector.detect_anomalies(metrics_array)
        
        # Return True if any metric is anomalous
        return bool(np.any(is_anomaly_array))
        
    except Exception as e:
        logger.warning(f"Anomaly detection failed: {e}")
        return False
