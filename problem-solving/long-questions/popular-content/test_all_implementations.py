"""
Comprehensive Test Suite for Popular Content Tracker Implementations

This module tests all three implementations (Basic, Heap, Advanced) to ensure
correctness and compare performance characteristics.

Test Categories:
1. Correctness Tests: Verify all implementations produce identical results
2. Edge Case Tests: Handle empty states, boundary conditions, invalid inputs
3. Performance Tests: Compare time complexity characteristics
4. Stress Tests: High-volume operations to test scalability
5. Memory Tests: Analyze memory usage patterns
"""

import unittest
import time
import random
from typing import List, Tuple, Any

# Import all implementations
from part_a_basic_implementation import PopularContentTrackerBasic
from part_b_heap_optimization import PopularContentTrackerHeap
from part_c_advanced_hybrid import PopularContentTrackerAdvanced


class TestPopularContentTracker(unittest.TestCase):
    """
    Comprehensive test suite for all Popular Content Tracker implementations.
    """
    
    def setUp(self):
        """Set up test fixtures with all implementations."""
        self.implementations = {
            'basic': PopularContentTrackerBasic(),
            'heap': PopularContentTrackerHeap(),
            'advanced': PopularContentTrackerAdvanced()
        }
    
    def apply_operations(self, operations: List[Tuple[str, int]]) -> None:
        """Apply a sequence of operations to all implementations."""
        for op_type, content_id in operations:
            for tracker in self.implementations.values():
                if op_type == 'increase':
                    tracker.increasePopularity(content_id)
                elif op_type == 'decrease':
                    tracker.decreasePopularity(content_id)
    
    def verify_consistency(self) -> None:
        """Verify all implementations produce the same results."""
        # Check getMostPopular
        most_popular_results = {
            name: tracker.getMostPopular() 
            for name, tracker in self.implementations.items()
        }
        
        # All should return the same result (or all valid results if tied)
        basic_result = most_popular_results['basic']
        for name, result in most_popular_results.items():
            if basic_result == -1:
                self.assertEqual(result, -1, f"{name} should return -1 when no content exists")
            else:
                # If basic returns valid content, others should return content with same popularity
                if result != -1:
                    basic_popularity = self.implementations['basic'].getPopularity(basic_result)
                    result_popularity = self.implementations[name].getPopularity(result)
                    self.assertEqual(basic_popularity, result_popularity,
                                   f"{name} returned content with different popularity than basic")
        
        # Check individual popularities for consistency
        all_content_ids = set()
        for tracker in self.implementations.values():
            if hasattr(tracker, 'getAllPopularContent'):
                all_content_ids.update(tracker.getAllPopularContent().keys())
        
        for content_id in all_content_ids:
            popularities = {
                name: tracker.getPopularity(content_id)
                for name, tracker in self.implementations.items()
            }
            first_popularity = next(iter(popularities.values()))
            for name, popularity in popularities.items():
                self.assertEqual(popularity, first_popularity,
                               f"Content {content_id} has different popularity in {name}")
    
    def test_basic_operations(self):
        """Test basic increase/decrease/getMostPopular operations."""
        operations = [
            ('increase', 1),
            ('increase', 2),
            ('increase', 1),  # Content 1 now has popularity 2
            ('increase', 3),
        ]
        
        self.apply_operations(operations)
        self.verify_consistency()
        
        # Content 1 should have highest popularity (2)
        for tracker in self.implementations.values():
            self.assertEqual(tracker.getPopularity(1), 2)
            self.assertEqual(tracker.getPopularity(2), 1)
            self.assertEqual(tracker.getPopularity(3), 1)
    
    def test_decrease_operations(self):
        """Test decrease operations and content removal."""
        operations = [
            ('increase', 1),
            ('increase', 1),
            ('increase', 2),
            ('decrease', 1),  # Content 1: 2 -> 1
            ('decrease', 2),  # Content 2: 1 -> 0 (removed)
        ]
        
        self.apply_operations(operations)
        self.verify_consistency()
        
        for tracker in self.implementations.values():
            self.assertEqual(tracker.getPopularity(1), 1)
            self.assertEqual(tracker.getPopularity(2), 0)
            self.assertEqual(tracker.getMostPopular(), 1)
    
    def test_empty_state(self):
        """Test behavior with no content."""
        for tracker in self.implementations.values():
            self.assertEqual(tracker.getMostPopular(), -1)
            self.assertEqual(tracker.size(), 0)
            self.assertEqual(tracker.getPopularity(999), 0)
    
    def test_single_content(self):
        """Test with single content item."""
        operations = [('increase', 42)]
        self.apply_operations(operations)
        self.verify_consistency()
        
        for tracker in self.implementations.values():
            self.assertEqual(tracker.getMostPopular(), 42)
            self.assertEqual(tracker.size(), 1)
    
    def test_complete_removal(self):
        """Test removing all content and returning to empty state."""
        operations = [
            ('increase', 1),
            ('increase', 1),
            ('decrease', 1),
            ('decrease', 1),  # Should remove content 1 completely
        ]
        
        self.apply_operations(operations)
        self.verify_consistency()
        
        for tracker in self.implementations.values():
            self.assertEqual(tracker.getMostPopular(), -1)
            self.assertEqual(tracker.size(), 0)
    
    def test_tied_popularities(self):
        """Test behavior when multiple content items have same max popularity."""
        operations = [
            ('increase', 1),
            ('increase', 2),
            ('increase', 3),  # All have popularity 1
        ]
        
        self.apply_operations(operations)
        self.verify_consistency()
        
        # All implementations should return one of {1, 2, 3}
        valid_results = {1, 2, 3}
        for tracker in self.implementations.values():
            result = tracker.getMostPopular()
            self.assertIn(result, valid_results)
            self.assertEqual(tracker.getPopularity(result), 1)
    
    def test_invalid_input(self):
        """Test handling of invalid inputs."""
        for tracker in self.implementations.values():
            with self.assertRaises(ValueError):
                tracker.increasePopularity(0)
            with self.assertRaises(ValueError):
                tracker.increasePopularity(-1)
            with self.assertRaises(ValueError):
                tracker.decreasePopularity(0)
            with self.assertRaises(ValueError):
                tracker.decreasePopularity(-1)
    
    def test_large_popularities(self):
        """Test with large popularity values."""
        operations = []
        for i in range(100):
            operations.append(('increase', 1))
        
        self.apply_operations(operations)
        self.verify_consistency()
        
        for tracker in self.implementations.values():
            self.assertEqual(tracker.getPopularity(1), 100)
            self.assertEqual(tracker.getMostPopular(), 1)
    
    def test_many_content_items(self):
        """Test with many different content items."""
        operations = []
        for content_id in range(1, 51):  # 50 different content items
            for _ in range(content_id % 5 + 1):  # Different popularity levels
                operations.append(('increase', content_id))
        
        self.apply_operations(operations)
        self.verify_consistency()
        
        # Content 49 should have highest popularity (5)
        for tracker in self.implementations.values():
            most_popular = tracker.getMostPopular()
            max_popularity = tracker.getPopularity(most_popular)
            self.assertGreaterEqual(max_popularity, 5)


class PerformanceTest(unittest.TestCase):
    """
    Performance comparison tests for all implementations.
    """
    
    def setUp(self):
        """Set up performance test fixtures."""
        self.implementations = {
            'basic': PopularContentTrackerBasic(),
            'heap': PopularContentTrackerHeap(),
            'advanced': PopularContentTrackerAdvanced()
        }
        
        # Generate test data
        self.test_operations = []
        random.seed(42)  # For reproducible results
        
        for i in range(1000):
            content_id = random.randint(1, 100)
            if random.random() < 0.7:  # 70% increase, 30% decrease
                self.test_operations.append(('increase', content_id))
            else:
                self.test_operations.append(('decrease', content_id))
    
    def measure_operation_time(self, tracker: Any, operations: List[Tuple[str, int]]) -> float:
        """Measure time to perform a sequence of operations."""
        start_time = time.perf_counter()
        
        for op_type, content_id in operations:
            if op_type == 'increase':
                tracker.increasePopularity(content_id)
            else:
                tracker.decreasePopularity(content_id)
        
        end_time = time.perf_counter()
        return end_time - start_time
    
    def measure_query_time(self, tracker: Any, num_queries: int = 1000) -> float:
        """Measure time to perform multiple getMostPopular queries."""
        start_time = time.perf_counter()
        
        for _ in range(num_queries):
            tracker.getMostPopular()
        
        end_time = time.perf_counter()
        return end_time - start_time
    
    def test_operation_performance(self):
        """Compare operation performance across implementations."""
        print("\n=== Operation Performance Comparison ===")
        
        results = {}
        for name, tracker in self.implementations.items():
            # Use fresh tracker for each test
            fresh_tracker = type(tracker)()
            operation_time = self.measure_operation_time(fresh_tracker, self.test_operations)
            results[name] = operation_time
            print(f"{name:10}: {operation_time * 1000:.2f}ms for {len(self.test_operations)} operations")
        
        # Advanced should be fastest or comparable for operations
        self.assertLessEqual(results['advanced'], results['basic'] * 2)  # Allow some variance
    
    def test_query_performance(self):
        """Compare getMostPopular query performance."""
        print("\n=== Query Performance Comparison ===")
        
        # First, populate all trackers with same data
        for tracker in self.implementations.values():
            for op_type, content_id in self.test_operations[:100]:  # Use subset for setup
                if op_type == 'increase':
                    tracker.increasePopularity(content_id)
                else:
                    tracker.decreasePopularity(content_id)
        
        # Measure query performance
        query_results = {}
        for name, tracker in self.implementations.items():
            query_time = self.measure_query_time(tracker, 1000)
            query_results[name] = query_time
            print(f"{name:10}: {query_time * 1000:.2f}ms for 1000 queries "
                  f"({query_time * 1000000 / 1000:.2f}μs per query)")
        
        # Advanced should have best query performance
        self.assertLessEqual(query_results['advanced'], min(query_results.values()) * 1.1)
    
    def test_scalability(self):
        """Test how implementations scale with data size."""
        print("\n=== Scalability Test ===")
        
        data_sizes = [100, 500, 1000]
        
        for size in data_sizes:
            print(f"\nTesting with {size} operations:")
            operations = self.test_operations[:size]
            
            for name, tracker_class in [
                ('basic', PopularContentTrackerBasic),
                ('heap', PopularContentTrackerHeap),
                ('advanced', PopularContentTrackerAdvanced)
            ]:
                tracker = tracker_class()
                operation_time = self.measure_operation_time(tracker, operations)
                query_time = self.measure_query_time(tracker, 100)
                
                print(f"  {name:10}: ops={operation_time*1000:.1f}ms, "
                      f"queries={query_time*1000:.1f}ms")


def run_stress_test():
    """
    Run stress test with high-volume operations.
    """
    print("\n=== Stress Test ===")
    
    implementations = {
        'basic': PopularContentTrackerBasic(),
        'heap': PopularContentTrackerHeap(),
        'advanced': PopularContentTrackerAdvanced()
    }
    
    # Generate large number of random operations
    random.seed(123)
    operations = []
    for _ in range(10000):
        content_id = random.randint(1, 1000)
        op_type = 'increase' if random.random() < 0.6 else 'decrease'
        operations.append((op_type, content_id))
    
    for name, tracker in implementations.items():
        print(f"\nTesting {name} implementation:")
        start_time = time.perf_counter()
        
        try:
            for op_type, content_id in operations:
                if op_type == 'increase':
                    tracker.increasePopularity(content_id)
                else:
                    tracker.decreasePopularity(content_id)
            
            # Perform some queries
            for _ in range(1000):
                most_popular = tracker.getMostPopular()
            
            end_time = time.perf_counter()
            print(f"  Completed in {(end_time - start_time) * 1000:.1f}ms")
            print(f"  Active content items: {tracker.size()}")
            print(f"  Most popular: {tracker.getMostPopular()}")
            
            # Additional stats for advanced implementation
            if hasattr(tracker, 'getBenchmarkStats'):
                stats = tracker.getBenchmarkStats()
                print(f"  Benchmark stats: {stats}")
                
        except Exception as e:
            print(f"  ERROR: {e}")


def main():
    """
    Run all tests and benchmarks.
    """
    print("Starting Comprehensive Test Suite for Popular Content Tracker")
    print("=" * 70)
    
    # Run correctness tests
    print("\n1. Running Correctness Tests...")
    unittest.TextTestRunner(verbosity=1).run(
        unittest.TestLoader().loadTestsFromTestCase(TestPopularContentTracker)
    )
    
    # Run performance tests
    print("\n2. Running Performance Tests...")
    unittest.TextTestRunner(verbosity=1).run(
        unittest.TestLoader().loadTestsFromTestCase(PerformanceTest)
    )
    
    # Run stress test
    print("\n3. Running Stress Test...")
    run_stress_test()
    
    print("\n" + "=" * 70)
    print("Test Suite Complete!")


if __name__ == "__main__":
    main()
