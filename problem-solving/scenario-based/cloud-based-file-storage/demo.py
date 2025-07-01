#!/usr/bin/env python3
"""
Interactive Demo for Cloud-Based File Storage System

This demo showcases the functionality of all three levels:
- Level 1: Basic file operations (add, get_size, delete)
- Level 2: Prefix-based file querying with sorting
- Level 3: User management with capacity limits and merging

Run this demo to see the system in action and understand how it works.
"""

from file_storage_system import CloudFileStorage
import time


def print_separator(title="", width=70):
    """Print a visual separator with optional title."""
    if title:
        padding = (width - len(title) - 2) // 2
        print("=" * padding + f" {title} " + "=" * padding)
    else:
        print("=" * width)


def print_step(step_num, description):
    """Print a numbered step."""
    print(f"\n🔸 Step {step_num}: {description}")


def demonstrate_level1():
    """Demonstrate Level 1: Basic file operations."""
    print_separator("LEVEL 1: BASIC FILE OPERATIONS")
    print("Testing core file manipulation: add, get_size, delete")
    
    storage = CloudFileStorage()
    
    print_step(1, "Adding files to storage")
    files_to_add = [
        ("/documents/report.pdf", 250),
        ("/documents/presentation.pptx", 800),
        ("/images/photo1.jpg", 1500),
        ("/images/photo2.png", 1200),
        ("/videos/demo.mp4", 5000)
    ]
    
    for filename, size in files_to_add:
        result = storage.add_file(filename, size)
        status = "✅ Added" if result else "❌ Failed"
        print(f"  {status}: {filename} ({size} bytes)")
    
    print_step(2, "Retrieving file sizes")
    for filename, expected_size in files_to_add:
        actual_size = storage.get_file_size(filename)
        if actual_size == expected_size:
            print(f"  ✅ {filename}: {actual_size} bytes")
        else:
            print(f"  ❌ {filename}: Expected {expected_size}, got {actual_size}")
    
    print_step(3, "Testing duplicate file addition")
    result = storage.add_file("/documents/report.pdf", 300)  # Different size
    status = "✅ Correctly rejected" if not result else "❌ Incorrectly accepted"
    print(f"  {status}: Duplicate filename /documents/report.pdf")
    
    print_step(4, "Deleting files")
    files_to_delete = ["/images/photo1.jpg", "/videos/demo.mp4"]
    for filename in files_to_delete:
        deleted_size = storage.delete_file(filename)
        if deleted_size is not None:
            print(f"  ✅ Deleted: {filename} (size: {deleted_size} bytes)")
        else:
            print(f"  ❌ Failed to delete: {filename}")
    
    print_step(5, "Verifying deleted files")
    for filename in files_to_delete:
        size = storage.get_file_size(filename)
        status = "✅ Correctly deleted" if size is None else f"❌ Still exists ({size} bytes)"
        print(f"  {status}: {filename}")
    
    print("\n📊 Level 1 Summary:")
    stats = storage.get_storage_stats()
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size']} bytes")
    
    return storage


def demonstrate_level2(storage):
    """Demonstrate Level 2: Prefix-based querying."""
    print_separator("LEVEL 2: PREFIX-BASED FILE QUERYING")
    print("Testing file retrieval with prefix filtering and sorting")
    
    print_step(1, "Adding more files for diverse prefixes")
    additional_files = [
        ("log_error_2023.txt", 150),
        ("log_warning_2023.txt", 100),
        ("log_info_2023.txt", 75),
        ("data_customers.csv", 500),
        ("data_products.csv", 300),
        ("data_orders.csv", 400),
        ("backup_daily.zip", 2000),
        ("backup_weekly.zip", 8000),
        ("config_app.json", 50),
        ("config_db.json", 80)
    ]
    
    for filename, size in additional_files:
        result = storage.add_file(filename, size)
        status = "✅" if result else "❌"
        print(f"  {status} {filename} ({size} bytes)")
    
    print_step(2, "Querying files by prefix (sorted by size, then name)")
    
    test_queries = [
        ("log_", 5, "Log files"),
        ("data_", 3, "Data files"),
        ("/documents/", 10, "Documents"),
        ("backup_", 2, "Backup files"),
        ("config_", 2, "Config files"),
        ("nonexistent_", 5, "Non-existent prefix")
    ]
    
    for prefix, limit, description in test_queries:
        print(f"\n  🔍 Query: {description} (prefix: '{prefix}', limit: {limit})")
        results = storage.get_n_largest(prefix, limit)
        
        if results:
            for i, filename in enumerate(results, 1):
                size = storage.get_file_size(filename)
                print(f"    {i}. {filename} ({size} bytes)")
        else:
            print("    No files found")
    
    print_step(3, "Testing edge cases")
    edge_cases = [
        ("", 3, "Empty prefix (should match all)"),
        ("log_", 0, "Zero limit"),
        ("log_", -1, "Negative limit"),
        ("LOG_", 3, "Case sensitivity test")
    ]
    
    for prefix, limit, description in edge_cases:
        results = storage.get_n_largest(prefix, limit)
        print(f"  {description}: {len(results)} results")
    
    return storage


def demonstrate_level3(storage):
    """Demonstrate Level 3: User management with capacity limits."""
    print_separator("LEVEL 3: USER MANAGEMENT & CAPACITY LIMITS")
    print("Testing user accounts, storage limits, and account merging")
    
    print_step(1, "Creating users with different capacities")
    users_to_create = [
        ("alice", 1000, "Alice - Developer"),
        ("bob", 500, "Bob - Designer"), 
        ("charlie", 2000, "Charlie - Manager"),
        ("diana", 300, "Diana - Intern")
    ]
    
    for user_id, capacity, description in users_to_create:
        result = storage.add_user(user_id, capacity)
        status = "✅ Created" if result else "❌ Failed"
        print(f"  {status}: {description} ({capacity} bytes capacity)")
    
    print_step(2, "Adding files owned by specific users")
    user_files = [
        ("alice", "alice_project.py", 200),
        ("alice", "alice_docs.md", 150),
        ("bob", "design_mockup.psd", 400),
        ("bob", "design_assets.zip", 350),  # This should fail (400+350 > 500)
        ("charlie", "budget_2023.xlsx", 800),
        ("charlie", "team_report.pdf", 600),
        ("diana", "notes.txt", 100),
        ("diana", "large_file.bin", 500)  # This should fail (100+500 > 300)
    ]
    
    for user_id, filename, size in user_files:
        result = storage.add_file_by(user_id, filename, size)
        if result is not None:
            print(f"  ✅ {user_id}: Added {filename} ({size} bytes) - {result} remaining")
        else:
            print(f"  ❌ {user_id}: Failed to add {filename} ({size} bytes) - capacity exceeded")
    
    print_step(3, "Checking user storage status")
    for user_id, _, description in users_to_create:
        user_info = storage.get_user_info(user_id)
        if user_info:
            used = user_info['used_storage']
            capacity = user_info['capacity']
            remaining = user_info['remaining_capacity']
            files = user_info['file_count']
            print(f"  📊 {description}:")
            print(f"     Used: {used}/{capacity} bytes ({files} files), Remaining: {remaining}")
        else:
            print(f"  ❌ User {user_id} not found")
    
    print_step(4, "Testing capacity enforcement")
    print("  Attempting to add files that would exceed capacity...")
    
    # Try to add a large file for diana (who has limited capacity)
    result = storage.add_file_by("diana", "huge_file.mov", 250)
    if result is None:
        print("  ✅ Correctly rejected file that would exceed Diana's capacity")
    else:
        print("  ❌ Incorrectly accepted file that exceeds capacity")
    
    print_step(5, "Demonstrating user account merging")
    print("  Merging Diana's account into Charlie's account...")
    
    # Show before state
    diana_info = storage.get_user_info("diana")
    charlie_info = storage.get_user_info("charlie")
    print(f"  Before merge:")
    print(f"    Diana: {diana_info['used_storage']}/{diana_info['capacity']} bytes")
    print(f"    Charlie: {charlie_info['used_storage']}/{charlie_info['capacity']} bytes")
    
    # Perform merge
    result = storage.merge_user("charlie", "diana")
    if result is not None:
        print(f"  ✅ Merge successful! Charlie's remaining capacity: {result} bytes")
        
        # Show after state
        charlie_info = storage.get_user_info("charlie")
        diana_info = storage.get_user_info("diana")
        print(f"  After merge:")
        print(f"    Charlie: {charlie_info['used_storage']}/{charlie_info['capacity']} bytes ({charlie_info['file_count']} files)")
        print(f"    Diana: {'Deleted' if diana_info is None else 'Still exists'}")
        
        # Show Charlie's files
        charlie_files = storage.list_files_by_user("charlie")
        print(f"  Charlie now owns: {[name for name, size in charlie_files]}")
    else:
        print("  ❌ Merge failed!")
    
    print_step(6, "Testing merge capacity validation")
    print("  Attempting merge that would exceed capacity...")
    
    # Try to merge alice into bob (should fail due to capacity)
    alice_info = storage.get_user_info("alice")
    bob_info = storage.get_user_info("bob")
    
    if alice_info and bob_info:
        combined_usage = alice_info['used_storage'] + bob_info['used_storage']
        bob_capacity = bob_info['capacity']
        
        print(f"    Combined usage would be: {combined_usage} bytes")
        print(f"    Bob's capacity: {bob_capacity} bytes")
        
        if combined_usage > bob_capacity:
            result = storage.merge_user("bob", "alice")
            if result is None:
                print("  ✅ Correctly rejected merge that would exceed capacity")
            else:
                print("  ❌ Incorrectly accepted merge that exceeds capacity")
    
    return storage


def demonstrate_integration(storage):
    """Demonstrate integration between all levels."""
    print_separator("CROSS-LEVEL INTEGRATION DEMO")
    print("Demonstrating how all levels work together seamlessly")
    
    print_step(1, "Cross-level file operations")
    print("  Adding files through different levels and verifying consistency...")
    
    # Add file via Level 1 (admin)
    storage.add_file("shared_document.pdf", 400)
    
    # Add file via Level 3 (user)
    storage.add_file_by("alice", "alice_shared.txt", 100)
    
    # Query via Level 2 (should see both files)
    shared_files = storage.get_n_largest("", 10)  # All files
    print(f"  📁 Total files in system: {len(shared_files)}")
    
    print_step(2, "User-aware prefix queries")
    print("  Querying files by prefix across all users...")
    
    # Show all files owned by each user
    all_users = ["admin", "alice", "bob", "charlie"]
    for user_id in all_users:
        user_files = storage.list_files_by_user(user_id)
        if user_files:
            print(f"  👤 {user_id}: {len(user_files)} files")
            for name, size in user_files[:3]:  # Show first 3
                print(f"     - {name} ({size} bytes)")
    
    print_step(3, "File deletion impact on users")
    print("  Deleting a user-owned file and checking storage update...")
    
    # Find a file owned by alice
    alice_files = storage.list_files_by_user("alice")
    if alice_files:
        file_to_delete, file_size = alice_files[0]
        
        # Check alice's storage before deletion
        alice_before = storage.get_user_info("alice")
        print(f"  Alice before deletion: {alice_before['used_storage']} bytes used")
        
        # Delete the file
        deleted_size = storage.delete_file(file_to_delete)
        print(f"  Deleted {file_to_delete} (size: {deleted_size} bytes)")
        
        # Check alice's storage after deletion
        alice_after = storage.get_user_info("alice")
        print(f"  Alice after deletion: {alice_after['used_storage']} bytes used")
        
        storage_diff = alice_before['used_storage'] - alice_after['used_storage']
        if storage_diff == deleted_size:
            print("  ✅ User storage correctly updated after file deletion")
        else:
            print("  ❌ User storage update mismatch")
    
    print_step(4, "System integrity validation")
    print("  Running comprehensive integrity checks...")
    
    issues = storage.validate_system_integrity()
    if not issues:
        print("  ✅ System integrity: All checks passed")
    else:
        print("  ❌ System integrity issues found:")
        for issue in issues:
            print(f"    - {issue}")
    
    # Final statistics
    print_step(5, "Final system statistics")
    stats = storage.get_storage_stats()
    print(f"  📊 System Overview:")
    print(f"    Total files: {stats['total_files']}")
    print(f"    Total storage used: {stats['total_size']} bytes")
    print(f"    Total users: {stats['total_users']}")
    print(f"    Average file size: {stats['average_file_size']:.1f} bytes")
    
    # Show largest files
    largest_files = storage.get_largest_files(5)
    print(f"\n  📈 Top 5 largest files:")
    for i, (name, size, owner) in enumerate(largest_files, 1):
        print(f"    {i}. {name} ({size} bytes) - owned by {owner}")


def main():
    """Run the complete interactive demo."""
    print("🗂️  CLOUD-BASED FILE STORAGE SYSTEM - INTERACTIVE DEMO")
    print_separator()
    print("This demo showcases a multi-level cloud storage implementation")
    print("designed for technical interview preparation.")
    print("\nThe system evolves through 3 levels:")
    print("  Level 1: Basic file operations (add, get_size, delete)")
    print("  Level 2: Prefix-based file querying with sorting")
    print("  Level 3: User management with capacity limits")
    print_separator()
    
    input("\nPress Enter to start the demo...")
    
    try:
        # Level 1 Demo
        storage = demonstrate_level1()
        input("\nPress Enter to continue to Level 2...")
        
        # Level 2 Demo
        storage = demonstrate_level2(storage)
        input("\nPress Enter to continue to Level 3...")
        
        # Level 3 Demo
        storage = demonstrate_level3(storage)
        input("\nPress Enter to see integration demo...")
        
        # Integration Demo
        demonstrate_integration(storage)
        
        print_separator("DEMO COMPLETED")
        print("🎉 Congratulations! You've seen the complete cloud storage system in action.")
        print("\n💡 Key Implementation Highlights:")
        print("  ✓ Efficient file operations with O(1) lookups")
        print("  ✓ Flexible prefix-based querying with custom sorting")
        print("  ✓ User capacity management with real-time tracking")
        print("  ✓ Seamless account merging with validation")
        print("  ✓ Cross-level integration and data consistency")
        print("  ✓ Comprehensive error handling and edge cases")
        
        print("\n🎯 Interview Preparation Tips:")
        print("  1. Understand the data structures used (dicts, sets, dataclasses)")
        print("  2. Explain the time complexity of each operation")
        print("  3. Discuss how the system could scale (sharding, caching, etc.)")
        print("  4. Consider additional features (versioning, permissions, etc.)")
        print("  5. Practice implementing each level step by step")
        
        print("\n📚 Next Steps:")
        print("  • Run 'python run_tests.py' to verify the implementation")
        print("  • Study the code structure and design patterns")
        print("  • Practice explaining the solution out loud")
        print("  • Consider optimizations and alternative approaches")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 