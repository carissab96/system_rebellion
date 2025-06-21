from datetime import datetime, timezone
from typing import Any, Dict
import uuid
import socket

import psutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.metrics import MetricCreate, MetricResponse, MetricUpdate
from app.services.metrics_repository import MetricsRepository
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService

router = APIRouter(tags=["metrics"])

@router.get("/system", response_model=Dict[str, Any])
async def get_metrics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get real-time system metrics using direct psutil implementation.
    No fallbacks, no sample data, pure metrics from the actual system.
    """
    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "cpu": {
            "percent": psutil.cpu_percent(interval=0.1),
            "cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "per_core": psutil.cpu_percent(interval=0.1, percpu=True)
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        },
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv,
            "packets_sent": psutil.net_io_counters().packets_sent,
            "packets_recv": psutil.net_io_counters().packets_recv
        }
    }
# return metrics;

@router.post("/", response_model=MetricResponse)
async def create_metric(
    metric: MetricCreate, 
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sir Hawkington's Metric Creation Endpoint
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Prepare metric data with user ID
        metric_data = metric.model_dump()
        metric_data["user_id"] = current_user["id"]
        
        # Create metric using repository pattern
        metrics_repo = MetricsRepository()
        result = await metrics_repo.create_metric(db, metric_data)
        
        # Ensure creation was successful
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create metric")
            
        return result
    except ValueError as ve:
        # Handle validation errors
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Handle other errors
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/", response_model=MetricResponse)
async def create_metric(
    metric: MetricCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sir Hawkington's Metric endpoint for creating new metrics
    
    Creates a new system metric record associated with the current user.
    """
    if not current_user:
        # Ensure user is authenticated before proceeding
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Convert Pydantic model to dict and add user ID from authenticated user
        metric_data = MetricCreate(**metric.model_dump(), user_id=current_user["id"])
            
        # Use repository pattern to handle database operations
        metrics_repo = MetricsRepository()
        result = await metrics_repo.create_metric(db, metric_data)
        
        # Return the created metric with status code 201 (Created)
        return result
    except ValueError as ve:
        # Handle validation errors with appropriate status code
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Ensure transaction is rolled back on error
        await db.rollback()
        # Log the error for debugging
        logger.error(f"Error creating metric: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create metric")

@router.get("/", response_model=list[MetricResponse])
async def read_user_metrics(
    skip: int = 0, 
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    The Meth Snail's Metric Retrieval Endpoint
    
    Retrieves a paginated list of metrics for the current user.
    Parameters:
    - skip: Number of records to skip (pagination offset)
    - limit: Maximum number of records to return
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    try:
        # Initialize repository and fetch metrics for current user
        metrics_repo = MetricsRepository()
        metrics = await metrics_repo.get_user_metrics(
            db, uuid.UUID(current_user['id']), skip, limit
        )
        
        # Return empty list instead of None if no metrics found
        return metrics or []
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@router.get("/{metric_id}", response_model=MetricResponse)
async def read_metric(
    metric_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quantum Precision Metric Lookup
    
    Retrieves a specific metric by ID, with authorization check.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    try:
        # Fetch the requested metric
        metrics_repo = MetricsRepository()
        metric = await metrics_repo.get_metric_by_id(db, metric_id)
        
        # Check if metric exists
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        # Security check: verify the current user owns this metric
        if str(metric.user_id) != current_user["id"]:
            logger.warning(f"Unauthorized access attempt to metric {metric_id} by user {current_user['id']}")
            raise HTTPException(status_code=403, detail="Not authorized to access this metric")
            
        return metric
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Error retrieving metric {metric_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metric")

@router.put("/{metric_id}", response_model=MetricResponse)
async def update_metric(
    metric_id: uuid.UUID,
    metric: MetricUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sir Hawkington's Metric Update Endpoint
    
    Updates an existing metric after performing authorization checks.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    try:
        metrics_repo = MetricsRepository()
        
        # First check if metric exists and user has permission
        db_metric = await metrics_repo.get_metric_by_id(db, metric_id)
        if not db_metric:
            raise HTTPException(status_code=404, detail="Metric not found")
            
        # Security check: verify the current user owns this metric
        if str(db_metric.user_id) != current_user["id"]:
            logger.warning(f"Unauthorized update attempt to metric {metric_id} by user {current_user['id']}")
            raise HTTPException(status_code=403, detail="Not authorized to update this metric")
        
        # Perform the update operation
        updated_metric = await metrics_repo.update_metric(db, metric_id, metric)
        if not updated_metric:
            raise HTTPException(status_code=500, detail="Failed to update metric")
            
        return updated_metric
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Ensure transaction is rolled back on error
        await db.rollback()
        logger.error(f"Error updating metric {metric_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update metric")

@router.delete("/{metric_id}", status_code=204)
async def delete_metric(
    metric_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    The Meth Snail's Metric Deletion Endpoint
    
    Deletes a specific metric after performing authorization checks.
    Returns 204 No Content on success.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    try:
        metrics_repo = MetricsRepository()
        
        # First check if metric exists and user has permission
        db_metric = await metrics_repo.get_metric_by_id(db, metric_id)
        if not db_metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        # Security check: verify the current user owns this metric
        if str(db_metric.user_id) != current_user["id"]:
            logger.warning(f"Unauthorized deletion attempt of metric {metric_id} by user {current_user['id']}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this metric")
        
        # Perform the deletion
        deleted = await metrics_repo.delete_metric(db, metric_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete metric")
            
        # Return no content on successful deletion
        return None
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Ensure transaction is rolled back on error
        await db.rollback()
        logger.error(f"Error deleting metric {metric_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete metric")
