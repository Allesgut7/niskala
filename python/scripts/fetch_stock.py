#!/usr/bin/env python3
"""Fetch single stock data from Yahoo Finance"""
import json
import sys
sys.path.insert(0, '.')

from python.data_sources.yfinance_client import YFinanceClient

symbol = sys.argv[1] if len(sys.argv) > 1 else 'BBCA'
client = YFinanceClient()
data = client.get_stock(symbol)
print(json.dumps(data))
