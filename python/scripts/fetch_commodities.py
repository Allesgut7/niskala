#!/usr/bin/env python3
"""Fetch commodity data using get_commodity()"""
import json
import sys
sys.path.insert(0, '.')

from python.data_sources.yfinance_client import YFinanceClient

client = YFinanceClient()
commodities = ['GC=F', 'CL=F', 'MTXF=F', 'NI=F', 'HG=F', 'NG=F']
results = []

for sym in commodities:
    try:
        data = client.get_commodity(sym)
        results.append(data)
    except:
        pass

print(json.dumps(results))
