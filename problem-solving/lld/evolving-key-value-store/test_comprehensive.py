import unittest
import time
from key_value_store import EvolvingKeyValueStore


class TestEvolvingKeyValueStore(unittest.TestCase):
    """Comprehensive test suite for all 4 stages of the evolving key-value store."""
    
    def setUp(self):
        """Set up a fresh store for each test."""
        self.store = EvolvingKeyValueStore()
    
    # ==================== STAGE 1: Basic Operations Tests ====================
    
    def test_stage1_basic_set_get(self):
        """Test basic set and get operations."""
        # Test setting and getting a value
        self.store.set_basic("key1", "value1")
        self.assertEqual(self.store.get_basic("key1"), "value1")
        
        # Test getting non-existent key
        self.assertIsNone(self.store.get_basic("nonexistent"))
        
        # Test overwriting a value
        self.store.set_basic("key1", "new_value1")
        self.assertEqual(self.store.get_basic("key1"), "new_value1")
    
    def test_stage1_multiple_keys(self):
        """Test multiple key operations."""
        keys_values = [("key1", "value1"), ("key2", 42), ("key3", [1, 2, 3]), ("key4", {"nested": "dict"})]
        
        # Set multiple keys
        for key, value in keys_values:
            self.store.set_basic(key, value)
        
        # Verify all keys
        for key, expected_value in keys_values:
            self.assertEqual(self.store.get_basic(key), expected_value)
    
    # ==================== STAGE 2: TTL Operations Tests ====================
    
    def test_stage2_ttl_basic(self):
        """Test basic TTL functionality."""
        # Set without TTL
        self.store.set_with_ttl("key1", "value1")
        self.assertEqual(self.store.get_with_ttl("key1"), "value1")
        
        # Set with TTL that hasn't expired
        self.store.set_with_ttl("key2", "value2", ttl=10.0)
        self.assertEqual(self.store.get_with_ttl("key2"), "value2")
    
    def test_stage2_ttl_expiration(self):
        """Test TTL expiration."""
        # Set with very short TTL
        self.store.set_with_ttl("short_ttl", "value", ttl=0.1)
        self.assertEqual(self.store.get_with_ttl("short_ttl"), "value")
        
        # Wait for expiration
        time.sleep(0.2)
        self.assertIsNone(self.store.get_with_ttl("short_ttl"))
    
    def test_stage2_ttl_overwrite(self):
        """Test overwriting TTL values."""
        # Set with TTL
        self.store.set_with_ttl("key1", "value1", ttl=10.0)
        self.assertEqual(self.store.get_with_ttl("key1"), "value1")
        
        # Overwrite with different TTL
        self.store.set_with_ttl("key1", "value2", ttl=0.1)
        self.assertEqual(self.store.get_with_ttl("key1"), "value2")
        
        # Wait for new TTL to expire
        time.sleep(0.2)
        self.assertIsNone(self.store.get_with_ttl("key1"))
    
    # ==================== STAGE 3: Point-in-Time Tests ====================
    
    def test_stage3_history_basic(self):
        """Test basic history functionality."""
        start_time = time.time()
        
        # Set initial value
        self.store.set_with_history("key1", "value1")
        time.sleep(0.1)
        
        # Set second value
        self.store.set_with_history("key1", "value2")
        time.sleep(0.1)
        
        # Set third value
        self.store.set_with_history("key1", "value3")
        
        # Test current value
        self.assertEqual(self.store.get_current_with_history("key1"), "value3")
        
        # Test point-in-time queries
        self.assertEqual(self.store.get_at_time("key1", start_time + 0.05), "value1")
        self.assertEqual(self.store.get_at_time("key1", start_time + 0.15), "value2")
        self.assertEqual(self.store.get_at_time("key1", time.time()), "value3")
    
    def test_stage3_history_with_ttl(self):
        """Test history with TTL."""
        start_time = time.time()
        
        # Set value with TTL
        self.store.set_with_history("key1", "value1", ttl=0.2)
        time.sleep(0.1)
        
        # Value should be available before expiration
        self.assertEqual(self.store.get_at_time("key1", start_time + 0.1), "value1")
        
        # Value should not be available after expiration
        time.sleep(0.2)
        self.assertIsNone(self.store.get_at_time("key1", time.time()))
    
    def test_stage3_history_nonexistent_key(self):
        """Test point-in-time query for non-existent key."""
        self.assertIsNone(self.store.get_at_time("nonexistent", time.time()))
    
    def test_stage3_history_before_creation(self):
        """Test querying before key creation."""
        current_time = time.time()
        time.sleep(0.1)
        
        self.store.set_with_history("key1", "value1")
        
        # Query before key was created
        self.assertIsNone(self.store.get_at_time("key1", current_time))
    
    # ==================== STAGE 4: Deletion Tests ====================
    
    def test_stage4_delete_basic(self):
        """Test basic deletion functionality."""
        # Set and verify key exists
        self.store.set("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        # Delete key
        self.assertTrue(self.store.delete("key1"))
        self.assertIsNone(self.store.get("key1"))
        
        # Try to delete again (should return False)
        self.assertFalse(self.store.delete("key1"))
    
    def test_stage4_delete_nonexistent(self):
        """Test deleting non-existent key."""
        self.assertFalse(self.store.delete("nonexistent"))
    
    def test_stage4_delete_with_history(self):
        """Test deletion with historical queries."""
        start_time = time.time()
        
        # Set value
        self.store.set("key1", "value1")
        time.sleep(0.1)
        
        deletion_time = time.time()
        # Delete key
        self.assertTrue(self.store.delete("key1"))
        
        # Current query should return None
        self.assertIsNone(self.store.get("key1"))
        
        # Historical query before deletion should return value
        self.assertEqual(self.store.get_at_time("key1", deletion_time - 0.05), "value1")
        
        # Historical query after deletion should return None
        self.assertIsNone(self.store.get_at_time("key1", deletion_time + 0.1))
    
    def test_stage4_recreate_after_delete(self):
        """Test recreating a key after deletion."""
        # Set, delete, then set again
        self.store.set("key1", "value1")
        self.assertTrue(self.store.delete("key1"))
        self.assertIsNone(self.store.get("key1"))
        
        # Recreate key
        self.store.set("key1", "new_value")
        self.assertEqual(self.store.get("key1"), "new_value")
        
        # Should be able to delete again
        self.assertTrue(self.store.delete("key1"))
        self.assertIsNone(self.store.get("key1"))
    
    # ==================== UNIFIED INTERFACE Tests ====================
    
    def test_unified_interface(self):
        """Test the unified set/get interface that works for all stages."""
        # Basic operation
        self.store.set("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        # With TTL
        self.store.set("key2", "value2", ttl=0.1)
        self.assertEqual(self.store.get("key2"), "value2")
        time.sleep(0.2)
        self.assertIsNone(self.store.get("key2"))
        
        # With deletion
        self.store.set("key3", "value3")
        self.assertTrue(self.store.delete("key3"))
        self.assertIsNone(self.store.get("key3"))
    
    # ==================== UTILITY METHODS Tests ====================
    
    def test_exists_method(self):
        """Test the exists utility method."""
        # Non-existent key
        self.assertFalse(self.store.exists("nonexistent"))
        
        # Existing key
        self.store.set("key1", "value1")
        self.assertTrue(self.store.exists("key1"))
        
        # Deleted key
        self.store.delete("key1")
        self.assertFalse(self.store.exists("key1"))
        
        # Expired key
        self.store.set("key2", "value2", ttl=0.1)
        self.assertTrue(self.store.exists("key2"))
        time.sleep(0.2)
        self.assertFalse(self.store.exists("key2"))
    
    def test_get_all_keys(self):
        """Test getting all valid keys."""
        # Empty store
        self.assertEqual(self.store.get_all_keys(), [])
        
        # Add some keys
        self.store.set("key1", "value1")
        self.store.set("key2", "value2")
        self.store.set("key3", "value3", ttl=10.0)
        
        keys = self.store.get_all_keys()
        self.assertEqual(len(keys), 3)
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)
        self.assertIn("key3", keys)
        
        # Delete one key
        self.store.delete("key2")
        keys = self.store.get_all_keys()
        self.assertEqual(len(keys), 2)
        self.assertNotIn("key2", keys)
    
    def test_size_method(self):
        """Test the size utility method."""
        self.assertEqual(self.store.size(), 0)
        
        self.store.set("key1", "value1")
        self.assertEqual(self.store.size(), 1)
        
        self.store.set("key2", "value2")
        self.assertEqual(self.store.size(), 2)
        
        self.store.delete("key1")
        self.assertEqual(self.store.size(), 1)
        
        self.store.set("key3", "value3", ttl=0.1)
        self.assertEqual(self.store.size(), 2)
        
        time.sleep(0.2)
        # Size might still be 2 until cleanup is called or get is accessed
        self.store.cleanup_expired()
        self.assertEqual(self.store.size(), 1)
    
    def test_clear_method(self):
        """Test the clear utility method."""
        # Add some data
        self.store.set("key1", "value1")
        self.store.set("key2", "value2", ttl=10.0)
        self.store.delete("key1")
        
        self.assertGreater(len(self.store.history), 0)
        
        # Clear everything
        self.store.clear()
        
        self.assertEqual(len(self.store.data), 0)
        self.assertEqual(len(self.store.ttl_data), 0)
        self.assertEqual(len(self.store.history), 0)
        self.assertEqual(len(self.store.deleted_keys), 0)
        self.assertEqual(self.store.size(), 0)
    
    # ==================== EDGE CASES Tests ====================
    
    def test_edge_cases_data_types(self):
        """Test various data types as values."""
        test_cases = [
            ("string", "hello"),
            ("int", 42),
            ("float", 3.14),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value"}),
            ("none", None),
            ("bool", True),
            ("tuple", (1, 2, 3)),
        ]
        
        for key, value in test_cases:
            self.store.set(key, value)
            self.assertEqual(self.store.get(key), value)
    
    def test_edge_cases_empty_string_key(self):
        """Test empty string as key."""
        self.store.set("", "empty_key_value")
        self.assertEqual(self.store.get(""), "empty_key_value")
    
    def test_edge_cases_zero_ttl(self):
        """Test zero TTL (should expire immediately)."""
        self.store.set("key1", "value1", ttl=0.0)
        # Should be expired almost immediately
        time.sleep(0.01)
        self.assertIsNone(self.store.get("key1"))
    
    def test_edge_cases_negative_ttl(self):
        """Test negative TTL (should be treated as expired)."""
        self.store.set("key1", "value1", ttl=-1.0)
        self.assertIsNone(self.store.get("key1"))
    
    # ==================== INTEGRATION Tests ====================
    
    def test_integration_complex_scenario(self):
        """Test a complex scenario involving all operations."""
        start_time = time.time()
        
        # Stage 1: Set some basic values
        self.store.set("user:1", {"name": "Alice", "age": 30})
        self.store.set("user:2", {"name": "Bob", "age": 25})
        
        time.sleep(0.1)
        
        # Stage 2: Set with TTL
        self.store.set("session:abc", "active", ttl=0.3)
        self.store.set("cache:data", "cached_value", ttl=1.0)
        
        time.sleep(0.1)
        
        # Stage 3: Update existing values (creating history)
        self.store.set("user:1", {"name": "Alice Smith", "age": 31})
        
        time.sleep(0.1)
        
        # Stage 4: Delete some keys
        self.assertTrue(self.store.delete("user:2"))
        
        # Verify current state
        self.assertEqual(self.store.get("user:1")["name"], "Alice Smith")
        self.assertIsNone(self.store.get("user:2"))
        self.assertEqual(self.store.get("session:abc"), "active")
        self.assertEqual(self.store.get("cache:data"), "cached_value")
        
        # Test historical queries
        old_user_data = self.store.get_at_time("user:1", start_time + 0.05)
        self.assertEqual(old_user_data["name"], "Alice")
        
        deleted_user_data = self.store.get_at_time("user:2", start_time + 0.15)
        self.assertEqual(deleted_user_data["name"], "Bob")
        
        # Wait for session to expire
        time.sleep(0.3)
        self.assertIsNone(self.store.get("session:abc"))
        
        # Verify final state
        self.assertEqual(self.store.size(), 2)  # user:1 and cache:data
        
        # Clear and verify empty
        self.store.clear()
        self.assertEqual(self.store.size(), 0)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2) 