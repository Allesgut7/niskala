# Niskala - WebSocket Real-Time Streaming
# Version: 1.0.0

import asyncio
import websockets
import json
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime
import logging


class MarketDataStream:
    """WebSocket-based real-time market data stream
    
    Streams market data from IDX to the TUI frontend.
    When no real IDX WebSocket is available, uses polling as fallback.
    """
    
    def __init__(self, update_callback: Optional[Callable] = None):
        """
        Args:
            update_callback: Called with (symbol, data_dict) on new data
        """
        self.callback = update_callback
        self.connected = False
        self.subscriptions: List[str] = []
        self._running = False
        self._ws = None
        
    async def connect(self, url: str = "wss://streaming.example.com"):
        """Connect to WebSocket server"""
        try:
            self._ws = await websockets.connect(url)
            self.connected = True
            logging.info(f"Connected to WebSocket: {url}")
        except Exception as e:
            logging.warning(f"WebSocket connection failed: {e}, using polling fallback")
            self.connected = False
    
    async def subscribe(self, symbols: List[str]):
        """Subscribe to stock symbols"""
        self.subscriptions.extend(symbols)
        
        if self.connected and self._ws:
            msg = json.dumps({
                'action': 'subscribe',
                'symbols': symbols
            })
            await self._ws.send(msg)
            logging.info(f"Subscribed to: {symbols}")
    
    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols"""
        for sym in symbols:
            if sym in self.subscriptions:
                self.subscriptions.remove(sym)
        
        if self.connected and self._ws:
            msg = json.dumps({
                'action': 'unsubscribe',
                'symbols': symbols
            })
            await self._ws.send(msg)
    
    async def start(self):
        """Start receiving data"""
        self._running = True
        
        if self.connected and self._ws:
            await self._listen_websocket()
        else:
            await self._listen_polling()
    
    async def stop(self):
        """Stop streaming"""
        self._running = False
        if self._ws:
            await self._ws.close()
    
    async def _listen_websocket(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self._ws:
                if not self._running:
                    break
                
                try:
                    data = json.loads(message)
                    symbol = data.get('symbol', '')
                    
                    if self.callback and symbol:
                        self.callback(symbol, data)
                        
                except json.JSONDecodeError:
                    continue
                    
        except websockets.ConnectionClosed:
            logging.warning("WebSocket connection closed")
            self.connected = False
    
    async def _listen_polling(self):
        """Fallback polling-based data collection"""
        import yfinance as yf
        
        logging.info("Starting polling-based data collection")
        
        while self._running:
            for symbol in self.subscriptions:
                try:
                    ticker = yf.Ticker(f"{symbol}.JK")
                    info = ticker.fast_info
                    
                    data = {
                        'symbol': symbol,
                        'price': float(info.last_price) if hasattr(info, 'last_price') else 0,
                        'volume': int(info.last_volume) if hasattr(info, 'last_volume') else 0,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if self.callback:
                        self.callback(symbol, data)
                        
                except Exception as e:
                    logging.debug(f"Polling error for {symbol}: {e}")
            
            # Wait before next poll
            await asyncio.sleep(1)


class OrderBookStream:
    """Real-time order book data stream"""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        self.callback = update_callback
        self._running = False
    
    async def start(self, symbol: str):
        """Start order book stream for a symbol"""
        self._running = True
        
        logging.info(f"Order book stream started for {symbol}")
        
        # Placeholder - in production, connect to real IDX order book feed
        while self._running:
            await asyncio.sleep(0.5)
    
    async def stop(self):
        self._running = False


class RunningTradeStream:
    """Real-time running trade data stream"""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        self.callback = update_callback
        self._running = False
    
    async def start(self, symbols: List[str] = None):
        """Start running trade stream"""
        self._running = True
        
        logging.info("Running trade stream started")
        
        # Placeholder - in production, connect to real IDX trade feed
        while self._running:
            await asyncio.sleep(0.1)
    
    async def stop(self):
        self._running = False


# Test
if __name__ == '__main__':
    def on_update(symbol, data):
        print(f"[{symbol}] {data}")
    
    stream = MarketDataStream(update_callback=on_update)
    stream.subscriptions = ['BBCA', 'BBRI', 'TLKM']
    
    async def run():
        print("Starting market data stream...")
        await stream.start()
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nStopped.")
