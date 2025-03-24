# models/__init__.py
from .user import User
from .user import UserProfile
from .system import SystemConfiguration
from .system import OptimizationProfile
from .alerts import SystemAlert
from .metrics import SystemMetrics

# Ensure all models are imported and registered
__all__ = [
    'User', 
    'UserProfile', 
    'SystemConfiguration', 
    'OptimizationProfile', 
    'SystemAlert', 
    'SystemMetrics'
]