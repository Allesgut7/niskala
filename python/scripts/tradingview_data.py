#!/usr/bin/env python3
"""Fetch OHLCV data from TradingView WebSocket"""
from tradingview_websocket import TradingViewWebSocket
import json
import sys
import threading
import time

symbol = sys.argv[1] if len(sys.argv) > 1 else 'XAUUSD'
timeframe = sys.argv[2] if len(sys.argv) > 2 else '1D'
candles = int(sys.argv[3]) if len(sys.argv) > 3 else 50

try:
    ws = TradingViewWebSocket(symbol, timeframe, candles)
    ws.connect()
    
    data_received = []
    
    def run_ws():
        ws.run()
    
    thread = threading.Thread(target=run_ws)
    thread.daemon = True
    thread.start()
    
    for i in range(30):
        time.sleep(1)
        if ws.result_data:
            for item in ws.result_data:
                data_received.append({
                    'timestamp': int(item['v'][0]),
                    'open': item['v'][1],
                    'high': item['v'][2],
                    'low': item['v'][3],
                    'close': item['v'][4],
                    'volume': int(item['v'][5])
                })
            break
    
    if data_received:
        print(json.dumps(data_received))
    else:
        print(json.dumps([]))
        
except Exception as e:
    print(json.dumps({'error': str(e)}))
