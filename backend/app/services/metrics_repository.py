"""
Metrics Repository

Provides database operations for storing and retrieving system metrics.
Implements the repository pattern for metric persistence.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from datetime import datetime, timedelta
from functools import lru_cache
import uuid
import asyncio
import logging

from app.models.metrics import SystemMetrics
from app.schemas.metrics import MetricCreate, MetricUpdate

logger = logging.getLogger(__name__)

class MetricsRepository:
    """Repository for managing system metrics persistence in the database.
    Handles all database operations including creating, reading, updating, and deleting metrics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    async def create_metric(
        db: AsyncSession, 
        metric_data: MetricCreate
    ) -> SystemMetrics:
        """
        Sir Hawkington's Metric Creation Protocol
        
        Creates a new metric record in the database with proper error handling.
        """
        try:
            db_metric = SystemMetrics(
                id=str(uuid.uuid4()),
                **metric_data.model_dump()
            )
            
            db.add(db_metric)
            await db.commit()
            await db.refresh(db_metric)
            
            logger.info(f"Sir Hawkington successfully created metric: {db_metric.id}")
            return db_metric
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Sir Hawkington's protocol failed: {str(e)}")
            raise

    @staticmethod
    async def get_user_metrics(
        db: AsyncSession, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[SystemMetrics]:
        """
        The Meth Snail's Metric Retrieval Mechanism
        
        Retrieves paginated metrics for a specific user.
        """
        try:
            query = select(SystemMetrics).filter(
                SystemMetrics.user_id == str(user_id)
            ).order_by(SystemMetrics.created_at.desc()).offset(skip).limit(limit)
            
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            logger.debug(f"The Meth Snail retrieved {len(metrics)} metrics for user {user_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"The Meth Snail's retrieval failed: {str(e)}")
            raise

    @staticmethod
    async def get_metric_by_id(
        db: AsyncSession, 
        metric_id: uuid.UUID
    ) -> Optional[SystemMetrics]:
        """
        Quantum Precision Metric Lookup
        
        Retrieves a single metric by its ID with quantum precision.
        """
        try:
            query = select(SystemMetrics).filter(
                SystemMetrics.id == str(metric_id)
            )
            
            result = await db.execute(query)
            metric = result.scalar_one_or_none()
            
            if metric:
                logger.debug(f"Quantum lookup successful for metric: {metric_id}")
            else:
                logger.warning(f"Quantum lookup found no metric with ID: {metric_id}")
                
            return metric
            
        except Exception as e:
            logger.error(f"Quantum precision lookup failed: {str(e)}")
            raise

    @staticmethod
    async def update_metric(
        db: AsyncSession, 
        metric_id: uuid.UUID, 
        metric_data: MetricUpdate
    ) -> Optional[SystemMetrics]:
        """
        Sir Hawkington's Metric Update Protocol
        
        Updates an existing metric with new data.
        """
        try:
            # First check if metric exists
            existing_metric = await MetricsRepository.get_metric_by_id(db, metric_id)
            if not existing_metric:
                logger.warning(f"Sir Hawkington cannot update non-existent metric: {metric_id}")
                return None
            
            query = update(SystemMetrics).where(
                SystemMetrics.id == str(metric_id)
            ).values(
                **metric_data.model_dump(exclude_unset=True),
                updated_at=datetime.utcnow()
            )
            
            await db.execute(query)
            await db.commit()
            
            updated_metric = await MetricsService.get_metric_by_id(db, metric_id)
            logger.info(f"Sir Hawkington successfully updated metric: {metric_id}")
            
            return updated_metric
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Sir Hawkington's update protocol failed: {str(e)}")
            raise

    @staticmethod
    async def delete_metric(
        db: AsyncSession, 
        metric_id: uuid.UUID
    ) -> bool:
        """
        The Meth Snail's Metric Deletion Ceremony
        
        Performs the sacred ritual of metric deletion.
        """
        try:
            query = delete(SystemMetrics).where(
                SystemMetrics.id == str(metric_id)
            )
            
            result = await db.execute(query)
            await db.commit()
            
            success = result.rowcount > 0
            if success:
                logger.info(f"The Meth Snail completed deletion ceremony for metric: {metric_id}")
            else:
                logger.warning(f"The Meth Snail found no metric to delete: {metric_id}")
                
            return success
            
        except Exception as e:
            await db.rollback()
            logger.error(f"The Meth Snail's deletion ceremony failed: {str(e)}")
            raise
    
    @staticmethod
    async def get_latest_metrics_for_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 10
    ) -> List[SystemMetrics]:
        """
        Get the most recent metrics for a user, optimized for real-time display.
        """
        try:
            query = select(SystemMetrics).filter(
                SystemMetrics.user_id == str(user_id)
            ).order_by(SystemMetrics.created_at.desc()).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics for user {user_id}: {str(e)}")
            raise
        
    @staticmethod
    async def get_live_system_metrics(
        db: AsyncSession = None, 
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get real-time system metrics with caching for WebSocket performance.
        
        Args:
            db: Database session (optional, for future database storage)
            force_refresh: If True, bypasses cache and gets fresh metrics
            
        Returns:
            Dictionary containing current system metrics
        """
        now = datetime.now()
        
        # Check cache first unless force refresh
        if not force_refresh and MetricsService._metrics_cache:
            last_update = MetricsService._metrics_cache.get('timestamp')
            if last_update and (now - datetime.fromisoformat(last_update.replace('Z', '+00:00').replace('+00:00', ''))) < MetricsService._cache_duration:
                logger.debug("Returning cached metrics")
                return MetricsService._metrics_cache
        
        try:
            import psutil
            
            # Get metrics asynchronously where possible
            metrics_data = await MetricsService._collect_system_metrics()
            
            # Update cache
            MetricsService._metrics_cache = metrics_data
            
            logger.debug("Fresh system metrics collected and cached")
            return metrics_data
            
        except ImportError:
            logger.error("psutil not available - cannot collect system metrics")
            return MetricsService._get_fallback_metrics()
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            return MetricsService._get_fallback_metrics(error=str(e))
    
    @staticmethod
    async def _collect_system_metrics() -> Dict[str, Any]:
        """
        Internal method to collect system metrics using psutil.
        Made async to avoid blocking the event loop.
        """
        import psutil
        
        # Run CPU intensive operations in thread pool
        loop = asyncio.get_event_loop()
        
        # Get CPU usage (this blocks for 1 second, so run in thread)
        cpu_percent = await loop.run_in_executor(
            None, lambda: psutil.cpu_percent(interval=0.1)
        )
        
        # Get other metrics (these are fast)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        process_count = len(psutil.pids())
        
        # Get CPU temperature if available
        cpu_temp = None
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps and temps['coretemp']:
                    cpu_temp = temps['coretemp'][0].current
        except Exception:
            pass  # Temperature not available on this system
        
        # Get disk I/O counters
        disk_io = psutil.disk_io_counters()
        
        # Get network interfaces info
        interfaces = await MetricsService._get_network_interfaces()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': round(cpu_percent, 2),
                'temperature': cpu_temp,
                'cores': psutil.cpu_count(logical=True),
                'physical_cores': psutil.cpu_count(logical=False)
            },
            'memory': {
                'percent': round(memory.percent, 2),
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free
            },
            'disk': {
                'percent': round(disk.percent, 2),
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'io': {
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0,
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0
                } if disk_io else {}
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'interfaces': interfaces
            },
            'process_count': process_count,
            'system_uptime': psutil.boot_time(),
            'load_average': list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else []
        }
    
    @staticmethod
    async def _get_network_interfaces() -> Dict[str, Any]:
        """Get network interface information safely."""
        try:
            import psutil
            
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            interfaces = {}
            for interface, addrs in net_if_addrs.items():
                if interface not in net_if_stats or not net_if_stats[interface].isup:
                    continue
                    
                interfaces[interface] = {
                    'addresses': [addr.address for addr in addrs if addr.address and addr.address != '::1' and addr.address != '127.0.0.1'],
                    'is_up': net_if_stats[interface].isup,
                    'mtu': net_if_stats[interface].mtu,
                    'speed': net_if_stats[interface].speed
                }
            
            return interfaces
            
        except Exception as e:
            logger.warning(f"Could not get network interfaces: {str(e)}")
            return {}
    
    @staticmethod
    def _get_fallback_metrics(error: str = None) -> Dict[str, Any]:
        """Return minimal fallback metrics when collection fails."""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {'percent': 0, 'cores': 0, 'physical_cores': 0, 'temperature': None},
            'memory': {'percent': 0, 'total': 0, 'available': 0, 'used': 0, 'free': 0},
            'disk': {'percent': 0, 'total': 0, 'used': 0, 'free': 0, 'io': {}},
            'network': {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0, 'interfaces': {}},
            'process_count': 0,
            'system_uptime': 0,
            'load_average': [],
            'error': error or 'System metrics unavailable',
            'status': 'error'
        }
    
    @staticmethod
    async def store_current_metrics(
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        metric_type: str = "system_snapshot"
    ) -> SystemMetrics:
        """
        Collect current system metrics and store them in the database.
        Useful for historical tracking and WebSocket updates.
        """
        try:
            # Get live metrics
            # Get metrics from the metrics service
            from app.services.metrics.metrics_service import MetricsService
            metrics_service = MetricsService()
            metrics_data = await metrics_service.get_metrics(force_refresh=True)
            
            # Create metric record
            metric_create = MetricCreate(
                user_id=str(user_id) if user_id else None,
                metric_type=metric_type,
                name="system_metrics",
                value=metrics_data.get('cpu', {}).get('percent', 0),
                unit="percent",
                metadata=metrics_data,
                timestamp=datetime.utcnow()
            )
            
            # Store in database
            stored_metric = await MetricsRepository.create_metric(db, metric_create)
            
            logger.info(f"Stored system metrics snapshot: {stored_metric.id}")
            return stored_metric
            
        except Exception as e:
            logger.error(f"Failed to store current metrics: {str(e)}")
            raise
    
    @staticmethod
    def clear_metrics_cache():
        """Clear the metrics cache to force fresh data on next request."""
        # This method is no longer needed as we don't cache metrics in the DB service
        pass
        logger.debug("Metrics cache cleared")