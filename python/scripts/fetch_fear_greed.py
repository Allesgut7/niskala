#!/usr/bin/env python3
"""Fetch fear and greed index for all regions with delta tracking"""
import json
import os
import sys
sys.path.insert(0, '.')

STATE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "..",
    "regime_trainer", "models", "fear_greed_state.json"
)

try:
    from python.fear_greed.calculator import FearGreedCalculator
    calc = FearGreedCalculator()
    results = calc.calculate_all()

    prev = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                prev = json.load(f)
        except Exception:
            prev = {}

    region_map = {"indonesia": "indo", "asia": "asia", "global": "global"}
    output = {}
    for py_key, ui_key in region_map.items():
        if py_key in results:
            score = results[py_key]["score"]
            prev_score = prev.get(ui_key, {}).get("score", score)
            output[ui_key] = {"score": score, "delta": score - prev_score}

    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({k: {"score": v["score"]} for k, v in output.items()}, f)

    print(json.dumps(output))
except Exception as e:
    print(json.dumps({
        "indo": {"score": 50, "delta": 0},
        "asia": {"score": 50, "delta": 0},
        "global": {"score": 50, "delta": 0},
    }))
