"""
Agent Instrumentation System
Automatic method execution tracking and WebSocket event emission.

NO FAKE DATA - Real method execution events only.
"""

import logging
import asyncio
import functools
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone
from app.api.websockets import get_websocket_manager

logger = logging.getLogger("AgentInstrumentation")


def utc_now():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


class AgentInstrumentationMixin:
    """
    Mixin for agents to automatically emit method execution events.
    
    Usage:
        class MyAgent(AgentInstrumentationMixin, BaseAIAgent):
            ...
    
    This mixin provides:
    - Automatic method execution tracking
    - WebSocket event emission for method start/end/error
    - State change tracking
    - Performance metrics
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instrumentation_enabled = False  # Disabled by default - use personality events instead
        self._current_method_execution = None
        self._method_execution_count = {}
        self._method_error_count = {}
        
    async def _emit_agent_event(self, event_data: Dict[str, Any]):
        """
        Emit an agent event via WebSocket manager.
        
        Args:
            event_data: Event data to broadcast
        """
        if not self._instrumentation_enabled:
            return
            
        try:
            ws_manager = get_websocket_manager()
            
            # Only broadcast if there are active connections
            if len(ws_manager.active_connections) == 0:
                return
            
            # Add agent context
            full_event = {
                "type": "agent_insight",
                "agent_name": self.agent_name,
                "timestamp": utc_now().isoformat(),
                **event_data
            }
            
            # Broadcast to all connected clients (with timeout protection)
            try:
                await asyncio.wait_for(
                    ws_manager.broadcast_json(full_event),
                    timeout=0.5
                )
            except asyncio.TimeoutError:
                logger.warning(f"WebSocket broadcast timed out for {self.agent_name}")
            
        except Exception as e:
            # Don't let instrumentation errors break agent functionality
            logger.debug(f"Failed to emit agent event (non-critical): {e}")
    
    async def _emit_method_start(self, method_name: str, parameters: Optional[Dict[str, Any]] = None):
        """Emit method start event"""
        self._current_method_execution = {
            "method_name": method_name,
            "start_time": time.time(),
            "start_timestamp": utc_now().isoformat()
        }
        
        # Track execution count
        self._method_execution_count[method_name] = self._method_execution_count.get(method_name, 0) + 1
        
        await self._emit_agent_event({
            "event_type": "method_start",
            "method_name": method_name,
            "parameters": parameters or {},
            "execution_count": self._method_execution_count[method_name]
        })
    
    async def _emit_method_end(
        self, 
        method_name: str, 
        result: Optional[Any] = None,
        state_changes: Optional[Dict[str, Any]] = None
    ):
        """Emit method end event"""
        if not self._current_method_execution or self._current_method_execution["method_name"] != method_name:
            return
            
        duration = time.time() - self._current_method_execution["start_time"]
        
        await self._emit_agent_event({
            "event_type": "method_end",
            "method_name": method_name,
            "duration_ms": round(duration * 1000, 2),
            "state_changes": state_changes or {},
            "has_result": result is not None
        })
        
        self._current_method_execution = None
    
    async def _emit_method_error(self, method_name: str, error: Exception):
        """Emit method error event"""
        if self._current_method_execution:
            duration = time.time() - self._current_method_execution["start_time"]
        else:
            duration = 0
            
        # Track error count
        self._method_error_count[method_name] = self._method_error_count.get(method_name, 0) + 1
        
        await self._emit_agent_event({
            "event_type": "method_error",
            "method_name": method_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "duration_ms": round(duration * 1000, 2),
            "error_count": self._method_error_count[method_name]
        })
        
        self._current_method_execution = None
    
    async def _emit_state_change(self, variable_name: str, old_value: Any, new_value: Any):
        """Emit state variable change event"""
        await self._emit_agent_event({
            "event_type": "state_change",
            "variable_name": variable_name,
            "old_value": str(old_value) if old_value is not None else None,
            "new_value": str(new_value) if new_value is not None else None,
            "current_method": self._current_method_execution["method_name"] if self._current_method_execution else None
        })
    
    def enable_instrumentation(self):
        """Enable instrumentation for this agent"""
        self._instrumentation_enabled = True
        logger.info(f"Instrumentation enabled for {self.agent_name}")
    
    def disable_instrumentation(self):
        """Disable instrumentation for this agent"""
        self._instrumentation_enabled = False
        logger.info(f"Instrumentation disabled for {self.agent_name}")


def instrument_method(method: Callable) -> Callable:
    """
    Decorator to automatically instrument agent methods.
    
    Usage:
        @instrument_method
        async def process_metrics(self, metrics, user_context=None):
            ...
    
    This decorator:
    - Emits method_start event before execution
    - Emits method_end event after successful execution
    - Emits method_error event on exception
    - Tracks execution time
    """
    
    @functools.wraps(method)
    async def async_wrapper(self, *args, **kwargs):
        method_name = method.__name__
        
        # Check if agent has instrumentation mixin
        if not hasattr(self, '_emit_method_start'):
            # No instrumentation, just call method
            return await method(self, *args, **kwargs)
        
        # Emit start event
        try:
            # Extract parameter info (first arg is usually metrics/data)
            param_info = {}
            if args:
                param_info["arg_count"] = len(args)
            if kwargs:
                param_info["kwargs"] = list(kwargs.keys())
                
            await self._emit_method_start(method_name, param_info)
        except Exception as e:
            logger.error(f"Failed to emit method start: {e}")
        
        # Execute method
        try:
            result = await method(self, *args, **kwargs)
            
            # Emit end event
            try:
                await self._emit_method_end(method_name, result)
            except Exception as e:
                logger.error(f"Failed to emit method end: {e}")
            
            return result
            
        except Exception as error:
            # Emit error event
            try:
                await self._emit_method_error(method_name, error)
            except Exception as e:
                logger.error(f"Failed to emit method error: {e}")
            
            # Re-raise the original error
            raise
    
    @functools.wraps(method)
    def sync_wrapper(self, *args, **kwargs):
        method_name = method.__name__
        
        # For sync methods, we can't emit events (they're async)
        # Just call the method
        logger.debug(f"Sync method {method_name} called (no instrumentation)")
        return method(self, *args, **kwargs)
    
    # Return appropriate wrapper based on whether method is async
    if asyncio.iscoroutinefunction(method):
        return async_wrapper
    else:
        return sync_wrapper


def track_state_change(variable_name: str):
    """
    Decorator to track state variable changes.
    
    Usage:
        @track_state_change("processing_count")
        def increment_count(self):
            self.processing_count += 1
    """
    def decorator(method: Callable) -> Callable:
        @functools.wraps(method)
        async def async_wrapper(self, *args, **kwargs):
            # Get old value
            old_value = getattr(self, variable_name, None)
            
            # Execute method
            result = await method(self, *args, **kwargs)
            
            # Get new value and emit change
            new_value = getattr(self, variable_name, None)
            if hasattr(self, '_emit_state_change') and old_value != new_value:
                try:
                    await self._emit_state_change(variable_name, old_value, new_value)
                except Exception as e:
                    logger.error(f"Failed to emit state change: {e}")
            
            return result
        
        @functools.wraps(method)
        def sync_wrapper(self, *args, **kwargs):
            # Sync methods can't emit events
            return method(self, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(method):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
