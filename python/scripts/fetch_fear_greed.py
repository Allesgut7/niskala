#!/usr/bin/env python3
"""Fetch fear and greed index"""
import json
import sys
sys.path.insert(0, '.')

try:
    from python.fear_greed.calculator import FearGreedCalculator
    calc = FearGreedCalculator()
    data = calc.calculate()
    print(json.dumps(data))
except Exception as e:
    print(json.dumps({'error': str(e)}))
