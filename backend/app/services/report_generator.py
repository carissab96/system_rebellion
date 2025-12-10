"""
Report Generator Service
=========================

Transforms raw agent database writes into human-readable narratives.
Each agent has personality-driven language for their reports.

This is the bridge between raw data and the terrarium feed.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# =============================================================================
# AGENT PERSONALITIES - How each agent "speaks" in reports
# =============================================================================

AGENT_VOICES = {
    "sir_hawkington": {
        "prefix": "🧐",
        "style": "aristocratic",
        "verbs": {
            "triage": "observed with distinction",
            "alert": "raised an eyebrow at",
            "decision": "decreed",
            "monocle_yeet": "YEETED HIS MONOCLE at",
            "escalate": "summoned VIC-20 regarding",
        },
        "phrases": [
            "Most irregular.",
            "Quite unacceptable.",
            "This requires attention.",
            "I say!",
            "Hmm, indeed.",
        ]
    },
    "hamsters": {
        "prefix": "🐹",
        "style": "chaotic_trio",
        "verbs": {
            "consensus": "reached telepathic consensus on",
            "decision": "argued about and eventually agreed on",
            "fix": "duct-taped together a solution for",
            "wild_idea": "Bob suggested",
            "calculate": "Carl calculated",
            "careful": "Steve carefully considered",
        },
        "phrases": [
            "Hold my beer.",
            "That'll buff out.",
            "Duct tape fixes everything.",
            "Bob says send it.",
            "Steve says wait.",
            "Carl's measuring tape.",
        ]
    },
    "meth_snail": {
        "prefix": "🐌⚡",
        "style": "hyperactive",
        "verbs": {
            "optimize": "ZOOMED through",
            "cache_clear": "OBLITERATED cache for",
            "memory": "turbocharged memory by",
            "speed": "accelerated",
            "shell_spin": "spun shell and",
        },
        "phrases": [
            "GOTTA GO FAST!",
            "Red Bull acquired.",
            "Shell spinning at maximum RPM!",
            "Optimization complete!",
            "Terry time!",
        ]
    },
    "quantum_shadow_people": {
        "prefix": "👁️",
        "style": "paranoid",
        "verbs": {
            "observe": "noticed something suspicious about",
            "network": "detected anomalies in",
            "phase": "phased through",
            "paranoia": "grew concerned about",
            "tequila": "took a shot and analyzed",
        },
        "phrases": [
            "They're watching.",
            "The patterns... they're everywhere.",
            "Trust no one.",
            "Something's not right here.",
            "I've seen this before.",
        ]
    },
    "the_stick": {
        "prefix": "📋",
        "style": "anxious_recorder",
        "verbs": {
            "record": "documented",
            "log": "carefully noted",
            "pattern": "identified a pattern in",
            "anxiety": "hyperventilated about",
            "paper_bag": "breathed into paper bag after seeing",
        },
        "phrases": [
            "*breathes into paper bag*",
            "This is fine. Everything is fine.",
            "Adding to the permanent record.",
            "I've logged everything.",
            "The patterns are concerning.",
        ]
    },
    "vic20_sage": {
        "prefix": "🖥️",
        "style": "wise_coordinator",
        "verbs": {
            "coordinate": "orchestrated",
            "route": "directed",
            "wisdom": "advised",
            "plan": "formulated a plan for",
            "delegate": "assigned",
        },
        "phrases": [
            "In my experience...",
            "The optimal path is clear.",
            "Coordinating resources.",
            "All agents aligned.",
            "Wisdom suggests patience.",
        ]
    }
}


def humanize_agent_name(raw_name: str) -> str:
    """Convert raw agent name to display name."""
    mapping = {
        "sir_hawkington": "Sir Hawkington",
        "hawkington": "Sir Hawkington",
        "hamsters": "The Hamsters",
        "meth_snail": "Terry",
        "terry": "Terry",
        "quantum_shadow_people": "QSP",
        "qsp": "QSP",
        "the_stick": "The Stick",
        "stick": "The Stick",
        "vic20_sage": "VIC-20",
        "vic_20_sage": "VIC-20",
        "vic20": "VIC-20",
    }
    return mapping.get(raw_name.lower(), raw_name.replace("_", " ").title())


def get_agent_voice(agent_name: str) -> Dict[str, Any]:
    """Get the voice configuration for an agent."""
    normalized = agent_name.lower()
    for key, voice in AGENT_VOICES.items():
        if key in normalized or normalized in key:
            return voice
    return AGENT_VOICES.get("sir_hawkington")  # Default to Hawk's style


def generate_narrative(
    agent_name: str,
    event_type: str,
    details: Dict[str, Any],
    timestamp: datetime
) -> str:
    """
    Generate a human-readable narrative from raw event data.
    
    Args:
        agent_name: The agent that generated this event
        event_type: Type of event (triage, decision, alert, etc.)
        details: Raw event details from database
        timestamp: When this happened
        
    Returns:
        Human-readable narrative string
    """
    voice = get_agent_voice(agent_name)
    display_name = humanize_agent_name(agent_name)
    
    # Find the best verb for this event type
    verb = "reported"
    for key, v in voice.get("verbs", {}).items():
        if key in event_type.lower():
            verb = v
            break
    
    # Build the narrative based on event type and details
    narrative_parts = [f"{display_name} {verb}"]
    
    # Extract key metrics if present
    if "cpu_usage" in details or "cpu" in details:
        cpu = details.get("cpu_usage") or details.get("cpu")
        if cpu is not None:
            narrative_parts.append(f"CPU at {cpu:.1f}%")
    
    if "memory_usage" in details or "memory" in details:
        mem = details.get("memory_usage") or details.get("memory")
        if mem is not None:
            narrative_parts.append(f"memory at {mem:.1f}%")
    
    if "disk_usage" in details or "disk" in details:
        disk = details.get("disk_usage") or details.get("disk")
        if disk is not None:
            narrative_parts.append(f"disk at {disk:.1f}%")
    
    # Add confidence if present
    if "confidence" in details:
        conf = details.get("confidence")
        if conf is not None:
            narrative_parts.append(f"({int(float(conf) * 100)}% confidence)")
    
    # Add disposition/severity if present
    if "disposition" in details:
        narrative_parts.append(f"→ {details['disposition']}")
    
    if "severity" in details:
        narrative_parts.append(f"[{details['severity']}]")
    
    # Add monocle state for Hawkington
    if "monocle_state" in details:
        state = details["monocle_state"]
        if state == "YEETED":
            narrative_parts.append("*MONOCLE YEETED*")
        elif state == "RAISED":
            narrative_parts.append("*monocle raised*")
    
    # Combine parts
    narrative = " ".join(narrative_parts)
    
    # Add a personality phrase occasionally (based on hash of content)
    phrases = voice.get("phrases", [])
    if phrases and hash(narrative) % 3 == 0:
        import random
        random.seed(hash(narrative))
        narrative += f" {random.choice(phrases)}"
    
    return narrative


async def get_recent_activity_feed(
    db: AsyncSession,
    hours: int = 1,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get recent agent activity as human-readable feed items.
    
    Args:
        db: Database session
        hours: Hours of history to retrieve
        limit: Maximum items to return
        
    Returns:
        List of feed items with agent, message, timestamp, type
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    feed_items = []
    
    # Query central memory bank for recent activity
    try:
        result = await db.execute(
            text("""
                SELECT agent_name, event_type, details, occurred_at, priority
                FROM central_memory_bank
                WHERE occurred_at >= :since
                ORDER BY occurred_at DESC
                LIMIT :limit
            """),
            {"since": since, "limit": limit}
        )
        
        for row in result.mappings():
            details = row["details"] if isinstance(row["details"], dict) else {}
            
            feed_items.append({
                "id": f"cmb-{row['occurred_at'].timestamp()}",
                "agent": humanize_agent_name(row["agent_name"]),
                "message": generate_narrative(
                    row["agent_name"],
                    row["event_type"],
                    details,
                    row["occurred_at"]
                ),
                "timestamp": row["occurred_at"].isoformat(),
                "type": "insight" if row["priority"] and row["priority"] <= 2 else "event",
                "raw_type": row["event_type"]
            })
            
    except Exception as e:
        logger.warning(f"Could not query central_memory_bank: {e}")
    
    # Also query decision vectors for triage decisions
    try:
        result = await db.execute(
            text("""
                SELECT agent_name, decision_type, decision_summary, 
                       confidence_score, created_at, metadata
                FROM agent_decision_vectors
                WHERE created_at >= :since
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"since": since, "limit": limit}
        )
        
        for row in result.mappings():
            metadata = row["metadata"] if isinstance(row["metadata"], dict) else {}
            
            feed_items.append({
                "id": f"dec-{row['created_at'].timestamp()}",
                "agent": humanize_agent_name(row["agent_name"]),
                "message": generate_narrative(
                    row["agent_name"],
                    row["decision_type"],
                    {
                        "confidence": row["confidence_score"],
                        **metadata
                    },
                    row["created_at"]
                ),
                "timestamp": row["created_at"].isoformat(),
                "type": "triage",
                "raw_type": row["decision_type"]
            })
            
    except Exception as e:
        logger.warning(f"Could not query agent_decision_vectors: {e}")
    
    # Also query interaction vectors for inter-agent comms
    try:
        result = await db.execute(
            text("""
                SELECT from_agent, to_agent, interaction_type, 
                       message_summary, created_at
                FROM agent_interaction_vectors
                WHERE created_at >= :since
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"since": since, "limit": limit}
        )
        
        for row in result.mappings():
            from_name = humanize_agent_name(row["from_agent"])
            to_name = humanize_agent_name(row["to_agent"])
            
            feed_items.append({
                "id": f"int-{row['created_at'].timestamp()}",
                "agent": from_name,
                "message": f"{from_name} → {to_name}: {row['message_summary'] or row['interaction_type']}",
                "timestamp": row["created_at"].isoformat(),
                "type": "insight",
                "raw_type": row["interaction_type"]
            })
            
    except Exception as e:
        logger.warning(f"Could not query agent_interaction_vectors: {e}")
    
    # Sort by timestamp descending and limit
    feed_items.sort(key=lambda x: x["timestamp"], reverse=True)
    return feed_items[:limit]


async def get_overnight_narrative(
    db: AsyncSession,
    hours: int = 12
) -> Dict[str, Any]:
    """
    Generate a narrative summary of overnight activity.
    
    Returns:
        Dictionary with summary stats and narrative highlights
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    summary = {
        "period_hours": hours,
        "total_events": 0,
        "agents_active": [],
        "highlights": [],
        "narrative": ""
    }
    
    # Count events per agent
    try:
        result = await db.execute(
            text("""
                SELECT agent_name, COUNT(*) as count
                FROM central_memory_bank
                WHERE occurred_at >= :since
                GROUP BY agent_name
                ORDER BY count DESC
            """),
            {"since": since}
        )
        
        for row in result.mappings():
            summary["agents_active"].append({
                "agent": humanize_agent_name(row["agent_name"]),
                "events": row["count"]
            })
            summary["total_events"] += row["count"]
            
    except Exception as e:
        logger.warning(f"Could not count events: {e}")
    
    # Get top highlights (high priority events)
    try:
        result = await db.execute(
            text("""
                SELECT agent_name, event_type, details, occurred_at
                FROM central_memory_bank
                WHERE occurred_at >= :since AND priority <= 2
                ORDER BY priority ASC, occurred_at DESC
                LIMIT 5
            """),
            {"since": since}
        )
        
        for row in result.mappings():
            details = row["details"] if isinstance(row["details"], dict) else {}
            summary["highlights"].append(
                generate_narrative(
                    row["agent_name"],
                    row["event_type"],
                    details,
                    row["occurred_at"]
                )
            )
            
    except Exception as e:
        logger.warning(f"Could not get highlights: {e}")
    
    # Build narrative summary
    if summary["total_events"] > 0:
        most_active = summary["agents_active"][0] if summary["agents_active"] else None
        summary["narrative"] = (
            f"In the last {hours} hours, {summary['total_events']} events occurred. "
        )
        if most_active:
            summary["narrative"] += (
                f"{most_active['agent']} was most active with {most_active['events']} events. "
            )
        if summary["highlights"]:
            summary["narrative"] += f"Key highlights: {summary['highlights'][0]}"
    else:
        summary["narrative"] = f"No agent activity recorded in the last {hours} hours."
    
    return summary
