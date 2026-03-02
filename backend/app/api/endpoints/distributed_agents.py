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


async def get_consciousness_status() -> Dict[str, Any]:
    """
    Get consciousness checkpoint status across all agents.
    
    Week 5 Task 5.2: Consciousness checkpoint visualization data
    
    Returns:
        Consciousness checkpoint summary
    """
    try:
        from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
        
        manager = get_distributed_manager()
        
        if not manager or not manager._initialized:
            return {
                "status": "not_initialized",
                "message": "Distributed agent manager not initialized"
            }
        
        # Check if we have distributed agents
        distributed_agents = [
            name for name, agent in _agent_registry.items()
            if hasattr(agent, 'is_distributed') and agent.is_distributed
        ]
        
        if not distributed_agents:
            return {
                "status": "no_distributed_agents",
                "message": "No distributed agents registered"
            }
        
        # Get time sync status
        time_sync_status = []
        for agent_name in distributed_agents:
            try:
                agent = _agent_registry[agent_name]
                state = agent.comm_hub.get_state()
                if state:
                    time_sync_status.append({
                        "agent_name": agent_name,
                        "last_heartbeat": state.last_heartbeat,
                        "is_active": state.is_active
                    })
            except Exception as e:
                logger.warning(f"Could not get state for {agent_name}: {e}")
        
        # Calculate consensus
        active_count = sum(1 for s in time_sync_status if s["is_active"])
        consensus_achieved = active_count == len(distributed_agents)
        
        return {
            "status": "healthy" if consensus_achieved else "degraded",
            "total_distributed_agents": len(distributed_agents),
            "active_agents": active_count,
            "consensus_achieved": consensus_achieved,
            "agents": time_sync_status,
            "last_check": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting consciousness status: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


async def get_triage_flow_data() -> Dict[str, Any]:
    """
    Get triage flow visualization data.
    
    Week 5 Task 5.2: Triage flow visualization
    
    Returns:
        Triage flow statistics and routing data
    """
    try:
        # Get Sir Hawkington (triage commander)
        sir_hawkington = None
        for agent_name, agent in _agent_registry.items():
            if 'hawkington' in agent_name.lower():
                sir_hawkington = agent
                break
        
        if not sir_hawkington:
            return {
                "status": "no_triage_commander",
                "message": "Sir Hawkington not found"
            }
        
        # Get triage statistics
        status = sir_hawkington.get_agent_status()
        
        # Build triage flow data
        triage_data = {
            "status": "active",
            "total_decisions": status.get("total_decisions", 0),
            "routing_stats": {}
        }
        
        # Get decision history if available
        if hasattr(sir_hawkington, 'comm_hub'):
            try:
                recent_decisions = await sir_hawkington.comm_hub.state_manager.get_recent_decisions(
                    count=20
                )
                
                # Analyze routing patterns
                routing_counts = {}
                severity_counts = {}
                
                for decision in recent_decisions:
                    # Count by severity
                    severity = decision.input_data.get('severity', 'UNKNOWN')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    # Count by routing
                    routing = decision.output_data.get('routing', 'UNKNOWN')
                    routing_counts[routing] = routing_counts.get(routing, 0) + 1
                
                triage_data["routing_stats"] = routing_counts
                triage_data["severity_distribution"] = severity_counts
                triage_data["recent_decisions_count"] = len(recent_decisions)
                
            except Exception as e:
                logger.warning(f"Could not get decision history: {e}")
        
        # Add monocle state if available
        if hasattr(sir_hawkington, 'current_monocle_state'):
            triage_data["monocle_state"] = str(sir_hawkington.current_monocle_state)
            if hasattr(sir_hawkington, 'monocle_yeets_by_severity'):
                triage_data["monocle_yeets"] = sir_hawkington.monocle_yeets_by_severity
        
        return triage_data
    
    except Exception as e:
        logger.error(f"Error getting triage flow data: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/agents")
async def list_agents():
    """
    List all registered agents and their current status.
    
    Week 5 Task 5.2: Enhanced with distributed consciousness state!
    
    Returns:
        List of agent summaries with distributed features
    """
    agents = []
    distributed_count = 0
    
    for agent_name, agent in _agent_registry.items():
        try:
            status = agent.get_agent_status()
            
            # Check if agent has distributed features
            is_distributed = hasattr(agent, 'is_distributed') and agent.is_distributed
            if is_distributed:
                distributed_count += 1
            
            # Extract health/uptime/decisions from distributed state if available
            dist_state = status.get("distributed", {})
            
            agent_summary = {
                "agent_name": agent_name,
                "agent_type": status.get("agent_type"),
                "health": dist_state.get("health") if is_distributed else status.get("health"),
                "is_active": status.get("is_active"),
                "uptime_seconds": dist_state.get("uptime_seconds") if is_distributed else status.get("uptime_seconds"),
                "total_decisions": dist_state.get("total_decisions") if is_distributed else status.get("total_decisions"),
                "is_distributed": is_distributed
            }
            
            # Add distributed state if available
            if is_distributed and dist_state:
                agent_summary["distributed"] = {
                    "is_initialized": dist_state.get("distributed_enabled"),
                    "redis_connected": dist_state.get("distributed_enabled"),  # If distributed is enabled, Redis is connected
                    "resource_monitoring": dist_state.get("resource_monitoring_active"),
                    "recent_decisions": dist_state.get("recent_decisions_count", 0),
                    "messages_sent": dist_state.get("total_messages_sent", 0),
                    "messages_received": dist_state.get("total_messages_received", 0)
                }
            
            # Add personality traits
            if hasattr(agent, 'personality_traits'):
                agent_summary["personality"] = agent.personality_traits
            
            # Add Week 4 system stats if available
            week4_stats = {}
            
            # Coordination capability
            if hasattr(agent, 'coordination_manager'):
                week4_stats["coordination_enabled"] = True
            
            # Alert escalation
            if hasattr(agent, 'escalation_manager'):
                week4_stats["alert_escalation_enabled"] = True
                if hasattr(agent, 'total_alerts_sent'):
                    week4_stats["total_alerts"] = agent.total_alerts_sent
                    week4_stats["escalated_alerts"] = getattr(agent, 'escalated_alerts', 0)
            
            # Action verification
            if hasattr(agent, 'verification_manager'):
                week4_stats["action_verification_enabled"] = True
                if hasattr(agent, 'total_actions_tracked'):
                    week4_stats["actions_tracked"] = agent.total_actions_tracked
            
            # Override learning (Terry)
            if hasattr(agent, 'total_overrides'):
                week4_stats["override_learning"] = {
                    "total_overrides": agent.total_overrides,
                    "successful_overrides": agent.successful_overrides,
                    "success_rate": agent.override_success_rate
                }
            
            # Bob detection (The Stick)
            if hasattr(agent, 'bob_proximity_events'):
                week4_stats["bob_detection"] = {
                    "proximity_events": agent.bob_proximity_events,
                    "paper_bags_consumed": agent.paper_bags_consumed,
                    "anxiety_spikes": agent.anxiety_spikes
                }
            
            # Beer levels (Hamsters)
            if hasattr(agent, 'collective_beer_level'):
                week4_stats["beer_level"] = str(agent.collective_beer_level)
                week4_stats["bob_wild_ideas"] = agent.bob_wild_ideas
            
            # Paranoia levels (QSP)
            if hasattr(agent, 'paranoia_level'):
                week4_stats["paranoia_level"] = agent.paranoia_level
                week4_stats["threats_detected"] = agent.threats_detected
                week4_stats["tequila_shots_today"] = agent.tequila_shots_today
            
            # Monocle state (Sir Hawkington)
            if hasattr(agent, 'current_monocle_state'):
                week4_stats["monocle_state"] = str(agent.current_monocle_state)
                if hasattr(agent, 'monocle_yeets_by_severity'):
                    week4_stats["monocle_yeets"] = agent.monocle_yeets_by_severity
            
            if week4_stats:
                agent_summary["week4_systems"] = week4_stats
            
            agents.append(agent_summary)
            
        except Exception as e:
            logger.error(f"💥 FATAL: Failed to get status for {agent_name}: {e}", exc_info=True)
            # Re-raise - don't hide failures with fake data
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get status for {agent_name}: {str(e)}"
            )
    
    # Get consciousness checkpoint status (Week 5 Task 5.2)
    consciousness_status = await get_consciousness_status()
    
    # Get triage flow visualization data (Week 5 Task 5.2)
    triage_flow = await get_triage_flow_data()
    
    return {
        "total_agents": len(agents),
        "distributed_agents": distributed_count,
        "agents": agents,
        "consciousness_checkpoint": consciousness_status,
        "triage_flow": triage_flow,
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
    
    Week 5 Task 5.2: Enhanced with consciousness checkpoint status!
    
    Returns:
        System-wide health summary with distributed consciousness info
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


@router.get("/system/consciousness-checkpoint")
async def run_consciousness_checkpoint():
    """
    Run a consciousness checkpoint across all distributed agents.
    
    Week 5 Task 5.2: Consciousness checkpoint status endpoint!
    
    Returns:
        Consciousness checkpoint results
    """
    from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
    
    try:
        manager = get_distributed_manager()
        
        if not manager or not manager._initialized:
            raise HTTPException(status_code=503, detail="Distributed agent manager not initialized")
        
        # Run consciousness checkpoint
        from app.ai_agents.distributed.consciousness_sync import consciousness_checkpoint
        result = await consciousness_checkpoint(manager)
        
        return {
            "consensus_achieved": result["consensus_achieved"],
            "total_agents": result["total_agents"],
            "agents_checked": result["agents_checked"],
            "discrepancy_count": result["discrepancy_count"],
            "discrepancies": result.get("discrepancies", []),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running consciousness checkpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/payloads")
async def debug_payloads():
    """
    DEBUG ONLY — Live payload inspector.

    Returns three blocks:
    1. get_agent_status() output per agent — exactly what the heartbeat sends
    2. assembled_system_update_agents — what simplified_websocket_routes builds
       into system_update.agents before sending to the frontend
    3. registry_summary — which agents are registered and their class names

    This endpoint is the authoritative source for current payload shapes.
    No transformations. Raw dicts from the running agents.
    """
    from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
    from datetime import datetime, timezone

    result: Dict[str, Any] = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "registry_summary": {},
        "get_agent_status_per_agent": {},
        "assembled_system_update_agents": {},
        "errors": {}
    }

    # 1. _agent_registry (set via register_agent() from distributed_agents.py)
    for agent_name, agent in _agent_registry.items():
        result["registry_summary"][agent_name] = {
            "class": type(agent).__name__,
            "has_get_agent_status": hasattr(agent, "get_agent_status"),
            "is_distributed": getattr(agent, "is_distributed", False)
        }

    # 2. get_agent_status() — raw output, no transformation
    for agent_name, agent in _agent_registry.items():
        if hasattr(agent, "get_agent_status"):
            try:
                result["get_agent_status_per_agent"][agent_name] = agent.get_agent_status()
            except Exception as e:
                result["errors"][f"get_agent_status:{agent_name}"] = str(e)
        else:
            result["errors"][f"get_agent_status:{agent_name}"] = "method not found"

    # 3. assembled_system_update_agents — mirrors what the WS loop builds
    #    (status + is_distributed spread + all get_agent_status() fields)
    try:
        manager = get_distributed_manager()
        if manager and manager.initialized:
            for agent_name in manager.agents:
                agent = manager.get_agent(agent_name)
                if agent and hasattr(agent, "get_agent_status"):
                    try:
                        agent_status = agent.get_agent_status()
                        result["assembled_system_update_agents"][agent_name] = {
                            "status": "active",
                            "distributed": getattr(agent, "is_distributed", False),
                            **agent_status
                        }
                    except Exception as e:
                        result["errors"][f"assembled:{agent_name}"] = str(e)
    except Exception as e:
        result["errors"]["manager"] = str(e)

    return result


@router.get("/system/week4-stats")
async def get_week4_system_stats():
    """
    Get Week 4 system statistics across all agents.
    
    Week 5 Task 5.2: Week 4 systems dashboard data!
    
    Returns:
        Aggregated Week 4 system statistics
    """
    stats = {
        "coordination": {
            "enabled_agents": 0,
            "total_requests": 0
        },
        "alert_escalation": {
            "enabled_agents": 0,
            "total_alerts": 0,
            "escalated_alerts": 0,
            "emergency_alerts": 0
        },
        "action_verification": {
            "enabled_agents": 0,
            "total_actions_tracked": 0
        },
        "override_learning": {
            "total_overrides": 0,
            "successful_overrides": 0,
            "failed_overrides": 0
        },
        "bob_chaos": {
            "proximity_events": 0,
            "paper_bags_consumed": 0,
            "anxiety_spikes": 0,
            "wild_ideas": 0
        },
        "agent_specifics": {}
    }
    
    for agent_name, agent in _agent_registry.items():
        try:
            agent_stats = {}
            
            # Coordination
            if hasattr(agent, 'coordination_manager'):
                stats["coordination"]["enabled_agents"] += 1
            
            # Alert escalation
            if hasattr(agent, 'escalation_manager'):
                stats["alert_escalation"]["enabled_agents"] += 1
                if hasattr(agent, 'total_alerts_sent'):
                    stats["alert_escalation"]["total_alerts"] += agent.total_alerts_sent
                    stats["alert_escalation"]["escalated_alerts"] += getattr(agent, 'escalated_alerts', 0)
                    stats["alert_escalation"]["emergency_alerts"] += getattr(agent, 'emergency_alerts', 0)
            
            # Action verification
            if hasattr(agent, 'verification_manager'):
                stats["action_verification"]["enabled_agents"] += 1
                if hasattr(agent, 'total_actions_tracked'):
                    stats["action_verification"]["total_actions_tracked"] += agent.total_actions_tracked
            
            # Override learning (Terry)
            if hasattr(agent, 'total_overrides'):
                stats["override_learning"]["total_overrides"] += agent.total_overrides
                stats["override_learning"]["successful_overrides"] += agent.successful_overrides
                stats["override_learning"]["failed_overrides"] += agent.failed_overrides
                agent_stats["override_success_rate"] = agent.override_success_rate
            
            # Bob chaos (The Stick + Hamsters)
            if hasattr(agent, 'bob_proximity_events'):
                stats["bob_chaos"]["proximity_events"] += agent.bob_proximity_events
                stats["bob_chaos"]["paper_bags_consumed"] += agent.paper_bags_consumed
                stats["bob_chaos"]["anxiety_spikes"] += agent.anxiety_spikes
            
            if hasattr(agent, 'bob_wild_ideas'):
                stats["bob_chaos"]["wild_ideas"] += agent.bob_wild_ideas
            
            # Agent-specific stats
            if hasattr(agent, 'collective_beer_level'):
                agent_stats["beer_level"] = str(agent.collective_beer_level)
            
            if hasattr(agent, 'paranoia_level'):
                agent_stats["paranoia_level"] = agent.paranoia_level
                agent_stats["threats_detected"] = agent.threats_detected
            
            if hasattr(agent, 'current_monocle_state'):
                agent_stats["monocle_state"] = str(agent.current_monocle_state)
            
            if agent_stats:
                stats["agent_specifics"][agent_name] = agent_stats
        
        except Exception as e:
            logger.error(f"Error getting Week 4 stats for {agent_name}: {e}")
    
    return {
        "week4_systems": stats,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
