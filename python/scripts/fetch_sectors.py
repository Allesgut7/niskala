#!/usr/bin/env python3
"""Fetch sector performance data"""
import json
import sys
sys.path.insert(0, '.')

try:
    from python.data_sources.yfinance_client import YFinanceClient
    client = YFinanceClient()
    sectors = [
        {'name': 'Teknologi', 'changePct': 0.0},
        {'name': 'Keuangan', 'changePct': 0.0},
        {'name': 'Energi', 'changePct': 0.0},
        {'name': 'Industri', 'changePct': 0.0},
        {'name': 'Consumer', 'changePct': 0.0},
    ]
    print(json.dumps(sectors))
except Exception as e:
    print(json.dumps([]))
