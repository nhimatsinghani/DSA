import unittest
import time
from key_value_store import EvolvingKeyValueStore


class TestStage4DeletionOperations(unittest.TestCase):
    """
    Stage 4: Deletion Operations Tests
    
    This stage adds deletion functionality to the key-value store.
    This was the stage where the original implementation had issues,
    so these tests focus on edge cases and proper deletion behavior.
    """
    
    def setUp(self):
        """Set up a fresh store for each test."""
        self.store = EvolvingKeyValueStore()
    
    def test_basic_deletion(self):
        """Test basic deletion functionality."""
        # Set a key and verify it exists
        self.store.set("test_key", "test_value")
        self.assertEqual(self.store.get("test_key"), "test_value")
        print(f"✓ Key set successfully: {self.store.get('test_key')}")
        
        # Delete the key
        result = self.store.delete("test_key")
        self.assertTrue(result)
        print(f"✓ Delete operation returned: {result}")
        
        # Verify key is gone
        result = self.store.get("test_key")
        self.assertIsNone(result)
        print(f"✓ Key after deletion: {result}")
    
    def test_delete_nonexistent_key(self):
        """Test deleting a key that doesn't exist."""
        result = self.store.delete("nonexistent_key")
        self.assertFalse(result)
        print(f"✓ Delete nonexistent key returned: {result}")
    
    def test_delete_already_deleted_key(self):
        """Test deleting a key that was already deleted."""
        # Set and delete a key
        self.store.set("deleteme", "value")
        first_delete = self.store.delete("deleteme")
        self.assertTrue(first_delete)
        print(f"✓ First delete returned: {first_delete}")
        
        # Try to delete again
        second_delete = self.store.delete("deleteme")
        self.assertFalse(second_delete)
        print(f"✓ Second delete returned: {second_delete}")
        
        # Key should still be None
        result = self.store.get("deleteme")
        self.assertIsNone(result)
        print(f"✓ Key remains deleted: {result}")
    
    def test_delete_with_history_queries(self):
        """Test deletion with point-in-time queries."""
        start_time = time.time()
        
        # Set a value
        self.store.set("historical", "before_deletion")
        time.sleep(0.1)
        before_deletion_time = time.time()
        
        # Delete the key
        deletion_time = time.time()
        delete_result = self.store.delete("historical")
        self.assertTrue(delete_result)
        time.sleep(0.1)
        after_deletion_time = time.time()
        
        # Current query should return None
        current_result = self.store.get("historical")
        self.assertIsNone(current_result)
        print(f"✓ Current query after deletion: {current_result}")
        
        # Historical query before deletion should return the value
        historical_result = self.store.get_at_time("historical", before_deletion_time)
        self.assertEqual(historical_result, "before_deletion")
        print(f"✓ Historical query before deletion: {historical_result}")
        
        # Historical query after deletion should return None
        post_deletion_result = self.store.get_at_time("historical", after_deletion_time)
        self.assertIsNone(post_deletion_result)
        print(f"✓ Historical query after deletion: {post_deletion_result}")
    
    def test_recreate_after_deletion(self):
        """Test recreating a key after it was deleted."""
        # Set, delete, then recreate
        self.store.set("phoenix", "first_life")
        self.assertEqual(self.store.get("phoenix"), "first_life")
        
        # Delete
        delete_result = self.store.delete("phoenix")
        self.assertTrue(delete_result)
        self.assertIsNone(self.store.get("phoenix"))
        print(f"✓ Key deleted successfully")
        
        # Recreate with new value
        self.store.set("phoenix", "second_life")
        result = self.store.get("phoenix")
        self.assertEqual(result, "second_life")
        print(f"✓ Key recreated with value: {result}")
        
        # Should be able to delete again
        second_delete = self.store.delete("phoenix")
        self.assertTrue(second_delete)
        self.assertIsNone(self.store.get("phoenix"))
        print(f"✓ Key deleted again successfully")
    
    def test_delete_with_ttl(self):
        """Test deleting keys that have TTL."""
        # Set with TTL
        self.store.set("ttl_key", "expires_soon", ttl=1.0)
        self.assertEqual(self.store.get("ttl_key"), "expires_soon")
        
        # Delete before expiration
        delete_result = self.store.delete("ttl_key")
        self.assertTrue(delete_result)
        print(f"✓ TTL key deleted before expiration")
        
        # Should be None immediately after deletion
        result = self.store.get("ttl_key")
        self.assertIsNone(result)
        print(f"✓ TTL key unavailable after deletion: {result}")
        
        # Should still be None after TTL would have expired
        time.sleep(0.1)  # Don't wait full TTL for test speed
        result = self.store.get("ttl_key")
        self.assertIsNone(result)
        print(f"✓ TTL key still unavailable: {result}")
    
    def test_delete_expired_key(self):
        """Test deleting a key that has already expired."""
        # Set with very short TTL
        self.store.set("expires_fast", "gone_soon", ttl=0.1)
        self.assertEqual(self.store.get("expires_fast"), "gone_soon")
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Verify it's expired
        self.assertIsNone(self.store.get("expires_fast"))
        
        # Try to delete expired key
        delete_result = self.store.delete("expires_fast")
        # This is a design decision - should return False since key doesn't "exist"
        self.assertFalse(delete_result)
        print(f"✓ Delete expired key returned: {delete_result}")
    
    def test_exists_method_with_deletion(self):
        """Test the exists method behavior with deletion."""
        # Set key
        self.store.set("existence_test", "here")
        self.assertTrue(self.store.exists("existence_test"))
        print(f"✓ Key exists before deletion")
        
        # Delete key
        self.store.delete("existence_test")
        self.assertFalse(self.store.exists("existence_test"))
        print(f"✓ Key doesn't exist after deletion")
        
        # Recreate key
        self.store.set("existence_test", "back")
        self.assertTrue(self.store.exists("existence_test"))
        print(f"✓ Key exists after recreation")
    
    def test_size_method_with_deletion(self):
        """Test size method behavior with deletion."""
        initial_size = self.store.size()
        
        # Add keys
        self.store.set("key1", "value1")
        self.store.set("key2", "value2")
        self.store.set("key3", "value3")
        self.assertEqual(self.store.size(), initial_size + 3)
        print(f"✓ Size after adding 3 keys: {self.store.size()}")
        
        # Delete one key
        self.store.delete("key2")
        self.assertEqual(self.store.size(), initial_size + 2)
        print(f"✓ Size after deleting 1 key: {self.store.size()}")
        
        # Delete all remaining keys
        self.store.delete("key1")
        self.store.delete("key3")
        self.assertEqual(self.store.size(), initial_size)
        print(f"✓ Size after deleting all keys: {self.store.size()}")
    
    def test_get_all_keys_with_deletion(self):
        """Test get_all_keys method behavior with deletion."""
        # Add some keys
        self.store.set("active1", "value1")
        self.store.set("active2", "value2")
        self.store.set("to_delete", "value3")
        
        keys = self.store.get_all_keys()
        self.assertIn("active1", keys)
        self.assertIn("active2", keys)
        self.assertIn("to_delete", keys)
        print(f"✓ All keys present: {sorted(keys)}")
        
        # Delete one key
        self.store.delete("to_delete")
        keys = self.store.get_all_keys()
        self.assertIn("active1", keys)
        self.assertIn("active2", keys)
        self.assertNotIn("to_delete", keys)
        print(f"✓ Deleted key not in list: {sorted(keys)}")
    
    def test_deletion_order_independence(self):
        """Test that deletion order doesn't affect results."""
        # Set multiple keys
        keys_values = [("order1", "val1"), ("order2", "val2"), ("order3", "val3")]
        for key, value in keys_values:
            self.store.set(key, value)
        
        # Verify all exist
        for key, value in keys_values:
            self.assertEqual(self.store.get(key), value)
        
        # Delete in different order
        delete_order = ["order2", "order1", "order3"]
        for key in delete_order:
            result = self.store.delete(key)
            self.assertTrue(result)
            self.assertIsNone(self.store.get(key))
            print(f"✓ Deleted {key} successfully")
        
        # All should be gone
        for key, _ in keys_values:
            self.assertIsNone(self.store.get(key))
        
        self.assertEqual(self.store.size(), 0)
        print(f"✓ All keys deleted, size is 0")
    
    def test_delete_with_complex_history(self):
        """Test deletion with complex update history."""
        # Create complex history
        self.store.set("complex", "v1")
        time.sleep(0.05)
        t1 = time.time()
        
        self.store.set("complex", "v2", ttl=10.0)
        time.sleep(0.05)
        t2 = time.time()
        
        self.store.set("complex", "v3")
        time.sleep(0.05)
        t3 = time.time()
        
        # Delete the key
        delete_result = self.store.delete("complex")
        self.assertTrue(delete_result)
        deletion_time = time.time()
        
        # Verify historical queries still work
        self.assertEqual(self.store.get_at_time("complex", t1), "v1")
        self.assertEqual(self.store.get_at_time("complex", t2), "v2")
        self.assertEqual(self.store.get_at_time("complex", t3), "v3")
        print(f"✓ Historical queries work after deletion")
        
        # But current and post-deletion queries return None
        self.assertIsNone(self.store.get("complex"))
        self.assertIsNone(self.store.get_at_time("complex", deletion_time + 0.01))
        print(f"✓ Current and post-deletion queries return None")
    
    def test_stress_deletion_operations(self):
        """Test many deletion operations to catch edge cases."""
        num_keys = 50
        
        # Create many keys
        for i in range(num_keys):
            self.store.set(f"stress_{i}", f"value_{i}")
        
        self.assertEqual(self.store.size(), num_keys)
        print(f"✓ Created {num_keys} keys")
        
        # Delete every other key
        deleted_count = 0
        for i in range(0, num_keys, 2):
            result = self.store.delete(f"stress_{i}")
            self.assertTrue(result)
            deleted_count += 1
        
        expected_remaining = num_keys - deleted_count
        self.assertEqual(self.store.size(), expected_remaining)
        print(f"✓ Deleted {deleted_count} keys, {expected_remaining} remaining")
        
        # Verify remaining keys are correct
        for i in range(num_keys):
            if i % 2 == 0:  # Should be deleted
                self.assertIsNone(self.store.get(f"stress_{i}"))
            else:  # Should still exist
                self.assertEqual(self.store.get(f"stress_{i}"), f"value_{i}")
        
        print(f"✓ All remaining keys have correct values")


def run_stage4_tests():
    """Run Stage 4 tests with detailed output for debugging."""
    print("=" * 60)
    print("STAGE 4: DELETION OPERATIONS TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage4DeletionOperations)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ STAGE 4: ALL TESTS PASSED!")
    else:
        print("❌ STAGE 4: SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_stage4_tests() 