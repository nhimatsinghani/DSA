#!/usr/bin/env python3
"""
Comprehensive Test Runner for Cloud-Based File Storage System

This script runs tests for all levels of the file storage system:
- Level 1: Basic file operations (add, get, delete)
- Level 2: Prefix-based file querying
- Level 3: User management with capacity limits

Usage examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --level 1          # Run only Level 1 tests
    python run_tests.py --level 2          # Run only Level 2 tests
    python run_tests.py --level 3          # Run only Level 3 tests
    python run_tests.py --comprehensive    # Run comprehensive integration tests
    python run_tests.py --quick            # Run quick smoke tests only
    python run_tests.py --verbose          # Run with extra verbose output
"""

import sys
import argparse
import unittest
from io import StringIO
import time

# Import test modules
from test_level1 import TestLevel1BasicOperations, run_level1_tests
from test_level2 import TestLevel2PrefixQuerying, run_level2_tests  
from test_level3 import TestLevel3UserManagement, run_level3_tests


class TestRunner:
    """Advanced test runner with multiple execution modes."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {}
        
    def run_quick_tests(self):
        """Run a quick smoke test of basic functionality."""
        print("🚀 RUNNING QUICK SMOKE TESTS")
        print("=" * 50)
        
        from file_storage_system import CloudFileStorage
        
        try:
            storage = CloudFileStorage()
            
            # Quick Level 1 test
            print("Testing Level 1: Basic operations...")
            assert storage.add_file("test.txt", 100) == True
            assert storage.get_file_size("test.txt") == 100
            assert storage.delete_file("test.txt") == 100
            print("✅ Level 1: Basic operations work")
            
            # Quick Level 2 test
            print("Testing Level 2: Prefix queries...")
            storage.add_file("log_error.txt", 50)
            storage.add_file("log_info.txt", 30)
            result = storage.get_n_largest("log_", 2)
            assert len(result) == 2
            assert result[0] == "log_error.txt"  # Larger file first
            print("✅ Level 2: Prefix queries work")
            
            # Quick Level 3 test
            print("Testing Level 3: User management...")
            assert storage.add_user("testuser", 200) == True
            result = storage.add_file_by("testuser", "user_file.txt", 50)
            assert result == 150  # 200 - 50 = 150 remaining
            print("✅ Level 3: User management works")
            
            print("\n🎉 ALL QUICK TESTS PASSED! System is functional.")
            return True
            
        except Exception as e:
            print(f"\n❌ QUICK TEST FAILED: {e}")
            return False
    
    def run_comprehensive_tests(self):
        """Run comprehensive integration tests across all levels."""
        print("🔬 RUNNING COMPREHENSIVE INTEGRATION TESTS")
        print("=" * 60)
        
        from file_storage_system import CloudFileStorage
        
        success = True
        
        try:
            # Test 1: Cross-level integration
            print("\n📋 Test 1: Cross-level Integration")
            storage = CloudFileStorage()
            
            # Create users (Level 3)
            storage.add_user("alice", 500)
            storage.add_user("bob", 300)
            
            # Add files by users (Level 3)
            storage.add_file_by("alice", "project_report.pdf", 200)
            storage.add_file_by("alice", "project_data.csv", 150)
            storage.add_file_by("bob", "project_notes.txt", 100)
            storage.add_file_by("admin", "project_backup.zip", 1000)  # Admin file
            
            # Query by prefix (Level 2) - should work across all users
            project_files = storage.get_n_largest("project_", 10)
            assert len(project_files) == 4
            assert project_files[0] == "project_backup.zip"  # Largest first
            
            # Delete file (Level 1) - should update user storage
            deleted_size = storage.delete_file("project_report.pdf")
            assert deleted_size == 200
            
            # Verify user storage updated
            alice_info = storage.get_user_info("alice")
            assert alice_info['used_storage'] == 150  # Only data.csv remains
            
            print("✅ Cross-level integration works correctly")
            
            # Test 2: Complex user merging scenario
            print("\n📋 Test 2: Complex User Merging")
            storage.clear_storage()
            
            # Create users with files
            storage.add_user("team1", 400)
            storage.add_user("team2", 300)
            
            storage.add_file_by("team1", "team1_doc1.txt", 100)
            storage.add_file_by("team1", "team1_doc2.txt", 150)
            storage.add_file_by("team2", "team2_doc1.txt", 80)
            storage.add_file_by("team2", "team2_doc2.txt", 120)
            
            # Merge teams
            result = storage.merge_user("team1", "team2")
            assert result is not None
            
            # Verify team1 now owns all files
            team1_files = storage.list_files_by_user("team1")
            assert len(team1_files) == 4
            
            # Verify team2 is deleted
            team2_info = storage.get_user_info("team2")
            assert team2_info is None
            
            print("✅ Complex user merging works correctly")
            
            # Test 3: Large-scale operations
            print("\n📋 Test 3: Large-scale Operations")
            storage.clear_storage()
            
            # Create many users and files
            for i in range(20):
                storage.add_user(f"user{i}", 1000)
                for j in range(5):
                    storage.add_file_by(f"user{i}", f"user{i}_file{j}.txt", 50)
            
            # Query large result set
            all_files = storage.get_n_largest("user", 200)
            assert len(all_files) == 100  # 20 users * 5 files each
            
            # Verify system integrity
            issues = storage.validate_system_integrity()
            assert len(issues) == 0
            
            print("✅ Large-scale operations work correctly")
            
            print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
            
        except Exception as e:
            print(f"\n❌ COMPREHENSIVE TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            success = False
            
        return success
    
    def run_specific_level(self, level):
        """Run tests for a specific level."""
        if level == 1:
            return run_level1_tests()
        elif level == 2:
            return run_level2_tests()
        elif level == 3:
            return run_level3_tests()
        else:
            print(f"❌ Invalid level: {level}. Must be 1, 2, or 3.")
            return False
    
    def run_all_levels(self):
        """Run all level tests in sequence."""
        print("🏃‍♂️ RUNNING ALL LEVEL TESTS")
        print("=" * 60)
        
        results = {}
        overall_success = True
        
        # Run each level
        for level in [1, 2, 3]:
            print(f"\n🎯 Starting Level {level} Tests...")
            start_time = time.time()
            
            success = self.run_specific_level(level)
            
            end_time = time.time()
            duration = end_time - start_time
            
            results[level] = {
                'success': success,
                'duration': duration
            }
            
            if not success:
                overall_success = False
            
            print(f"⏱️  Level {level} completed in {duration:.2f} seconds")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS SUMMARY")
        print("=" * 60)
        
        for level, result in results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            print(f"Level {level}: {status} ({result['duration']:.2f}s)")
        
        total_time = sum(r['duration'] for r in results.values())
        print(f"\nTotal execution time: {total_time:.2f} seconds")
        
        if overall_success:
            print("🎉 ALL LEVELS PASSED! Your implementation is ready for interview.")
        else:
            print("⚠️  Some levels failed. Please review the failed tests.")
        
        return overall_success


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Test runner for Cloud-Based File Storage System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                    # Run all level tests
    python run_tests.py --level 1          # Run only Level 1
    python run_tests.py --level 2          # Run only Level 2
    python run_tests.py --level 3          # Run only Level 3
    python run_tests.py --comprehensive    # Run integration tests
    python run_tests.py --quick            # Run quick smoke tests
    python run_tests.py --all              # Run everything (levels + comprehensive)
        """
    )
    
    parser.add_argument(
        '--level', 
        type=int, 
        choices=[1, 2, 3],
        help='Run tests for specific level only (1, 2, or 3)'
    )
    
    parser.add_argument(
        '--comprehensive',
        action='store_true',
        help='Run comprehensive integration tests'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true', 
        help='Run quick smoke tests only'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tests: levels + comprehensive'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser


def main():
    """Main entry point for test runner."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(verbose=args.verbose)
    
    success = True
    
    print("🗂️  CLOUD-BASED FILE STORAGE SYSTEM - TEST RUNNER")
    print("=" * 70)
    print("Testing multi-level cloud storage implementation")
    print("Designed for technical interview preparation")
    print("=" * 70)
    
    # Determine what to run
    if args.quick:
        success = runner.run_quick_tests()
    elif args.level:
        success = runner.run_specific_level(args.level)
    elif args.comprehensive:
        success = runner.run_comprehensive_tests()
    elif args.all:
        # Run levels first, then comprehensive
        level_success = runner.run_all_levels()
        comprehensive_success = runner.run_comprehensive_tests()
        success = level_success and comprehensive_success
    else:
        # Default: run all level tests
        success = runner.run_all_levels()
    
    # Final status
    print("\n" + "=" * 70)
    if success:
        print("🎊 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("Your cloud storage implementation is ready for technical interviews.")
        print("\nNext steps:")
        print("1. Review the implementation for optimization opportunities")
        print("2. Practice explaining the design decisions")
        print("3. Consider edge cases and scalability improvements")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the failed tests and fix any issues.")
        print("\nDebugging tips:")
        print("1. Run individual level tests to isolate issues")
        print("2. Use --verbose flag for detailed output")
        print("3. Check the test logs for specific failure details")
    
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 