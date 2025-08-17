#!/usr/bin/env python3
"""
Evolving Key-Value Store Demo

This demo showcases all 4 stages of the evolving key-value store problem.
It's designed to help with technical interview preparation by demonstrating
the expected functionality at each stage.

Run this demo to see the complete functionality in action.
"""

import time
from key_value_store import EvolvingKeyValueStore


def print_stage_header(stage_num, title):
    """Print a formatted stage header."""
    print("\n" + "=" * 80)
    print(f"STAGE {stage_num}: {title}")
    print("=" * 80)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def demo_stage1_basic_operations():
    """Demonstrate Stage 1: Basic get/set operations."""
    print_stage_header(1, "BASIC GET/SET OPERATIONS")
    
    store = EvolvingKeyValueStore()
    
    print_section("Basic Set and Get")
    store.set_basic("username", "alice")
    store.set_basic("age", 25)
    store.set_basic("city", "San Francisco")
    
    print(f"username: {store.get_basic('username')}")
    print(f"age: {store.get_basic('age')}")
    print(f"city: {store.get_basic('city')}")
    
    print_section("Getting Non-existent Key")
    result = store.get_basic("nonexistent")
    print(f"nonexistent key: {result}")
    
    print_section("Overwriting Values")
    print(f"age before: {store.get_basic('age')}")
    store.set_basic("age", 26)
    print(f"age after: {store.get_basic('age')}")
    
    print_section("Different Data Types")
    store.set_basic("list_data", [1, 2, 3, "four"])
    store.set_basic("dict_data", {"nested": "value", "count": 42})
    store.set_basic("bool_data", True)
    
    print(f"list: {store.get_basic('list_data')}")
    print(f"dict: {store.get_basic('dict_data')}")
    print(f"bool: {store.get_basic('bool_data')}")
    
    return store


def demo_stage2_ttl_operations():
    """Demonstrate Stage 2: TTL operations."""
    print_stage_header(2, "TTL (TIME-TO-LIVE) OPERATIONS")
    
    store = EvolvingKeyValueStore()
    
    print_section("Setting Values Without TTL")
    store.set_with_ttl("permanent_key", "never_expires")
    print(f"permanent_key: {store.get_with_ttl('permanent_key')}")
    
    print_section("Setting Values With TTL")
    store.set_with_ttl("temporary_key", "expires_in_3_seconds", ttl=3.0)
    store.set_with_ttl("very_temporary", "expires_soon", ttl=0.5)
    
    print(f"temporary_key: {store.get_with_ttl('temporary_key')}")
    print(f"very_temporary: {store.get_with_ttl('very_temporary')}")
    
    print_section("Demonstrating TTL Expiration")
    print("Waiting 1 second...")
    time.sleep(1.0)
    
    print(f"permanent_key (should exist): {store.get_with_ttl('permanent_key')}")
    print(f"temporary_key (should exist): {store.get_with_ttl('temporary_key')}")
    print(f"very_temporary (should be None): {store.get_with_ttl('very_temporary')}")
    
    print_section("Overwriting TTL Values")
    store.set_with_ttl("changeable", "first_value", ttl=10.0)
    print(f"changeable (long TTL): {store.get_with_ttl('changeable')}")
    
    store.set_with_ttl("changeable", "second_value", ttl=0.2)
    print(f"changeable (short TTL): {store.get_with_ttl('changeable')}")
    
    print("Waiting for short TTL to expire...")
    time.sleep(0.3)
    print(f"changeable (after expiration): {store.get_with_ttl('changeable')}")
    
    return store


def demo_stage3_point_in_time():
    """Demonstrate Stage 3: Point-in-time queries."""
    print_stage_header(3, "POINT-IN-TIME QUERIES")
    
    store = EvolvingKeyValueStore()
    
    print_section("Building History for a Key")
    timestamps = []
    
    store.set_with_history("user_status", "offline")
    timestamps.append(("offline", time.time()))
    print(f"t0: Set user_status = 'offline'")
    
    time.sleep(0.1)
    store.set_with_history("user_status", "online")
    timestamps.append(("online", time.time()))
    print(f"t1: Set user_status = 'online'")
    
    time.sleep(0.1)
    store.set_with_history("user_status", "away")
    timestamps.append(("away", time.time()))
    print(f"t2: Set user_status = 'away'")
    
    time.sleep(0.1)
    store.set_with_history("user_status", "busy")
    timestamps.append(("busy", time.time()))
    print(f"t3: Set user_status = 'busy'")
    
    print_section("Current Value")
    current = store.get_current_with_history("user_status")
    print(f"Current user_status: {current}")
    
    print_section("Historical Queries")
    for i, (expected_value, timestamp) in enumerate(timestamps):
        # Query slightly after each timestamp
        result = store.get_at_time("user_status", timestamp + 0.01)
        print(f"Value at t{i}: {result} (expected: {expected_value})")
    
    print_section("Point-in-Time with TTL")
    start_time = time.time()
    store.set_with_history("session", "active", ttl=0.3)
    time.sleep(0.1)
    
    # Query before expiration
    result = store.get_at_time("session", time.time())
    print(f"Session before expiration: {result}")
    
    # Wait for expiration
    time.sleep(0.3)
    
    # Query after expiration
    result = store.get_at_time("session", time.time())
    print(f"Session after expiration: {result}")
    
    # But historical query within valid window should work
    result = store.get_at_time("session", start_time + 0.05)
    print(f"Session historical query (valid window): {result}")
    
    return store


def demo_stage4_deletion():
    """Demonstrate Stage 4: Deletion operations."""
    print_stage_header(4, "DELETION OPERATIONS")
    
    store = EvolvingKeyValueStore()
    
    print_section("Basic Deletion")
    store.set("to_delete", "goodbye")
    print(f"Before deletion: {store.get('to_delete')}")
    
    delete_result = store.delete("to_delete")
    print(f"Delete operation returned: {delete_result}")
    print(f"After deletion: {store.get('to_delete')}")
    
    print_section("Deleting Non-existent Key")
    delete_result = store.delete("never_existed")
    print(f"Delete non-existent key returned: {delete_result}")
    
    print_section("Deletion with History")
    # Build some history
    store.set("historical_key", "version_1")
    time.sleep(0.1)
    before_deletion = time.time()
    
    store.set("historical_key", "version_2")
    time.sleep(0.1)
    
    deletion_time = time.time()
    delete_result = store.delete("historical_key")
    time.sleep(0.1)
    after_deletion = time.time()
    
    print(f"Deletion returned: {delete_result}")
    print(f"Current value: {store.get('historical_key')}")
    print(f"Historical value (before deletion): {store.get_at_time('historical_key', before_deletion)}")
    print(f"Historical value (after deletion): {store.get_at_time('historical_key', after_deletion)}")
    
    print_section("Recreation After Deletion")
    store.set("phoenix", "first_life")
    print(f"Initial value: {store.get('phoenix')}")
    
    store.delete("phoenix")
    print(f"After deletion: {store.get('phoenix')}")
    
    store.set("phoenix", "second_life")
    print(f"After recreation: {store.get('phoenix')}")
    
    print_section("Deletion with TTL")
    store.set("ttl_delete_test", "temporary", ttl=1.0)
    print(f"TTL key before deletion: {store.get('ttl_delete_test')}")
    
    delete_result = store.delete("ttl_delete_test")
    print(f"Delete TTL key returned: {delete_result}")
    print(f"TTL key after deletion: {store.get('ttl_delete_test')}")
    
    return store


def demo_unified_interface():
    """Demonstrate the unified interface that works across all stages."""
    print_stage_header("UNIFIED", "UNIFIED INTERFACE (ALL STAGES COMBINED)")
    
    store = EvolvingKeyValueStore()
    
    print_section("Mixed Operations")
    
    # Basic operations
    store.set("user:1", {"name": "Alice", "role": "admin"})
    store.set("user:2", {"name": "Bob", "role": "user"})
    
    # Operations with TTL
    store.set("session:abc123", "active", ttl=2.0)
    store.set("cache:data", "cached_content", ttl=5.0)
    
    # Build history
    store.set("server_status", "starting")
    time.sleep(0.05)
    store.set("server_status", "running")
    time.sleep(0.05)
    before_maintenance = time.time()
    store.set("server_status", "maintenance")
    time.sleep(0.05)
    
    print("Initial state:")
    print(f"  user:1 = {store.get('user:1')}")
    print(f"  user:2 = {store.get('user:2')}")
    print(f"  session:abc123 = {store.get('session:abc123')}")
    print(f"  server_status = {store.get('server_status')}")
    
    print_section("Utility Methods")
    print(f"Total keys: {store.size()}")
    print(f"All keys: {store.get_all_keys()}")
    
    print_section("Point-in-time Query")
    historical_status = store.get_at_time("server_status", before_maintenance - 0.01)
    print(f"Server status before maintenance: {historical_status}")
    
    print_section("Deletions")
    store.delete("user:2")
    print(f"After deleting user:2:")
    print(f"  user:2 = {store.get('user:2')}")
    print(f"  Total keys: {store.size()}")
    
    print_section("Waiting for TTL Expiration")
    print("Waiting 3 seconds for session to expire...")
    time.sleep(3.0)
    
    print("After TTL expiration:")
    print(f"  session:abc123 = {store.get('session:abc123')}")
    print(f"  cache:data = {store.get('cache:data')}")
    print(f"  Total keys: {store.size()}")
    
    return store


def demo_performance_considerations():
    """Demonstrate performance considerations and edge cases."""
    print_stage_header("PERF", "PERFORMANCE CONSIDERATIONS & EDGE CASES")
    
    store = EvolvingKeyValueStore()
    
    print_section("Handling Large Numbers of Keys")
    num_keys = 1000
    
    start_time = time.time()
    for i in range(num_keys):
        store.set(f"key_{i:04d}", f"value_{i}")
    
    creation_time = time.time() - start_time
    print(f"Created {num_keys} keys in {creation_time:.3f} seconds")
    print(f"Average per key: {creation_time/num_keys*1000:.3f} ms")
    
    print_section("Batch Operations")
    start_time = time.time()
    
    # Get operations
    for i in range(0, num_keys, 10):
        value = store.get(f"key_{i:04d}")
    
    retrieval_time = time.time() - start_time
    print(f"Retrieved {num_keys//10} keys in {retrieval_time:.3f} seconds")
    
    # Deletion operations
    start_time = time.time()
    deleted_count = 0
    for i in range(0, num_keys, 2):  # Delete every other key
        if store.delete(f"key_{i:04d}"):
            deleted_count += 1
    
    deletion_time = time.time() - start_time
    print(f"Deleted {deleted_count} keys in {deletion_time:.3f} seconds")
    print(f"Remaining keys: {store.size()}")
    
    print_section("Edge Cases")
    
    # Empty string key
    store.set("", "empty_key_value")
    print(f"Empty string key: '{store.get('')}'")
    
    # None value
    store.set("null_value", None)
    print(f"None value: {store.get('null_value')}")
    
    # Zero TTL
    store.set("zero_ttl", "should_expire", ttl=0.0)
    time.sleep(0.01)
    print(f"Zero TTL key: {store.get('zero_ttl')}")
    
    # Negative TTL
    store.set("negative_ttl", "already_expired", ttl=-1.0)
    print(f"Negative TTL key: {store.get('negative_ttl')}")
    
    store.clear()
    print(f"After clear(): {store.size()} keys remain")


def run_all_tests():
    """Run all stage tests to verify implementation."""
    print_stage_header("TEST", "RUNNING ALL TEST SUITES")
    
    # Import test runners
    from test_stage1 import run_stage1_tests
    from test_stage2 import run_stage2_tests
    from test_stage3 import run_stage3_tests
    from test_stage4 import run_stage4_tests
    
    results = []
    
    # Run each stage
    results.append(("Stage 1", run_stage1_tests()))
    results.append(("Stage 2", run_stage2_tests()))
    results.append(("Stage 3", run_stage3_tests()))
    results.append(("Stage 4", run_stage4_tests()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for stage_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{stage_name:12} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Implementation is ready for interview.")
    else:
        print("⚠️  Some tests failed. Review the implementation.")
    print("=" * 80)
    
    return all_passed


def main():
    """Run the complete demo."""
    print("EVOLVING KEY-VALUE STORE DEMONSTRATION")
    print("=" * 80)
    print("This demo showcases a complete implementation of a multi-stage")
    print("key-value store problem commonly used in technical interviews.")
    print()
    print("Each stage builds upon the previous one:")
    print("  Stage 1: Basic get/set operations")
    print("  Stage 2: TTL (Time-To-Live) functionality")
    print("  Stage 3: Point-in-time queries with history")
    print("  Stage 4: Deletion operations")
    print()
    
    try:
        # Run individual stage demos
        demo_stage1_basic_operations()
        demo_stage2_ttl_operations()
        demo_stage3_point_in_time()
        demo_stage4_deletion()
        
        # Show unified interface
        demo_unified_interface()
        
        # Performance and edge cases
        demo_performance_considerations()
        
        # Run tests
        run_all_tests()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("Demo completed! Good luck with your technical interview!")
    print("=" * 80)


if __name__ == "__main__":
    main() 