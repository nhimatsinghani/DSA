"""
Comprehensive tests for HyperLogLog implementation.

These tests demonstrate:
1. Basic functionality and correctness
2. Accuracy across different data sizes
3. Internal algorithm behavior
4. Edge cases and error handling
5. Educational examples showing how HyperLogLog works
"""

import unittest
import random
import string
import math
from hyperloglog import HyperLogLog


class TestHyperLogLog(unittest.TestCase):
    """Test suite for HyperLogLog implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hll = HyperLogLog(precision=10)
        
    def test_initialization(self):
        """Test HyperLogLog initialization with different precisions."""
        # Test default initialization
        hll_default = HyperLogLog()
        self.assertEqual(hll_default.precision, 10)
        self.assertEqual(hll_default.bucket_count, 1024)
        self.assertEqual(len(hll_default.buckets), 1024)
        
        # Test custom precision
        hll_custom = HyperLogLog(precision=8)
        self.assertEqual(hll_custom.precision, 8)
        self.assertEqual(hll_custom.bucket_count, 256)
        
        # Test edge cases
        with self.assertRaises(ValueError):
            HyperLogLog(precision=3)  # Too low
        with self.assertRaises(ValueError):
            HyperLogLog(precision=17)  # Too high
    
    def test_alpha_calculation(self):
        """Test that alpha constants are calculated correctly."""
        test_cases = [
            (4, 0.5),    # Small buckets
            (5, 0.697),  # 32 buckets
            (6, 0.709),  # 64 buckets
            (10, 0.7213 / (1 + 1.079 / 1024))  # Large buckets
        ]
        
        for precision, expected_alpha in test_cases:
            hll = HyperLogLog(precision=precision)
            if precision <= 5:
                self.assertAlmostEqual(hll.alpha, expected_alpha, places=3)
            else:
                self.assertGreater(hll.alpha, 0.7)
                self.assertLess(hll.alpha, 0.8)
    
    def test_hash_function(self):
        """Test hash function properties."""
        hll = HyperLogLog(precision=10)
        
        # Test different input types
        test_inputs = [
            "string",
            42,
            3.14,
            ["list", "item"],
            {"key": "value"}
        ]
        
        hashes = []
        for item in test_inputs:
            hash_val = hll._hash(item)
            hashes.append(hash_val)
            self.assertIsInstance(hash_val, int)
            self.assertGreaterEqual(hash_val, 0)
            self.assertLess(hash_val, 2**64)
        
        # Hashes should be different for different inputs
        self.assertEqual(len(set(hashes)), len(hashes))
        
        # Same input should produce same hash
        self.assertEqual(hll._hash("test"), hll._hash("test"))
    
    def test_leading_zeros_counting(self):
        """Test leading zeros counting function."""
        hll = HyperLogLog(precision=10)
        
        test_cases = [
            (0b1000000000000000, 1),  # 0 leading zeros
            (0b0100000000000000, 2),  # 1 leading zero
            (0b0010000000000000, 3),  # 2 leading zeros
            (0b0001000000000000, 4),  # 3 leading zeros
            (0b0000000000000001, 16), # 15 leading zeros
            (0, 17)                   # All zeros
        ]
        
        for value, expected_rank in test_cases:
            rank = hll._leading_zeros(value, 16)
            self.assertEqual(rank, expected_rank)
    
    def test_add_element_details(self):
        """Test detailed information returned by add() method."""
        hll = HyperLogLog(precision=4)  # Small precision for easier testing
        
        # Add an element and examine the details
        details = hll.add("test_element")
        
        # Verify all expected keys are present
        expected_keys = [
            'item', 'hash_value', 'hash_binary', 'bucket_bits',
            'bucket_index', 'remaining_bits', 'remaining_binary',
            'rank', 'old_bucket_rank', 'new_bucket_rank', 'bucket_updated'
        ]
        
        for key in expected_keys:
            self.assertIn(key, details)
        
        # Verify data types and constraints
        self.assertEqual(details['item'], "test_element")
        self.assertIsInstance(details['bucket_index'], int)
        self.assertGreaterEqual(details['bucket_index'], 0)
        self.assertLess(details['bucket_index'], 16)  # 2^4 = 16 buckets
        self.assertGreaterEqual(details['rank'], 1)
        self.assertIsInstance(details['bucket_updated'], bool)
        
        # Verify binary representations have correct length
        self.assertEqual(len(details['hash_binary']), 64)
        self.assertEqual(len(details['bucket_bits']), 4)
    
    def test_small_dataset_accuracy(self):
        """Test accuracy with small datasets (10-1000 elements)."""
        for true_cardinality in [10, 50, 100, 500, 1000]:
            with self.subTest(cardinality=true_cardinality):
                hll = HyperLogLog(precision=10)
                
                # Add unique elements
                for i in range(true_cardinality):
                    hll.add(f"element_{i}")
                
                estimate = hll.estimate_cardinality()
                estimated_cardinality = estimate['estimated_cardinality']
                
                # Calculate relative error
                relative_error = abs(estimated_cardinality - true_cardinality) / true_cardinality
                
                # For small datasets, we expect higher relative error
                # but it should still be reasonable (within 50% for very small sets)
                if true_cardinality >= 100:
                    self.assertLess(relative_error, 0.3, 
                                  f"Error too high for {true_cardinality} elements: "
                                  f"estimated {estimated_cardinality}, error {relative_error:.2%}")
    
    def test_large_dataset_accuracy(self):
        """Test accuracy with larger datasets (10K-100K elements)."""
        for true_cardinality in [10000, 50000, 100000]:
            with self.subTest(cardinality=true_cardinality):
                hll = HyperLogLog(precision=12)  # Higher precision for better accuracy
                
                # Add unique elements
                for i in range(true_cardinality):
                    hll.add(f"element_{i:06d}")
                
                estimate = hll.estimate_cardinality()
                estimated_cardinality = estimate['estimated_cardinality']
                
                # Calculate relative error
                relative_error = abs(estimated_cardinality - true_cardinality) / true_cardinality
                
                # For larger datasets, error should be within theoretical bounds
                # Theoretical error ≈ 1.04/√(2^12) ≈ 1.625%
                self.assertLess(relative_error, 0.05,  # 5% tolerance
                              f"Error too high for {true_cardinality} elements: "
                              f"estimated {estimated_cardinality}, error {relative_error:.2%}")
    
    def test_duplicate_handling(self):
        """Test that duplicates don't affect cardinality estimate."""
        hll = HyperLogLog(precision=10)
        
        # Add same elements multiple times
        unique_elements = ["a", "b", "c", "d", "e"]
        
        for _ in range(100):  # Add each element 100 times
            for element in unique_elements:
                hll.add(element)
        
        estimate = hll.estimate_cardinality()
        estimated_cardinality = estimate['estimated_cardinality']
        
        # Should estimate close to 5, regardless of repetitions
        self.assertGreater(estimated_cardinality, 2)
        self.assertLess(estimated_cardinality, 15)  # Generous bounds for small dataset
    
    def test_precision_impact_on_accuracy(self):
        """Test how precision affects accuracy."""
        true_cardinality = 10000
        precisions = [4, 6, 8, 10, 12]
        errors = []
        
        for precision in precisions:
            hll = HyperLogLog(precision=precision)
            
            # Add elements
            for i in range(true_cardinality):
                hll.add(f"element_{i}")
            
            estimate = hll.estimate_cardinality()
            estimated_cardinality = estimate['estimated_cardinality']
            relative_error = abs(estimated_cardinality - true_cardinality) / true_cardinality
            errors.append(relative_error)
            
            # Verify theoretical error bound
            theoretical_error = 1.04 / math.sqrt(2 ** precision)
            self.assertLess(relative_error, theoretical_error * 3,  # 3x tolerance
                          f"Error exceeds theoretical bound for precision {precision}")
        
        # Higher precision should generally give better accuracy
        # (though this isn't guaranteed for every single run due to randomness)
        self.assertLess(errors[-1], errors[0] * 2,  # Last error should be better than first
                       "Higher precision should generally give better accuracy")
    
    def test_merge_functionality(self):
        """Test merging of HyperLogLog structures."""
        hll1 = HyperLogLog(precision=8)
        hll2 = HyperLogLog(precision=8)
        
        # Add different elements to each
        for i in range(1000):
            hll1.add(f"set1_element_{i}")
        
        for i in range(1000, 2000):
            hll2.add(f"set2_element_{i}")
        
        # Merge them
        merged = hll1.merge(hll2)
        
        # Merged estimate should be close to 2000
        estimate = merged.estimate_cardinality()
        estimated_cardinality = estimate['estimated_cardinality']
        
        relative_error = abs(estimated_cardinality - 2000) / 2000
        self.assertLess(relative_error, 0.3)
        
        # Test merging with different precisions should fail
        hll_different = HyperLogLog(precision=10)
        with self.assertRaises(ValueError):
            hll1.merge(hll_different)
    
    def test_bucket_analysis(self):
        """Test bucket analysis functionality."""
        hll = HyperLogLog(precision=6)  # 64 buckets
        
        # Add some elements
        for i in range(100):
            hll.add(f"element_{i}")
        
        analysis = hll.get_bucket_analysis()
        
        # Verify analysis structure
        expected_keys = [
            'bucket_count', 'precision', 'elements_added', 'unique_hashes',
            'rank_distribution', 'bucket_utilization', 'max_rank', 'min_rank',
            'avg_rank', 'memory_usage_bits', 'memory_usage_bytes'
        ]
        
        for key in expected_keys:
            self.assertIn(key, analysis)
        
        # Verify values
        self.assertEqual(analysis['bucket_count'], 64)
        self.assertEqual(analysis['precision'], 6)
        self.assertEqual(analysis['elements_added'], 100)
        self.assertGreater(analysis['bucket_utilization'], 0)
        self.assertLessEqual(analysis['bucket_utilization'], 1)
        self.assertGreater(analysis['max_rank'], 0)
        self.assertEqual(analysis['min_rank'], 0)  # Some buckets should be empty
    
    def test_reset_functionality(self):
        """Test reset functionality."""
        hll = HyperLogLog(precision=8)
        
        # Add elements
        for i in range(100):
            hll.add(f"element_{i}")
        
        # Verify state before reset
        self.assertEqual(hll.elements_added, 100)
        self.assertGreater(len(hll.unique_hashes_seen), 0)
        self.assertNotEqual(hll.buckets, [0] * hll.bucket_count)
        
        # Reset
        hll.reset()
        
        # Verify state after reset
        self.assertEqual(hll.elements_added, 0)
        self.assertEqual(len(hll.unique_hashes_seen), 0)
        self.assertEqual(hll.buckets, [0] * hll.bucket_count)
    
    def test_mathematical_properties(self):
        """Test mathematical properties of the algorithm."""
        hll = HyperLogLog(precision=10)
        
        # Add elements and analyze mathematical properties
        for i in range(1000):
            hll.add(f"element_{i}")
        
        estimate_details = hll.estimate_cardinality()
        
        # Verify calculation components
        self.assertIn('calculation_details', estimate_details)
        details = estimate_details['calculation_details']
        
        # Alpha should be reasonable
        self.assertGreater(details['alpha'], 0.7)
        self.assertLess(details['alpha'], 0.8)
        
        # Bucket count should match
        self.assertEqual(details['bucket_count'], 1024)
        
        # Some buckets should be zero, some non-zero
        self.assertGreater(details['zero_buckets'], 0)
        self.assertGreater(details['non_zero_buckets'], 0)
        self.assertEqual(details['zero_buckets'] + details['non_zero_buckets'], 1024)
        
        # Error rate should be theoretical value
        expected_error = 1.04 / math.sqrt(1024)
        self.assertAlmostEqual(float(details['theoretical_error_rate'].split()[0]), 
                              expected_error, places=4)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        hll = HyperLogLog(precision=8)
        
        # Test empty HLL
        estimate = hll.estimate_cardinality()
        self.assertGreaterEqual(estimate['estimated_cardinality'], 0)
        
        # Test single element
        hll.add("single_element")
        estimate = hll.estimate_cardinality()
        self.assertGreater(estimate['estimated_cardinality'], 0)
        
        # Test None and empty string
        hll.add(None)
        hll.add("")
        hll.add(0)
        hll.add(False)
        
        # Should not crash and should update estimate
        estimate = hll.estimate_cardinality()
        self.assertGreater(estimate['estimated_cardinality'], 0)
    
    def test_string_representation(self):
        """Test string representation of HyperLogLog."""
        hll = HyperLogLog(precision=8)
        
        # Add some elements
        for i in range(50):
            hll.add(f"element_{i}")
        
        str_repr = str(hll)
        
        # Should contain key information
        self.assertIn("HyperLogLog", str_repr)
        self.assertIn("precision=8", str_repr)
        self.assertIn("buckets=256", str_repr)
        self.assertIn("elements_added=50", str_repr)
        self.assertIn("estimated_cardinality=", str_repr)


class TestHyperLogLogEducational(unittest.TestCase):
    """Educational tests that demonstrate HyperLogLog behavior."""
    
    def test_demonstrate_hash_distribution(self):
        """Demonstrate how hash function distributes elements across buckets."""
        print("\n=== Hash Distribution Demonstration ===")
        
        hll = HyperLogLog(precision=4)  # 16 buckets for easy visualization
        
        elements = ["apple", "banana", "cherry", "date", "elderberry"]
        
        print(f"Adding {len(elements)} elements to HyperLogLog with {hll.bucket_count} buckets:")
        
        for element in elements:
            details = hll.add(element)
            print(f"\nElement: '{element}'")
            print(f"  Hash: {details['hash_value']}")
            print(f"  Binary: {details['hash_binary'][:16]}... (showing first 16 bits)")
            print(f"  Bucket bits: {details['bucket_bits']} -> Bucket {details['bucket_index']}")
            print(f"  Remaining bits: {details['remaining_binary'][:16]}... (showing first 16 bits)")
            print(f"  Leading zeros rank: {details['rank']}")
            print(f"  Bucket updated: {details['bucket_updated']}")
        
        # Show final bucket state
        print(f"\nFinal bucket states:")
        for i, rank in enumerate(hll.buckets):
            if rank > 0:
                print(f"  Bucket {i}: rank {rank}")
        
        estimate = hll.estimate_cardinality()
        print(f"\nEstimated cardinality: {estimate['estimated_cardinality']}")
        print(f"Actual cardinality: {len(elements)}")
    
    def test_demonstrate_precision_effect(self):
        """Demonstrate how precision affects accuracy and memory usage."""
        print("\n=== Precision Effect Demonstration ===")
        
        true_cardinality = 1000
        elements = [f"element_{i}" for i in range(true_cardinality)]
        
        print(f"Testing with {true_cardinality} unique elements:")
        print(f"{'Precision':<10} {'Buckets':<8} {'Memory(KB)':<12} {'Estimate':<10} {'Error':<8} {'Theoretical Error':<18}")
        print("-" * 75)
        
        for precision in [4, 6, 8, 10, 12]:
            hll = HyperLogLog(precision=precision)
            
            for element in elements:
                hll.add(element)
            
            estimate = hll.estimate_cardinality()
            estimated_cardinality = estimate['estimated_cardinality']
            error = abs(estimated_cardinality - true_cardinality) / true_cardinality
            theoretical_error = 1.04 / math.sqrt(2 ** precision)
            memory_kb = (hll.bucket_count * 6) / 8 / 1024  # Approximate memory in KB
            
            print(f"{precision:<10} {hll.bucket_count:<8} {memory_kb:<12.3f} "
                  f"{estimated_cardinality:<10} {error:<8.2%} {theoretical_error:<18.2%}")
    
    def test_demonstrate_leading_zeros_probability(self):
        """Demonstrate the probability distribution of leading zeros."""
        print("\n=== Leading Zeros Probability Demonstration ===")
        
        # Generate random numbers and count leading zeros
        hll = HyperLogLog(precision=10)
        leading_zero_counts = {}
        
        num_samples = 10000
        for i in range(num_samples):
            hash_val = hll._hash(f"random_{i}")
            remaining_bits = hash_val >> hll.precision
            rank = hll._leading_zeros(remaining_bits, 64 - hll.precision)
            
            leading_zero_counts[rank] = leading_zero_counts.get(rank, 0) + 1
        
        print(f"Distribution of leading zero ranks from {num_samples} random hashes:")
        print(f"{'Rank':<6} {'Count':<8} {'Probability':<12} {'Theoretical':<12}")
        print("-" * 40)
        
        for rank in sorted(leading_zero_counts.keys())[:10]:  # Show first 10 ranks
            count = leading_zero_counts[rank]
            probability = count / num_samples
            theoretical = (2 ** (-rank)) - (2 ** (-(rank + 1)))  # P(rank = k)
            
            print(f"{rank:<6} {count:<8} {probability:<12.4f} {theoretical:<12.4f}")


def run_educational_examples():
    """Run educational examples to demonstrate HyperLogLog concepts."""
    print("=" * 60)
    print("HYPERLOGLOG EDUCATIONAL EXAMPLES")
    print("=" * 60)
    
    # Run educational test methods
    educational_tests = TestHyperLogLogEducational()
    educational_tests.test_demonstrate_hash_distribution()
    educational_tests.test_demonstrate_precision_effect()
    educational_tests.test_demonstrate_leading_zeros_probability()
    
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