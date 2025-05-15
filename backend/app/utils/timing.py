"""
Timing utilities for performance monitoring.
"""
import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, TypeVar, cast
from typing_extensions import ParamSpec

P = ParamSpec('P')
T = TypeVar('T')

def timeit(logger: Optional[logging.Logger] = None, level: int = logging.DEBUG, 
          threshold_ms: float = 100.0) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to measure and log execution time of synchronous and async functions.
    
    Args:
        logger: Logger instance to use for logging
        level: Logging level
        threshold_ms: Only log if execution time exceeds this threshold in milliseconds
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if is_async_func(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.monotonic()
                try:
                    return await func(*args, **kwargs)
                finally:
                    duration = (time.monotonic() - start_time) * 1000  # in ms
                    if duration >= threshold_ms:
                        log_msg = f"{func.__qualname__} took {duration:.2f}ms"
                        if logger:
                            logger.log(level, log_msg)
                        else:
                            print(log_msg)
            return cast(Callable[P, T], async_wrapper)
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.monotonic()
                try:
                    return func(*args, **kwargs)
                finally:
                    duration = (time.monotonic() - start_time) * 1000  # in ms
                    if duration >= threshold_ms:
                        log_msg = f"{func.__qualname__} took {duration:.2f}ms"
                        if logger:
                            logger.log(level, log_msg)
                        else:
                            print(log_msg)
            return sync_wrapper
    return decorator

def is_async_func(func: Callable[..., Any]) -> bool:
    """Check if a function is async."""
    return str(type(func).__name__) == 'function' and str(func.__code__.co_flags & 0x80) != '0'
