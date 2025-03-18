# config/settings/development.py - Sir Hawkington's Development Configuration
# The Meth Snail's special import trick to avoid duplicate entries
# First, import everything from base settings
from .base import *

# Then, deduplicate the INSTALLED_APPS to avoid Sir Hawkington's monocle from popping out
# This is done by creating a new list with only unique entries while preserving order
seen_apps = set()
unique_apps = []

for app in INSTALLED_APPS:
    if app not in seen_apps:
        seen_apps.add(app)
        unique_apps.append(app)
    else:
        print(f"🧐 Sir Hawkington gasps: 'Good heavens! A duplicate {app} entry! Removing the imposter...'")

# Replace the INSTALLED_APPS with the deduplicated list
INSTALLED_APPS = unique_apps

# Add development-specific apps without duplicating
DEV_APPS = ['debug_toolbar', 'channels_redis']

# The Hamsters carefully check for duplicates before adding to INSTALLED_APPS
for app in DEV_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

print("HOLY SHIT, I'M ACTUALLY BEING USED!")
print("Show me where Django touched you...")

# Debug settings - The Meth Snail's playground
DEBUG = True  # Is this ACTUALLY True or is it lying like my ex?
print(f"DEBUG is set to: {DEBUG}")

# Host settings - The Stick's anxiety management zone
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # Fuck it, let's go nuclear for development
    '*'  # The universal "I don't give a fuck" wildcard
]
print(f"ALLOWED_HOSTS contains: {ALLOWED_HOSTS}")

# Add debug toolbar to installed apps - The VIC-20's development toolkit
# Check for duplicate apps to avoid Sir Hawkington's monocle from popping out in shock
DEV_APPS = ['debug_toolbar', 'channels_redis']

# The Hamsters carefully check for duplicates before adding to INSTALLED_APPS
for app in DEV_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

# The Meth Snail ensures no duplicate rest_framework entries exist
if INSTALLED_APPS.count('rest_framework') > 1:
    print("🧐 Sir Hawkington gasps: 'Good heavens! A duplicate rest_framework entry! Removing the imposter...'")
    # Keep only the first occurrence and remove others
    first_index = INSTALLED_APPS.index('rest_framework')
    INSTALLED_APPS = INSTALLED_APPS[:first_index+1] + [app for app in INSTALLED_APPS[first_index+1:] if app != 'rest_framework']

# Debug middleware - The VIC-20's 8-bit wisdom
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS first (The Hamsters insist)
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # Debug toolbar for development
] + MIDDLEWARE  # Add the base middleware after our additions

# Debug toolbar settings (Sir Hawkington's debugging monocle)
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,  # Always show the toolbar (The Meth Snail demands visibility)
    'RESULTS_CACHE_SIZE': 5,  # The VIC-20 suggests a reasonable cache size
    'RENDER_PANELS': True,    # The Hamsters insist on rendering all panels
    'SHOW_TEMPLATE_CONTEXT': True,  # The Stick needs all context for proper anxiety management
}

# Proxy settings for development (The Quantum Shadow People's domain)
USE_PROXY = True  # Enable proxy for development
PROXY_BASE_URL = '/api/'  # Base URL for API requests through the proxy
WS_PROXY_URL = '/ws/'  # WebSocket URL through the proxy

# CSRF Configuration - Sir Hawkington's Cross-Site Request Forgery Shield
CSRF_COOKIE_SECURE = False  # Set to False for development (no HTTPS)
CSRF_COOKIE_HTTPONLY = False  # Set to False so JavaScript can access it
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF
CSRF_COOKIE_SAMESITE = 'Lax'  # Less restrictive for development

# Add a health check endpoint that doesn't require authentication
HEALTH_CHECK_URL = 'api/health-check/'

# REST Framework settings for development - Sir Hawkington's API Configuration
# The Meth Snail checks if REST_FRAMEWORK exists before modifying it
if 'REST_FRAMEWORK' not in globals():
    # The VIC-20's 8-bit wisdom: Define it if it doesn't exist
    print("🧐 Sir Hawkington adjusts his monocle: 'I say, REST_FRAMEWORK is missing! Creating it from scratch...'")
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
    }

# The Hamsters add their special sauce to REST_FRAMEWORK
REST_FRAMEWORK['UNAUTHENTICATED_USER'] = None
