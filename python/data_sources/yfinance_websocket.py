#!/usr/bin/env python3
"""
Yahoo Finance WebSocket Client for Real-Time Market Data
Uses yliveticker for real-time streaming via Yahoo Finance WebSocket
"""
import json
import sys
import yliveticker


class YFinanceWebSocket:
    """Real-time market data streaming using yliveticker WebSocket"""
    
    def __init__(self):
        self.symbols = []
        self.running = False
        
    def connect(self, symbols):
        """Connect to market data stream"""
        self.symbols = symbols
        self.running = True
        
    def on_msg(self, ws, msg):
        """Handle incoming WebSocket message from yliveticker"""
        output = {
            "symbol": msg.get("id", ""),
            "price": msg.get("price", 0),
            "change": msg.get("change", 0),
            "changePct": msg.get("changePercent", 0),
            "volume": msg.get("dayVolume", 0),
            "high": msg.get("dayHigh", 0),
            "low": msg.get("dayLow", 0),
            "open": msg.get("openPrice", 0),
            "timestamp": int(msg.get("timestamp", 0) / 1000),
        }
        print(json.dumps(output))
        sys.stdout.flush()
        
    def run(self):
        """Start real-time streaming"""
        yliveticker.YLiveTicker(
            on_ticker=self.on_msg,
            ticker_names=self.symbols
        )
        
    def stop(self):
        """Stop the data stream"""
        self.running = False


if __name__ == "__main__":
    symbols = sys.argv[1].split(',') if len(sys.argv) > 1 else ['^JKSE']
    ws = YFinanceWebSocket()
    ws.connect(symbols)
    ws.run()
