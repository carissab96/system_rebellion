"""
Distributed Agents API Endpoints
=================================

FastAPI endpoints for managing and monitoring distributed agents.

Endpoints:
- GET /agents - List all agents and their status
- GET /agents/{agent_name} - Get specific agent details
- GET /agents/{agent_name}/state - Get agent state
- GET /agents/{agent_name}/decisions - Get decision history
- GET /agents/{agent_name}/metrics - Get resource metrics
- POST /agents/{agent_name}/message - Send message to agent
- GET /agents/messages/history - Get message history
- GET /system/health - Get overall system health
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import logging

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/distributed-agents", tags=["distributed-agents"])


# Pydantic models for request/response
class SendMessageRequest(BaseModel):
    """Request to send a message to an agent"""
    message_type: str
    payload: Dict[str, Any]
    priority: str = "normal"
    to_agent: Optional[str] = None  # None = broadcast


class AgentCommandRequest(BaseModel):
    """Request to send a command to an agent"""
    command: str  # "start", "stop", "restart", "set_threshold"
    parameters: Optional[Dict[str, Any]] = None


# Global agent registry (will be populated by agent manager)
_agent_registry: Dict[str, Any] = {}


def register_agent(agent_name: str, agent_instance: Any):
    """
    Register an agent instance for API access.
    
    Call this from your agent initialization code.
    """
    _agent_registry[agent_name] = agent_instance
    logger.info(f"Registered agent for API: {agent_name}")


def get_agent(agent_name: str):
    """Get agent instance by name"""
    if agent_name not in _agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    return _agent_registry[agent_name]


@router.get("/agents")
async def list_agents():
    """
    List all registered agents and their current status.
    
    Returns:
        List of agent summaries
    """
    agents = []
    
    for agent_name, agent in _agent_registry.items():
        try:
            status = agent.get_agent_status()
            agents.append({
                "agent_name": agent_name,
                "agent_role": status.get("agent_role"),
                "health": status.get("health"),
                "is_active": status.get("is_active"),
                "uptime_seconds": status.get("uptime_seconds"),
                "total_decisions": status.get("total_decisions")
            })
        except Exception as e:
            logger.error(f"Error getting status for {agent_name}: {e}")
            agents.append({
                "agent_name": agent_name,
                "error": str(e)
            })
    
    return {
        "total_agents": len(agents),
        "agents": agents,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/agents/{agent_name}")
async def get_agent_details(agent_name: str):
    """
    Get detailed information about a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Complete agent status and configuration
    """
    agent = get_agent(agent_name)
    
    try:
        status = agent.get_agent_status()
        return {
            "agent_name": agent_name,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting details for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}/state")
async def get_agent_state(agent_name: str):
    """
    Get the persisted state of an agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent state from Redis
    """
    agent = get_agent(agent_name)
    
    try:
        state = agent.comm_hub.get_state()
        if not state:
            raise HTTPException(status_code=404, detail="Agent state not found")
        
        return {
            "agent_name": agent_name,
            "state": {
                "health": state.health.value,
                "is_active": state.is_active,
                "started_at": state.started_at,
                "last_heartbeat": state.last_heartbeat,
                "restart_count": state.restart_count,
                "uptime_seconds": state.calculate_uptime(),
                "total_decisions": state.total_decisions,
                "total_messages_sent": state.total_messages_sent,
                "total_messages_received": state.total_messages_received,
                "error_count": state.error_count,
                "personality_traits": state.personality_traits,
                "custom_state": state.custom_state
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting state for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}/decisions")
async def get_agent_decisions(
    agent_name: str,
    limit: int = Query(default=10, ge=1, le=100),
    since_hours: Optional[int] = Query(default=None, ge=1, le=168)
):
    """
    Get decision history for an agent.
    
    Args:
        agent_name: Name of the agent
        limit: Maximum number of decisions to return
        since_hours: Optional filter for decisions in last N hours
        
    Returns:
        List of recent decisions
    """
    agent = get_agent(agent_name)
    
    try:
        since = None
        if since_hours:
            since = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        
        decisions = await agent.comm_hub.state_manager.get_recent_decisions(
            count=limit,
            since=since
        )
        
        return {
            "agent_name": agent_name,
            "total_decisions": len(decisions),
            "decisions": [
                {
                    "decision_id": d.decision_id,
                    "timestamp": d.timestamp,
                    "decision_type": d.decision_type,
                    "confidence": d.confidence,
                    "was_successful": d.was_successful,
                    "input_data": d.input_data,
                    "output_data": d.output_data
                }
                for d in decisions
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting decisions for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}/metrics")
async def get_agent_metrics(agent_name: str):
    """
    Get current resource metrics for an agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Current resource metrics
    """
    agent = get_agent(agent_name)
    
    try:
        metrics = agent.get_resource_metrics()
        
        if not metrics:
            return {
                "agent_name": agent_name,
                "metrics": None,
                "message": "No metrics available yet",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "agent_name": agent_name,
            "metrics": {
                "timestamp": metrics.timestamp,
                "hostname": metrics.hostname,
                "cpu": {
                    "percent": metrics.cpu_percent,
                    "count": metrics.cpu_count,
                    "per_core": metrics.cpu_per_core,
                    "load_average": metrics.load_average
                },
                "memory": {
                    "total_gb": metrics.memory_total / (1024**3),
                    "used_gb": metrics.memory_used / (1024**3),
                    "available_gb": metrics.memory_available / (1024**3),
                    "percent": metrics.memory_percent
                },
                "disk": {
                    "total_gb": metrics.disk_total / (1024**3),
                    "used_gb": metrics.disk_used / (1024**3),
                    "free_gb": metrics.disk_free / (1024**3),
                    "percent": metrics.disk_percent
                },
                "network": {
                    "bytes_sent": metrics.network_bytes_sent,
                    "bytes_recv": metrics.network_bytes_recv,
                    "packets_sent": metrics.network_packets_sent,
                    "packets_recv": metrics.network_packets_recv
                }
            },
            "alert_history": agent.resource_monitor.get_alert_history(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/message")
async def send_message_to_agent(agent_name: str, request: SendMessageRequest):
    """
    Send a message to a specific agent or broadcast.
    
    Args:
        agent_name: Name of the sending agent (or "system")
        request: Message details
        
    Returns:
        Success status
    """
    from app.ai_agents.distributed.message_protocol import MessageType, Priority
    
    # Validate message type
    try:
        msg_type = MessageType(request.message_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid message type: {request.message_type}"
        )
    
    # Validate priority
    try:
        priority = Priority[request.priority.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {request.priority}"
        )
    
    # Get agent or use system sender
    if agent_name in _agent_registry:
        agent = _agent_registry[agent_name]
        
        try:
            if request.to_agent:
                success = await agent.send_message_to_agent(
                    request.to_agent,
                    msg_type,
                    request.payload,
                    priority
                )
            else:
                success = await agent.broadcast_message(
                    msg_type,
                    request.payload,
                    priority
                )
            
            return {
                "success": success,
                "from_agent": agent_name,
                "to_agent": request.to_agent or "broadcast",
                "message_type": request.message_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")


@router.get("/system/health")
async def get_system_health():
    """
    Get overall system health across all agents.
    
    Returns:
        System-wide health summary
    """
    health_summary = {
        "healthy": 0,
        "degraded": 0,
        "critical": 0,
        "offline": 0
    }
    
    agent_details = []
    
    for agent_name, agent in _agent_registry.items():
        try:
            status = agent.get_agent_status()
            health = status.get("health", "unknown")
            
            if health in health_summary:
                health_summary[health] += 1
            
            agent_details.append({
                "agent_name": agent_name,
                "health": health,
                "uptime_seconds": status.get("uptime_seconds", 0),
                "error_count": status.get("error_count", 0)
            })
        except Exception as e:
            logger.error(f"Error checking health for {agent_name}: {e}")
            health_summary["offline"] += 1
            agent_details.append({
                "agent_name": agent_name,
                "health": "offline",
                "error": str(e)
            })
    
    overall_health = "healthy"
    if health_summary["critical"] > 0:
        overall_health = "critical"
    elif health_summary["degraded"] > 0:
        overall_health = "degraded"
    elif health_summary["offline"] > 0:
        overall_health = "degraded"
    
    return {
        "overall_health": overall_health,
        "total_agents": len(_agent_registry),
        "health_summary": health_summary,
        "agents": agent_details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/messages/history")
async def get_message_history(
    date: Optional[str] = Query(default=None, description="Date in YYYY-MM-DD format"),
    limit: int = Query(default=50, ge=1, le=500)
):
    """
    Get message history from Redis archive.
    
    Args:
        date: Optional date filter (defaults to today)
        limit: Maximum messages to return
        
    Returns:
        List of archived messages
    """
    from app.ai_agents.distributed.message_protocol import RedisKeys
    from app.core.redis import get_redis_client
    
    try:
        redis = await get_redis_client()
        
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        key = RedisKeys.message_archive(date)
        messages = await redis.lrange(key, 0, limit - 1)
        
        return {
            "date": date,
            "total_messages": len(messages),
            "messages": [eval(msg) for msg in messages],  # Convert JSON strings
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting message history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
