# Niskala - YFinance Data Provider
# Version: 1.0.0

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class YFinanceClient:
    """Yahoo Finance data provider for IDX stocks"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 5  # seconds
        
    def get_stock(self, symbol: str) -> Dict:
        """Get stock data for IDX ticker
        
        Args:
            symbol: Stock symbol (e.g., 'BBCA', 'BBRI')
            
        Returns:
            Dict with price, change, volume, etc.
        """
        try:
            # Add .JK suffix for IDX stocks
            ticker_symbol = f"{symbol}.JK" if not symbol.endswith('.JK') else symbol
            ticker = yf.Ticker(ticker_symbol)
            
            # Get current info
            info = ticker.info
            
            # Get history for change calculation
            hist = ticker.history(period='2d')
            
            if hist.empty:
                return self._empty_stock_data(symbol)
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - prev_price
            change_pct = (change / prev_price * 100) if prev_price > 0 else 0.0
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': float(current_price),
                'change': float(change),
                'change_pct': float(change_pct),
                'volume': int(hist['Volume'].iloc[-1]),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'pe_ratio': info.get('trailingPE', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return self._empty_stock_data(symbol)
    
    def get_stocks_batch(self, symbols: List[str]) -> List[Dict]:
        """Get multiple stocks at once
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of stock data dicts
        """
        return [self.get_stock(symbol) for symbol in symbols]
    
    def get_history(self, symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Get historical data
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker_symbol = f"{symbol}.JK" if not symbol.endswith('.JK') else symbol
            ticker = yf.Ticker(ticker_symbol)
            return ticker.history(period=period, interval=interval)
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_index(self, index_symbol: str) -> Dict:
        """Get index data (IHSG, S&P 500, etc.)
        
        Args:
            index_symbol: Index symbol (^JKSE for IHSG, ^GSPC for S&P 500)
            
        Returns:
            Dict with index data
        """
        try:
            ticker = yf.Ticker(index_symbol)
            hist = ticker.history(period='2d')
            
            if hist.empty:
                return self._empty_stock_data(index_symbol)
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - prev_price
            change_pct = (change / prev_price * 100) if prev_price > 0 else 0.0
            
            return {
                'symbol': index_symbol,
                'name': self._get_index_name(index_symbol),
                'price': float(current_price),
                'change': float(change),
                'change_pct': float(change_pct),
                'volume': int(hist['Volume'].iloc[-1]),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching index {index_symbol}: {e}")
            return self._empty_stock_data(index_symbol)
    
    def get_commodity(self, commodity_symbol: str) -> Dict:
        """Get commodity price
        
        Args:
            commodity_symbol: Commodity symbol (GC=F for Gold, CL=F for Oil)
            
        Returns:
            Dict with commodity data
        """
        return self.get_index(commodity_symbol)
    
    def get_forex(self, forex_symbol: str) -> Dict:
        """Get forex rate
        
        Args:
            forex_symbol: Forex symbol (USDIDR=X, EURUSD=X)
            
        Returns:
            Dict with forex data
        """
        return self.get_index(forex_symbol)
    
    def _empty_stock_data(self, symbol: str) -> Dict:
        """Return empty stock data structure"""
        return {
            'symbol': symbol,
            'name': symbol,
            'price': 0.0,
            'change': 0.0,
            'change_pct': 0.0,
            'volume': 0,
            'market_cap': 0,
            'sector': 'Unknown',
            'pe_ratio': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_index_name(self, symbol: str) -> str:
        """Get human-readable index name"""
        index_names = {
            '^JKSE': 'IHSG',
            '^GSPC': 'S&P 500',
            '^N225': 'Nikkei 225',
            '^HSI': 'Hang Seng',
            '^STI': 'STI',
            'GC=F': 'Gold',
            'CL=F': 'Crude Oil',
            'SI=F': 'Silver',
            'USDIDR=X': 'USD/IDR',
            'EURUSD=X': 'EUR/USD'
        }
        return index_names.get(symbol, symbol)


# Test function
if __name__ == '__main__':
    client = YFinanceClient()
    
    # Test single stock
    print("Testing BBCA...")
    bbca = client.get_stock('BBCA')
    print(f"{bbca['symbol']}: {bbca['price']} ({bbca['change_pct']:.2f}%)")
    
    # Test batch
    print("\nTesting batch...")
    stocks = client.get_stocks_batch(['BBCA', 'BBRI', 'BMRI'])
    for stock in stocks:
        print(f"{stock['symbol']}: {stock['price']} ({stock['change_pct']:.2f}%)")
    
    # Test index
    print("\nTesting IHSG...")
    ihsg = client.get_index('^JKSE')
    print(f"{ihsg['name']}: {ihsg['price']} ({ihsg['change_pct']:.2f}%)")
