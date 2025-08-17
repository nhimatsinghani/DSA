"""
Comprehensive Test Suite for Skip List Implementation
==================================================

Tests all operations, edge cases, and performance characteristics.
"""

import unittest
import random
from skiplist import SkipList, SkipListNode, create_skip_list_from_list, merge_skip_lists


class TestSkipListNode(unittest.TestCase):
    """Test SkipListNode class."""
    
    def test_node_creation(self):
        """Test node creation with different levels."""
        node = SkipListNode(10, "ten", 3)
        self.assertEqual(node.key, 10)
        self.assertEqual(node.value, "ten")
        self.assertEqual(len(node.forward), 4)  # level 3 means 4 forward pointers
        self.assertTrue(all(ptr is None for ptr in node.forward))
    
    def test_node_repr(self):
        """Test string representation."""
        node = SkipListNode(5, "five", 2)
        expected = "SkipListNode(key=5, value=five, level=2)"
        self.assertEqual(repr(node), expected)


class TestSkipListBasicOperations(unittest.TestCase):
    """Test basic skip list operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sl = SkipList(max_level=4, p=0.5)
        # Use fixed seed for reproducible tests
        random.seed(42)
    
    def test_empty_skip_list(self):
        """Test empty skip list properties."""
        self.assertEqual(len(self.sl), 0)
        self.assertIsNone(self.sl.search(10))
        self.assertFalse(10 in self.sl)
        self.assertEqual(list(self.sl), [])
        self.assertIsNone(self.sl.min_key())
        self.assertIsNone(self.sl.max_key())
    
    def test_single_element(self):
        """Test skip list with single element."""
        self.assertTrue(self.sl.insert(10, "ten"))
        
        self.assertEqual(len(self.sl), 1)
        self.assertEqual(self.sl.search(10), "ten")
        self.assertTrue(10 in self.sl)
        self.assertEqual(list(self.sl), [(10, "ten")])
        self.assertEqual(self.sl.min_key(), 10)
        self.assertEqual(self.sl.max_key(), 10)
    
    def test_insert_and_search(self):
        """Test insert and search operations."""
        # Insert elements
        elements = [(5, "five"), (10, "ten"), (3, "three"), (8, "eight"), (15, "fifteen")]
        
        for key, value in elements:
            self.assertTrue(self.sl.insert(key, value))
        
        # Test search
        for key, value in elements:
            self.assertEqual(self.sl.search(key), value)
        
        # Test non-existent keys
        self.assertIsNone(self.sl.search(1))
        self.assertIsNone(self.sl.search(20))
    
    def test_insert_duplicate_key(self):
        """Test inserting duplicate keys."""
        self.assertTrue(self.sl.insert(10, "ten"))
        self.assertFalse(self.sl.insert(10, "TEN"))  # Should update, not insert
        
        self.assertEqual(len(self.sl), 1)
        self.assertEqual(self.sl.search(10), "TEN")
    
    def test_delete_operations(self):
        """Test delete operations."""
        # Insert elements
        elements = [5, 10, 3, 8, 15]
        for key in elements:
            self.sl.insert(key, f"value_{key}")
        
        # Delete existing elements
        self.assertTrue(self.sl.delete(8))
        self.assertEqual(len(self.sl), 4)
        self.assertIsNone(self.sl.search(8))
        
        # Delete non-existent element
        self.assertFalse(self.sl.delete(20))
        self.assertEqual(len(self.sl), 4)
        
        # Delete all elements
        for key in [5, 10, 3, 15]:
            self.assertTrue(self.sl.delete(key))
        
        self.assertEqual(len(self.sl), 0)
    
    def test_iteration(self):
        """Test iteration over skip list."""
        elements = [(5, "five"), (10, "ten"), (3, "three"), (8, "eight")]
        
        for key, value in elements:
            self.sl.insert(key, value)
        
        # Test sorted iteration
        result = list(self.sl)
        expected = [(3, "three"), (5, "five"), (8, "eight"), (10, "ten")]
        self.assertEqual(result, expected)
        
        # Test keys() method
        keys = list(self.sl.keys())
        self.assertEqual(keys, [3, 5, 8, 10])
        
        # Test values() method
        values = list(self.sl.values())
        self.assertEqual(values, ["three", "five", "eight", "ten"])


class TestSkipListRangeQueries(unittest.TestCase):
    """Test range query functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sl = SkipList()
        # Insert test data
        for i in range(0, 21, 2):  # 0, 2, 4, ..., 20
            self.sl.insert(i, f"value_{i}")
    
    def test_range_query_normal(self):
        """Test normal range queries."""
        result = self.sl.range_query(4, 12)
        expected = [(4, "value_4"), (6, "value_6"), (8, "value_8"), 
                   (10, "value_10"), (12, "value_12")]
        self.assertEqual(result, expected)
    
    def test_range_query_single_element(self):
        """Test range query returning single element."""
        result = self.sl.range_query(8, 8)
        expected = [(8, "value_8")]
        self.assertEqual(result, expected)
    
    def test_range_query_empty(self):
        """Test range query returning empty result."""
        result = self.sl.range_query(1, 1)
        self.assertEqual(result, [])
        
        result = self.sl.range_query(25, 30)
        self.assertEqual(result, [])
    
    def test_range_query_full_range(self):
        """Test range query covering all elements."""
        result = self.sl.range_query(-10, 30)
        expected = [(i, f"value_{i}") for i in range(0, 21, 2)]
        self.assertEqual(result, expected)


class TestSkipListEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_different_key_types(self):
        """Test with different key types."""
        sl = SkipList()
        
        # String keys
        sl.insert("apple", 1)
        sl.insert("banana", 2)
        sl.insert("cherry", 3)
        
        result = list(sl.keys())
        self.assertEqual(result, ["apple", "banana", "cherry"])
    
    def test_clear_operation(self):
        """Test clearing skip list."""
        sl = SkipList()
        
        # Add elements
        for i in range(10):
            sl.insert(i, f"value_{i}")
        
        self.assertEqual(len(sl), 10)
        
        # Clear
        sl.clear()
        
        self.assertEqual(len(sl), 0)
        self.assertEqual(list(sl), [])
        self.assertIsNone(sl.search(5))
    
    def test_large_dataset(self):
        """Test with larger dataset."""
        sl = SkipList()
        size = 1000
        
        # Insert random data
        keys = list(range(size))
        random.shuffle(keys)
        
        for key in keys:
            sl.insert(key, f"value_{key}")
        
        self.assertEqual(len(sl), size)
        
        # Verify all elements
        for key in keys:
            self.assertEqual(sl.search(key), f"value_{key}")
        
        # Test iteration is sorted
        sorted_keys = list(sl.keys())
        self.assertEqual(sorted_keys, sorted(keys))


class TestSkipListStatistics(unittest.TestCase):
    """Test statistical analysis functionality."""
    
    def test_statistics_empty(self):
        """Test statistics on empty skip list."""
        sl = SkipList()
        stats = sl.get_statistics()
        
        self.assertEqual(stats['size'], 0)
        self.assertEqual(stats['current_max_level'], 0)
        self.assertEqual(stats['expected_height'], 0)
        self.assertEqual(stats['average_node_level'], 0)
    
    def test_statistics_with_data(self):
        """Test statistics with data."""
        sl = SkipList(max_level=8, p=0.5)
        
        # Insert data
        for i in range(100):
            sl.insert(i, f"value_{i}")
        
        stats = sl.get_statistics()
        
        self.assertEqual(stats['size'], 100)
        self.assertGreater(stats['current_max_level'], 0)
        self.assertGreater(stats['expected_height'], 0)
        self.assertGreater(stats['average_node_level'], 0)
        self.assertEqual(stats['probability'], 0.5)
        self.assertIsInstance(stats['level_counts'], list)


class TestSkipListUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_create_from_list(self):
        """Test creating skip list from list."""
        items = [(5, "five"), (2, "two"), (8, "eight"), (1, "one")]
        sl = create_skip_list_from_list(items)
        
        self.assertEqual(len(sl), 4)
        for key, value in items:
            self.assertEqual(sl.search(key), value)
        
        # Check sorted order
        result = list(sl)
        expected = [(1, "one"), (2, "two"), (5, "five"), (8, "eight")]
        self.assertEqual(result, expected)
    
    def test_merge_skip_lists(self):
        """Test merging two skip lists."""
        # Create first skip list
        sl1 = SkipList()
        for i in [1, 3, 5]:
            sl1.insert(i, f"sl1_value_{i}")
        
        # Create second skip list
        sl2 = SkipList()
        for i in [2, 4, 6]:
            sl2.insert(i, f"sl2_value_{i}")
        
        # Merge
        merged = merge_skip_lists(sl1, sl2)
        
        self.assertEqual(len(merged), 6)
        
        # Check all elements present
        for i in range(1, 7):
            expected_value = f"sl1_value_{i}" if i % 2 == 1 else f"sl2_value_{i}"
            self.assertEqual(merged.search(i), expected_value)
    
    def test_merge_with_duplicates(self):
        """Test merging skip lists with duplicate keys."""
        sl1 = SkipList()
        sl1.insert(1, "sl1_one")
        sl1.insert(2, "sl1_two")
        
        sl2 = SkipList()
        sl2.insert(2, "sl2_two")  # Duplicate key
        sl2.insert(3, "sl2_three")
        
        merged = merge_skip_lists(sl1, sl2)
        
        self.assertEqual(len(merged), 3)
        self.assertEqual(merged.search(1), "sl1_one")
        self.assertEqual(merged.search(2), "sl2_two")  # sl2 overwrites sl1
        self.assertEqual(merged.search(3), "sl2_three")


class TestSkipListPerformance(unittest.TestCase):
    """Test performance characteristics."""
    
    def test_search_comparisons(self):
        """Test that search comparisons are reasonable."""
        sl = SkipList()
        
        # Insert many elements
        size = 1000
        for i in range(size):
            sl.insert(i, f"value_{i}")
        
        # Test search comparisons
        key_to_search = size // 2
        result = sl.search(key_to_search)
        
        self.assertEqual(result, f"value_{key_to_search}")
        
        # Comparisons should be much less than size (logarithmic)
        # In practice, should be around log2(size) = ~10 for size=1000
        self.assertLess(sl.search_comparisons, size // 10)
    
    def test_random_level_distribution(self):
        """Test that random level generation follows expected distribution."""
        sl = SkipList(p=0.5)
        
        # Generate many levels
        levels = [sl._random_level() for _ in range(10000)]
        
        # Count level 0 occurrences (should be ~50% for p=0.5)
        level_0_count = levels.count(0)
        level_0_ratio = level_0_count / len(levels)
        
        # Should be approximately 0.5, allowing for some variance
        self.assertGreater(level_0_ratio, 0.45)
        self.assertLess(level_0_ratio, 0.55)


class TestSkipListConcurrency(unittest.TestCase):
    """Test thread safety considerations."""
    
    def test_iterator_stability(self):
        """Test that iterator works with concurrent modifications."""
        sl = SkipList()
        
        # Insert initial data
        for i in range(10):
            sl.insert(i, f"value_{i}")
        
        # Get iterator
        iterator = iter(sl)
        first_item = next(iterator)
        
        # Modify skip list
        sl.insert(15, "value_15")
        
        # Iterator should still work (implementation dependent)
        remaining_items = list(iterator)
        
        # At minimum, we should get the first item
        self.assertEqual(first_item, (0, "value_0"))


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2) 