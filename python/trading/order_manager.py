# Niskala - Order Manager
# Order lifecycle management for paper trading

import uuid
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging


class OrderStatus(Enum):
    PENDING = 'pending'
    MATCHING = 'matching'
    FILLED = 'filled'
    PARTIALLY_FILLED = 'partially_filled'
    CANCELLED = 'cancelled'
    REJECTED = 'rejected'


class OrderType(Enum):
    MARKET = 'market'
    LIMIT = 'limit'


class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'


@dataclass
class Order:
    """Trading order"""
    id: str
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    fill_price: float = 0.0
    commission: float = 0.0
    created_at: str = ''
    updated_at: str = ''
    filled_at: str = ''
    notes: str = ''


class OrderManager:
    """Order lifecycle management"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
        self._pending_orders: List[str] = []
        logging.info("OrderManager initialized")
    
    def create_order(self, symbol: str, side: str, quantity: int,
                     order_type: str = 'market', price: Optional[float] = None,
                     notes: str = '') -> Order:
        """Create a new order
        
        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: 'market' or 'limit'
            price: Limit price (required for limit orders)
            notes: Optional notes
        
        Returns:
            Created Order
        """
        now = datetime.now().isoformat()
        
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=OrderSide(side),
            quantity=quantity,
            order_type=OrderType(order_type),
            price=price,
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now,
            notes=notes,
        )
        
        self._orders[order.id] = order
        self._pending_orders.append(order.id)
        
        logging.info(f"Order created: {order.id[:8]}... {side} {quantity} {symbol} @ {order_type}")
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order
        
        Args:
            order_id: Order ID
        
        Returns:
            True if cancelled, False if not found or not cancellable
        """
        order = self._orders.get(order_id)
        if not order:
            logging.warning(f"Order not found: {order_id}")
            return False
        
        if order.status != OrderStatus.PENDING:
            logging.warning(f"Cannot cancel order {order_id}: status is {order.status.value}")
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now().isoformat()
        
        if order_id in self._pending_orders:
            self._pending_orders.remove(order_id)
        
        logging.info(f"Order cancelled: {order_id[:8]}...")
        return True
    
    def fill_order(self, order_id: str, fill_price: float,
                   fill_quantity: Optional[int] = None,
                   commission: float = 0) -> Optional[Order]:
        """Fill an order
        
        Args:
            order_id: Order ID
            fill_price: Execution price
            fill_quantity: Quantity filled (default: full order)
            commission: Commission charged
        
        Returns:
            Updated Order or None
        """
        order = self._orders.get(order_id)
        if not order:
            return None
        
        if order.status not in (OrderStatus.PENDING, OrderStatus.MATCHING):
            return None
        
        if fill_quantity is None:
            fill_quantity = order.quantity - order.filled_quantity
        
        # Ensure we don't overfill
        remaining = order.quantity - order.filled_quantity
        fill_quantity = min(fill_quantity, remaining)
        
        # Round to lot size
        from ..quant.backtest_engine import IDXCommissionModel
        fill_quantity = IDXCommissionModel.round_to_lot(fill_quantity)
        
        if fill_quantity == 0:
            order.status = OrderStatus.FILLED
            order.updated_at = datetime.now().isoformat()
            order.filled_at = datetime.now().isoformat()
            if order_id in self._pending_orders:
                self._pending_orders.remove(order_id)
            return order
        
        # Update order
        order.filled_quantity += fill_quantity
        order.fill_price = fill_price
        order.commission = commission
        order.updated_at = datetime.now().isoformat()
        
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.now().isoformat()
            if order_id in self._pending_orders:
                self._pending_orders.remove(order_id)
        else:
            order.status = OrderStatus.PARTIALLY_FILLED
        
        logging.info(f"Order filled: {order_id[:8]}... {fill_quantity} @ {fill_price:,.0f}")
        return order
    
    def reject_order(self, order_id: str, reason: str = '') -> bool:
        """Reject an order
        
        Args:
            order_id: Order ID
            reason: Rejection reason
        
        Returns:
            True if rejected
        """
        order = self._orders.get(order_id)
        if not order:
            return False
        
        order.status = OrderStatus.REJECTED
        order.notes = reason
        order.updated_at = datetime.now().isoformat()
        
        if order_id in self._pending_orders:
            self._pending_orders.remove(order_id)
        
        logging.info(f"Order rejected: {order_id[:8]}... reason: {reason}")
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self._orders.get(order_id)
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders"""
        return [self._orders[oid] for oid in self._pending_orders if oid in self._orders]
    
    def get_orders_by_symbol(self, symbol: str) -> List[Order]:
        """Get all orders for a symbol"""
        return [o for o in self._orders.values() if o.symbol == symbol]
    
    def get_all_orders(self, status: Optional[str] = None) -> List[Order]:
        """Get all orders, optionally filtered by status"""
        orders = list(self._orders.values())
        if status:
            orders = [o for o in orders if o.status.value == status]
        return sorted(orders, key=lambda o: o.created_at, reverse=True)
    
    def to_dict(self, order: Order) -> Dict:
        """Convert order to dictionary"""
        return {
            'id': order.id,
            'symbol': order.symbol,
            'side': order.side.value,
            'quantity': order.quantity,
            'order_type': order.order_type.value,
            'price': order.price,
            'status': order.status.value,
            'filled_quantity': order.filled_quantity,
            'fill_price': order.fill_price,
            'commission': order.commission,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
            'filled_at': order.filled_at,
            'notes': order.notes,
        }
    
    def from_dict(self, data: Dict) -> Order:
        """Restore order from dictionary"""
        order = Order(
            id=data['id'],
            symbol=data['symbol'],
            side=OrderSide(data['side']),
            quantity=data['quantity'],
            order_type=OrderType(data['order_type']),
            price=data.get('price'),
            status=OrderStatus(data['status']),
            filled_quantity=data.get('filled_quantity', 0),
            fill_price=data.get('fill_price', 0),
            commission=data.get('commission', 0),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            filled_at=data.get('filled_at', ''),
            notes=data.get('notes', ''),
        )
        self._orders[order.id] = order
        if order.status == OrderStatus.PENDING:
            self._pending_orders.append(order.id)
        return order
