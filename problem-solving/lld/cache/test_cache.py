import unittest

from cache import KeyValueCache, LRUEvictionPolicy


class TestCache(unittest.TestCase):
    def test_put_get(self):
        c = KeyValueCache(capacity=2)
        c.put("a", 1)
        c.put("b", 2)
        self.assertEqual(c.get("a"), 1)
        self.assertEqual(c.get("b"), 2)
        self.assertIsNone(c.get("c"))

    def test_lru_eviction(self):
        c = KeyValueCache(capacity=2)
        c.put("a", 1)  # a most recent
        c.put("b", 2)  # b most recent
        # Access 'a' so 'b' becomes LRU
        c.get("a")
        # Insert 'c' => evict 'b'
        c.put("c", 3)
        self.assertIsNone(c.get("b"))
        self.assertEqual(c.get("a"), 1)
        self.assertEqual(c.get("c"), 3)

    def test_update_refresh(self):
        c = KeyValueCache(capacity=2)
        c.put("a", 1)
        c.put("b", 2)
        # Update 'a' should refresh its recency
        c.put("a", 10)
        # Insert 'c' should evict 'b'
        c.put("c", 3)
        self.assertIsNone(c.get("b"))
        self.assertEqual(c.get("a"), 10)
        self.assertEqual(c.get("c"), 3)

    def test_remove(self):
        c = KeyValueCache(capacity=1)
        c.put("x", 99)
        self.assertTrue(c.contains("x"))
        self.assertTrue(c.remove("x"))
        self.assertFalse(c.contains("x"))
        # Removing absent key should return False
        self.assertFalse(c.remove("y"))


if __name__ == "__main__":
    unittest.main(verbosity=2) 