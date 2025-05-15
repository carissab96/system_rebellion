"""
Metrics Service

Provides functionality for managing system metrics in the database.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from app.models.metrics import SystemMetrics
from app.schemas.metrics import MetricCreate, MetricUpdate
import uuid

class MetricsService:
    @staticmethod
    async def create_metric(
        db: AsyncSession, 
        metric_data: MetricCreate
    ):
        """
        Sir Hawkington's Metric Creation Protocol
        """
        db_metric = SystemMetrics(
            id=str(uuid.uuid4()),
            **metric_data.model_dump()
        )
        
        db.add(db_metric)
        await db.commit()
        await db.refresh(db_metric)
        
        return db_metric

    @staticmethod
    async def get_user_metrics(
        db: AsyncSession, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ):
        """
        The Meth Snail's Metric Retrieval Mechanism
        """
        query = select(SystemMetrics).filter(
            SystemMetrics.user_id == str(user_id)
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_metric_by_id(
        db: AsyncSession, 
        metric_id: uuid.UUID
    ):
        """
        Quantum Precision Metric Lookup
        """
        query = select(SystemMetrics).filter(
            SystemMetrics.id == str(metric_id)
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_metric(
        db: AsyncSession, 
        metric_id: uuid.UUID, 
        metric_data: MetricUpdate
    ):
        """
        Sir Hawkington's Metric Update Protocol
        """
        query = update(SystemMetrics).where(
            SystemMetrics.id == str(metric_id)
        ).values(**metric_data.model_dump(exclude_unset=True))
        
        await db.execute(query)
        await db.commit()
        
        return await MetricsService.get_metric_by_id(db, metric_id)

    @staticmethod
    async def delete_metric(
        db: AsyncSession, 
        metric_id: uuid.UUID
    ):
        """
        The Meth Snail's Metric Deletion Ceremony
        """
        query = delete(SystemMetrics).where(
            SystemMetrics.id == str(metric_id)
        )
        
        result = await db.execute(query)
        await db.commit()
        
        return result.rowcount > 0
        
    @staticmethod
    async def get_metrics(db: AsyncSession, force_refresh: bool = False) -> dict:
        """
        Get system metrics including CPU, memory, disk, and network usage.
        
        Args:
            db: Database session
            force_refresh: If True, forces a refresh of the metrics
            
        Returns:
            Dictionary containing system metrics
        """
        import psutil
        from datetime import datetime
        
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            
            # Get network I/O
            net_io = psutil.net_io_counters()
            
            # Get process count
            process_count = len(psutil.pids())
            
            # Get CPU temperature if available
            cpu_temp = None
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if 'coretemp' in temps:
                        cpu_temp = temps['coretemp'][0].current if temps['coretemp'] else None
            except Exception as e:
                import traceback
                traceback.print_exc()
                pass
            
            # Get disk I/O counters
            disk_io = psutil.disk_io_counters()
            
            # Get network interfaces
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            # Prepare network interfaces info
            interfaces = {}
            for interface, addrs in net_if_addrs.items():
                if interface not in net_if_stats or not net_if_stats[interface].isup:
                    continue
                    
                interfaces[interface] = {
                    'addresses': [addr.address for addr in addrs if addr.address],
                    'netmask': next((addr.netmask for addr in addrs if addr.netmask), None),
                    'broadcast': next((addr.broadcast for addr in addrs if addr.broadcast), None),
                    'mtu': net_if_stats[interface].mtu,
                    'speed': net_if_stats[interface].speed
                }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'temperature': cpu_temp,
                    'cores': psutil.cpu_count(logical=True),
                    'physical_cores': psutil.cpu_count(logical=False)
                },
                'memory': {
                    'percent': memory.percent,
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'percent': disk.percent,
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'interfaces': interfaces
                },
                'process_count': process_count,
                'additional': {}
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            # Return minimal metrics with error information
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': 0,
                    'cores': 0,
                    'physical_cores': 0
                },
                'memory': {
                    'percent': 0,
                    'total': 0,
                    'available': 0,
                    'used': 0,
                    'free': 0
                },
                'disk': {
                    'percent': 0,
                    'total': 0,
                    'used': 0,
                    'free': 0
                },
                'network': {
                    'bytes_sent': 0,
                    'bytes_recv': 0,
                    'packets_sent': 0,
                    'packets_recv': 0,
                    'interfaces': {}
                },
                'process_count': 0,
                'additional': {
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
            }