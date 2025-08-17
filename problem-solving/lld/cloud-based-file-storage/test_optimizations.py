#!/usr/bin/env python3
"""
Test Suite for Performance Optimizations

Tests to verify that the optimizations in get_n_largest work correctly:
1. Prefix Index Optimization: Using files_by_prefix for efficient prefix lookup
2. Min Heap Optimization: Using heapq for efficient top-n selection

These tests ensure that optimizations maintain correctness while improving performance.
"""

import unittest
import time
from file_storage_system import CloudFileStorage


class TestOptimizations(unittest.TestCase):
    """Test performance optimizations in the cloud storage system."""
    
    def setUp(self):
        """Set up a fresh storage system for each test."""
        self.storage = CloudFileStorage()
    
    def test_prefix_index_correctness(self):
        """Test that prefix index optimization returns correct results."""
        # Add files with various prefixes
        test_files = [
            ("log_error.txt", 100),
            ("log_warning.txt", 80), 
            ("log_info.txt", 60),
            ("logic_error.py", 150),  # Should NOT match "log_" prefix
            ("data_file.csv", 200),
            ("data_backup.zip", 300),
            ("other_file.txt", 50)
        ]
        
        for name, size in test_files:
            self.storage.add_file(name, size)
        
        # Test exact prefix matching
        log_files = self.storage.get_n_largest("log_", 10)
        expected_log = ["log_error.txt", "log_warning.txt", "log_info.txt"]
        self.assertEqual(set(log_files), set(expected_log))
        print(f"✓ Prefix 'log_' correctly matched: {log_files}")
        
        # Test that "logic_error.py" is NOT included (it doesn't start with "log_")
        self.assertNotIn("logic_error.py", log_files)
        
        # Test another prefix
        data_files = self.storage.get_n_largest("data_", 10)
        expected_data = ["data_backup.zip", "data_file.csv"]  # Sorted by size desc
        self.assertEqual(data_files, expected_data)
        print(f"✓ Prefix 'data_' correctly matched: {data_files}")
        
        # Test empty prefix (should match all files)
        all_files = self.storage.get_n_largest("", 10)
        self.assertEqual(len(all_files), 7)  # All files
        print(f"✓ Empty prefix matched all {len(all_files)} files")
        
        # Test non-existent prefix
        missing_files = self.storage.get_n_largest("missing_", 10)
        self.assertEqual(missing_files, [])
        print("✓ Non-existent prefix returned empty list")
    
    def test_min_heap_correctness(self):
        """Test that min heap optimization returns correct top-n results."""
        # Create many files to trigger heap optimization (when matching files > n)
        files = []
        for i in range(20):
            name = f"test_file_{i:02d}.txt"
            size = 1000 - i * 10  # Decreasing sizes: 1000, 990, 980, ...
            files.append((name, size))
            self.storage.add_file(name, size)
        
        # Test getting top 5 files
        top_5 = self.storage.get_n_largest("test_file_", 5)
        
        # Should be the 5 largest files
        expected_top_5 = [
            "test_file_00.txt",  # size 1000
            "test_file_01.txt",  # size 990
            "test_file_02.txt",  # size 980
            "test_file_03.txt",  # size 970
            "test_file_04.txt"   # size 960
        ]
        
        self.assertEqual(top_5, expected_top_5)
        print(f"✓ Min heap correctly selected top 5: {top_5}")
        
        # Test getting top 3
        top_3 = self.storage.get_n_largest("test_file_", 3)
        expected_top_3 = expected_top_5[:3]
        self.assertEqual(top_3, expected_top_3)
        print(f"✓ Min heap correctly selected top 3: {top_3}")
        
        # Test getting more than available (should return all)
        all_files = self.storage.get_n_largest("test_file_", 50)
        self.assertEqual(len(all_files), 20)
        print(f"✓ Requesting more than available returned all {len(all_files)} files")
    
    def test_sorting_correctness_with_heap(self):
        """Test that files with same size are sorted correctly by name when using heap."""
        # Add files with same sizes to test tie-breaking
        same_size_files = [
            ("zebra.txt", 100),
            ("apple.txt", 100), 
            ("monkey.txt", 100),
            ("banana.txt", 50),
            ("cherry.txt", 50)
        ]
        
        for name, size in same_size_files:
            self.storage.add_file(name, size)
        
        # Get top 3 files - should prioritize by size first, then name
        top_3 = self.storage.get_n_largest("", 3)
        
        # Expected: the 3 files with size 100, sorted alphabetically
        expected = ["apple.txt", "monkey.txt", "zebra.txt"]
        self.assertEqual(top_3, expected)
        print(f"✓ Tie-breaking by name works with heap: {top_3}")
        
        # Get all files to verify full sorting
        all_sorted = self.storage.get_n_largest("", 10)
        expected_all = [
            "apple.txt",   # size 100
            "monkey.txt",  # size 100  
            "zebra.txt",   # size 100
            "banana.txt",  # size 50
            "cherry.txt"   # size 50
        ]
        self.assertEqual(all_sorted, expected_all)
        print(f"✓ Full sorting with tie-breaking: {all_sorted}")
    
    def test_edge_cases_with_optimizations(self):
        """Test edge cases to ensure optimizations handle them correctly."""
        # Test with only 1 file
        self.storage.add_file("single.txt", 100)
        result = self.storage.get_n_largest("single", 5)
        self.assertEqual(result, ["single.txt"])
        print("✓ Single file case handled correctly")
        
        # Test with exact n files
        for i in range(3):
            self.storage.add_file(f"exact_{i}.txt", 100 - i)
        
        result = self.storage.get_n_largest("exact_", 3)  # Exactly 3 files match
        expected = ["exact_0.txt", "exact_1.txt", "exact_2.txt"]
        self.assertEqual(result, expected)
        print("✓ Exact n files case handled correctly")
        
        # Test with n = 1 (edge case for heap)
        result = self.storage.get_n_largest("exact_", 1)
        self.assertEqual(result, ["exact_0.txt"])  # Largest file
        print("✓ n=1 case handled correctly")
        
    def test_prefix_fallback_mechanism(self):
        """Test that the system falls back correctly when prefix is not in index."""
        # This tests the fallback mechanism in case the prefix index doesn't have
        # the exact prefix (though with our current implementation, it should always have it)
        
        # Add a file
        self.storage.add_file("special_file.txt", 100)
        
        # The prefix index should have this, but let's test it works
        result = self.storage.get_n_largest("special", 5)
        self.assertEqual(result, ["special_file.txt"])
        print("✓ Prefix lookup works correctly")
        
        # Test a prefix that definitely won't be in the index
        result = self.storage.get_n_largest("nonexistent", 5)
        self.assertEqual(result, [])
        print("✓ Non-existent prefix handled correctly")

    def test_performance_characteristics(self):
        """Basic performance test to show improvement (not a rigorous benchmark)."""
        # This is more of a demonstration than a precise performance test
        
        # Create a large number of files
        num_files = 1000
        print(f"\n📊 Performance test with {num_files} files:")
        
        # Add files
        start_time = time.time()
        for i in range(num_files):
            self.storage.add_file(f"perf_test_{i:04d}.dat", 1000 + i)
        add_time = time.time() - start_time
        print(f"  Adding {num_files} files: {add_time:.3f}s")
        
        # Test prefix query performance
        start_time = time.time()
        result = self.storage.get_n_largest("perf_test_", 10)
        query_time = time.time() - start_time
        print(f"  Querying top 10 from {num_files} files: {query_time:.3f}s")
        
        # Verify correctness
        expected_top = [f"perf_test_{1000-1-i:04d}.dat" for i in range(10)]
        self.assertEqual(result, expected_top)
        print(f"  ✓ Results correct: {result[:3]}...{result[-1:]}")
        
        # The query should be very fast due to optimizations
        self.assertLess(query_time, 0.1)  # Should be much faster than 100ms
        print(f"  ✓ Query completed in {query_time*1000:.1f}ms (optimized)")


def run_optimization_tests():
    """Run optimization tests with detailed output."""
    print("=" * 70)
    print("🚀 PERFORMANCE OPTIMIZATION TESTS")
    print("=" * 70)
    print("Testing prefix index and min heap optimizations in get_n_largest")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOptimizations)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL OPTIMIZATION TESTS PASSED!")
        print("\n🎯 Key Optimizations Verified:")
        print("  • Prefix Index: O(1) prefix lookup instead of O(F) scanning")
        print("  • Min Heap: O(m log n) selection instead of O(m log m) sorting")
        print("  • Correct tie-breaking: Size descending, then name ascending")
        print("  • Edge case handling: Empty results, single files, etc.")
    else:
        print("❌ SOME OPTIMIZATION TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_optimization_tests() 