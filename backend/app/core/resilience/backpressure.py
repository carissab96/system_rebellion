import time
import logging
import asyncio
from collections import deque
from typing import Dict, List, Any, Optional, Callable, TypeVar, Generic, Deque
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for the items in the buffer

class BackpressureHandler(Generic[T]):
    """
    The Hamster's Quantum Duct Tape Solution for Backpressure
    
    Handles data flow control to prevent overwhelming the system when
    data is produced faster than it can be consumed.
    """
    
    def __init__(
        self, 
        name: str = "default",
        max_buffer_size: int = 1000,
        sampling_strategy: str = "priority",  # Options: random, priority, latest
        processing_rate_window: int = 10,  # Calculate processing rate over this many items
        adaptive_sampling: bool = True,
        priority_func: Optional[Callable[[T], float]] = None
    ):
        self.name = name
        self.buffer: Deque[T] = deque(maxlen=max_buffer_size)
        self.max_buffer_size = max_buffer_size
        self.sampling_strategy = sampling_strategy
        self.adaptive_sampling = adaptive_sampling
        self.priority_func = priority_func
        
        # Performance tracking
        self.processing_times: Deque[float] = deque(maxlen=processing_rate_window)
        self.incoming_rate = 0  # items per second
        self.processing_rate = 0  # items per second
        self.last_incoming_time = time.time()
        self.incoming_count = 0
        self.processed_count = 0
        self.dropped_count = 0
        self.last_rate_calculation = time.time()
        self.rate_calculation_interval = 5.0  # seconds
        
        logger.info(f"Backpressure Handler '{name}' initialized with buffer size={max_buffer_size}, strategy={sampling_strategy}")
    
    def _update_rates(self) -> None:
        """Update the incoming and processing rates"""
        now = time.time()
        if now - self.last_rate_calculation >= self.rate_calculation_interval:
            time_diff = now - self.last_rate_calculation
            
            # Calculate rates
            if time_diff > 0:
                self.incoming_rate = self.incoming_count / time_diff
                self.processing_rate = self.processed_count / time_diff
            
            # Reset counters
            self.incoming_count = 0
            self.processed_count = 0
            self.last_rate_calculation = now
            
            # Log the current state
            buffer_usage = len(self.buffer) / self.max_buffer_size * 100
            logger.debug(
                f"Backpressure '{self.name}': Buffer {buffer_usage:.1f}% full, "
                f"In: {self.incoming_rate:.2f}/s, Out: {self.processing_rate:.2f}/s, "
                f"Dropped: {self.dropped_count} total"
            )
    
    def get_buffer_pressure(self) -> float:
        """
        Get the current buffer pressure as a value between 0.0 and 1.0
        0.0 = empty buffer, 1.0 = full buffer
        """
        return len(self.buffer) / self.max_buffer_size if self.max_buffer_size > 0 else 0.0
    
    def get_rate_pressure(self) -> float:
        """
        Get the current rate pressure as a value between 0.0 and 1.0
        0.0 = processing faster than incoming, 1.0 = incoming much faster than processing
        """
        if self.processing_rate <= 0:
            return 1.0  # Nothing being processed, maximum pressure
        
        if self.incoming_rate <= 0:
            return 0.0  # Nothing coming in, no pressure
        
        ratio = self.incoming_rate / self.processing_rate
        # Cap at 1.0 for values above 1.0 (incoming > processing)
        return min(1.0, ratio)
    
    def get_overall_pressure(self) -> float:
        """
        Get the overall system pressure as a value between 0.0 and 1.0
        Combines buffer fullness and processing rate pressure
        """
        buffer_pressure = self.get_buffer_pressure()
        rate_pressure = self.get_rate_pressure()
        
        # Weight buffer pressure more as it fills up
        # This creates an exponential response as the buffer fills
        return 0.4 * buffer_pressure + 0.6 * rate_pressure
    
    def should_sample(self) -> bool:
        """
        Determine if an incoming item should be sampled or dropped
        based on the current system pressure
        """
        if not self.adaptive_sampling:
            return True
            
        pressure = self.get_overall_pressure()
        
        # The higher the pressure, the more aggressive the sampling
        # At pressure 0.0, accept 100% of items
        # At pressure 1.0, accept very few items
        threshold = 1.0 - pressure**2  # Squared for more aggressive sampling at high pressure
        
        # Random sampling based on pressure
        return np.random.random() < threshold
    
    def add_item(self, item: T) -> bool:
        """
        Add an item to the buffer
        
        Returns:
            bool: True if the item was added, False if it was dropped
        """
        self._update_rates()
        self.incoming_count += 1
        
        # If buffer has space, always add the item
        if len(self.buffer) < self.max_buffer_size:
            self.buffer.append(item)
            return True
            
        # Buffer is full, use sampling strategy
        if self.should_sample():
            # Determine which item to replace based on strategy
            if self.sampling_strategy == "random":
                # Replace a random item
                idx = np.random.randint(0, len(self.buffer))
                self.buffer[idx] = item
                return True
                
            elif self.sampling_strategy == "priority" and self.priority_func:
                # Replace the lowest priority item if new item has higher priority
                new_priority = self.priority_func(item)
                lowest_idx = 0
                lowest_priority = float('inf')
                
                for i, existing in enumerate(self.buffer):
                    priority = self.priority_func(existing)
                    if priority < lowest_priority:
                        lowest_priority = priority
                        lowest_idx = i
                
                if new_priority > lowest_priority:
                    self.buffer[lowest_idx] = item
                    return True
            else:
                # Default: replace oldest (leftmost) item
                self.buffer.popleft()
                self.buffer.append(item)
                return True
        
        # Item was dropped
        self.dropped_count += 1
        return False
    
    def get_batch(self, max_batch_size: int) -> List[T]:
        """
        Get a batch of items from the buffer
        
        Args:
            max_batch_size: Maximum number of items to retrieve
            
        Returns:
            List of items, may be empty if buffer is empty
        """
        start_time = time.time()
        batch_size = min(max_batch_size, len(self.buffer))
        
        if batch_size == 0:
            return []
            
        batch = []
        for _ in range(batch_size):
            if not self.buffer:
                break
            batch.append(self.buffer.popleft())
        
        # Update processing stats
        self.processed_count += len(batch)
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)
        
        self._update_rates()
        return batch
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics about the backpressure handler"""
        return {
            "name": self.name,
            "buffer_size": len(self.buffer),
            "max_buffer_size": self.max_buffer_size,
            "buffer_usage_percent": len(self.buffer) / self.max_buffer_size * 100 if self.max_buffer_size > 0 else 0,
            "incoming_rate": self.incoming_rate,
            "processing_rate": self.processing_rate,
            "dropped_count": self.dropped_count,
            "buffer_pressure": self.get_buffer_pressure(),
            "rate_pressure": self.get_rate_pressure(),
            "overall_pressure": self.get_overall_pressure(),
        }


# Global registry of backpressure handlers
_backpressure_handlers: Dict[str, BackpressureHandler] = {}

def get_backpressure_handler(name: str = "default", **kwargs) -> BackpressureHandler:
    """Get or create a backpressure handler by name"""
    if name not in _backpressure_handlers:
        _backpressure_handlers[name] = BackpressureHandler(name=name, **kwargs)
    return _backpressure_handlers[name]
