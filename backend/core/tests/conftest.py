import pytest
import django
import uuid
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Configure Django settings before importing models
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME'),
                'USER': os.getenv('DB_USER'),
                'PASSWORD': os.getenv('DB_PASSWORD'),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'rest_framework_simplejwt',
            'drf_spectacular',
            'debug_toolbar',
            'core.apps.CoreConfig',
        ],
        MIDDLEWARE=[
             'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        ],
        ROOT_URLCONF='config.urls',
        AUTH_USER_MODEL='core.User',
        ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
        SECRET_KEY='test-key-not-for-production',
        STATIC_URL='/static/',
        STATIC_ROOT='static',
        MEDIA_URL='/media/',
        MEDIA_ROOT='media',
        USE_TZ=True,
        TIME_ZONE='UTC',
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
        },
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }],
    )

django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import (
    SystemMetrics,
    OptimizationProfile,
    OptimizationResult,
    SystemAlert,
    UserProfile,
    UserPreferences
)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    User = get_user_model()
    def make_user(username=None, password="testpass123", email=None):
        if username is None:
            username = f"testuser_{uuid.uuid4().hex[:8]}"
        if email is None:
            email = f"{username}@example.com"
            
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            optimization_preferences={}
        )
    return make_user

@pytest.fixture
def create_user_with_profile(create_user):
    def make_user_with_profile(
        username=None,
        password="testpass123",
        email=None,
        operating_system="linux",
        os_version="5.15",
        linux_distro="Ubuntu",
        linux_distro_version="20.04",
        cpu_cores=4,
        total_memory=8,
    ):
        user = create_user(username=username, password=password, email=email)
        UserProfile.objects.filter(user=user).update(
            operating_system=operating_system,
            os_version=os_version,
            linux_distro=linux_distro,
            linux_distro_version=linux_distro_version,
            cpu_cores=cpu_cores,
            total_memory=total_memory,
        )
        return user
    return make_user_with_profile

@pytest.fixture
def sample_metrics_batch(create_user):
    user = create_user()
    metrics = []
    for i in range(5):
        metrics.append(SystemMetrics.objects.create(
            cpu_usage=40.0 + i * 10,
            memory_usage=60.0 + i * 5,
            disk_usage=70.0 + i * 2,
            network_usage=1000.0 + i * 100,
            process_count=120 + i
        ))
    return metrics