#!/usr/bin/env python3
"""
TradingView WebSocket Client for Real-Time Market Data
Protocol: ~m~{length}~m~{json}
"""
import json
import sys
import time
import threading

try:
    import websocket
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False


class TradingViewWS:
    """TradingView WebSocket client"""
    
    def __init__(self):
        self.ws = None
        self.running = False
        self.session_id = None
        self.symbols = []
        
    def on_message(self, ws, message):
        """Handle incoming message"""
        # Parse TradingView format: ~m~{length}~m~{json}
        if message.startswith("~m~"):
            try:
                parts = message.split("~m~")
                if len(parts) >= 3:
                    json_str = parts[2]
                    data = json.loads(json_str)
                    
                    # Handle different message types
                    if data.get("m") == "session_created":
                        self.session_id = data.get("p", [None])[0]
                        print(json.dumps({"status": "session_created", "session_id": self.session_id}))
                    
                    elif data.get("m") == "symbol_data":
                        print(json.dumps(data))
                    
                    elif data.get("m") == "q":
                        # Quote data
                        print(json.dumps(data))
                    
                    elif data.get("m") == "timescale_update":
                        print(json.dumps(data))
                    
            except Exception as e:
                pass
    
    def on_error(self, ws, error):
        print(json.dumps({"error": str(error)}))
    
    def on_close(self, ws, close_status_code, close_msg):
        print(json.dumps({"status": "disconnected"}))
    
    def on_open(self, ws):
        """Send auth and subscribe to symbols"""
        print(json.dumps({"status": "connected"}))
        
        # Step 1: Send auth token
        auth_msg = json.dumps({"m": "set_auth_token", "p": ["unauthorized_user_token"]})
        ws.send(f"~m~{len(auth_msg)}~m~{auth_msg}")
        
        # Step 2: Create chart session
        session_msg = json.dumps({"m": "chart_create_session", "p": ["", ""], "name": "qs"})
        ws.send(f"~m~{len(session_msg)}~m~{session_msg}")
        
        # Step 3: Subscribe to symbols
        for sym in self.symbols:
            sub_msg = json.dumps({
                "m": "subscribe",
                "params": {"symbol": sym}
            })
            ws.send(f"~m~{len(sub_msg)}~m~{sub_msg}")
    
    def connect(self, symbols):
        """Connect to TradingView WebSocket"""
        self.symbols = symbols
        self.running = True
        
        url = "wss://data.tradingview.com/socket.io/websocket"
        
        self.ws = websocket.WebSocketApp(
            url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Run in separate thread
        thread = threading.Thread(target=self.ws.run_forever)
        thread.daemon = True
        thread.start()
    
    def stop(self):
        """Stop the WebSocket connection"""
        self.running = False
        if self.ws:
            self.ws.close()


if __name__ == "__main__":
    if not WS_AVAILABLE:
        print(json.dumps({"error": "websocket-client not installed"}))
        sys.exit(1)
    
    symbols = sys.argv[1].split(',') if len(sys.argv) > 1 else ['XAUUSD']
    
    client = TradingViewWS()
    client.connect(symbols)
    
    # Run for 30 seconds then stop
    time.sleep(30)
    client.stop()
