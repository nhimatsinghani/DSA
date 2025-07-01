import unittest
import time
from key_value_store import EvolvingKeyValueStore


class TestStage2TTLOperations(unittest.TestCase):
    """
    Stage 2: TTL (Time-To-Live) Operations Tests
    
    This stage adds TTL functionality to the key-value store,
    allowing keys to automatically expire after a specified time.
    """
    
    def setUp(self):
        """Set up a fresh store for each test."""
        self.store = EvolvingKeyValueStore()
    
    def test_set_without_ttl(self):
        """Test setting values without TTL (should never expire)."""
        self.store.set_with_ttl("permanent_key", "permanent_value")
        
        # Should be available immediately
        result = self.store.get_with_ttl("permanent_key")
        self.assertEqual(result, "permanent_value")
        
        # Should still be available after some time
        time.sleep(0.1)
        result = self.store.get_with_ttl("permanent_key")
        self.assertEqual(result, "permanent_value")
        
        print(f"✓ Key without TTL persists: {result}")
    
    def test_set_with_long_ttl(self):
        """Test setting values with long TTL."""
        # Set with 10 second TTL
        self.store.set_with_ttl("long_lived", "value", ttl=10.0)
        
        result = self.store.get_with_ttl("long_lived")
        self.assertEqual(result, "value")
        
        # Should still be available after short wait
        time.sleep(0.1)
        result = self.store.get_with_ttl("long_lived")
        self.assertEqual(result, "value")
        
        print(f"✓ Key with long TTL (10s) is available: {result}")
    
    def test_ttl_expiration(self):
        """Test that keys expire after TTL."""
        # Set with very short TTL
        self.store.set_with_ttl("short_lived", "expires_soon", ttl=0.1)
        
        # Should be available immediately
        result = self.store.get_with_ttl("short_lived")
        self.assertEqual(result, "expires_soon")
        print(f"✓ Key available immediately: {result}")
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be None after expiration
        result = self.store.get_with_ttl("short_lived")
        self.assertIsNone(result)
        print(f"✓ Key expired after TTL: {result}")
    
    def test_ttl_precision(self):
        """Test TTL precision with more exact timing."""
        start_time = time.time()
        ttl_duration = 0.15
        
        self.store.set_with_ttl("precision_test", "timing_value", ttl=ttl_duration)
        
        # Check at intervals
        time.sleep(0.05)  # Should still be available
        self.assertIsNotNone(self.store.get_with_ttl("precision_test"))
        print(f"✓ Key available at t+50ms")
        
        time.sleep(0.05)  # 100ms total, should still be available
        self.assertIsNotNone(self.store.get_with_ttl("precision_test"))
        print(f"✓ Key available at t+100ms")
        
        time.sleep(0.1)   # 200ms total, should be expired
        self.assertIsNone(self.store.get_with_ttl("precision_test"))
        print(f"✓ Key expired at t+200ms")
    
    def test_overwrite_ttl(self):
        """Test overwriting a key with different TTL."""
        # Set with long TTL
        self.store.set_with_ttl("changeable", "first_value", ttl=10.0)
        self.assertEqual(self.store.get_with_ttl("changeable"), "first_value")
        
        # Overwrite with short TTL
        self.store.set_with_ttl("changeable", "second_value", ttl=0.1)
        self.assertEqual(self.store.get_with_ttl("changeable"), "second_value")
        print(f"✓ Key overwritten successfully")
        
        # Wait for new TTL to expire
        time.sleep(0.2)
        result = self.store.get_with_ttl("changeable")
        self.assertIsNone(result)
        print(f"✓ Key expired with new TTL: {result}")
    
    def test_overwrite_no_ttl_with_ttl(self):
        """Test overwriting a permanent key with TTL."""
        # Set without TTL
        self.store.set_with_ttl("evolving", "permanent")
        self.assertEqual(self.store.get_with_ttl("evolving"), "permanent")
        
        # Overwrite with TTL
        self.store.set_with_ttl("evolving", "temporary", ttl=0.1)
        self.assertEqual(self.store.get_with_ttl("evolving"), "temporary")
        
        # Wait for expiration
        time.sleep(0.2)
        result = self.store.get_with_ttl("evolving")
        self.assertIsNone(result)
        print(f"✓ Permanent key converted to temporary: {result}")
    
    def test_overwrite_ttl_with_no_ttl(self):
        """Test overwriting a TTL key with permanent key."""
        # Set with TTL
        self.store.set_with_ttl("evolving2", "temporary", ttl=0.1)
        self.assertEqual(self.store.get_with_ttl("evolving2"), "temporary")
        
        # Overwrite without TTL
        self.store.set_with_ttl("evolving2", "permanent")
        self.assertEqual(self.store.get_with_ttl("evolving2"), "permanent")
        
        # Wait (should not expire)
        time.sleep(0.2)
        result = self.store.get_with_ttl("evolving2")
        self.assertEqual(result, "permanent")
        print(f"✓ Temporary key converted to permanent: {result}")
    
    def test_multiple_keys_different_ttls(self):
        """Test multiple keys with different TTL values."""
        # Set multiple keys with different TTLs
        self.store.set_with_ttl("no_ttl", "permanent")
        self.store.set_with_ttl("short_ttl", "expires_quickly", ttl=0.1)
        self.store.set_with_ttl("medium_ttl", "expires_later", ttl=0.2)
        self.store.set_with_ttl("long_ttl", "expires_much_later", ttl=1.0)
        
        # All should be available initially
        self.assertEqual(self.store.get_with_ttl("no_ttl"), "permanent")
        self.assertEqual(self.store.get_with_ttl("short_ttl"), "expires_quickly")
        self.assertEqual(self.store.get_with_ttl("medium_ttl"), "expires_later")
        self.assertEqual(self.store.get_with_ttl("long_ttl"), "expires_much_later")
        print("✓ All keys available initially")
        
        # Wait for short TTL to expire
        time.sleep(0.15)
        self.assertEqual(self.store.get_with_ttl("no_ttl"), "permanent")
        self.assertIsNone(self.store.get_with_ttl("short_ttl"))
        self.assertEqual(self.store.get_with_ttl("medium_ttl"), "expires_later")
        self.assertEqual(self.store.get_with_ttl("long_ttl"), "expires_much_later")
        print("✓ Short TTL expired, others remain")
        
        # Wait for medium TTL to expire
        time.sleep(0.1)
        self.assertEqual(self.store.get_with_ttl("no_ttl"), "permanent")
        self.assertIsNone(self.store.get_with_ttl("short_ttl"))
        self.assertIsNone(self.store.get_with_ttl("medium_ttl"))
        self.assertEqual(self.store.get_with_ttl("long_ttl"), "expires_much_later")
        print("✓ Medium TTL expired, permanent and long remain")
    
    def test_zero_ttl(self):
        """Test TTL of zero (should expire immediately)."""
        self.store.set_with_ttl("instant_expire", "gone", ttl=0.0)
        
        # Might be available for a very brief moment, but should expire quickly
        time.sleep(0.01)
        result = self.store.get_with_ttl("instant_expire")
        self.assertIsNone(result)
        print(f"✓ Zero TTL expires immediately: {result}")
    
    def test_negative_ttl(self):
        """Test negative TTL (should be treated as expired)."""
        self.store.set_with_ttl("already_expired", "never_seen", ttl=-1.0)
        
        result = self.store.get_with_ttl("already_expired")
        self.assertIsNone(result)
        print(f"✓ Negative TTL treated as expired: {result}")


def run_stage2_tests():
    """Run Stage 2 tests with detailed output for debugging."""
    print("=" * 60)
    print("STAGE 2: TTL OPERATIONS TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage2TTLOperations)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ STAGE 2: ALL TESTS PASSED!")
    else:
        print("❌ STAGE 2: SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_stage2_tests() 