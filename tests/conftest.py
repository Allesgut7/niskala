# Niskala - Pytest Configuration
# Version: 1.0.0

import pytest
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))


def pytest_collection_modifyitems(config, items):
    """Add markers to tests"""
    for item in items:
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
