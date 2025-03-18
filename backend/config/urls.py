"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from core.views import error_403, error_404, error_500

# Use drf_spectacular for API documentation
spectacular_urls = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Legacy URLs for compatibility
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='schema-swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='schema-redoc'),
]

urlpatterns = [
    # The stick insisted on keeping admin properly formatted
    path('admin/', admin.site.urls),
    # Include core URLs for dashboard and other views
    path('', include('core.urls')),
    # Core API paths
    path('api/', include('core.api.urls')),
    # ML module paths (now with correct routing!)
    path('api/ml/', include('core.ml.urls')),
]  

# Add API documentation URLs
urlpatterns += spectacular_urls

# Static and media files (the stick wouldn't let us remove this)
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
# Error handlers (now with extra chaos)
handler404 = 'core.views.error_404'  # Page not found (probably stolen by shadow people)
handler500 = 'core.views.error_500'  # Server error (meth snail is investigating)
handler403 = 'core.views.error_403'  # Forbidden (hamsters deny everything)