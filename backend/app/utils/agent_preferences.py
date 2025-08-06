from typing import Dict, Any
from app.models.user import User
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def adjust_agent_preferences_for_system(user_preferences, system_profile):
    """
    Frontend has already done the intelligent system-aware adjustements. 
    Just trust it and pass through.
    """
    return user_preferences

def adjust_monitoring_preferences_for_system(user_preferences, system_profile):
    """Frontend has already done the intelligent system-aware adjustments."""  
    return user_preferences