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