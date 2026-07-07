# Niskala - Execution Tracker
# Real-time order execution status tracking

import asyncio
import json
from typing import Dict, Optional, List, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExecutionTracker:
    """Real-time order execution status tracking"""
    
    def __init__(self):
        self._order_statuses: Dict[str, Dict] = {}
        self._callbacks: List[Callable] = []
        self._ws_connections: List = []
        logger.info("ExecutionTracker initialized")
    
    def on_status_update(self, callback: Callable):
        """Register callback for status updates"""
        self._callbacks.append(callback)
    
    async def register_websocket(self, websocket):
        """Register WebSocket for real-time updates"""
        self._ws_connections.append(websocket)
    
    def unregister_websocket(self, websocket):
        """Unregister WebSocket"""
        if websocket in self._ws_connections:
            self._ws_connections.remove(websocket)
    
    async def update_status(self, order_id: str, status: str,
                            fill_price: Optional[float] = None,
                            fill_quantity: Optional[int] = None,
                            broker: str = '', error: str = ''):
        """Update order status
        
        Args:
            order_id: Order ID
            status: New status
            fill_price: Fill price (if filled)
            fill_quantity: Fill quantity (if filled)
            broker: Broker name
            error: Error message (if rejected)
        """
        update = {
            'order_id': order_id,
            'status': status,
            'fill_price': fill_price,
            'fill_quantity': fill_quantity,
            'broker': broker,
            'error': error,
            'timestamp': datetime.now().isoformat(),
        }
        
        self._order_statuses[order_id] = update
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        # Broadcast to WebSocket connections
        await self._broadcast(update)
        
        logger.info(f"Order {order_id[:8]}... status: {status}")
    
    async def _broadcast(self, message: Dict):
        """Broadcast message to all WebSocket connections"""
        dead_connections = []
        
        for ws in self._ws_connections:
            try:
                await ws.send_json({
                    'type': 'order_update',
                    'data': message,
                })
            except Exception:
                dead_connections.append(ws)
        
        # Remove dead connections
        for ws in dead_connections:
            self._ws_connections.remove(ws)
    
    def get_status(self, order_id: str) -> Optional[Dict]:
        """Get order status"""
        return self._order_statuses.get(order_id)
    
    def get_all_statuses(self) -> Dict[str, Dict]:
        """Get all order statuses"""
        return dict(self._order_statuses)
    
    def get_pending_orders(self) -> List[Dict]:
        """Get all pending orders"""
        return [
            status for status in self._order_statuses.values()
            if status['status'] in ('pending', 'matching')
        ]
    
    def get_filled_orders(self) -> List[Dict]:
        """Get all filled orders"""
        return [
            status for status in self._order_statuses.values()
            if status['status'] == 'filled'
        ]
    
    async def simulate_fill(self, order_id: str, price: float,
                            quantity: int, broker: str = 'paper'):
        """Simulate order fill (for paper trading)"""
        await self.update_status(
            order_id=order_id,
            status='filled',
            fill_price=price,
            fill_quantity=quantity,
            broker=broker,
        )
    
    async def simulate_rejection(self, order_id: str, reason: str,
                                 broker: str = 'paper'):
        """Simulate order rejection"""
        await self.update_status(
            order_id=order_id,
            status='rejected',
            broker=broker,
            error=reason,
        )
