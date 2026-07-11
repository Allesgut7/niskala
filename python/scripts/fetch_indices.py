#!/usr/bin/env python3
"""Fetch market index data using get_index()"""
import json
import sys
sys.path.insert(0, '.')

from python.data_sources.yfinance_client import YFinanceClient

client = YFinanceClient()
indices = ['^JKSE', '^N225', '^HSI', '^KS11', '^GSPC', '^IXIC', 'USDIDR=X']
results = []

for sym in indices:
    try:
        data = client.get_index(sym)
        results.append(data)
    except:
        pass

print(json.dumps(results))
