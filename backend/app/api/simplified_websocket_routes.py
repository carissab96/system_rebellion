from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from websockets.exceptions import ConnectionClosedError
from app.api.websockets import get_websocket_manager
from app.api.websocket_auth import get_current_user_from_token

from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.core.database import get_async_db
from app.core.resilience import (
    get_circuit_breaker,
    get_backpressure_handler,
    with_error_recovery,
    ErrorSeverity,
    error_recovery,
    RecoveryAction,
    RecoveryStrategy
)

import asyncio
import logging
from datetime import datetime, timezone
import time
import json
import socket
import platform
import psutil
import os
from typing import Dict, Any, Optional, Union

# Optional Datadog statsd (no-op if unavailable)
try:
    from datadog import statsd as _dd
    def dd_inc(metric: str, **tags):  # type: ignore
        _dd.increment(metric, tags=[f"{k}:{v}" for k, v in tags.items()])
except Exception:
    def dd_inc(*_args, **_kwargs):  # type: ignore
        return

# preferred repo accessor (singleton)
try:
    from app.services.metrics_repository import get_metrics_repository
except Exception:
    get_metrics_repository = None  # type: ignore

# Import agent memory bank models
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_memory_banks import (
    SirHawkingtonMemoryBank,
    TheStickMemoryBank,
    MethSnailMemoryBank,
    HamstersMemoryBank,
    QuantumShadowPeopleMemoryBank,
    VIC20MemoryBank,
    CentralMemoryBank
)

logger = logging.getLogger(__name__)
router = APIRouter()

if not getattr(error_recovery, "recovery_strategies", {}).get("websocket", {}).get("ConnectionClosedError"):
    error_recovery.register_strategy(
        component="websocket",
        error_type=ConnectionClosedError,
        recovery_action=RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            max_retries=3,
            retry_delay=2.0,
            exponential_backoff=True
        )
    )

async def safe_websocket_send(websocket: WebSocket, data: dict) -> bool:
    """
    Safely send data to WebSocket, handling closed connections gracefully.
    Returns True if sent successfully, False if connection was closed.
    """
    try:
        await websocket.send_json(data)
        return True
    except (ConnectionClosedError, RuntimeError) as e:
        logger.debug("WebSocket connection closed during send, skipping message: %s", str(e))
        return False
    except TypeError as e:
        logger.error("JSON serialization error: %s. Data keys: %s", str(e), list(data.keys()))
        # Log which field is problematic
        for key, value in data.items():
            try:
                import json
                json.dumps(value)
            except TypeError:
                logger.error(f"Field '{key}' contains non-serializable data")
        return False
    except Exception as e:
        logger.error("Unexpected error sending WebSocket message: %s", str(e))
        return False

async def fetch_latest_agent_memories(db: AsyncSession, user_id: str) -> Dict[str, Any]:
    """
    Fetch the latest memory bank entry for each agent from CENTRAL memory bank.
    Returns dict with agent_name -> full memory data
    """
    agent_memories = {}
    
    # Agent names to query
    agent_names = [
        "sir_hawkington",
        "the_stick", 
        "meth_snail",
        "hamsters",
        "quantum_shadow_people",
        "vic20_sage"
    ]
    
    for agent_name in agent_names:
        try:
            # Query latest memory for this agent from CENTRAL memory bank
            stmt = (
                select(CentralMemoryBank)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.agent_name == agent_name)
                .order_by(CentralMemoryBank.occurred_at.desc())
                .limit(1)
            )
            result = await db.execute(stmt)
            memory = result.scalars().first()
            
            if memory:
                # Convert SQLAlchemy model to dict
                memory_dict = {
                    "memory_id": str(memory.memory_id),
                    "timestamp": memory.occurred_at.isoformat() if memory.occurred_at else None,
                    "user_id": memory.user_id,
                    "agent_name": memory.agent_name,
                    "event_type": memory.event_type,
                    "details": memory.details,
                    "priority": memory.priority,
                    "metadata": memory.__dict__.get('metadata'),  # Get metadata column directly from __dict__
                }
                
                # Add all other fields
                for column in CentralMemoryBank.__table__.columns:
                    col_name = column.name
                    if col_name not in memory_dict and hasattr(memory, col_name):
                        value = getattr(memory, col_name)
                        # Convest)rt datetime to ISO string
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        memory_dict[col_name] = value
                
                agent_memories[agent_name] = memory_dict
                logger.debug(f"✅ Loaded memory for {agent_name}: {memory.event_type}")
                
        except Exception as e:
            logger.debug(f"Could not fetch memory for {agent_name}: {e}")
            continue
    
    return agent_memories

# --- Persistence policy toggles ---
# Per prompt: default is SOFT, and soft means "do not close on DB failure".
PERSISTENCE_POLICY = os.getenv("WS_PERSISTENCE_POLICY", "soft").lower()  # soft | hard | hybrid
FAIL_THRESHOLD = int(os.getenv("WS_PERSISTENCE_FAIL_THRESHOLD", "3"))
FAIL_WINDOW_SEC = int(os.getenv("WS_PERSISTENCE_FAIL_WINDOW_SEC", "60"))

async def _apply_backpressure(bp) -> None:
    """
    Backpressure shim with preference for v2-style get_overall_pressure().
    Falls back to older should_throttle/get_wait_time signatures if needed.
    Never throws.
    """
    if not bp:
        return
    try:
        # Preferred: a single pressure scalar
        gop = getattr(bp, "get_overall_pressure", None)
        if callable(gop):
            try:
                pressure = float(gop() or 0)
            except Exception:
                pressure = 0.0
            if pressure > 0:
                # gentle linear sleep; cap small
                await asyncio.sleep(min(0.5, 0.01 * pressure))
                return

        # Legacy APIs
        wait = 0.0
        fn = getattr(bp, "should_throttle", None)
        if callable(fn) and fn():
            getter = getattr(bp, "get_wait_time", None)
            if callable(getter):
                try:
                    wait = float(getter() or 0)
                except Exception:
                    wait = 0.0

        if wait <= 0:
            fn = getattr(bp, "should_backoff", None)
            if callable(fn) and fn():
                getter = getattr(bp, "backoff_time", None)
                if callable(getter):
                    try:
                        wait = float(getter() or 0)
                    except Exception:
                        wait = 0.0

        if wait <= 0:
            for name in ("get_wait_time", "get_delay"):
                getter = getattr(bp, name, None)
                if callable(getter):
                    try:
                        wait = float(getter() or 0)
                        break
                    except Exception:
                        wait = 0.0

        if wait <= 0:
            val = getattr(bp, "wait_time", 0) or getattr(bp, "delay", 0)
            try:
                wait = float(val or 0)
            except Exception:
                wait = 0.0

        if wait > 0:
            await asyncio.sleep(wait)

    except Exception as e:
        logger.error("Backpressure handler error: %s", e, exc_info=True)

async def get_system_info() -> Dict[str, Any]:
    """Return real host info. On failure, return explicit error object."""
    try:
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "memory_total": psutil.virtual_memory().total,
            "boot_time": datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc).isoformat(),
            "python_version": platform.python_version(),
        }
    except Exception as e:
        logger.error("Error getting system info: %s", str(e), exc_info=True)
        return {"error": True, "message": "Failed to retrieve system information"}

# Resilience components (names are part of the public contract)
metrics_circuit_breaker = get_circuit_breaker("system_metrics_ws")
metrics_backpressure = get_backpressure_handler("websocket_messages")

def _parse_number(v: Any) -> Optional[float]:
    """Parse numeric inputs without inventing values. Returns None if unparseable."""
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace(",", "")
        if s.endswith("%"):
            s = s[:-1]
        try:
            return float(s)
        except Exception:
            return None
    if isinstance(v, dict):
        for k in ("percent", "percentage", "value", "avg", "average", "mean", "current", "usage"):
            if k in v:
                return _parse_number(v[k])
        return None
    if isinstance(v, list) and v:
        return _parse_number(v[0])

def _get_in(d: Dict[str, Any], *paths: str) -> Optional[Any]:
    """Safely fetch nested values via dotted paths or top-level keys."""
    for p in paths:
        cur: Any = d
        parts = p.split(".")
        ok = True
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok:
            return cur
        if p in d:
            return d[p]
    return None

def _extract_metrics(m: Dict[str, Any]) -> Dict[str, Optional[Union[float, int, Dict[str, Any]]]]:
    """Normalize incoming metrics to flat fields expected by the repo, without defaults."""
    cpu = _parse_number(_get_in(m, "cpu_usage", "cpu.percent"))
    mem = _parse_number(_get_in(m, "memory_usage", "memory.percent"))
    disk = _parse_number(_get_in(m, "disk_usage", "disk.percent"))
    pc_f = _parse_number(_get_in(m, "process_count", "procs", "processes"))
    pc = int(pc_f) if pc_f is not None else None

    net = _get_in(m, "network", "net", "network_data")
    if net is not None and not isinstance(net, dict):
        net = None

    return {
        "cpu_usage": cpu,
        "memory_usage": mem,
        "disk_usage": disk,
        "process_count": pc,
        "network_data": net,
    }

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@router.websocket("/ws/system-metrics")
@with_error_recovery(component="websocket", operation="system_metrics_socket")
async def system_metrics_socket(websocket: WebSocket):
    """
    System Metrics WebSocket:
      - authenticate via query ?token=... only (do NOT accept token in first message),
      - register once (breaker-guarded),
      - persist metrics with a single ACK/NACK,
      - no fake data, no duplicate sends.
    """

    # If the circuit is already open, tell the client and close politely.
    if hasattr(metrics_circuit_breaker, "is_open") and metrics_circuit_breaker.is_open():
        await websocket.accept()
        retry = 30
        if hasattr(metrics_circuit_breaker, "get_wait_time"):
            try:
                retry = int(metrics_circuit_breaker.get_wait_time() or 30)
            except Exception:
                retry = 30
        await websocket.send_json({"type": "circuit_open", "retry_after": retry})
        await websocket.close(code=1013, reason=f"circuit_open; retry_after={retry}")
        return

    client_id = f"client_{id(websocket)}"
    connection_registered = False
    db = None
    db_gen = None
    db_needs_cleanup = False
    user = None
    agent_manager = None
    ws_manager = get_websocket_manager()

    # failure tracking (for hybrid/hard cutoff)
    consec_failures = 0
    first_fail_ts: Optional[float] = None

    try:
        ws_start = time.time()
        
        # Accept connection first
        await websocket.accept()
        logger.info("WebSocket connection accepted for %s", client_id)
        
        # THEN authenticate via query param
        auth_start = time.time()
        token = (websocket.query_params.get("token") or "").replace("Bearer ", "").strip()
        if not token:
            logger.warning("WebSocket connection rejected: missing token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            user = await get_current_user_from_token(token)
        except Exception as e:
            logger.error("Auth failed: %s", str(e))
            user = None

        if not user:
            logger.warning("WebSocket connection rejected: invalid token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        logger.info("⏱️ WebSocket authenticated for user %s (%s) - Auth took %.2fms", 
                   getattr(user, "email", None), client_id, (time.time() - auth_start)*1000)
        logger.info("WebSocket connection accepted for %s (%.2fms)", client_id, (time.time() - ws_start)*1000)

        # Register the connection under the circuit breaker
        # Note: websocket is already accepted above, so just add to manager
        try:
            # Don't call ws_manager.connect() as it tries to accept() again
            # Just add to active connections directly
            ws_manager.active_connections.add(websocket)
            connection_registered = True
            if hasattr(metrics_circuit_breaker, "reset"):
                metrics_circuit_breaker.reset()
            logger.info("✅ WebSocket registered for %s", client_id)
        except Exception as e:
            # Don’t kill the socket; run in “local-only” mode and tell the client exactly why.
            logger.error("❌ WebSocket registration failed for %s: %s", client_id, str(e), exc_info=True)
            try:
                await websocket.send_json({
                    "type": "registration_error",
                    "message": str(e)[:500],
                    "timestamp": _now_iso(),
                })
            except Exception:
                pass
            connection_registered = False
            logger.warning("Continuing without global WS manager for %s", client_id)

        # DB session - use async context manager properly
        db_gen = get_async_db()
        db = await db_gen.__anext__()  # async generator
        db_needs_cleanup = True

        # Send immediate handshake FIRST (don't wait for agent manager)
        handshake_start = time.time()
        sent = await safe_websocket_send(websocket, {
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": _now_iso(),
        })
        if not sent:
            logger.warning("Failed to send connection_established handshake")
        else:
            logger.info("✅ Sent connection_established to %s (%.2fms from WS start)", 
                       client_id, (time.time() - ws_start)*1000)
            # Small delay to ensure message is sent before next one
            await asyncio.sleep(0.1)
        
        # Distributed Agent Manager (should already be initialized at startup)
        agent_manager = None
        try:
            from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
            agent_manager = get_distributed_manager()
            if agent_manager and agent_manager.initialized:
                logger.info("✅ Distributed agent manager ready for %s", getattr(user, "email", None))
            else:
                logger.warning("⚠️ Distributed agent manager not initialized yet")
                agent_manager = None
        except Exception as e:
            logger.error("❌ Failed to get Distributed Agent Manager: %s", str(e))
            agent_manager = None

        # System info
        sent = await safe_websocket_send(websocket, {
            "type": "system_info",
            "data": await get_system_info(),
            "message": "System Metrics WebSocket ready.",
            "timestamp": _now_iso(),
        })
        if not sent:
            logger.warning("Failed to send system_info")
        else:
            logger.info("✅ Sent system_info to %s", client_id)
            # Small delay to ensure message is sent before next one
            await asyncio.sleep(0.1)

        # Send initial agent roster (so frontend knows which agents are active)
        if agent_manager and agent_manager.initialized:
            try:
                active_agents = agent_manager.get_active_agents()
                logger.info("📋 Active agents to send: %s", active_agents)
                
                roster_msg = {
                    "type": "agent_roster",
                    "active_agents": active_agents,
                    "count": len(active_agents),
                    "timestamp": _now_iso(),
                }
                
                sent = await safe_websocket_send(websocket, roster_msg)
                if sent:
                    logger.info("✅ Sent agent roster to %s: %s", client_id, active_agents)
                else:
                    logger.warning("Failed to send agent_roster - connection may be closed")
            except Exception as e:
                logger.error("Error sending agent roster: %s", str(e), exc_info=True)

        # Metrics service
        metrics_service = await SimplifiedMetricsService.get_instance()
        update_interval = 5.0  # seconds (raised from 1s to reduce load)

        # Throttle AI triage to every 10 seconds (not every loop)
        last_triage_time = 0.0
        triage_interval = 10.0  # Only run triage every 10 seconds
        cached_agent_insights: Dict[str, Any] = {}

        # Cache agent memories to avoid hammering DB each loop
        memory_refresh_interval = 30.0
        last_memory_sync = 0.0
        cached_agent_memories: Dict[str, Any] = {}

        # === Main loop ===
        while True:
            loop_start_time = time.time()

            # Respect breaker cooling without flapping
            if hasattr(metrics_circuit_breaker, "can_attempt_connection") and not metrics_circuit_breaker.can_attempt_connection():
                wait_time = int(getattr(metrics_circuit_breaker, "get_wait_time", lambda: 5)())
                await safe_websocket_send(websocket, {
                    "type": "circuit_open",
                    "status": "open",
                    "message": f"Cooling down for {wait_time}s",
                    "retry_after": wait_time,
                    "timestamp": _now_iso(),
                })
                await asyncio.sleep(min(wait_time, update_interval))
                continue

            try:
                # Collect metrics (real values only)
                metrics = await metrics_service.get_metrics()

                # Optional AI enrichment (non-fatal) - THROTTLED to every 10 seconds
                agent_insights: Dict[str, Any] = {}

                # Fetch latest agent memory bank data from database on a slower cadence
                if db and user:
                    should_refresh_memories = (
                        (loop_start_time - last_memory_sync) >= memory_refresh_interval or not cached_agent_memories
                    )

                    if should_refresh_memories:
                        try:
                            agent_memories_from_db = await fetch_latest_agent_memories(
                                db, str(getattr(user, "id", ""))
                            )
                            cached_agent_memories = {
                                agent_name: {
                                    "status": "active",
                                    **memory_data
                                }
                                for agent_name, memory_data in agent_memories_from_db.items()
                            }
                            last_memory_sync = loop_start_time
                            logger.debug("📚 Refreshed agent memories (%d entries)", len(cached_agent_memories))
                        except Exception as e:
                            logger.error("Failed to fetch agent memories: %s", str(e))
                    else:
                        logger.debug("⏳ Using cached agent memories (%d entries)", len(cached_agent_memories))

                # Start insights with cached memories (deep copy to avoid mutation)
                if cached_agent_memories:
                    agent_insights = {
                        name: dict(data)
                        for name, data in cached_agent_memories.items()
                    }
                else:
                    agent_insights = {}
                
                # Get current status from all distributed agents
                if agent_manager and agent_manager.initialized:
                    try:
                        for agent_name in agent_manager.get_active_agents():
                            agent = agent_manager.get_agent(agent_name)
                            if agent and hasattr(agent, 'get_agent_status'):
                                agent_status = agent.get_agent_status()
                                if agent_name not in agent_insights:
                                    agent_insights[agent_name] = {}
                                agent_insights[agent_name].update({
                                    "status": "active",
                                    "distributed": getattr(agent, 'is_distributed', False),
                                    **agent_status
                                })
                        logger.debug("📊 Updated insights for %d distributed agents", len(agent_insights))
                    except Exception as e:
                        logger.error("Failed to get distributed agent status: %s", str(e))
                
                # Only run expensive triage if enough time has passed
                should_run_triage = (loop_start_time - last_triage_time) >= triage_interval
                
                if agent_manager and should_run_triage:
                    try:
                        user_context = {
                            "user_id": str(getattr(user, "id", "")),
                            "email": getattr(user, "email", None),
                            "client_id": client_id,
                        }
                        triage_result = await agent_manager.process_metrics_through_triage_engine(metrics, user_context)
                        last_triage_time = loop_start_time  # Update last run time
        
                        # 🔥 DEBUG: Log what triage returned
                        logger.info("🎯 TRIAGE RESULT KEYS: %s", list(triage_result.keys()))
                        logger.info("🎯 DISPOSITION: %s", triage_result.get("disposition"))
                        logger.info("🎯 AGENT_DISPATCH: %s", triage_result.get("agent_dispatch", []))
        
                        # Extract agent insights from triage result
                        triage_decision = triage_result.get("triage_decision")
                        confidence = 0
                        
                        # Convert dataclass to dict if needed
                        if triage_decision and hasattr(triage_decision, "__dataclass_fields__"):
                            from dataclasses import asdict
                            from datetime import datetime
                            
                            # Get confidence before conversion
                            confidence = getattr(triage_decision, "confidence", 0)
                            
                            # Convert to dict
                            triage_decision = asdict(triage_decision)
                            
                            # Convert ALL datetime objects to ISO strings (recursive)
                            def serialize_datetimes(obj):
                                if isinstance(obj, datetime):
                                    return obj.isoformat()
                                elif isinstance(obj, dict):
                                    return {k: serialize_datetimes(v) for k, v in obj.items()}
                                elif isinstance(obj, list):
                                    return [serialize_datetimes(item) for item in obj]
                                return obj
                            
                            triage_decision = serialize_datetimes(triage_decision)
                        
                        # Merge triage data into existing Sir Hawkington memory data
                        if "sir_hawkington" not in agent_insights:
                            agent_insights["sir_hawkington"] = {"status": "active"}
                        
                        agent_insights["sir_hawkington"].update({
                            "triage": triage_decision or {},
                            "disposition": triage_result.get("disposition"),
                            "routed_by": triage_result.get("routed_by"),
                            "confidence": confidence,
                        })
        
                        # If VIC-20 was involved, merge plan data
                        if "vic20_plan" in triage_result:
                            if "vic20_sage" not in agent_insights:
                                agent_insights["vic20_sage"] = {"status": "active"}
                            agent_insights["vic20_sage"]["plan"] = triage_result["vic20_plan"]
        
                        # If agents were dispatched, merge their results
                        if "results" in triage_result:
                            for result in triage_result["results"]:
                                if isinstance(result, dict) and "agent" in result:
                                    agent_key = result["agent"]
                                    if agent_key not in agent_insights:
                                        agent_insights[agent_key] = {"status": "active"}
                                    agent_insights[agent_key]["result"] = result.get("result", {})
        
                        # Cache the insights for reuse in subsequent loops
                        cached_agent_insights = agent_insights
                        logger.info("✅ Extracted %d agent insights (cached for reuse)", len(agent_insights))
                        logger.info("🔍 Agent insights keys: %s", list(agent_insights.keys()))
                        for agent_name, data in agent_insights.items():
                            logger.info("🔍 %s data: %s", agent_name, str(data)[:200])
        
                    except Exception as ai_error:
                        logger.error("AI Agent processing failed (non-critical): %s", str(ai_error), exc_info=True)
                else:
                    # Reuse cached insights if triage didn't run this loop
                    agent_insights = cached_agent_insights

                # Persist (single ACK/NACK)
                if user and db and get_metrics_repository:
                    ok = False
                    err_msg: Optional[str] = None
                    saved_id: Optional[str] = None

                    try:
                        flat = _extract_metrics(metrics)
                        missing = [k for k in ("cpu_usage", "memory_usage", "disk_usage") if flat.get(k) is None]

                        if missing:
                            err_msg = f"Missing required metrics: {', '.join(missing)}"
                            dd_inc("rebellion.ws.persist.failure", route="system_metrics", reason="missing_required")
                        else:
                            repo = await get_metrics_repository()
                            saved = await repo.create_metric(
                                db=db,
                                user_id=str(getattr(user, "id", "")),
                                cpu_usage=flat["cpu_usage"],
                                memory_usage=flat["memory_usage"],
                                disk_usage=flat["disk_usage"],
                                network_data=flat["network_data"],
                                process_count=flat["process_count"],
                                additional_metrics=metrics,
                            )
                            saved_id = str(getattr(saved, "id", ""))
                            ok = True
                            dd_inc("rebellion.ws.persist.success", route="system_metrics")
                            logger.debug("💾 Metrics saved for user %s", getattr(user, "email", None))

                    except Exception as db_error:
                        err_msg = str(db_error)
                        dd_inc("rebellion.ws.persist.failure", route="system_metrics", reason="exception")
                        logger.error("DB save failed: %s", err_msg, exc_info=True)

                    # One send, always
                    payload: Dict[str, Any] = {
                        "type": "persist_result",
                        "ok": ok,
                        "timestamp": _now_iso(),
                    }
                    if ok:
                        payload["id"] = saved_id
                    else:
                        payload["error"] = err_msg
                    await safe_websocket_send(websocket, payload)

                    # SOFT policy: do NOT close on persist failure. Ever.
                    if PERSISTENCE_POLICY in ("hard", "hybrid"):
                        # failure counting only applies to non-soft modes
                        if not ok:
                            nonlocal_fail_ts = locals().get("first_fail_ts")
                            nonlocal_consec = locals().get("consec_failures")
                            # bump counters in outer scope
                        consec_failures += (0 if ok else 1)
                        first_fail_ts = first_fail_ts or (0 if ok else time.time())

                        recent_burst = (time.time() - first_fail_ts) <= FAIL_WINDOW_SEC if first_fail_ts else False
                        should_cutoff = (
                            (PERSISTENCE_POLICY == "hard") or
                            (PERSISTENCE_POLICY == "hybrid" and consec_failures >= FAIL_THRESHOLD and recent_burst)
                        )
                        if (not ok) and should_cutoff:
                            try:
                                sent = await safe_websocket_send(websocket, {
                                    "type": "ingest_down",
                                    "message": "DB persistence failing; closing socket",
                                    "failures": consec_failures,
                                    "window_sec": FAIL_WINDOW_SEC,
                                    "policy": PERSISTENCE_POLICY,
                                    "timestamp": _now_iso(),
                                })
                                if not sent:
                                    logger.debug("Failed to send ingest_down message")
                            except Exception:
                                pass
                            await websocket.close(code=1011)
                            break
                    else:
                        # soft: reset failure counters on success, ignore otherwise
                        if ok:
                            consec_failures = 0
                            first_fail_ts = None

                # transport/compute path success for this iteration
                if hasattr(metrics_circuit_breaker, "record_success"):
                    metrics_circuit_breaker.record_success()

                # Preferred backpressure model with compatibility fallback
                await _apply_backpressure(metrics_backpressure)

                # Send latest metrics update to client (with agent data, insights, and events embedded)
                try:
                    # Get recent insights and events from buffer
                    recent_insights = ws_manager.get_recent_insights(limit=10)
                    recent_events = ws_manager.get_recent_events(limit=10)
                    
                    # Log what we're about to send
                    logger.info(f"📊 Metrics structure: {list(metrics.keys()) if isinstance(metrics, dict) else type(metrics)}")
                    logger.info(f"📊 Metrics size: {len(str(metrics))} chars")
                    logger.info(f"🤖 Agent insights: {list(agent_insights.keys())}")
                    logger.info(f"💡 Insights: {len(recent_insights)}, Events: {len(recent_events)}")
                    
                    out_msg = {
                        "type": "system_update",  # Renamed from metrics_update to reflect unified payload
                        "timestamp": _now_iso(),
                        "metrics": metrics,  # Renamed from 'data' for clarity
                        "agents": agent_insights,  # Agent memory banks and triage data
                        "recent_insights": recent_insights,  # Last 10 inter-agent communications
                        "recent_events": recent_events,  # Last 10 personality events
                    }
                    sent = await safe_websocket_send(websocket, out_msg)
                    if not sent:
                        logger.warning("❌ Failed to send system_update - connection likely closed")
                    else:
                        logger.info(f"✅ Successfully sent {len(str(out_msg))} char payload")
                    
                    # NOTE: This unified endpoint now includes all agent data, insights, and events
                    # Separate agent-insights and agent-events endpoints are deprecated
                except TypeError as e:
                    # Prevent accidental coroutine leakage in the payload
                    logger.error("Serialization error: %s", str(e))
                    sent = await safe_websocket_send(websocket, {
                        "type": "error",
                        "timestamp": _now_iso(),
                        "message": "Metrics processing error",
                    })
                    if not sent:
                        logger.debug("Failed to send error message - connection likely closed")

                # Handle small control messages from client (non-blocking)
                try:
                    msg_timeout = min(0.5, update_interval / 2)
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=msg_timeout)
                    try:
                        msg = json.loads(raw)
                        msg_type = msg.get("type", "")
                        msg_data = msg.get("data", {})

                        if msg_type == "ping":
                            await safe_websocket_send(websocket, {"type": "pong", "timestamp": _now_iso()})
                        elif msg_type == "set_interval":
                            try:
                                requested = float(msg_data.get("interval", update_interval))
                                update_interval = max(1.0, min(10.0, requested))
                            except (ValueError, TypeError):
                                pass
                            await safe_websocket_send(websocket, {
                                "type": "interval_update",
                                "interval": update_interval,
                                "message": f"Update interval set to {update_interval} seconds",
                            })
                        elif msg_type == "request_system_info":
                            await safe_websocket_send(websocket, {"type": "system_info", "data": await get_system_info()})
                        elif msg_type == "reset_circuit_breaker":
                            if hasattr(metrics_circuit_breaker, "reset"):
                                metrics_circuit_breaker.reset()
                            if hasattr(metrics_service, "reset_circuit_breakers"):
                                await metrics_service.reset_circuit_breakers()
                            await safe_websocket_send(websocket, {"type": "circuit_breaker_reset", "message": "Breakers reset"})
                    except json.JSONDecodeError:
                        logger.warning("Received non-JSON message from client %s", client_id)
                except asyncio.TimeoutError:
                    pass  # no control msg this tick

                # Maintain consistent update cadence
                elapsed = time.time() - loop_start_time
                await asyncio.sleep(max(0.1, update_interval - elapsed))

            except WebSocketDisconnect:
                logger.info("WebSocket for %s disconnected", client_id)
                if hasattr(metrics_circuit_breaker, "record_failure"):
                    metrics_circuit_breaker.record_failure()
                break
            except Exception as e:
                logger.error("Error in WebSocket loop for %s: %s", client_id, str(e), exc_info=True)
                if hasattr(metrics_circuit_breaker, "record_failure"):
                    metrics_circuit_breaker.record_failure()
                try:
                    sent = await safe_websocket_send(websocket, {"type": "error", "message": f"Internal error: {str(e)}", "timestamp": _now_iso()})
                    if not sent:
                        logger.debug("Failed to send error message to client")
                except Exception:
                    pass
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                break

    finally:
        # Cleanup
        try:
            if connection_registered:
                await get_websocket_manager().disconnect(websocket)  # idempotent
        except Exception:
            pass
        
        # Properly close DB session and return to pool
        try:
            if db_needs_cleanup and db_gen:
                try:
                    await db_gen.aclose()  # Properly close the async generator
                except Exception as e:
                    logger.error("Error closing database generator: %s", str(e))
        except Exception:
            logger.error("Error in database cleanup", exc_info=True)
        
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info("WebSocket connection closed for %s", client_id)


@router.websocket("/ws/demo-metrics")
async def demo_metrics_socket(websocket: WebSocket):
    """
    Public Demo WebSocket - No authentication required.
    Streams real system metrics and agent status for landing page terrarium.
    Read-only: no persistence, no user context, no triage.
    """
    client_id = f"demo_{id(websocket)}"
    
    try:
        await websocket.accept()
        logger.info("Demo WebSocket connection accepted for %s", client_id)
        
        # Send handshake
        await safe_websocket_send(websocket, {
            "type": "connection_established",
            "client_id": client_id,
            "mode": "demo",
            "timestamp": _now_iso(),
        })
        
        # System info
        await safe_websocket_send(websocket, {
            "type": "system_info",
            "data": await get_system_info(),
            "message": "Demo Metrics WebSocket ready.",
            "timestamp": _now_iso(),
        })
        
        # Get distributed agent manager for real agent status
        agent_manager = None
        try:
            from app.ai_agents.distributed.distributed_agent_manager import get_distributed_manager
            agent_manager = get_distributed_manager()
            if agent_manager and agent_manager.initialized:
                logger.info("✅ Demo: Distributed agent manager ready")
            else:
                agent_manager = None
        except Exception as e:
            logger.warning("Demo: Agent manager not available: %s", str(e))
        
        # Send agent roster
        if agent_manager and agent_manager.initialized:
            try:
                active_agents = agent_manager.get_active_agents()
                await safe_websocket_send(websocket, {
                    "type": "agent_roster",
                    "active_agents": active_agents,
                    "count": len(active_agents),
                    "timestamp": _now_iso(),
                })
            except Exception as e:
                logger.error("Demo: Error sending agent roster: %s", str(e))
        
        # Metrics service
        metrics_service = await SimplifiedMetricsService.get_instance()
        update_interval = 5.0
        
        # Main loop - simplified, no persistence
        while True:
            loop_start = time.time()
            
            try:
                # Get real metrics
                metrics = await metrics_service.get_metrics()
                
                # Get agent insights (status only, no triage)
                agent_insights: Dict[str, Any] = {}
                
                if agent_manager and agent_manager.initialized:
                    try:
                        for agent_name in agent_manager.get_active_agents():
                            agent = agent_manager.get_agent(agent_name)
                            if agent and hasattr(agent, 'get_agent_status'):
                                agent_status = agent.get_agent_status()
                                agent_insights[agent_name] = {
                                    "status": "active",
                                    "is_active": True,
                                    **agent_status
                                }
                    except Exception as e:
                        logger.error("Demo: Failed to get agent status: %s", str(e))
                
                # Fallback: if no agents from manager, provide demo presence
                if not agent_insights:
                    agent_insights = {
                        "sir_hawkington": {"status": "active", "is_active": True, "monocle_state": "POLISHED"},
                        "hamsters": {"status": "active", "is_active": True, "beer_level": "OPTIMAL"},
                        "quantum_shadow_people": {"status": "active", "is_active": True, "paranoia_level": 42},
                        "the_stick": {"status": "active", "is_active": True, "anxiety_spikes": 3},
                        "vic20_sage": {"status": "active", "is_active": True},
                        "meth_snail": {"status": "active", "is_active": True},
                    }
                
                # Send update
                sent = await safe_websocket_send(websocket, {
                    "type": "system_update",
                    "timestamp": _now_iso(),
                    "metrics": metrics,
                    "agents": agent_insights,
                    "mode": "demo",
                })
                
                if not sent:
                    logger.info("Demo: Client %s disconnected", client_id)
                    break
                
                # Handle ping/pong
                try:
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
                    msg = json.loads(raw)
                    if msg.get("type") == "ping":
                        await safe_websocket_send(websocket, {"type": "pong", "timestamp": _now_iso()})
                except asyncio.TimeoutError:
                    pass
                except json.JSONDecodeError:
                    pass
                
                # Maintain cadence
                elapsed = time.time() - loop_start
                await asyncio.sleep(max(0.1, update_interval - elapsed))
                
            except WebSocketDisconnect:
                logger.info("Demo WebSocket %s disconnected", client_id)
                break
            except Exception as e:
                logger.error("Demo WebSocket error: %s", str(e))
                break
    
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info("Demo WebSocket closed for %s", client_id)
