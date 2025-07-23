"""
Metrics Repository - PURIFIED ARISTOCRATIC VERSION

Handles ONLY database persistence operations for system metrics.
Follows the Single Responsibility Principle with aristocratic precision.

🧐 "A repository's duty is data persistence - nothing more, nothing less"

CORE PRINCIPLES:
- Database operations ONLY
- NO metrics collection
- NO fake data generation  
- NO business logic
- Clean separation of concerns
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, func, and_, or_
from datetime import datetime, timedelta
import uuid
import logging
import json

from app.models.metrics import SystemMetrics
from app.schemas.metrics import MetricCreate, MetricUpdate

logger = logging.getLogger("MetricsRepository")

class MetricsRepository:
    """
    Pure database repository for system metrics persistence.
    
    🧐 ARISTOCRATIC ARCHITECTURE:
    - Handles ONLY database CRUD operations
    - No metrics collection (that's SimplifiedMetricsService's job)
    - No triage logic (that's Sir Hawkington's domain)
    - No fake data generation (EVER!)
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MetricsRepository")
        self.logger.info("🧐 Metrics Repository initialized with aristocratic precision")

    # === CORE CRUD OPERATIONS ===
    
    async def create_metric(
        self,
        db: AsyncSession, 
        user_id: str,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_data: Dict[str, Any],
        process_count: int,
        additional_metrics: Dict[str, Any]
    ) -> SystemMetrics:
        """
        🧐 Sir Hawkington's Metric Persistence Protocol
        
        Store a complete system metrics snapshot in the database.
        
        Args:
            db: Database session
            user_id: User identifier
            cpu_usage: CPU usage percentage
            memory_usage: Memory usage percentage  
            disk_usage: Disk usage percentage
            network_data: Network metrics dictionary
            process_count: Number of running processes
            additional_metrics: Any additional metrics data
            
        Returns:
            Created SystemMetrics database record
        """
        try:
            # Create the database record
            db_metric = SystemMetrics(
                user_id=user_id,
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network=json.dumps(network_data) if isinstance(network_data, dict) else str(network_data),
                process_count=process_count,
                additional_metrics=json.dumps(additional_metrics) if isinstance(additional_metrics, dict) else str(additional_metrics)
            )
            
            db.add(db_metric)
            await db.commit()
            await db.refresh(db_metric)
            
            self.logger.info(f"🧐✅ Sir Hawkington successfully persisted metric: {db_metric.id}")
            return db_metric
            
        except Exception as e:
            await db.rollback()
            self.logger.error(f"🧐💥 Sir Hawkington's persistence protocol failed: {str(e)}")
            raise Exception(f"Database persistence failed: {str(e)}")

    async def get_user_metrics(
        self,
        db: AsyncSession, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100,
        order_desc: bool = True
    ) -> List[SystemMetrics]:
        """
        🐌 The Meth Snail's Metric Retrieval Mechanism
        
        Retrieve paginated metrics for a specific user from database.
        
        Args:
            db: Database session
            user_id: User identifier
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            order_desc: If True, order by timestamp descending (newest first)
            
        Returns:
            List of SystemMetrics records from database
        """
        try:
            query = select(SystemMetrics).filter(
                SystemMetrics.user_id == str(user_id)
            )
            
            # Apply ordering
            if order_desc:
                query = query.order_by(SystemMetrics.timestamp.desc())
            else:
                query = query.order_by(SystemMetrics.timestamp.asc())
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            self.logger.debug(f"🐌📊 Retrieved {len(metrics)} metrics for user {user_id}")
            return list(metrics)
            
        except Exception as e:
            self.logger.error(f"🐌💥 Metric retrieval failed: {str(e)}")
            raise Exception(f"Database query failed: {str(e)}")

    async def get_metric_by_id(
        self,
        db: AsyncSession, 
        metric_id: int
    ) -> Optional[SystemMetrics]:
        """
        👻 Quantum Shadow People's Precision Lookup
        
        Retrieve a single metric by its database ID.
        
        Args:
            db: Database session
            metric_id: Database ID of the metric
            
        Returns:
            SystemMetrics record or None if not found
        """
        try:
            query = select(SystemMetrics).filter(
                SystemMetrics.id == metric_id
            )
            
            result = await db.execute(query)
            metric = result.scalar_one_or_none()
            
            if metric:
                self.logger.debug(f"👻✅ Quantum lookup successful for metric: {metric_id}")
            else:
                self.logger.debug(f"👻📭 No metric found with ID: {metric_id}")
                
            return metric
            
        except Exception as e:
            self.logger.error(f"👻💥 Quantum lookup failed: {str(e)}")
            raise Exception(f"Database lookup failed: {str(e)}")

    async def delete_metric(
        self,
        db: AsyncSession, 
        metric_id: int
    ) -> bool:
        """
        🐹 The Hamsters' Metric Deletion Protocol
        
        Delete a metric record from the database.
        
        Args:
            db: Database session
            metric_id: Database ID of metric to delete
            
        Returns:
            True if metric was deleted, False if not found
        """
        try:
            query = delete(SystemMetrics).where(
                SystemMetrics.id == metric_id
            )
            
            result = await db.execute(query)
            await db.commit()
            
            deleted = result.rowcount > 0
            
            if deleted:
                self.logger.info(f"🐹✅ The Hamsters successfully deleted metric: {metric_id}")
            else:
                self.logger.warning(f"🐹📭 The Hamsters found no metric to delete: {metric_id}")
                
            return deleted
            
        except Exception as e:
            await db.rollback()
            self.logger.error(f"🐹💥 The Hamsters' deletion protocol failed: {str(e)}")
            raise Exception(f"Database deletion failed: {str(e)}")
    
    # === ADVANCED QUERY OPERATIONS ===
    
    async def get_latest_metrics_for_user(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 10
    ) -> List[SystemMetrics]:
        """
        📏 The Stick's Latest Metrics Retrieval
        
        Get the most recent metrics for a user (optimized query).
        
        Args:
            db: Database session
            user_id: User identifier
            limit: Maximum number of recent metrics
            
        Returns:
            List of most recent SystemMetrics records
        """
        try:
            query = select(SystemMetrics).filter(
                SystemMetrics.user_id == str(user_id)
            ).order_by(
                SystemMetrics.timestamp.desc()
            ).limit(limit)
            
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            self.logger.debug(f"📏📊 Retrieved {len(metrics)} latest metrics for user {user_id}")
            return list(metrics)
            
        except Exception as e:
            self.logger.error(f"📏💥 Latest metrics retrieval failed: {str(e)}")
            raise Exception(f"Database query failed: {str(e)}")

    async def get_metrics_by_date_range(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000
    ) -> List[SystemMetrics]:
        """
        🧐 Sir Hawkington's Historical Analysis Query
        
        Retrieve metrics within a specific date range for historical analysis.
        
        Args:
            db: Database session
            user_id: User identifier
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            limit: Maximum number of records to return
            
        Returns:
            List of SystemMetrics within the date range
        """
        try:
            query = select(SystemMetrics).filter(
                and_(
                    SystemMetrics.user_id == str(user_id),
                    SystemMetrics.timestamp >= start_date,
                    SystemMetrics.timestamp <= end_date
                )
            ).order_by(
                SystemMetrics.timestamp.desc()
            ).limit(limit)
            
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            self.logger.debug(
                f"🧐📊 Retrieved {len(metrics)} metrics for user {user_id} "
                f"between {start_date.isoformat()} and {end_date.isoformat()}"
            )
            return list(metrics)
            
        except Exception as e:
            self.logger.error(f"🧐💥 Date range query failed: {str(e)}")
            raise Exception(f"Database query failed: {str(e)}")

    async def get_metrics_with_high_cpu_usage(
        self,
        db: AsyncSession,
        user_id: str,
        cpu_threshold: float = 80.0,
        limit: int = 100
    ) -> List[SystemMetrics]:
        """
        🔥 Emergency High CPU Usage Query
        
        Find metrics where CPU usage exceeded a threshold.
        
        Args:
            db: Database session
            user_id: User identifier
            cpu_threshold: CPU usage percentage threshold
            limit: Maximum records to return
            
        Returns:
            List of SystemMetrics with high CPU usage
        """
        try:
            query = select(SystemMetrics).filter(
                and_(
                    SystemMetrics.user_id == str(user_id),
                    SystemMetrics.cpu_usage >= cpu_threshold
                )
            ).order_by(
                SystemMetrics.timestamp.desc()
            ).limit(limit)
            
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            self.logger.debug(
                f"🔥 Found {len(metrics)} metrics with CPU >= {cpu_threshold}% for user {user_id}"
            )
            return list(metrics)
            
        except Exception as e:
            self.logger.error(f"🔥💥 High CPU query failed: {str(e)}")
            raise Exception(f"Database query failed: {str(e)}")

    # === STATISTICS AND AGGREGATION ===
    
    async def get_metrics_count_for_user(
        self,
        db: AsyncSession,
        user_id: str
    ) -> int:
        """
        📊 Total Metrics Count Query
        
        Get the total number of metrics stored for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            Total count of metrics for the user
        """
        try:
            query = select(func.count(SystemMetrics.id)).filter(
                SystemMetrics.user_id == str(user_id)
            )
            
            result = await db.execute(query)
            count = result.scalar() or 0
            
            self.logger.debug(f"📊 User {user_id} has {count} total metrics in database")
            return count
            
        except Exception as e:
            self.logger.error(f"📊💥 Metrics count query failed: {str(e)}")
            raise Exception(f"Database query failed: {str(e)}")

    async def get_average_cpu_usage(
        self,
        db: AsyncSession,
        user_id: str,
        days: int = 7
    ) -> float:
        """
        📈 Average CPU Usage Calculation
        
        Calculate average CPU usage over the last N days.
        
        Args:
            db: Database session
            user_id: User identifier
            days: Number of days to average over
            
        Returns:
            Average CPU usage percentage
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(func.avg(SystemMetrics.cpu_usage)).filter(
                and_(
                    SystemMetrics.user_id == str(user_id),
                    SystemMetrics.timestamp >= cutoff_date
                )
            )
            
            result = await db.execute(query)
            average = result.scalar()
            
            if average is not None:
                average = round(float(average), 2)
                self.logger.debug(f"📈 Average CPU usage for user {user_id} over {days} days: {average}%")
            else:
                average = 0.0
                self.logger.debug(f"📈 No CPU data available for user {user_id} over {days} days")
            
            return average
            
        except Exception as e:
            self.logger.error(f"📈💥 Average CPU calculation failed: {str(e)}")
            raise Exception(f"Database calculation failed: {str(e)}")

    # === MAINTENANCE OPERATIONS ===
    
    async def cleanup_old_metrics(
        self,
        db: AsyncSession,
        days_to_keep: int = 30
    ) -> int:
        """
        🧹 Database Maintenance - Old Metrics Cleanup
        
        Remove metrics older than specified number of days.
        
        Args:
            db: Database session
            days_to_keep: Number of days of metrics to retain
            
        Returns:
            Number of metrics deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            query = delete(SystemMetrics).where(
                SystemMetrics.timestamp < cutoff_date
            )
            
            result = await db.execute(query)
            await db.commit()
            
            deleted_count = result.rowcount
            self.logger.info(f"🧹✅ Cleaned up {deleted_count} metrics older than {days_to_keep} days")
            
            return deleted_count
            
        except Exception as e:
            await db.rollback()
            self.logger.error(f"🧹💥 Cleanup operation failed: {str(e)}")
            raise Exception(f"Database cleanup failed: {str(e)}")

    async def get_database_size_info(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        📊 Database Size Information
        
        Get information about the metrics table size and storage.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with database size information
        """
        try:
            # Get total record count
            total_count_query = select(func.count(SystemMetrics.id))
            total_result = await db.execute(total_count_query)
            total_metrics = total_result.scalar() or 0
            
            # Get oldest and newest records
            oldest_query = select(func.min(SystemMetrics.timestamp))
            oldest_result = await db.execute(oldest_query)
            oldest_timestamp = oldest_result.scalar()
            
            newest_query = select(func.max(SystemMetrics.timestamp))
            newest_result = await db.execute(newest_query)
            newest_timestamp = newest_result.scalar()
            
            # Calculate date range
            date_range_days = 0
            if oldest_timestamp and newest_timestamp:
                date_range_days = (newest_timestamp - oldest_timestamp).days
            
            return {
                'total_metrics': total_metrics,
                'oldest_metric': oldest_timestamp.isoformat() if oldest_timestamp else None,
                'newest_metric': newest_timestamp.isoformat() if newest_timestamp else None,
                'date_range_days': date_range_days,
                'estimated_daily_average': round(total_metrics / max(date_range_days, 1), 2) if date_range_days > 0 else 0,
                'last_analyzed': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"📊💥 Database size analysis failed: {str(e)}")
            raise Exception(f"Database analysis failed: {str(e)}")

    # === HEALTH CHECK ===
    
    async def health_check(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        🏥 Repository Health Check
        
        Perform comprehensive health check of the repository and database.
        
        Args:
            db: Database session
            
        Returns:
            Health check status dictionary
        """
        try:
            start_time = datetime.utcnow()
            
            # Test basic connectivity with a simple query
            test_query = select(SystemMetrics).limit(1)
            await db.execute(test_query)
            
            query_response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Get database statistics
            size_info = await self.get_database_size_info(db)
            
            return {
                'status': 'OPERATIONAL',
                'repository_type': 'metrics_persistence',
                'database_connected': True,
                'query_response_time_seconds': round(query_response_time, 4),
                'total_metrics_stored': size_info['total_metrics'],
                'date_range_days': size_info['date_range_days'],
                'available_operations': [
                    'create_metric', 'get_user_metrics', 'get_metric_by_id',
                    'delete_metric', 'get_latest_metrics_for_user', 
                    'get_metrics_by_date_range', 'get_metrics_with_high_cpu_usage',
                    'get_metrics_count_for_user', 'get_average_cpu_usage',
                    'cleanup_old_metrics', 'get_database_size_info'
                ],
                'architectural_principles': [
                    'single_responsibility_principle',
                    'no_metrics_collection',
                    'no_fake_data_generation',
                    'database_operations_only'
                ],
                'aristocratic_authority': 'DATABASE_PERSISTENCE_MAINTAINED',
                'last_health_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'repository_type': 'metrics_persistence',
                'database_connected': False,
                'error': str(e),
                'last_health_check': datetime.utcnow().isoformat()
            }

# === SINGLETON PATTERN ===

_metrics_repository: Optional[MetricsRepository] = None

async def get_metrics_repository() -> MetricsRepository:
    """
    Get the singleton metrics repository instance.
    
    Returns:
        MetricsRepository instance
    """
    global _metrics_repository
    
    if _metrics_repository is None:
        _metrics_repository = MetricsRepository()
    
    return _metrics_repository

# === CONVENIENCE FUNCTIONS ===

async def store_metrics_snapshot(
    db: AsyncSession,
    user_id: str,
    enhanced_metrics: Dict[str, Any]
) -> SystemMetrics:
    """
    Convenience function to store a metrics snapshot from triage engine.
    
    Args:
        db: Database session
        user_id: User identifier
        enhanced_metrics: Enhanced metrics from Sir Hawkington's triage engine
        
    Returns:
        Created SystemMetrics record
    """
    repository = await get_metrics_repository()
    
    return await repository.create_metric(
        db=db,
        user_id=user_id,
        cpu_usage=enhanced_metrics.get('cpu_usage', 0.0),
         memory_usage=enhanced_metrics.get('memory_usage', 0.0),
        disk_usage=enhanced_metrics.get('disk_usage', 0.0),
        network_data=enhanced_metrics.get('network', {}),
        process_count=enhanced_metrics.get('process_count', 0),
        additional_metrics=enhanced_metrics  # Store the complete enhanced metrics
    )

async def get_recent_user_metrics(
    db: AsyncSession,
    user_id: str,
    limit: int = 10
) -> List[SystemMetrics]:
    """
    Convenience function to get recent metrics for a user.
    
    Args:
        db: Database session
        user_id: User identifier
        limit: Number of recent metrics to retrieve
        
    Returns:
        List of recent SystemMetrics records
    """
    repository = await get_metrics_repository()
    return await repository.get_latest_metrics_for_user(db, user_id, limit)

async def repository_health_check(db: AsyncSession) -> Dict[str, Any]:
    """
    Convenience function for repository health check.
    
    Args:
        db: Database session
        
    Returns:
        Health check results
    """
    repository = await get_metrics_repository()
    return await repository.health_check(db)

# === TESTING FUNCTIONS ===

async def test_metrics_repository():
    """
    Test function for the metrics repository (requires database connection).
    This would typically be run with a test database session.
    """
    print("\n" + "="*80)
    print(" 🧐📊 METRICS REPOSITORY TEST - ARISTOCRATIC DATABASE OPERATIONS")
    print("="*80)
    
    print("\n🧐 Metrics Repository initialized and ready")
    print("📊 Available operations:")
    operations = [
        "create_metric", "get_user_metrics", "get_metric_by_id",
        "delete_metric", "get_latest_metrics_for_user", 
        "get_metrics_by_date_range", "get_metrics_with_high_cpu_usage",
        "get_metrics_count_for_user", "get_average_cpu_usage",
        "cleanup_old_metrics", "get_database_size_info", "health_check"
    ]
    
    for i, operation in enumerate(operations, 1):
        print(f"   {i:2d}. {operation}")
    
    print("\n🏗️ Architectural Principles:")
    principles = [
        "✅ Single Responsibility: Database operations ONLY",
        "✅ No metrics collection (that's SimplifiedMetricsService)",
        "✅ No triage logic (that's Sir Hawkington's domain)", 
        "✅ No fake data generation (EVER!)",
        "✅ Clean separation of concerns",
        "✅ Proper error handling with honest failures"
    ]
    
    for principle in principles:
        print(f"   {principle}")
    
    print("\n🧐 Repository ready for aristocratic database operations!")
    print("   To test with actual database, provide AsyncSession to methods")
    
    print("\n" + "="*80)
    print(" 🧐✨ METRICS REPOSITORY READY - PURE DATABASE PERSISTENCE")
    print("="*80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_metrics_repository())