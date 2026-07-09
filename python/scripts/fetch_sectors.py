#!/usr/bin/env python3
"""Fetch sector performance data from Yahoo Finance - IDX 11 Sectors"""
import json
import sys
sys.path.insert(0, '.')

try:
    from python.data_sources.yfinance_client import YFinanceClient
    client = YFinanceClient()
    
    # IDX 11 sectors with representative stocks
    sectors = {
        'Teknologi': ['TLKM', 'GOTO', 'EXCL', 'ISAT', 'MTEL'],
        'Keuangan': ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'BRIS'],
        'Energi': ['ADRO', 'PGAS', 'MEDC', 'PTBA', 'ITMG'],
        'Industri': ['ASII', 'MDKA', 'UNTR', 'INTP', 'SMGR'],
        'Bahan Baku': ['INTP', 'SMGR', 'CPIN', 'TPIA', 'INKP'],
        'Infrastruktur': ['JSMR', 'WSKT', 'WIKA', 'PTPP', 'TLKM'],
        'Konsumen Primer': ['UNVR', 'ICBP', 'HMSP', 'GGRM', 'CLPI'],
        'Properti': ['PWON', 'BSDE', 'CTRA', 'SMRA', 'SMCI'],
        'Kesehatan': ['KLBF', 'MIKA', 'SIDO', 'HEAL', 'MIKA'],
        'Konsumen Non-Primer': ['MNCN', 'SCBD', 'GGRM', 'CPIN', 'HRUM'],
        'Transportasi': ['PTBA', 'INDY', 'HRUM', 'ADRO', 'ITMG']
    }
    
    results = []
    for sector_name, symbols in sectors.items():
        try:
            # Get average change for sector
            total_change = 0
            count = 0
            for sym in symbols:
                try:
                    data = client.get_stock(sym)
                    if data.get('changePct', 0) != 0:
                        total_change += data['changePct']
                        count += 1
                except:
                    pass
            
            avg_change = total_change / count if count > 0 else 0
            results.append({'name': sector_name, 'changePct': round(avg_change, 2)})
        except Exception as e:
            results.append({'name': sector_name, 'changePct': 0.0})
    
    # Sort by changePct descending (highest first)
    results.sort(key=lambda x: x['changePct'], reverse=True)
    
    print(json.dumps(results))
except Exception as e:
    print(json.dumps([]))
