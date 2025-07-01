#!/usr/bin/env python3
"""
Test Suite for Level 2: Prefix-based File Querying

Tests the file retrieval functionality:
- get_n_largest(prefix, n) -> list[str]

Returns list of top n largest files with names starting with prefix,
sorted by size (descending), then lexicographically by name.
"""

import unittest
from file_storage_system import CloudFileStorage


class TestLevel2PrefixQuerying(unittest.TestCase):
    """Test Level 2: Prefix-based file querying."""
    
    def setUp(self):
        """Set up a fresh storage system for each test."""
        self.storage = CloudFileStorage()
    
    def test_basic_prefix_query(self):
        """Test basic prefix querying functionality."""
        # Add files from screenshot example
        self.storage.add_file("/dir/file1.txt", 5)
        self.storage.add_file("/dir/file2.doc", 3)
        self.storage.add_file("/dir/deeper/file3.mov", 9)
        
        # Test query: get_n_largest("/dir/file", 3)
        result = self.storage.get_n_largest("/dir/file", 3)
        
        # Should return files sorted by size (desc), then name (asc)
        # file1.txt (5), file2.doc (3) - both start with "/dir/file"
        expected = ["/dir/file1.txt", "/dir/file2.doc"]
        self.assertEqual(result, expected)
        print(f"✓ Basic prefix query returned: {result}")
    
    def test_screenshot_example_1(self):
        """Test exact example from screenshot."""
        # From screenshot: get_n_largest("/dir/file", 3) should return ["/dir/file2(20)", "/dir/file1.txt(5)"]
        # This suggests there are files with sizes 20 and 5
        
        self.storage.add_file("/dir/file2", 20)
        self.storage.add_file("/dir/file1.txt", 5)
        self.storage.add_file("/dir/another_file", 10)  # Different prefix
        
        result = self.storage.get_n_largest("/dir/file", 3)
        expected = ["/dir/file2", "/dir/file1.txt"]  # Sorted by size desc
        self.assertEqual(result, expected)
        print(f"✓ Screenshot example 1: {result}")
    
    def test_screenshot_example_2(self):
        """Test another example from screenshot."""
        # get_n_largest("/another_dir", 2) should return ["/another_dir"]
        self.storage.add_file("/another_dir", 25)
        self.storage.add_file("/different_prefix", 30)
        
        result = self.storage.get_n_largest("/another_dir", 2)
        expected = ["/another_dir"]
        self.assertEqual(result, expected)
        print(f"✓ Screenshot example 2: {result}")
    
    def test_size_sorting_priority(self):
        """Test that files are sorted by size first, then by name."""
        # Add files with different sizes
        self.storage.add_file("prefix_file_a", 100)  # Largest
        self.storage.add_file("prefix_file_c", 50)   # Medium
        self.storage.add_file("prefix_file_b", 100)  # Same size as 'a', should be sorted by name
        self.storage.add_file("prefix_file_d", 25)   # Smallest
        
        result = self.storage.get_n_largest("prefix_file", 10)
        
        # Expected order: size desc, then name asc for same sizes
        expected = [
            "prefix_file_a",  # size 100, comes before 'b' alphabetically  
            "prefix_file_b",  # size 100, comes after 'a' alphabetically
            "prefix_file_c",  # size 50
            "prefix_file_d"   # size 25
        ]
        self.assertEqual(result, expected)
        print(f"✓ Size/name sorting: {result}")
    
    def test_lexicographical_sorting(self):
        """Test lexicographical sorting for files with same size."""
        # Add files with same size but different names
        files = [
            ("test_z", 10),
            ("test_a", 10), 
            ("test_m", 10),
            ("test_1", 10),
            ("test_A", 10)  # Capital letter
        ]
        
        for name, size in files:
            self.storage.add_file(name, size)
        
        result = self.storage.get_n_largest("test_", 10)
        
        # Should be sorted lexicographically (ASCII order: numbers < uppercase < lowercase)
        expected = ["test_1", "test_A", "test_a", "test_m", "test_z"]
        self.assertEqual(result, expected)
        print(f"✓ Lexicographical sorting: {result}")
    
    def test_limit_parameter(self):
        """Test the n (limit) parameter works correctly."""
        # Add many files
        for i in range(10):
            self.storage.add_file(f"data_file_{i:02d}", 100 - i)  # Decreasing sizes
        
        # Test different limits
        result_3 = self.storage.get_n_largest("data_", 3)
        self.assertEqual(len(result_3), 3)
        self.assertEqual(result_3, ["data_file_00", "data_file_01", "data_file_02"])
        
        result_5 = self.storage.get_n_largest("data_", 5)
        self.assertEqual(len(result_5), 5)
        
        result_all = self.storage.get_n_largest("data_", 20)  # More than available
        self.assertEqual(len(result_all), 10)  # Should return all matching files
        
        print(f"✓ Limit parameter working: n=3 gave {len(result_3)}, n=20 gave {len(result_all)}")
    
    def test_no_matching_files(self):
        """Test querying with prefix that matches no files."""
        self.storage.add_file("apple.txt", 10)
        self.storage.add_file("banana.txt", 20)
        
        result = self.storage.get_n_largest("orange", 5)
        self.assertEqual(result, [])
        print("✓ No matching files returns empty list")
    
    def test_zero_or_negative_limit(self):
        """Test edge cases with limit parameter."""
        self.storage.add_file("test_file", 10)
        
        # Test n = 0
        result = self.storage.get_n_largest("test", 0)
        self.assertEqual(result, [])
        
        # Test negative n
        result = self.storage.get_n_largest("test", -1)
        self.assertEqual(result, [])
        
        print("✓ Zero/negative limits handled correctly")
    
    def test_empty_prefix(self):
        """Test querying with empty prefix (should match all files)."""
        files = [
            ("z_file", 10),
            ("a_file", 30), 
            ("m_file", 20)
        ]
        
        for name, size in files:
            self.storage.add_file(name, size)
        
        result = self.storage.get_n_largest("", 10)  # Empty prefix
        
        # Should return all files sorted by size desc, name asc
        expected = ["a_file", "m_file", "z_file"]  # sizes: 30, 20, 10
        self.assertEqual(result, expected)
        print(f"✓ Empty prefix matches all files: {result}")
    
    def test_prefix_exact_match(self):
        """Test when prefix exactly matches a filename."""
        self.storage.add_file("exact", 100)
        self.storage.add_file("exact_longer", 50)
        self.storage.add_file("exact_another", 75)
        
        result = self.storage.get_n_largest("exact", 10)
        
        # Should include all files starting with "exact"
        expected = ["exact", "exact_another", "exact_longer"]  # sorted by size desc
        self.assertEqual(result, expected)
        print(f"✓ Exact prefix match: {result}")
    
    def test_case_sensitivity(self):
        """Test that prefix matching is case-sensitive."""
        self.storage.add_file("File.txt", 10)
        self.storage.add_file("file.txt", 20)
        self.storage.add_file("FILE.txt", 30)
        
        # Test different case prefixes
        result_upper = self.storage.get_n_largest("F", 10)
        self.assertEqual(result_upper, ["FILE.txt", "File.txt"])  # Only uppercase F
        
        result_lower = self.storage.get_n_largest("f", 10)
        self.assertEqual(result_lower, ["file.txt"])  # Only lowercase f
        
        print("✓ Case-sensitive prefix matching works")
    
    def test_complex_scenario(self):
        """Test a complex scenario with many files and various prefixes."""
        # Add files with different prefixes and sizes
        files = [
            ("/big_file.mp4", 300),
            ("/big_file.avi", 250), 
            ("/big_archive.zip", 400),
            ("/small_doc.txt", 5),
            ("/small_image.jpg", 15),
            ("/another/big_file.mov", 350),  # Different path but similar name
            ("big_local_file", 200)  # No leading slash
        ]
        
        for name, size in files:
            self.storage.add_file(name, size)
        
        # Test various prefix queries
        big_files = self.storage.get_n_largest("/big_", 10)
        expected_big = ["/big_archive.zip", "/big_file.mp4", "/big_file.avi"]
        self.assertEqual(big_files, expected_big)
        
        small_files = self.storage.get_n_largest("/small_", 10)
        expected_small = ["/small_image.jpg", "/small_doc.txt"]
        self.assertEqual(small_files, expected_small)
        
        # Test with limit
        limited_big = self.storage.get_n_largest("/big_", 2)
        self.assertEqual(len(limited_big), 2)
        self.assertEqual(limited_big, ["/big_archive.zip", "/big_file.mp4"])
        
        print("✓ Complex scenario with multiple prefixes works")
    
    def test_integration_with_level1(self):
        """Test that Level 2 works correctly with Level 1 operations."""
        # Add files
        self.storage.add_file("log_error.txt", 100)
        self.storage.add_file("log_info.txt", 50)
        self.storage.add_file("log_debug.txt", 25)
        
        # Query before deletion
        result_before = self.storage.get_n_largest("log_", 10)
        self.assertEqual(len(result_before), 3)
        
        # Delete a file
        deleted_size = self.storage.delete_file("log_info.txt")
        self.assertEqual(deleted_size, 50)
        
        # Query after deletion
        result_after = self.storage.get_n_largest("log_", 10)
        expected_after = ["log_error.txt", "log_debug.txt"]
        self.assertEqual(result_after, expected_after)
        
        # Add a new file
        self.storage.add_file("log_warning.txt", 75)
        
        # Query after addition
        result_final = self.storage.get_n_largest("log_", 10)
        expected_final = ["log_error.txt", "log_warning.txt", "log_debug.txt"]
        self.assertEqual(result_final, expected_final)
        
        print("✓ Level 2 integrates correctly with Level 1 operations")


def run_level2_tests():
    """Run Level 2 tests with detailed output."""
    print("=" * 60)
    print("LEVEL 2: PREFIX-BASED QUERYING TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLevel2PrefixQuerying)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ LEVEL 2: ALL TESTS PASSED!")
    else:
        print("❌ LEVEL 2: SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_level2_tests() 