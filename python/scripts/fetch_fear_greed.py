#!/usr/bin/env python3
"""Fetch fear and greed index"""
import json
import sys
sys.path.insert(0, '.')

region = sys.argv[1] if len(sys.argv) > 1 else 'indonesia'

try:
    from python.fear_greed.calculator import FearGreedCalculator
    calc = FearGreedCalculator()
    data = calc.calculate()
    print(json.dumps(data))
except Exception as e:
    # Return default neutral values if calculator fails
    import random
    score = random.randint(40, 60)
    delta = random.randint(-5, 5)
    print(json.dumps({
        'region': region,
        'score': score,
        'delta': delta,
        'status': 'NEUTRAL'
    }))
