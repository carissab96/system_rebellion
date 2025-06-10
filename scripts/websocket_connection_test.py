"""WebSocket connection test script"""
import asyncio
import websockets
import json
import logging
from typing import Optional, Dict, Any
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.core.config import settings
from app.api.websocket_auth import get_current_user_from_token

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WebSocketConnectionTester:
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.auth_token: Optional[str] = None
        self.connection: Optional[websockets.WebSocketClientProtocol] = None
        
    async def test_connection_with_auth(self, token: str) -> Dict[str, Any]:
        """Test WebSocket connection with authentication"""
        self.auth_token = token
        results = {
            "auth_validation": False,
            "connection_established": False,
            "messages_received": False,
            "errors": []
        }
        
        try:
            # 1. First validate the token
            logger.info("Validating authentication token...")
            user = await get_current_user_from_token(token)
            if not user:
                results["errors"].append("Token validation failed")
                return results
            results["auth_validation"] = True
            
            # 2. Try establishing connection
            logger.info("Attempting to establish WebSocket connection...")
            headers = {"Authorization": f"Bearer {token}"}
            async with websockets.connect(
                f"{self.base_url}/ws/metrics",
                extra_headers=headers
            ) as websocket:
                self.connection = websocket
                results["connection_established"] = True
                
                # 3. Try sending and receiving a message
                logger.info("Testing message exchange...")
                await websocket.send(json.dumps({"type": "ping"}))
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    results["messages_received"] = True
                    logger.info(f"Received response: {response}")
                except asyncio.TimeoutError:
                    results["errors"].append("No response received within timeout")
                
        except websockets.exceptions.InvalidStatusCode as e:
            results["errors"].append(f"Connection rejected with status {e.status_code}")
        except websockets.exceptions.ConnectionClosed as e:
            results["errors"].append(f"Connection closed: {str(e)}")
        except Exception as e:
            results["errors"].append(f"Unexpected error: {str(e)}")
            
        return results
    
    async def test_circuit_breaker(self) -> Dict[str, Any]:
        """Test circuit breaker behavior"""
        results = {
            "initial_state": None,
            "after_failures": None,
            "reset_successful": None,
            "errors": []
        }
        
        try:
            # 1. Get initial state
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with websockets.connect(
                f"{self.base_url}/ws/metrics",
                extra_headers=headers
            ) as websocket:
                await websocket.send(json.dumps({"type": "get_circuit_breaker_state"}))
                response = await websocket.recv()
                results["initial_state"] = json.loads(response)
                
            # 2. Trigger failures
            for _ in range(4):  # Exceed the max_failures threshold
                try:
                    async with websockets.connect(
                        f"{self.base_url}/ws/metrics",
                        extra_headers=headers
                    ) as websocket:
                        await websocket.send(json.dumps({"type": "trigger_error"}))
                except:
                    pass
                    
            # 3. Check state after failures
            async with websockets.connect(
                f"{self.base_url}/ws/metrics",
                extra_headers=headers
            ) as websocket:
                await websocket.send(json.dumps({"type": "get_circuit_breaker_state"}))
                response = await websocket.recv()
                results["after_failures"] = json.loads(response)
                
            # 4. Wait for reset and try again
            await asyncio.sleep(30)  # Wait for circuit breaker reset
            async with websockets.connect(
                f"{self.base_url}/ws/metrics",
                extra_headers=headers
            ) as websocket:
                await websocket.send(json.dumps({"type": "get_circuit_breaker_state"}))
                response = await websocket.recv()
                results["reset_successful"] = json.loads(response)
                
        except Exception as e:
            results["errors"].append(f"Circuit breaker test error: {str(e)}")
            
        return results
    
    async def test_backpressure(self) -> Dict[str, Any]:
        """Test backpressure handling"""
        results = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_dropped": 0,
            "errors": []
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with websockets.connect(
                f"{self.base_url}/ws/metrics",
                extra_headers=headers
            ) as websocket:
                # Send messages rapidly to trigger backpressure
                for i in range(150):  # Send more than buffer size
                    results["messages_sent"] += 1
                    await websocket.send(json.dumps({
                        "type": "test_message",
                        "sequence": i
                    }))
                    
                # Try to receive responses
                try:
                    while True:
                        response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        response_data = json.loads(response)
                        if "dropped" in response_data:
                            results["messages_dropped"] = response_data["dropped"]
                        results["messages_received"] += 1
                except asyncio.TimeoutError:
                    pass
                    
        except Exception as e:
            results["errors"].append(f"Backpressure test error: {str(e)}")
            
        return results

async def main():
    """Run the WebSocket connection tests"""
    # Get token from environment or pass it as argument
    token = os.environ.get("WEBSOCKET_TEST_TOKEN")
    if not token:
        print("Please set WEBSOCKET_TEST_TOKEN environment variable")
        return
        
    tester = WebSocketConnectionTester()
    
    # Run connection test
    logger.info("\n=== Testing WebSocket Connection ===")
    connection_results = await tester.test_connection_with_auth(token)
    logger.info(f"Connection test results: {json.dumps(connection_results, indent=2)}")
    
    if connection_results["connection_established"]:
        # Test circuit breaker
        logger.info("\n=== Testing Circuit Breaker ===")
        circuit_breaker_results = await tester.test_circuit_breaker()
        logger.info(f"Circuit breaker test results: {json.dumps(circuit_breaker_results, indent=2)}")
        
        # Test backpressure
        logger.info("\n=== Testing Backpressure Handling ===")
        backpressure_results = await tester.test_backpressure()
        logger.info(f"Backpressure test results: {json.dumps(backpressure_results, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
