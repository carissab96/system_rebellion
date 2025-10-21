"""
Agent Insight Emitter - Inter-Agent Communication Broadcasting
Tracks meaningful agent-to-agent interactions and decision reasoning.

This is for INSIGHTS (why agents do things and how they communicate),
NOT for low-level method execution tracking.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def emit_agent_insight(
    from_agent: str,
    to_agent: str,
    action: str,
    reasoning: str,
    context: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """
    Emit an inter-agent communication insight via WebSocket.
    
    This tracks meaningful agent interactions:
    - Routing decisions (Hawkington → The Stick)
    - Escalations (Hawkington → VIC-20)
    - Delegations (VIC-20 → Meth Snail)
    - Resource transfers (Hawkington → Meth Snail Red Bull)
    - Coordination requests (VIC-20 → Quantum Shadow People)
    
    Args:
        from_agent: Agent initiating the communication
        to_agent: Agent receiving the communication
        action: What action is being taken (route_metrics, escalate, delegate, etc.)
        reasoning: WHY this action is being taken
        context: Additional context data (severity, metrics, etc.)
        user_id: User ID (optional)
    
    Example:
        await emit_agent_insight(
            from_agent="sir_hawkington",
            to_agent="the_stick",
            action="route_normal_operations",
            reasoning="System stress 0.25 - routing to baseline learning",
            context={
                "severity": "normal",
                "stress_score": 0.25,
                "confidence": 0.85
            },
            user_id=user_id
        )
    """
    try:
        from app.api.websockets import get_websocket_manager
        ws_manager = get_websocket_manager()
        
        # Only broadcast if there are active connections
        if len(ws_manager.active_connections) == 0:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        await ws_manager.broadcast_json({
            "type": "agent_insight",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "action": action,
            "reasoning": reasoning,
            "context": context,
            "user_id": user_id,
            "timestamp": timestamp.isoformat()
        })
        
        logger.info(f"💡 Insight: {from_agent} → {to_agent}: {action}")
        
    except Exception as e:
        # Don't fail the operation if broadcast fails
        logger.warning(f"⚠️ Failed to emit agent insight (non-critical): {e}")


async def emit_coordination_insight(
    coordinator: str,
    coordinated_agents: list[str],
    coordination_type: str,
    reasoning: str,
    context: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """
    Emit a multi-agent coordination insight.
    
    Used when VIC-20 coordinates multiple agents for complex scenarios.
    
    Args:
        coordinator: Agent coordinating (usually vic20_sage)
        coordinated_agents: List of agents being coordinated
        coordination_type: Type of coordination (emergency, optimization, etc.)
        reasoning: WHY this coordination is needed
        context: Additional context
        user_id: User ID (optional)
    
    Example:
        await emit_coordination_insight(
            coordinator="vic20_sage",
            coordinated_agents=["sir_hawkington", "the_stick", "hamsters"],
            coordination_type="emergency_response",
            reasoning="System stress 0.92 - multi-agent intervention required",
            context={
                "severity": "emergency",
                "stress_score": 0.92,
                "monocle_yeeted": True
            },
            user_id=user_id
        )
    """
    try:
        from app.api.websockets import get_websocket_manager
        ws_manager = get_websocket_manager()
        
        if len(ws_manager.active_connections) == 0:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        await ws_manager.broadcast_json({
            "type": "agent_insight",
            "insight_category": "coordination",
            "coordinator": coordinator,
            "coordinated_agents": coordinated_agents,
            "coordination_type": coordination_type,
            "reasoning": reasoning,
            "context": context,
            "user_id": user_id,
            "timestamp": timestamp.isoformat()
        })
        
        logger.info(f"🎯 Coordination: {coordinator} coordinating {len(coordinated_agents)} agents: {coordination_type}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to emit coordination insight (non-critical): {e}")


async def emit_resource_transfer_insight(
    from_agent: str,
    to_agent: str,
    resource_type: str,
    amount: Any,
    reasoning: str,
    context: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """
    Emit a resource transfer insight between agents.
    
    Tracks when agents share resources:
    - Hawkington → Meth Snail: Red Bull (energy boost)
    - Hamsters → Meth Snail: Duct tape (infrastructure support)
    - The Stick → Anyone: Paper bags (anxiety management)
    
    Args:
        from_agent: Agent giving resource
        to_agent: Agent receiving resource
        resource_type: Type of resource (red_bull, duct_tape, paper_bag, etc.)
        amount: Amount transferred
        reasoning: WHY this transfer is happening
        context: Additional context
        user_id: User ID (optional)
    
    Example:
        await emit_resource_transfer_insight(
            from_agent="sir_hawkington",
            to_agent="meth_snail",
            resource_type="red_bull",
            amount=1,
            reasoning="Meth Snail optimization performance declining - energy boost authorized",
            context={
                "snail_jitter_level": 0.45,
                "optimization_success_rate": 0.72,
                "authorization_level": "aristocratic"
            },
            user_id=user_id
        )
    """
    try:
        from app.api.websockets import get_websocket_manager
        ws_manager = get_websocket_manager()
        
        if len(ws_manager.active_connections) == 0:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        await ws_manager.broadcast_json({
            "type": "agent_insight",
            "insight_category": "resource_transfer",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "resource_type": resource_type,
            "amount": amount,
            "reasoning": reasoning,
            "context": context,
            "user_id": user_id,
            "timestamp": timestamp.isoformat()
        })
        
        logger.info(f"🎁 Resource Transfer: {from_agent} → {to_agent}: {amount}x {resource_type}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to emit resource transfer insight (non-critical): {e}")


async def emit_agent_memory_update(
    agent_name: str,
    memory_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """
    Broadcast an agent memory update via WebSocket.
    
    This sends the full agent memory bank data to connected clients
    via the agent_insights_websocket endpoint.
    
    Args:
        agent_name: Name of the agent (sir_hawkington, the_stick, etc.)
        memory_data: Full memory bank data for the agent
        user_id: User ID (optional)
    
    Example:
        await emit_agent_memory_update(
            agent_name="sir_hawkington",
            memory_data={
                "memory_id": "abc123",
                "timestamp": "2025-10-20T21:00:00Z",
                "triage_decision_context": {...},
                "data_quality_pattern": {...},
                ...
            },
            user_id=user_id
        )
    """
    try:
        from app.api.websockets import get_websocket_manager
        ws_manager = get_websocket_manager()
        
        if len(ws_manager.active_connections) == 0:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        await ws_manager.broadcast_json({
            "type": "agent_memory_update",
            "agent_name": agent_name,
            "memory": {
                "memory_id": memory_data.get("memory_id", f"{agent_name}_{timestamp.timestamp()}"),
                "user_id": user_id or memory_data.get("user_id", ""),
                "timestamp": memory_data.get("timestamp", timestamp.isoformat()),
                "shared_with_central": memory_data.get("shared_with_central", True),
                "central_memory_id": memory_data.get("central_memory_id", ""),
                **memory_data
            },
            "timestamp": timestamp.isoformat()
        })
        
        logger.info(f"📚 Memory Update: {agent_name}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to emit agent memory update (non-critical): {e}")
