# core/utils/exceptions.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging
import random

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Sir Hawkington's Distinguished Exception Handler
    Adds colorful error messages to the standard DRF exception handler
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, it's an unhandled exception
    if response is None:
        logger.error(f"🔥 Unhandled exception: {str(exc)}")
        return Response({
            'status': 'error',
            'message': 'Sir Hawkington regrets to inform you of a server error!',
            'error': str(exc),
            'meth_snail_panic': random_meth_snail_panic(),
            'hamster_status': random_hamster_status()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # For authentication errors, add some personality
    if response.status_code == 401:
        response.data = {
            'status': 'error',
            'message': 'Authentication required! Sir Hawkington cannot verify your papers! 📜',
            'error': response.data.get('detail', 'Invalid or expired token'),
            'meth_snail_panic': 'Your credentials are in another dimension!',
            'hamster_suggestion': 'Try authentication-grade duct tape'
        }
    
    # For permission errors
    elif response.status_code == 403:
        response.data = {
            'status': 'error',
            'message': 'Sir Hawkington denies you access to this resource! 🧐',
            'error': response.data.get('detail', 'You do not have permission'),
            'meth_snail_warning': 'The cosmic permissions are misaligned!',
            'hamster_advice': 'Perhaps more duct tape would help?'
        }
    
    # For not found errors
    elif response.status_code == 404:
        response.data = {
            'status': 'error',
            'message': 'Resource not found! Sir Hawkington has searched high and low! 🔍',
            'error': response.data.get('detail', 'Not found'),
            'meth_snail_theory': 'It might have slipped into a parallel universe',
            'hamster_status': 'Deploying search-and-rescue duct tape'
        }
    
    # For validation errors
    elif response.status_code == 400:
        response.data = {
            'status': 'error',
            'message': 'Invalid data! Sir Hawkington cannot process this! 📋',
            'errors': response.data,
            'meth_snail_advice': 'Your data needs cosmic alignment',
            'hamster_solution': 'Try validation-grade duct tape'
        }
    
    # For method not allowed
    elif response.status_code == 405:
        response.data = {
            'status': 'error',
            'message': 'Method not allowed! Sir Hawkington disapproves of your approach! ⛔',
            'error': response.data.get('detail', 'Method not allowed'),
            'meth_snail_suggestion': 'Try a different dimensional approach',
            'stick_panic': 'IMPROPER METHOD DETECTED!'
        }
    
    # For throttled requests
    elif response.status_code == 429:
        response.data = {
            'status': 'error',
            'message': 'Too many requests! Sir Hawkington requests you slow down! ⏱️',
            'error': response.data.get('detail', 'Request was throttled'),
            'meth_snail_status': 'Cosmic bandwidth overload',
            'hamster_action': 'Applying rate-limiting duct tape'
        }
    
    return response

def random_meth_snail_panic():
    """The Meth Snail's random panic messages"""
    panics = [
        "The API is having a cosmic meltdown!",
        "Your request broke the space-time continuum!",
        "The quantum shadow people have infiltrated the server!",
        "ERROR: Snail.exe has stopped responding to reality",
        "The server is experiencing interdimensional turbulence",
        "CRITICAL: Methamphetamine reserves at 2%!"
    ]
    return random.choice(panics)

def random_hamster_status():
    """The Hamsters' random status messages"""
    statuses = [
        "Deploying emergency duct tape protocols",
        "Hamster wheel spinning at maximum capacity",
        "Rerouting power to the primary duct tape reserves",
        "Hamster team dispatched with repair tape",
        "Activating the backup hamster generator",
        "Applying industrial-strength duct tape to the situation"
    ]
    return random.choice(statuses)
