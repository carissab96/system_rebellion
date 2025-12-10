"""
Agent Reports API Endpoints
============================

FastAPI endpoints for viewing agent activity, memory bank entries,
and vector database contents.

Endpoints:
- GET /reports/activity - Recent agent activity with content
- GET /reports/memory-bank - Central memory bank entries
- GET /reports/vectors/summary - Vector table counts and stats
- GET /reports/vectors/decisions - Recent decision vectors
- GET /reports/vectors/patterns - Recent pattern vectors
- GET /reports/vectors/interactions - Recent interaction vectors
- GET /reports/overnight - Overnight activity summary
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import logging
import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


# =============================================================================
# Response Models
# =============================================================================

class AgentActivityEntry(BaseModel):
    """Single agent activity entry"""
    id: str
    agent_name: str
    event_type: str
    timestamp: datetime
    details: Dict[str, Any]
    importance: Optional[str] = None


class MemoryBankEntry(BaseModel):
    """Central memory bank entry"""
    id: str
    agent_name: str
    memory_type: str
    timestamp: datetime
    content: Dict[str, Any]
    importance: Optional[str] = None
    tags: Optional[List[str]] = None


class VectorSummary(BaseModel):
    """Summary of vector table contents"""
    table_name: str
    total_count: int
    last_24h_count: int
    last_hour_count: int
    agents: Dict[str, int]
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None


class VectorEntry(BaseModel):
    """Single vector entry (without the actual embedding)"""
    id: int
    vector_id: str
    agent_name: str
    created_at: datetime
    content_type: str
    content_text: str
    metadata: Optional[Dict[str, Any]] = None


# =============================================================================
# Activity Endpoints
# =============================================================================

@router.get("/activity", response_model=Dict[str, Any])
async def get_agent_activity(
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    hours: int = Query(24, description="Hours of history to retrieve"),
    limit: int = Query(100, description="Maximum entries to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get recent agent activity from agent-specific memory banks.
    
    Returns decisions, actions, and events from all agents or a specific agent.
    """
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Query each agent's memory bank table
        activities = []
        
        # Sir Hawkington - hawkington_memory_bank
        if not agent_name or agent_name == "sir_hawkington":
            result = await db.execute(
                text("""
                    SELECT id, 'sir_hawkington' as agent_name, event_type, 
                           timestamp, details, importance
                    FROM hawkington_memory_bank
                    WHERE timestamp >= :since
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """),
                {"since": since, "limit": limit}
            )
            for row in result.mappings():
                activities.append({
                    "id": str(row["id"]),
                    "agent_name": row["agent_name"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "details": row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {},
                    "importance": row["importance"]
                })
        
        # Terry (Meth Snail) - meth_snail_memory_bank
        if not agent_name or agent_name == "meth_snail":
            result = await db.execute(
                text("""
                    SELECT id, 'meth_snail' as agent_name, event_type,
                           timestamp, details, importance
                    FROM meth_snail_memory_bank
                    WHERE timestamp >= :since
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """),
                {"since": since, "limit": limit}
            )
            for row in result.mappings():
                activities.append({
                    "id": str(row["id"]),
                    "agent_name": row["agent_name"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "details": row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {},
                    "importance": row["importance"]
                })
        
        # Hamsters - hamsters_memory_bank
        if not agent_name or agent_name == "hamsters":
            result = await db.execute(
                text("""
                    SELECT id, 'hamsters' as agent_name, event_type,
                           timestamp, details, importance
                    FROM hamsters_memory_bank
                    WHERE timestamp >= :since
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """),
                {"since": since, "limit": limit}
            )
            for row in result.mappings():
                activities.append({
                    "id": str(row["id"]),
                    "agent_name": row["agent_name"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "details": row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {},
                    "importance": row["importance"]
                })
        
        # QSP - qsp_memory_bank
        if not agent_name or agent_name == "quantum_shadow_people":
            result = await db.execute(
                text("""
                    SELECT id, 'quantum_shadow_people' as agent_name, event_type,
                           timestamp, details, importance
                    FROM qsp_memory_bank
                    WHERE timestamp >= :since
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """),
                {"since": since, "limit": limit}
            )
            for row in result.mappings():
                activities.append({
                    "id": str(row["id"]),
                    "agent_name": row["agent_name"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "details": row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {},
                    "importance": row["importance"]
                })
        
        # The Stick - stick_memory_bank
        if not agent_name or agent_name == "the_stick":
            result = await db.execute(
                text("""
                    SELECT id, 'the_stick' as agent_name, event_type,
                           timestamp, details, importance
                    FROM stick_memory_bank
                    WHERE timestamp >= :since
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """),
                {"since": since, "limit": limit}
            )
            for row in result.mappings():
                activities.append({
                    "id": str(row["id"]),
                    "agent_name": row["agent_name"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "details": row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {},
                    "importance": row["importance"]
                })
        
        # VIC-20 - vic20_memory_bank
        if not agent_name or agent_name == "vic_20_sage":
            result = await db.execute(
                text("""
                    SELECT id, 'vic_20_sage' as agent_name, event_type,
                           timestamp, details, importance
                    FROM vic20_memory_bank
                    WHERE timestamp >= :since
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """),
                {"since": since, "limit": limit}
            )
            for row in result.mappings():
                activities.append({
                    "id": str(row["id"]),
                    "agent_name": row["agent_name"],
                    "event_type": row["event_type"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "details": row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {},
                    "importance": row["importance"]
                })
        
        # Sort by timestamp descending
        activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        
        # Limit total results
        activities = activities[:limit]
        
        return {
            "status": "success",
            "query": {
                "agent_name": agent_name,
                "hours": hours,
                "limit": limit,
                "since": since.isoformat()
            },
            "count": len(activities),
            "activities": activities
        }
        
    except Exception as e:
        logger.error(f"Error fetching agent activity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Central Memory Bank Endpoint
# =============================================================================

@router.get("/memory-bank", response_model=Dict[str, Any])
async def get_memory_bank(
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    hours: int = Query(24, description="Hours of history to retrieve"),
    limit: int = Query(100, description="Maximum entries to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get entries from the central memory bank.
    
    The central memory bank contains cross-agent memories and shared context.
    """
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = """
            SELECT id, agent_name, memory_type, timestamp, content, 
                   importance, tags
            FROM central_memory_bank
            WHERE timestamp >= :since
        """
        params = {"since": since, "limit": limit}
        
        if agent_name:
            query += " AND agent_name = :agent_name"
            params["agent_name"] = agent_name
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        
        result = await db.execute(text(query), params)
        
        entries = []
        for row in result.mappings():
            entries.append({
                "id": str(row["id"]),
                "agent_name": row["agent_name"],
                "memory_type": row["memory_type"],
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                "content": row["content"] if isinstance(row["content"], dict) else json.loads(row["content"]) if row["content"] else {},
                "importance": row["importance"],
                "tags": row["tags"] if row["tags"] else []
            })
        
        return {
            "status": "success",
            "query": {
                "agent_name": agent_name,
                "hours": hours,
                "limit": limit,
                "since": since.isoformat()
            },
            "count": len(entries),
            "entries": entries
        }
        
    except Exception as e:
        logger.error(f"Error fetching memory bank: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Vector Summary Endpoint
# =============================================================================

@router.get("/vectors/summary", response_model=Dict[str, Any])
async def get_vector_summary(
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get summary statistics for all vector tables.
    
    Shows counts, time ranges, and per-agent breakdowns.
    """
    try:
        summaries = []
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_hour = now - timedelta(hours=1)
        
        # Decision vectors
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE created_at >= :last_24h) as last_24h,
                COUNT(*) FILTER (WHERE created_at >= :last_hour) as last_hour,
                MIN(created_at) as oldest,
                MAX(created_at) as newest
            FROM agent_decision_vectors
        """), {"last_24h": last_24h, "last_hour": last_hour})
        row = result.mappings().first()
        
        # Get per-agent counts for decisions
        agent_result = await db.execute(text("""
            SELECT agent_name, COUNT(*) as count
            FROM agent_decision_vectors
            GROUP BY agent_name
        """))
        agent_counts = {r["agent_name"]: r["count"] for r in agent_result.mappings()}
        
        summaries.append({
            "table_name": "agent_decision_vectors",
            "total_count": row["total"] or 0,
            "last_24h_count": row["last_24h"] or 0,
            "last_hour_count": row["last_hour"] or 0,
            "oldest_entry": row["oldest"].isoformat() if row["oldest"] else None,
            "newest_entry": row["newest"].isoformat() if row["newest"] else None,
            "agents": agent_counts
        })
        
        # Pattern vectors
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE created_at >= :last_24h) as last_24h,
                COUNT(*) FILTER (WHERE created_at >= :last_hour) as last_hour,
                MIN(created_at) as oldest,
                MAX(created_at) as newest
            FROM agent_pattern_vectors
        """), {"last_24h": last_24h, "last_hour": last_hour})
        row = result.mappings().first()
        
        agent_result = await db.execute(text("""
            SELECT agent_name, COUNT(*) as count
            FROM agent_pattern_vectors
            GROUP BY agent_name
        """))
        agent_counts = {r["agent_name"]: r["count"] for r in agent_result.mappings()}
        
        summaries.append({
            "table_name": "agent_pattern_vectors",
            "total_count": row["total"] or 0,
            "last_24h_count": row["last_24h"] or 0,
            "last_hour_count": row["last_hour"] or 0,
            "oldest_entry": row["oldest"].isoformat() if row["oldest"] else None,
            "newest_entry": row["newest"].isoformat() if row["newest"] else None,
            "agents": agent_counts
        })
        
        # Interaction vectors
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE created_at >= :last_24h) as last_24h,
                COUNT(*) FILTER (WHERE created_at >= :last_hour) as last_hour,
                MIN(created_at) as oldest,
                MAX(created_at) as newest
            FROM agent_interaction_vectors
        """), {"last_24h": last_24h, "last_hour": last_hour})
        row = result.mappings().first()
        
        agent_result = await db.execute(text("""
            SELECT from_agent as agent_name, COUNT(*) as count
            FROM agent_interaction_vectors
            GROUP BY from_agent
        """))
        agent_counts = {r["agent_name"]: r["count"] for r in agent_result.mappings()}
        
        summaries.append({
            "table_name": "agent_interaction_vectors",
            "total_count": row["total"] or 0,
            "last_24h_count": row["last_24h"] or 0,
            "last_hour_count": row["last_hour"] or 0,
            "oldest_entry": row["oldest"].isoformat() if row["oldest"] else None,
            "newest_entry": row["newest"].isoformat() if row["newest"] else None,
            "agents": agent_counts
        })
        
        # Calculate totals
        total_vectors = sum(s["total_count"] for s in summaries)
        total_24h = sum(s["last_24h_count"] for s in summaries)
        total_hour = sum(s["last_hour_count"] for s in summaries)
        
        return {
            "status": "success",
            "generated_at": now.isoformat(),
            "totals": {
                "all_vectors": total_vectors,
                "last_24h": total_24h,
                "last_hour": total_hour
            },
            "tables": summaries
        }
        
    except Exception as e:
        logger.error(f"Error fetching vector summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Vector Detail Endpoints
# =============================================================================

@router.get("/vectors/decisions", response_model=Dict[str, Any])
async def get_decision_vectors(
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    hours: int = Query(24, description="Hours of history to retrieve"),
    limit: int = Query(50, description="Maximum entries to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get recent decision vectors (without embeddings).
    """
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = """
            SELECT id, vector_id::text, agent_name, user_id, decision_type,
                   event_type, priority, occurred_at, created_at,
                   decision_text, decision_summary, metadata, confidence_score
            FROM agent_decision_vectors
            WHERE created_at >= :since
        """
        params = {"since": since, "limit": limit}
        
        if agent_name:
            query += " AND agent_name = :agent_name"
            params["agent_name"] = agent_name
        
        query += " ORDER BY created_at DESC LIMIT :limit"
        
        result = await db.execute(text(query), params)
        
        entries = []
        for row in result.mappings():
            entries.append({
                "id": row["id"],
                "vector_id": row["vector_id"],
                "agent_name": row["agent_name"],
                "user_id": row["user_id"],
                "decision_type": row["decision_type"],
                "event_type": row["event_type"],
                "priority": row["priority"],
                "occurred_at": row["occurred_at"].isoformat() if row["occurred_at"] else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "decision_text": row["decision_text"][:500] + "..." if row["decision_text"] and len(row["decision_text"]) > 500 else row["decision_text"],
                "decision_summary": row["decision_summary"],
                "metadata": row["metadata"],
                "confidence_score": row["confidence_score"]
            })
        
        return {
            "status": "success",
            "query": {
                "agent_name": agent_name,
                "hours": hours,
                "limit": limit
            },
            "count": len(entries),
            "entries": entries
        }
        
    except Exception as e:
        logger.error(f"Error fetching decision vectors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectors/patterns", response_model=Dict[str, Any])
async def get_pattern_vectors(
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    hours: int = Query(168, description="Hours of history (default 1 week)"),
    limit: int = Query(50, description="Maximum entries to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get recent pattern vectors (without embeddings).
    """
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = """
            SELECT id, vector_id::text, agent_name, user_id, pattern_type,
                   pattern_name, pattern_description, first_observed, last_observed,
                   observation_count, created_at, confidence_score, success_rate,
                   application_count, pattern_data
            FROM agent_pattern_vectors
            WHERE created_at >= :since
        """
        params = {"since": since, "limit": limit}
        
        if agent_name:
            query += " AND agent_name = :agent_name"
            params["agent_name"] = agent_name
        
        query += " ORDER BY last_observed DESC LIMIT :limit"
        
        result = await db.execute(text(query), params)
        
        entries = []
        for row in result.mappings():
            entries.append({
                "id": row["id"],
                "vector_id": row["vector_id"],
                "agent_name": row["agent_name"],
                "pattern_type": row["pattern_type"],
                "pattern_name": row["pattern_name"],
                "pattern_description": row["pattern_description"][:300] + "..." if row["pattern_description"] and len(row["pattern_description"]) > 300 else row["pattern_description"],
                "first_observed": row["first_observed"].isoformat() if row["first_observed"] else None,
                "last_observed": row["last_observed"].isoformat() if row["last_observed"] else None,
                "observation_count": row["observation_count"],
                "confidence_score": row["confidence_score"],
                "success_rate": row["success_rate"],
                "application_count": row["application_count"],
                "pattern_data": row["pattern_data"]
            })
        
        return {
            "status": "success",
            "query": {
                "agent_name": agent_name,
                "hours": hours,
                "limit": limit
            },
            "count": len(entries),
            "entries": entries
        }
        
    except Exception as e:
        logger.error(f"Error fetching pattern vectors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectors/interactions", response_model=Dict[str, Any])
async def get_interaction_vectors(
    from_agent: Optional[str] = Query(None, description="Filter by sending agent"),
    to_agent: Optional[str] = Query(None, description="Filter by receiving agent"),
    hours: int = Query(24, description="Hours of history to retrieve"),
    limit: int = Query(50, description="Maximum entries to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get recent interaction vectors (without embeddings).
    """
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = """
            SELECT id, vector_id::text, from_agent, to_agent, interaction_type,
                   occurred_at, created_at, interaction_text, interaction_summary,
                   metadata, priority
            FROM agent_interaction_vectors
            WHERE created_at >= :since
        """
        params = {"since": since, "limit": limit}
        
        if from_agent:
            query += " AND from_agent = :from_agent"
            params["from_agent"] = from_agent
        
        if to_agent:
            query += " AND to_agent = :to_agent"
            params["to_agent"] = to_agent
        
        query += " ORDER BY occurred_at DESC LIMIT :limit"
        
        result = await db.execute(text(query), params)
        
        entries = []
        for row in result.mappings():
            entries.append({
                "id": row["id"],
                "vector_id": row["vector_id"],
                "from_agent": row["from_agent"],
                "to_agent": row["to_agent"],
                "interaction_type": row["interaction_type"],
                "occurred_at": row["occurred_at"].isoformat() if row["occurred_at"] else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "interaction_text": row["interaction_text"][:500] + "..." if row["interaction_text"] and len(row["interaction_text"]) > 500 else row["interaction_text"],
                "interaction_summary": row["interaction_summary"],
                "metadata": row["metadata"],
                "priority": row["priority"]
            })
        
        return {
            "status": "success",
            "query": {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "hours": hours,
                "limit": limit
            },
            "count": len(entries),
            "entries": entries
        }
        
    except Exception as e:
        logger.error(f"Error fetching interaction vectors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Overnight Summary Endpoint
# =============================================================================

@router.get("/overnight", response_model=Dict[str, Any])
async def get_overnight_summary(
    hours: int = Query(12, description="Hours to look back (default 12 for overnight)"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a summary of overnight agent activity.
    
    Provides counts, highlights, and timeline of what happened while you were away.
    """
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        now = datetime.now(timezone.utc)
        
        summary = {
            "period": {
                "start": since.isoformat(),
                "end": now.isoformat(),
                "hours": hours
            },
            "agents": {},
            "highlights": [],
            "totals": {
                "memory_bank_writes": 0,
                "central_memory_writes": 0,
                "vector_writes": 0,
                "alerts_triggered": 0
            }
        }
        
        # Count per-agent activity in memory banks
        agent_tables = [
            ("sir_hawkington", "hawkington_memory_bank"),
            ("meth_snail", "meth_snail_memory_bank"),
            ("hamsters", "hamsters_memory_bank"),
            ("quantum_shadow_people", "qsp_memory_bank"),
            ("the_stick", "stick_memory_bank"),
            ("vic_20_sage", "vic20_memory_bank")
        ]
        
        for agent_name, table_name in agent_tables:
            try:
                result = await db.execute(
                    text(f"""
                        SELECT COUNT(*) as count,
                               COUNT(*) FILTER (WHERE importance = 'HIGH' OR importance = 'CRITICAL') as high_priority
                        FROM {table_name}
                        WHERE timestamp >= :since
                    """),
                    {"since": since}
                )
                row = result.mappings().first()
                
                summary["agents"][agent_name] = {
                    "memory_bank_writes": row["count"] or 0,
                    "high_priority_events": row["high_priority"] or 0
                }
                summary["totals"]["memory_bank_writes"] += row["count"] or 0
                
                # Get most recent event for this agent
                recent = await db.execute(
                    text(f"""
                        SELECT event_type, timestamp, details
                        FROM {table_name}
                        WHERE timestamp >= :since
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """),
                    {"since": since}
                )
                recent_row = recent.mappings().first()
                if recent_row:
                    summary["agents"][agent_name]["last_event"] = {
                        "type": recent_row["event_type"],
                        "timestamp": recent_row["timestamp"].isoformat() if recent_row["timestamp"] else None
                    }
                    
            except Exception as e:
                logger.warning(f"Could not query {table_name}: {e}")
                summary["agents"][agent_name] = {"error": str(e)}
        
        # Count central memory bank writes
        result = await db.execute(
            text("""
                SELECT COUNT(*) as count
                FROM central_memory_bank
                WHERE timestamp >= :since
            """),
            {"since": since}
        )
        row = result.mappings().first()
        summary["totals"]["central_memory_writes"] = row["count"] or 0
        
        # Count vector writes
        for table in ["agent_decision_vectors", "agent_pattern_vectors", "agent_interaction_vectors"]:
            try:
                result = await db.execute(
                    text(f"SELECT COUNT(*) as count FROM {table} WHERE created_at >= :since"),
                    {"since": since}
                )
                row = result.mappings().first()
                summary["totals"]["vector_writes"] += row["count"] or 0
            except Exception as e:
                logger.warning(f"Could not query {table}: {e}")
        
        # Generate highlights
        if summary["totals"]["memory_bank_writes"] > 0:
            most_active = max(summary["agents"].items(), 
                            key=lambda x: x[1].get("memory_bank_writes", 0) if isinstance(x[1], dict) else 0)
            summary["highlights"].append(
                f"Most active agent: {most_active[0]} with {most_active[1].get('memory_bank_writes', 0)} events"
            )
        
        high_priority_total = sum(
            a.get("high_priority_events", 0) 
            for a in summary["agents"].values() 
            if isinstance(a, dict)
        )
        if high_priority_total > 0:
            summary["highlights"].append(f"High priority events: {high_priority_total}")
        
        if summary["totals"]["vector_writes"] == 0:
            summary["highlights"].append("⚠️ No vector writes detected - check vector storage")
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error generating overnight summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Public Demo Feed - No Auth Required
# =============================================================================

@router.get("/demo-feed", response_model=Dict[str, Any])
async def get_demo_feed(
    hours: int = Query(1, description="Hours of history to retrieve"),
    limit: int = Query(20, description="Maximum entries to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Public endpoint for the terrarium demo feed.
    
    Returns human-readable agent activity narratives.
    No authentication required - this is for the landing page.
    """
    try:
        from app.services.report_generator import get_recent_activity_feed
        
        feed = await get_recent_activity_feed(db, hours=hours, limit=limit)
        
        return {
            "status": "success",
            "count": len(feed),
            "feed": feed
        }
        
    except Exception as e:
        logger.error(f"Error generating demo feed: {e}", exc_info=True)
        # Return empty feed on error, don't break the terrarium
        return {
            "status": "error",
            "count": 0,
            "feed": [],
            "message": str(e)
        }


@router.get("/demo-narrative", response_model=Dict[str, Any])
async def get_demo_narrative(
    hours: int = Query(12, description="Hours of history for narrative"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Public endpoint for overnight narrative summary.
    
    Returns a human-readable summary of what happened.
    No authentication required - this is for the landing page.
    """
    try:
        from app.services.report_generator import get_overnight_narrative
        
        narrative = await get_overnight_narrative(db, hours=hours)
        
        return {
            "status": "success",
            "narrative": narrative
        }
        
    except Exception as e:
        logger.error(f"Error generating narrative: {e}", exc_info=True)
        return {
            "status": "error",
            "narrative": {
                "period_hours": hours,
                "total_events": 0,
                "agents_active": [],
                "highlights": [],
                "narrative": "Unable to retrieve activity at this time."
            }
        }
