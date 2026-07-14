#!/usr/bin/env python3
"""Fetch top gainers and losers from IDX BEI API"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from data_sources.idx_bei_client import IdxBeiClient

    client = IdxBeiClient()
    gainers = client.get_top_gainers(7)
    losers = client.get_top_losers(7)

    result = {
        'gainers': gainers,
        'losers': losers
    }
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({'gainers': [], 'losers': [], 'error': str(e)}))
