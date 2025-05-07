"""
System Rebellion Metrics Package

This package contains services for collecting various system metrics.
Each metric type has its own dedicated service for better separation of concerns.
"""

from app.services.metrics.metrics_service import MetricsService

# Export the main service for easy importing
__all__ = ['MetricsService']
