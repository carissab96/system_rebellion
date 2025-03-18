# core/routing.py
from django.urls import re_path
from core.consumers import MetricsConsumer  # Updated import

websocket_urlpatterns = [
    re_path(r'ws/metrics/$', MetricsConsumer.as_asgi()),
]