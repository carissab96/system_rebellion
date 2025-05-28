import numpy as np
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
import time
import json

logger = logging.getLogger(__name__)

class MetricTransformer:
    """
    Sir Hawkington's Distinguished Metric Transformation System
    
    Transforms raw system metrics into actionable intelligence using NumPy.
    Provides statistical analysis, anomaly detection, and data smoothing.
    """
    
    def __init__(
        self,
        name: str = "default",
        history_size: int = 60,  # Keep 60 data points by default
        smoothing_window: int = 5,  # Smooth over 5 data points
        anomaly_threshold: float = 2.0,  # Z-score threshold for anomalies
        percentiles: List[float] = [25, 50, 75, 90, 95, 99]
    ):
        self.name = name
        self.history_size = history_size
        self.smoothing_window = smoothing_window
        self.anomaly_threshold = anomaly_threshold
        self.percentiles = percentiles
        
        # Initialize history storage for different metric types
        self.cpu_history = []
        self.memory_history = []
        self.disk_history = []
        self.network_history = []
        
        # Timestamps for each data point
        self.timestamps = []
        
        logger.info(f"Metric Transformer '{name}' initialized with history_size={history_size}")
    
    def _add_to_history(self, metric_type: str, data_point: Any) -> None:
        """Add a data point to the appropriate history"""
        if metric_type == "cpu":
            self.cpu_history.append(data_point)
            if len(self.cpu_history) > self.history_size:
                self.cpu_history.pop(0)
        elif metric_type == "memory":
            self.memory_history.append(data_point)
            if len(self.memory_history) > self.history_size:
                self.memory_history.pop(0)
        elif metric_type == "disk":
            self.disk_history.append(data_point)
            if len(self.disk_history) > self.history_size:
                self.disk_history.pop(0)
        elif metric_type == "network":
            self.network_history.append(data_point)
            if len(self.network_history) > self.history_size:
                self.network_history.pop(0)
        
        # Add timestamp
        now = datetime.now()
        self.timestamps.append(now)
        if len(self.timestamps) > self.history_size:
            self.timestamps.pop(0)
    
    def _smooth_data(self, data: List[float]) -> np.ndarray:
        """Apply smoothing to a data series"""
        if not data or len(data) < 2:
            return np.array(data)
            
        # Convert to numpy array
        data_array = np.array(data)
        
        # Apply moving average smoothing
        if len(data_array) >= self.smoothing_window:
            # Create a rolling window view of the data
            window_size = min(self.smoothing_window, len(data_array))
            smoothed = np.convolve(data_array, np.ones(window_size)/window_size, mode='valid')
            
            # Pad the beginning to maintain the same length
            padding = len(data_array) - len(smoothed)
            if padding > 0:
                # Use the first smoothed value for padding
                padding_value = smoothed[0] if len(smoothed) > 0 else data_array[0]
                smoothed = np.concatenate([np.full(padding, padding_value), smoothed])
                
            return smoothed
        else:
            return data_array
    
    def _detect_anomalies(self, data: List[float]) -> List[bool]:
        """
        Detect anomalies in a data series using Z-score
        
        Returns:
            List of booleans indicating whether each point is an anomaly
        """
        if not data or len(data) < 4:  # Need some data for meaningful statistics
            return [False] * len(data)
            
        # Convert to numpy array
        data_array = np.array(data)
        
        # Calculate Z-scores
        mean = np.mean(data_array)
        std = np.std(data_array)
        
        if std == 0:  # Avoid division by zero
            return [False] * len(data)
            
        z_scores = np.abs((data_array - mean) / std)
        
        # Mark points with Z-score above threshold as anomalies
        return (z_scores > self.anomaly_threshold).tolist()
    
    def _calculate_rate_of_change(self, data: List[float]) -> List[float]:
        """Calculate rate of change between consecutive data points"""
        if not data or len(data) < 2:
            return [0.0] * len(data)
            
        # Convert to numpy array
        data_array = np.array(data)
        
        # Calculate differences
        diffs = np.diff(data_array)
        
        # Pad with 0 at the beginning to maintain length
        return np.concatenate([[0.0], diffs]).tolist()
    
    def _calculate_statistics(self, data: List[float]) -> Dict[str, float]:
        """Calculate statistical measures for a data series"""
        if not data:
            return {
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
                "std_dev": 0.0,
                "percentiles": {str(p): 0.0 for p in self.percentiles}
            }
            
        # Convert to numpy array
        data_array = np.array(data)
        
        # Calculate statistics
        stats = {
            "mean": float(np.mean(data_array)),
            "min": float(np.min(data_array)),
            "max": float(np.max(data_array)),
            "std_dev": float(np.std(data_array)),
            "percentiles": {
                str(p): float(np.percentile(data_array, p)) for p in self.percentiles
            }
        }
        
        return stats
    
    def transform_cpu_metrics(self, raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CPU metrics"""
        # Extract CPU usage percentage
        cpu_percent = raw_metrics.get('percent', 0.0)
        
        # Add to history
        self._add_to_history("cpu", cpu_percent)
        
        # Get CPU history as numpy array
        cpu_history_array = np.array(self.cpu_history)
        
        # Apply transformations
        smoothed_cpu = self._smooth_data(self.cpu_history)
        anomalies = self._detect_anomalies(self.cpu_history)
        rate_of_change = self._calculate_rate_of_change(self.cpu_history)
        statistics = self._calculate_statistics(self.cpu_history)
        
        # Calculate load trend (positive = increasing, negative = decreasing)
        if len(self.cpu_history) >= 10:
            recent_trend = np.polyfit(range(len(self.cpu_history[-10:])), self.cpu_history[-10:], 1)[0]
        else:
            recent_trend = 0.0
        
        # Prepare transformed metrics
        transformed = {
            "current": cpu_percent,
            "smoothed": float(smoothed_cpu[-1]) if len(smoothed_cpu) > 0 else cpu_percent,
            "history": self.cpu_history,
            "smoothed_history": smoothed_cpu.tolist(),
            "anomalies": anomalies,
            "rate_of_change": rate_of_change,
            "statistics": statistics,
            "trend": float(recent_trend),
            "is_anomaly": anomalies[-1] if anomalies else False
        }
        
        # Add the original metrics
        transformed.update(raw_metrics)
        
        return transformed
    
    def transform_memory_metrics(self, raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Transform memory metrics"""
        # Extract memory usage percentage
        memory_percent = raw_metrics.get('percent', 0.0)
        
        # Add to history
        self._add_to_history("memory", memory_percent)
        
        # Apply transformations
        smoothed_memory = self._smooth_data(self.memory_history)
        anomalies = self._detect_anomalies(self.memory_history)
        rate_of_change = self._calculate_rate_of_change(self.memory_history)
        statistics = self._calculate_statistics(self.memory_history)
        
        # Calculate trend
        if len(self.memory_history) >= 10:
            recent_trend = np.polyfit(range(len(self.memory_history[-10:])), self.memory_history[-10:], 1)[0]
        else:
            recent_trend = 0.0
        
        # Prepare transformed metrics
        transformed = {
            "current": memory_percent,
            "smoothed": float(smoothed_memory[-1]) if len(smoothed_memory) > 0 else memory_percent,
            "history": self.memory_history,
            "smoothed_history": smoothed_memory.tolist(),
            "anomalies": anomalies,
            "rate_of_change": rate_of_change,
            "statistics": statistics,
            "trend": float(recent_trend),
            "is_anomaly": anomalies[-1] if anomalies else False
        }
        
        # Add the original metrics
        transformed.update(raw_metrics)
        
        return transformed
    
    def transform_disk_metrics(self, raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Transform disk metrics"""
        # Extract disk usage percentage
        disk_percent = raw_metrics.get('percent', 0.0)
        
        # Add to history
        self._add_to_history("disk", disk_percent)
        
        # Apply transformations
        smoothed_disk = self._smooth_data(self.disk_history)
        anomalies = self._detect_anomalies(self.disk_history)
        rate_of_change = self._calculate_rate_of_change(self.disk_history)
        statistics = self._calculate_statistics(self.disk_history)
        
        # Calculate trend
        if len(self.disk_history) >= 10:
            recent_trend = np.polyfit(range(len(self.disk_history[-10:])), self.disk_history[-10:], 1)[0]
        else:
            recent_trend = 0.0
        
        # Prepare transformed metrics
        transformed = {
            "current": disk_percent,
            "smoothed": float(smoothed_disk[-1]) if len(smoothed_disk) > 0 else disk_percent,
            "history": self.disk_history,
            "smoothed_history": smoothed_disk.tolist(),
            "anomalies": anomalies,
            "rate_of_change": rate_of_change,
            "statistics": statistics,
            "trend": float(recent_trend),
            "is_anomaly": anomalies[-1] if anomalies else False
        }
        
        # Add the original metrics
        transformed.update(raw_metrics)
        
        return transformed
    
    def transform_network_metrics(self, raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Transform network metrics"""
        # Extract network bandwidth (MB/s)
        network_bandwidth = raw_metrics.get('bandwidth_mbps', 0.0)
        
        # Add to history
        self._add_to_history("network", network_bandwidth)
        
        # Apply transformations
        smoothed_network = self._smooth_data(self.network_history)
        anomalies = self._detect_anomalies(self.network_history)
        rate_of_change = self._calculate_rate_of_change(self.network_history)
        statistics = self._calculate_statistics(self.network_history)
        
        # Calculate trend
        if len(self.network_history) >= 10:
            recent_trend = np.polyfit(range(len(self.network_history[-10:])), self.network_history[-10:], 1)[0]
        else:
            recent_trend = 0.0
        
        # Prepare transformed metrics
        transformed = {
            "current": network_bandwidth,
            "smoothed": float(smoothed_network[-1]) if len(smoothed_network) > 0 else network_bandwidth,
            "history": self.network_history,
            "smoothed_history": smoothed_network.tolist(),
            "anomalies": anomalies,
            "rate_of_change": rate_of_change,
            "statistics": statistics,
            "trend": float(recent_trend),
            "is_anomaly": anomalies[-1] if anomalies else False,
            # Set a minimum threshold to avoid confusing drops to zero
            "display_value": max(0.25, network_bandwidth)  # Minimum 0.25 MB/s for display
        }
        
        # Add the original metrics
        transformed.update(raw_metrics)
        
        return transformed
    
    def transform_system_metrics(self, raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Transform all system metrics"""
        transformed = {}
        
        # Transform each metric type
        if 'cpu' in raw_metrics:
            transformed['cpu'] = self.transform_cpu_metrics(raw_metrics['cpu'])
            
        if 'memory' in raw_metrics:
            transformed['memory'] = self.transform_memory_metrics(raw_metrics['memory'])
            
        if 'disk' in raw_metrics:
            transformed['disk'] = self.transform_disk_metrics(raw_metrics['disk'])
            
        if 'network' in raw_metrics:
            transformed['network'] = self.transform_network_metrics(raw_metrics['network'])
        
        # Add system-wide analysis
        transformed['system_analysis'] = self._analyze_system_state(transformed)
        
        # Add timestamp
        transformed['timestamp'] = datetime.now().isoformat()
        
        return transformed
    
    def _analyze_system_state(self, transformed_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall system state based on all metrics"""
        analysis = {
            "overall_health": "good",
            "issues": [],
            "recommendations": []
        }
        
        # Check CPU
        if 'cpu' in transformed_metrics:
            cpu = transformed_metrics['cpu']
            if cpu.get('is_anomaly', False):
                analysis["issues"].append("CPU usage anomaly detected")
                analysis["overall_health"] = "warning"
                
            if cpu.get('current', 0) > 80:
                analysis["issues"].append("High CPU usage")
                analysis["recommendations"].append("Check for resource-intensive processes")
                analysis["overall_health"] = "warning"
                
            if cpu.get('trend', 0) > 2.0:
                analysis["issues"].append("Rapidly increasing CPU usage")
                analysis["overall_health"] = "warning"
        
        # Check Memory
        if 'memory' in transformed_metrics:
            memory = transformed_metrics['memory']
            if memory.get('is_anomaly', False):
                analysis["issues"].append("Memory usage anomaly detected")
                analysis["overall_health"] = "warning"
                
            if memory.get('current', 0) > 90:
                analysis["issues"].append("High memory usage")
                analysis["recommendations"].append("Check for memory leaks")
                analysis["overall_health"] = "warning"
        
        # Check Disk
        if 'disk' in transformed_metrics:
            disk = transformed_metrics['disk']
            if disk.get('current', 0) > 90:
                analysis["issues"].append("Disk space critically low")
                analysis["recommendations"].append("Clean up unnecessary files")
                analysis["overall_health"] = "critical"
        
        # Check Network
        if 'network' in transformed_metrics:
            network = transformed_metrics['network']
            if network.get('is_anomaly', False) and network.get('current', 0) > 10:
                analysis["issues"].append("Unusual network activity")
                analysis["recommendations"].append("Check for bandwidth-intensive applications")
                analysis["overall_health"] = "warning"
        
        # Set overall health based on issues
        if len(analysis["issues"]) >= 3:
            analysis["overall_health"] = "critical"
        elif len(analysis["issues"]) >= 1:
            analysis["overall_health"] = "warning"
        
        return analysis


# Global registry of metric transformers
_metric_transformers = {}

def get_metric_transformer(name: str = "default", **kwargs) -> MetricTransformer:
    """Get or create a metric transformer by name"""
    if name not in _metric_transformers:
        _metric_transformers[name] = MetricTransformer(name=name, **kwargs)
    return _metric_transformers[name]
