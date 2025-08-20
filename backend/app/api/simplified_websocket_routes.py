from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.websockets import websocket_manager
from app.api.websocket_auth import get_current_user_from_token
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.services.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricCreate
from app.core.database import get_async_db
from app.core.resilience import get_circuit_breaker
from app.core.resilience.backpressure import BackpressureHandler
from app.ai_agents.agent_manager import get_agent_manager
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

@router.websocket("/ws/system-metrics")
async def system_metrics_socket(websocket: WebSocket):
    """
    Sir Hawkington's Simplified System Metrics WebSocket with Database Persistence and AI Integration
    """
    client_id = f"client_{id(websocket)}"
    connection_active = False
    db = None
    user = None
    agent_manager = None
    
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
        
        logger.info(f"WebSocket authenticated for user {user.email} ({client_id})")
        
        # Get async database session
        db_gen = get_async_db()
        db = await db_gen.__anext__()

        # Initialize AI Agent Manager
        try:
            agent_manager = await get_agent_manager()
            active_agents = await agent_manager.get_active_agents()
            logger.info(f" AI Agent manager initialized for user {user.email} - Active agents: { active_agents }")
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent Manager: {str(e)}")
            agent_manager = None
            # Continue without AI agents - don't break the WebSocket
        
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
                
                # 🤖 AI AGENT PROCESSING - Let all agents analyze the metrics
                if agent_manager:
                    try:
                        # Create user context for personalized analysis
                        user_context = {
                            'user_id': str(user.id),
                            'email': user.email,
                            'client_id': client_id
                        }
                        
                        # Process metrics through all AI agents
                        enhanced_metrics = await agent_manager.process_metrics_through_triage_engine(
                            metrics, 
                            user_context
                        )
                        
                        # Log AI agent processing results
                        if 'agent_processing' in enhanced_metrics:
                            successful_agents = enhanced_metrics['agent_processing']['successful_agents']
                            failed_agents = enhanced_metrics['agent_processing']['failed_agents']
                            
                            if successful_agents:
                                agent_names = [agent['agent_name'] for agent in successful_agents]
                                logger.info(f"🤖 AI Agents processed metrics: {', '.join(agent_names)}")
                            
                            if failed_agents:
                                failed_names = [agent['agent_name'] for agent in failed_agents]
                                logger.warning(f"🤖 AI Agents failed: {', '.join(failed_names)}")
                        
                        # Use enhanced metrics for further processing
                        metrics = enhanced_metrics
                        
                    except Exception as ai_error:
                        logger.error(f"AI Agent processing failed (non-critical): {str(ai_error)}")
                        # Continue with original metrics if AI processing fails
                        # This ensures the WebSocket keeps working even if AI fails
                
                # 🔥 DATABASE PERSISTENCE - Save enhanced metrics to database
                if user and db:
                    try:
                        # Create metric record for database
                        metric_create = MetricCreate(
                            user_id=str(user.id),
                            cpu_usage=metrics.get('cpu_usage'),
                            memory_usage=metrics.get('memory_usage'),
                            disk_usage=metrics.get('disk_usage'),
                            network=metrics.get('network'),
                            process_count=metrics.get('process_count'),
                            additional_metrics=metrics,  # Store full metrics as JSON (now includes AI analysis!)
                            timestamp=datetime.now(timezone.utc)
                        )
                        
                        # Save to database using repository - get singleton instance
                        from app.services.metrics_repository import get_metrics_repository
                        metrics_repo = await get_metrics_repository()
                        await metrics_repo.create_metric(
                            db=db,
                            user_id=str(user.id),
                            cpu_usage=metrics.get('cpu_usage', 0.0),
                            memory_usage=metrics.get('memory_usage', 0.0),
                            disk_usage=metrics.get('disk_usage', 0.0),
                            network_data=metrics.get('network', {}),
                            process_count=metrics.get('process_count', 0),
                            additional_metrics=metrics  # Store full metrics including AI analysis
                        )
                        
                        # Enhanced logging to show what we're saving
                        ai_info = " + AI analysis" if 'sir_hawkington' in metrics else ""
                        logger.debug(f"💾 Metrics{ai_info} saved to database for user {user.email}")
                        
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
                            "data": metric_data  # Now includes AI agent analysis!
                        }
                        
                        # Enhanced debug logging to show AI integration
                        ai_agents = []
                        if 'sir_hawkington' in metric_data:
                            decision_type = metric_data['sir_hawkington'].get('decision_type', 'unknown')
                            ai_agents.append(f"🧐 Hawkington({decision_type})")
                        
                        base_keys = list(metric_data.keys()) if isinstance(metric_data, dict) else 'not_dict'
                        ai_info = f" + AI: {', '.join(ai_agents)}" if ai_agents else ""
                        
                        logger.info(f"📤 Sending metrics{ai_info} to {client_id}: keys={base_keys}")
                        import json  # Move import to top to fix variable scoping
                        logger.debug(f"📤 Full metrics data structure: {json.dumps(metric_data, indent=2, default=str)[:500]}...")
                        
                        # Ensure no coroutine objects are in the message before serialization
                        try:
                            # Test serialization to catch coroutine objects early
                            json.dumps(message_to_send, default=str)
                            await websocket.send_json(message_to_send)
                        except TypeError as e:
                            if "coroutine" in str(e).lower():
                                logger.error(f"Coroutine serialization error prevented: {str(e)}")
                                # Send error message instead of crashing
                                error_message = {
                                    "type": "metrics_error",
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "message": "Metrics processing error - coroutine not awaited"
                                }
                                await websocket.send_json(error_message)
                            else:
                                raise
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
            await db.close()