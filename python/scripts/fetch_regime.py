#!/usr/bin/env python3
"""Fetch AI market regime"""
import json
import sys
sys.path.insert(0, '.')

try:
    from python.data_sources.yfinance_client import YFinanceClient
    client = YFinanceClient()
    data = client.get_index('^JKSE')
    regime = 'BULL' if data.get('changePct', 0) > 0 else 'BEAR'
    confidence = min(90, max(50, 70 + abs(data.get('changePct', 0)) * 2))
    result = {
        'regime': regime,
        'confidence': int(confidence),
        'analysis': f'IHSG change: {data.get("changePct", 0):.2f}%. Market regime: {regime}.'
    }
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'regime': 'NEUTRAL', 'confidence': 50, 'analysis': 'Insufficient data'}))
