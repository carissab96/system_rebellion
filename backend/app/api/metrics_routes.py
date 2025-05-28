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
from app.services.system_metrics_service import SystemMetricsService

router = APIRouter(tags=["metrics"])

@router.get("/system", response_model=dict)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Public endpoint for system metrics that doesn't require authentication
    """
    try:
        # Direct psutil implementation for all metrics
        # Get basic system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        swap = psutil.swap_memory()
        
        # Get CPU details
        cpu_freq = psutil.cpu_freq()
        cpu_count_logical = psutil.cpu_count()
        cpu_count_physical = psutil.cpu_count(logical=False)
        
        # Get per-core CPU usage
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_cores = [{'id': i, 'usage': usage} for i, usage in enumerate(per_cpu)]
        
        # Get top CPU and memory processes
        top_processes = []
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
                          key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:5]:
            try:
                top_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'] or 0,
                    'memory_percent': proc.info['memory_percent'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Get disk partitions
        partitions = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'fstype': part.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except (PermissionError, OSError):
                continue
        
        # Get network interfaces
        interfaces = []
        for name, stats in psutil.net_if_stats().items():
            try:
                addrs = psutil.net_if_addrs().get(name, [])
                address = next((addr.address for addr in addrs if addr.family == socket.AF_INET), None)
                interfaces.append({
                    'name': name,
                    'address': address,
                    'isup': stats.isup,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                })
            except (KeyError, StopIteration):
                continue
        
        # Format the response with directly collected metrics
        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "network_io": {
                "sent": net_io.bytes_sent,
                "recv": net_io.bytes_recv,
                "sent_rate": 0,  # We don't have rate data without historical values
                "recv_rate": 0   # We don't have rate data without historical values
            },
            "process_count": len(psutil.pids()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "cpu": {
                    "percent": cpu_percent,
                    "cores": cpu_cores,
                    "temperature": None,  # Would need platform-specific code
                    "frequency": cpu_freq.current if cpu_freq else None,
                    "core_count": cpu_count_physical,
                    "thread_count": cpu_count_logical,
                    "top_processes": top_processes,
                    "model": "CPU",  # Would need platform-specific code
                    "vendor": "Vendor"  # Would need platform-specific code
                },
                "memory": {
                    "percent": memory.percent,
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "free": memory.free,
                    "buffer": getattr(memory, 'buffers', 0),
                    "cache": getattr(memory, 'cached', 0),
                    "swap_percent": swap.percent,
                    "swap_total": swap.total,
                    "swap_used": swap.used,
                    "swap_free": swap.free,
                    "top_processes": top_processes
                },
                "disk": {
                    "percent": disk.percent,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "available": disk.free,  # Same as free for compatibility
                    "partitions": partitions,
                    "read_rate": 0,  # Would need historical data
                    "write_rate": 0   # Would need historical data
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "interfaces": interfaces,
                    "rate_mbps": 0,  # Would need historical data
                    "connection_quality": {
                        "average_latency": 0,
                        "packet_loss_percent": 0,
                        "connection_stability": 0,
                        "jitter": 0,
                        "gateway_latency": 0,
                        "dns_latency": 0,
                        "internet_latency": 0
                    }
                }
            }
        }
    except Exception as e:
        # Log the error and return a minimal response
        print(f"Error getting system metrics: {str(e)}")
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "network_io": {"sent": 0, "recv": 0},
            "process_count": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "details": {
                "cpu": {"percent": 0, "cores": [], "temperature": None, "frequency": None},
                "memory": {"percent": 0, "total": 0, "available": 0, "used": 0, "free": 0},
                "disk": {"percent": 0, "total": 0, "used": 0, "free": 0, "available": 0},
                "network": {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}
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
        metrics_repo = MetricsRepository()
        return await metrics_repo.create_metric(db, metric_data)
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
    metrics_repo = MetricsRepository()
    return await metrics_repo.get_user_metrics(
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
    metrics_repo = MetricsRepository()
    metric = await metrics_repo.get_metric_by_id(db, metric_id)
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
    metrics_repo = MetricsRepository()
    db_metric = await metrics_repo.get_metric_by_id(db, metric_id)
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metric not found")
        
    # Verify the current user owns this metric
    if str(db_metric.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this metric")
        
    return await metrics_repo.update_metric(db, metric_id, metric)

@router.delete("/{metric_id}")
async def delete_metric(
    metric_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    The Meth Snail's Metric Deletion Endpoint
    """
    metrics_repo = MetricsRepository()
    db_metric = await metrics_repo.get_metric_by_id(db, metric_id)
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # Verify the current user owns this metric
    if str(db_metric.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this metric")
    
    deleted = await metrics_repo.delete_metric(db, metric_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete metric")
    return {"ok": True}
