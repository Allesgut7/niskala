# Niskala - Market Registry
# Registry for all supported markets

import os
import json
from typing import Dict, List, Optional
from .base_market import MarketConfig, CommissionModel, LotSize, TickSize, TradingHours
import logging

logger = logging.getLogger(__name__)


class MarketRegistry:
    """Registry for all supported markets"""
    
    def __init__(self, configs_path: Optional[str] = None):
        self.markets: Dict[str, MarketConfig] = {}
        self.default_market = 'IDX'
        
        if configs_path is None:
            configs_path = os.path.join(os.path.dirname(__file__), 'configs')
        
        self._load_all_markets(configs_path)
        logger.info(f"MarketRegistry initialized with {len(self.markets)} markets")
    
    def _load_all_markets(self, configs_path: str):
        """Load all market configurations from JSON files"""
        if not os.path.exists(configs_path):
            logger.warning(f"Configs path not found: {configs_path}")
            return
        
        for filename in os.listdir(configs_path):
            if filename.endswith('.json'):
                filepath = os.path.join(configs_path, filename)
                try:
                    config = MarketConfig.from_json(filepath)
                    self.markets[config.code] = config
                    logger.info(f"Loaded market: {config.code} ({config.name})")
                except Exception as e:
                    logger.error(f"Failed to load market config {filename}: {e}")
    
    def get_market(self, code: str) -> Optional[MarketConfig]:
        """Get market config by code"""
        return self.markets.get(code)
    
    def get_default_market(self) -> MarketConfig:
        """Get default market (IDX)"""
        return self.markets.get(self.default_market)
    
    def list_markets(self) -> List[MarketConfig]:
        """List all supported markets"""
        return list(self.markets.values())
    
    def list_market_codes(self) -> List[str]:
        """List all market codes"""
        return list(self.markets.keys())
    
    def get_market_by_country(self, country: str) -> Optional[MarketConfig]:
        """Get market by country code"""
        for market in self.markets.values():
            if market.country == country:
                return market
        return None
    
    def get_ticker(self, symbol: str, market_code: Optional[str] = None) -> str:
        """Get full ticker with suffix for market"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.get_ticker(symbol)
        return symbol
    
    def strip_suffix(self, ticker: str, market_code: Optional[str] = None) -> str:
        """Remove suffix from ticker"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.strip_suffix(ticker)
        return ticker
    
    def get_commission(self, market_code: Optional[str] = None) -> CommissionModel:
        """Get commission model for market"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.commission
        return CommissionModel(buy_commission=0.0015, sell_commission=0.0025, transaction_tax=0.001)
    
    def get_trading_hours(self, market_code: Optional[str] = None) -> TradingHours:
        """Get trading hours for market"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.trading_hours
        return TradingHours(timezone='Asia/Jakarta', open_time='09:00', close_time='16:00')
    
    def round_to_lot(self, quantity: int, market_code: Optional[str] = None) -> int:
        """Round quantity to valid lot size"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.lot_size.round_to_lot(quantity)
        return (quantity // 100) * 100
    
    def round_to_tick(self, price: float, market_code: Optional[str] = None) -> float:
        """Round price to valid tick size"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.tick_size.round_to_tick(price)
        return round(price)
    
    def get_top_stocks(self, market_code: Optional[str] = None) -> List[Dict]:
        """Get default watchlist for market"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.top_stocks
        return []
    
    def get_initial_capital(self, market_code: Optional[str] = None) -> float:
        """Get default initial capital for market"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.initial_capital_default
        return 100_000_000
    
    def is_market_open(self, market_code: Optional[str] = None) -> bool:
        """Check if market is currently open"""
        market = self.get_market(market_code or self.default_market)
        if market:
            return market.trading_hours.is_open()
        return False
    
    def register_market(self, market: MarketConfig):
        """Register a custom market"""
        self.markets[market.code] = market
        logger.info(f"Market registered: {market.code}")
    
    def to_dict(self) -> Dict:
        """Export all markets as dict"""
        return {code: market.to_json() for code, market in self.markets.items()}


# Singleton
_registry: Optional[MarketRegistry] = None


def get_market_registry() -> MarketRegistry:
    """Get global market registry instance"""
    global _registry
    if _registry is None:
        _registry = MarketRegistry()
    return _registry
