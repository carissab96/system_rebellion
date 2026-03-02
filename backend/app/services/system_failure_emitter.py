"""
System Failure Event Emitter

Broadcasts ML pipeline failures to all stakeholders:
- Frontend (WebSocket)
- The Stick (learning hygiene)
- VIC-20 (coordination awareness)
- Logs (audit trail)

These failures are LOUD and VISIBLE. No hiding.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def emit_system_failure_event(
    agent_name: str,
    failure_type: str,
    error: str,
    emergency_action_taken: bool = False,
    emergency_action_details: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emit a system failure event that EVERYONE sees.
    
    This is called when an ML pipeline fails. The failure is broadcast
    to all stakeholders so nobody can miss it.
    
    Args:
        agent_name: Which agent's ML pipeline failed
        failure_type: Type of failure (ML_PIPELINE_FAILURE, VALIDATION_FAILURE, etc.)
        error: Error message/stack trace
        emergency_action_taken: Whether emergency action was taken
        emergency_action_details: Details of emergency action if taken
        context: Additional context about the failure
    """
    
    failure_event = {
        "type": "system_failure",
        "agent_name": agent_name,
        "failure_type": failure_type,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "emergency_action_taken": emergency_action_taken,
        "emergency_action_details": emergency_action_details or {},
        "context": context or {},
        "severity": "CRITICAL",
        "ml_informed": False  # This is NOT a normal ML decision
    }
    
    # Log it LOUDLY
    logger.error(
        f"🚨🚨🚨 SYSTEM FAILURE EVENT 🚨🚨🚨\n"
        f"Agent: {agent_name}\n"
        f"Failure Type: {failure_type}\n"
        f"Error: {error}\n"
        f"Emergency Action Taken: {emergency_action_taken}\n"
        f"Details: {emergency_action_details}"
    )
    
    # Broadcast to WebSocket (frontend sees it)
    try:
        from app.services.agent_decision_emitter import emit_agent_decision
        
        await emit_agent_decision(
            agent_name=agent_name,
            decision_id=f"system_failure_{agent_name}_{failure_event['timestamp']}",
            perception={"failure_type": failure_type, "error": error},
            reasoning={"emergency_action_taken": emergency_action_taken},
            action_selection={"type": "system_failure"},
            learning={"failure_event": failure_event}
        )
    except Exception as e:
        logger.error(f"Failed to emit failure event to WebSocket: {e}")
    
    # Send to The Stick for learning hygiene tracking
    try:
        from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
        manager = get_distributed_manager()

        if manager and manager.redis_client:
            from app.ai_agents.distributed.message_protocol import AgentMessage, MessageType, Priority

            stick_message = AgentMessage(
                message_type=MessageType.DECISION_LOG,
                from_agent=agent_name,
                to_agent="the_stick",
                payload={
                    "log_type": "system_failure",
                    "failure_event": failure_event,
                    "requires_review": True,
                    "learning_hygiene_flag": True
                },
                priority=Priority.CRITICAL
            )

            await manager.redis_client.publish(
                "agent:the_stick:messages",
                stick_message.to_json()
            )
            logger.debug("System failure logged to The Stick for learning hygiene review")
    except Exception as e:
        logger.error(f"Failed to notify The Stick: {e}")

    # Send to VIC-20 for coordination awareness
    try:
        from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
        manager = get_distributed_manager()

        if manager and manager.redis_client:
            from app.ai_agents.distributed.message_protocol import AgentMessage, MessageType, Priority

            vic20_message = AgentMessage(
                message_type=MessageType.DECISION_LOG,
                from_agent=agent_name,
                to_agent="vic_20_sage",
                payload={
                    "log_type": "ml_pipeline_failure",
                    "failed_agent": agent_name,
                    "failure_event": failure_event,
                    "coordination_impact": True
                },
                priority=Priority.CRITICAL
            )

            await manager.redis_client.publish(
                "agent:vic_20_sage:messages",
                vic20_message.to_json()
            )
            logger.debug("ML pipeline failure reported to VIC-20 for coordination awareness")
    except Exception as e:
        logger.error(f"Failed to notify VIC-20: {e}")
    
    logger.error(
        f"🚨 System failure event broadcast complete. "
        f"Frontend, Stick, and VIC-20 have been notified."
    )


async def record_emergency_action(
    agent: str,
    action: str,
    reason: str,
    ml_informed: bool = False,
    metrics_before: Optional[Dict[str, Any]] = None,
    metrics_after: Optional[Dict[str, Any]] = None,
    success: bool = True
) -> None:
    """
    Record an emergency action in the audit trail.
    
    Emergency actions are FLAGGED as such so they're never confused
    with normal ML-informed decisions.
    
    Args:
        agent: Which agent took the action
        action: What action was taken
        reason: Why it was taken (usually ML_PIPELINE_FAILURE + critical state)
        ml_informed: Whether this was ML-informed (should be False for emergencies)
        metrics_before: System metrics before action
        metrics_after: System metrics after action
        success: Whether the action succeeded
    """
    
    emergency_record = {
        "type": "emergency_action",
        "agent": agent,
        "action": action,
        "reason": reason,
        "ml_informed": ml_informed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics_before": metrics_before or {},
        "metrics_after": metrics_after or {},
        "success": success,
        "flagged_as_emergency": True  # THIS IS KEY
    }
    
    logger.error(
        f"🚨 EMERGENCY ACTION RECORDED 🚨\n"
        f"Agent: {agent}\n"
        f"Action: {action}\n"
        f"Reason: {reason}\n"
        f"ML-Informed: {ml_informed}\n"
        f"Success: {success}\n"
        f"⚠️ THIS IS NOT A NORMAL OPERATION ⚠️"
    )
    
    # Store in database with emergency flag
    try:
        from app.core.database import get_async_db
        from app.models.agent_memory_banks import CentralMemoryBank
        
        async for db in get_async_db():
            memory_entry = CentralMemoryBank(
                agent_name=agent,
                decision_type="emergency_action",
                context={
                    "action": action,
                    "reason": reason,
                    "ml_informed": ml_informed,
                    "metrics_before": metrics_before or {},
                    "metrics_after": metrics_after or {},
                    "flagged_as_emergency": True,
                    "emergency_record": emergency_record
                },
                outcome={
                    "success": success,
                    "emergency_override": True
                },
                confidence=0.0,  # Not ML-informed
                reasoning=reason,
                priority=10,  # Maximum priority for emergency actions
                stick_anxiety_level=100.0  # Maximum anxiety
            )
            
            db.add(memory_entry)
            await db.commit()
            
            logger.debug(f"Emergency action stored in Central Memory Bank (ID: {memory_entry.memory_id})")
            break
    except Exception as e:
        logger.error(f"Failed to store emergency action in database: {e}")
    
    # Send to The Stick for audit trail
    try:
        from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
        manager = get_distributed_manager()
        
        if manager and manager.redis_client:
            from app.ai_agents.distributed.message_protocol import AgentMessage, MessageType, Priority
            
            stick_message = AgentMessage(
                message_type=MessageType.DECISION_LOG,
                from_agent=agent,
                to_agent="the_stick",
                payload={
                    "log_type": "emergency_action",
                    "emergency_record": emergency_record,
                    "requires_audit": True,
                    "stick_anxiety_level": 100.0
                },
                priority=Priority.CRITICAL
            )
            
            await manager.redis_client.publish(
                f"agent:the_stick:messages",
                stick_message.to_json()
            )
            logger.debug(f"Emergency action logged to The Stick for audit trail")
    except Exception as e:
        logger.error(f"Failed to notify The Stick of emergency action: {e}")
    
    logger.error(
        f"🚨 Emergency action logged. This will be visible in all audit trails."
    )
