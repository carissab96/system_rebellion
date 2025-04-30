from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.metrics_service import MetricsService
from app.schemas.metrics import MetricCreate, MetricResponse, MetricUpdate
from app.core.security import get_current_user
import uuid
import psutil
from datetime import datetime, timezone

router = APIRouter(tags=["metrics"])

@router.get("/system", response_model=dict)
async def get_system_metrics():
    """
    Public endpoint for system metrics that doesn't require authentication
    """
    # Get system metrics using psutil
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    network_io = psutil.net_io_counters()
    
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory.percent,
        "disk_usage": disk.percent,
        "network_io": {
            "sent": network_io.bytes_sent,
            "recv": network_io.bytes_recv
        },
        "process_count": len(psutil.pids()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }   

@router.post("/", response_model=MetricResponse)
async def create_metric(
    metric: MetricCreate, 
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sir Hawkington's Metric Creation Endpoint
    """
    metric.user_id = current_user['id']
    return await MetricsService.create_metric(db, metric)

@router.get("/", response_model=list[MetricResponse])
async def read_user_metrics(
    skip: int = 0, 
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    The Meth Snail's Metric Retrieval Endpoint
    """
    return await MetricsService.get_user_metrics(
        db, current_user['id'], skip, limit
    )

@router.get("/{metric_id}", response_model=MetricResponse)
async def read_metric(
    metric_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quantum Precision Metric Lookup
    """
    metric = await MetricsService.get_metric_by_id(db, metric_id)
    if not metric or metric.user_id != str(current_user['id']):
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric

@router.put("/{metric_id}", response_model=MetricResponse)
async def update_metric(
    metric_id: uuid.UUID,
    metric: MetricUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sir Hawkington's Metric Update Endpoint
    """
    existing_metric = await MetricsService.get_metric_by_id(db, metric_id)
    if not existing_metric or existing_metric.user_id != str(current_user['id']):
        raise HTTPException(status_code=404, detail="Metric not found")
    
    return await MetricsService.update_metric(db, metric_id, metric)

@router.delete("/{metric_id}")
async def delete_metric(
    metric_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    The Meth Snail's Metric Deletion Endpoint
    """
    existing_metric = await MetricsService.get_metric_by_id(db, metric_id)
    if not existing_metric or existing_metric.user_id != str(current_user['id']):
        raise HTTPException(status_code=404, detail="Metric not found")
    
    deleted = await MetricsService.delete_metric(db, metric_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete metric")
    
    return {"message": "Metric deleted successfully"}