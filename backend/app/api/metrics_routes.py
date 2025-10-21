from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.metrics_repository import get_metrics_repository

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Metrics"])


# ----------------------------
# Parsing helpers (no fake data)
# ----------------------------
def _parse_number(v: Any) -> Optional[float]:
    """
    Parse a number WITHOUT inventing values.
    Accepts numbers, numeric strings (incl. '85%'), dicts with value-like keys, and lists (first element).
    Returns float or None.
    """
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
    """
    Safely fetch nested values via dotted paths or exact keys.
    """
    for p in paths:
        cur: Any = d
        ok = True
        for part in p.split("."):
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


def _row_to_dict(r) -> Dict[str, Any]:
    return {
        "id": str(getattr(r, "id", "")) if getattr(r, "id", None) is not None else None,
        "user_id": getattr(r, "user_id", None),
        "timestamp": getattr(r, "timestamp", None).isoformat() if getattr(r, "timestamp", None) else None,
        "cpu_usage": getattr(r, "cpu_usage", None),
        "memory_usage": getattr(r, "memory_usage", None),
        "disk_usage": getattr(r, "disk_usage", None),
        "process_count": getattr(r, "process_count", None),
        "network": getattr(r, "network", None),
        "additional_metrics": getattr(r, "additional_metrics", None),
    }


# ----------------------------
# Routes
# ----------------------------
@router.get("/system")
async def get_system_snapshot(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns the most recent SystemMetrics snapshot for the **current user**.
    Honest output:
      - If no rows: latest=null, count=0
      - JSON columns are returned as-is (dict) if present, else null
    """
    if not current_user or "id" not in current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    repo = await get_metrics_repository()
    rows = await repo.get_latest_metrics_for_user(db, user_id=current_user["id"], limit=1)
    latest = rows[0] if rows else None

    return JSONResponse({
        "user_id": str(current_user["id"]),
        "count": len(rows),
        "latest": _row_to_dict(latest) if latest else None,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    })


@router.post("/metrics")
async def post_metrics(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Ingest one metrics document for the **current user**.
    - No fabricated values; required metrics must be present and parseable.
    - On success: {ok: true, id: "..."}.
    - On failure: 4xx/5xx with the honest reason.
    """
    if not current_user or "id" not in current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Extract required metrics (support nested shapes like {"cpu":{"percent":"85%"}})
    cpu = _parse_number(_get_in(payload, "cpu_usage", "cpu.percent", "cpu"))
    mem = _parse_number(_get_in(payload, "memory_usage", "memory.percent", "memory"))
    disk = _parse_number(_get_in(payload, "disk_usage", "disk.percent", "disk"))

    missing = [k for k, v in (("cpu_usage", cpu), ("memory_usage", mem), ("disk_usage", disk)) if v is None]
    if missing:
        # 422: Unprocessable Entity — payload missing required truths
        detail = {"error": "Missing required metrics", "missing": missing}
        logger.error("Rejecting metrics payload: %s", detail)
        raise HTTPException(status_code=422, detail=detail)

    # Optional fields
    pc_raw = _parse_number(_get_in(payload, "process_count", "processes", "procs"))
    process_count: Optional[int] = int(pc_raw) if pc_raw is not None else None

    network = _get_in(payload, "network", "net", "network_data")
    network_data: Optional[Dict[str, Any]] = network if isinstance(network, dict) else None

    # Persist via repo (commit+refresh inside)
    try:
        repo = await get_metrics_repository()
        saved = await repo.create_metric(
            db=db,
            user_id=str(current_user["id"]),   # your model uses String FK
            cpu_usage=cpu,
            memory_usage=mem,
            disk_usage=disk,
            network_data=network_data,
            process_count=process_count,
            additional_metrics=payload,        # store full doc for transparency
        )
        return JSONResponse({"ok": True, "id": str(getattr(saved, "id", ""))})
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to persist metrics: %s", str(e), exc_info=True)
        # 500: repo/DB failed; truth is it did not persist.
        raise HTTPException(status_code=500, detail="Failed to persist metrics")


@router.get("/", summary="List metrics for the current user")
async def list_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if not current_user or "id" not in current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    repo = await get_metrics_repository()
    rows = await repo.get_user_metrics(db, user_id=current_user["id"], skip=skip, limit=limit, order_desc=True)
    return JSONResponse([_row_to_dict(r) for r in rows])


@router.get("/{metric_id}", summary="Get a specific metric for the current user")
async def read_metric(
    metric_id: str = Path(..., description="Metric UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if not current_user or "id" not in current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        _ = uuid.UUID(metric_id)  # validate format; actual comparison occurs in repo
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid metric_id")

    repo = await get_metrics_repository()
    m = await repo.get_metric_by_id(db, metric_id)
    if not m:
        raise HTTPException(status_code=404, detail="Metric not found")
    if str(getattr(m, "user_id", "")) != str(current_user["id"]):
        logger.warning("Unauthorized access attempt to metric %s by user %s", metric_id, current_user["id"])
        raise HTTPException(status_code=403, detail="Not authorized to access this metric")
    return JSONResponse(_row_to_dict(m))


@router.put("/{metric_id}", summary="Update a specific metric for the current user")
async def update_metric(
    metric_id: str = Path(..., description="Metric UUID"),
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if not current_user or "id" not in current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        _ = uuid.UUID(metric_id)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid metric_id")

    # Authorize ownership first
    repo = await get_metrics_repository()
    existing = await repo.get_metric_by_id(db, metric_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Metric not found")
    if str(getattr(existing, "user_id", "")) != str(current_user["id"]):
        logger.warning("Unauthorized update attempt to metric %s by user %s", metric_id, current_user["id"])
        raise HTTPException(status_code=403, detail="Not authorized to update this metric")

    # Build update fields (only what client supplies)
    fields: Dict[str, Any] = {}
    if "cpu_usage" in payload or "cpu" in payload:
        v = _parse_number(_get_in(payload, "cpu_usage", "cpu.percent", "cpu"))
        if v is None:
            raise HTTPException(status_code=422, detail="cpu_usage must be a number")
        fields["cpu_usage"] = v
    if "memory_usage" in payload or "memory" in payload:
        v = _parse_number(_get_in(payload, "memory_usage", "memory.percent", "memory"))
        if v is None:
            raise HTTPException(status_code=422, detail="memory_usage must be a number")
        fields["memory_usage"] = v
    if "disk_usage" in payload or "disk" in payload:
        v = _parse_number(_get_in(payload, "disk_usage", "disk.percent", "disk"))
        if v is None:
            raise HTTPException(status_code=422, detail="disk_usage must be a number")
        fields["disk_usage"] = v
    if "process_count" in payload or "processes" in payload or "procs" in payload:
        v = _parse_number(_get_in(payload, "process_count", "processes", "procs"))
        if v is None:
            fields["process_count"] = None
        else:
            fields["process_count"] = int(v)
    if "network" in payload or "net" in payload or "network_data" in payload:
        n = _get_in(payload, "network", "net", "network_data")
        fields["network"] = n if isinstance(n, dict) else None
    if "additional_metrics" in payload:
        fields["additional_metrics"] = payload.get("additional_metrics")

    if not fields:
        raise HTTPException(status_code=422, detail="No updatable fields provided")

    try:
        updated = await repo.update_metric_fields(db, metric_id, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="Metric not found")
        return JSONResponse(_row_to_dict(updated))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update metric %s: %s", metric_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update metric")


@router.delete("/{metric_id}", status_code=204, summary="Delete a specific metric for the current user")
async def delete_metric(
    metric_id: str = Path(..., description="Metric UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    if not current_user or "id" not in current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        _ = uuid.UUID(metric_id)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid metric_id")

    # Authorize ownership first
    repo = await get_metrics_repository()
    existing = await repo.get_metric_by_id(db, metric_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Metric not found")
    if str(getattr(existing, "user_id", "")) != str(current_user["id"]):
        logger.warning("Unauthorized deletion attempt of metric %s by user %s", metric_id, current_user["id"])
        raise HTTPException(status_code=403, detail="Not authorized to delete this metric")

    try:
        deleted = await repo.delete_metric(db, metric_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Metric not found")
        return JSONResponse(status_code=204, content=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete metric %s: %s", metric_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete metric")
