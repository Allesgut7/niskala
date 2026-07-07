# Niskala - Backtesting Engine
# Version: 1.0.0
# Event-driven backtesting for IDX stocks

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
import logging


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Trading order"""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    filled: bool = False
    fill_price: float = 0.0


@dataclass
class Position:
    """Trading position"""
    symbol: str
    quantity: int
    avg_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0


@dataclass
class Trade:
    """Executed trade"""
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    commission: float
    timestamp: datetime
    pnl: float = 0.0


class IDXCommissionModel:
    """IDX commission and fee model"""
    
    # IDX trading fees
    BUY_COMMISSION = 0.0015  # 0.15%
    SELL_COMMISSION = 0.0025  # 0.25%
    TRANSACTION_TAX = 0.001   # 0.1%
    
    # IDX trading rules
    LOT_SIZE = 100
    TICK_SIZE_SMALL = 50    # For price < 2000
    TICK_SIZE_LARGE = 100   # For price >= 2000
    
    @classmethod
    def calculate_commission(cls, side: OrderSide, value: float) -> float:
        """Calculate commission for trade"""
        if side == OrderSide.BUY:
            return value * cls.BUY_COMMISSION
        else:
            return value * (cls.SELL_COMMISSION + cls.TRANSACTION_TAX)
    
    @classmethod
    def round_to_tick(cls, price: float) -> float:
        """Round price to valid tick size"""
        if price < 2000:
            return round(price / cls.TICK_SIZE_SMALL) * cls.TICK_SIZE_SMALL
        else:
            return round(price / cls.TICK_SIZE_LARGE) * cls.TICK_SIZE_LARGE
    
    @classmethod
    def round_to_lot(cls, quantity: int) -> int:
        """Round quantity to lot size"""
        return (quantity // cls.LOT_SIZE) * cls.LOT_SIZE


class BacktestEngine:
    """Event-driven backtesting engine for IDX stocks"""
    
    def __init__(
        self,
        initial_capital: float = 100_000_000,  # 100M IDR
        commission_model: Optional[IDXCommissionModel] = None
    ):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission_model = commission_model or IDXCommissionModel()
        
        # Portfolio state
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        
        # Performance tracking
        self.equity_curve: List[float] = [initial_capital]
        self.timestamps: List[datetime] = []
        
        # Strategy
        self.strategy_func: Optional[Callable] = None
        
        logging.info(f"Backtest engine initialized with {initial_capital:,.0f} IDR")
    
    def set_strategy(self, strategy_func: Callable):
        """Set trading strategy function
        
        Args:
            strategy_func: Function(data, portfolio) -> List[Order]
        """
        self.strategy_func = strategy_func
    
    def run(self, data: pd.DataFrame, symbol: str) -> Dict:
        """Run backtest on historical data
        
        Args:
            data: DataFrame with columns: timestamp, open, high, low, close, volume
            symbol: Stock symbol
            
        Returns:
            Dict with backtest results
        """
        if self.strategy_func is None:
            raise ValueError("Strategy function not set")
        
        logging.info(f"Running backtest for {symbol} with {len(data)} bars")
        
        # Reset state
        self._reset()
        
        # Iterate through each bar
        for idx, row in data.iterrows():
            timestamp = row['timestamp'] if 'timestamp' in row else idx
            self.timestamps.append(timestamp)
            
            # Create bar data
            bar = {
                'symbol': symbol,
                'timestamp': timestamp,
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            }
            
            # Update unrealized P&L
            self._update_positions(bar['close'])
            
            # Generate signals from strategy
            signals = self.strategy_func(data.loc[:idx], self.get_portfolio_state())
            
            # Execute orders
            if signals:
                for order in signals:
                    self._execute_order(order, bar)
            
            # Record equity
            equity = self._calculate_equity(bar['close'])
            self.equity_curve.append(equity)
        
        # Calculate final metrics
        results = self._calculate_metrics()
        
        logging.info(f"Backtest complete. Final equity: {results['final_equity']:,.0f} IDR")
        logging.info(f"Total return: {results['total_return']:.2f}%")
        logging.info(f"Sharpe ratio: {results['sharpe_ratio']:.2f}")
        
        return results
    
    def _execute_order(self, order: Order, bar: Dict):
        """Execute order with slippage"""
        # Round to lot size
        order.quantity = self.commission_model.round_to_lot(order.quantity)
        
        if order.quantity == 0:
            return
        
        # Determine fill price (with slippage)
        if order.order_type == OrderType.MARKET:
            if order.side == OrderSide.BUY:
                fill_price = bar['high']  # Conservative: fill at high
            else:
                fill_price = bar['low']   # Conservative: fill at low
        else:
            fill_price = order.price or bar['close']
        
        fill_price = self.commission_model.round_to_tick(fill_price)
        
        # Check if we have enough capital (for buys)
        if order.side == OrderSide.BUY:
            value = fill_price * order.quantity
            commission = self.commission_model.calculate_commission(OrderSide.BUY, value)
            total_cost = value + commission
            
            if total_cost > self.capital:
                logging.warning(f"Insufficient capital for {order.symbol} buy")
                return
            
            # Execute buy
            self.capital -= total_cost
            
            if order.symbol in self.positions:
                # Add to existing position
                pos = self.positions[order.symbol]
                total_qty = pos.quantity + order.quantity
                pos.avg_price = (pos.avg_price * pos.quantity + fill_price * order.quantity) / total_qty
                pos.quantity = total_qty
            else:
                # Create new position
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_price=fill_price
                )
            
            # Record trade
            self.trades.append(Trade(
                symbol=order.symbol,
                side=OrderSide.BUY,
                quantity=order.quantity,
                price=fill_price,
                commission=commission,
                timestamp=bar['timestamp']
            ))
            
        else:  # SELL
            if order.symbol not in self.positions:
                logging.warning(f"No position to sell for {order.symbol}")
                return
            
            pos = self.positions[order.symbol]
            
            if order.quantity > pos.quantity:
                order.quantity = pos.quantity
            
            value = fill_price * order.quantity
            commission = self.commission_model.calculate_commission(OrderSide.SELL, value)
            proceeds = value - commission
            
            # Calculate P&L
            cost_basis = pos.avg_price * order.quantity
            pnl = proceeds - cost_basis
            
            # Execute sell
            self.capital += proceeds
            pos.quantity -= order.quantity
            pos.realized_pnl += pnl
            
            # Remove position if fully closed
            if pos.quantity == 0:
                del self.positions[order.symbol]
            
            # Record trade
            self.trades.append(Trade(
                symbol=order.symbol,
                side=OrderSide.SELL,
                quantity=order.quantity,
                price=fill_price,
                commission=commission,
                timestamp=bar['timestamp'],
                pnl=pnl
            ))
    
    def _update_positions(self, current_price: float):
        """Update unrealized P&L for open positions"""
        for pos in self.positions.values():
            market_value = current_price * pos.quantity
            cost_basis = pos.avg_price * pos.quantity
            pos.unrealized_pnl = market_value - cost_basis
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate total portfolio equity"""
        positions_value = sum(
            pos.quantity * current_price
            for pos in self.positions.values()
        )
        return self.capital + positions_value
    
    def _reset(self):
        """Reset backtest state"""
        self.capital = self.initial_capital
        self.positions = {}
        self.orders = []
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.timestamps = []
    
    def get_portfolio_state(self) -> Dict:
        """Get current portfolio state"""
        return {
            'capital': self.capital,
            'positions': self.positions.copy(),
            'equity': self.equity_curve[-1] if self.equity_curve else self.initial_capital
        }
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        equity = np.array(self.equity_curve)
        returns = np.diff(equity) / equity[:-1]
        
        final_equity = equity[-1]
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        
        # Sharpe ratio (annualized, assuming daily data)
        if len(returns) > 1 and returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe = 0.0
        
        # Maximum drawdown
        cummax = np.maximum.accumulate(equity)
        drawdown = (equity - cummax) / cummax
        max_drawdown = drawdown.min() * 100
        
        # Win rate
        winning_trades = [t for t in self.trades if t.pnl > 0]
        total_trades = len(self.trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        # Total commission paid
        total_commission = sum(t.commission for t in self.trades)
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'win_rate': win_rate,
            'total_commission': total_commission,
            'equity_curve': self.equity_curve,
            'trades': self.trades
        }


# Example strategy: Simple MA Crossover
def ma_crossover_strategy(data: pd.DataFrame, portfolio: Dict) -> List[Order]:
    """Simple moving average crossover strategy"""
    if len(data) < 50:
        return []
    
    # Calculate MAs
    data['ma20'] = data['close'].rolling(20).mean()
    data['ma50'] = data['close'].rolling(50).mean()
    
    # Get last two bars
    prev = data.iloc[-2]
    curr = data.iloc[-1]
    
    symbol = 'BBRI'  # Example
    orders = []
    
    # Golden cross: buy signal
    if prev['ma20'] <= prev['ma50'] and curr['ma20'] > curr['ma50']:
        # Buy with 20% of capital
        capital = portfolio['capital']
        position_size = capital * 0.2
        quantity = int(position_size / curr['close'])
        
        orders.append(Order(
            symbol=symbol,
            side=OrderSide.BUY,
            quantity=quantity,
            order_type=OrderType.MARKET
        ))
    
    # Death cross: sell signal
    elif prev['ma20'] >= prev['ma50'] and curr['ma20'] < curr['ma50']:
        # Sell all
        if symbol in portfolio['positions']:
            quantity = portfolio['positions'][symbol].quantity
            orders.append(Order(
                symbol=symbol,
                side=OrderSide.SELL,
                quantity=quantity,
                order_type=OrderType.MARKET
            ))
    
    return orders


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample data
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    np.random.seed(42)
    prices = 4500 + np.cumsum(np.random.randn(len(dates)) * 50)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, len(dates))
    })
    
    # Run backtest
    engine = BacktestEngine(initial_capital=100_000_000)
    engine.set_strategy(ma_crossover_strategy)
    results = engine.run(data, 'BBRI')
    
    print("\n=== Backtest Results ===")
    print(f"Initial Capital: {results['initial_capital']:,.0f} IDR")
    print(f"Final Equity: {results['final_equity']:,.0f} IDR")
    print(f"Total Return: {results['total_return']:.2f}%")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Win Rate: {results['win_rate']:.2f}%")
    print(f"Total Commission: {results['total_commission']:,.0f} IDR")
