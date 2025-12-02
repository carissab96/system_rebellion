"""
WebSocket Log Handler - Broadcast backend logs to frontend
Captures Python logging output and sends to WebSocket clients
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

class WebSocketLogHandler(logging.Handler):
    """
    Custom logging handler that broadcasts log messages to WebSocket clients.
    Uses dedicated agent_logs_websocket endpoint.
    """
    
    def __init__(self, broadcast_func=None):
        super().__init__()
        self.broadcast_func = broadcast_func
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
    def set_broadcast_function(self, broadcast_func):
        """Set the broadcast function after initialization"""
        self.broadcast_func = broadcast_func
        
    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the event loop for async operations"""
        self.loop = loop
    
    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to WebSocket clients.
        Called automatically by Python's logging system.
        """
        if not self.broadcast_func:
            return
            
        try:
            # Format the log message
            log_entry = self.format(record)
            
            # Extract agent name from logger name
            # Logger names are like "TheStick.Distributed", "VIC20.Coordination", etc.
            agent_name = self._extract_agent_name(record.name)
            
            # Categorize the log
            category = self._categorize_log(record, log_entry)
            
            # Create WebSocket message
            message = {
                'type': 'agent_log',
                'agent_name': agent_name,
                'level': record.levelname.lower(),
                'category': category,
                'message': log_entry,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Broadcast to all WebSocket clients
            if self.loop and self.loop.is_running():
                print(f"🔊 Broadcasting log: {message['agent_name']} - {message['category']} - {message['message'][:50]}")
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_func(message),
                    self.loop
                )
            else:
                print(f"⚠️ Cannot broadcast - loop not running or not set")
            
        except Exception as e:
            # Don't let logging errors break the application
            self.handleError(record)
    
    def _extract_agent_name(self, logger_name: str) -> str:
        """Extract agent name from logger name"""
        # Map logger names to agent names
        logger_lower = logger_name.lower()
        
        if 'hawkington' in logger_lower or 'hawk' in logger_lower:
            return 'sir_hawkington'
        elif 'vic' in logger_lower or 'vic20' in logger_lower:
            return 'vic_20_sage'
        elif 'meth' in logger_lower or 'snail' in logger_lower or 'terry' in logger_lower:
            return 'meth_snail'
        elif 'stick' in logger_lower:
            return 'the_stick'
        elif 'hamster' in logger_lower:
            return 'hamsters'
        elif 'quantum' in logger_lower or 'qsp' in logger_lower or 'shadow' in logger_lower:
            return 'quantum_shadow_people'
        else:
            return 'system'
    
    def _categorize_log(self, record: logging.LogRecord, message: str) -> str:
        """Categorize the log message"""
        message_lower = message.lower()
        
        # Check for database/PostgreSQL operations
        if any(keyword in message_lower for keyword in ['postgres', 'database', 'db', 'wrote', 'commit', 'query', 'sql']):
            return 'postgres'
        
        # Check for Redis/pub-sub operations
        if any(keyword in message_lower for keyword in ['redis', 'pub', 'sub', 'broadcast', 'message', 'channel']):
            return 'redis'
        
        # Check for vector operations
        if any(keyword in message_lower for keyword in ['vector', 'embedding', 'semantic', 'similarity']):
            return 'vector'
        
        # Default to system
        return 'system'


def setup_websocket_logging(broadcast_func, event_loop: asyncio.AbstractEventLoop, level=logging.INFO):
    """
    Set up WebSocket logging for all agent loggers.
    
    Args:
        broadcast_func: Async function to broadcast messages
        event_loop: Asyncio event loop
        level: Minimum log level to broadcast (default: INFO)
    """
    # Create the WebSocket log handler
    ws_handler = WebSocketLogHandler(broadcast_func)
    ws_handler.set_event_loop(event_loop)
    ws_handler.setLevel(level)
    
    # Use a simple formatter
    formatter = logging.Formatter('%(message)s')
    ws_handler.setFormatter(formatter)
    
    # Add handler to agent loggers
    agent_loggers = [
        'TheStick.Distributed',
        'Stick.Database',
        'VIC20.Coordination',
        'VIC20.Database',
        'MethSnail.Distributed',
        'MethSnail.Database',
        'Hawkington.Triage',
        'Hawkington.Distributed',
        'Hamsters.Distributed',
        'QSP.Distributed',
    ]
    
    for logger_name in agent_loggers:
        logger = logging.getLogger(logger_name)
        logger.addHandler(ws_handler)
    
    return ws_handler
