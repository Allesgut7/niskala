#!/usr/bin/env python3
"""Fetch OHLCV data from TradingView WebSocket with yfinance fallback"""
import json
import os
import sys
import threading
import time

symbol = sys.argv[1] if len(sys.argv) > 1 else 'XAUUSD'
timeframe = sys.argv[2] if len(sys.argv) > 2 else 'D'
candles = int(sys.argv[3]) if len(sys.argv) > 3 else 50

SYMBOL_MAP = {
    'JKSE': '^JKSE', 'IXIC': '^IXIC', 'GSPC': '^GSPC',
    'N225': '^N225', 'HSI': '^HSI', 'KS11': '^KS11',
    'STI': '^STI', 'DJI': '^DJI', 'XAUUSD': 'GC=F',
    'XAGUSD': 'SI=F', 'USOIL': 'CL=F', 'UKOIL': 'BZ=F',
    'USDIDR': 'USDIDR=X', 'EURUSD': 'EURUSD=X',
}

def candles_to_period(c, interval):
    days_per_candle = {
        '1': 1/1440, '5': 5/1440, '15': 15/1440, '30': 30/1440,
        '60': 1/24, 'D': 1, '1D': 1, 'W': 7, '1W': 7, 'M': 30, '1M': 30,
    }
    d = c * days_per_candle.get(interval, 1)
    if d <= 7: return '1mo'
    if d <= 31: return '3mo'
    if d <= 93: return '6mo'
    if d <= 186: return '1y'
    return 'max'

# Try TradingView first (redirect stdout at OS level to suppress lib noise)
data_received = []
saved_fd1 = os.dup(1)
devnull_fd = os.open(os.devnull, os.O_WRONLY)

try:
    from tradingview_websocket import TradingViewWebSocket

    os.dup2(devnull_fd, 1)

    ws = TradingViewWebSocket(symbol, timeframe, candles)
    ws.connect()

    def run_ws():
        try:
            ws.run()
        except Exception:
            pass

    thread = threading.Thread(target=run_ws)
    thread.daemon = True
    thread.start()

    for i in range(15):
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

    try:
        ws.disconnect()
    except Exception:
        pass
except Exception:
    pass
finally:
    os.dup2(saved_fd1, 1)
    os.close(devnull_fd)
    os.close(saved_fd1)

if data_received:
    print(json.dumps(data_received))
    sys.exit(0)

# Fallback: Gunakan yfinance (dengan timeout thread)
result = []

def fetch_yfinance():
    global result
    try:
        sys.path.insert(0, '.')
        from python.data_sources.yfinance_client import YFinanceClient

        client = YFinanceClient()

        yf_symbol = SYMBOL_MAP.get(symbol, symbol)
        if not yf_symbol.startswith('^') and '=' not in yf_symbol and '.JK' not in yf_symbol:
            yf_symbol = f"{yf_symbol}.JK"

        interval_map = {
            '1': '1m', '5': '5m', '15': '15m', '30': '30m',
            '60': '1h', 'D': '1d', '1D': '1d', 'W': '1wk', '1W': '1wk',
            'M': '1mo', '1M': '1mo',
        }
        yf_interval = interval_map.get(timeframe, '1d')
        periods = [candles_to_period(candles, timeframe)]
        if periods[0] in ('1mo', '2mo', '3mo'):
            periods.append('5d')
        if periods[0] in ('2mo', '3mo', '6mo'):
            periods.append('1mo')

        for period in periods:
            client = YFinanceClient()
            hist = client.get_history(yf_symbol, period, yf_interval)
            if not hist.empty:
                break

        if not hist.empty:
            result = []
            for index, row in hist.iterrows():
                result.append({
                    'timestamp': int(index.timestamp()),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
    except Exception:
        pass

yf_thread = threading.Thread(target=fetch_yfinance)
yf_thread.daemon = True
yf_thread.start()
yf_thread.join(timeout=15)

if result:
    print(json.dumps(result))
else:
    print(json.dumps([]))
