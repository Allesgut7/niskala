# Niskala - Background Worker
# Processes background tasks (trade alerts, price alerts, sync)

import asyncio
import signal
import sys
import logging
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Worker:
    """Background task worker"""
    
    def __init__(self):
        self._running = False
        self._tasks = {}
        logger.info("Worker initialized")
    
    async def start(self):
        """Start the worker"""
        self._running = True
        logger.info("Worker started")
        
        # Register task handlers
        self._tasks = {
            "trade_alert": self._handle_trade_alert,
            "price_alert": self._handle_price_alert,
            "portfolio_sync": self._handle_portfolio_sync,
            "market_update": self._handle_market_update,
        }
        
        # Main loop
        while self._running:
            try:
                await asyncio.sleep(1)
                # Process tasks from queue
                await self._process_queue()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the worker"""
        self._running = False
        logger.info("Worker stopped")
    
    async def _process_queue(self):
        """Process tasks from Redis queue"""
        try:
            from .cloud.cache import get_cache
            cache = await get_cache()
            
            # Check for tasks in queue
            task_data = await cache._client.lpop("niskala:tasks:queue")
            if task_data:
                import json
                task = json.loads(task_data)
                task_name = task.get("name")
                payload = task.get("payload", {})
                
                if task_name in self._tasks:
                    logger.info(f"Processing task: {task_name}")
                    await self._tasks[task_name](payload)
                else:
                    logger.warning(f"Unknown task: {task_name}")
        except Exception as e:
            # Queue might not be available yet
            pass
    
    async def _handle_trade_alert(self, payload: Dict[str, Any]):
        """Handle trade alert notification"""
        symbol = payload.get("symbol")
        action = payload.get("action")
        price = payload.get("price")
        logger.info(f"Trade alert: {action} {symbol} @ {price}")
        # TODO: Send notification via Telegram/Discord
    
    async def _handle_price_alert(self, payload: Dict[str, Any]):
        """Handle price alert"""
        symbol = payload.get("symbol")
        target_price = payload.get("target_price")
        condition = payload.get("condition")
        logger.info(f"Price alert: {symbol} {condition} {target_price}")
        # TODO: Check price and notify
    
    async def _handle_portfolio_sync(self, payload: Dict[str, Any]):
        """Handle portfolio sync from broker"""
        user_id = payload.get("user_id")
        logger.info(f"Portfolio sync for user: {user_id}")
        # TODO: Sync positions from broker
    
    async def _handle_market_update(self, payload: Dict[str, Any]):
        """Handle market data update"""
        symbol = payload.get("symbol")
        logger.info(f"Market update: {symbol}")
        # TODO: Update cached prices


async def main():
    """Main entry point"""
    worker = Worker()
    
    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    
    def shutdown():
        logger.info("Shutdown signal received")
        asyncio.create_task(worker.stop())
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown)
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
