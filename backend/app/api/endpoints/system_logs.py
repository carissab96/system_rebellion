from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any

from app.api.deps import get_current_user
from app.models.user import User
from app.services.system_log_service import SystemLogService

router = APIRouter()

@router.get("/")
async def get_system_logs(
    limit: int = Query(100, ge=1, le=1000),
    source: Optional[str] = None,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get system logs with optional filtering.
    
    Returns recent system logs, including authentication attempts, command outputs,
    and system tuning events.
    """
    log_service = await SystemLogService.get_instance()
    logs = log_service.get_logs(limit=limit, source=source, level=level)
    
    return {
        "logs": logs,
        "total": len(logs),
        "has_more": len(logs) == limit
    }

@router.delete("/")
async def clear_system_logs(
    current_user: User = Depends(get_current_user)
):
    """
    Clear all system logs.
    
    This will remove all stored logs from the system.
    """
    # Check if user is admin (you may want to add this check)
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Not authorized")
    
    log_service = await SystemLogService.get_instance()
    log_service.clear_logs()
    
    return {"message": "Logs cleared successfully"}
