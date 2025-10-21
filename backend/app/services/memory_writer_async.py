# app/services/memory_writer_async.py
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_memory_banks import CentralMemoryBank  # unified table

async def log_agent_event_async(
    session: AsyncSession,
    *,
    agent_name: str,
    event_type: str,
    occurred_at: Optional[datetime] = None,
    user_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    priority: Optional[int] = None,
    correlation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
):
    occurred_at = occurred_at or datetime.now(timezone.utc)
    row = CentralMemoryBank(
        agent_name=agent_name,
        event_type=event_type,
        occurred_at=occurred_at,
        user_id=user_id,
        title=title,
        description=description,
        details=details or {},
        metadata=metadata or {},
        priority=priority,
        correlation_id=correlation_id,
        trace_id=trace_id,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row
