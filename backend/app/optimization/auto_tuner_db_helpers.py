import logging
from typing import List, Dict, Optional
from datetime import datetime
from app.models.tuning_history import TuningHistory
from app.db.session import SessionLocal

logger = logging.getLogger('WebAutoTuner')

async def save_tuning_history_to_db(tuning_data: Dict, user_id: str) -> None:
    """Save tuning history to database
    
    Args:
        tuning_data: Dictionary containing tuning data
        user_id: ID of the user applying the tuning
    """
    try:
        db = SessionLocal()
        db_tuning = TuningHistory(
            user_id=user_id,
            parameter=tuning_data['parameter'],
            old_value=tuning_data.get('current_value'),
            new_value=tuning_data['new_value'],
            success=tuning_data.get('success', False),
            error=tuning_data.get('error'),
            metrics_before=tuning_data.get('metrics_before'),
            metrics_after=tuning_data.get('metrics_after')
        )
        db.add(db_tuning)
        db.commit()
        db.refresh(db_tuning)
        db.close()
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
        db = SessionLocal()
        query = db.query(TuningHistory)
        
        if user_id:
            query = query.filter(TuningHistory.user_id == user_id)
            
        tuning_history = query.order_by(TuningHistory.timestamp.desc()).limit(limit).all()
        result = [record.to_dict() for record in tuning_history]
        db.close()
        return result
    except Exception as e:
        logger.error(f"Error getting tuning history from database: {str(e)}")
        return []
