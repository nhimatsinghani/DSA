# Cache Versioning: Invalidation Without Deletion

## The Problem with Traditional Cache Invalidation

Traditional cache invalidation has several challenges:

- **Race Conditions**: Cache might be invalidated after new data is written but before cache is updated
- **Partial Failures**: Some cache nodes might fail to invalidate while others succeed
- **Thundering Herd**: All clients rush to rebuild cache simultaneously after invalidation
- **Complexity**: Coordinating invalidation across distributed cache layers

## How Cache Versioning Works

Cache versioning **doesn't actually delete old cache entries**. Instead, it makes them **unreachable** by changing the cache key pattern when data changes.

### The Key Insight

Instead of having cache keys like:

```
user:123 → {name: "John", email: "john@example.com"}
```

You have versioned keys like:

```
user:123:version → 5
user:123:v5 → {name: "John", email: "john@example.com"}
```

When data changes, you increment the version:

```
user:123:version → 6  (updated)
user:123:v6 → {name: "Johnny", email: "johnny@example.com"}  (new entry)
user:123:v5 → {name: "John", email: "john@example.com"}  (still exists but unreachable)
```

## Step-by-Step Process

### Reading Data

1. **Read version**: `GET user:123:version` → returns `6`
2. **Construct versioned key**: `user:123:v6`
3. **Read data**: `GET user:123:v6` → returns user data
4. **On cache miss**: Fetch from database, cache with versioned key

### Updating Data

1. **Update database**: Change user's name to "Johnny"
2. **Increment version**: `INCR user:123:version` → returns `7`
3. **Cache new data**: `SET user:123:v7` → new user data
4. **No explicit invalidation needed**

## Code Example

```python
import redis
import json
from typing import Optional, Dict, Any

class VersionedCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get_user(self, user_id: int) -> Optional[Dict[Any, Any]]:
        """Read user data using cache versioning"""

        # Step 1: Get current version number
        version_key = f"user:{user_id}:version"
        version = self.redis.get(version_key)

        if not version:
            # No version exists, fetch from database
            user_data = self._fetch_user_from_db(user_id)
            if user_data:
                # Initialize version and cache data
                version = 1
                self.redis.set(version_key, version)
                data_key = f"user:{user_id}:v{version}"
                self.redis.setex(data_key, 3600, json.dumps(user_data))
            return user_data

        # Step 2: Construct versioned key
        data_key = f"user:{user_id}:v{version.decode()}"

        # Step 3: Try to get data with versioned key
        cached_data = self.redis.get(data_key)

        if cached_data:
            return json.loads(cached_data)
        else:
            # Cache miss - fetch from database and cache
            user_data = self._fetch_user_from_db(user_id)
            if user_data:
                self.redis.setex(data_key, 3600, json.dumps(user_data))
            return user_data

    def update_user(self, user_id: int, new_data: Dict[Any, Any]):
        """Update user data and increment version"""

        # Step 1: Update database
        self._update_user_in_db(user_id, new_data)

        # Step 2: Increment version (this effectively "invalidates" old cache)
        version_key = f"user:{user_id}:version"
        new_version = self.redis.incr(version_key)

        # Step 3: Cache new data with new version
        data_key = f"user:{user_id}:v{new_version}"
        self.redis.setex(data_key, 3600, json.dumps(new_data))

        # Note: Old cache entries like user:123:v5 still exist
        # but are now unreachable since version is v6

    def _fetch_user_from_db(self, user_id: int) -> Optional[Dict[Any, Any]]:
        # Simulate database fetch
        return {"id": user_id, "name": "John", "email": "john@example.com"}

    def _update_user_in_db(self, user_id: int, data: Dict[Any, Any]):
        # Simulate database update
        pass
```

## Why This "Invalidates" Without Deleting

Let's trace through an example:

### Initial State

```
user:123:version → 1
user:123:v1 → {"name": "John", "email": "john@example.com"}
```

### After Update

```
user:123:version → 2  (incremented)
user:123:v2 → {"name": "Johnny", "email": "johnny@example.com"}  (new)
user:123:v1 → {"name": "John", "email": "john@example.com"}  (still exists)
```

### What Happens to Old Cache?

- Old cache entry `user:123:v1` still exists in memory
- But no new requests will ever access it because:
  - All new requests read version number first
  - Version number is now `2`, so they construct key `user:123:v2`
  - `user:123:v1` becomes "unreachable" and will eventually expire

## Timeline Visualization

```
Time 1: Data = "John"
├── user:123:version = 1
└── user:123:v1 = "John"

Time 2: Update to "Johnny"
├── user:123:version = 2  (incremented)
├── user:123:v2 = "Johnny"  (new entry)
└── user:123:v1 = "John"  (old entry, unreachable)

Time 3: All requests now use v2
├── GET user:123:version → 2
├── GET user:123:v2 → "Johnny"  ✓ (current data)
└── user:123:v1 = "John"  (ignored, will expire)
```

## Trade-offs

### Advantages

- **No race conditions**: Version increments are atomic
- **No partial failures**: Either version increments or it doesn't
- **No thundering herd**: Old cache serves requests during transition
- **Simple implementation**: Just increment a counter

### Disadvantages

- **Extra cache read**: Every request needs version lookup first
- **Memory usage**: Old cache entries persist until expiration
- **Two-round-trip**: More network calls to cache

## Advanced Patterns

### Batch Version Updates

```python
# Update multiple related entities with same version
def update_user_profile(user_id: int, profile_data: Dict):
    # Increment version once
    version = self.redis.incr(f"user:{user_id}:version")

    # Cache multiple related data with same version
    self.redis.setex(f"user:{user_id}:v{version}", 3600, json.dumps(profile_data))
    self.redis.setex(f"user:{user_id}:settings:v{version}", 3600, json.dumps(settings))
    self.redis.setex(f"user:{user_id}:preferences:v{version}", 3600, json.dumps(prefs))
```

### Global Version for Cache-wide Invalidation

```python
# Invalidate entire cache layer by incrementing global version
global_version = redis.incr("cache:global:version")
# All cache keys now need to include global version
key = f"user:{user_id}:v{local_version}:g{global_version}"
```

## When to Use Cache Versioning

**Good for:**

- Frequently updated data
- Systems where consistency is critical
- Distributed cache scenarios
- When you can afford extra cache reads

**Not good for:**

- Read-heavy workloads where extra latency matters
- Memory-constrained cache systems
- Simple single-node cache setups

## Summary

Cache versioning achieves "invalidation" by making old cache entries unreachable rather than deleting them. It's a trade-off between simplicity/reliability and performance, eliminating many distributed caching problems at the cost of additional cache reads.
