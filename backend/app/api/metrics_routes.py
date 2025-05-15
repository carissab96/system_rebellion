from datetime import datetime, timezone
from typing import Any, Dict
import uuid

import psutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core import async_session
from app.core.security import get_current_user
from app.schemas.metrics import MetricCreate, MetricResponse, MetricUpdate
from app.services.metrics.metrics_service import MetricsService as MetricsOrchestrator
from app.services.metrics_service import MetricsService  # For database operations
from app.services.system_metrics_service import SystemMetricsService

router = APIRouter(tags=["metrics"])

@router.get("/system", response_model=dict)
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """
    Public endpoint for system metrics that doesn't require authentication
    """
    try:
        # Use the centralized metrics service with the database session
        metrics_service = await SystemMetricsService.get_instance(db)
        metrics = await metrics_service.get_metrics(force_refresh=True, db=db)
        
        # Get network details from the metrics
        network = metrics.get('network', {})
        network_sent = network.get('bytes_sent', 0)
        network_recv = network.get('bytes_recv', 0)
        
        # If we couldn't get network details, try psutil directly
        if not network_sent and not network_recv:
            net_io = psutil.net_io_counters()
            network_sent = net_io.bytes_sent
            network_recv = net_io.bytes_recv
        
        # Format the response to match the existing API structure
        return {
            "cpu_usage": metrics.get("cpu", {}).get("percent", 0),
            "memory_usage": metrics.get("memory", {}).get("percent", 0),
            "disk_usage": metrics.get("disk", {}).get("percent", 0),
            "network_io": {
                "sent": network_sent,
                "recv": network_recv
            },
            "process_count": metrics.get("process_count", 0),
            "timestamp": metrics.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "details": metrics  # Include all the detailed metrics
        }
    except Exception as e:
        print(f"Error getting system metrics: {e}")
        # Return fallback metrics with the new structure
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "network_io": {
                "sent": net_io.bytes_sent,
                "recv": net_io.bytes_recv
            },
            "process_count": len(psutil.pids()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": psutil.cpu_percent(),
                    "cores": psutil.cpu_count(logical=True),
                    "physical_cores": psutil.cpu_count(logical=False)
                },
                "memory": {
                    "percent": memory.percent,
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "percent": disk.percent,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "interfaces": {}
                },
                "process_count": len(psutil.pids()),
                "additional": {
                    "error": str(e)
                }
            }
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
    try:
        # Set the user ID from the current user
        metric_data = metric.model_dump()
        metric_data["user_id"] = current_user["id"]
        return await MetricsService.create_metric(db, metric_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # Verify the current user owns this metric
    if str(metric.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this metric")
        
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
    db_metric = await MetricsService.get_metric_by_id(db, metric_id)
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metric not found")
        
    # Verify the current user owns this metric
    if str(db_metric.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this metric")
        
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
    db_metric = await MetricsService.get_metric_by_id(db, metric_id)
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # Verify the current user owns this metric
    if str(db_metric.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this metric")
    
    deleted = await MetricsService.delete_metric(db, metric_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete metric")
    return {"ok": True}