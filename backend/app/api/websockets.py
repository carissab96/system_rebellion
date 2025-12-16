import asyncio
import logging
import json
from typing import Set, List, Dict, Any, Optional
from collections import deque
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()
        self._heartbeat_task: asyncio.Task | None = None
        self._redis_subscription_task: asyncio.Task | None = None
        self._started = False
        self._redis_client: Optional[Any] = None
        
        # Buffers for insights and events (last 20 of each)
        self.recent_insights: deque = deque(maxlen=20)
        self.recent_events: deque = deque(maxlen=20)
        
        # Buffers for distributed agent messages
        self.recent_agent_messages: deque = deque(maxlen=50)
        self.recent_triage_decisions: deque = deque(maxlen=20)
        self.recent_resource_alerts: deque = deque(maxlen=20)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("🔌 WebSocket connected. Active: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("🔌 WebSocket disconnected. Active: %d", len(self.active_connections))

    async def broadcast_json(self, message: dict) -> None:
        """Broadcast a message to all connected clients and buffer if needed."""
        # Buffer insights and events for inclusion in system updates
        msg_type = message.get("type")
        if msg_type == "agent_insight":
            self.recent_insights.append(message)
            logger.debug("📝 Buffered insight: %s → %s", message.get("from_agent"), message.get("to_agent"))
        elif msg_type == "agent_event":
            self.recent_events.append(message)
            logger.debug("📝 Buffered event: %s - %s", message.get("agent_name"), message.get("event_type"))
        elif msg_type == "agent_log":
            # Buffer agent logs as insights so they appear in activity feed
            self.recent_insights.append(message)
            logger.debug("📝 Buffered log: %s - %s", message.get("agent_name"), message.get("message", "")[:50])
        
        # Broadcast to all connections
        to_drop = []
        for ws in list(self.active_connections):
            try:
                await ws.send_json(message)
            except Exception:
                to_drop.append(ws)
        for ws in to_drop:
            self.disconnect(ws)
    
    def get_recent_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent insights from buffer."""
        return list(self.recent_insights)[-limit:]
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events from buffer."""
        return list(self.recent_events)[-limit:]

    async def _heartbeat_loop(self) -> None:
        # lightweight keepalive + observability
        while True:
            try:
                await asyncio.sleep(30)
                await self.broadcast_json({"type": "heartbeat", "active": len(self.active_connections)})
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning("WS heartbeat error: %s", e, exc_info=True)

    async def _subscribe_to_agent_messages(self) -> None:
        """
        Subscribe to Redis channels and forward messages to WebSocket clients.
        
        Week 5 Task 5.1: Redis → WebSocket Bridge
        """
        if not self._redis_client:
            logger.warning("⚠️ Redis client not set - agent messages will not be forwarded")
            return
        
        try:
            # Create Redis pubsub
            pubsub = self._redis_client.pubsub()
            
            # Subscribe to agent broadcast channels (distributed agent protocol)
            await pubsub.subscribe(
                'agents:broadcast',  # All agent messages (distributed protocol)
                'agents:decisions',  # Decision coordination
                'agents:resources:alerts',  # Resource monitoring alerts
                'agents:emergency',  # Emergency broadcasts
                'agents:heartbeats',  # Agent heartbeats
                'agents:learning',  # Shared learning and patterns
                # Legacy channels for backward compatibility
                'agent:broadcast',  # Old protocol
                'triage:decisions',  # Triage decisions from Sir Hawkington
                'resource:alerts',  # Resource alerts
                'coordination:requests',  # VIC-20 coordination
                'agent:actions'  # Agent actions (overrides, etc.)
            )
            
            logger.info("📡 Subscribed to Redis agent channels - forwarding to WebSocket clients")
            
            # Listen for messages
            while True:
                try:
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    
                    if message and message['type'] == 'message':
                        channel = message['channel'].decode('utf-8') if isinstance(message['channel'], bytes) else message['channel']
                        data = message['data']
                        
                        # Parse message data
                        try:
                            if isinstance(data, bytes):
                                data = data.decode('utf-8')
                            
                            message_data = json.loads(data) if isinstance(data, str) else data
                            
                            # Add channel info
                            message_data['redis_channel'] = channel
                            
                            # Route to appropriate buffer and broadcast
                            # Distributed agent protocol channels
                            if channel in ['agents:decisions', 'triage:decisions']:
                                self.recent_triage_decisions.append(message_data)
                                await self.broadcast_json({
                                    'type': 'triage_decision',
                                    'data': message_data
                                })
                                logger.debug("🎯 Forwarded triage decision to WebSocket clients")
                            
                            elif channel in ['agents:resources:alerts', 'resource:alerts']:
                                self.recent_resource_alerts.append(message_data)
                                await self.broadcast_json({
                                    'type': 'resource_alert',
                                    'data': message_data
                                })
                                logger.debug("⚠️ Forwarded resource alert to WebSocket clients")
                            
                            elif channel == 'agents:emergency':
                                await self.broadcast_json({
                                    'type': 'emergency',
                                    'data': message_data
                                })
                                logger.warning("🚨 Forwarded EMERGENCY to WebSocket clients")
                            
                            elif channel == 'agents:heartbeats':
                                await self.broadcast_json({
                                    'type': 'agent_heartbeat',
                                    'data': message_data
                                })
                                logger.debug("💓 Forwarded agent heartbeat to WebSocket clients")
                            
                            elif channel == 'agents:learning':
                                await self.broadcast_json({
                                    'type': 'learning_update',
                                    'data': message_data
                                })
                                logger.debug("🧠 Forwarded learning update to WebSocket clients")
                            
                            elif channel == 'coordination:requests':
                                await self.broadcast_json({
                                    'type': 'coordination_request',
                                    'data': message_data
                                })
                                logger.debug("🤝 Forwarded coordination request to WebSocket clients")
                            
                            elif channel == 'agent:actions':
                                await self.broadcast_json({
                                    'type': 'agent_action',
                                    'data': message_data
                                })
                                logger.debug("⚡ Forwarded agent action to WebSocket clients")
                            
                            else:  # agents:broadcast or agent:broadcast
                                self.recent_agent_messages.append(message_data)
                                await self.broadcast_json({
                                    'type': 'agent_message',
                                    'data': message_data
                                })
                                logger.debug("📨 Forwarded agent message to WebSocket clients")
                        
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ Failed to parse Redis message: {e}")
                        except Exception as e:
                            logger.error(f"❌ Error processing Redis message: {e}", exc_info=True)
                    
                    # Small delay to prevent tight loop
                    await asyncio.sleep(0.01)
                
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"❌ Error in Redis subscription loop: {e}", exc_info=True)
                    await asyncio.sleep(1)  # Back off on error
        
        except asyncio.CancelledError:
            logger.info("🛑 Redis subscription cancelled")
            raise
        except Exception as e:
            logger.error(f"❌ Fatal error in Redis subscription: {e}", exc_info=True)
        finally:
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except Exception:
                pass
    
    def set_redis_client(self, redis_client: Any) -> None:
        """
        Set the Redis client for subscribing to agent messages.
        
        Args:
            redis_client: Connected Redis client
        """
        self._redis_client = redis_client
        logger.info("✅ Redis client set for WebSocket bridge")
    
    async def start(self) -> None:
        if self._started:
            return
        logger.info("✅ WebSocketManager starting…")
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(), name="ws-heartbeat")
        
        # Start Redis subscription if client is set
        if self._redis_client:
            self._redis_subscription_task = asyncio.create_task(
                self._subscribe_to_agent_messages(),
                name="redis-ws-bridge"
            )
            logger.info("🌉 Redis → WebSocket bridge started")
        else:
            logger.warning("⚠️ Redis client not set - agent messages will not be forwarded")
        
        self._started = True

    async def shutdown(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self._redis_subscription_task:
            self._redis_subscription_task.cancel()
            try:
                await self._redis_subscription_task
            except asyncio.CancelledError:
                pass
        
        self._started = False
        logger.info("🛑 WebSocketManager stopped")

_ws_manager: WebSocketManager | None = None

def get_websocket_manager() -> WebSocketManager:
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
