from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.websockets import websocket_manager
from app.api.websocket_auth import authenticate_websocket
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.core.database import get_db
from app.core.resilience import get_circuit_breaker
import asyncio
import logging
from datetime import datetime, timezone
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize circuit breaker for metrics
metrics_circuit_breaker = get_circuit_breaker(
    name="metrics_websocket", 
    max_failures=3,
    reset_timeout=30,
    exponential_backoff_factor=1.5
)


async def system_metrics_socket(websocket: WebSocket):

    """
    Sir Hawkington's Simplified System Metrics WebSocket
    
    This WebSocket endpoint provides real-time system metrics to authenticated clients.
    It implements a connection-first flow (accept connection before authentication),
    robust error handling, and resilience features.
    
    Flow:
    1. Accept WebSocket connection
    2. Request authentication from client
    3. Validate authentication token
    4. Send initial system info
    5. Begin metrics streaming loop
    6. Handle client messages and disconnections
    """
    # Generate unique ID for this client connection for logging
    client_id = f"client_{id(websocket)}"
    connection_active = False
    db = None
    
    try:
        # Accept the connection FIRST (website connection before auth)
        # This differs from traditional auth-first approaches
        await websocket.accept()
        print(f"WebSocket connection accepted for {client_id}")
        connection_active = True
        
        # Register the connection with the WebSocket manager for tracking
        # This allows for centralized management of all active connections
        await websocket_manager.connect(websocket)
        
        # Send connection established message and request authentication
        # This informs the client that the connection was successful and auth is needed
        await websocket.send_json({
            "type": "connection_established",
            "message": "Sir Hawkington welcomes you! Please provide authentication.",
            "client_id": client_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Wait for authentication message from frontend with timeout
        try:
            # Give client 10 seconds to send auth token
            # This prevents hanging connections from unauthenticated clients
            auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
            
            # Verify message type is "auth"
            # Enforce proper message format and protocol
            if auth_message.get("type") != "auth":
                await websocket.send_json({
                    "type": "error",
                    "message": "Expected authentication message",
                    "code": "auth_required"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Extract and validate token
            # Ensure token is present before attempting authentication
            token = auth_message.get("token", "")
            if not token:
                await websocket.send_json({
                    "type": "error",
                    "message": "No authentication token provided",
                    "code": "no_token"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Remove Bearer prefix if present and add to query params for auth function
            # This accommodates different token formats from various clients
            token = token.replace("Bearer ", "").strip()
            websocket.query_params = {"token": token}
            
        except asyncio.TimeoutError:
            # Client didn't send auth in time
            # Close connection with appropriate error message to prevent resource waste
            await websocket.send_json({
                "type": "error",
                "message": "Authentication timeout",
                "code": "auth_timeout"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        except Exception as e:
            # Handle any unexpected errors during authentication process
            # Log detailed error for debugging while sending generic message to client
            logger.error(f"Auth error: {str(e)} - Type: {type(e).__name__}")
            await websocket.send_json({
                "type": "error",
                "message": "Authentication error",
                "code": "auth_error"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Authenticate the user using the provided token
        # This verifies the user's identity and permissions
        user = await authenticate_websocket(websocket)
        if not user:
            # If authentication fails, inform client and close connection
            await websocket.send_json({
                "type": "auth_failed",
                "message": "Authentication required for System Rebellion access",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        logger.info(f"WebSocket authenticated for user {user.username} ({client_id})")
        
        # Get database session for any DB operations needed during the connection
        # This provides access to persistent storage during the WebSocket session
        db = next(get_db())
        
        # Send initial system info to provide immediate context to the client
        # This gives baseline system information before starting metrics stream
        system_info = await get_system_info()
        await websocket.send_json({
            "type": "system_info",
            "data": system_info,
            "message": "Sir Hawkington welcomes you to the System Metrics WebSocket!"
        })
        
        # Initialize metrics service to collect system performance data
        # This service handles the actual metrics collection logic
        metrics_service = await SimplifiedMetricsService.get_instance()
        update_interval = 1.0  # seconds - default refresh rate
        
        # Main WebSocket loop - continuously sends metrics until disconnection
        # This is the core of the WebSocket functionality
        while True:
            # Record start time to maintain consistent update intervals
            # This ensures metrics are sent at regular intervals regardless of processing time
            loop_start_time = time.time()
            
            # Check circuit breaker status before attempting to get metrics
            # This prevents repeated attempts when the system is in a failure state
            if metrics_circuit_breaker.is_open():
                # Circuit is open (too many failures), inform client and wait
                # This implements the circuit breaker pattern for fault tolerance
                wait_time = metrics_circuit_breaker.get_wait_time()
                await websocket.send_json({
                    "type": "circuit_breaker",
                    "status": "open",
                    "message": f"Too many errors, service cooling down for {wait_time}s",
                    "retry_after": wait_time
                })
                await asyncio.sleep(min(wait_time, update_interval))
                continue
            
            # Get metrics with backpressure handling to prevent system overload
            # This ensures the system remains responsive even under heavy load
            metrics = await metrics_backpressure.handle(metrics_service.get_metrics)
            metrics_circuit_breaker.record_success()
            
            # Send metrics to client with current timestamp
            # This delivers the real-time system data to the connected client
            await websocket.send_json({
                "type": "metrics_update",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": metrics
            })
            
            # Check for client messages to implement bidirectional communication
            # This allows clients to control aspects of the metrics stream
            try:
                # Set timeout to a fraction of update interval to remain responsive
                # This ensures we don't block the loop for too long while waiting for messages
                message_timeout = min(0.5, update_interval / 2)
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=message_timeout
                )
                
                # Process client message based on type and data
                # This implements the command pattern for client-server interaction
                try:
                    msg = json.loads(message)
                    msg_type = msg.get("type", "")
                    msg_data = msg.get("data", {})
                    
                    if msg_type == "ping":
                        # Respond to ping requests for connection health monitoring
                        # This allows clients to verify the connection is still alive
                        await websocket.send_json({
                            "type": "pong", 
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                    elif msg_type == "set_interval":
                        # Allow client to adjust metrics update frequency within limits
                        # This provides flexibility while preventing excessive requests
                        update_interval = max(1.0, min(10.0, float(msg_data.get("interval", 1.0))))
                        await websocket.send_json({
                            "type": "interval_update", 
                            "interval": update_interval,
                            "message": f"Update interval set to {update_interval} seconds"
                        })
                    elif msg_type == "request_system_info":
                        # Provide updated system information on demand
                        # This allows clients to refresh baseline system data as needed
                        system_info = await get_system_info()
                        await websocket.send_json({
                            "type": "system_info",
                            "data": system_info
                        })
                    elif msg_type == "reset_circuit_breaker":
                        # Allow manual reset of circuit breakers after failures
                        # This provides a recovery mechanism for persistent issues
                        metrics_circuit_breaker.reset()
                        await metrics_service.reset_circuit_breakers()
                        await websocket.send_json({
                            "type": "circuit_breaker_reset",
                            "message": "All circuit breakers have been reset"
                        })
                except json.JSONDecodeError:
                    # Handle malformed JSON messages gracefully
                    # This prevents crashes from invalid client input
                    logger.warning(f"Received non-JSON message from client {client_id}")
                except Exception as e:
                    # Catch any other errors during message processing
                    # This ensures the WebSocket remains stable despite client errors
                    logger.error(f"Error processing message from client {client_id}: {str(e)}")
            except asyncio.TimeoutError:
                # No message received within timeout, which is expected behavior
                # This is not an error condition, just continue with the loop
                pass
            
            # Calculate sleep time to maintain consistent update interval
            # This ensures metrics are sent at regular intervals regardless of processing time
            elapsed = time.time() - loop_start_time
            sleep_time = max(0.1, update_interval - elapsed)
            await asyncio.sleep(sleep_time)
                
    except WebSocketDisconnect:
        # WebSocketDisconnect exception is raised when the client closes the connection
        # This is a normal part of the WebSocket lifecycle and indicates the client
        # has terminated the connection either intentionally (e.g. user navigating away)
        # or due to network issues (connection dropped)
        
        # Log the disconnection event with the client identifier for tracking purposes
        logger.info(f"WebSocket for {client_id} disconnected")
        
        # Record the disconnection as a failure in the circuit breaker
        # This helps track connection stability and may trigger circuit breaking
        # if too many disconnections occur in a short period
        metrics_circuit_breaker.record_failure()
        logger.info(f"WebSocket for {client_id} disconnected")
        metrics_circuit_breaker.record_failure()
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}", exc_info=True)
        metrics_circuit_breaker.record_failure()
        try:
            await websocket.send_json({
                "type": "connection_error",
                "message": f"Sir Hawkington regrets to inform you of a connection error: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "retry_after": metrics_circuit_breaker.get_wait_time()
            })
        except:
            pass
    finally:
        if connection_active:
            await websocket_manager.disconnect(websocket)
            logger.info(f"WebSocket disconnected for {client_id}")
        
        if db:
            db.close()