import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple, Union, Type
from enum import Enum
import traceback
import functools
import inspect
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    RESET = "reset"
    NOTIFY = "notify"
    LOG_ONLY = "log_only"


class ErrorContext:
    """Context information about an error"""
    
    def __init__(
        self,
        error: Exception,
        component: str,
        operation: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.error = error
        self.error_type = type(error).__name__
        self.error_message = str(error)
        self.component = component
        self.operation = operation
        self.severity = severity
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        self.traceback = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization"""
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "component": self.component,
            "operation": self.operation,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class RecoveryAction:
    """A recovery action to be taken in response to an error"""
    
    def __init__(
        self,
        strategy: RecoveryStrategy,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        exponential_backoff: bool = True,
        fallback_function: Optional[Callable] = None,
        reset_function: Optional[Callable] = None,
        notify_channels: Optional[List[str]] = None,
    ):
        self.strategy = strategy
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        self.fallback_function = fallback_function
        self.reset_function = reset_function
        self.notify_channels = notify_channels or ["log"]
        
    async def execute(
        self, 
        context: ErrorContext, 
        original_function: Callable, 
        *args, **kwargs
    ) -> Any:
        """Execute the recovery action"""
        if self.strategy == RecoveryStrategy.RETRY:
            return await self._execute_retry(context, original_function, *args, **kwargs)
        elif self.strategy == RecoveryStrategy.FALLBACK:
            return await self._execute_fallback(context, *args, **kwargs)
        elif self.strategy == RecoveryStrategy.RESET:
            return await self._execute_reset(context)
        elif self.strategy == RecoveryStrategy.NOTIFY:
            return await self._execute_notify(context)
        elif self.strategy == RecoveryStrategy.LOG_ONLY:
            return await self._execute_log_only(context)
        else:
            logger.warning(f"Unknown recovery strategy: {self.strategy}")
            return None
    
    async def _execute_retry(
        self, 
        context: ErrorContext, 
        original_function: Callable, 
        *args, **kwargs
    ) -> Any:
        """Execute retry strategy"""
        logger.info(f"Attempting retry for {context.component}.{context.operation}")
        
        for attempt in range(self.max_retries):
            try:
                # Calculate delay with exponential backoff if enabled
                if attempt > 0:
                    delay = self.retry_delay
                    if self.exponential_backoff:
                        delay = self.retry_delay * (2 ** (attempt - 1))
                    
                    logger.info(f"Retry attempt {attempt+1}/{self.max_retries} after {delay:.2f}s delay")
                    await asyncio.sleep(delay)
                
                # Check if the function is a coroutine
                if inspect.iscoroutinefunction(original_function):
                    result = await original_function(*args, **kwargs)
                else:
                    result = original_function(*args, **kwargs)
                
                logger.info(f"Retry successful for {context.component}.{context.operation}")
                return result
                
            except Exception as e:
                logger.warning(
                    f"Retry attempt {attempt+1}/{self.max_retries} failed for "
                    f"{context.component}.{context.operation}: {str(e)}"
                )
                # Continue to next retry attempt
        
        logger.error(
            f"All {self.max_retries} retry attempts failed for {context.component}.{context.operation}"
        )
        # If all retries fail, re-raise the original exception
        raise context.error
    
    async def _execute_fallback(self, context: ErrorContext, *args, **kwargs) -> Any:
        """Execute fallback strategy"""
        if not self.fallback_function:
            logger.error(f"No fallback function provided for {context.component}.{context.operation}")
            return None
            
        logger.info(f"Executing fallback for {context.component}.{context.operation}")
        try:
            # Check if the fallback is a coroutine
            if inspect.iscoroutinefunction(self.fallback_function):
                result = await self.fallback_function(context, *args, **kwargs)
            else:
                result = self.fallback_function(context, *args, **kwargs)
                
            logger.info(f"Fallback successful for {context.component}.{context.operation}")
            return result
            
        except Exception as e:
            logger.error(
                f"Fallback failed for {context.component}.{context.operation}: {str(e)}"
            )
            # If fallback fails, re-raise the original exception
            raise context.error
    
    async def _execute_reset(self, context: ErrorContext) -> None:
        """Execute reset strategy"""
        if not self.reset_function:
            logger.error(f"No reset function provided for {context.component}.{context.operation}")
            return None
            
        logger.info(f"Executing reset for {context.component}.{context.operation}")
        try:
            # Check if the reset function is a coroutine
            if inspect.iscoroutinefunction(self.reset_function):
                await self.reset_function(context)
            else:
                self.reset_function(context)
                
            logger.info(f"Reset successful for {context.component}.{context.operation}")
            
        except Exception as e:
            logger.error(
                f"Reset failed for {context.component}.{context.operation}: {str(e)}"
            )
    
    async def _execute_notify(self, context: ErrorContext) -> None:
        """Execute notification strategy"""
        logger.info(f"Sending notifications for {context.component}.{context.operation}")
        
        error_info = context.to_dict()
        
        for channel in self.notify_channels:
            if channel == "log":
                log_level = logging.ERROR if context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else logging.WARNING
                logger.log(log_level, f"Error notification: {error_info}")
            else:
                # Here you would implement other notification channels
                # like email, Slack, etc.
                logger.info(f"Would send notification to channel '{channel}' (not implemented)")
    
    async def _execute_log_only(self, context: ErrorContext) -> None:
        """Just log the error without taking action"""
        log_level = logging.ERROR if context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else logging.WARNING
        logger.log(log_level, f"Error logged (no recovery): {context.to_dict()}")


class AutonomousErrorRecovery:
    """
    The Quantum Shadow People's Error Recovery System
    
    Provides automatic error recovery strategies for different types of errors.
    """
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.max_history_size = 100
        self.recovery_strategies: Dict[str, Dict[str, RecoveryAction]] = {}
    
    def register_strategy(
        self,
        component: str,
        error_type: Union[Type[Exception], str],
        recovery_action: RecoveryAction
    ) -> None:
        """
        Register a recovery strategy for a specific component and error type
        
        Args:
            component: The component name (e.g., "websocket", "metrics")
            error_type: The exception type or name to handle
            recovery_action: The recovery action to take
        """
        error_type_name = error_type if isinstance(error_type, str) else error_type.__name__
        
        if component not in self.recovery_strategies:
            self.recovery_strategies[component] = {}
            
        self.recovery_strategies[component][error_type_name] = recovery_action
        logger.info(f"Registered {recovery_action.strategy.value} strategy for {component}.{error_type_name}")
    
    def _get_recovery_action(
        self, 
        component: str, 
        error_type: str
    ) -> Optional[RecoveryAction]:
        """Get the appropriate recovery action for a component and error type"""
        # First try exact component and error type match
        if component in self.recovery_strategies and error_type in self.recovery_strategies[component]:
            return self.recovery_strategies[component][error_type]
            
        # Try wildcard error type for this component
        if component in self.recovery_strategies and "*" in self.recovery_strategies[component]:
            return self.recovery_strategies[component]["*"]
            
        # Try wildcard component with this error type
        if "*" in self.recovery_strategies and error_type in self.recovery_strategies["*"]:
            return self.recovery_strategies["*"][error_type]
            
        # Try complete wildcard
        if "*" in self.recovery_strategies and "*" in self.recovery_strategies["*"]:
            return self.recovery_strategies["*"]["*"]
            
        return None
    
    async def handle_error(
        self,
        error: Exception,
        component: str,
        operation: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        original_function: Optional[Callable] = None,
        *args, **kwargs
    ) -> Any:
        """
        Handle an error with the appropriate recovery strategy
        
        Args:
            error: The exception that occurred
            component: The component where the error occurred
            operation: The operation that failed
            severity: The severity of the error
            metadata: Additional context about the error
            original_function: The function that failed (for retry)
            *args, **kwargs: Arguments to pass to recovery functions
            
        Returns:
            The result of the recovery action, if any
        """
        # Create error context
        context = ErrorContext(
            error=error,
            component=component,
            operation=operation,
            severity=severity,
            metadata=metadata
        )
        
        # Add to history, maintaining max size
        self.error_history.append(context)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
        
        # Get the appropriate recovery action
        recovery_action = self._get_recovery_action(component, type(error).__name__)
        
        if recovery_action:
            logger.info(
                f"Applying {recovery_action.strategy.value} recovery for "
                f"{component}.{operation} ({type(error).__name__})"
            )
            
            if original_function or recovery_action.strategy != RecoveryStrategy.RETRY:
                return await recovery_action.execute(
                    context, 
                    original_function,
                    *args, **kwargs
                )
            else:
                logger.error(
                    f"Retry strategy selected but no original function provided for "
                    f"{component}.{operation}"
                )
        else:
            logger.warning(
                f"No recovery strategy found for {component}.{type(error).__name__}, "
                f"logging only"
            )
            
            # Default to logging only
            log_action = RecoveryAction(strategy=RecoveryStrategy.LOG_ONLY)
            await log_action._execute_log_only(context)
        
        # If we get here, recovery failed or wasn't attempted
        return None
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get statistics about errors and recovery attempts"""
        if not self.error_history:
            return {"total_errors": 0}
            
        stats = {
            "total_errors": len(self.error_history),
            "errors_by_component": {},
            "errors_by_type": {},
            "errors_by_severity": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "recent_errors": [e.to_dict() for e in self.error_history[-5:]]
        }
        
        # Count errors by various dimensions
        for error in self.error_history:
            # By component
            if error.component not in stats["errors_by_component"]:
                stats["errors_by_component"][error.component] = 0
            stats["errors_by_component"][error.component] += 1
            
            # By type
            if error.error_type not in stats["errors_by_type"]:
                stats["errors_by_type"][error.error_type] = 0
            stats["errors_by_type"][error.error_type] += 1
            
            # By severity
            stats["errors_by_severity"][error.severity.value] += 1
        
        return stats


# Create a global instance for easy access
error_recovery = AutonomousErrorRecovery()

# Decorator for automatic error recovery
def with_error_recovery(
    component: str,
    operation: Optional[str] = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    recovery_strategy: Optional[RecoveryAction] = None
):
    """
    Decorator to apply automatic error recovery to a function
    
    Args:
        component: The component name
        operation: The operation name (defaults to function name)
        severity: The error severity
        recovery_strategy: Custom recovery strategy (overrides registered strategies)
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal operation
            if operation is None:
                operation = func.__name__
                
            try:
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                # Get metadata about the function call
                metadata = {
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "function": func.__name__
                }
                
                if recovery_strategy:
                    # Use the provided strategy
                    context = ErrorContext(
                        error=e,
                        component=component,
                        operation=operation,
                        severity=severity,
                        metadata=metadata
                    )
                    return await recovery_strategy.execute(context, func, *args, **kwargs)
                else:
                    # Use the global error recovery system
                    return await error_recovery.handle_error(
                        error=e,
                        component=component,
                        operation=operation,
                        severity=severity,
                        metadata=metadata,
                        original_function=func,
                        *args, **kwargs
                    )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            nonlocal operation
            if operation is None:
                operation = func.__name__
                
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # For synchronous functions, we still need to run the async error handler
                # but we'll use asyncio.run to make it work in a synchronous context
                metadata = {
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "function": func.__name__
                }
                
                if recovery_strategy:
                    # Use the provided strategy
                    context = ErrorContext(
                        error=e,
                        component=component,
                        operation=operation,
                        severity=severity,
                        metadata=metadata
                    )
                    return asyncio.run(recovery_strategy.execute(context, func, *args, **kwargs))
                else:
                    # Use the global error recovery system
                    return asyncio.run(error_recovery.handle_error(
                        error=e,
                        component=component,
                        operation=operation,
                        severity=severity,
                        metadata=metadata,
                        original_function=func,
                        *args, **kwargs
                    ))
        
        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator
