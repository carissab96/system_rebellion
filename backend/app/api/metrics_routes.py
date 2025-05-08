from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.metrics_service import MetricsService
from app.services.system_metrics_service import SystemMetricsService
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
    try:
        # Use the centralized metrics service
        metrics_service = await SystemMetricsService.get_instance()
        metrics = await metrics_service.get_metrics()
        
        # Get network details with proper error handling
        network_sent = 0
        network_recv = 0
        
        # Handle different possible structures for network metrics
        if "additional" in metrics and "network_details" in metrics["additional"]:
            network_details = metrics["additional"]["network_details"]
            if isinstance(network_details, dict):
                network_sent = network_details.get("bytes_sent", 0)
                network_recv = network_details.get("bytes_recv", 0)
        
        # If we couldn't get network details from the metrics service, use psutil directly
        if network_sent == 0 and network_recv == 0:
            net_io = psutil.net_io_counters()
            network_sent = net_io.bytes_sent
            network_recv = net_io.bytes_recv
        
        # Format the response to match the existing API structure
        return {
            "cpu_usage": metrics.get("cpu_usage", 0),
            "memory_usage": metrics.get("memory_usage", 0),
            "disk_usage": metrics.get("disk_usage", 0),
            "network_io": {
                "sent": network_sent,
                "recv": network_recv
            },
            "process_count": metrics.get("process_count", 0),
            "timestamp": metrics.get("timestamp", datetime.now(timezone.utc).isoformat())
        }
    except Exception as e:
        print(f"Error getting system metrics: {e}")
        # Return fallback metrics
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": {
                "sent": psutil.net_io_counters().bytes_sent,
                "recv": psutil.net_io_counters().bytes_recv
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