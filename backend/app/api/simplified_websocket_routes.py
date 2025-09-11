from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.core.websockets import get_websocket_manager
from app.api.websocket_auth import get_current_user_from_token

from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.core.database import get_async_db
from app.core.resilience import (
    get_circuit_breaker,
    get_backpressure_handler,
    with_error_recovery,
)
from app.ai_agents.agent_manager import get_agent_manager

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

# --- Persistence policy toggles ---
PERSISTENCE_POLICY = os.getenv("WS_PERSISTENCE_POLICY", "soft")  # soft | hard | hybrid
FAIL_THRESHOLD = int(os.getenv("WS_PERSISTENCE_FAIL_THRESHOLD", "3"))
FAIL_WINDOW_SEC = int(os.getenv("WS_PERSISTENCE_FAIL_WINDOW_SEC", "60"))
async def _apply_backpressure(bp) -> None:
    """
    Tolerant backpressure shim. Supports multiple handler APIs.
    Never throws. Sleeps if a positive wait is indicated.
    """
    if not bp:
        return
    try:
        wait = 0.0

        # Common pattern: should_* + get_wait_time()
        fn = getattr(bp, "should_throttle", None)
        if callable(fn) and fn():
            getter = getattr(bp, "get_wait_time", None)
            if callable(getter):
                wait = float(getter() or 0)

        # Alternate names
        if wait <= 0:
            fn = getattr(bp, "should_backoff", None)
            if callable(fn) and fn():
                getter = getattr(bp, "backoff_time", None)
                if callable(getter):
                    wait = float(getter() or 0)

        # “Just tell me the wait” style APIs
        if wait <= 0:
            getter = getattr(bp, "get_wait_time", None)
            if callable(getter):
                wait = float(getter() or 0)
        if wait <= 0:
            getter = getattr(bp, "get_delay", None)
            if callable(getter):
                wait = float(getter() or 0)
        if wait <= 0:
            # Some folks store a field
            val = getattr(bp, "wait_time", 0) or getattr(bp, "delay", 0)
            try:
                wait = float(val or 0)
            except Exception:
                wait = 0.0

        if wait > 0:
            await asyncio.sleep(wait)
    except Exception as e:
        logger.error("Backpressure handler error: %s", e, exc_info=True)

logger = logging.getLogger(__name__)
router = APIRouter()

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

# Resilience components
metrics_circuit_breaker = get_circuit_breaker("websocket_connection")
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
    return None

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
      - authenticate first (query ?token= or one-time message),
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
    user = None
    agent_manager = None
    ws_manager = get_websocket_manager()

    # failure tracking (for hybrid/hard cutoff)
    consec_failures = 0
    first_fail_ts: Optional[float] = None

    try:
        # Accept the connection once
        await websocket.accept()
        logger.info("WebSocket connection accepted for %s", client_id)

        # Authenticate: prefer query param ?token=; otherwise prompt once for {"token": "..."}
        token = (websocket.query_params.get("token") or "").replace("Bearer ", "").strip()
        if not token:
            await websocket.send_json({
                "type": "connection_established",
                "message": "Please authenticate by sending {'token': '...'}",
                "client_id": client_id,
                "timestamp": _now_iso(),
            })
            try:
                auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
                if not isinstance(auth_message, dict) or "token" not in auth_message:
                    await websocket.send_json({"type": "error", "message": "Invalid authentication message", "code": "invalid_auth_format"})
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                token = (auth_message.get("token") or "").replace("Bearer ", "").strip()
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "error", "message": "Authentication timeout", "code": "auth_timeout"})
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

        try:
            user = await get_current_user_from_token(token)
        except Exception:
            user = None

        if not user:
            await websocket.send_json({"type": "error", "message": "Invalid authentication token", "code": "invalid_token"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        logger.info("WebSocket authenticated for user %s (%s)", getattr(user, "email", None), client_id)

         # Register the connection under the circuit breaker
        try:
            if hasattr(metrics_circuit_breaker, "execute"):
                await metrics_circuit_breaker.execute(ws_manager.connect, websocket)
            else:
                await ws_manager.connect(websocket)
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
                    "message": str(e)[:500],   # enough to see signature/args
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                pass
            connection_registered = False
            logger.warning("Continuing without global WS manager for %s", client_id)

        # DB session
        db_gen = get_async_db()
        db = await db_gen.__anext__()  # async generator

        # AI Agent Manager (non-fatal on error)
        try:
            agent_manager = await get_agent_manager()
            active_agents = await agent_manager.get_active_agents()
            logger.info("AI Agent manager ready for %s - Active: %s", getattr(user, "email", None), active_agents)
        except Exception as e:
            logger.error("Failed to initialize AI Agent Manager: %s", str(e))
            agent_manager = None

        # Initial system info
        await websocket.send_json({
            "type": "system_info",
            "data": await get_system_info(),
            "message": "System Metrics WebSocket ready.",
            "timestamp": _now_iso(),
        })

        # Metrics service
        metrics_service = await SimplifiedMetricsService.get_instance()
        update_interval = 1.0  # seconds

        # === Main loop ===
        while True:
            loop_start_time = time.time()

            # Respect breaker cooling without flapping
            if hasattr(metrics_circuit_breaker, "can_attempt_connection") and not metrics_circuit_breaker.can_attempt_connection():
                wait_time = int(getattr(metrics_circuit_breaker, "get_wait_time", lambda: 5)())
                await websocket.send_json({
                    "type": "circuit_breaker",
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

                # Optional AI enrichment (non-fatal)
                if agent_manager:
                    try:
                        user_context = {
                            "user_id": str(getattr(user, "id", "")),
                            "email": getattr(user, "email", None),
                            "client_id": client_id,
                        }
                        metrics = await agent_manager.process_metrics_through_triage_engine(metrics, user_context)
                    except Exception as ai_error:
                        logger.error("AI Agent processing failed (non-critical): %s", str(ai_error))

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
                            consec_failures += 1
                            first_fail_ts = first_fail_ts or time.time()
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
                            consec_failures = 0
                            first_fail_ts = None
                            logger.debug("💾 Metrics saved for user %s", getattr(user, "email", None))

                    except Exception as db_error:
                        err_msg = str(db_error)
                        dd_inc("rebellion.ws.persist.failure", route="system_metrics", reason="exception")
                        consec_failures += 1
                        first_fail_ts = first_fail_ts or time.time()
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
                    await websocket.send_json(payload)

                    # Optional cutoff logic AFTER sending the result
                    recent_burst = (time.time() - first_fail_ts) <= FAIL_WINDOW_SEC if first_fail_ts else False
                    should_cutoff = (
                        (PERSISTENCE_POLICY == "soft") or
                        (PERSISTENCE_POLICY == "hybrid" and consec_failures >= FAIL_THRESHOLD and recent_burst)
                    )
                    if should_cutoff:
                        try:
                            await websocket.send_json({
                                "type": "ingest_down",
                                "message": "DB persistence failing; closing socket",
                                "failures": consec_failures,
                                "window_sec": FAIL_WINDOW_SEC,
                                "policy": PERSISTENCE_POLICY,
                                "timestamp": _now_iso(),
                            })
                        except Exception:
                            pass
                        await websocket.close(code=1011)
                        break

                # transport/compute path success for this iteration
                if hasattr(metrics_circuit_breaker, "record_success"):
                    metrics_circuit_breaker.record_success()

                # Backpressure for outbound stream
                if metrics_backpressure.should_throttle():
                    wait = metrics_backpressure.get_wait_time()
                    if wait > 0:
                        await asyncio.sleep(wait)

                # Send latest metrics update to client
                try:
                    out_msg = {
                        "type": "metrics_update",
                        "timestamp": _now_iso(),
                        "data": metrics,
                    }
                    json.dumps(out_msg, default=str)  # ensure serializable
                    await websocket.send_json(out_msg)
                except TypeError as e:
                    # Prevent accidental coroutine leakage in the payload
                    logger.error("Serialization error: %s", str(e))
                    await websocket.send_json({
                        "type": "metrics_error",
                        "timestamp": _now_iso(),
                        "message": "Metrics processing error",
                    })

                # Handle small control messages from client (non-blocking)
                try:
                    msg_timeout = min(0.5, update_interval / 2)
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=msg_timeout)
                    try:
                        msg = json.loads(raw)
                        msg_type = msg.get("type", "")
                        msg_data = msg.get("data", {})

                        if msg_type == "ping":
                            await websocket.send_json({"type": "pong", "timestamp": _now_iso()})
                        elif msg_type == "set_interval":
                            try:
                                requested = float(msg_data.get("interval", update_interval))
                                update_interval = max(1.0, min(10.0, requested))
                            except (ValueError, TypeError):
                                pass
                            await websocket.send_json({
                                "type": "interval_update",
                                "interval": update_interval,
                                "message": f"Update interval set to {update_interval} seconds",
                            })
                        elif msg_type == "request_system_info":
                            await websocket.send_json({"type": "system_info", "data": await get_system_info()})
                        elif msg_type == "reset_circuit_breaker":
                            if hasattr(metrics_circuit_breaker, "reset"):
                                metrics_circuit_breaker.reset()
                            if hasattr(metrics_service, "reset_circuit_breakers"):
                                await metrics_service.reset_circuit_breakers()
                            await websocket.send_json({"type": "circuit_breaker_reset", "message": "Breakers reset"})
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
                    await websocket.send_json({"type": "error", "message": f"Internal error: {str(e)}", "timestamp": _now_iso()})
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
        try:
            if db:
                await db.close()
        except Exception:
            logger.error("Error closing database connection", exc_info=True)
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info("WebSocket connection closed for %s", client_id)
