#!/usr/bin/env python3
"""Fetch sector performance data from Yahoo Finance"""
import json
import sys
sys.path.insert(0, '.')

try:
    from python.data_sources.yfinance_client import YFinanceClient
    client = YFinanceClient()
    
    # Get sector data from major IDX stocks
    sectors = {
        'Teknologi': ['TLKM', 'GOTO', 'EXCL'],
        'Keuangan': ['BBCA', 'BBRI', 'BMRI', 'BBNI'],
        'Energi': ['ADRO', 'PGAS'],
        'Industri': ['ASII', 'MDKA'],
        'Consumer': ['UNVR', 'ICBP']
    }
    
    results = []
    for sector_name, symbols in sectors.items():
        try:
            # Get average change for sector
            total_change = 0
            count = 0
            for sym in symbols:
                data = client.get_stock(sym)
                if data.get('changePct', 0) != 0:
                    total_change += data['changePct']
                    count += 1
            avg_change = total_change / count if count > 0 else 0
            results.append({'name': sector_name, 'changePct': round(avg_change, 2)})
        except:
            results.append({'name': sector_name, 'changePct': 0.0})
    
    print(json.dumps(results))
except Exception as e:
    print(json.dumps([]))
