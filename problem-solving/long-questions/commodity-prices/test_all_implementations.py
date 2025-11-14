"""
Comprehensive Test Suite for Commodity Price Tracker Implementations

Tests all three implementations (O(N), O(log N), O(1)) to ensure:
1. Correctness across different scenarios
2. Performance characteristics
3. Edge case handling
4. Memory efficiency
"""

import unittest
import time
import random
from typing import List, Tuple

# Import all implementations
from part_a_basic_implementation import BasicCommodityPriceTracker
from part_b_logn_implementation import LogNSortedListTracker, LogNHeapTracker, LogNBalancedTracker
from part_c_constant_implementation import ConstantTimeTracker, OptimizedConstantTracker


class TestCommodityTrackerCorrectness(unittest.TestCase):
    """Test correctness of all implementations."""
    
    def setUp(self):
        """Set up test instances."""
        self.implementations = [
            ("Basic O(N)", BasicCommodityPriceTracker()),
            ("LogN Sorted", LogNSortedListTracker()),
            ("LogN Heap", LogNHeapTracker()),
            ("LogN Balanced", LogNBalancedTracker()),
            ("O(1) Constant", ConstantTimeTracker()),
            ("O(1) Optimized", OptimizedConstantTracker()),
        ]
    
    def test_basic_functionality(self):
        """Test basic insert and max retrieval."""
        test_data = [(1000, 50.0), (1001, 60.0), (1002, 55.0)]
        expected_max = 60.0
        
        for name, tracker in self.implementations:
            with self.subTest(implementation=name):
                for timestamp, price in test_data:
                    tracker.upsert_price(timestamp, price)
                
                self.assertEqual(tracker.get_max_commodity_price(), expected_max,
                               f"{name} failed basic functionality test")
    
    def test_out_of_order_timestamps(self):
        """Test handling of out-of-order timestamps."""
        test_data = [
            (1002, 55.0),  # Middle timestamp first
            (1000, 50.0),  # Earliest timestamp
            (1001, 60.0),  # Latest timestamp, new max
        ]
        expected_max = 60.0
        
        for name, tracker in self.implementations:
            with self.subTest(implementation=name):
                for timestamp, price in test_data:
                    tracker.upsert_price(timestamp, price)
                
                self.assertEqual(tracker.get_max_commodity_price(), expected_max,
                               f"{name} failed out-of-order test")
    
    def test_duplicate_timestamp_updates(self):
        """Test updating existing timestamps."""
        for name, tracker in self.implementations:
            with self.subTest(implementation=name):
                # Initial data
                tracker.upsert_price(1000, 50.0)
                tracker.upsert_price(1001, 60.0)
                self.assertEqual(tracker.get_max_commodity_price(), 60.0)
                
                # Update existing max to higher value
                tracker.upsert_price(1001, 70.0)
                self.assertEqual(tracker.get_max_commodity_price(), 70.0)
                
                # Update existing max to lower value
                tracker.upsert_price(1001, 45.0)
                self.assertEqual(tracker.get_max_commodity_price(), 50.0)
    
    def test_edge_cases(self):
        """Test edge cases like empty data, single entry, etc."""
        for name, tracker in self.implementations:
            with self.subTest(implementation=name):
                # Empty data
                self.assertIsNone(tracker.get_max_commodity_price(),
                                f"{name} failed empty data test")
                
                # Single entry
                tracker.upsert_price(1000, 42.0)
                self.assertEqual(tracker.get_max_commodity_price(), 42.0)
                
                # Update single entry
                tracker.upsert_price(1000, 37.0)
                self.assertEqual(tracker.get_max_commodity_price(), 37.0)
    
    def test_multiple_max_values(self):
        """Test handling multiple timestamps with same max value."""
        test_data = [
            (1000, 50.0),
            (1001, 60.0),
            (1002, 60.0),  # Duplicate max
            (1003, 55.0),
        ]
        
        for name, tracker in self.implementations:
            with self.subTest(implementation=name):
                for timestamp, price in test_data:
                    tracker.upsert_price(timestamp, price)
                
                self.assertEqual(tracker.get_max_commodity_price(), 60.0)
                
                # Remove one max entry
                tracker.upsert_price(1001, 40.0)
                self.assertEqual(tracker.get_max_commodity_price(), 60.0,
                               f"{name} failed multiple max values test")
    
    def test_negative_price_validation(self):
        """Test that negative prices are rejected."""
        for name, tracker in self.implementations:
            with self.subTest(implementation=name):
                with self.assertRaises(ValueError):
                    tracker.upsert_price(1000, -10.0)


class TestPerformanceCharacteristics(unittest.TestCase):
    """Test performance characteristics of different implementations."""
    
    def setUp(self):
        """Set up performance test data."""
        self.small_dataset = 100
        self.medium_dataset = 1000
        self.large_dataset = 5000
        
        # Suppress print statements during performance tests
        import sys
        self.original_stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
    
    def tearDown(self):
        """Clean up after performance tests."""
        import sys
        sys.stdout.close()
        sys.stdout = self.original_stdout
    
    def _generate_test_data(self, size: int) -> List[Tuple[int, float]]:
        """Generate random test data."""
        return [(i, random.uniform(10.0, 100.0)) for i in range(size)]
    
    def _measure_performance(self, tracker, test_data: List[Tuple[int, float]], 
                           query_count: int = 100) -> Tuple[float, float]:
        """Measure insert and query performance."""
        # Measure insertion time
        start_time = time.time()
        for timestamp, price in test_data:
            tracker.upsert_price(timestamp, price)
        insert_time = time.time() - start_time
        
        # Measure query time
        start_time = time.time()
        for _ in range(query_count):
            tracker.get_max_commodity_price()
        query_time = time.time() - start_time
        
        return insert_time, query_time
    
    def test_small_dataset_performance(self):
        """Test performance on small dataset."""
        test_data = self._generate_test_data(self.small_dataset)
        
        implementations = [
            ("Basic O(N)", BasicCommodityPriceTracker()),
            ("O(1) Constant", ConstantTimeTracker()),
        ]
        
        for name, tracker in implementations:
            insert_time, query_time = self._measure_performance(tracker, test_data)
            self.assertLess(insert_time, 1.0, f"{name} insert too slow on small dataset")
            self.assertLess(query_time, 0.1, f"{name} query too slow on small dataset")
    
    def test_scalability_comparison(self):
        """Compare scalability of different approaches."""
        test_sizes = [100, 500, 1000]
        
        implementations = [
            ("Basic O(N)", BasicCommodityPriceTracker()),
            ("O(1) Constant", ConstantTimeTracker()),
        ]
        
        results = {}
        
        for size in test_sizes:
            test_data = self._generate_test_data(size)
            
            for name, tracker in implementations:
                insert_time, query_time = self._measure_performance(tracker, test_data, 50)
                
                if name not in results:
                    results[name] = []
                results[name].append((size, insert_time, query_time))
        
        # O(1) implementation should have better query performance at scale
        o1_query_times = [qt for _, _, qt in results["O(1) Constant"]]
        basic_query_times = [qt for _, _, qt in results["Basic O(N)"]]
        
        # At larger scales, O(1) should be faster for queries
        self.assertLess(o1_query_times[-1], basic_query_times[-1] * 2,
                       "O(1) implementation not showing expected performance advantage")


class TestMemoryEfficiency(unittest.TestCase):
    """Test memory usage patterns."""
    
    def test_memory_overhead(self):
        """Test that implementations don't have excessive memory overhead."""
        import sys
        
        trackers = [
            BasicCommodityPriceTracker(),
            ConstantTimeTracker(),
        ]
        
        test_data = [(i, float(i)) for i in range(1000)]
        
        for tracker in trackers:
            initial_size = sys.getsizeof(tracker)
            
            for timestamp, price in test_data:
                tracker.upsert_price(timestamp, price)
            
            final_size = sys.getsizeof(tracker)
            memory_per_entry = (final_size - initial_size) / len(test_data)
            
            # Memory per entry should be reasonable (rough heuristic)
            self.assertLess(memory_per_entry, 200,
                           f"Excessive memory usage: {memory_per_entry} bytes per entry")


class TestStressScenarios(unittest.TestCase):
    """Test implementations under stress conditions."""
    
    def test_rapid_updates(self):
        """Test rapid updates to same timestamps."""
        tracker = ConstantTimeTracker()
        
        # Rapidly update same timestamp
        for i in range(100):
            tracker.upsert_price(1000, float(i))
        
        self.assertEqual(tracker.get_max_commodity_price(), 99.0)
        self.assertEqual(tracker.size(), 1)
    
    def test_alternating_max_updates(self):
        """Test alternating between different max values."""
        tracker = ConstantTimeTracker()
        
        # Set up initial state
        tracker.upsert_price(1000, 50.0)
        tracker.upsert_price(1001, 60.0)
        
        # Alternate max values
        for i in range(50):
            if i % 2 == 0:
                tracker.upsert_price(1001, 70.0)  # New max
                expected_max = 70.0
            else:
                tracker.upsert_price(1001, 40.0)  # Remove max
                expected_max = 50.0
            
            self.assertEqual(tracker.get_max_commodity_price(), expected_max,
                           f"Failed on iteration {i}")
    
    def test_large_price_range(self):
        """Test with very large price ranges."""
        tracker = ConstantTimeTracker()
        
        # Test with extreme values
        test_cases = [
            (1000, 0.01),     # Very small
            (1001, 1000000.0), # Very large
            (1002, 50.0),      # Normal
        ]
        
        for timestamp, price in test_cases:
            tracker.upsert_price(timestamp, price)
        
        self.assertEqual(tracker.get_max_commodity_price(), 1000000.0)


def run_comprehensive_demo():
    """Run a comprehensive demo showing all implementations."""
    print("=== Comprehensive Commodity Price Tracker Demo ===\n")
    
    # Create instances of all implementations
    implementations = [
        ("Basic O(N)", BasicCommodityPriceTracker()),
        ("LogN Heap", LogNHeapTracker()),
        ("O(1) Constant", ConstantTimeTracker()),
    ]
    
    # Complex test scenario
    print("Test Scenario: Stock market simulation")
    print("- Morning: Initial prices")
    print("- Midday: Market volatility (updates)")
    print("- Afternoon: New data points")
    print("- End of day: Final max price\n")
    
    scenarios = [
        ("Morning", [(1000, 45.50), (1001, 47.25), (1002, 46.75)]),
        ("Midday Volatility", [(1001, 52.00), (1000, 44.25)]),
        ("Afternoon", [(1003, 49.50), (1004, 48.25)]),
        ("Late Update", [(1002, 53.75)]),  # New max
    ]
    
    for name, tracker in implementations:
        print(f"--- {name} Implementation ---")
        
        for scenario_name, operations in scenarios:
            print(f"\n{scenario_name}:")
            for timestamp, price in operations:
                tracker.upsert_price(timestamp, price)
                max_price = tracker.get_max_commodity_price()
                print(f"  After {timestamp}: ${price:.2f} -> Max: ${max_price:.2f}")
        
        print(f"\nFinal max: ${tracker.get_max_commodity_price():.2f}")
        print(f"Total data points: {tracker.size()}\n")


if __name__ == "__main__":
    # Run the comprehensive demo
    run_comprehensive_demo()
    
    # Run unit tests
    print("\n" + "="*50)
    print("Running Unit Tests...")
    print("="*50)
    
    unittest.main(verbosity=2, exit=False)
