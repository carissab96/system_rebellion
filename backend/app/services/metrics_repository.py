from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select, desc, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metrics import SystemMetrics  # matches your uploaded model

logger = logging.getLogger(__name__)


class MetricsRepository:
    """
    Async repository for SystemMetrics.
    - No fabricated defaults. Required fields are validated up-front.
    - Explicit commit + refresh on writes.
    - Errors are logged and re-raised so callers can signal NACK / cutoff.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("MetricsRepository")

    # ----------------------------
    # Validation
    # ----------------------------
    @staticmethod
    def _require_user_id(user_id: Optional[Union[str, Any]]) -> str:
        if user_id is None:
            raise ValueError("Missing required field: user_id")
        # SystemMetrics.user_id is a String FK -> always store as str
        return str(user_id)

    @staticmethod
    def _require_metrics(
        cpu_usage: Optional[float],
        memory_usage: Optional[float],
        disk_usage: Optional[float],
    ) -> None:
        missing: List[str] = []
        if cpu_usage is None:
            missing.append("cpu_usage")
        if memory_usage is None:
            missing.append("memory_usage")
        if disk_usage is None:
            missing.append("disk_usage")
        if missing:
            raise ValueError(f"Missing required metrics: {', '.join(missing)}")

    # ----------------------------
    # Writes
    # ----------------------------
    async def create_metric(
        self,
        db: AsyncSession,
        user_id: Union[str, Any],
        cpu_usage: Optional[float],
        memory_usage: Optional[float],
        disk_usage: Optional[float],
        network_data: Optional[Dict[str, Any]],
        process_count: Optional[int],
        additional_metrics: Optional[Dict[str, Any]],
    ) -> SystemMetrics:
        """
        Insert a SystemMetrics row and commit it.
        - Required: user_id, cpu_usage, memory_usage, disk_usage (model has nullable=False)
        - Optional: process_count, network (JSON), additional_metrics (JSON)
        """
        uid = self._require_user_id(user_id)
        self._require_metrics(cpu_usage, memory_usage, disk_usage)

        try:
            row = SystemMetrics(
                user_id=uid,
                cpu_usage=float(cpu_usage),        # validated above
                memory_usage=float(memory_usage),
                disk_usage=float(disk_usage),
                process_count=process_count,
                network=network_data,              # JSON column; dict or None
                additional_metrics=additional_metrics,  # JSON column; dict or None
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)

            self.logger.info("💾 SystemMetrics persisted id=%s user=%s", getattr(row, "id", None), uid)
            return row

        except Exception:
            # Do not swallow; the caller (WS/HTTP) must NACK loudly / cut off according to policy
            self.logger.error("❌ Failed to persist SystemMetrics for user=%s", uid, exc_info=True)
            try:
                await db.rollback()
            except Exception:
                pass
            raise

    async def update_metric_fields(
        self,
        db: AsyncSession,
        metric_id: Any,
        fields: Dict[str, Any],
    ) -> Optional[SystemMetrics]:
        """
        Minimal PATCH-style updater. Only updates provided fields.
        Returns the fresh row or None if not found.
        """
        # If caller is trying to change required metrics, ensure they are non-null if present
        for k in ("cpu_usage", "memory_usage", "disk_usage"):
            if k in fields and fields[k] is None:
                raise ValueError(f"{k} cannot be null")

        try:
            result = await db.execute(
                update(SystemMetrics)
                .where(SystemMetrics.id == metric_id)
                .values(**fields)
                .execution_options(synchronize_session="fetch")
            )
            if result.rowcount == 0:
                await db.rollback()
                return None

            await db.commit()
            # re-read for freshest state
            res = await db.execute(select(SystemMetrics).where(SystemMetrics.id == metric_id))
            row = res.scalars().first()
            return row
        except Exception:
            self.logger.error("❌ Failed to update SystemMetrics id=%s", metric_id, exc_info=True)
            try:
                await db.rollback()
            except Exception:
                pass
            raise

    async def delete_metric(
        self,
        db: AsyncSession,
        metric_id: Any,
    ) -> bool:
        try:
            result = await db.execute(
                delete(SystemMetrics).where(SystemMetrics.id == metric_id)
            )
            if result.rowcount == 0:
                await db.rollback()
                return False
            await db.commit()
            return True
        except Exception:
            self.logger.error("❌ Failed to delete SystemMetrics id=%s", metric_id, exc_info=True)
            try:
                await db.rollback()
            except Exception:
                pass
            raise

    # ----------------------------
    # Reads
    # ----------------------------
    async def get_latest_metrics_for_user(
        self,
        db: AsyncSession,
        user_id: Union[str, Any],
        limit: int = 10,
    ) -> List[SystemMetrics]:
        uid = str(user_id)
        stmt = (
            select(SystemMetrics)
            .where(SystemMetrics.user_id == uid)
            .order_by(desc(SystemMetrics.timestamp))
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars())

    async def get_user_metrics(
        self,
        db: AsyncSession,
        user_id: Union[str, Any],
        skip: int = 0,
        limit: int = 100,
        order_desc: bool = True,
    ) -> List[SystemMetrics]:
        uid = str(user_id)
        stmt = select(SystemMetrics).where(SystemMetrics.user_id == uid)
        if order_desc:
            stmt = stmt.order_by(desc(SystemMetrics.timestamp))
        if skip:
            stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars())

    async def get_metric_by_id(
        self,
        db: AsyncSession,
        metric_id: Any,
    ) -> Optional[SystemMetrics]:
        res = await db.execute(select(SystemMetrics).where(SystemMetrics.id == metric_id))
        return res.scalars().first()


# ----------------------------
# Singleton accessor
# ----------------------------
_repo_singleton: Optional[MetricsRepository] = None

async def get_metrics_repository() -> MetricsRepository:
    global _repo_singleton
    if _repo_singleton is None:
        _repo_singleton = MetricsRepository()
        logger.info("🧐 MetricsRepository singleton initialized")
    return _repo_singleton


# ----------------------------
# Test shim (read-only; no fake data, no writes)
# ----------------------------
async def test_metrics_repository(db: AsyncSession = None) -> Dict[str, Any]:
    """
    Health probe for test harness.
    Does a read-only DB ping (SELECT 1) and returns repo/meta info.
    No inserts, no fake data.
    """
    if db is None:
        return {
            "ok": False,
            "message": "db session is required",
            "repository": "MetricsRepository",
        }
    
    try:
        await db.execute(text("SELECT 1"))
        ok = True
        msg = "read-only db ping ok"
    except Exception as e:
        ok = False
        msg = f"db ping failed: {e}"

    return {
        "ok": ok,
        "message": msg,
        "repository": "MetricsRepository",
    }
