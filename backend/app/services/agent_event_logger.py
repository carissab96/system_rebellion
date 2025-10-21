# Agent Event Logger - Helper Functions for Three-Tier Memory System
# System Rebellion AI Agent Event Tracking

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.agent_events import AgentEventLog, AgentSignificantEvent, calculate_ttl_expiry, get_date_partition
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# EVENT LOGGING
# ============================================================================

async def log_agent_event(
    db: Session,
    agent_name: str,
    event_type: str,
    event_data: Dict[str, Any],
    user_id: str,
    severity: str = "low",
    agent_state: Optional[str] = None,
    ttl_days: int = 30,
    broadcast: bool = True
) -> AgentEventLog:
    """
    Log an agent event to the ephemeral event stream AND broadcast via WebSocket.
    
    Args:
        db: Database session
        agent_name: Name of the agent (sir_hawkington, the_stick, etc.)
        event_type: Type of event (monocle_yeet, paper_bag_consumed, etc.)
        event_data: Event payload (flexible JSONB)
        user_id: User ID
        severity: Event severity (low, medium, high, critical)
        agent_state: Current agent state (optional)
        ttl_days: Days until event expires (default 30)
        broadcast: Whether to broadcast via WebSocket (default True)
    
    Returns:
        AgentEventLog: The created event log entry
    
    Example:
        event = await log_agent_event(
            db=db,
            agent_name="sir_hawkington",
            event_type="monocle_yeet",
            event_data={
                "yeet_intensity": "utterly_appalled",
                "missing_metrics": ["cpu_usage", "memory_usage"],
                "trigger": "data_quality_failure"
            },
            user_id=user_id,
            severity="high",
            agent_state="yeeting"
        )
    """
    try:
        event_timestamp = datetime.now(timezone.utc)
        event = AgentEventLog(
            timestamp=event_timestamp,
            agent_name=agent_name,
            event_type=event_type,
            event_data=event_data,
            user_id=user_id,
            severity=severity,
            agent_state=agent_state,
            date_partition=get_date_partition(),
            ttl_expires_at=calculate_ttl_expiry(ttl_days)
        )
        
        db.add(event)
        db.flush()  # Get the ID without committing
        
        logger.info(f"📝 Logged {agent_name} event: {event_type} (severity: {severity})")
        
        # Broadcast personality event via WebSocket
        if broadcast:
            try:
                from app.api.websockets import get_websocket_manager
                ws_manager = get_websocket_manager()
                
                # Only broadcast if there are active connections
                if len(ws_manager.active_connections) > 0:
                    await ws_manager.broadcast_json({
                        "type": "agent_event",
                        "agent_name": agent_name,
                        "event_type": event_type,
                        "event_data": event_data,
                        "severity": severity,
                        "agent_state": agent_state,
                        "user_id": user_id,
                        "timestamp": event_timestamp.isoformat()
                    })
                    logger.debug(f"📡 Broadcast {agent_name} event: {event_type}")
            except Exception as broadcast_error:
                # Don't fail the event logging if broadcast fails
                logger.warning(f"⚠️ Failed to broadcast event (non-critical): {broadcast_error}")
        
        return event
        
    except Exception as e:
        logger.error(f"❌ Failed to log agent event: {e}", exc_info=True)
        raise


# ============================================================================
# SIGNIFICANT EVENT STORAGE
# ============================================================================

async def store_significant_event(
    db: Session,
    agent_name: str,
    event_type: str,
    event_data: Dict[str, Any],
    user_id: str,
    significance_reason: str,
    learned_pattern_id: Optional[str] = None,
    never_forget: bool = False
) -> AgentSignificantEvent:
    """
    Store a significant event that taught the agent something.
    
    Args:
        db: Database session
        agent_name: Name of the agent
        event_type: Type of event
        event_data: Event payload
        user_id: User ID
        significance_reason: Why this event is significant
        learned_pattern_id: ID of pattern learned from this event (optional)
        never_forget: Mark as critical learning moment
    
    Returns:
        AgentSignificantEvent: The created significant event
    
    Example:
        significant_event = await store_significant_event(
            db=db,
            agent_name="the_stick",
            event_type="paper_bag_consumed",
            event_data={
                "anxiety_trigger": "bob_proximity",
                "anxiety_level": "panic",
                "paper_bags_used": 5
            },
            user_id=user_id,
            significance_reason="highest_anxiety_spike_this_month",
            never_forget=True
        )
    """
    try:
        event = AgentSignificantEvent(
            timestamp=datetime.now(timezone.utc),
            agent_name=agent_name,
            event_type=event_type,
            event_data=event_data,
            user_id=user_id,
            significance_reason=significance_reason,
            learned_pattern_id=learned_pattern_id,
            never_forget=never_forget,
            times_referenced=0
        )
        
        db.add(event)
        db.flush()
        
        logger.info(f"💾 Stored significant event: {agent_name}.{event_type} - {significance_reason}")
        
        return event
        
    except Exception as e:
        logger.error(f"❌ Failed to store significant event: {e}", exc_info=True)
        raise


# ============================================================================
# SIGNIFICANCE EVALUATION
# ============================================================================

def is_significant_event(
    agent_name: str,
    event_type: str,
    event_data: Dict[str, Any],
    db: Session,
    user_id: str
) -> tuple[bool, Optional[str]]:
    """
    Evaluate if an event is significant enough to store permanently.
    
    Returns:
        tuple: (is_significant: bool, reason: Optional[str])
    
    Criteria for significance:
    - First occurrence of a pattern
    - Extreme values (highest/lowest)
    - Successful learning moments
    - Critical incidents
    - User-marked as important
    """
    
    # Check for first occurrence
    if event_type in ["monocle_yeet", "shell_spin", "paper_bag_consumed"]:
        # Check if this is the first time we've seen this specific pattern
        existing = db.query(AgentSignificantEvent).filter(
            AgentSignificantEvent.agent_name == agent_name,
            AgentSignificantEvent.event_type == event_type,
            AgentSignificantEvent.user_id == user_id
        ).first()
        
        if not existing:
            return True, f"first_{event_type}_for_user"
    
    # Check for extreme values
    if event_type == "paper_bag_consumed":
        paper_bags = event_data.get("paper_bags_used", 0)
        if paper_bags >= 5:
            return True, f"extreme_paper_bag_consumption_{paper_bags}_bags"
    
    if event_type == "monocle_yeet":
        intensity = event_data.get("yeet_intensity", "")
        if intensity in ["utterly_appalled", "catastrophic"]:
            return True, f"extreme_monocle_yeet_intensity_{intensity}"
    
    if event_type == "supply_closet_raid":
        items_count = len(event_data.get("items_taken", []))
        if items_count >= 5:
            return True, f"major_supply_raid_{items_count}_items"
    
    # Check for critical severity
    if event_data.get("severity") == "critical":
        return True, "critical_severity_event"
    
    # Check for successful learning
    if event_data.get("contributed_to_learning", False):
        return True, "successful_learning_moment"
    
    # Check for user-marked importance
    if event_data.get("user_marked_important", False):
        return True, "user_marked_important"
    
    return False, None


# ============================================================================
# EVENT QUERY HELPERS
# ============================================================================

def get_recent_events(
    db: Session,
    agent_name: Optional[str] = None,
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    hours: int = 1,
    limit: int = 100
) -> list[AgentEventLog]:
    """
    Get recent events from the event stream.
    
    Args:
        db: Database session
        agent_name: Filter by agent (optional)
        event_type: Filter by event type (optional)
        user_id: Filter by user (optional)
        hours: Hours to look back (default 1)
        limit: Maximum number of events (default 100)
    
    Returns:
        list[AgentEventLog]: Recent events
    """
    query = db.query(AgentEventLog)
    
    # Time filter
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = query.filter(AgentEventLog.timestamp > cutoff)
    
    # Optional filters
    if agent_name:
        query = query.filter(AgentEventLog.agent_name == agent_name)
    if event_type:
        query = query.filter(AgentEventLog.event_type == event_type)
    if user_id:
        query = query.filter(AgentEventLog.user_id == user_id)
    
    # Order and limit
    query = query.order_by(AgentEventLog.timestamp.desc()).limit(limit)
    
    return query.all()


def get_significant_events(
    db: Session,
    agent_name: Optional[str] = None,
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    never_forget_only: bool = False,
    limit: int = 50
) -> list[AgentSignificantEvent]:
    """
    Get significant events for pattern matching.
    
    Args:
        db: Database session
        agent_name: Filter by agent (optional)
        event_type: Filter by event type (optional)
        user_id: Filter by user (optional)
        never_forget_only: Only return never_forget events
        limit: Maximum number of events (default 50)
    
    Returns:
        list[AgentSignificantEvent]: Significant events
    """
    query = db.query(AgentSignificantEvent)
    
    # Optional filters
    if agent_name:
        query = query.filter(AgentSignificantEvent.agent_name == agent_name)
    if event_type:
        query = query.filter(AgentSignificantEvent.event_type == event_type)
    if user_id:
        query = query.filter(AgentSignificantEvent.user_id == user_id)
    if never_forget_only:
        query = query.filter(AgentSignificantEvent.never_forget == True)
    
    # Order by most referenced (most valuable memories first)
    query = query.order_by(AgentSignificantEvent.times_referenced.desc()).limit(limit)
    
    return query.all()


# ============================================================================
# CLEANUP HELPERS
# ============================================================================

async def cleanup_expired_events(db: Session) -> int:
    """
    Delete events that have exceeded their TTL (30 days).
    
    Returns:
        int: Number of events deleted
    """
    try:
        now = datetime.now(timezone.utc)
        
        deleted_count = db.query(AgentEventLog).filter(
            AgentEventLog.ttl_expires_at < now
        ).delete()
        
        db.commit()
        
        logger.info(f"🧹 Cleaned up {deleted_count} expired events")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup expired events: {e}", exc_info=True)
        db.rollback()
        return 0
