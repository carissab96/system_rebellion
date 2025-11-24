from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum

class MetricType(str, Enum):
    """Types of system metrics"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    PROCESS_COUNT = "process_count"
    TEMPERATURE = "temperature"
    BATTERY_LEVEL = "battery_level"
    POWER_CONSUMPTION = "power_consumption"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    CUSTOM = "custom"

class MetricUnit(str, Enum):
    """Standard units for metrics"""
    PERCENT = "%"
    BYTES = "bytes"
    KILOBYTES = "KB"
    MEGABYTES = "MB"
    GIGABYTES = "GB"
    BITS_PER_SECOND = "bps"
    BYTES_PER_SECOND = "B/s"
    KILOBYTES_PER_SECOND = "KB/s"
    MEGABYTES_PER_SECOND = "MB/s"
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    COUNT = "count"
    MILLISECONDS = "ms"
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    WATTS = "W"
    MILLIWATTS = "mW"
    NONE = ""  # For unitless metrics

class SystemMetrics(BaseModel):
    """Base model for system metrics"""
    metric_type: MetricType = Field(..., description="Type of the metric")
    value: Union[float, int, Dict[str, float], List[float]] = Field(
        ...,
        description="Metric value(s). Can be a single value, a list of values, or a dictionary of named values."
    )
    unit: MetricUnit = Field(
        MetricUnit.NONE,
        description="Unit of measurement for the metric"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the metric was recorded"
    )
    source: str = Field(
        "system",
        description="Source of the metric (e.g., 'system', 'agent:name', 'service:name')"
    )
    tags: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata tags for the metric"
    )
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        """Validate that the value is a number, list of numbers, or dict of numbers"""
        if isinstance(v, (int, float)):
            return v
        elif isinstance(v, list):
            if not all(isinstance(x, (int, float)) for x in v):
                raise ValueError("All elements in value list must be numbers")
            return v
        elif isinstance(v, dict):
            if not all(isinstance(x, (int, float)) for x in v.values()):
                raise ValueError("All values in value dict must be numbers")
            return v
        raise ValueError("Value must be a number, list of numbers, or dict of numbers")

class SystemMetricsCreate(SystemMetrics):
    """Schema for creating a new system metric"""
    pass

class SystemMetricsUpdate(SystemMetrics):
    """Schema for updating an existing system metric"""
    value: Optional[Union[float, int, Dict[str, float], List[float]]] = None
    unit: Optional[MetricUnit] = None
    tags: Optional[Dict[str, str]] = None

class SystemMetricsInDB(SystemMetrics):
    """Schema for system metric as stored in the database"""
    id: int = Field(..., description="Database primary key")
    user_id: str = Field(..., description="ID of the user this metric belongs to")
    created_at: datetime = Field(..., description="When the metric was created")
    updated_at: datetime = Field(..., description="When the metric was last updated")
    
    model_config = ConfigDict(from_attributes=True)

class SystemMetricsResponse(SystemMetricsInDB):
    """Schema for system metric as returned in API responses"""
    pass

class SystemMetricsQuery(BaseModel):
    """Query parameters for retrieving system metrics"""
    start_time: Optional[datetime] = Field(
        None,
        description="Start time for the query (inclusive)"
    )
    end_time: Optional[datetime] = Field(
        None,
        description="End time for the query (inclusive)"
    )
    metric_types: Optional[List[MetricType]] = Field(
        None,
        description="Filter by metric type(s)"
    )
    sources: Optional[List[str]] = Field(
        None,
        description="Filter by source(s)"
    )
    tags: Optional[Dict[str, str]] = Field(
        None,
        description="Filter by tag key-value pairs"
    )
    limit: int = Field(
        1000,
        ge=1,
        le=10000,
        description="Maximum number of metrics to return"
    )
    aggregate: Optional[str] = Field(
        None,
        description="Aggregation function to apply (e.g., 'avg', 'sum', 'min', 'max', 'count')"
    )
    interval: Optional[str] = Field(
        None,
        description="Time interval for grouping results (e.g., '1h', '1d')"
    )
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

class SystemMetricsSummary(BaseModel):
    """Summary statistics for system metrics"""
    count: int = Field(..., description="Number of metrics")
    avg: Optional[float] = Field(None, description="Average value")
    min: Optional[float] = Field(None, description="Minimum value")
    max: Optional[float] = Field(None, description="Maximum value")
    sum: Optional[float] = Field(None, description="Sum of values")
    start_time: Optional[datetime] = Field(None, description="Earliest timestamp")
    end_time: Optional[datetime] = Field(None, description="Latest timestamp")
