import unittest
from key_value_store import EvolvingKeyValueStore


class TestStage1BasicOperations(unittest.TestCase):
    """
    Stage 1: Basic Operations Tests
    
    This stage focuses on implementing basic get/set functionality
    for an in-memory key-value store.
    """
    
    def setUp(self):
        """Set up a fresh store for each test."""
        self.store = EvolvingKeyValueStore()
    
    def test_basic_set_and_get(self):
        """Test basic set and get operations."""
        # Test setting and getting a simple string value
        self.store.set_basic("username", "alice")
        result = self.store.get_basic("username")
        self.assertEqual(result, "alice")
        
        print(f"✓ Set 'username' to 'alice', got: {result}")
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        result = self.store.get_basic("nonexistent")
        self.assertIsNone(result)
        
        print(f"✓ Getting nonexistent key returns: {result}")
    
    def test_overwrite_value(self):
        """Test overwriting an existing value."""
        # Set initial value
        self.store.set_basic("counter", 1)
        self.assertEqual(self.store.get_basic("counter"), 1)
        
        # Overwrite with new value
        self.store.set_basic("counter", 2)
        result = self.store.get_basic("counter")
        self.assertEqual(result, 2)
        
        print(f"✓ Overwrote 'counter' from 1 to 2, got: {result}")
    
    def test_multiple_keys(self):
        """Test storing multiple different keys."""
        test_data = {
            "name": "John Doe",
            "age": 30,
            "city": "New York"
        }
        
        # Set all values
        for key, value in test_data.items():
            self.store.set_basic(key, value)
        
        # Verify all values
        for key, expected_value in test_data.items():
            result = self.store.get_basic(key)
            self.assertEqual(result, expected_value)
            print(f"✓ Key '{key}': set {expected_value}, got {result}")
    
    def test_different_data_types(self):
        """Test storing different Python data types."""
        test_cases = [
            ("string_val", "hello world"),
            ("int_val", 42),
            ("float_val", 3.14159),
            ("bool_val", True),
            ("none_val", None),
            ("list_val", [1, 2, 3, "four"]),
            ("dict_val", {"nested": "data", "count": 5}),
            ("tuple_val", (1, "two", 3.0))
        ]
        
        for key, value in test_cases:
            self.store.set_basic(key, value)
            result = self.store.get_basic(key)
            self.assertEqual(result, value)
            print(f"✓ {type(value).__name__} - Key '{key}': {value} == {result}")
    
    def test_empty_string_key(self):
        """Test using empty string as a key."""
        self.store.set_basic("", "empty key value")
        result = self.store.get_basic("")
        self.assertEqual(result, "empty key value")
        
        print(f"✓ Empty string key works: {result}")
    
    def test_key_independence(self):
        """Test that keys are independent of each other."""
        # Set multiple keys with similar names
        self.store.set_basic("user", "general_user")
        self.store.set_basic("user_name", "specific_name")
        self.store.set_basic("user1", "first_user")
        
        # Verify independence
        self.assertEqual(self.store.get_basic("user"), "general_user")
        self.assertEqual(self.store.get_basic("user_name"), "specific_name")
        self.assertEqual(self.store.get_basic("user1"), "first_user")
        
        print("✓ Keys are independent: 'user', 'user_name', 'user1' work correctly")
    
    def test_large_value(self):
        """Test storing a relatively large value."""
        large_string = "x" * 10000  # 10KB string
        self.store.set_basic("large_data", large_string)
        result = self.store.get_basic("large_data")
        self.assertEqual(result, large_string)
        self.assertEqual(len(result), 10000)
        
        print(f"✓ Large value (10KB) stored and retrieved successfully")


def run_stage1_tests():
    """Run Stage 1 tests with detailed output for debugging."""
    print("=" * 60)
    print("STAGE 1: BASIC OPERATIONS TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage1BasicOperations)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ STAGE 1: ALL TESTS PASSED!")
    else:
        print("❌ STAGE 1: SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_stage1_tests() 