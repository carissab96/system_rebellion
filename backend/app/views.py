from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .models import SystemMetrics, OptimizationProfile, SystemAlert
from .recommendations import RecommendationsEngine
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
@login_required
@ensure_csrf_cookie
def dashboard(request):
    """Dashboard view - Sir Hawkington's Control Room"""
    try:
        latest_metrics = SystemMetrics.objects.order_by('-timestamp').first()
        engine = RecommendationsEngine()
        
        recommendations_summary = None
        if latest_metrics:
            recommendations_summary = engine.get_optimization_summary(latest_metrics)

        context = {
            'metrics': SystemMetrics.objects.all().order_by('-timestamp')[:5],
            'profiles': OptimizationProfile.objects.filter(user=request.user),
            'alerts': SystemAlert.objects.filter(user=request.user).order_by('-timestamp')[:5],
            'user_preferences': request.user.optimization_preferences,
            'recommendations': recommendations_summary,
            'latest_metrics': latest_metrics,
            'csrf_token': get_token(request),  # Add CSRF token to context
        }
        return render(request, 'core/dashboard.html', context)
    except Exception as e:
        return JsonResponse({
            'error': 'Dashboard malfunction',
            'details': str(e),
            'meth_snail_status': 'Dashboard is having a bad trip, man',
            'hamster_action': 'Applying dashboard-grade duct tape',
            'stick_panic': 'DASHBOARD REGULATIONS BREACHED!'
        }, status=500)

@ensure_csrf_cookie
def home(request):
    """Home view - The Meth Snail's Welcome Mat"""
    return render(request, 'core/home.html')

@login_required
@ensure_csrf_cookie
def test_data(request):
    """Test Data API - The Hamsters' Data Playground"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        offset = (page - 1) * page_size
        limit = offset + page_size
        
        data = {
            'metrics': list(SystemMetrics.objects.order_by('-timestamp')[offset:limit].values()),
            'profiles': list(OptimizationProfile.objects.select_related('user')[offset:limit].values()),
            'alerts': list(SystemAlert.objects.order_by('-created_at')[offset:limit].values()),
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_metrics': SystemMetrics.objects.count(),
                'total_profiles': OptimizationProfile.objects.count(),
                'total_alerts': SystemAlert.objects.count()
            }
        }
        return JsonResponse(data, safe=False)
        
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'error': 'Invalid pagination parameters',
            'details': str(e),
            'meth_snail_math': 'These numbers are like... not cosmic, man',
            'hamster_suggestion': 'Try counting the duct tape rolls instead'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e),
            'meth_snail_panic': 'The data... it is everywhere man!',
            'hamster_status': 'Running out of emergency duct tape'
        }, status=500)

# core/views.pyLogin failed: Failed to execute 'json' on 'Response': Unexpected end of JSON input

def error_403(request, exception=None):
    return JsonResponse({
        'error': 'Forbidden',
        'code': 403,
        'message': 'Access denied by aristocratic decree',
        'meth_snail_advice': 'Try adding more tinfoil to your hat',
        'hamster_suggestion': 'Have you tried duct tape?',
        'shadow_people': 'We blocked this through your router',
        'VIC20_status': 'SHALL WE PLAY A GAME INSTEAD?'
    }, status=403)

def error_404(request, exception=None):
    return JsonResponse({
        'error': 'Not Found',
        'code': 404,
        'message': 'Page has ascended to a higher plane of existence',
        'meth_snail_location': 'Check the lawn mower shop',
        'hamster_status': 'Too busy buying more duct tape',
        'shadow_people': 'We might have redirected this through 1983',
        'stick_anxiety': 'REGULATIONS VIOLATED!'
    }, status=404)

def error_500(request, exception=None):  # Add exception parameter
    return JsonResponse({
        'error': 'Server Error',
        'code': 500,
        'message': 'The server is having an existential crisis',
        'meth_snail_diagnosis': 'Server needs more meth',
        'hamster_solution': 'Applied emergency duct tape',
        'shadow_people': 'Have you tried turning your router off and on again?',
        'ET_status': 'Still trying to phone home',
        'stick_status': 'Writing new chapters about this incident'
    }, status=500)