from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
# from app.websockets import WebSocketManager
from app.api.websocket_auth import authenticate_websocket
from app.services.metrics.metrics_service import MetricsService
from app.services.system_metrics_service import SystemMetricsService
from app.core.resilience import (
    WebSocketCircuitBreaker, 
    get_circuit_breaker,
    BackpressureHandler,
    get_backpressure_handler,
    RecoveryAction,
    RecoveryStrategy,
    ErrorSeverity,
    with_error_recovery,
    error_recovery,
    get_metric_transformer
)
import psutil
import asyncio
import socket
import os
import json
import platform
import logging
import time
import numpy as np
from datetime import datetime, timezone
from typing import List, Any, Optional, Tuple, Union, Dict
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# WebSocket Manager
websocket_manager = WebSocketManager()
connection_manager = websocket_manager

# Initialize resilience components
metrics_circuit_breaker = get_circuit_breaker(
    name="metrics_websocket", 
    max_failures=3,
    reset_timeout=30,
    exponential_backoff_factor=1.5
)

metrics_backpressure = get_backpressure_handler(
    name="metrics_backpressure",
    max_buffer_size=100,
    sampling_strategy="latest"
)

# Initialize metric transformer
metric_transformer = get_metric_transformer(
    name="system_metrics",
    history_size=120,  # 2 minutes of history at 1s intervals
    smoothing_window=5
)

# Register recovery strategies
error_recovery.register_strategy(
    component="websocket",
    error_type="WebSocketDisconnect",
    recovery_action=RecoveryAction(
        strategy=RecoveryStrategy.RETRY,
        max_retries=3,
        retry_delay=2.0,
        exponential_backoff=True
    )
)

error_recovery.register_strategy(
    component="websocket",
    error_type="ConnectionError",
    recovery_action=RecoveryAction(
        strategy=RecoveryStrategy.RETRY,
        max_retries=5,
        retry_delay=1.0,
        exponential_backoff=True
    )
)

# For metrics errors - return ERROR state, not fake data
error_recovery.register_strategy(
    component="metrics",
    error_type="*",  # Any error in metrics collection
    recovery_action=RecoveryAction(
        strategy=RecoveryStrategy.FALLBACK,
        fallback_function=lambda ctx, *args, **kwargs: {
            "error": True,
            "error_type": "metrics_collection_failed",
            "message": f"Failed to collect metrics: {ctx.get('error', 'Unknown error')}",
            "timestamp": datetime.now().isoformat(),
            "retry_available": True
        }
    )
)
def transform_metrics_for_frontend(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform backend metrics to match EXACTLY what components expect
    Based on component field analysis
    """
    
    transformed = {}
    
    # Transform CPU metrics - Component expects these exact fields
    if "cpu" in metrics:
        cpu_data = metrics["cpu"]
        
        # Map to the fields CPUMetric.tsx expects
        transformed.update({
            "cpu_usage": cpu_data.get("current", cpu_data.get("usage_percent", cpu_data.get("total_percent", 0.0))),
            "cpu_temperature": cpu_data.get("temperature", 0),
            "cpu_frequency": cpu_data.get("frequency_mhz", cpu_data.get("frequency", {}).get("current", 0)),
            "cpu_core_count": cpu_data.get("physical_cores", cpu_data.get("core_count", psutil.cpu_count(logical=False))),
            "cpu_thread_count": cpu_data.get("logical_cores", cpu_data.get("thread_count", psutil.cpu_count(logical=True))),
            "cpu_model": cpu_data.get("model_name", cpu_data.get("processor", "System CPU")),
            "cpu_percent": cpu_data.get("current", cpu_data.get("usage_percent", 0.0)),
            "frequency_mhz": cpu_data.get("frequency_mhz", 0),
            "overall_usage": cpu_data.get("current", cpu_data.get("usage_percent", 0.0)),
            "process_count": len(cpu_data.get("top_processes", [])),
            "model_name": cpu_data.get("model_name", "System CPU"),
            
            # The nested 'cpu' object with cores and processes
            "cpu": {
                "cores": cpu_data.get("cores", []),
                "top_processes": cpu_data.get("top_processes", [])
            }
        })
    
    # Transform Memory metrics - Component expects these exact fields
    if "memory" in metrics:
        mem_data = metrics["memory"]
        
        transformed.update({
            "memory_percent": mem_data.get("current", mem_data.get("usage_percent", mem_data.get("percent", 0.0))),
            "memory_total": mem_data.get("total", 0),
            "memory_available": mem_data.get("available", 0),
            "memory_buffer": mem_data.get("buffers", 0),
            "memory_cache": mem_data.get("cached", 0),
            "memory_swap_free": mem_data.get("swap", {}).get("free", 0),
            "memory_swap_percent": mem_data.get("swap", {}).get("percent", 0),
            "memory_swap_total": mem_data.get("swap", {}).get("total", 0),
            "memory_swap_used": mem_data.get("swap", {}).get("used", 0)
        })
    
    # Transform Disk metrics - Component expects directories
    if "disk" in metrics:
        disk_data = metrics["disk"]
        
        transformed.update({
            "directories": disk_data.get("directories", []),
            # Add other disk fields the component might need
            "disk_usage": disk_data.get("current", disk_data.get("usage_percent", 0.0)),
            "disk_total": disk_data.get("total", 0),
            "disk_used": disk_data.get("used", 0),
            "disk_free": disk_data.get("free", 0)
        })
    
    # Transform Network metrics - Component expects quality metrics
    if "network" in metrics:
        net_data = metrics["network"]
        
        # Extract quality data if available
        quality = net_data.get("quality", {})
        
        transformed.update({
            "average_latency": quality.get("latency_ms", quality.get("average_latency", 0)),
            "connection_stability": quality.get("stability", 100),
            "dns_latency": quality.get("dns_latency", 0),
            "gateway_latency": quality.get("gateway_latency", 0),
            "internet_latency": quality.get("internet_latency", 0),
            "jitter": quality.get("jitter_ms", quality.get("jitter", 0)),
            "packet_loss_percent": quality.get("packet_loss_percent", 0),
            "protocol_breakdown": net_data.get("protocol_breakdown", {}),
            "protocol_stats": net_data.get("protocol_stats", {}),
            "top_bandwidth_processes": net_data.get("top_processes", []),
            
            # Also include the raw network data
            "network": net_data
        })
    
    return transformed

router = APIRouter()

@router.websocket("/ws/system-metrics")
@with_error_recovery(component="websocket", operation="system_metrics_socket", severity=ErrorSeverity.HIGH)
async def system_metrics_socket(websocket: WebSocket):
    """
    Sir Hawkington's Distinguished System Metrics WebSocket
    
    Now with POST-CONNECTION authentication for maximum elegance!
    """
    connection_active = False
    client_id = f"client_{id(websocket)}"
    authenticated = False
    user = None
    db: Session = None
    
    try:
        # Check if the circuit breaker allows this connection
        if not metrics_circuit_breaker.can_attempt_connection():
            wait_time = metrics_circuit_breaker.get_wait_time()
            logger.warning(f"🛑 Circuit breaker is open, rejecting connection for {wait_time:.2f}s")
            # Accept first to be able to send the error message
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "message": f"System is experiencing high load. Please try again in {int(wait_time)} seconds.",
                "code": "circuit_open"
            })
            await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
            return
            
        logger.info(f"🔌 WebSocket connection attempt to /ws/system-metrics from {client_id}")
        
        # STEP 1: Accept the connection WITHOUT authentication
        await websocket.accept()
        logger.info(f"🔌 WebSocket connection accepted for {client_id}, awaiting authentication...")
        
        # STEP 2: Wait for authentication message (with timeout)
        try:
            auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
            logger.info(f"📨 Received message from {client_id}: {auth_message.get('type', 'unknown')}")
            
            if auth_message.get("type") != "auth":
                logger.error(f"❌ Expected auth message, got: {auth_message.get('type', 'unknown')}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Expected authentication message",
                    "code": "auth_required"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Extract and validate token
            token = auth_message.get("token", "")
            if not token:
                logger.error(f"❌ No token provided in auth message from {client_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": "No authentication token provided",
                    "code": "no_token"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Remove Bearer prefix if present
            token = token.replace("Bearer ", "").strip()
            
            try:
                # Validate JWT token
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )
                username: str = payload.get("sub")
                if username is None:
                    raise JWTError("No username in token")
                
                # Get database session and fetch user
                db = next(get_db())
                user = User.get_current_user(db, username)
                
                if user is None:
                    logger.error(f"❌ User not found: {username}")
                    await websocket.send_json({
                        "type": "auth_failed",
                        "message": "User not found",
                        "code": "user_not_found"
                    })
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                
                authenticated = True
                logger.info(f"✅ WebSocket authenticated for user {user.username} ({client_id})")
                
                # Send authentication success
                await websocket.send_json({
                    "type": "auth_success",
                    "message": f"Welcome, {user.username}!",
                    "user": user.username,
                    "system_info": await get_system_info()
                })
                
            except JWTError as e:
                logger.error(f"❌ JWT validation error for {client_id}: {str(e)}")
                await websocket.send_json({
                    "type": "auth_failed",
                    "message": "Invalid or expired token",
                    "code": "invalid_token"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                metrics_circuit_breaker.record_failure()
                return
                
        except asyncio.TimeoutError:
            logger.error(f"❌ Authentication timeout for {client_id}")
            await websocket.send_json({
                "type": "error",
                "message": "Authentication timeout - no auth message received",
                "code": "auth_timeout"
            })
            await websocket.close(code=status.WS_1002_PROTOCOL_ERROR)
            return
        
        # STEP 3: Authentication successful, start metrics streaming
        if authenticated:
            # Connect to the WebSocket manager
            await websocket_manager.connect(websocket)
            connection_active = True
            metrics_circuit_breaker.record_success()
            
            # Initialize rate limiter
            rate_limiter = RateLimiter(
                calls=100,  # 100 requests
                period=60   # per minute
            )
            
            # Initialize last metrics time
            update_interval = 1.0  # 1 second default update interval
            
            # Main WebSocket loop
            while True:
                try:
                    loop_start_time = time.time()
                    
                    # Check rate limit
                    if not rate_limiter.allow_request():
                        retry_after = rate_limiter.time_until_next_request()
                        await websocket.send_json({
                            "type": "rate_limit",
                            "retry_after": retry_after,
                            "message": f"Rate limit exceeded. Try again in {retry_after} seconds"
                        })
                        await asyncio.sleep(1)
                        continue
                    
                    # Get metrics from the metrics service with circuit breaker protection
                    try:
                        logger.info(f"📡 Fetching metrics from metrics service for client {client_id}")
                        metrics_service = MetricsService()
                        
                        # Execute the metrics retrieval with circuit breaker
                        system_metrics = await metrics_circuit_breaker.execute(
                            metrics_service.get_metrics
                        )
                        
                        # Transform metrics using our NumPy-powered transformer
                        logger.info(f"🔄 Transforming metrics for client {client_id}")
                        transformed_metrics = metric_transformer.transform_system_metrics(system_metrics)
                        
                        # Add to backpressure handler
                        metrics_backpressure.add_item({
                            "metrics": transformed_metrics,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    except Exception as metrics_error:
                        logger.error(f"❌ Error getting metrics: {str(metrics_error)}", exc_info=True)
                        
                        # Send error message to frontend instead of fake data
                        error_message = {
                            "type": "metrics_error",
                            "timestamp": datetime.now().isoformat(),
                            "error": {
                                "message": "Failed to collect system metrics",
                                "details": str(metrics_error),
                                "code": "METRICS_COLLECTION_FAILED"
                            }
                        }
    
                        try:
                            await websocket.send_json(error_message)
                            logger.info(f"Sent error notification to client {client_id}")
                        except Exception as send_error:
                            logger.error(f"Failed to send error message: {send_error}")
    
                        # Continue to next iteration instead of using fake data
                        await asyncio.sleep(update_interval)
                        continue                  
                    # Send metrics update
                    try:
                        await websocket.send_json(message)
                        logger.debug(f"✅ Successfully sent metrics update to client {client_id}")
                    except Exception as send_error:
                        logger.error(f"❌ Failed to send metrics to client {client_id}: {str(send_error)}")
                        raise
                    
                    # Check for client messages with a short timeout
                    try:
                        client_msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                        
                        # Process client message
                        try:
                            msg_data = json.loads(client_msg)
                            msg_type = msg_data.get("type", "")
                            
                            if msg_type == "ping":
                                await websocket.send_json({
                                    "type": "pong", 
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                })
                            elif msg_type == "set_interval":
                                # Client requesting to change the update interval (1-10 seconds)
                                new_interval = max(1.0, min(10.0, float(msg_data.get("interval", 1.0))))
                                update_interval = new_interval
                                logger.info(f"Client {client_id} set update interval to {update_interval}s")
                                
                                await websocket.send_json({
                                    "type": "interval_update", 
                                    "interval": update_interval,
                                    "message": f"Update interval set to {update_interval} seconds"
                                })
                            elif msg_type == "request_system_info":
                                # Send system info on demand
                                system_info = await get_system_info()
                                await websocket.send_json({
                                    "type": "system_info",
                                    "data": system_info
                                })
                        except json.JSONDecodeError:
                            logger.warning(f"Received non-JSON message from client {client_id}")
                    except asyncio.TimeoutError:
                        # No message received, continue with the loop
                        pass
                    
                    # Calculate how long to sleep to maintain the desired update interval
                    elapsed = time.time() - loop_start_time
                    sleep_time = max(0.1, update_interval - elapsed)
                    await asyncio.sleep(sleep_time)
                    
                except WebSocketDisconnect:
                    logger.info(f"WebSocket for {client_id} disconnected by client")
                    break
                    
                except Exception as e:
                    logger.error(f"⚠️ Unhandled WebSocket error: {str(e)}")
                    try:
                        if websocket.client_state.name == "CONNECTED":
                            await websocket.send_json({
                                "type": "error",
                                "message": f"The Meth Snail encountered an error: {str(e)}",
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            })
                    except:
                        pass
                    break
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket for {client_id} disconnected during setup")
        metrics_circuit_breaker.record_failure()
    except Exception as e:
        logger.error(f"WebSocket error during setup for {client_id}: {str(e)}", exc_info=True)
        metrics_circuit_breaker.record_failure()
        # Try to send error message if possible
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
        # Clean up connection if it was established
        if connection_active:
            await websocket_manager.disconnect(websocket)
            logger.info(f"WebSocket disconnected and cleaned for {client_id}")
        
        # Close database session if it was opened
        if db:
            db.close()
            logger.debug(f"Database session closed for {client_id}")