## core/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # Authentication views
    UserViewSet,
    CustomTokenObtainPairView,
    health_check,
    
    # System views
    SystemMetricsViewSet,
    OptimizationProfileViewSet,
    OptimizationResultViewSet,
    SystemAlertViewSet,
    AutoTuningViewSet,
    AutoTuningResultViewSet,
    UserPreferencesViewSet,
    SystemConfigurationViewSet
)

router = DefaultRouter()

# User management
router.register(r'users', UserViewSet, basename='user')
router.register(r'preferences', UserPreferencesViewSet, basename='preferences')

# System optimization
router.register(r'metrics', SystemMetricsViewSet, basename='metrics')
router.register(r'optimization-profile', OptimizationProfileViewSet, basename='optimization-profile')
router.register(r'optimization-result', OptimizationResultViewSet, basename='optimization-result')
router.register(r'system-alert', SystemAlertViewSet, basename='system-alert')
router.register(r'auto-tuning', AutoTuningViewSet, basename='auto-tuning')
router.register(r'auto-tuning-result', AutoTuningResultViewSet, basename='auto-tuning-result')
# Sir Hawkington's Distinguished Configuration Routes
router.register(r'configurations', SystemConfigurationViewSet, basename='configurations')  # The Quantum Shadow People insist on consistent URL patterns

urlpatterns = [
    # API Routes
    path('', include(router.urls)),
    
    # Authentication Routes
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    
    # Sir Hawkington's Distinguished Health Checks
    # The Quantum Shadow People insist on having both endpoints for maximum reliability
    path('auth/status/', health_check, name='auth_status'),  # The Stick's preferred authentication status endpoint
    path('health-check/', health_check, name='health_check'),  # Sir Hawkington's Monocle of Inspection
]