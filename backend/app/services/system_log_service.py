"""
System Log Service

Captures and stores important system events and command outputs
for display in the UI.
"""

import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
from collections import deque

class LogEntry:
    def __init__(self, message: str, level: str, source: str, timestamp: Optional[datetime] = None):
        self.message = message
        self.level = level  # "info", "warning", "error", "success", "command"
        self.source = source  # "auth", "system", "command", "tuner", etc.
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "level": self.level,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }

class LogService:
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('LogService')
        # Use a deque with a max length to prevent memory issues
        self.logs = deque(maxlen=1000)  # Store last 1000 log entries
        self._initialized = True
        
        # Set up a handler to capture logs from other parts of the application
        self._setup_log_capture()
        
        self.logger.info("LogService initialized")
        self.add_log("Log Service initialized", "info", "system")
    
    def _setup_log_capture(self):
        """Set up handlers to capture logs from other loggers"""
        class LogCaptureHandler(logging.Handler):
            def __init__(self, log_service):
                super().__init__()
                self.log_service = log_service
                
            def emit(self, record):
                try:
                    level = record.levelname.lower()
                    if level == 'critical':
                        level = 'error'
                    elif level == 'debug':
                        level = 'info'
                    
                    # Map log level to our system
                    if level not in ["info", "warning", "error", "success", "command"]:
                        level = "info"
                        
                    self.log_service.add_log(
                        message=self.format(record),
                        level=level,
                        source=record.name
                    )
                except Exception:
                    pass
        
        # Create a formatter
        formatter = logging.Formatter('%(message)s')
        
        # Create and add our handler
        handler = LogCaptureHandler(self)
        handler.setFormatter(formatter)
        
        # Add to root logger to capture all logs
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
    
    def add_log(self, message: str, level: str, source: str):
        """Add a new log entry"""
        entry = LogEntry(message, level, source)
        self.logs.append(entry)
        return entry
    
    def add_command_log(self, command: str, output: str, success: bool):
        """Add a command execution log entry"""
        level = "success" if success else "error"
        message = f"Command: {command}\nOutput: {output}"
        return self.add_log(message, level, "command")
    
    def add_auth_log(self, username: str, success: bool, ip_address: Optional[str] = None):
        """Add an authentication log entry"""
        level = "success" if success else "error"
        action = "successful" if success else "failed"
        message = f"Authentication {action} for user: {username}"
        if ip_address:
            message += f" from {ip_address}"
        return self.add_log(message, level, "auth")
    
    def add_tuner_log(self, action: str, parameter: str, old_value: Any, new_value: Any, success: bool):
        """Add a system tuning log entry"""
        level = "success" if success else "error"
        status = "successfully" if success else "failed to"
        message = f"{action} {status} change {parameter} from {old_value} to {new_value}"
        return self.add_log(message, level, "tuner")
    
    def get_logs(self, limit: int = 100, source: Optional[str] = None, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent logs with optional filtering"""
        filtered_logs = list(self.logs)
        
        # Apply filters
        if source:
            filtered_logs = [log for log in filtered_logs if log.source == source]
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        # Return most recent logs first
        return [log.to_dict() for log in reversed(filtered_logs)][:limit]
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
        self.add_log("Logs cleared", "info", "system")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
