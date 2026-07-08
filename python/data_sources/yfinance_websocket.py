"""
YFinance WebSocket Client for Real-Time Market Data
Provides live streaming data from Yahoo Finance
"""

import json
import sys
import time
import threading
from typing import Callable, Dict, List, Optional

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False


class YFinanceWebSocket:
    """
    Real-time market data streaming using yfinance.
    Falls back to polling if WebSocket is not available.
    """
    
    def __init__(self):
        self.symbols: List[str] = []
        self.callbacks: Dict[str, Callable] = {}
        self.running = False
        self.poll_interval = 5  # seconds
        
    def connect(self, symbols: List[str]):
        """Connect to market data stream"""
        self.symbols = symbols
        self.running = True
        
    def subscribe(self, symbol: str, callback: Callable):
        """Subscribe to symbol updates"""
        self.callbacks[symbol] = callback
    
    def unsubscribe(self, symbol: str):
        """Unsubscribe from symbol updates"""
        if symbol in self.callbacks:
            del self.callbacks[symbol]
    
    def run(self):
        """Start polling for real-time data"""
        if not YF_AVAILABLE:
            print(json.dumps({"error": "yfinance not installed"}))
            return
            
        while self.running:
            for symbol in self.symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.fast_info
                    
                    data = {
                        "symbol": symbol,
                        "price": float(info.last_price) if hasattr(info, 'last_price') else 0,
                        "change": float(info.last_price - info.previous_close) if hasattr(info, 'last_price') and hasattr(info, 'previous_close') else 0,
                        "changePct": float((info.last_price - info.previous_close) / info.previous_close * 100) if hasattr(info, 'last_price') and hasattr(info, 'previous_close') and info.previous_close > 0 else 0,
                        "volume": int(info.last_volume) if hasattr(info, 'last_volume') else 0,
                        "high": float(info.day_high) if hasattr(info, 'day_high') else 0,
                        "low": float(info.day_low) if hasattr(info, 'day_low') else 0,
                        "open": float(info.open) if hasattr(info, 'open') else 0,
                        "timestamp": int(time.time())
                    }
                    
                    # Call callback if registered
                    if symbol in self.callbacks:
                        self.callbacks[symbol](data)
                    
                    # Output as JSON for QProcess
                    print(json.dumps(data))
                    sys.stdout.flush()
                    
                except Exception as e:
                    error_data = {
                        "symbol": symbol,
                        "error": str(e),
                        "timestamp": int(time.time())
                    }
                    print(json.dumps(error_data))
                    sys.stdout.flush()
            
            time.sleep(self.poll_interval)
    
    def stop(self):
        """Stop the data stream"""
        self.running = False


def get_market_data(symbol: str) -> dict:
    """Get current market data for a symbol"""
    if not YF_AVAILABLE:
        return {"error": "yfinance not installed"}
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        
        return {
            "symbol": symbol,
            "price": float(info.last_price) if hasattr(info, 'last_price') else 0,
            "change": float(info.last_price - info.previous_close) if hasattr(info, 'last_price') and hasattr(info, 'previous_close') else 0,
            "changePct": float((info.last_price - info.previous_close) / info.previous_close * 100) if hasattr(info, 'last_price') and hasattr(info, 'previous_close') and info.previous_close > 0 else 0,
            "volume": int(info.last_volume) if hasattr(info, 'last_volume') else 0,
            "high": float(info.day_high) if hasattr(info, 'day_high') else 0,
            "low": float(info.day_low) if hasattr(info, 'day_low') else 0,
            "open": float(info.open) if hasattr(info, 'open') else 0,
            "timestamp": int(time.time())
        }
    except Exception as e:
        return {"error": str(e)}


def get_historical_data(symbol: str, period: str = "1d", interval: str = "1m") -> dict:
    """Get historical OHLCV data"""
    if not YF_AVAILABLE:
        return {"error": "yfinance not installed"}
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        data = []
        for index, row in df.iterrows():
            data.append({
                "timestamp": int(index.timestamp()),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {"symbol": symbol, "data": data}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Run as standalone WebSocket server
    ws = YFinanceWebSocket()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        symbols = sys.argv[1].split(',')
        ws.connect(symbols)
        ws.run()
    else:
        print(json.dumps({"error": "No symbols provided"}))
