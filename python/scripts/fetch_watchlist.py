#!/usr/bin/env python3
"""Fetch IDX stock watchlist data"""
import json
import sys
sys.path.insert(0, '.')

from python.data_sources.yfinance_client import YFinanceClient

symbols = sys.argv[1].split(',') if len(sys.argv) > 1 else ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'GOTO', 'ADRO', 'UNVR', 'ICBP']
client = YFinanceClient()
results = []
for sym in symbols:
    try:
        data = client.get_stock(sym)
        if 'change_pct' in data:
            data['changePct'] = data.pop('change_pct')
        results.append(data)
    except:
        pass
print(json.dumps(results))
