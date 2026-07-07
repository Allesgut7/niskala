# Niskala - Position Tracker
# Real-time position tracking with P&L

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging


@dataclass
class TrackedPosition:
    """Tracked position with real-time data"""
    symbol: str
    quantity: int
    avg_price: float
    total_cost: float
    current_price: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    realized_pnl: float = 0.0
    commission_paid: float = 0.0
    opened_at: str = ''
    updated_at: str = ''


class PositionTracker:
    """Real-time position tracking engine"""
    
    def __init__(self):
        self._positions: Dict[str, TrackedPosition] = {}
        self._closed_positions: List[TrackedPosition] = []
        logging.info("PositionTracker initialized")
    
    def open_position(self, symbol: str, quantity: int, price: float,
                      commission: float = 0) -> TrackedPosition:
        """Open or add to a position
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares to buy
            price: Execution price
            commission: Commission paid
        
        Returns:
            Updated TrackedPosition
        """
        now = datetime.now().isoformat()
        
        if symbol in self._positions:
            # Add to existing position
            pos = self._positions[symbol]
            total_cost = (pos.avg_price * pos.quantity) + (price * quantity) + commission
            total_quantity = pos.quantity + quantity
            avg_price = total_cost / total_quantity if total_quantity > 0 else 0
            
            pos.quantity = total_quantity
            pos.avg_price = avg_price
            pos.total_cost = total_cost
            pos.commission_paid += commission
            pos.updated_at = now
        else:
            # Create new position
            total_cost = (price * quantity) + commission
            avg_price = total_cost / quantity if quantity > 0 else 0
            
            pos = TrackedPosition(
                symbol=symbol,
                quantity=quantity,
                avg_price=avg_price,
                total_cost=total_cost,
                commission_paid=commission,
                opened_at=now,
                updated_at=now,
            )
            self._positions[symbol] = pos
        
        logging.info(f"Position opened/updated: {symbol} x{quantity} @ {price:,.0f}")
        return pos
    
    def close_position(self, symbol: str, quantity: int, price: float,
                       commission: float = 0) -> Optional[TrackedPosition]:
        """Close or reduce a position
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares to sell
            price: Execution price
            commission: Commission paid
        
        Returns:
            Closed position or None if not found
        """
        if symbol not in self._positions:
            logging.warning(f"No position to close for {symbol}")
            return None
        
        pos = self._positions[symbol]
        
        if quantity > pos.quantity:
            quantity = pos.quantity
        
        # Calculate realized P&L
        sell_proceeds = (price * quantity) - commission
        cost_basis = pos.avg_price * quantity
        realized_pnl = sell_proceeds - cost_basis
        
        # Update position
        pos.quantity -= quantity
        pos.realized_pnl += realized_pnl
        pos.commission_paid += commission
        pos.updated_at = datetime.now().isoformat()
        
        # Remove if fully closed
        if pos.quantity == 0:
            closed_pos = self._positions.pop(symbol)
            self._closed_positions.append(closed_pos)
            logging.info(f"Position closed: {symbol} P&L: {realized_pnl:,.0f}")
            return closed_pos
        
        logging.info(f"Position reduced: {symbol} x{quantity} P&L: {realized_pnl:,.0f}")
        return pos
    
    def update_prices(self, current_prices: Dict[str, float]):
        """Update all positions with current market prices
        
        Args:
            current_prices: {symbol: current_price}
        """
        for symbol, pos in self._positions.items():
            if symbol in current_prices:
                pos.current_price = current_prices[symbol]
                pos.market_value = pos.current_price * pos.quantity
                cost_basis = pos.avg_price * pos.quantity
                pos.unrealized_pnl = pos.market_value - cost_basis
                pos.unrealized_pnl_pct = (pos.unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
                pos.updated_at = datetime.now().isoformat()
    
    def get_position(self, symbol: str) -> Optional[TrackedPosition]:
        """Get position for a symbol"""
        return self._positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, TrackedPosition]:
        """Get all open positions"""
        return dict(self._positions)
    
    def get_closed_positions(self) -> List[TrackedPosition]:
        """Get all closed positions"""
        return list(self._closed_positions)
    
    def get_total_realized_pnl(self) -> float:
        """Get total realized P&L from closed positions"""
        return sum(pos.realized_pnl for pos in self._closed_positions)
    
    def get_total_unrealized_pnl(self) -> float:
        """Get total unrealized P&L from open positions"""
        return sum(pos.unrealized_pnl for pos in self._positions.values())
    
    def get_total_commission(self) -> float:
        """Get total commission paid"""
        open_commission = sum(pos.commission_paid for pos in self._positions.values())
        closed_commission = sum(pos.commission_paid for pos in self._closed_positions)
        return open_commission + closed_commission
    
    def get_positions_summary(self) -> Dict:
        """Get positions summary"""
        positions = list(self._positions.values())
        
        total_market_value = sum(p.market_value for p in positions)
        total_cost = sum(p.total_cost for p in positions)
        total_unrealized = sum(p.unrealized_pnl for p in positions)
        total_realized = sum(p.realized_pnl for p in self._closed_positions)
        
        return {
            'position_count': len(positions),
            'total_market_value': total_market_value,
            'total_cost': total_cost,
            'total_unrealized_pnl': total_unrealized,
            'total_realized_pnl': total_realized,
            'total_pnl': total_unrealized + total_realized,
            'total_commission': self.get_total_commission(),
            'positions': [
                {
                    'symbol': p.symbol,
                    'quantity': p.quantity,
                    'avg_price': p.avg_price,
                    'current_price': p.current_price,
                    'market_value': p.market_value,
                    'unrealized_pnl': p.unrealized_pnl,
                    'unrealized_pnl_pct': p.unrealized_pnl_pct,
                }
                for p in positions
            ],
            'closed_count': len(self._closed_positions),
        }
    
    def to_dict(self) -> Dict:
        """Export positions state for persistence"""
        return {
            'open': {
                symbol: {
                    'quantity': p.quantity,
                    'avg_price': p.avg_price,
                    'total_cost': p.total_cost,
                    'realized_pnl': p.realized_pnl,
                    'commission_paid': p.commission_paid,
                    'opened_at': p.opened_at,
                }
                for symbol, p in self._positions.items()
            },
            'closed': [
                {
                    'symbol': p.symbol,
                    'quantity': p.quantity,
                    'avg_price': p.avg_price,
                    'realized_pnl': p.realized_pnl,
                    'commission_paid': p.commission_paid,
                    'opened_at': p.opened_at,
                }
                for p in self._closed_positions
            ],
        }
    
    def from_dict(self, data: Dict):
        """Restore positions from persistence"""
        self._positions.clear()
        self._closed_positions.clear()
        
        for symbol, pos_data in data.get('open', {}).items():
            self._positions[symbol] = TrackedPosition(
                symbol=symbol,
                quantity=pos_data['quantity'],
                avg_price=pos_data['avg_price'],
                total_cost=pos_data.get('total_cost', 0),
                realized_pnl=pos_data.get('realized_pnl', 0),
                commission_paid=pos_data.get('commission_paid', 0),
                opened_at=pos_data.get('opened_at', ''),
                updated_at=datetime.now().isoformat(),
            )
        
        for pos_data in data.get('closed', []):
            self._closed_positions.append(TrackedPosition(
                symbol=pos_data['symbol'],
                quantity=pos_data['quantity'],
                avg_price=pos_data['avg_price'],
                total_cost=0,
                realized_pnl=pos_data.get('realized_pnl', 0),
                commission_paid=pos_data.get('commission_paid', 0),
                opened_at=pos_data.get('opened_at', ''),
            ))
