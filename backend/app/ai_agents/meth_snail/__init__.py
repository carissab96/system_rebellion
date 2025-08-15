"""
Meth Snail Agent - High-energy optimization with caffeine-powered shell spinning.

This module provides the Meth Snail agent's API endpoints and WebSocket handlers
for real-time system optimization and monitoring.
"""

# Import the router from endpoints to make it available for the main app
from .meth_snail_endpoints import router

# Export the router for use in the main FastAPI app
__all__ = ['router']