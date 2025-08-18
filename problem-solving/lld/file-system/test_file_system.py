import unittest

from file_system import FileSystemAggregator

try:
    from sortedcontainers import SortedList  # type: ignore
    HAS_SORTED = True
except Exception:  # pragma: no cover
    HAS_SORTED = False


class TestFileSystemPart1(unittest.TestCase):
    def test_example(self):
        fs = FileSystemAggregator()
        fs.add_file("file1.txt", 100)
        fs.add_file("file2.txt", 200, collections=["collection1"])
        fs.add_file("file3.txt", 200, collections=["collection1"])
        fs.add_file("file4.txt", 300, collections=["collection2"])
        fs.add_file("file5.txt", 100)

        self.assertEqual(fs.get_total_size(), 900)
        top2 = fs.top_k_collections(2)
        self.assertEqual(top2, [("collection1", 400), ("collection2", 300)])

    def test_empty_and_k_zero(self):
        fs = FileSystemAggregator()
        self.assertEqual(fs.get_total_size(), 0)
        self.assertEqual(fs.top_k_collections(2), [])
        self.assertEqual(fs.top_k_collections(0), [])

    def test_negative_size_raises(self):
        fs = FileSystemAggregator()
        with self.assertRaises(ValueError):
            fs.add_file("bad.txt", -1)

    @unittest.skipUnless(HAS_SORTED, "sortedcontainers not installed")
    def test_top_k_optimized(self):
        fs = FileSystemAggregator()
        fs.add_file("file2.txt", 200, collections=["collection1"])
        fs.add_file("file3.txt", 200, collections=["collection1"])
        fs.add_file("file4.txt", 300, collections=["collection2"])
        self.assertEqual(fs.top_k_collections_optimized(1), [("collection1", 400)])
        self.assertEqual(fs.top_k_collections_optimized(2), [("collection1", 400), ("collection2", 300)])


class TestFileSystemPart2(unittest.TestCase):
    def test_multi_collection_per_file(self):
        fs = FileSystemAggregator()
        fs.add_file("a.txt", 100, collections=["c1", "c2"])  # counts in both
        self.assertEqual(fs.get_total_size(), 100)
        self.assertEqual(dict(fs.top_k_collections(2)), {"c1": 100, "c2": 100})

    def test_update_file_size_only(self):
        fs = FileSystemAggregator()
        fs.add_file("a.txt", 100, collections=["c1"])  # c1=100
        fs.update_file("a.txt", 150)  # c1 += 50
        self.assertEqual(fs.get_total_size(), 150)
        self.assertEqual(fs.top_k_collections(1), [("c1", 150)])

    def test_update_file_collections_change(self):
        fs = FileSystemAggregator()
        fs.add_file("a.txt", 100, collections=["c1", "c2"])  # c1=100,c2=100
        # Move file to c2 and c3, and change size to 200
        fs.update_file("a.txt", 200, new_collections=["c2", "c3"])  # c1-=100, c2+=100, c3+=200
        self.assertEqual(fs.get_total_size(), 200)
        # c1=0 (implicit), c2=200, c3=200
        top = dict(fs.top_k_collections(3))
        self.assertEqual(top.get("c1", 0), 0)
        self.assertEqual(top.get("c2"), 200)
        self.assertEqual(top.get("c3"), 200)

    @unittest.skipUnless(HAS_SORTED, "sortedcontainers not installed")
    def test_update_preserves_optimized_index(self):
        fs = FileSystemAggregator()
        fs.add_file("a.txt", 100, collections=["c1"])  # c1=100
        fs.add_file("b.txt", 150, collections=["c2"])  # c2=150
        self.assertEqual(fs.top_k_collections_optimized(1), [("c2", 150)])
        fs.update_file("a.txt", 200)  # c1=200
        self.assertEqual(fs.top_k_collections_optimized(2), [("c1", 200), ("c2", 150)])


if __name__ == "__main__":
    unittest.main(verbosity=2) 