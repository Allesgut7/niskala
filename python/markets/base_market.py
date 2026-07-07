# Niskala - Base Market Configuration
# Abstract market config for multi-market support

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import time
import json
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommissionModel:
    """Market-specific commission model"""
    buy_commission: float
    sell_commission: float
    transaction_tax: float
    min_commission: float = 0
    
    def calculate(self, side: str, value: float) -> float:
        """Calculate commission for trade"""
        if side == 'buy':
            commission = value * self.buy_commission
        else:
            commission = value * (self.sell_commission + self.transaction_tax)
        return max(commission, self.min_commission)


@dataclass
class LotSize:
    """Market-specific lot size rules"""
    default_lot: int = 100
    price_ranges: Optional[Dict] = None
    
    def round_to_lot(self, quantity: int) -> int:
        """Round quantity to valid lot size"""
        return (quantity // self.default_lot) * self.default_lot


@dataclass
class TickSize:
    """Market-specific tick size rules"""
    rules: List[Dict] = field(default_factory=list)
    
    def round_to_tick(self, price: float) -> float:
        """Round price to valid tick size"""
        for rule in self.rules:
            if rule['min'] <= price < rule['max']:
                tick = rule['tick']
                return round(price / tick) * tick
        # Default: round to nearest integer
        return round(price)


@dataclass
class TradingHours:
    """Market trading hours"""
    timezone: str
    open_time: str  # "HH:MM"
    close_time: str  # "HH:MM"
    lunch_start: Optional[str] = None
    lunch_end: Optional[str] = None
    
    def is_open(self) -> bool:
        """Check if market is currently open"""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        
        try:
            tz = ZoneInfo(self.timezone)
            now = datetime.now(tz)
            
            # Check if weekday
            if now.weekday() >= 5:  # Saturday or Sunday
                return False
            
            current_time = now.time()
            open_time = time.fromisoformat(self.open_time)
            close_time = time.fromisoformat(self.close_time)
            
            if not (open_time <= current_time <= close_time):
                return False
            
            # Check lunch break
            if self.lunch_start and self.lunch_end:
                lunch_start = time.fromisoformat(self.lunch_start)
                lunch_end = time.fromisoformat(self.lunch_end)
                if lunch_start <= current_time <= lunch_end:
                    return False
            
            return True
        except Exception:
            return False


@dataclass
class MarketConfig:
    """Complete market configuration"""
    code: str
    name: str
    country: str
    currency: str
    currency_symbol: str
    ticker_suffix: str
    index_symbol: str
    index_name: str
    commission: CommissionModel
    lot_size: LotSize
    tick_size: TickSize
    trading_hours: TradingHours
    initial_capital_default: float
    sector_classification: Dict = field(default_factory=dict)
    top_stocks: List[Dict] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    risk_free_rate: float = 0.0
    
    def get_ticker(self, symbol: str) -> str:
        """Get full ticker with suffix"""
        if symbol.endswith(self.ticker_suffix):
            return symbol
        return f"{symbol}{self.ticker_suffix}"
    
    def strip_suffix(self, ticker: str) -> str:
        """Remove suffix from ticker"""
        return ticker.replace(self.ticker_suffix, '')
    
    @classmethod
    def from_json(cls, json_path: str) -> 'MarketConfig':
        """Load market config from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            code=data['code'],
            name=data['name'],
            country=data['country'],
            currency=data['currency'],
            currency_symbol=data['currency_symbol'],
            ticker_suffix=data['ticker_suffix'],
            index_symbol=data['index_symbol'],
            index_name=data['index_name'],
            commission=CommissionModel(**data['commission']),
            lot_size=LotSize(**data['lot_size']),
            tick_size=TickSize(**data['tick_size']),
            trading_hours=TradingHours(**data['trading_hours']),
            initial_capital_default=data['initial_capital_default'],
            sector_classification=data.get('sector_classification', {}),
            top_stocks=data.get('top_stocks', []),
            data_sources=data.get('data_sources', []),
            risk_free_rate=data.get('risk_free_rate', 0.0),
        )
    
    def to_json(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            'code': self.code,
            'name': self.name,
            'country': self.country,
            'currency': self.currency,
            'currency_symbol': self.currency_symbol,
            'ticker_suffix': self.ticker_suffix,
            'index_symbol': self.index_symbol,
            'index_name': self.index_name,
            'commission': {
                'buy_commission': self.commission.buy_commission,
                'sell_commission': self.commission.sell_commission,
                'transaction_tax': self.commission.transaction_tax,
                'min_commission': self.commission.min_commission,
            },
            'lot_size': {'default_lot': self.lot_size.default_lot},
            'tick_size': {'rules': self.tick_size.rules},
            'trading_hours': {
                'timezone': self.trading_hours.timezone,
                'open_time': self.trading_hours.open_time,
                'close_time': self.trading_hours.close_time,
                'lunch_start': self.trading_hours.lunch_start,
                'lunch_end': self.trading_hours.lunch_end,
            },
            'initial_capital_default': self.initial_capital_default,
            'sector_classification': self.sector_classification,
            'top_stocks': self.top_stocks,
            'data_sources': self.data_sources,
            'risk_free_rate': self.risk_free_rate,
        }
