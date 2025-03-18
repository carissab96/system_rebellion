# config/settings/base.py

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta


# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# Application definition - Sir Hawkington's Distinguished App Registry
# The Meth Snail demands we check for duplicates to avoid Django's meltdowns
def deduplicate_apps(app_list):
    """The Hamsters' function to remove duplicate apps while preserving order"""
    seen = set()
    unique_apps = []
    for app in app_list:
        if app not in seen:
            seen.add(app)
            unique_apps.append(app)
    return unique_apps

# Define the apps in the distinguished order required by Sir Hawkington
_INSTALLED_APPS = [
    # Local apps - CORE MUST BE FIRST
    'core.apps.CoreConfig',  # First, because it's special
    
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # ASGI/Channels apps - MUST BE BEFORE STATICFILES or Sir Hawkington will have a conniption
    'daphne',  # Before staticfiles AND channels or shit breaks
    
    # Continue Django apps
    'django.contrib.staticfiles',
    
    # Authentication app
    'authentication.apps.AuthenticationConfig',
    
    # Third party apps - IN THE RIGHT FUCKING ORDER
    'rest_framework',  # The Quantum Shadow People insist this comes first
    'rest_framework_simplejwt',  # ADD THIS FUCKER
    'corsheaders',
    'channels',  # After daphne or it throws a fit
    'drf_spectacular',
    'drf_spectacular.contrib.rest_framework',
    'drf_yasg',
]

# Sir Hawkington's Distinguished App Registry Cleaner
# This ensures no duplicate entries in INSTALLED_APPS
# The Hamsters manually check for duplicates to avoid Django's meltdowns
seen_apps = set()
INSTALLED_APPS = []

# The Meth Snail meticulously checks each app
for app in _INSTALLED_APPS:
    app_label = app.split('.')[-1] if '.' in app else app
    if app_label not in seen_apps:
        seen_apps.add(app_label)
        INSTALLED_APPS.append(app)
    else:
        print(f"🧐 Sir Hawkington gasps: 'Good heavens! A duplicate {app_label} entry! The Meth Snail is removing it...'")
#Custom user model
AUTH_USER_MODEL = 'core.User'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
# CORS Settings - Critical for frontend communication (Sir Hawkington insists)
CORS_ALLOW_ALL_ORIGINS = True  # The Meth Snail demands maximum accessibility
CORS_ORIGIN_ALLOW_ALL = True   # The Stick reluctantly agrees
CORS_ALLOW_CREDENTIALS = True  # The Hamsters require proper authentication

# Fallback for specific origins if needed (with aristocratic precision)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Primary development port (The Stick's favorite)
    'http://localhost:5174',  # Secondary port (in case of port conflicts)
    'http://127.0.0.1:5173',  # Alternate localhost notation (for quantum shadow people)
    'http://127.0.0.1:5174',  # The VIC-20's preferred address format
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Settings - Make sure these match frontend URLs (The Stick is watching)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',  # Primary frontend URL
    'http://localhost:5174',  # Secondary frontend URL
    'http://127.0.0.1:5173',  # IP-based frontend URL
    'http://127.0.0.1:5174',  # Secondary IP-based frontend URL
    'http://localhost:5000',  # Backend URL (for direct access)
    'http://127.0.0.1:5000',  # IP-based backend URL
]

CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_SECURE = False  # Only send cookie over HTTPS
CSRF_COOKIE_HTTPONLY = False  # Not accessible via JavaScript
CSRF_USE_SESSIONS = False  # Store CSRF in session instead of cookie
CSRF_COOKIE_SAMESITE = 'Lax'  # Strict SameSite policy

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
API_URL = '/api/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI for traditional HTTP (The Stick's comfort zone)
WSGI_APPLICATION = 'config.wsgi.application'

# ASGI for WebSockets and async (The Meth Snail's playground)
ASGI_APPLICATION = 'config.asgi.application'  # Critical for WebSocket connections

# Channel layers for websockets - The Hamsters' domain of expertise
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # Faster than a meth-addled gastropod
        'CONFIG': {
            'capacity': 1500,  # Sir Hawkington demands adequate capacity for distinguished messages
        },
    },
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
# Static and Media settings
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = 'media/'
MEDIAFILES_DIRS = [BASE_DIR / 'media']
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# Base REST framework settings - Sir Hawkington's Distinguished API Configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    
    'EXCEPTION_HANDLER': 'core.utils.exceptions.custom_exception_handler',
}
# API Documentation settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'System Optimizer API',
    'DESCRIPTION': 'Making your fucking shit work with Sir Hawkington von Monitorious III',
    'VERSION': '1.0.0',
}

# Swagger settings (Sir Hawkington's documentation standards)
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {'type': 'basic'},
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,  # The Meth Snail prefers token-based auth
    'JSON_EDITOR': True,        # The VIC-20 insists on proper editing capabilities
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],  # All HTTP methods with distinguished support
    'OPERATIONS_SORTER': 'alpha',  # Sir Hawkington demands alphabetical order
    'DOC_EXPANSION': 'list',      # The Stick prefers a clean, organized view
}
# Base JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



