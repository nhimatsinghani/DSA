#!/usr/bin/env python3
"""
Test Runner for Evolving Key-Value Store

This script allows you to run individual stage tests or all tests together.
Perfect for debugging during the technical interview process.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --stage 1          # Run only Stage 1 tests
    python run_tests.py --stage 2          # Run only Stage 2 tests
    python run_tests.py --stage 3          # Run only Stage 3 tests
    python run_tests.py --stage 4          # Run only Stage 4 tests
    python run_tests.py --comprehensive    # Run comprehensive test suite
    python run_tests.py --quick            # Run quick smoke tests only
"""

import argparse
import sys
import time


def run_individual_stage(stage_num):
    """Run tests for a specific stage."""
    stage_functions = {
        1: ("test_stage1", "run_stage1_tests"),
        2: ("test_stage2", "run_stage2_tests"),
        3: ("test_stage3", "run_stage3_tests"),
        4: ("test_stage4", "run_stage4_tests"),
    }
    
    if stage_num not in stage_functions:
        print(f"❌ Invalid stage number: {stage_num}")
        print("Valid stages: 1, 2, 3, 4")
        return False
    
    module_name, function_name = stage_functions[stage_num]
    
    try:
        module = __import__(module_name)
        test_function = getattr(module, function_name)
        return test_function()
    except ImportError as e:
        print(f"❌ Could not import {module_name}: {e}")
        return False
    except AttributeError as e:
        print(f"❌ Could not find function {function_name} in {module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running Stage {stage_num} tests: {e}")
        return False


def run_all_stages():
    """Run all stage tests in sequence."""
    print("=" * 80)
    print("RUNNING ALL STAGE TESTS")
    print("=" * 80)
    
    results = []
    total_start_time = time.time()
    
    for stage_num in [1, 2, 3, 4]:
        print(f"\n{'='*20} STAGE {stage_num} {'='*20}")
        start_time = time.time()
        
        success = run_individual_stage(stage_num)
        
        elapsed = time.time() - start_time
        results.append((stage_num, success, elapsed))
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\nStage {stage_num} completed in {elapsed:.2f}s: {status}")
    
    total_elapsed = time.time() - total_start_time
    
    # Print summary
    print("\n" + "=" * 80)
    print("FINAL RESULTS SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for stage_num, success, elapsed in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"Stage {stage_num:1d}: {status:9} ({elapsed:.2f}s)")
        if not success:
            all_passed = False
    
    print(f"\nTotal time: {total_elapsed:.2f}s")
    print("=" * 80)
    
    if all_passed:
        print("🎉 ALL STAGES PASSED! Your implementation is ready!")
    else:
        print("⚠️  Some stages failed. Check the output above for details.")
    
    return all_passed


def run_comprehensive_tests():
    """Run the comprehensive test suite."""
    print("=" * 80)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    try:
        from test_comprehensive import TestEvolvingKeyValueStore
        import unittest
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestEvolvingKeyValueStore)
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        if result.wasSuccessful():
            print("✅ ALL COMPREHENSIVE TESTS PASSED!")
        else:
            print("❌ SOME COMPREHENSIVE TESTS FAILED")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"❌ Could not import comprehensive tests: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
        return False


def run_quick_smoke_tests():
    """Run quick smoke tests to verify basic functionality."""
    print("=" * 80)
    print("RUNNING QUICK SMOKE TESTS")
    print("=" * 80)
    
    try:
        from key_value_store import EvolvingKeyValueStore
        
        store = EvolvingKeyValueStore()
        
        # Test Stage 1: Basic operations
        print("Testing Stage 1: Basic operations...")
        store.set_basic("test", "value")
        assert store.get_basic("test") == "value"
        print("✅ Stage 1 basic functionality works")
        
        # Test Stage 2: TTL
        print("Testing Stage 2: TTL...")
        store.set_with_ttl("ttl_test", "expires", ttl=0.1)
        assert store.get_with_ttl("ttl_test") == "expires"
        time.sleep(0.2)
        assert store.get_with_ttl("ttl_test") is None
        print("✅ Stage 2 TTL functionality works")
        
        # Test Stage 3: History
        print("Testing Stage 3: History...")
        store.set_with_history("history_test", "v1")
        time.sleep(0.05)
        timestamp = time.time()
        store.set_with_history("history_test", "v2")
        assert store.get_at_time("history_test", timestamp - 0.01) == "v1"
        assert store.get_current_with_history("history_test") == "v2"
        print("✅ Stage 3 history functionality works")
        
        # Test Stage 4: Deletion
        print("Testing Stage 4: Deletion...")
        store.set("delete_test", "to_be_deleted")
        assert store.delete("delete_test") == True
        assert store.get("delete_test") is None
        assert store.delete("delete_test") == False  # Already deleted
        print("✅ Stage 4 deletion functionality works")
        
        # Test unified interface
        print("Testing unified interface...")
        store.set("unified", "test", ttl=1.0)
        assert store.get("unified") == "test"
        assert store.exists("unified") == True
        store.delete("unified")
        assert store.exists("unified") == False
        print("✅ Unified interface works")
        
        print("\n" + "=" * 80)
        print("🎉 ALL SMOKE TESTS PASSED!")
        print("Basic functionality is working correctly.")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to handle command-line arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Test runner for Evolving Key-Value Store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all stage tests
  python run_tests.py --stage 2          # Run only Stage 2 tests
  python run_tests.py --comprehensive    # Run comprehensive test suite
  python run_tests.py --quick            # Run quick smoke tests
        """
    )
    
    parser.add_argument(
        "--stage", 
        type=int, 
        choices=[1, 2, 3, 4],
        help="Run tests for a specific stage (1-4)"
    )
    
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run the comprehensive test suite"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick smoke tests only"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Check for conflicting arguments
    specified_options = sum([
        args.stage is not None,
        args.comprehensive,
        args.quick
    ])
    
    if specified_options > 1:
        print("❌ Error: Please specify only one test type.")
        parser.print_help()
        return 1
    
    success = False
    
    if args.quick:
        success = run_quick_smoke_tests()
    elif args.comprehensive:
        success = run_comprehensive_tests()
    elif args.stage is not None:
        success = run_individual_stage(args.stage)
    else:
        # Default: run all stages
        success = run_all_stages()
    
    # Exit with appropriate code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 