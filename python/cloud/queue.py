# Niskala - Background Task Queue
# Redis-based task queue for background jobs

import asyncio
import json
import uuid
from typing import Optional, Dict, Any, Callable, Awaitable
from datetime import datetime
from enum import Enum
import logging

from .cache import get_cache, RedisCache

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class Task:
    """Task representation"""
    
    def __init__(self, task_id: str, name: str, payload: Dict, 
                 priority: TaskPriority = TaskPriority.NORMAL):
        self.id = task_id
        self.name = name
        self.payload = payload
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.retry_count = 0
        self.max_retries = 3
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'payload': self.payload,
            'priority': self.priority.value,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'retry_count': self.retry_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        task = cls(
            task_id=data['id'],
            name=data['name'],
            payload=data['payload'],
            priority=TaskPriority(data.get('priority', 1)),
        )
        task.status = TaskStatus(data.get('status', 'pending'))
        task.result = data.get('result')
        task.error = data.get('error')
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.started_at = data.get('started_at')
        task.completed_at = data.get('completed_at')
        task.retry_count = data.get('retry_count', 0)
        return task


class TaskQueue:
    """Redis-based task queue"""
    
    QUEUE_KEY = "niskala:tasks:queue"
    PROCESSING_KEY = "niskala:tasks:processing"
    RESULTS_KEY = "niskala:tasks:results"
    
    def __init__(self):
        self._cache: Optional[RedisCache] = None
        self._handlers: Dict[str, Callable[..., Awaitable]] = {}
        self._running = False
    
    async def connect(self):
        """Connect to Redis"""
        self._cache = await get_cache()
        logger.info("TaskQueue connected")
    
    def register_handler(self, task_name: str, handler: Callable[..., Awaitable]):
        """Register task handler"""
        self._handlers[task_name] = handler
        logger.info(f"Handler registered: {task_name}")
    
    async def enqueue(self, task_name: str, payload: Dict, 
                      priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Add task to queue"""
        task_id = str(uuid.uuid4())
        task = Task(task_id, task_name, payload, priority)
        
        # Store task
        await self._cache.set_json(
            f"{self.RESULTS_KEY}:{task_id}",
            task.to_dict(),
            ttl=86400 * 7,  # 7 days
        )
        
        # Add to queue (sorted by priority)
        await self._cache._client.zadd(
            self.QUEUE_KEY,
            {task_id: priority.value}
        )
        
        logger.info(f"Task enqueued: {task_name} (id: {task_id[:8]})")
        return task_id
    
    async def dequeue(self) -> Optional[Task]:
        """Get next task from queue"""
        if not self._cache:
            return None
        
        # Get highest priority task
        result = await self._cache._client.zpopmin(self.QUEUE_KEY, count=1)
        
        if not result:
            return None
        
        task_id = result[0][0]
        
        # Get task data
        task_data = await self._cache.get_json(f"{self.RESULTS_KEY}:{task_id}")
        if not task_data:
            return None
        
        task = Task.from_dict(task_data)
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        # Move to processing
        await self._cache._client.sadd(self.PROCESSING_KEY, task_id)
        
        # Update task
        await self._cache.set_json(
            f"{self.RESULTS_KEY}:{task_id}",
            task.to_dict(),
            ttl=86400 * 7,
        )
        
        return task
    
    async def complete_task(self, task: Task, result: Any = None):
        """Mark task as completed"""
        task.status = TaskStatus.COMPLETED
        task.result = result
        task.completed_at = datetime.now().isoformat()
        
        await self._cache._client.srem(self.PROCESSING_KEY, task.id)
        
        await self._cache.set_json(
            f"{self.RESULTS_KEY}:{task.id}",
            task.to_dict(),
            ttl=86400 * 7,
        )
        
        logger.info(f"Task completed: {task.name} (id: {task.id[:8]})")
    
    async def fail_task(self, task: Task, error: str):
        """Mark task as failed"""
        task.error = error
        
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRY
            # Re-queue with lower priority
            await self._cache._client.zadd(
                self.QUEUE_KEY,
                {task.id: TaskPriority.LOW.value}
            )
            logger.warning(f"Task retry: {task.name} (attempt {task.retry_count})")
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            logger.error(f"Task failed: {task.name} - {error}")
        
        await self._cache._client.srem(self.PROCESSING_KEY, task.id)
        
        await self._cache.set_json(
            f"{self.RESULTS_KEY}:{task.id}",
            task.to_dict(),
            ttl=86400 * 7,
        )
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        task_data = await self._cache.get_json(f"{self.RESULTS_KEY}:{task_id}")
        if task_data:
            return Task.from_dict(task_data)
        return None
    
    async def get_queue_size(self) -> int:
        """Get queue size"""
        return await self._cache._client.zcard(self.QUEUE_KEY)
    
    async def process_tasks(self):
        """Process tasks from queue"""
        while self._running:
            try:
                task = await self.dequeue()
                if task:
                    handler = self._handlers.get(task.name)
                    if handler:
                        try:
                            result = await handler(task.payload)
                            await self.complete_task(task, result)
                        except Exception as e:
                            await self.fail_task(task, str(e))
                    else:
                        await self.fail_task(task, f"No handler for task: {task.name}")
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Task processing error: {e}")
                await asyncio.sleep(5)
    
    async def start(self):
        """Start task processing"""
        self._running = True
        asyncio.create_task(self.process_tasks())
        logger.info("TaskQueue started")
    
    async def stop(self):
        """Stop task processing"""
        self._running = False
        logger.info("TaskQueue stopped")


# Task handlers

async def handle_trade_alert(payload: Dict) -> Dict:
    """Handle trade alert task"""
    logger.info(f"Processing trade alert: {payload}")
    # Send notification via Telegram/Discord
    return {"sent": True}


async def handle_price_alert(payload: Dict) -> Dict:
    """Handle price alert task"""
    logger.info(f"Processing price alert: {payload}")
    # Check price and notify
    return {"checked": True}


async def handle_portfolio_sync(payload: Dict) -> Dict:
    """Handle portfolio sync task"""
    logger.info(f"Processing portfolio sync: {payload}")
    # Sync positions from broker
    return {"synced": True}


# Singleton
_queue: Optional[TaskQueue] = None


async def get_queue() -> TaskQueue:
    """Get task queue instance"""
    global _queue
    if _queue is None:
        _queue = TaskQueue()
        await _queue.connect()
        _queue.register_handler("trade_alert", handle_trade_alert)
        _queue.register_handler("price_alert", handle_price_alert)
        _queue.register_handler("portfolio_sync", handle_portfolio_sync)
    return _queue


async def close_queue():
    """Close task queue"""
    global _queue
    if _queue:
        await _queue.stop()
        _queue = None
