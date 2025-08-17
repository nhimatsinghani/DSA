import unittest
import time
from key_value_store import EvolvingKeyValueStore


class TestStage3PointInTimeQueries(unittest.TestCase):
    """
    Stage 3: Point-in-Time Queries Tests
    
    This stage adds the ability to query the value of keys at specific points in time,
    maintaining a history of all changes to each key.
    """
    
    def setUp(self):
        """Set up a fresh store for each test."""
        self.store = EvolvingKeyValueStore()
    
    def test_basic_history_tracking(self):
        """Test basic history tracking for a single key."""
        start_time = time.time()
        
        # Set initial value
        self.store.set_with_history("user_status", "offline")
        time.sleep(0.1)
        timestamp1 = time.time()
        
        # Update value
        self.store.set_with_history("user_status", "online")
        time.sleep(0.1)
        timestamp2 = time.time()
        
        # Update again
        self.store.set_with_history("user_status", "away")
        
        # Test current value
        current = self.store.get_current_with_history("user_status")
        self.assertEqual(current, "away")
        print(f"✓ Current value: {current}")
        
        # Test historical values
        value_at_start = self.store.get_at_time("user_status", timestamp1 - 0.05)
        self.assertEqual(value_at_start, "offline")
        print(f"✓ Value at start: {value_at_start}")
        
        value_at_middle = self.store.get_at_time("user_status", timestamp2 - 0.05)
        self.assertEqual(value_at_middle, "online")
        print(f"✓ Value in middle: {value_at_middle}")
        
        value_at_end = self.store.get_at_time("user_status", timestamp2 + 0.05)
        self.assertEqual(value_at_end, "away")
        print(f"✓ Value at end: {value_at_end}")
    
    def test_query_before_key_creation(self):
        """Test querying before a key was created."""
        query_time = time.time()
        time.sleep(0.1)
        
        # Create key after query time
        self.store.set_with_history("new_key", "new_value")
        
        # Query before creation should return None
        result = self.store.get_at_time("new_key", query_time)
        self.assertIsNone(result)
        print(f"✓ Query before creation returns: {result}")
        
        # Query after creation should return value
        result = self.store.get_at_time("new_key", time.time())
        self.assertEqual(result, "new_value")
        print(f"✓ Query after creation returns: {result}")
    
    def test_query_nonexistent_key(self):
        """Test querying a key that never existed."""
        result = self.store.get_at_time("never_existed", time.time())
        self.assertIsNone(result)
        print(f"✓ Query nonexistent key returns: {result}")
    
    def test_history_with_ttl(self):
        """Test point-in-time queries with TTL values."""
        start_time = time.time()
        
        # Set value with TTL
        self.store.set_with_history("session", "active", ttl=0.2)
        time.sleep(0.1)
        middle_time = time.time()
        
        # Value should be available at middle time (before expiration)
        result = self.store.get_at_time("session", middle_time)
        self.assertEqual(result, "active")
        print(f"✓ Value available before TTL expiration: {result}")
        
        # Wait for expiration
        time.sleep(0.2)
        end_time = time.time()
        
        # Value should not be available at end time (after expiration)
        result = self.store.get_at_time("session", end_time)
        self.assertIsNone(result)
        print(f"✓ Value unavailable after TTL expiration: {result}")
        
        # But historical query at valid time should still work
        result = self.store.get_at_time("session", start_time + 0.05)
        self.assertEqual(result, "active")
        print(f"✓ Historical query within TTL window works: {result}")
    
    def test_multiple_updates_same_key(self):
        """Test multiple rapid updates to the same key."""
        timestamps = []
        values = ["v1", "v2", "v3", "v4", "v5"]
        
        for i, value in enumerate(values):
            self.store.set_with_history("rapid_updates", value)
            timestamps.append(time.time())
            if i < len(values) - 1:  # Don't sleep after last update
                time.sleep(0.05)
        
        # Test each historical value
        for i, (timestamp, expected_value) in enumerate(zip(timestamps, values)):
            # Query slightly after each timestamp
            result = self.store.get_at_time("rapid_updates", timestamp + 0.01)
            self.assertEqual(result, expected_value)
            print(f"✓ Update {i+1}: {result}")
        
        # Current value should be the last one
        current = self.store.get_current_with_history("rapid_updates")
        self.assertEqual(current, values[-1])
        print(f"✓ Final current value: {current}")
    
    def test_overwrite_ttl_in_history(self):
        """Test overwriting TTL values and their effect on history."""
        start_time = time.time()
        
        # Set with long TTL
        self.store.set_with_history("evolving_ttl", "long_lived", ttl=10.0)
        time.sleep(0.1)
        timestamp1 = time.time()
        
        # Overwrite with short TTL
        self.store.set_with_history("evolving_ttl", "short_lived", ttl=0.1)
        time.sleep(0.05)
        timestamp2 = time.time()
        
        # Before short TTL expires
        result = self.store.get_at_time("evolving_ttl", timestamp2)
        self.assertEqual(result, "short_lived")
        print(f"✓ New value available before its TTL expires: {result}")
        
        # Historical query for old value (should work even though key was overwritten)
        result = self.store.get_at_time("evolving_ttl", timestamp1)
        self.assertEqual(result, "long_lived")
        print(f"✓ Historical value available: {result}")
        
        # Wait for short TTL to expire
        time.sleep(0.1)
        
        # Current query should return None (expired)
        result = self.store.get_current_with_history("evolving_ttl")
        self.assertIsNone(result)
        print(f"✓ Current query after expiration: {result}")
        
        # But historical query within the valid window should still work
        result = self.store.get_at_time("evolving_ttl", timestamp2 - 0.02)
        self.assertEqual(result, "short_lived")
        print(f"✓ Historical query within valid window: {result}")
    
    def test_mixed_ttl_and_permanent_values(self):
        """Test mixing permanent and TTL values in history."""
        # Set permanent value
        self.store.set_with_history("mixed_key", "permanent_value")
        time.sleep(0.1)
        timestamp1 = time.time()
        
        # Overwrite with TTL value
        self.store.set_with_history("mixed_key", "temporary_value", ttl=0.1)
        time.sleep(0.05)
        timestamp2 = time.time()
        
        # Overwrite with permanent value again
        self.store.set_with_history("mixed_key", "permanent_again")
        
        # Test all historical values
        result1 = self.store.get_at_time("mixed_key", timestamp1 - 0.05)
        self.assertEqual(result1, "permanent_value")
        print(f"✓ First permanent value: {result1}")
        
        result2 = self.store.get_at_time("mixed_key", timestamp2)
        self.assertEqual(result2, "temporary_value")
        print(f"✓ Temporary value in middle: {result2}")
        
        result3 = self.store.get_current_with_history("mixed_key")
        self.assertEqual(result3, "permanent_again")
        print(f"✓ Final permanent value: {result3}")
        
        # Wait for temporary TTL to "expire" (shouldn't affect current value)
        time.sleep(0.1)
        result4 = self.store.get_current_with_history("mixed_key")
        self.assertEqual(result4, "permanent_again")
        print(f"✓ Current value unaffected by past TTL: {result4}")
    
    def test_multiple_keys_independent_history(self):
        """Test that multiple keys maintain independent histories."""
        # Set up different timelines for different keys
        self.store.set_with_history("user1", "offline")
        self.store.set_with_history("user2", "busy")
        time.sleep(0.1)
        timestamp1 = time.time()
        
        self.store.set_with_history("user1", "online")  # Only user1 changes
        time.sleep(0.1)
        timestamp2 = time.time()
        
        self.store.set_with_history("user2", "available")  # Only user2 changes
        
        # Verify independent histories
        # user1 at timestamp1 should be "offline"
        result = self.store.get_at_time("user1", timestamp1 - 0.05)
        self.assertEqual(result, "offline")
        print(f"✓ user1 at timestamp1: {result}")
        
        # user2 at timestamp1 should be "busy"
        result = self.store.get_at_time("user2", timestamp1 - 0.05)
        self.assertEqual(result, "busy")
        print(f"✓ user2 at timestamp1: {result}")
        
        # user1 at timestamp2 should be "online"
        result = self.store.get_at_time("user1", timestamp2 - 0.05)
        self.assertEqual(result, "online")
        print(f"✓ user1 at timestamp2: {result}")
        
        # user2 at timestamp2 should still be "busy"
        result = self.store.get_at_time("user2", timestamp2 - 0.05)
        self.assertEqual(result, "busy")
        print(f"✓ user2 at timestamp2: {result}")
    
    def test_precise_timestamp_queries(self):
        """Test precise timestamp queries around update times."""
        # Record exact timestamps
        before_time = time.time()
        time.sleep(0.01)
        
        self.store.set_with_history("precise", "first_value")
        update_time = time.time()
        time.sleep(0.01)
        
        self.store.set_with_history("precise", "second_value")
        second_update_time = time.time()
        time.sleep(0.01)
        
        after_time = time.time()
        
        # Query just before first update
        result = self.store.get_at_time("precise", before_time)
        self.assertIsNone(result)
        print(f"✓ Before any update: {result}")
        
        # Query just after first update
        result = self.store.get_at_time("precise", update_time + 0.001)
        self.assertEqual(result, "first_value")
        print(f"✓ After first update: {result}")
        
        # Query just after second update
        result = self.store.get_at_time("precise", second_update_time + 0.001)
        self.assertEqual(result, "second_value")
        print(f"✓ After second update: {result}")
        
        # Query well after all updates
        result = self.store.get_at_time("precise", after_time)
        self.assertEqual(result, "second_value")
        print(f"✓ Well after updates: {result}")


def run_stage3_tests():
    """Run Stage 3 tests with detailed output for debugging."""
    print("=" * 60)
    print("STAGE 3: POINT-IN-TIME QUERIES TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage3PointInTimeQueries)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ STAGE 3: ALL TESTS PASSED!")
    else:
        print("❌ STAGE 3: SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_stage3_tests() 