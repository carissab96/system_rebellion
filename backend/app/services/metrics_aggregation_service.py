# app/services/metrics_aggregation_service.py
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

logger = logging.getLogger(__name__)

UTC = timezone.utc


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness"""
    return datetime.now(UTC)

class MetricsAggregationService:
    """The Meth Snail's data optimization engine"""
    
    def __init__(self):
        self.logger = logging.getLogger("MethSnail.Aggregation")
        
    async def aggregate_hourly_metrics(
        self, 
        db: AsyncSession, 
        user_id: str, 
        start_hour: datetime
    ):
        """
        The Meth Snail's hourly aggregation ritual.
        Compresses raw metrics into hourly summaries.
        """
        try:
            end_hour = start_hour + timedelta(hours=1)
            
            # Query raw metrics for this hour
            from backend.app.models.metrics import SystemMetrics
            
            query = select(SystemMetrics).filter(
                SystemMetrics.user_id == user_id,
                SystemMetrics.timestamp >= start_hour,
                SystemMetrics.timestamp < end_hour
            )
            
            result = await db.execute(query)
            raw_metrics = result.scalars().all()
            
            if not raw_metrics:
                return None
            
            # Calculate aggregates
            cpu_values = [m.cpu_usage for m in raw_metrics]
            memory_values = [m.memory_usage for m in raw_metrics]
            disk_values = [m.disk_usage for m in raw_metrics]
            
            # Extract AI events
            ai_events = []
            for metric in raw_metrics:
                if metric.additional_metrics and 'sir_hawkington' in metric.additional_metrics:
                    hawk_data = metric.additional_metrics['sir_hawkington']
                    if hawk_data.get('decision_type') != 'normal':
                        ai_events.append({
                            'timestamp': metric.timestamp.isoformat(),
                            'decision': hawk_data.get('decision_type'),
                            'message': hawk_data.get('message')
                        })
            
            # Create hourly aggregate
            hourly_metric = MetricsHourly(
                user_id=user_id,
                hour_start=start_hour,
                cpu_avg=sum(cpu_values) / len(cpu_values),
                cpu_max=max(cpu_values),
                cpu_min=min(cpu_values),
                memory_avg=sum(memory_values) / len(memory_values),
                memory_max=max(memory_values),
                memory_min=min(memory_values),
                disk_avg=sum(disk_values) / len(disk_values),
                network_bytes_total=self._calculate_network_total(raw_metrics),
                ai_events=ai_events,
                anomaly_count=len(ai_events),
                sample_count=len(raw_metrics)
            )
            
            db.add(hourly_metric)
            await db.commit()
            
            self.logger.info(
                f"🐌 Meth Snail aggregated {len(raw_metrics)} samples "
                f"into hourly summary for {user_id} at {start_hour}"
            )
            
            return hourly_metric
            
        except Exception as e:
            self.logger.error(f"🐌 Meth Snail aggregation failed: {str(e)}")
            await db.rollback()
            raise
    
    async def cleanup_old_raw_metrics(
        self, 
        db: AsyncSession, 
        retention_days: int = 7
    ):
        """
        The Meth Snail's cleanup protocol.
        Removes raw metrics older than retention period.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Delete old raw metrics
            query = delete(SystemMetrics).where(
                SystemMetrics.timestamp < cutoff_date
            )
            
            result = await db.execute(query)
            await db.commit()
            
            self.logger.info(
                f"🐌 Meth Snail cleaned up {result.rowcount} old metrics "
                f"(older than {retention_days} days)"
            )
            
            return result.rowcount
            
        except Exception as e:
            self.logger.error(f"🐌 Meth Snail cleanup failed: {str(e)}")
            await db.rollback()
            raise