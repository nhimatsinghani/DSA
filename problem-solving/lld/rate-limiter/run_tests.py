#!/usr/bin/env python3
"""
Test Runner for Rate Limiter

Usage:
    python run_tests.py             # Run all tests
"""

import os
import sys
import unittest
from pathlib import Path


def run_tests():
    # Ensure discovery runs from this script's directory
    here = Path(__file__).parent.resolve()
    os.chdir(here)
    # Ensure this directory is on sys.path for module imports
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))

    suite = unittest.defaultTestLoader.discover(str(here), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    ok = run_tests()
    raise SystemExit(0 if ok else 1) 