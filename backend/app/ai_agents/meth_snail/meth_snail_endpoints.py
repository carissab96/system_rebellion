"""
Meth Snail API endpoints for jitter level and optimization metrics.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.meth_snail_model import MethSnailJitterLevels, MethSnailOptimizationStats

# Enums and Models for API
class TimeRange(str, Enum):
    LAST_HOUR = "1h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"

class JitterLevelResponse(BaseModel):
    """Response model for jitter level data"""
    timestamp: datetime
    current_jitter_level: float = Field(..., ge=0.0, le=1.0)
    peak_jitter_level: float = Field(..., ge=0.0, le=1.0)
    baseline_jitter_level: float = Field(..., ge=0.0, le=1.0)
    caffeine_level_mg: float = Field(..., ge=0.0)
    is_decaffeinated: bool
    shell_spin_probability: float = Field(..., ge=0.0, le=1.0)
    optimization_effectiveness: Optional[float] = Field(None, ge=0.0, le=1.0)
    focus_level: float = Field(..., ge=0.0, le=1.0)
    hypercaffeinated: bool
    requires_stick_intervention: bool
    vic20_mediation_requested: bool
    energy_source: Optional[str]
    jitter_trend: Optional[str]
    raw_jitter_data: Optional[Dict[str, Any]]

class OptimizationMetricsResponse(BaseModel):
    """Response model for optimization metrics"""
    timestamp: datetime
    optimization_success: bool
    shell_spins_executed: int = Field(..., ge=0)
    cpu_usage_before: Optional[float]
    cpu_usage_after: Optional[float]
    memory_usage_before: Optional[float]
    memory_usage_after: Optional[float]
    energy_drink_level: Optional[float]
    raw_metrics: Optional[Dict[str, Any]]

class JitterLevelAggregate(BaseModel):
    """Response model for aggregated jitter level statistics"""
    time_range: TimeRange
    start_time: datetime
    end_time: datetime
    avg_jitter: float
    max_jitter: float
    min_jitter: float
    avg_caffeine: float
    sample_count: int

router = APIRouter()

@router.get("/jitter-levels", response_model=List[JitterLevelResponse])
async def get_jitter_levels(
    db: AsyncSession = Depends(get_db),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
) -> List[JitterLevelResponse]:
    """
    Get historical jitter level data with optional time filtering.
    
    Args:
        start_time: Start time for filtering records (inclusive)
        end_time: End time for filtering records (inclusive)
        limit: Maximum number of records to return (1-1000)
        
    Returns:
        List of jitter level records
    """
    from sqlalchemy import select, and_
    from sqlalchemy.orm import selectinload
    
    try:
        query = select(MethSnailJitterLevels).order_by(MethSnailJitterLevels.timestamp.desc())
        
        # Apply time filters if provided
        conditions = []
        if start_time:
            conditions.append(MethSnailJitterLevels.timestamp >= start_time)
        if end_time:
            conditions.append(MethSnailJitterLevels.timestamp <= end_time)
            
        if conditions:
            query = query.where(and_(*conditions))
            
        # Apply limit
        query = query.limit(limit)
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        return [
            JitterLevelResponse(
                timestamp=record.timestamp,
                current_jitter_level=record.current_jitter_level,
                peak_jitter_level=record.peak_jitter_level,
                baseline_jitter_level=record.baseline_jitter_level,
                caffeine_level_mg=record.caffeine_level_mg,
                is_decaffeinated=record.is_decaffeinated,
                shell_spin_probability=record.shell_spin_probability,
                optimization_effectiveness=record.optimization_effectiveness,
                focus_level=record.focus_level,
                hypercaffeinated=record.hypercaffeinated,
                requires_stick_intervention=record.requires_stick_intervention,
                vic20_mediation_requested=record.vic20_mediation_requested,
                energy_source=record.energy_source,
                jitter_trend=record.jitter_trend,
                raw_jitter_data=record.raw_jitter_data
            )
            for record in records
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving jitter levels: {str(e)}")

@router.get("/optimization-metrics", response_model=List[OptimizationMetricsResponse])
async def get_optimization_metrics(
    db: AsyncSession = Depends(get_db),
    time_range: TimeRange = TimeRange.LAST_24_HOURS,
    limit: int = Query(100, ge=1, le=1000),
) -> List[OptimizationMetricsResponse]:
    """
    Get optimization metrics with optional time range filtering.
    
    Args:
        time_range: Time range for filtering records
        limit: Maximum number of records to return (1-1000)
        
    Returns:
        List of optimization metrics records
    """
    from sqlalchemy import select, func
    from datetime import datetime, timedelta
    
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        if time_range == TimeRange.LAST_HOUR:
            start_time = end_time - timedelta(hours=1)
        elif time_range == TimeRange.LAST_24_HOURS:
            start_time = end_time - timedelta(days=1)
        elif time_range == TimeRange.LAST_7_DAYS:
            start_time = end_time - timedelta(days=7)
        else:  # LAST_30_DAYS
            start_time = end_time - timedelta(days=30)
        
        # Build and execute query
        query = (
            select(MethSnailOptimizationStats)
            .where(MethSnailOptimizationStats.timestamp.between(start_time, end_time))
            .order_by(MethSnailOptimizationStats.timestamp.desc())
            .limit(limit)
        )
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        return [
            OptimizationMetricsResponse(
                timestamp=record.timestamp,
                optimization_success=record.optimization_success,
                shell_spins_executed=record.shell_spins_executed,
                cpu_usage_before=record.cpu_usage_before,
                cpu_usage_after=record.cpu_usage_after,
                memory_usage_before=record.memory_usage_before,
                memory_usage_after=record.memory_usage_after,
                energy_drink_level=record.energy_drink_level,
                raw_metrics=record.raw_metrics
            )
            for record in records
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving optimization metrics: {str(e)}")

@router.get("/jitter-aggregates", response_model=JitterLevelAggregate)
async def get_jitter_aggregates(
    db: AsyncSession = Depends(get_db),
    time_range: TimeRange = TimeRange.LAST_24_HOURS,
) -> JitterLevelAggregate:
    """
    Get aggregated jitter level statistics for the specified time range.
    
    Args:
        time_range: Time range for aggregating data
        
    Returns:
        Aggregated jitter level statistics
    """
    from sqlalchemy import select, func
    from datetime import datetime, timedelta
    
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        if time_range == TimeRange.LAST_HOUR:
            start_time = end_time - timedelta(hours=1)
        elif time_range == TimeRange.LAST_24_HOURS:
            start_time = end_time - timedelta(days=1)
        elif time_range == TimeRange.LAST_7_DAYS:
            start_time = end_time - timedelta(days=7)
        else:  # LAST_30_DAYS
            start_time = end_time - timedelta(days=30)
        
        # Build and execute aggregation query
        query = select(
            func.avg(MethSnailJitterLevels.current_jitter_level).label("avg_jitter"),
            func.max(MethSnailJitterLevels.current_jitter_level).label("max_jitter"),
            func.min(MethSnailJitterLevels.current_jitter_level).label("min_jitter"),
            func.avg(MethSnailJitterLevels.caffeine_level_mg).label("avg_caffeine"),
            func.count(MethSnailJitterLevels.id).label("sample_count")
        ).where(
            MethSnailJitterLevels.timestamp.between(start_time, end_time)
        )
        
        result = await db.execute(query)
        stats = result.first()
        
        return JitterLevelAggregate(
            time_range=time_range,
            start_time=start_time,
            end_time=end_time,
            avg_jitter=stats.avg_jitter or 0,
            max_jitter=stats.max_jitter or 0,
            min_jitter=stats.min_jitter or 0,
            avg_caffeine=stats.avg_caffeine or 0,
            sample_count=stats.sample_count or 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating jitter aggregates: {str(e)}")
