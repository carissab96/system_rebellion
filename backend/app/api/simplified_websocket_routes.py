from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.websockets import websocket_manager
from app.api.websocket_auth import get_current_user_from_token
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.services.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricCreate
from app.core.database import get_db
from app.core.resilience import get_circuit_breaker
from app.core.resilience.backpressure import BackpressureHandler
import asyncio
import logging
from datetime import datetime, timezone
import time
import json
import socket
import platform
import psutil
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information for the client
    """
    try:
        system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "memory_total": psutil.virtual_memory().total,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "python_version": platform.python_version()
        }
        return system_info
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return {
            "error": True,
            "message": "Failed to retrieve system information"
        }

# Initialize circuit breaker for metrics
metrics_circuit_breaker = get_circuit_breaker(
    name="metrics_websocket", 
    max_failures=3,
    reset_timeout=30,
    exponential_backoff_factor=1.5
)

# Initialize backpressure handler for metrics
metrics_backpressure = BackpressureHandler(
    name="metrics_websocket",
    max_buffer_size=100,
    sampling_strategy="latest"
)


@router.websocket("/system-metrics")
async def system_metrics_socket(websocket: WebSocket):
    """
    Sir Hawkington's Simplified System Metrics WebSocket with Database Persistence
    """
    client_id = f"client_{id(websocket)}"
    connection_active = False
    db = None
    user = None
    
    try:
        # Accept the connection FIRST
        await websocket.accept()
        print(f"WebSocket connection accepted for {client_id}")
        connection_active = True
        
        # Register the connection with the WebSocket manager
        await websocket_manager.connect(websocket)
        
        # Send connection established message and request authentication
        await websocket.send_json({
            "type": "connection_established",
            "message": "Sir Hawkington welcomes you! Please provide authentication.",
            "client_id": client_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Wait for authentication message from client
        try:
            auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
            
            # Validate authentication message format
            if not isinstance(auth_message, dict) or "token" not in auth_message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid authentication message format",
                    "code": "invalid_auth_format"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Extract and validate token
            token = auth_message.get("token", "")
            if not token:
                await websocket.send_json({
                    "type": "error",
                    "message": "No authentication token provided",
                    "code": "no_token"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Remove Bearer prefix if present
            token = token.replace("Bearer ", "").strip()
            
            # Authenticate the user
            user = await get_current_user_from_token(token)
            if not user:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid authentication token",
                    "code": "invalid_token"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
        except asyncio.TimeoutError:
            await websocket.send_json({
                "type": "error",
                "message": "Authentication timeout",
                "code": "auth_timeout"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        except Exception as e:
            logger.error(f"Auth error: {str(e)} - Type: {type(e).__name__}")
            await websocket.send_json({
                "type": "error",
                "message": "Authentication error",
                "code": "auth_error"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        logger.info(f"WebSocket authenticated for user {user.username} ({client_id})")
        
        # Get database session
        db = next(get_db())
        
        # Send initial system info
        system_info = await get_system_info()
        await websocket.send_json({
            "type": "system_info",
            "data": system_info,
            "message": "Sir Hawkington welcomes you to the System Metrics WebSocket!"
        })
        
        # Initialize metrics service
        metrics_service = await SimplifiedMetricsService.get_instance()
        update_interval = 1.0  # seconds
        
        # Main WebSocket loop with database persistence
        while True:
            loop_start_time = time.time()
            
            # Check circuit breaker status
            if not metrics_circuit_breaker.can_attempt_connection():
                wait_time = metrics_circuit_breaker.get_wait_time()
                await websocket.send_json({
                    "type": "circuit_breaker",
                    "status": "open",
                    "message": f"Too many errors, service cooling down for {wait_time}s",
                    "retry_after": wait_time
                })
                await asyncio.sleep(min(wait_time, update_interval))
                continue
            
            try:
                # Get metrics from service
                metrics = await metrics_service.get_metrics()
                
                # 🔥 DATABASE PERSISTENCE - Save metrics to database
                if user and db:
                    try:
                        # Create metric record for database
                        metric_create = MetricCreate(
                            user_id=user.id,  # Add required user_id field
                            cpu_usage=metrics.get('cpu', {}).get('percent', 0),
                            memory_usage=metrics.get('memory', {}).get('percent', 0),
                            disk_usage=metrics.get('disk', {}).get('percent', 0),
                            network=metrics.get('network', {}),  # Fix field name: network not network_usage
                            process_count=metrics.get('process_count', 0),
                            additional_metrics=metrics,  # Store full metrics as JSON
                            timestamp=datetime.now(timezone.utc)
                        )
                        
                        # Save to database using repository
                        await MetricsRepository.create_metric(db, metric_create)
                        logger.debug(f"💾 Metrics saved to database for user {user.username}")
                        
                    except Exception as db_error:
                        logger.error(f"Database save failed (non-critical): {db_error}")
                        # Don't break WebSocket if DB save fails
                
                # Record successful operation
                metrics_circuit_breaker.record_success()
                
                # Add metrics to backpressure handler
                if metrics_backpressure.add_item(metrics):
                    # Get buffered metrics to send
                    batch = metrics_backpressure.get_batch(max_batch_size=1)
                    
                    # Send each metrics update
                    for metric_data in batch:
                        message_to_send = {
                            "type": "metrics_update",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "data": metric_data
                        }
                        
                        # Debug logging
                        logger.info(f"📤 Sending metrics to {client_id}: keys={list(metric_data.keys()) if isinstance(metric_data, dict) else 'not_dict'}")
                        logger.debug(f"📤 Full metrics data structure: {json.dumps(metric_data, indent=2, default=str)[:500]}...")
                        
                        await websocket.send_json(message_to_send)
                else:
                    # Item was dropped due to backpressure
                    logger.warning(f"Metrics dropped due to backpressure for {client_id}")
                
            except Exception as e:
                # Record failure for circuit breaker
                metrics_circuit_breaker.record_failure()
                
                logger.error(f"Error getting metrics for {client_id}: {str(e)}")
                
                # Send error to client
                await websocket.send_json({
                    "type": "connection_error",
                    "message": f"Sir Hawkington regrets to inform you of a connection error: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                # Wait before retrying
                await asyncio.sleep(update_interval)
            
            # Check for client messages
            try:
                message_timeout = min(0.5, update_interval / 2)
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=message_timeout
                )
            
                # Process client message
                try:
                    msg = json.loads(message)
                    msg_type = msg.get("type", "")
                    msg_data = msg.get("data", {})
                
                    if msg_type == "ping":
                        await websocket.send_json({
                            "type": "pong", 
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                    elif msg_type == "set_interval":
                        update_interval = max(1.0, min(10.0, float(msg_data.get("interval", 1.0))))
                        await websocket.send_json({
                            "type": "interval_update", 
                            "interval": update_interval,
                            "message": f"Update interval set to {update_interval} seconds"
                        })
                    elif msg_type == "request_system_info":
                        system_info = await get_system_info()
                        await websocket.send_json({
                            "type": "system_info",
                            "data": system_info
                        })
                    elif msg_type == "reset_circuit_breaker":
                        metrics_circuit_breaker.reset()
                        await metrics_service.reset_circuit_breakers()
                        await websocket.send_json({
                            "type": "circuit_breaker_reset",
                            "message": "All circuit breakers have been reset"
                        })
                except json.JSONDecodeError:
                    logger.warning(f"Received non-JSON message from client {client_id}")
                except Exception as e:
                    logger.error(f"Error processing message from client {client_id}: {str(e)}")
            except asyncio.TimeoutError:
                # No message received, continue
                pass
        
            # Maintain consistent update interval
            elapsed = time.time() - loop_start_time
            sleep_time = max(0.1, update_interval - elapsed)
            await asyncio.sleep(sleep_time)
                
    except WebSocketDisconnect:
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