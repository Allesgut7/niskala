# Niskala - Paper Trading Engine
# Core paper trading engine with IDX-specific rules

import json
import time
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from ..quant.backtest_engine import IDXCommissionModel, OrderSide, OrderType
from .order_manager import OrderManager, Order, OrderStatus
from .position_tracker import PositionTracker
from .pnl_calculator import PnLCalculator, PnLSummary
from .risk_manager import RiskManager, RiskLimits
from .trade_history import TradeHistory
from .market_simulator import MarketSimulator


@dataclass
class TradingConfig:
    """Paper trading configuration"""
    initial_capital: float = 100_000_000  # 100M IDR
    commission_model: Optional[IDXCommissionModel] = None
    risk_limits: Optional[RiskLimits] = None
    db_path: str = 'data/paper_trading.db'
    use_simulator: bool = True


class PaperTradingEngine:
    """Paper trading engine for IDX stocks
    
    Features:
    - Real-time order execution (simulated)
    - IDX-specific rules (lot size, tick size, commission)
    - Position tracking with P&L
    - Risk management (stop loss, take profit)
    - Trade history with SQLite persistence
    """
    
    def __init__(self, config: Optional[TradingConfig] = None):
        self.config = config or TradingConfig()
        
        # Initialize components
        self.commission_model = self.config.commission_model or IDXCommissionModel()
        self.order_manager = OrderManager()
        self.position_tracker = PositionTracker()
        self.pnl_calculator = PnLCalculator()
        self.risk_manager = RiskManager(self.config.risk_limits)
        self.trade_history = TradeHistory(self.config.db_path)
        self.market_simulator = MarketSimulator()
        
        # Portfolio state
        self.cash: float = self.config.initial_capital
        self.initial_capital: float = self.config.initial_capital
        self.total_realized_pnl: float = 0
        self.total_commission: float = 0
        self.day_pnl: float = 0
        
        # Load saved state
        self._load_state()
        
        # Callbacks
        self._on_trade: Optional[Callable] = None
        self._on_order_update: Optional[Callable] = None
        
        logging.info(f"PaperTradingEngine initialized with {self.initial_capital:,.0f} IDR")
    
    def set_callbacks(self, on_trade: Optional[Callable] = None,
                      on_order_update: Optional[Callable] = None):
        """Set event callbacks"""
        self._on_trade = on_trade
        self._on_order_update = on_order_update
    
    def place_order(self, symbol: str, side: str, quantity: int,
                    order_type: str = 'market', price: Optional[float] = None,
                    notes: str = '') -> Dict:
        """Place a new order
        
        Args:
            symbol: Stock symbol (e.g., 'BBCA')
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: 'market' or 'limit'
            price: Limit price (required for limit orders)
            notes: Optional notes
        
        Returns:
            Dict with order result
        """
        # Validate inputs
        symbol = symbol.upper()
        
        if order_type == 'limit' and price is None:
            return {'success': False, 'error': 'Limit order requires price'}
        
        if quantity <= 0:
            return {'success': False, 'error': 'Quantity must be positive'}
        
        # Round to lot size
        quantity = self.commission_model.round_to_lot(quantity)
        if quantity == 0:
            return {'success': False, 'error': 'Quantity too small for minimum lot (100)'}
        
        # Get current price
        current_price = price or self.market_simulator.get_price(symbol)
        if current_price is None:
            return {'success': False, 'error': f'No price available for {symbol}'}
        
        # Round to tick size
        current_price = self.commission_model.round_to_tick(current_price)
        
        # Create order
        order = self.order_manager.create_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=current_price if order_type == 'limit' else None,
            notes=notes,
        )
        
        # Risk check
        portfolio = self._get_portfolio_state()
        risk_check = self.risk_manager.check_pre_trade(
            order={'symbol': symbol, 'side': side, 'quantity': quantity,
                   'price': current_price, 'order_type': order_type},
            portfolio=portfolio,
            current_prices={symbol: current_price}
        )
        
        if not risk_check.passed:
            self.order_manager.reject_order(order.id, risk_check.reason)
            self._save_state()
            return {
                'success': False,
                'error': risk_check.reason,
                'order_id': order.id,
            }
        
        # Execute order (paper trading - immediate fill for market orders)
        if order_type == 'market':
            result = self._execute_order(order, current_price)
        else:
            # Limit orders wait for price match
            result = {'success': True, 'order_id': order.id, 'status': 'pending'}
        
        self._save_state()
        
        if self._on_order_update:
            self._on_order_update(self.order_manager.to_dict(order))
        
        return result
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel a pending order"""
        success = self.order_manager.cancel_order(order_id)
        self._save_state()
        
        if success:
            return {'success': True, 'message': 'Order cancelled'}
        return {'success': False, 'error': 'Cannot cancel order'}
    
    def _execute_order(self, order: Order, price: float) -> Dict:
        """Execute a paper order
        
        Args:
            order: Order to execute
            price: Execution price
        
        Returns:
            Execution result
        """
        symbol = order.symbol
        side = order.side.value
        quantity = order.quantity
        
        # Calculate commission
        trade_value = price * quantity
        commission = self.commission_model.calculate_commission(
            OrderSide(side), trade_value
        )
        
        if side == 'buy':
            total_cost = trade_value + commission
            
            # Check sufficient cash
            if total_cost > self.cash:
                self.order_manager.reject_order(order.id, 'Insufficient cash')
                return {'success': False, 'error': 'Insufficient cash'}
            
            # Execute buy
            self.cash -= total_cost
            self.position_tracker.open_position(symbol, quantity, price, commission)
            self.total_commission += commission
            
            # Record trade
            trade_id = f"trade_{order.id[:8]}"
            self.trade_history.save_trade(
                trade_id=trade_id,
                order_id=order.id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                value=trade_value,
                commission=commission,
                pnl=-commission,
            )
            
            # Fill order
            self.order_manager.fill_order(order.id, price, quantity, commission)
            
            logging.info(f"BUY {quantity} {symbol} @ {price:,.0f} = {trade_value:,.0f} (+{commission:,.0f} commission)")
            
        else:  # sell
            # Check position
            pos = self.position_tracker.get_position(symbol)
            if not pos or pos.quantity < quantity:
                available = pos.quantity if pos else 0
                self.order_manager.reject_order(order.id, f'Insufficient position: have {available}')
                return {'success': False, 'error': f'Insufficient position: have {available}'}
            
            # Execute sell
            proceeds = trade_value - commission
            self.cash += proceeds
            self.total_commission += commission
            
            # Close position
            closed_pos = self.position_tracker.close_position(symbol, quantity, price, commission)
            realized_pnl = closed_pos.realized_pnl if closed_pos else 0
            self.total_realized_pnl += realized_pnl
            self.day_pnl += realized_pnl
            
            # Record trade
            trade_id = f"trade_{order.id[:8]}"
            self.trade_history.save_trade(
                trade_id=trade_id,
                order_id=order.id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                value=trade_value,
                commission=commission,
                pnl=realized_pnl,
            )
            
            # Fill order
            self.order_manager.fill_order(order.id, price, quantity, commission)
            
            logging.info(f"SELL {quantity} {symbol} @ {price:,.0f} = {trade_value:,.0f} (P&L: {realized_pnl:,.0f})")
        
        # Update prices
        self.position_tracker.update_prices({symbol: price})
        
        # Fire callback
        if self._on_trade:
            self._on_trade({
                'order': self.order_manager.to_dict(order),
                'trade_id': trade_id,
                'price': price,
                'quantity': quantity,
                'commission': commission,
                'pnl': realized_pnl if side == 'sell' else -commission,
            })
        
        return {
            'success': True,
            'order_id': order.id,
            'trade_id': trade_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'commission': commission,
            'pnl': realized_pnl if side == 'sell' else -commission,
        }
    
    def check_stop_loss_take_profit(self) -> List[Dict]:
        """Check all positions for stop loss / take profit triggers"""
        triggers = []
        current_prices = {}
        
        for symbol, pos in self.position_tracker.get_all_positions().items():
            price = self.market_simulator.get_price(symbol)
            if price is None:
                continue
            
            current_prices[symbol] = price
            
            # Check stop loss
            sl_check = self.risk_manager.check_stop_loss(
                {'avg_price': pos.avg_price, 'quantity': pos.quantity},
                price
            )
            if not sl_check.passed:
                triggers.append({
                    'type': 'stop_loss',
                    'symbol': symbol,
                    'reason': sl_check.reason,
                    'action': 'sell',
                })
            
            # Check take profit
            tp_check = self.risk_manager.check_take_profit(
                {'avg_price': pos.avg_price, 'quantity': pos.quantity},
                price
            )
            if not tp_check.passed:
                triggers.append({
                    'type': 'take_profit',
                    'symbol': symbol,
                    'reason': tp_check.reason,
                    'action': 'sell',
                })
        
        # Update position prices
        self.position_tracker.update_prices(current_prices)
        
        return triggers
    
    def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio summary"""
        current_prices = {
            symbol: self.market_simulator.get_price(symbol)
            for symbol in self.position_tracker.get_all_positions()
        }
        current_prices = {k: v for k, v in current_prices.items() if v is not None}
        
        # Update position prices
        self.position_tracker.update_prices(current_prices)
        
        # Get P&L summary
        portfolio = self._get_portfolio_state()
        pnl_summary = self.pnl_calculator.calculate_portfolio_summary(
            portfolio=portfolio,
            current_prices=current_prices,
            initial_capital=self.initial_capital,
            total_realized_pnl=self.total_realized_pnl,
            total_commission=self.total_commission,
            day_pnl=self.day_pnl,
        )
        
        # Get risk metrics
        risk_metrics = self.risk_manager.get_portfolio_risk_metrics(portfolio, current_prices)
        
        return {
            'cash': self.cash,
            'initial_capital': self.initial_capital,
            'equity': pnl_summary.equity,
            'positions_value': pnl_summary.positions_value,
            'total_realized_pnl': self.total_realized_pnl,
            'total_unrealized_pnl': pnl_summary.total_unrealized_pnl,
            'total_pnl': pnl_summary.total_pnl,
            'total_commission': self.total_commission,
            'return_pct': pnl_summary.return_pct,
            'day_pnl': self.day_pnl,
            'day_return_pct': pnl_summary.day_return_pct,
            'positions': self.position_tracker.get_positions_summary(),
            'risk': risk_metrics,
            'pending_orders': len(self.order_manager.get_pending_orders()),
        }
    
    def get_trade_history(self, symbol: Optional[str] = None,
                          limit: int = 50) -> List[Dict]:
        """Get trade history"""
        trades = self.trade_history.get_trades(symbol=symbol, limit=limit)
        return [
            {
                'id': t.id,
                'order_id': t.order_id,
                'symbol': t.symbol,
                'side': t.side,
                'quantity': t.quantity,
                'price': t.price,
                'value': t.value,
                'commission': t.commission,
                'pnl': t.pnl,
                'timestamp': t.timestamp,
            }
            for t in trades
        ]
    
    def get_order_history(self, status: Optional[str] = None,
                          limit: int = 50) -> List[Dict]:
        """Get order history"""
        orders = self.order_manager.get_all_orders(status=status)[:limit]
        return [self.order_manager.to_dict(o) for o in orders]
    
    def reset_day_pnl(self):
        """Reset daily P&L tracking"""
        self.day_pnl = 0
        self.risk_manager.reset_daily()
    
    def _get_portfolio_state(self) -> Dict:
        """Get current portfolio state for risk checks"""
        positions = {}
        for symbol, pos in self.position_tracker.get_all_positions().items():
            price = self.market_simulator.get_price(symbol) or pos.avg_price
            positions[symbol] = {
                'quantity': pos.quantity,
                'avg_price': pos.avg_price,
                'market_value': price * pos.quantity,
            }
        
        equity = self.cash + sum(p['market_value'] for p in positions.values())
        
        return {
            'cash': self.cash,
            'positions': positions,
            'equity': equity,
        }
    
    def _save_state(self):
        """Save state to database"""
        self.trade_history.save_portfolio(
            cash=self.cash,
            initial_capital=self.initial_capital,
            total_realized_pnl=self.total_realized_pnl,
            total_commission=self.total_commission,
        )
        
        # Save positions
        for symbol, pos in self.position_tracker.get_all_positions().items():
            self.trade_history.save_position(
                symbol=symbol,
                quantity=pos.quantity,
                avg_price=pos.avg_price,
                total_cost=pos.total_cost,
                realized_pnl=pos.realized_pnl,
                unrealized_pnl=pos.unrealized_pnl,
            )
    
    def _load_state(self):
        """Load state from database"""
        portfolio = self.trade_history.load_portfolio()
        if portfolio:
            self.cash = portfolio['cash']
            self.initial_capital = portfolio['initial_capital']
            self.total_realized_pnl = portfolio['total_realized_pnl']
            self.total_commission = portfolio['total_commission']
        
        positions = self.trade_history.load_positions()
        for pos_data in positions:
            self.position_tracker.open_position(
                symbol=pos_data['symbol'],
                quantity=pos_data['quantity'],
                price=pos_data['avg_price'],
                commission=0,
            )
            # Restore realized P&L
            pos = self.position_tracker.get_position(pos_data['symbol'])
            if pos:
                pos.realized_pnl = pos_data.get('realized_pnl', 0)
    
    def to_dict(self) -> Dict:
        """Export engine state"""
        return {
            'cash': self.cash,
            'initial_capital': self.initial_capital,
            'total_realized_pnl': self.total_realized_pnl,
            'total_commission': self.total_commission,
            'day_pnl': self.day_pnl,
            'positions': self.position_tracker.to_dict(),
        }
    
    def from_dict(self, data: Dict):
        """Restore engine state"""
        self.cash = data.get('cash', self.initial_capital)
        self.total_realized_pnl = data.get('total_realized_pnl', 0)
        self.total_commission = data.get('total_commission', 0)
        self.day_pnl = data.get('day_pnl', 0)
        
        if 'positions' in data:
            self.position_tracker.from_dict(data['positions'])
