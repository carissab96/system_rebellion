from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets import WebSocketManager
import psutil
import asyncio
from datetime import datetime, timezone

# The Meth Snail's Global WebSocket Manager
websocket_manager = WebSocketManager()

# Export the connection manager for dependency injection
connection_manager = websocket_manager

router = APIRouter()

@router.websocket("/system-metrics")
async def system_metrics_socket(websocket: WebSocket):
    """
    Sir Hawkington's Distinguished System Metrics WebSocket
    The Meth Snail monitors your system with quantum precision!
    """
    try:
        await websocket_manager.connect(websocket)
        
        # Initialize metrics collection
        metrics = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": {
                "sent": psutil.net_io_counters().bytes_sent,
                "recv": psutil.net_io_counters().bytes_recv
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send initial metrics
        await websocket_manager.broadcast({
            "type": "system_metrics",
            "data": metrics
        })

        # Start metrics update loop
        while True:
            try:
                # Collect system metrics
                metrics = {
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                    "network_io": {
                        "sent": psutil.net_io_counters().bytes_sent,
                        "recv": psutil.net_io_counters().bytes_recv
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Broadcast metrics
                await websocket_manager.broadcast({
                    "type": "system_metrics",
                    "data": metrics
                })
                
                # Sleep to control update frequency
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except WebSocketDisconnect:
                print("WebSocket disconnected by client")
                break
            except Exception as e:
                print(f"Error in metrics collection: {e}")
                break

    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)