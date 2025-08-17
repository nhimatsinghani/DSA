#!/usr/bin/env python3
"""
Test Runner for Customer Rating

Usage:
    python run_tests.py
"""

import os
import sys
import unittest
from pathlib import Path


def run_tests():
    here = Path(__file__).parent.resolve()
    os.chdir(here)
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))

    suite = unittest.defaultTestLoader.discover(str(here), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    ok = run_tests()
    raise SystemExit(0 if ok else 1) 