import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.future import select
from app.models.tuning_history import TuningHistory
from app.core.database import SessionLocal, AsyncSessionLocal

logger = logging.getLogger('WebAutoTuner')

async def save_tuning_history_to_db(tuning_data: Dict, user_id: str) -> None:
    """Save tuning history to database
    
    Args:
        tuning_data: Dictionary containing tuning data
        user_id: ID of the user applying the tuning
    """
    try:
        from app.core.database import AsyncSessionLocal
        
        # Convert user_id to int if it's a string
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            # If conversion fails, use a default user ID of 1
            logger.warning(f"Invalid user_id format: {user_id}, using default user_id=1")
            user_id_int = 1
        
        async with AsyncSessionLocal() as db:
            db_tuning = TuningHistory(
                user_id=user_id_int,
                parameter=tuning_data['parameter'],
                old_value=str(tuning_data.get('current_value', '')),
                new_value=str(tuning_data['new_value']),
                success=bool(tuning_data.get('success', False)),
                error=str(tuning_data.get('error', '')) if tuning_data.get('error') else None,
                metrics_before=tuning_data.get('metrics_before'),
                metrics_after=tuning_data.get('metrics_after')
            )
            db.add(db_tuning)
            await db.commit()
            await db.refresh(db_tuning)
            logger.info(f"Saved tuning history to database: {tuning_data['parameter']}")
    except Exception as e:
        logger.error(f"Error saving tuning history to database: {str(e)}")
        
async def get_tuning_history_from_db(user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """Get tuning history from database
    
    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of records to return
        
    Returns:
        List of tuning history records
    """
    try:
        from sqlalchemy.future import select
        from app.core.database import AsyncSessionLocal
        
        # Convert user_id to int if it's a string and not None
        user_id_int = None
        if user_id is not None:
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id format: {user_id}, not filtering by user_id")
        
        async with AsyncSessionLocal() as db:
            query = select(TuningHistory)
            
            if user_id_int is not None:
                query = query.where(TuningHistory.user_id == user_id_int)
                
            query = query.order_by(TuningHistory.timestamp.desc()).limit(limit)
            result = await db.execute(query)
            tuning_history = result.scalars().all()
            
            history_dicts = []
            for record in tuning_history:
                try:
                    history_dicts.append(record.to_dict())
                except Exception as e:
                    logger.error(f"Error converting record to dict: {str(e)}")
            
            return history_dicts
    except Exception as e:
        logger.error(f"Error getting tuning history from database: {str(e)}")
        return []
