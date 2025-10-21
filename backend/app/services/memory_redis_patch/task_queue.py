import json
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import IntEnum
import redis.asyncio as aioredis
from .redis_client import RedisClient


class Priority(IntEnum):
    CRITICAL = 1  # Auth, CSRF
    HIGH = 2      # User requests
    NORMAL = 5    # Regular metrics
    LOW = 10      # Background tasks

class TaskProcessingError(Exception):
    """Custom exception for task processing errors"""
    pass

class RedisTaskQueue:
    def __init__(
        self, 
        redis_client,
        max_retries: int = 3, 
        dead_letter_queue: str = "hawkington:dead_letters"
    ):
        self.redis = redis_client
        self.max_retries = max_retries
        self.dead_letter_queue = dead_letter_queue

    async def enqueue(
        self,
        task_type: str,
        data: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        retry_count: int = 0
    ) -> str:
        """Enqueue a task with retry logic and dead-letter queue support"""
        task_id = f"{task_type}_{uuid.uuid4().hex}"
        task = {
            'id': task_id,
            'type': task_type,
            'data': data,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'retry_count': retry_count,
            'max_retries': self.max_retries
        }

        try:
            # Use transaction to ensure atomicity
            async with self.redis.pipeline(transaction=True) as pipe:
                await (
                    pipe.zadd(
                        'hawkington:task_queue',
                        {json.dumps(task, default=str): int(priority)}  # default=str handles datetime
                    )
                    .expire('hawkington:task_queue', 86400)  # 24h TTL
                    .execute()
                )
            return task_id
        except Exception as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.enqueue(task_type, data, priority, retry_count + 1)
            await self._move_to_dead_letter_queue(task, str(e))
            raise TaskProcessingError(f"Failed to enqueue task after {self.max_retries} attempts: {str(e)}")

    async def _move_to_dead_letter_queue(self, task: Dict[str, Any], error: str):
        """Move failed task to dead-letter queue"""
        try:
            task['error'] = error
            task['failed_at'] = datetime.now(timezone.utc).isoformat()
            await self.redis.lpush(
                self.dead_letter_queue,
                json.dumps(task, default=str)  # default=str handles datetime
            )
            await self.redis.ltrim(self.dead_letter_queue, 0, 999)  # Keep last 1000 failed tasks
        except Exception as e:
            # If we can't even log to dead-letter queue, log to error log
            import logging
            logging.error(f"CRITICAL: Failed to write to dead-letter queue: {str(e)}")
            logging.error(f"Original task: {task}")

    async def dequeue(self, batch_size: int = 5) -> list:
        """Get highest priority tasks"""
        # Pop lowest scores (highest priority)
        pipe = self.redis.pipeline()
        pipe.zrange('hawkington:task_queue', 0, batch_size - 1)
        pipe.zremrangebyrank('hawkington:task_queue', 0, batch_size - 1)
        results = await pipe.execute()
        
        return [json.loads(task) for task in results[0]] if results[0] else []