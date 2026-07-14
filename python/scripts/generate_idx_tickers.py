#!/usr/bin/env python3
"""Generate/update idx_tickers.json from IDX API or CSV fallback"""

import csv
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(PROJECT_ROOT, '..', 'config', 'idx_tickers.json')
CSV_PATH = os.path.join(PROJECT_ROOT, '..', '..', 'indobert-financial', 'data', 'raw', 'daftar_saham.csv')


def fetch_from_idx_api():
    """Fetch stock list from IDX BEI API"""
    try:
        sys.path.insert(0, PROJECT_ROOT)
        from data_sources.idx_bei_client import IdxBeiClient
        client = IdxBeiClient()
        stocks = client.get_stock_list()
        if stocks:
            tickers = sorted([f"{s['Code']}.JK" for s in stocks if s.get('Code')])
            return tickers
    except Exception as e:
        print(f"IDX API fetch failed: {e}")
    return None


def fetch_from_csv():
    """Fallback: read from local CSV"""
    try:
        tickers = []
        with open(CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row['Code'].strip()
                if code:
                    tickers.append(f"{code}.JK")
        return sorted(tickers)
    except Exception as e:
        print(f"CSV read failed: {e}")
        return None


def main():
    print("Generating idx_tickers.json...")

    tickers = fetch_from_idx_api()
    source = "IDX API"
    
    if not tickers:
        print("Falling back to CSV...")
        tickers = fetch_from_csv()
        source = "CSV"
    
    if not tickers:
        print("ERROR: Could not fetch ticker list from any source")
        sys.exit(1)

    data = {
        'tickers': tickers,
        'total': len(tickers),
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'source': source
    }

    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Written {len(tickers)} tickers to {JSON_PATH} (source: {source})")


if __name__ == '__main__':
    main()
