"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.
Now with 100% more WebSocket fuckery and proxy support!

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# config/asgi.py - Sir Hawkington's Distinguished WebSocket Configuration
import os
import logging
import django

# Set the Django settings module with aristocratic authority BEFORE any imports
# The Stick insists this must be done first to avoid anxiety-inducing configuration errors
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# The Meth Snail demands we initialize Django before importing any app modules
# This prevents the dreaded AppRegistryNotReady error
django.setup()

# The VIC-20's 8-bit wisdom: Only import Django components AFTER setting up Django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# The Hamsters' domain - imported after Django is properly initialized
from core.routing import websocket_urlpatterns

# Configure logging for WebSocket connections - The Stick requires proper monitoring
logger = logging.getLogger('websockets')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('🧐 Sir Hawkington observes: %(message)s'))
logger.addHandler(handler)

# Log WebSocket connection attempts with distinguished elegance
class LoggingMiddleware:
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            logger.debug(f"🐌 The Meth Snail reports a WebSocket connection from {scope['client']}!")
            logger.debug(f"🐹 The Hamsters are preparing the WebSocket path: {scope['path']}!")
        return await self.inner(scope, receive, send)

# This is the fucking key part - The VIC-20's 8-bit wisdom
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Standard HTTP handling
    "websocket": LoggingMiddleware(  # Add distinguished logging
        AllowedHostsOriginValidator(  # The Stick's security measures
            AuthMiddlewareStack(  # Proper fucking authentication
                URLRouter(
                    websocket_urlpatterns  # The Hamsters' routing configuration
                )
            )
        )
    ),
})
