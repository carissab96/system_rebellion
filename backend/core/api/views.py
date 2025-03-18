from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.        response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import login, logout, get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
import logging
from functools import wraps
from asgiref.sync import async_to_sync


# Sir Hawkington's Distinguished Logger
logger = logging.getLogger(__name__)
from core.models import (
    SystemMetrics, 
    OptimizationProfile, 
    OptimizationResult, 
    SystemAlert,
    UserPreferences,
    AutoTuner,
    AutoTuningResult,
    SystemConfiguration  
)
from .serializers import (
    SystemMetricsSerializer,
    OptimizationProfileSerializer,
    OptimizationResultSerializer,
    SystemAlertSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    UserPreferencesSerializer,
    AutoTuningSerializer,
    AutoTuningResultSerializer,
    SystemConfigurationSerializer
)
from authentication.serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer
)
from core.optimization.auto_tuner import AutoTuner
from core.optimization.web_auto_tuner import WebAutoTuner

User = get_user_model()

def async_view(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return async_to_sync(func)(*args, **kwargs)
    return wrapped

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def health_check(request):
    """
    A simple health check endpoint that also sets a CSRF cookie.
    This is useful for frontend applications to check if the backend is available
    and to get a CSRF token without having to authenticate.
    """
    csrf_token = get_token(request)
    return Response({
        'status': 'ok',
        'message': 'Backend is up and running!',
        'csrf_token': csrf_token,
    }, status=status.HTTP_200_OK)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Login successful! Sir Hawkington welcomes you back! 🦅',
                'data': response.data,
                'meth_snail_approval': 'Authentication vibes are cosmic!',
                'hamster_status': 'Token wrapped in quantum duct tape'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Invalid credentials! Sir Hawkington cannot verify your papers! 📜',
                'error': str(e),
                'meth_snail_panic': 'Your credentials are in another dimension!',
                'hamster_suggestion': 'Try authentication-grade duct tape'
            }, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    @method_decorator(csrf_protect)
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    'status': 'success',
                    'user_id': user.id,
                    'system_id': user.system_id,
                    'message': 'User created successfully! Sir Hawkington tips his hat to you! 🎩',
                    'meth_snail_welcome': 'Welcome to the cosmic optimization realm!',
                    'hamster_gift': 'Complimentary duct tape included'
                })
            return Response({
                'error': serializer.errors,
                'meth_snail_panic': 'Registration vibes are off, man',
                'hamster_suggestion': 'More duct tape may be required'
            }, status=status.HTTP_400_BAD_REQUEST)
        except (ValidationError, DjangoValidationError) as e:
            return Response({
                'status': 'error',
                'message': 'Invalid data provided! Sir Hawkington suggests a review! 📝',
                'errors': str(e),
                'meth_snail_advice': 'Your data needs cosmic alignment',
                'hamster_solution': 'Try validation-grade duct tape'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e),
                'meth_snail_status': 'The registration... it\'s complicated man',
                'hamster_emergency': 'Deploying registration duct tape',
                'stick_panic': 'NEW USER REGULATIONS BREACHED!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    @method_decorator(csrf_protect)
    def login(self, request):
        try:
            login(request)
            return Response({
                'status': 'success',
                'message': 'Welcome back! Sir Hawkington adjusts his monocle in approval! 🧐',
                'meth_snail_greeting': 'The cosmic vibes are aligned!',
                'hamster_status': 'Login duct tape holding strong'
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'meth_snail_panic': 'Your login chakras are misaligned',
                'hamster_suggestion': 'Try login-grade duct tape'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    @method_decorator(csrf_protect)
    def logout(self, request):
        logout(request)
        return Response({
            'status': 'success',
            'message': 'Farewell! Sir Hawkington waves his wing goodbye 🦅',
            'meth_snail_farewell': 'Safe travels through the quantum void',
            'hamster_action': 'Storing duct tape for your return'
        })
class SystemMetricsViewSet(viewsets.ModelViewSet):
    serializer_class = SystemMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Base queryset for metrics"""
        return SystemMetrics.objects.all()

    def list(self, request):
        """Get latest metrics"""
        logger.debug(f"🎯 Metrics list endpoint hit by user: {request.user}")
        logger.debug(f"🔑 Auth header: {request.headers.get('Authorization')}")
        
        try:
            # Get latest metrics
            latest_metrics = self.get_queryset().order_by('-timestamp').first()
            
            if not latest_metrics:
                logger.warning("⚠️ No metrics found in database")
                return Response({
                    'error': 'No metrics available',
                    'meth_snail_panic': 'The metrics... they\'re in another dimension!',
                    'hamster_status': 'Deploying metric-finding duct tape'
                }, status=status.HTTP_404_NOT_FOUND)

            data = {
                'cpu': latest_metrics.cpu,
                'memory': latest_metrics.memory,
                'disk': latest_metrics.disk,
                'timestamp': latest_metrics.timestamp,
                'connection_id': latest_metrics.connection_id
            }
            logger.debug("✨ Successfully serialized latest metrics")
            
                 
            return Response({
                'status': 'success',
                'data': data,
                'meth_snail_approval': 'Metrics looking cosmic!',
                'hamster_status': 'Metrics secured with quantum duct tape'
            })

        except Exception as e:
            logger.error(f"💩 Error fetching metrics: {str(e)}")
            return Response({
                'error': str(e),
                'meth_snail_panic': 'The metrics are having an existential crisis!',
                'hamster_emergency': 'Emergency metric duct tape deployed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def historical(self, request):
        """Get historical metrics"""
        logger.debug(f"📊 Historical metrics requested by user: {request.user}")
        
        try:
            # Get and validate limit parameter
            try:
                limit = int(request.query_params.get('limit', 20))
                if limit < 1:
                    raise ValueError("Limit must be positive")
            except ValueError as ve:
                logger.warning(f"⚠️ Invalid limit parameter: {str(ve)}")
                return Response({
                    'error': 'Invalid limit parameter',
                    'meth_snail_concern': 'Your numbers are... non-euclidean, man',
                    'hamster_status': 'Numerical duct tape needed'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get historical metrics
            metrics = self.get_queryset().order_by('-timestamp')[:limit]
            
            if not metrics.exists():  # Use exists() for efficiency
                logger.warning("⚠️ No historical metrics found")
                return Response({
                    'error': 'No historical metrics available',
                    'meth_snail_concern': 'The past is... cloudy, man',
                    'hamster_status': 'Time-travel duct tape required'
                }, status=status.HTTP_404_NOT_FOUND)

            historical_data = [{
                'cpu': metric.cpu,
                'memory': metric.memory,
                'disk': metric.disk,
                'timestamp': metric.timestamp,
                'connection_id': metric.connection_id
            } for metric in metrics]

            logger.debug(f"✨ Successfully serialized {len(metrics)} historical metrics")
            
            return Response({
                'status': 'success',
                'data': historical_data,
                'meth_snail_approval': 'Historical vibes are strong!',
                'hamster_status': 'Timeline secured with temporal duct tape'
            })

        except Exception as e:
            logger.error(f"💩 Error fetching historical metrics: {str(e)}")
            return Response({
                'error': str(e),
                'meth_snail_panic': 'The timeline is unraveling!',
                'hamster_emergency': 'Deploying temporal stability duct tape'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class OptimizationProfileViewSet(viewsets.ModelViewSet):
    queryset = OptimizationProfile.objects.all()
    serializer_class = OptimizationProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class OptimizationResultViewSet(viewsets.ModelViewSet):
    queryset = OptimizationResult.objects.all()
    serializer_class = OptimizationResultSerializer
    permission_classes = [permissions.IsAuthenticated]


class SystemAlertViewSet(viewsets.ModelViewSet):
    queryset = SystemAlert.objects.all()
    serializer_class = SystemAlertSerializer
    permission_classes = [permissions.IsAuthenticated]


class AutoTuningViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_tuner(self):
        return WebAutoTuner()

    @action(detail=False, methods=['get'])
    @async_view
    async def current_state(self, request):
        try:
            tuner = self.get_tuner()
            state = await tuner._get_system_state()
            if not state:
                return Response(
                    {'error': 'No metrics available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(state)
        except Exception as e:
            return Response(
                {'error': f'Failed to get system state: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    @async_view
    async def recommendations(self, request):
        try:
            tuner = self.get_tuner()
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 5))
            
            recs = await tuner._get_recommendations()
            
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_recs = recs[start_idx:end_idx]
            
            response_data = {
                'recommendations': [tuner._tuning_to_dict(r) for r in paginated_recs],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_recommendations': len(recs)
                }
            }
            return Response(response_data)
        except ValueError as e:
            return Response(
                {'error': f'Invalid pagination parameters: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get recommendations: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    @async_view
    async def apply_tuning(self, request):
        try:
            tuner = self.get_tuner()
            if not request.data:
                return Response(
                    {'error': 'No tuning data provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            tuning_data = request.data.copy()
            tuning_data['user_id'] = request.user.id
            
            result = await tuner._apply_tuning(tuning_data)
            if not result:
                return Response(
                    {'error': 'Failed to apply tuning'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response_data = {
                'id': str(result.id),
                'timestamp': result.timestamp.isoformat(),
                'actions_taken': result.actions_taken,
                'metrics': {
                    'before': result.metrics_before,
                    'after': result.metrics_after
                },
                'success': result.success,
                'error_message': result.error_message
            }
            
            return Response(response_data)
        except Exception as e:
            return Response(
                {'error': f'Error applying tuning: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        return Response({
            'endpoints': {
                'current_state': '/api/auto-tuning/current_state/',
                'recommendations': '/api/auto-tuning/recommendations/',
                'apply_tuning': '/api/auto-tuning/apply_tuning/'
            },
            'documentation': {
                'current_state': 'Get current system metrics and state',
                'recommendations': 'Get system optimization recommendations with pagination',
                'apply_tuning': 'Apply a specific tuning recommendation'
            },
            'version': 'web-auto-tuner-1.0'
        })
class UserPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPreferences.objects.filter(user=self.request.user)

    @action(detail=False, methods=['patch'])
    def update_optimization_level(self, request):
        try:
            preferences = self.get_queryset().first()
            level = request.data.get('optimization_level')

            if level not in ['conservative', 'balanced', 'aggressive', 'meth_snail']:
                return Response({
                    'error': 'Invalid optimization level',
                    'meth_snail_advice': 'Try something more... cosmic, man',
                    'hamster_suggestion': 'optimization-level duct tape required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            preferences.optimization_level = level
            preferences.save()

            return Response({
                'status': 'success',
                'message': f'Optimization level updated to {level}',
                'meth_snail_approval': 'Your vibes are now aligned',
                'hamster_status': 'Applying optimization-grade duct tape'
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'meth_snail_panic': 'The optimization... it\'s not flowing, man',
                'hamster_emergency': 'Deploying emergency duct tape reserves'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AutoTuningResultViewSet(viewsets.ModelViewSet):
    serializer_class = AutoTuningResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AutoTuningResult.objects.filter(user=self.request.user)

class SystemConfigurationViewSet(viewsets.ModelViewSet):
    """
    Sir Hawkington's distinguished viewset for managing system configurations.
    
    Sir Hawkington oversees these configurations with his monocle of inspection,
    ensuring that your system remains in a state of distinguished order.
    """
    serializer_class = SystemConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only configurations belonging to the current user.
        Sir Hawkington insists on proper privacy!
        """
        user = self.request.user
        logger.info(f"🧐 Sir Hawkington is fetching configurations for {user.username} with distinguished elegance!")
        return SystemConfiguration.objects.filter(user=user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        """
        Create a new configuration for the current user.
        Sir Hawkington will oversee this process with his distinguished elegance.
        """
        logger.info(f"🧐 Sir Hawkington is creating a new configuration for {self.request.user.username}!")
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        Apply a configuration by setting it as active.
        Sir Hawkington will apply this configuration with his distinguished elegance.
        """
        configuration = self.get_object()
        
        # Set this configuration as active
        configuration.is_active = True
        configuration.save()
        
        logger.info(f"🧐 Sir Hawkington has applied the '{configuration.name}' configuration with distinguished elegance!")
        
        # Return the updated configuration
        serializer = self.get_serializer(configuration)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active configurations for the current user.
        Sir Hawkington will fetch these with his distinguished elegance.
        """
        user = request.user
        active_configs = SystemConfiguration.objects.filter(user=user, is_active=True)
        
        logger.info(f"🧐 Sir Hawkington is fetching active configurations for {user.username}!")
        
        serializer = self.get_serializer(active_configs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get configurations filtered by type.
        Sir Hawkington appreciates proper organization!
        """
        user = request.user
        config_type = request.query_params.get('type', None)
        
        if not config_type:
            return Response(
                {"detail": "Sir Hawkington requires a configuration type parameter!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        configs = SystemConfiguration.objects.filter(user=user, config_type=config_type)
        
        logger.info(f"🧐 Sir Hawkington is fetching {config_type} configurations for {user.username}!")
        
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)
