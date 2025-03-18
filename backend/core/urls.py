from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from core import views
from core.api import urls as api_urls
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('', views.home, name='home'), 
    path('dashboard/', views.dashboard, name='dashboard'),  # Added trailing slash for consistency
    path('api/test-data/', views.test_data, name='test-data'),  # Added trailing slash for consistency
    path('api/', include(api_urls)),
    # Remove duplicate JWT token endpoints as they're already in api_urls
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]