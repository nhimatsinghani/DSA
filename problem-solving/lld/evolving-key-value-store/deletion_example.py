#!/usr/bin/env python3
"""
Demonstration: Why deleted_keys Set is Essential

This example shows the problems that would occur without proper deletion tracking
and how the deleted_keys set solves them.
"""

import time
from key_value_store import EvolvingKeyValueStore


def demonstrate_deletion_tracking():
    """Show why deleted_keys set is essential."""
    
    print("=" * 60)
    print("DELETION TRACKING DEMONSTRATION")
    print("=" * 60)
    
    store = EvolvingKeyValueStore()
    
    # === Scenario 1: Basic Deletion ===
    print("\n1. Basic Deletion Behavior")
    print("-" * 30)
    
    store.set("user", "Alice")
    print(f"After set: get('user') = {store.get('user')}")
    print(f"exists('user') = {store.exists('user')}")
    
    delete_result = store.delete("user")
    print(f"delete('user') returned: {delete_result}")
    print(f"After delete: get('user') = {store.get('user')}")
    print(f"exists('user') = {store.exists('user')}")
    
    # === Scenario 2: Double Deletion Prevention ===
    print("\n2. Double Deletion Prevention")
    print("-" * 30)
    
    second_delete = store.delete("user")
    print(f"Second delete('user') returned: {second_delete}")
    print("^ This returns False because key is already deleted")
    
    # === Scenario 3: Recreation After Deletion ===
    print("\n3. Recreation After Deletion")
    print("-" * 30)
    
    store.set("user", "Bob")  # Recreate with new value
    print(f"After recreation: get('user') = {store.get('user')}")
    print(f"exists('user') = {store.exists('user')}")
    print("^ Key can be recreated after deletion")
    
    # Check that it's removed from deleted_keys
    print(f"'user' in deleted_keys: {'user' in store.deleted_keys}")
    
    # === Scenario 4: Historical Queries Around Deletion ===
    print("\n4. Historical Queries Around Deletion")
    print("-" * 30)
    
    # Create a timeline
    store.set("timeline", "v1")
    time.sleep(0.05)
    before_delete = time.time()
    
    store.delete("timeline")
    time.sleep(0.05)
    after_delete = time.time()
    
    # Historical queries
    before_result = store.get_at_time("timeline", before_delete - 0.01)
    after_result = store.get_at_time("timeline", after_delete)
    
    print(f"Value before deletion: {before_result}")
    print(f"Value after deletion: {after_result}")
    print("^ History preserves data before deletion, but not after")
    
    # === Scenario 5: Complex Multi-Operation Timeline ===
    print("\n5. Complex Timeline with Multiple Operations")
    print("-" * 40)
    
    # Build complex history
    store.set("complex", "initial")
    time.sleep(0.02)
    t1 = time.time()
    
    store.set("complex", "updated")  
    time.sleep(0.02)
    t2 = time.time()
    
    store.delete("complex")
    time.sleep(0.02)
    t3 = time.time()
    
    store.set("complex", "recreated")
    time.sleep(0.02)
    t4 = time.time()
    
    # Query at each point in timeline
    print(f"At t1 (after initial): {store.get_at_time('complex', t1)}")
    print(f"At t2 (after update): {store.get_at_time('complex', t2)}")  
    print(f"At t3 (after delete): {store.get_at_time('complex', t3)}")
    print(f"At t4 (after recreate): {store.get_at_time('complex', t4)}")
    print(f"Current value: {store.get('complex')}")


def show_without_deleted_keys():
    """Demonstrate what would happen without deleted_keys tracking."""
    
    print("\n" + "=" * 60)
    print("PROBLEMS WITHOUT deleted_keys TRACKING")
    print("=" * 60)
    
    print("""
Without the deleted_keys set, we would face these problems:

1. **No Double-Delete Prevention**
   - delete("key") could return True multiple times
   - No way to distinguish "already deleted" from "doesn't exist"

2. **Ambiguous Recreation**
   - Can't tell if set() after delete() is recreation or update
   - History tracking becomes confused

3. **Incorrect Historical Queries**
   - No way to mark "deletion point" in timeline
   - get_at_time() after deletion might still return values

4. **Inconsistent exists() Behavior**
   - exists() couldn't distinguish deleted keys from expired keys
   - Size calculations would be incorrect

5. **Memory Leaks**
   - Without tracking, we might never clean up deletion markers
   - History could grow indefinitely
""")


def show_alternative_approaches():
    """Show why alternative approaches don't work as well."""
    
    print("\n" + "=" * 60)
    print("WHY ALTERNATIVE APPROACHES DON'T WORK")
    print("=" * 60)
    
    print("""
❌ **Alternative 1: Just remove from data structures**
   Problem: No way to distinguish "never existed" from "was deleted"
   
❌ **Alternative 2: Mark in history only**
   Problem: Expensive to scan history for every operation
   
❌ **Alternative 3: Use None values**
   Problem: Can't distinguish None value from deleted key
   
❌ **Alternative 4: Separate deleted flag per key**
   Problem: More complex than a simple set, harder to manage
   
✅ **Our Approach: deleted_keys Set**
   - O(1) lookup to check if key is deleted
   - Clear semantic distinction between states
   - Easy to manage (add/remove from set)
   - Memory efficient
   - Plays well with recreation logic
""")


if __name__ == "__main__":
    demonstrate_deletion_tracking()
    show_without_deleted_keys()
    show_alternative_approaches()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("""
The deleted_keys set is essential because it provides:

1. **Clear State Tracking**: Unambiguous record of deleted keys
2. **Performance**: O(1) deletion checks vs O(n) history scanning  
3. **Correctness**: Proper semantics for edge cases
4. **Simplicity**: Clean separation of concerns

This design pattern is common in database systems where you need
to track deletion while preserving history for auditing/recovery.
""") 