"""
Comprehensive Test Suite for Segment Tree Implementation

This module contains extensive test cases for all segment tree implementations,
including unit tests, integration tests, edge cases, and performance tests.
"""

import unittest
import random
import time
from typing import List, Tuple

# Import the modules to test
try:
    from segment_tree import SegmentTree, SumSegmentTree, MinSegmentTree, MaxSegmentTree
    from num_array import NumArray, NumArrayAlternative
except ImportError:
    # Handle relative imports when running from different directories
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from segment_tree import SegmentTree, SumSegmentTree, MinSegmentTree, MaxSegmentTree
    from num_array import NumArray, NumArrayAlternative


class TestSegmentTree(unittest.TestCase):
    """Test cases for the generic SegmentTree class."""
    
    def test_sum_segment_tree_basic(self):
        """Test basic sum segment tree operations."""
        arr = [1, 3, 5, 7, 9, 11]
        st = SumSegmentTree(arr)
        
        # Test range queries
        self.assertEqual(st.query(0, 5), sum(arr))  # Full range
        self.assertEqual(st.query(1, 4), 3 + 5 + 7 + 9)  # Partial range
        self.assertEqual(st.query(2, 2), 5)  # Single element
        self.assertEqual(st.query(0, 2), 1 + 3 + 5)  # First three elements
        
        # Test updates
        st.update(2, 10)  # Change 5 to 10
        self.assertEqual(st.query(0, 5), 1 + 3 + 10 + 7 + 9 + 11)
        self.assertEqual(st.query(1, 4), 3 + 10 + 7 + 9)
        self.assertEqual(st.query(2, 2), 10)
    
    def test_min_segment_tree(self):
        """Test minimum segment tree operations."""
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        min_tree = MinSegmentTree(arr)
        
        # Test range minimum queries
        self.assertEqual(min_tree.query(0, 7), 1)  # Global minimum
        self.assertEqual(min_tree.query(2, 5), 1)  # min(4, 1, 5, 9)
        self.assertEqual(min_tree.query(4, 7), 2)  # min(5, 9, 2, 6)
        self.assertEqual(min_tree.query(3, 3), 1)  # Single element
        
        # Test updates
        min_tree.update(3, 0)  # Change second 1 to 0
        self.assertEqual(min_tree.query(0, 7), 0)  # New global minimum
        self.assertEqual(min_tree.query(2, 5), 0)  # min(4, 0, 5, 9)
    
    def test_max_segment_tree(self):
        """Test maximum segment tree operations."""
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        max_tree = MaxSegmentTree(arr)
        
        # Test range maximum queries
        self.assertEqual(max_tree.query(0, 7), 9)  # Global maximum
        self.assertEqual(max_tree.query(2, 5), 9)  # max(4, 1, 5, 9)
        self.assertEqual(max_tree.query(0, 3), 4)  # max(3, 1, 4, 1)
        self.assertEqual(max_tree.query(6, 7), 6)  # max(2, 6)
        
        # Test updates
        max_tree.update(1, 15)  # Change first 1 to 15
        self.assertEqual(max_tree.query(0, 7), 15)  # New global maximum
        self.assertEqual(max_tree.query(0, 3), 15)  # max(3, 15, 4, 1)
    
    def test_custom_operation(self):
        """Test segment tree with custom operation (multiplication)."""
        def multiply(a, b):
            return a * b
        
        arr = [1, 2, 3, 4]
        mult_tree = SegmentTree(arr, multiply, 1)  # Identity for multiplication is 1
        
        self.assertEqual(mult_tree.query(0, 3), 24)  # 1*2*3*4 = 24
        self.assertEqual(mult_tree.query(1, 2), 6)   # 2*3 = 6
        self.assertEqual(mult_tree.query(0, 1), 2)   # 1*2 = 2
        
        mult_tree.update(2, 5)  # Change 3 to 5
        self.assertEqual(mult_tree.query(0, 3), 40)  # 1*2*5*4 = 40
        self.assertEqual(mult_tree.query(1, 2), 10)  # 2*5 = 10
    
    def test_empty_and_single_element(self):
        """Test edge cases with empty and single element arrays."""
        # Single element
        single_tree = SumSegmentTree([42])
        self.assertEqual(single_tree.query(0, 0), 42)
        
        single_tree.update(0, 100)
        self.assertEqual(single_tree.query(0, 0), 100)
        
        # Empty array (edge case)
        empty_tree = SumSegmentTree([])
        self.assertEqual(empty_tree.query(0, 0), 0)  # Should return identity
    
    def test_boundary_conditions(self):
        """Test boundary conditions and invalid queries."""
        arr = [1, 2, 3, 4, 5]
        st = SumSegmentTree(arr)
        
        # Valid boundaries
        self.assertEqual(st.query(0, 4), 15)  # Full range
        self.assertEqual(st.query(0, 0), 1)   # First element
        self.assertEqual(st.query(4, 4), 5)   # Last element
        
        # Invalid queries should return identity (0 for sum)
        self.assertEqual(st.query(-1, 0), 0)   # Invalid left boundary
        self.assertEqual(st.query(0, 5), 0)    # Invalid right boundary
        self.assertEqual(st.query(3, 2), 0)    # Invalid range (left > right)


class TestNumArray(unittest.TestCase):
    """Test cases for the NumArray class."""
    
    def test_leetcode_example(self):
        """Test the example from the LeetCode problem."""
        nums = [1, 3, 5]
        num_array = NumArray(nums)
        
        # Initial queries
        self.assertEqual(num_array.sumRange(0, 2), 9)  # 1 + 3 + 5 = 9
        
        # Update and query
        num_array.update(1, 2)  # Change 3 to 2
        self.assertEqual(num_array.sumRange(0, 2), 8)  # 1 + 2 + 5 = 8
        
        # Verify internal state
        self.assertEqual(num_array.get_array(), [1, 2, 5])
    
    def test_multiple_updates_and_queries(self):
        """Test multiple updates and queries in sequence."""
        nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        num_array = NumArray(nums)
        
        # Initial queries
        self.assertEqual(num_array.sumRange(0, 9), 55)  # Sum of 1-10
        self.assertEqual(num_array.sumRange(2, 7), 33)  # 3+4+5+6+7+8
        self.assertEqual(num_array.sumRange(5, 5), 6)   # Single element
        
        # Multiple updates
        num_array.update(0, 10)  # 1 → 10
        num_array.update(4, 50)  # 5 → 50
        num_array.update(9, 100) # 10 → 100
        
        # Queries after updates
        self.assertEqual(num_array.sumRange(0, 9), 199)  # Updated sum
        self.assertEqual(num_array.sumRange(2, 7), 78)   # 3+4+50+6+7+8
        self.assertEqual(num_array.sumRange(0, 4), 69)   # 10+2+3+4+50
        
        # Verify final state
        expected = [10, 2, 3, 4, 50, 6, 7, 8, 9, 100]
        self.assertEqual(num_array.get_array(), expected)
    
    def test_negative_numbers(self):
        """Test NumArray with negative numbers."""
        nums = [-1, -2, 3, -4, 5, -6]
        num_array = NumArray(nums)
        
        self.assertEqual(num_array.sumRange(0, 5), -5)  # Sum of all elements
        self.assertEqual(num_array.sumRange(2, 4), 4)   # 3 + (-4) + 5 = 4
        self.assertEqual(num_array.sumRange(1, 1), -2)  # Single negative element
        
        # Update negative to positive
        num_array.update(1, 10)  # -2 → 10
        self.assertEqual(num_array.sumRange(0, 5), 7)   # Updated sum
        self.assertEqual(num_array.sumRange(0, 2), 12)  # -1 + 10 + 3 = 12
    
    def test_large_numbers(self):
        """Test NumArray with large numbers."""
        nums = [1000000, 2000000, 3000000, 4000000]
        num_array = NumArray(nums)
        
        self.assertEqual(num_array.sumRange(0, 3), 10000000)
        self.assertEqual(num_array.sumRange(1, 2), 5000000)
        
        num_array.update(2, 5000000)  # 3M → 5M
        self.assertEqual(num_array.sumRange(0, 3), 12000000)
    
    def test_edge_cases(self):
        """Test various edge cases."""
        # Single element array
        single = NumArray([42])
        self.assertEqual(single.sumRange(0, 0), 42)
        single.update(0, 100)
        self.assertEqual(single.sumRange(0, 0), 100)
        
        # Two element array
        double = NumArray([1, 2])
        self.assertEqual(double.sumRange(0, 1), 3)
        self.assertEqual(double.sumRange(0, 0), 1)
        self.assertEqual(double.sumRange(1, 1), 2)
        
        double.update(0, 5)
        self.assertEqual(double.sumRange(0, 1), 7)
        
        # Zero values
        zeros = NumArray([0, 0, 0, 0])
        self.assertEqual(zeros.sumRange(0, 3), 0)
        zeros.update(2, 5)
        self.assertEqual(zeros.sumRange(0, 3), 5)


class TestNumArrayAlternative(unittest.TestCase):
    """Test cases for the alternative NumArray implementation."""
    
    def test_equivalence_with_main_implementation(self):
        """Test that alternative implementation gives same results."""
        nums = [1, 3, 5, 7, 9, 11, 13, 15]
        
        # Create both implementations
        num_array1 = NumArray(nums)
        num_array2 = NumArrayAlternative(nums)
        
        # Test initial queries
        for left in range(len(nums)):
            for right in range(left, len(nums)):
                result1 = num_array1.sumRange(left, right)
                result2 = num_array2.sumRange(left, right)
                self.assertEqual(result1, result2, 
                               f"Query [{left}, {right}] differs: {result1} vs {result2}")
        
        # Test after updates
        updates = [(2, 10), (5, 20), (0, 100)]
        for index, value in updates:
            num_array1.update(index, value)
            num_array2.update(index, value)
            
            # Test queries after each update
            for left in range(len(nums)):
                for right in range(left, len(nums)):
                    result1 = num_array1.sumRange(left, right)
                    result2 = num_array2.sumRange(left, right)
                    self.assertEqual(result1, result2,
                                   f"After update({index}, {value}), query [{left}, {right}] differs")


class TestPerformance(unittest.TestCase):
    """Performance tests for segment tree implementations."""
    
    def test_build_time_complexity(self):
        """Test that build time is O(n)."""
        sizes = [1000, 2000, 4000]
        times = []
        
        for size in sizes:
            arr = list(range(size))
            
            start_time = time.time()
            st = SumSegmentTree(arr)
            build_time = time.time() - start_time
            
            times.append(build_time)
        
        # Build time should scale roughly linearly
        # times[1] should be roughly 2x times[0], etc.
        # Allow some variance for system factors
        ratio1 = times[1] / times[0] if times[0] > 0 else 1
        ratio2 = times[2] / times[1] if times[1] > 0 else 1
        
        # Should be between 1.5x and 3x (allowing for variance)
        self.assertLess(ratio1, 4.0, "Build time doesn't scale linearly")
        self.assertLess(ratio2, 4.0, "Build time doesn't scale linearly")
    
    def test_query_and_update_performance(self):
        """Test query and update performance."""
        size = 10000
        arr = list(range(size))
        st = SumSegmentTree(arr)
        
        # Test query performance
        start_time = time.time()
        for _ in range(1000):
            left = random.randint(0, size - 1)
            right = random.randint(left, size - 1)
            result = st.query(left, right)
        query_time = time.time() - start_time
        
        # Test update performance
        start_time = time.time()
        for _ in range(1000):
            index = random.randint(0, size - 1)
            value = random.randint(1, 100)
            st.update(index, value)
        update_time = time.time() - start_time
        
        # Both should complete reasonably quickly
        self.assertLess(query_time, 1.0, "Queries are too slow")
        self.assertLess(update_time, 1.0, "Updates are too slow")
    
    def test_comparison_with_naive(self):
        """Compare segment tree performance with naive approach."""
        size = 1000
        arr = list(range(size))
        
        # Segment tree approach
        st = SumSegmentTree(arr)
        operations = []
        for _ in range(500):
            if random.random() < 0.7:  # 70% queries
                left = random.randint(0, size - 1)
                right = random.randint(left, size - 1)
                operations.append(('query', left, right))
            else:  # 30% updates
                index = random.randint(0, size - 1)
                value = random.randint(1, 100)
                operations.append(('update', index, value))
        
        # Time segment tree
        start_time = time.time()
        for op in operations:
            if op[0] == 'query':
                result = st.query(op[1], op[2])
            else:
                st.update(op[1], op[2])
        st_time = time.time() - start_time
        
        # Time naive approach
        naive_arr = arr[:]
        start_time = time.time()
        for op in operations:
            if op[0] == 'query':
                result = sum(naive_arr[op[1]:op[2]+1])
            else:
                naive_arr[op[1]] = op[2]
        naive_time = time.time() - start_time
        
        # Segment tree should be faster (allowing some variance)
        speedup = naive_time / st_time if st_time > 0 else 1
        self.assertGreater(speedup, 0.5, f"Segment tree not competitive: {speedup:.2f}x speedup")


class TestCorrectness(unittest.TestCase):
    """Comprehensive correctness tests with random operations."""
    
    def test_random_operations_correctness(self):
        """Test correctness with many random operations."""
        for _ in range(10):  # Run multiple random tests
            size = random.randint(10, 100)
            arr = [random.randint(-100, 100) for _ in range(size)]
            
            # Create both segment tree and naive reference
            st = NumArray(arr)
            naive = arr[:]
            
            # Perform random operations
            for _ in range(100):
                if random.random() < 0.6:  # 60% queries
                    left = random.randint(0, size - 1)
                    right = random.randint(left, size - 1)
                    
                    st_result = st.sumRange(left, right)
                    naive_result = sum(naive[left:right+1])
                    
                    self.assertEqual(st_result, naive_result,
                                   f"Query mismatch for range [{left}, {right}]: "
                                   f"ST={st_result}, Naive={naive_result}, Array={naive}")
                else:  # 40% updates
                    index = random.randint(0, size - 1)
                    value = random.randint(-100, 100)
                    
                    st.update(index, value)
                    naive[index] = value
                    
                    # Verify array state matches
                    self.assertEqual(st.get_array(), naive,
                                   f"Array state mismatch after update({index}, {value})")
    
    def test_stress_test(self):
        """Stress test with many operations."""
        size = 500
        arr = [1] * size  # Start with all 1s
        st = NumArray(arr)
        expected_sum = size
        
        # Perform many updates and verify total sum
        for i in range(size):
            new_value = i + 1
            st.update(i, new_value)
            expected_sum = expected_sum - 1 + new_value
            
            actual_sum = st.sumRange(0, size - 1)
            self.assertEqual(actual_sum, expected_sum,
                           f"Sum mismatch after update {i}: expected {expected_sum}, got {actual_sum}")


def run_all_tests():
    """Run all test suites."""
    print("🧪 Running Segment Tree Test Suite")
    print("=" * 50)
    
    # Create test suites
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSegmentTree,
        TestNumArray,
        TestNumArrayAlternative,
        TestPerformance,
        TestCorrectness
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ ALL TESTS PASSED!' if success else '❌ SOME TESTS FAILED!'}")
    
    return success


if __name__ == "__main__":
    run_all_tests() 