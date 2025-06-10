"""WebSocket debugging utilities"""
import logging
import asyncio
from fastapi import WebSocket
from app.api.websocket_auth import get_current_user_from_token
from app.core.resilience import WebSocketCircuitBreaker, BackpressureHandler
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WebSocketDebugger:
    def __init__(self):
        self.auth_failures: Dict[str, Any] = {}
        self.circuit_breaker_state: Dict[str, Any] = {}
        self.backpressure_stats: Dict[str, Any] = {}
        
    async def debug_connection(self, websocket: WebSocket, token: str):
        """Debug a WebSocket connection attempt"""
        logger.info("Starting WebSocket connection debug...")
        
        # Test 1: Authentication
        logger.info("Testing authentication...")
        user = await get_current_user_from_token(token)
        self.auth_failures[token] = {
            "success": user is not None,
            "error": None if user else "Authentication failed",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if not user:
            logger.error("Authentication failed - check token validity and user existence")
            return
            
        # Test 2: Circuit Breaker State
        logger.info("Checking circuit breaker state...")
        circuit_breaker = WebSocketCircuitBreaker(
            name="debug_breaker",
            max_failures=3,
            reset_timeout=30
        )
        self.circuit_breaker_state = {
            "state": circuit_breaker.state,
            "failure_count": circuit_breaker.failure_count,
            "last_failure": circuit_breaker.last_failure_time
        }
        
        # Test 3: Backpressure
        logger.info("Checking backpressure handler...")
        backpressure = BackpressureHandler(
            name="debug_backpressure",
            max_buffer_size=100
        )
        self.backpressure_stats = {
            "buffer_size": backpressure.current_buffer_size,
            "dropped_messages": backpressure.dropped_message_count
        }
        
        return {
            "auth": self.auth_failures[token],
            "circuit_breaker": self.circuit_breaker_state,
            "backpressure": self.backpressure_stats
        }
    
    def print_diagnostic_report(self):
        """Print a diagnostic report of the debugging session"""
        logger.info("\n=== WebSocket Diagnostic Report ===")
        
        # Auth issues
        logger.info("\nAuthentication Status:")
        for token, data in self.auth_failures.items():
            logger.info(f"Token: {token[:10]}...")
            logger.info(f"Success: {data['success']}")
            if data['error']:
                logger.info(f"Error: {data['error']}")
                
        # Circuit breaker
        logger.info("\nCircuit Breaker Status:")
        logger.info(f"State: {self.circuit_breaker_state.get('state', 'Unknown')}")
        logger.info(f"Failures: {self.circuit_breaker_state.get('failure_count', 0)}")
        
        # Backpressure
        logger.info("\nBackpressure Status:")
        logger.info(f"Buffer Size: {self.backpressure_stats.get('buffer_size', 0)}")
        logger.info(f"Dropped Messages: {self.backpressure_stats.get('dropped_messages', 0)}")
