# Niskala - Market Simulator
# Simulated market data for paper trading

import random
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
import math


@dataclass
class SimulatedQuote:
    """Simulated stock quote"""
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    timestamp: str
    bid_size: int = 0
    ask_size: int = 0
    change: float = 0.0
    change_pct: float = 0.0


@dataclass
class SimulatedOrderBook:
    """Simulated order book"""
    symbol: str
    bids: List[List[float]]  # [[price, size], ...]
    asks: List[List[float]]
    timestamp: str


# Default IDX stock universe with typical price ranges
DEFAULT_STOCKS = {
    'BBCA': {'base_price': 9500, 'volatility': 0.015, 'avg_volume': 50_000_000},
    'BBRI': {'base_price': 4800, 'volatility': 0.018, 'avg_volume': 40_000_000},
    'BMRI': {'base_price': 6200, 'volatility': 0.016, 'avg_volume': 35_000_000},
    'TLKM': {'base_price': 3800, 'volatility': 0.012, 'avg_volume': 30_000_000},
    'GOTO': {'base_price': 75, 'volatility': 0.025, 'avg_volume': 100_000_000},
    'ADRO': {'base_price': 2800, 'volatility': 0.020, 'avg_volume': 25_000_000},
    'UNVR': {'base_price': 4200, 'volatility': 0.010, 'avg_volume': 15_000_000},
    'ICBP': {'base_price': 12500, 'volatility': 0.012, 'avg_volume': 8_000_000},
    'ASII': {'base_price': 5100, 'volatility': 0.018, 'avg_volume': 20_000_000},
    'PGAS': {'base_price': 2100, 'volatility': 0.022, 'avg_volume': 22_000_000},
    'HMSP': {'base_price': 2200, 'volatility': 0.014, 'avg_volume': 18_000_000},
    'KLBF': {'base_price': 1500, 'volatility': 0.013, 'avg_volume': 12_000_000},
    'INTP': {'base_price': 4800, 'volatility': 0.017, 'avg_volume': 5_000_000},
    'SMGR': {'base_price': 4200, 'volatility': 0.019, 'avg_volume': 8_000_000},
    'BSDE': {'base_price': 1600, 'volatility': 0.016, 'avg_volume': 10_000_000},
}


class MarketSimulator:
    """Simulated market data generator for paper trading"""
    
    def __init__(self, stocks: Optional[Dict] = None):
        self.stocks = stocks or DEFAULT_STOCKS
        self._prices: Dict[str, float] = {}
        self._volumes: Dict[str, int] = {}
        self._last_update: Dict[str, float] = {}
        self._trends: Dict[str, float] = {}
        
        # Initialize prices
        for symbol, config in self.stocks.items():
            self._prices[symbol] = config['base_price']
            self._volumes[symbol] = config['avg_volume']
            self._trends[symbol] = 0.0
        
        logging.info(f"MarketSimulator initialized with {len(self.stocks)} stocks")
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within IDX trading hours (09:00-16:00 WIB)"""
        now = datetime.utcnow() + timedelta(hours=7)  # WIB = UTC+7
        market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Check if weekday (Mon-Fri)
        if now.weekday() >= 5:
            return False
        
        return market_open <= now <= market_close
    
    def get_quote(self, symbol: str) -> Optional[SimulatedQuote]:
        """Get simulated quote for a symbol"""
        if symbol not in self._prices:
            return None
        
        # Simulate price movement
        self._update_price(symbol)
        
        last = self._prices[symbol]
        config = self.stocks[symbol]
        
        # Generate bid/ask spread (0.1-0.3% spread)
        spread_pct = random.uniform(0.001, 0.003)
        spread = last * spread_pct
        
        bid = last - spread / 2
        ask = last + spread / 2
        
        # Round to tick size
        from ..quant.backtest_engine import IDXCommissionModel
        bid = IDXCommissionModel.round_to_tick(bid)
        ask = IDXCommissionModel.round_to_tick(ask)
        last = IDXCommissionModel.round_to_tick(last)
        
        # Calculate change from base price
        base_price = config['base_price']
        change = last - base_price
        change_pct = (change / base_price) * 100
        
        # Simulate volume
        volume = int(config['avg_volume'] * random.uniform(0.5, 1.5))
        
        return SimulatedQuote(
            symbol=symbol,
            bid=bid,
            ask=ask,
            last=last,
            volume=volume,
            timestamp=datetime.now().isoformat(),
            bid_size=random.randint(10, 100) * 100,
            ask_size=random.randint(10, 100) * 100,
            change=change,
            change_pct=change_pct,
        )
    
    def get_orderbook(self, symbol: str, depth: int = 5) -> Optional[SimulatedOrderBook]:
        """Get simulated order book"""
        if symbol not in self._prices:
            return None
        
        last = self._prices[symbol]
        from ..quant.backtest_engine import IDXCommissionModel
        
        bids = []
        asks = []
        
        for i in range(depth):
            # Bid levels (descending price)
            bid_price = IDXCommissionModel.round_to_tick(last - (i + 1) * 50)
            bid_size = random.randint(5, 50) * 100
            bids.append([bid_price, bid_size])
            
            # Ask levels (ascending price)
            ask_price = IDXCommissionModel.round_to_tick(last + (i + 1) * 50)
            ask_size = random.randint(5, 50) * 100
            asks.append([ask_price, ask_size])
        
        return SimulatedOrderBook(
            symbol=symbol,
            bids=bids,
            asks=asks,
            timestamp=datetime.now().isoformat(),
        )
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, SimulatedQuote]:
        """Get quotes for multiple symbols"""
        return {sym: self.get_quote(sym) for sym in symbols if self.get_quote(sym)}
    
    def get_all_quotes(self) -> Dict[str, SimulatedQuote]:
        """Get quotes for all stocks"""
        return {sym: self.get_quote(sym) for sym in self.stocks}
    
    def simulate_market_event(self, symbol: str, event_type: str = 'normal'):
        """Simulate a market event (spike, crash, etc.)
        
        Args:
            symbol: Stock symbol
            event_type: 'normal', 'spike', 'crash', 'volatile'
        """
        if symbol not in self._prices:
            return
        
        config = self.stocks[symbol]
        
        if event_type == 'spike':
            self._trends[symbol] = random.uniform(0.02, 0.05)
        elif event_type == 'crash':
            self._trends[symbol] = random.uniform(-0.05, -0.02)
        elif event_type == 'volatile':
            self._trends[symbol] = random.uniform(-0.03, 0.03)
        else:
            self._trends[symbol] = 0.0
    
    def _update_price(self, symbol: str):
        """Update simulated price with random walk"""
        if symbol not in self._prices:
            return
        
        config = self.stocks[symbol]
        volatility = config['volatility']
        
        # Random walk with mean reversion
        drift = -0.1 * (self._prices[symbol] - config['base_price']) / config['base_price']
        shock = random.gauss(0, volatility)
        trend = self._trends.get(symbol, 0)
        
        # Calculate new price
        ret = drift + shock + trend
        self._prices[symbol] *= (1 + ret)
        
        # Ensure price stays positive and within reasonable bounds
        min_price = config['base_price'] * 0.3
        max_price = config['base_price'] * 3.0
        self._prices[symbol] = max(min_price, min(max_price, self._prices[symbol]))
        
        # Decay trend
        self._trends[symbol] *= 0.95
        
        self._last_update[symbol] = time.time()
    
    def set_price(self, symbol: str, price: float):
        """Manually set price for a symbol"""
        if symbol in self._prices:
            self._prices[symbol] = price
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current simulated price"""
        if symbol in self._prices:
            self._update_price(symbol)
            return self._prices[symbol]
        return None
    
    def get_market_status(self) -> Dict:
        """Get simulated market status"""
        return {
            'is_open': self.is_trading_hours(),
            'stocks_count': len(self.stocks),
            'last_prices': dict(self._prices),
        }
