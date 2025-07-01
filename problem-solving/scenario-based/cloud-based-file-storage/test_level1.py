#!/usr/bin/env python3
"""
Test Suite for Level 1: Basic File Operations

Tests the core file manipulation functionality:
- add_file(name, size) -> bool
- get_file_size(name) -> int | None  
- delete_file(name) -> int | None
"""

import unittest
from file_storage_system import CloudFileStorage


class TestLevel1BasicOperations(unittest.TestCase):
    """Test Level 1: Basic file operations."""
    
    def setUp(self):
        """Set up a fresh storage system for each test."""
        self.storage = CloudFileStorage()
    
    def test_add_file_success(self):
        """Test successfully adding new files."""
        # Test from screenshot example
        result = self.storage.add_file("/dir1/dir2/file.txt", 10)
        self.assertTrue(result)
        print("✓ Added file '/dir1/dir2/file.txt' with size 10")
        
        # Verify file was actually added
        size = self.storage.get_file_size("/dir1/dir2/file.txt")
        self.assertEqual(size, 10)
        
        # Add another file
        result = self.storage.add_file("document.pdf", 1000)
        self.assertTrue(result)
        print("✓ Added file 'document.pdf' with size 1000")
    
    def test_add_file_already_exists(self):
        """Test adding a file that already exists."""
        # Add file first time
        result1 = self.storage.add_file("/dir1/dir2/file.txt", 5)
        self.assertTrue(result1)
        
        # Try to add same file again (should fail)
        result2 = self.storage.add_file("/dir1/dir2/file.txt", 5)
        self.assertFalse(result2)
        print("✓ Correctly rejected duplicate file '/dir1/dir2/file.txt'")
        
        # Verify original file is unchanged
        size = self.storage.get_file_size("/dir1/dir2/file.txt")
        self.assertEqual(size, 5)
    
    def test_get_file_size_existing(self):
        """Test getting size of existing files."""
        # Add some files
        self.storage.add_file("/dir1/dir2/file.txt", 10)
        self.storage.add_file("small_file", 1)
        self.storage.add_file("large_file", 999999)
        
        # Test getting sizes
        self.assertEqual(self.storage.get_file_size("/dir1/dir2/file.txt"), 10)
        self.assertEqual(self.storage.get_file_size("small_file"), 1)
        self.assertEqual(self.storage.get_file_size("large_file"), 999999)
        print("✓ Successfully retrieved file sizes")
    
    def test_get_file_size_nonexistent(self):
        """Test getting size of non-existent files."""
        # Test from screenshot example
        result = self.storage.get_file_size("/not-existing-file")
        self.assertIsNone(result)
        print("✓ Correctly returned None for non-existent file")
        
        # Test empty storage
        result = self.storage.get_file_size("any_file")
        self.assertIsNone(result)
    
    def test_delete_file_success(self):
        """Test successfully deleting files."""
        # Add files first
        self.storage.add_file("/root-existing-file", 100)
        self.storage.add_file("temp_file", 50)
        
        # Delete and verify return value
        deleted_size = self.storage.delete_file("/root-existing-file")
        self.assertEqual(deleted_size, 100)
        print("✓ Successfully deleted file and returned size 100")
        
        # Verify file is gone
        self.assertIsNone(self.storage.get_file_size("/root-existing-file"))
        
        # Delete another file
        deleted_size = self.storage.delete_file("temp_file")
        self.assertEqual(deleted_size, 50)
    
    def test_delete_file_nonexistent(self):
        """Test deleting non-existent files."""
        # Test from screenshot example
        result = self.storage.delete_file("/not-existing-file")
        self.assertIsNone(result)
        print("✓ Correctly returned None for non-existent file deletion")
        
        # Test on empty storage
        result = self.storage.delete_file("any_file")
        self.assertIsNone(result)
    
    def test_file_operations_sequence(self):
        """Test a sequence of file operations."""
        # Following the screenshot examples exactly
        
        # add_file("/dir1/dir2/file.txt", 10) -> True
        result = self.storage.add_file("/dir1/dir2/file.txt", 10)
        self.assertTrue(result)
        
        # add_file("/dir1/dir2/file.txt", 5) -> False (already exists)  
        result = self.storage.add_file("/dir1/dir2/file.txt", 5)
        self.assertFalse(result)
        
        # get_file_size("/dir1/dir2/file.txt") -> 10
        size = self.storage.get_file_size("/dir1/dir2/file.txt")
        self.assertEqual(size, 10)
        
        # delete_file("/not-existing-file") -> None
        result = self.storage.delete_file("/not-existing-file")
        self.assertIsNone(result)
        
        # delete_file("/dir1/dir2/file.txt") -> 10
        result = self.storage.delete_file("/dir1/dir2/file.txt")
        self.assertEqual(result, 10)
        
        # get_file_size("/not-existing-file") -> None  
        result = self.storage.get_file_size("/not-existing-file")
        self.assertIsNone(result)
        
        print("✓ All screenshot examples passed!")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty filename
        result = self.storage.add_file("", 10)
        self.assertTrue(result)  # Empty string is a valid filename
        
        # Zero size file
        result = self.storage.add_file("empty_file", 0)
        self.assertTrue(result)
        self.assertEqual(self.storage.get_file_size("empty_file"), 0)
        
        # Very large file
        large_size = 10**12  # 1TB
        result = self.storage.add_file("huge_file", large_size)
        self.assertTrue(result)
        self.assertEqual(self.storage.get_file_size("huge_file"), large_size)
        
        # Special characters in filename
        special_names = [
            "file with spaces.txt",
            "file-with-dashes.txt", 
            "file_with_underscores.txt",
            "file.with.multiple.dots.txt",
            "123numeric_start.txt"
        ]
        
        for name in special_names:
            result = self.storage.add_file(name, 100)
            self.assertTrue(result, f"Failed to add file: {name}")
        
        print("✓ Edge cases handled correctly")
    
    def test_multiple_files_independence(self):
        """Test that multiple files can coexist independently."""
        files = [
            ("file1.txt", 100),
            ("file2.doc", 200), 
            ("folder/file3.pdf", 300),
            ("another/folder/file4.jpg", 400),
            ("file5", 500)  # No extension
        ]
        
        # Add all files
        for name, size in files:
            result = self.storage.add_file(name, size)
            self.assertTrue(result, f"Failed to add {name}")
        
        # Verify all files exist with correct sizes
        for name, size in files:
            actual_size = self.storage.get_file_size(name)
            self.assertEqual(actual_size, size, f"Wrong size for {name}")
        
        # Delete every other file
        for i, (name, size) in enumerate(files):
            if i % 2 == 0:
                deleted_size = self.storage.delete_file(name)
                self.assertEqual(deleted_size, size)
        
        # Verify remaining files are unaffected
        for i, (name, size) in enumerate(files):
            if i % 2 == 1:  # Should still exist
                actual_size = self.storage.get_file_size(name)
                self.assertEqual(actual_size, size)
            else:  # Should be deleted
                actual_size = self.storage.get_file_size(name)
                self.assertIsNone(actual_size)
        
        print("✓ Multiple files operate independently")


def run_level1_tests():
    """Run Level 1 tests with detailed output."""
    print("=" * 60)
    print("LEVEL 1: BASIC FILE OPERATIONS TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLevel1BasicOperations)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ LEVEL 1: ALL TESTS PASSED!")
    else:
        print("❌ LEVEL 1: SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_level1_tests() 