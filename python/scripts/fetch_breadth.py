#!/usr/bin/env python3
"""Fetch market breadth data"""
import json
import sys
sys.path.insert(0, '.')

try:
    from python.data_sources.yfinance_client import YFinanceClient
    client = YFinanceClient()
    data = client.get_market_breadth()
    print(json.dumps(data))
except Exception as e:
    print(json.dumps({'naik': 0, 'turun': 0, 'stagnan': 0, 'error': str(e)}))
