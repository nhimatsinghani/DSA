#!/usr/bin/env python3
"""
Cache Versioning Demo

This demo shows how cache versioning works as an invalidation technique
without actually deleting old cache entries.
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


class InMemoryCache:
    """Simple in-memory cache to simulate Redis behavior"""
    
    def __init__(self):
        self.data = {}
        self.access_log = []  # Track what keys are accessed
    
    def get(self, key: str) -> Optional[str]:
        self.access_log.append(f"GET {key}")
        return self.data.get(key)
    
    def set(self, key: str, value: str):
        self.access_log.append(f"SET {key} = {value}")
        self.data[key] = value
    
    def incr(self, key: str) -> int:
        current = int(self.data.get(key, 0))
        new_value = current + 1
        self.set(key, str(new_value))
        return new_value
    
    def keys_matching(self, pattern: str) -> list:
        """Get all keys matching a pattern (for demo purposes)"""
        return [k for k in self.data.keys() if pattern in k]
    
    def show_state(self):
        """Show current cache state"""
        print("\n=== Cache State ===")
        for key, value in sorted(self.data.items()):
            print(f"{key} → {value}")
        print("==================")


@dataclass
class User:
    id: int
    name: str
    email: str
    
    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class VersionedUserCache:
    """User cache using version-based invalidation"""
    
    def __init__(self, cache: InMemoryCache):
        self.cache = cache
        self.database = {  # Simulate database
            123: User(123, "John Doe", "john@example.com"),
            456: User(456, "Jane Smith", "jane@example.com")
        }
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user with cache versioning"""
        print(f"\n🔍 Getting user {user_id}...")
        
        # Step 1: Get version number
        version_key = f"user:{user_id}:version"
        version = self.cache.get(version_key)
        
        if not version:
            print(f"   No version found for user {user_id}, initializing...")
            # Initialize version
            version = str(self.cache.incr(version_key))
            
        print(f"   Current version: {version}")
        
        # Step 2: Construct versioned data key
        data_key = f"user:{user_id}:v{version}"
        print(f"   Looking for data at key: {data_key}")
        
        # Step 3: Try to get cached data
        cached_data = self.cache.get(data_key)
        
        if cached_data:
            print(f"   ✅ Cache HIT! Retrieved from {data_key}")
            return eval(cached_data)  # In real code, use json.loads
        else:
            print(f"   ❌ Cache MISS! Fetching from database...")
            # Fetch from database
            user = self.database.get(user_id)
            if user:
                user_dict = user.to_dict()
                self.cache.set(data_key, str(user_dict))
                print(f"   💾 Cached data at {data_key}")
                return user_dict
            return None
    
    def update_user(self, user_id: int, **updates):
        """Update user and increment version (effectively invalidating old cache)"""
        print(f"\n📝 Updating user {user_id} with {updates}...")
        
        # Step 1: Update database
        if user_id in self.database:
            user = self.database[user_id]
            for field, value in updates.items():
                setattr(user, field, value)
            print(f"   Database updated: {user}")
        
        # Step 2: Increment version (this "invalidates" old cache)
        version_key = f"user:{user_id}:version"
        new_version = self.cache.incr(version_key)
        print(f"   🔄 Version incremented to: {new_version}")
        
        # Step 3: Cache new data with new version
        new_data_key = f"user:{user_id}:v{new_version}"
        user_dict = self.database[user_id].to_dict()
        self.cache.set(new_data_key, str(user_dict))
        print(f"   💾 New data cached at: {new_data_key}")
        
        print(f"   🎯 Old cache entries still exist but are now unreachable!")


def demonstrate_cache_versioning():
    """Main demonstration of cache versioning"""
    
    print("=" * 60)
    print("CACHE VERSIONING DEMONSTRATION")
    print("=" * 60)
    
    # Initialize cache and user service
    cache = InMemoryCache()
    user_service = VersionedUserCache(cache)
    
    print("\n1️⃣ INITIAL REQUESTS - Building Cache")
    print("-" * 40)
    
    # First request - cache miss, will initialize version
    user1 = user_service.get_user(123)
    print(f"Retrieved: {user1}")
    
    # Second request - cache hit
    user1_again = user_service.get_user(123)
    print(f"Retrieved: {user1_again}")
    
    cache.show_state()
    
    print("\n2️⃣ UPDATE USER - Version Increment")
    print("-" * 40)
    
    # Update user - this increments version
    user_service.update_user(123, name="Johnny Doe", email="johnny@example.com")
    
    cache.show_state()
    
    print("\n3️⃣ REQUEST AFTER UPDATE - New Version Used")
    print("-" * 40)
    
    # Request after update - will use new version
    updated_user = user_service.get_user(123)
    print(f"Retrieved: {updated_user}")
    
    cache.show_state()
    
    print("\n4️⃣ ANALYSIS - What Happened to Old Cache?")
    print("-" * 40)
    
    # Show all cache keys for user 123
    user_keys = cache.keys_matching("user:123")
    print(f"All cache keys for user 123: {user_keys}")
    
    # Try to access old version directly (this won't happen in normal flow)
    old_cache = cache.get("user:123:v1")
    new_cache = cache.get("user:123:v2")
    
    print(f"\nOld cache (v1) still exists: {old_cache}")
    print(f"New cache (v2) has updated data: {new_cache}")
    print(f"\n🔑 Key insight: Old cache exists but is UNREACHABLE through normal flow!")
    
    print("\n5️⃣ ANOTHER UPDATE - Version Increment Again")
    print("-" * 40)
    
    user_service.update_user(123, email="john.doe@newcompany.com")
    user_service.get_user(123)  # Use new version
    
    cache.show_state()
    
    final_keys = cache.keys_matching("user:123")
    print(f"\nFinal cache keys for user 123: {final_keys}")
    print(f"Notice: v1 and v2 still exist, but only v3 is reachable!")
    
    print("\n6️⃣ ACCESS LOG - What Actually Happened")
    print("-" * 40)
    print("Cache access log:")
    for i, log_entry in enumerate(cache.access_log, 1):
        print(f"{i:2d}. {log_entry}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Cache versioning achieves 'invalidation' by making old entries unreachable")
    print("✅ No race conditions - version increments are atomic")
    print("✅ No explicit deletion required")
    print("✅ Old cache entries naturally expire over time")
    print("❌ Requires extra cache read for version number")
    print("❌ Uses more memory (old entries persist until expiration)")


if __name__ == "__main__":
    demonstrate_cache_versioning() 