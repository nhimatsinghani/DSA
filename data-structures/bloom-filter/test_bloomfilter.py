"""
Comprehensive tests for Bloom Filter implementation.

These tests demonstrate:
1. Basic functionality and correctness
2. False positive rate validation
3. Mathematical property verification
4. Edge cases and error handling
5. Educational examples showing how Bloom filters work
"""

import unittest
import random
import string
import math
from bloomfilter import BloomFilter


class TestBloomFilter(unittest.TestCase):
    """Test suite for Bloom Filter implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bf = BloomFilter(capacity=1000, error_rate=0.01)
        
    def test_initialization(self):
        """Test Bloom Filter initialization with different parameters."""
        # Test default initialization
        bf_default = BloomFilter()
        self.assertEqual(bf_default.capacity, 1000)
        self.assertEqual(bf_default.desired_error_rate, 0.01)
        self.assertGreater(bf_default.bit_array_size, 0)
        self.assertGreater(bf_default.num_hash_functions, 0)
        
        # Test custom parameters
        bf_custom = BloomFilter(capacity=500, error_rate=0.05)
        self.assertEqual(bf_custom.capacity, 500)
        self.assertEqual(bf_custom.desired_error_rate, 0.05)
        
        # Test edge cases
        with self.assertRaises(ValueError):
            BloomFilter(capacity=0)  # Invalid capacity
        with self.assertRaises(ValueError):
            BloomFilter(error_rate=0)  # Invalid error rate
        with self.assertRaises(ValueError):
            BloomFilter(error_rate=1)  # Invalid error rate
    
    def test_optimal_parameter_calculation(self):
        """Test that optimal parameters are calculated correctly."""
        capacity = 1000
        error_rate = 0.01
        
        bf = BloomFilter(capacity=capacity, error_rate=error_rate)
        
        # Verify bit array size formula: m = -n × ln(p) / (ln(2))²
        expected_m = int(-capacity * math.log(error_rate) / (math.log(2) ** 2))
        self.assertEqual(bf.bit_array_size, expected_m)
        
        # Verify hash functions formula: k = (m/n) × ln(2)
        expected_k = int((bf.bit_array_size / capacity) * math.log(2))
        expected_k = max(1, expected_k)
        self.assertEqual(bf.num_hash_functions, expected_k)
    
    def test_hash_function_properties(self):
        """Test hash function properties and distribution."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Test different input types
        test_inputs = [
            "string",
            42,
            3.14,
            ["list", "item"],
            {"key": "value"}
        ]
        
        hash_sets = []
        for item in test_inputs:
            hash_positions = bf._hash_functions(item)
            hash_sets.append(set(hash_positions))
            
            # Verify we get the right number of hash functions
            self.assertEqual(len(hash_positions), bf.num_hash_functions)
            
            # Verify hash positions are within bit array bounds
            for pos in hash_positions:
                self.assertGreaterEqual(pos, 0)
                self.assertLess(pos, bf.bit_array_size)
        
        # Hash functions should produce different results for different inputs
        # (though collisions are possible, they should be rare for small test set)
        unique_hash_sets = set(frozenset(s) for s in hash_sets)
        self.assertGreater(len(unique_hash_sets), 1)
        
        # Same input should produce same hash
        hash1 = bf._hash_functions("test")
        hash2 = bf._hash_functions("test")
        self.assertEqual(hash1, hash2)
    
    def test_bit_operations(self):
        """Test bit setting and getting operations."""
        bf = BloomFilter(capacity=100)
        
        # Test setting and getting bits
        test_positions = [0, 1, 7, 8, 15, 16, 100, 1000]
        
        for pos in test_positions:
            if pos < bf.bit_array_size:
                # Initially bit should be 0
                self.assertFalse(bf._get_bit(pos))
                
                # Set bit and verify it's set
                was_zero = bf._set_bit(pos)
                self.assertTrue(was_zero)  # Should return True (was zero)
                self.assertTrue(bf._get_bit(pos))
                
                # Setting again should return False (wasn't zero)
                was_zero = bf._set_bit(pos)
                self.assertFalse(was_zero)
                self.assertTrue(bf._get_bit(pos))
    
    def test_add_element_details(self):
        """Test detailed information returned by add() method."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Add an element and examine details
        details = bf.add("test_element")
        
        # Verify expected keys are present
        expected_keys = [
            'item', 'hash_positions', 'newly_set_bits', 'already_set_bits',
            'total_bits_set', 'bits_already_set', 'elements_added',
            'theoretical_fp_rate', 'fill_ratio'
        ]
        
        for key in expected_keys:
            self.assertIn(key, details)
        
        # Verify data types and constraints
        self.assertEqual(details['item'], "test_element")
        self.assertEqual(len(details['hash_positions']), bf.num_hash_functions)
        self.assertEqual(details['elements_added'], 1)
        self.assertGreaterEqual(details['total_bits_set'], 0)
        self.assertLessEqual(details['total_bits_set'], bf.num_hash_functions)
        self.assertGreaterEqual(details['fill_ratio'], 0)
        self.assertLessEqual(details['fill_ratio'], 1)
        
        # Add same element again
        details2 = bf.add("test_element")
        
        # Should have fewer newly set bits (some already set)
        self.assertLessEqual(details2['total_bits_set'], details['total_bits_set'])
        self.assertEqual(details2['elements_added'], 2)
    
    def test_query_functionality(self):
        """Test query functionality and return values."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Query non-existent element
        result = bf.query("not_added")
        self.assertEqual(result['result'], "DEFINITELY_NOT_IN_SET")
        self.assertEqual(result['actual_result'], "TRUE_NEGATIVE")
        self.assertFalse(result['all_bits_set'])
        
        # Add element and query it
        bf.add("added_element")
        result = bf.query("added_element")
        self.assertEqual(result['result'], "POSSIBLY_IN_SET")
        self.assertEqual(result['actual_result'], "TRUE_POSITIVE")
        self.assertTrue(result['all_bits_set'])
        
        # Verify query statistics
        self.assertEqual(result['query_statistics']['true_positives'], 1)
        self.assertEqual(result['query_statistics']['true_negatives'], 1)
        self.assertEqual(result['query_statistics']['false_positives'], 0)
    
    def test_false_positive_behavior(self):
        """Test false positive behavior and rates."""
        # Use small filter to increase chance of false positives
        bf = BloomFilter(capacity=50, error_rate=0.1)
        
        # Add elements
        added_elements = []
        for i in range(50):
            element = f"element_{i}"
            bf.add(element)
            added_elements.append(element)
        
        # Test added elements (should all be positive)
        for element in added_elements:
            result = bf.query(element)
            self.assertEqual(result['result'], "POSSIBLY_IN_SET")
            self.assertEqual(result['actual_result'], "TRUE_POSITIVE")
        
        # Test many non-added elements to find false positives
        false_positives = 0
        true_negatives = 0
        test_count = 1000
        
        for i in range(test_count):
            element = f"not_added_{i}"
            result = bf.query(element)
            
            if result['result'] == "POSSIBLY_IN_SET":
                self.assertEqual(result['actual_result'], "FALSE_POSITIVE")
                false_positives += 1
            else:
                self.assertEqual(result['actual_result'], "TRUE_NEGATIVE")
                true_negatives += 1
        
        # Calculate actual false positive rate
        actual_fp_rate = false_positives / test_count
        theoretical_fp_rate = bf.theoretical_fp_rate
        
        # Actual rate should be reasonably close to theoretical
        # (within 3x tolerance due to randomness)
        self.assertLess(actual_fp_rate, theoretical_fp_rate * 3)
        
        print(f"\nFalse Positive Rate Test:")
        print(f"  Theoretical: {theoretical_fp_rate:.4f}")
        print(f"  Actual: {actual_fp_rate:.4f}")
        print(f"  False positives: {false_positives}/{test_count}")
    
    def test_no_false_negatives(self):
        """Test that there are never false negatives."""
        bf = BloomFilter(capacity=200, error_rate=0.01)
        
        # Add many elements
        added_elements = []
        for i in range(200):
            element = f"element_{i}"
            bf.add(element)
            added_elements.append(element)
        
        # Verify no false negatives
        for element in added_elements:
            result = bf.query(element)
            self.assertEqual(result['result'], "POSSIBLY_IN_SET")
            # Should never be a false negative
            self.assertNotEqual(result['actual_result'], "FALSE_NEGATIVE")
    
    def test_fill_ratio_progression(self):
        """Test how fill ratio progresses as elements are added."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        fill_ratios = []
        
        # Add elements and track fill ratio
        for i in range(100):
            bf.add(f"element_{i}")
            stats = bf.get_statistics()
            fill_ratios.append(stats['performance']['fill_ratio'])
        
        # Fill ratio should generally increase (though it may plateau)
        self.assertGreater(fill_ratios[-1], fill_ratios[0])
        
        # Fill ratio should never exceed 1.0
        for ratio in fill_ratios:
            self.assertLessEqual(ratio, 1.0)
            self.assertGreaterEqual(ratio, 0.0)
    
    def test_error_rate_impact(self):
        """Test how error rate affects filter characteristics."""
        capacity = 1000
        error_rates = [0.001, 0.01, 0.1]
        
        results = []
        
        for error_rate in error_rates:
            bf = BloomFilter(capacity=capacity, error_rate=error_rate)
            stats = bf.get_statistics()
            results.append({
                'error_rate': error_rate,
                'bit_array_size': bf.bit_array_size,
                'hash_functions': bf.num_hash_functions,
                'memory_bytes': stats['configuration']['memory_bytes']
            })
        
        # Lower error rate should require more memory
        self.assertGreater(results[0]['bit_array_size'], results[1]['bit_array_size'])
        self.assertGreater(results[1]['bit_array_size'], results[2]['bit_array_size'])
        
        # Lower error rate typically requires more hash functions
        self.assertGreaterEqual(results[0]['hash_functions'], results[2]['hash_functions'])
    
    def test_capacity_scaling(self):
        """Test how capacity affects filter characteristics."""
        error_rate = 0.01
        capacities = [100, 1000, 10000]
        
        for capacity in capacities:
            bf = BloomFilter(capacity=capacity, error_rate=error_rate)
            
            # Bit array size should scale with capacity
            expected_bits_per_element = -math.log(error_rate) / (math.log(2) ** 2)
            expected_size = int(capacity * expected_bits_per_element)
            
            # Should be approximately correct (exact calculation)
            self.assertEqual(bf.bit_array_size, expected_size)
    
    def test_union_operation(self):
        """Test union of two Bloom filters."""
        bf1 = BloomFilter(capacity=100, error_rate=0.01)
        bf2 = BloomFilter(capacity=100, error_rate=0.01)
        
        # Add different elements to each
        elements1 = [f"set1_{i}" for i in range(50)]
        elements2 = [f"set2_{i}" for i in range(50)]
        
        for elem in elements1:
            bf1.add(elem)
        for elem in elements2:
            bf2.add(elem)
        
        # Create union
        union_bf = bf1.union(bf2)
        
        # Union should contain elements from both sets
        for elem in elements1 + elements2:
            result = union_bf.query(elem)
            self.assertEqual(result['result'], "POSSIBLY_IN_SET")
        
        # Test union with incompatible filters
        bf_different = BloomFilter(capacity=200, error_rate=0.01)
        with self.assertRaises(ValueError):
            bf1.union(bf_different)
    
    def test_intersection_estimation(self):
        """Test intersection estimation (approximate)."""
        bf1 = BloomFilter(capacity=100, error_rate=0.01)
        bf2 = BloomFilter(capacity=100, error_rate=0.01)
        
        # Add overlapping sets
        common_elements = [f"common_{i}" for i in range(20)]
        unique_elements1 = [f"unique1_{i}" for i in range(30)]
        unique_elements2 = [f"unique2_{i}" for i in range(30)]
        
        for elem in common_elements + unique_elements1:
            bf1.add(elem)
        for elem in common_elements + unique_elements2:
            bf2.add(elem)
        
        # Estimate intersection
        intersection_result = bf1.intersection_estimate(bf2)
        
        # Should have reasonable estimate (within broad range due to approximation)
        estimated = intersection_result['estimated_intersection_size']
        actual = intersection_result['actual_intersection_size']
        
        self.assertEqual(actual, len(common_elements))  # Should be 20
        # Estimation can be quite rough, so we use generous bounds
        self.assertGreater(estimated, 0)
        self.assertLess(estimated, 100)
    
    def test_membership_operator(self):
        """Test 'in' operator functionality."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Initially should not contain anything
        self.assertNotIn("test", bf)
        
        # Add element
        bf.add("test")
        
        # Should now contain it
        self.assertIn("test", bf)
    
    def test_statistics_comprehensiveness(self):
        """Test that statistics provide comprehensive information."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Add some elements
        for i in range(50):
            bf.add(f"element_{i}")
        
        # Query some elements
        for i in range(60):  # Some will be false positives
            bf.query(f"test_{i}")
        
        stats = bf.get_statistics()
        
        # Verify all expected sections are present
        expected_sections = ['configuration', 'performance', 'test_statistics', 'mathematical_analysis']
        for section in expected_sections:
            self.assertIn(section, stats)
        
        # Verify configuration
        config = stats['configuration']
        self.assertEqual(config['capacity'], 100)
        self.assertEqual(config['desired_error_rate'], 0.01)
        
        # Verify performance metrics
        perf = stats['performance']
        self.assertEqual(perf['elements_added'], 50)
        self.assertGreater(perf['fill_ratio'], 0)
        self.assertGreater(perf['theoretical_fp_rate'], 0)
        
        # Verify test statistics
        test_stats = stats['test_statistics']
        self.assertGreater(test_stats['total_queries'], 0)
    
    def test_reset_functionality(self):
        """Test reset functionality."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Add elements and perform queries
        bf.add("test1")
        bf.add("test2")
        bf.query("test1")
        bf.query("nonexistent")
        
        # Verify state before reset
        self.assertEqual(bf.elements_added, 2)
        self.assertGreater(bf._get_fill_ratio(), 0)
        
        # Reset
        bf.reset()
        
        # Verify state after reset
        self.assertEqual(bf.elements_added, 0)
        self.assertEqual(bf._get_fill_ratio(), 0)
        self.assertEqual(bf.false_positive_tests, 0)
        self.assertEqual(bf.true_positive_tests, 0)
        self.assertEqual(bf.negative_tests, 0)
        self.assertEqual(len(bf.actual_elements), 0)
        
        # Should not contain previously added elements
        self.assertNotIn("test1", bf)
        self.assertNotIn("test2", bf)
    
    def test_string_representation(self):
        """Test string representation."""
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Add some elements
        for i in range(10):
            bf.add(f"element_{i}")
        
        str_repr = str(bf)
        
        # Should contain key information
        self.assertIn("BloomFilter", str_repr)
        self.assertIn("capacity=100", str_repr)
        self.assertIn("error_rate=0.010", str_repr)
        self.assertIn("elements=10", str_repr)


class TestBloomFilterEducational(unittest.TestCase):
    """Educational tests that demonstrate Bloom filter behavior."""
    
    def test_demonstrate_basic_functionality(self):
        """Demonstrate basic Bloom filter operations."""
        print("\n=== Basic Bloom Filter Demonstration ===")
        
        bf = BloomFilter(capacity=10, error_rate=0.1)
        
        print(f"Created Bloom filter:")
        print(f"  Capacity: {bf.capacity}")
        print(f"  Error rate: {bf.desired_error_rate}")
        print(f"  Bit array size: {bf.bit_array_size}")
        print(f"  Hash functions: {bf.num_hash_functions}")
        
        # Add elements with detailed output
        elements = ["apple", "banana", "cherry"]
        
        print(f"\nAdding elements:")
        for element in elements:
            details = bf.add(element)
            print(f"  '{element}':")
            print(f"    Hash positions: {details['hash_positions']}")
            print(f"    Newly set bits: {details['newly_set_bits']}")
            print(f"    Fill ratio: {details['fill_ratio']:.3f}")
        
        # Query elements
        print(f"\nQuerying elements:")
        test_elements = ["apple", "banana", "cherry", "date", "elderberry"]
        
        for element in test_elements:
            result = bf.query(element)
            print(f"  '{element}': {result['result']} ({result['actual_result']})")
    
    def test_demonstrate_false_positives(self):
        """Demonstrate false positive behavior."""
        print("\n=== False Positive Demonstration ===")
        
        # Small filter to increase false positive rate
        bf = BloomFilter(capacity=20, error_rate=0.2)
        
        # Add elements
        added = ["cat", "dog", "bird", "fish", "rabbit"]
        for animal in added:
            bf.add(animal)
        
        print(f"Added animals: {added}")
        print(f"Theoretical false positive rate: {bf.theoretical_fp_rate:.3f}")
        
        # Test various animals
        test_animals = ["cat", "dog", "elephant", "tiger", "lion", "bear", "wolf", "fox"]
        
        print(f"\nTesting membership:")
        for animal in test_animals:
            result = bf.query(animal)
            status = "✓ (added)" if animal in added else "? (not added)"
            print(f"  {animal:<10}: {result['result']:<20} {status}")
    
    def test_demonstrate_parameter_optimization(self):
        """Demonstrate parameter optimization."""
        print("\n=== Parameter Optimization Demonstration ===")
        
        capacity = 1000
        error_rates = [0.001, 0.01, 0.1]
        
        print(f"Optimizing for capacity = {capacity}")
        print(f"{'Error Rate':<12} {'Bits':<8} {'Hash Funcs':<12} {'Memory (KB)':<12} {'Bits/Element':<12}")
        print("-" * 70)
        
        for error_rate in error_rates:
            bf = BloomFilter(capacity=capacity, error_rate=error_rate)
            stats = bf.get_statistics()
            
            memory_kb = stats['configuration']['memory_bytes'] / 1024
            bits_per_element = stats['configuration']['bits_per_element']
            
            print(f"{error_rate:<12.3f} {bf.bit_array_size:<8} {bf.num_hash_functions:<12} "
                  f"{memory_kb:<12.2f} {bits_per_element:<12.1f}")
    
    def test_demonstrate_mathematical_properties(self):
        """Demonstrate mathematical properties."""
        print("\n=== Mathematical Properties Demonstration ===")
        
        bf = BloomFilter(capacity=100, error_rate=0.01)
        
        # Add elements and track theoretical vs actual behavior
        print("Tracking false positive rate vs theory:")
        print(f"{'Elements':<10} {'Fill Ratio':<12} {'Theoretical FP':<15} {'Predicted Rate':<15}")
        print("-" * 60)
        
        for i in range(0, 101, 20):
            if i > 0:
                for j in range(20):
                    bf.add(f"element_{i-20+j}")
            
            stats = bf.get_statistics()
            theoretical = stats['performance']['theoretical_fp_rate']
            fill_ratio = stats['performance']['fill_ratio']
            
            # Calculate predicted rate using formula
            if bf.elements_added > 0:
                predicted = (1 - math.exp(-bf.num_hash_functions * bf.elements_added / bf.bit_array_size)) ** bf.num_hash_functions
            else:
                predicted = 0
            
            print(f"{bf.elements_added:<10} {fill_ratio:<12.3f} {theoretical:<15.6f} {predicted:<15.6f}")


def run_educational_examples():
    """Run educational examples to demonstrate Bloom filter concepts."""
    print("=" * 60)
    print("BLOOM FILTER EDUCATIONAL EXAMPLES")
    print("=" * 60)
    print("This demonstrates the functionality and mathematics of Bloom filters")
    print()
    
    # Run educational test methods
    educational_tests = TestBloomFilterEducational()
    educational_tests.test_demonstrate_basic_functionality()
    educational_tests.test_demonstrate_false_positives()
    educational_tests.test_demonstrate_parameter_optimization()
    educational_tests.test_demonstrate_mathematical_properties()
    
    print("\n" + "=" * 60)
    print("END OF EDUCATIONAL EXAMPLES")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        # Run educational examples
        run_educational_examples()
    else:
        # Run regular tests
        unittest.main(verbosity=2) 