# Ticketmaster System Design - Cache Invalidation Deep Dive

## Cache Invalidation with Cache Tags and Triggers

### The Challenge

In a Ticketmaster-like system, cache invalidation becomes complex due to the interconnected nature of data:

- When an event's details change, multiple cached search results become stale
- Venue capacity updates affect all events at that venue
- Performer information changes impact all their events
- Seat availability changes affect event listings and search results

Traditional TTL-based invalidation is insufficient because:

1. **Stale Data Risk**: Users might see outdated pricing or availability
2. **Over-invalidation**: TTLs cause unnecessary cache misses
3. **Under-invalidation**: Long TTLs lead to stale data serving

### Cache Tags: Semantic Cache Organization

Cache tags are semantic labels attached to cache entries that group related data. Instead of managing individual cache keys, we invalidate by tags.

#### Tag Structure for Ticketmaster

```
event:{eventId}           - All data related to specific event
venue:{venueId}           - All data related to specific venue
performer:{performerId}   - All data related to specific performer
search:events:{hash}      - Search result caches
category:{categoryId}     - Event category-based caches
location:{city}           - Location-based searches
```

### Cache Invalidation Triggers Architecture

#### 1. Database Trigger Pattern

**PostgreSQL Trigger Setup:**

```sql
-- Create notification table for cache invalidation
CREATE TABLE cache_invalidation_queue (
    id SERIAL PRIMARY KEY,
    tags TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

-- Trigger function for event changes
CREATE OR REPLACE FUNCTION notify_event_cache_invalidation()
RETURNS TRIGGER AS $$
BEGIN
    -- Determine which tags to invalidate based on the change
    IF TG_OP = 'UPDATE' THEN
        -- Event details changed
        INSERT INTO cache_invalidation_queue (tags)
        VALUES (ARRAY[
            'event:' || NEW.id,
            'venue:' || NEW.venue_id,
            'performer:' || NEW.performer_id,
            'search:events:*',  -- Wildcard for all search caches
            'category:' || NEW.category_id
        ]);

        -- If venue changed, additional invalidation
        IF OLD.venue_id != NEW.venue_id THEN
            INSERT INTO cache_invalidation_queue (tags)
            VALUES (ARRAY['venue:' || OLD.venue_id]);
        END IF;

    ELSIF TG_OP = 'INSERT' THEN
        -- New event added
        INSERT INTO cache_invalidation_queue (tags)
        VALUES (ARRAY[
            'search:events:*',
            'venue:' || NEW.venue_id,
            'performer:' || NEW.performer_id,
            'category:' || NEW.category_id
        ]);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to events table
CREATE TRIGGER event_cache_invalidation_trigger
    AFTER INSERT OR UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION notify_event_cache_invalidation();
```

#### 2. Cache Invalidation Worker

**Python/Redis Implementation:**

```python
import redis
import psycopg2
import json
from typing import List, Set
import fnmatch

class CacheInvalidationManager:
    def __init__(self, redis_client: redis.Redis, db_connection):
        self.redis = redis_client
        self.db = db_connection

    def process_invalidation_queue(self):
        """Process pending cache invalidations from PostgreSQL queue"""
        with self.db.cursor() as cursor:
            # Get unprocessed invalidation requests
            cursor.execute("""
                SELECT id, tags FROM cache_invalidation_queue
                WHERE processed = FALSE
                ORDER BY created_at ASC
                LIMIT 100
            """)

            for record_id, tags in cursor.fetchall():
                self.invalidate_by_tags(tags)

                # Mark as processed
                cursor.execute(
                    "UPDATE cache_invalidation_queue SET processed = TRUE WHERE id = %s",
                    (record_id,)
                )

            self.db.commit()

    def invalidate_by_tags(self, tags: List[str]):
        """Invalidate all cache entries matching the given tags"""
        pipe = self.redis.pipeline()

        for tag in tags:
            if '*' in tag:
                # Handle wildcard tags
                cache_keys = self._get_keys_by_wildcard_tag(tag)
            else:
                # Get exact tag matches
                cache_keys = self._get_keys_by_tag(tag)

            # Delete cache entries
            if cache_keys:
                pipe.delete(*cache_keys)
                print(f"Invalidating {len(cache_keys)} entries for tag: {tag}")

        pipe.execute()

    def _get_keys_by_tag(self, tag: str) -> List[str]:
        """Get all cache keys associated with a specific tag"""
        # Redis SET stores all cache keys for each tag
        tag_key = f"tag:{tag}"
        return list(self.redis.smembers(tag_key))

    def _get_keys_by_wildcard_tag(self, tag_pattern: str) -> List[str]:
        """Handle wildcard tag patterns like 'search:events:*'"""
        pattern = tag_pattern.replace('*', '*')
        tag_keys = self.redis.keys(f"tag:{pattern}")

        all_cache_keys = set()
        for tag_key in tag_keys:
            cache_keys = self.redis.smembers(tag_key)
            all_cache_keys.update(cache_keys)

        return list(all_cache_keys)

# Cache storage with tag management
class TaggedCacheManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def set_with_tags(self, key: str, value: str, tags: List[str], ttl: int = 3600):
        """Store cache entry with associated tags"""
        pipe = self.redis.pipeline()

        # Store the actual cache entry
        pipe.setex(key, ttl, value)

        # Associate this cache key with each tag
        for tag in tags:
            tag_key = f"tag:{tag}"
            pipe.sadd(tag_key, key)
            pipe.expire(tag_key, ttl * 2)  # Tag TTL longer than cache TTL

        pipe.execute()
        print(f"Cached {key} with tags: {tags}")

    def get(self, key: str) -> str:
        """Get cache entry"""
        return self.redis.get(key)

# Example usage in Ticketmaster application
class TicketmasterCacheService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_manager = TaggedCacheManager(self.redis)

    def cache_event_details(self, event_id: int, event_data: dict):
        """Cache event details with appropriate tags"""
        cache_key = f"event:details:{event_id}"
        tags = [
            f"event:{event_id}",
            f"venue:{event_data['venue_id']}",
            f"performer:{event_data['performer_id']}",
            f"category:{event_data['category_id']}"
        ]

        self.cache_manager.set_with_tags(
            cache_key,
            json.dumps(event_data),
            tags,
            ttl=3600  # 1 hour
        )

    def cache_search_results(self, search_params: dict, results: list):
        """Cache search results with relevant tags"""
        # Create deterministic cache key from search parameters
        search_hash = hash(frozenset(search_params.items()))
        cache_key = f"search:events:{search_hash}"

        tags = ["search:events:all"]

        # Add location-based tags if present
        if 'city' in search_params:
            tags.append(f"location:{search_params['city']}")

        # Add category tags if present
        if 'category' in search_params:
            tags.append(f"category:{search_params['category']}")

        self.cache_manager.set_with_tags(
            cache_key,
            json.dumps(results),
            tags,
            ttl=1800  # 30 minutes for search results
        )
```

#### 3. Real-time Invalidation with Redis Pub/Sub

```python
class RealtimeCacheInvalidation:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.pubsub = redis_client.pubsub()

    def setup_listeners(self):
        """Setup Redis pub/sub for real-time invalidation"""
        self.pubsub.subscribe('cache:invalidate')

        for message in self.pubsub.listen():
            if message['type'] == 'message':
                invalidation_data = json.loads(message['data'])
                self.handle_invalidation(invalidation_data)

    def handle_invalidation(self, data: dict):
        """Handle real-time cache invalidation"""
        tags = data.get('tags', [])
        reason = data.get('reason', 'unknown')

        print(f"Real-time invalidation: {reason}")
        invalidation_manager = CacheInvalidationManager(self.redis, None)
        invalidation_manager.invalidate_by_tags(tags)

    def publish_invalidation(self, tags: List[str], reason: str):
        """Publish invalidation event"""
        message = {
            'tags': tags,
            'reason': reason,
            'timestamp': time.time()
        }
        self.redis.publish('cache:invalidate', json.dumps(message))
```

### Specific Ticketmaster Use Cases

#### 1. Event Update Scenario

When an event's price changes:

```python
def update_event_price(event_id: int, new_price: float):
    # Update database
    cursor.execute(
        "UPDATE events SET price = %s WHERE id = %s",
        (new_price, event_id)
    )

    # PostgreSQL trigger automatically adds to invalidation queue:
    # - event:{event_id}
    # - search:events:*
    # - Any other related tags

    # Optional: Immediate invalidation for critical updates
    realtime_invalidator.publish_invalidation(
        tags=[f"event:{event_id}"],
        reason="price_update"
    )
```

#### 2. Venue Capacity Change

When a venue's capacity changes:

```python
def update_venue_capacity(venue_id: int, new_capacity: int):
    # This affects all events at this venue
    cursor.execute(
        "UPDATE venues SET capacity = %s WHERE id = %s",
        (new_capacity, venue_id)
    )

    # Trigger invalidates:
    # - venue:{venue_id}
    # - All events at this venue
    # - Related search results
```

#### 3. Search Result Invalidation

Complex search results are invalidated efficiently:

```python
# Search: "Rock concerts in Seattle"
search_params = {
    'genre': 'rock',
    'city': 'seattle',
    'date_range': '2024-01-01:2024-12-31'
}

# Cache tags applied:
tags = [
    'search:events:all',
    'location:seattle',
    'category:rock'
]

# When ANY rock event in Seattle changes, this cache is invalidated
```

### Monitoring and Observability

```python
class CacheInvalidationMetrics:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def track_invalidation(self, tags: List[str], keys_invalidated: int):
        """Track invalidation metrics"""
        pipe = self.redis.pipeline()

        for tag in tags:
            # Count invalidations per tag
            pipe.hincrby('metrics:invalidations:tags', tag, 1)
            pipe.hincrby('metrics:invalidations:keys', tag, keys_invalidated)

        # Overall metrics
        pipe.incr('metrics:invalidations:total')
        pipe.incr('metrics:keys_invalidated:total', keys_invalidated)

        pipe.execute()

    def get_invalidation_stats(self) -> dict:
        """Get invalidation statistics"""
        return {
            'total_invalidations': self.redis.get('metrics:invalidations:total'),
            'tag_breakdown': self.redis.hgetall('metrics:invalidations:tags'),
            'keys_per_tag': self.redis.hgetall('metrics:invalidations:keys')
        }
```

### Benefits and Trade-offs

**Benefits:**

- **Granular Control**: Invalidate exactly what needs to be invalidated
- **Efficiency**: Batch invalidation of related cache entries
- **Consistency**: Immediate invalidation prevents stale data
- **Scalability**: Asynchronous processing handles high-volume changes

**Trade-offs:**

- **Complexity**: More complex than TTL-based invalidation
- **Storage Overhead**: Additional metadata for tag management
- **Processing Overhead**: Tag resolution and wildcard matching
- **Debugging**: More complex cache behavior to troubleshoot

**Best Practices:**

1. Use specific tags for critical data (event details, pricing)
2. Use wildcard tags sparingly for broad invalidation
3. Monitor invalidation patterns to optimize tag structure
4. Implement circuit breakers for invalidation failures
5. Log invalidation events for debugging and analysis

This cache invalidation strategy ensures that Ticketmaster users always see current event information while maintaining high performance through intelligent caching.

## Optimistic Concurrency Control for Ticket Reservation

### The Concurrent Seat Selection Challenge

In a Ticketmaster-like system, one of the most critical concurrency challenges occurs when multiple users simultaneously attempt to reserve the same seats. Consider this scenario:

- User A and User B both view the seatmap for a popular concert
- Both users simultaneously click on seat "A-15" at exactly the same time
- Both see the seat as "available" and proceed to checkout
- Only one user should successfully reserve the seat

This is where PostgreSQL's **Multi-Version Concurrency Control (MVCC)** and **Optimistic Concurrency Control (OCC)** patterns become essential.

### PostgreSQL MVCC Fundamentals

According to "Designing Data Intensive Applications" by Martin Kleppmann, PostgreSQL implements **snapshot isolation** using MVCC, which provides several key guarantees:

1. **Non-blocking Reads**: Read operations never block write operations
2. **Consistent Snapshots**: Each transaction sees a consistent snapshot of the database
3. **Write Conflict Detection**: Conflicts are detected at commit time, not during execution

#### Database Schema for Ticket Reservation

```sql
CREATE TABLE tickets (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    seat_section VARCHAR(10) NOT NULL,
    seat_row VARCHAR(5) NOT NULL,
    seat_number VARCHAR(5) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available', -- available, reserved, sold
    reserved_by_user_id BIGINT NULL,
    last_reserved_at TIMESTAMP NULL,
    reservation_expires_at TIMESTAMP NULL,
    version INTEGER NOT NULL DEFAULT 1, -- For optimistic locking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(event_id, seat_section, seat_row, seat_number)
);

-- Index for fast seat availability queries
CREATE INDEX idx_tickets_availability ON tickets (event_id, status)
WHERE status IN ('available', 'reserved');

-- Index for reservation cleanup
CREATE INDEX idx_tickets_expired_reservations ON tickets (reservation_expires_at)
WHERE status = 'reserved' AND reservation_expires_at IS NOT NULL;
```

### Optimistic Concurrency Control Implementation

#### Pattern 1: Version-Based OCC

```python
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, List
import time

class TicketReservationService:
    def __init__(self, db_connection):
        self.db = db_connection

    def reserve_seats(self, user_id: int, event_id: int, seat_ids: List[int]) -> dict:
        """
        Reserve multiple seats using optimistic concurrency control.
        Returns success status and details about the reservation attempt.
        """
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                with self.db.cursor() as cursor:
                    # Start transaction with SERIALIZABLE isolation level
                    # This provides the strongest consistency guarantees
                    cursor.execute("BEGIN ISOLATION LEVEL SERIALIZABLE")

                    result = self._attempt_reservation(cursor, user_id, event_id, seat_ids)

                    if result['success']:
                        cursor.execute("COMMIT")
                        return result
                    else:
                        cursor.execute("ROLLBACK")
                        return result

            except psycopg2.errors.SerializationFailure as e:
                # SERIALIZABLE isolation detected a conflict
                retry_count += 1
                if retry_count >= max_retries:
                    return {
                        'success': False,
                        'error': 'high_contention',
                        'message': 'Too many users trying to reserve these seats. Please try again.',
                        'retry_after': 1000  # milliseconds
                    }

                # Exponential backoff with jitter
                sleep_time = (0.1 * (2 ** retry_count)) + (0.05 * time.time() % 1)
                time.sleep(sleep_time)

            except Exception as e:
                cursor.execute("ROLLBACK")
                return {
                    'success': False,
                    'error': 'system_error',
                    'message': str(e)
                }

    def _attempt_reservation(self, cursor, user_id: int, event_id: int, seat_ids: List[int]) -> dict:
        """
        Attempt to reserve seats within a transaction.
        Uses version-based optimistic locking.
        """
        reservation_duration = timedelta(minutes=10)  # 10-minute reservation window
        expires_at = datetime.now() + reservation_duration

        # Step 1: Read current state of all requested seats
        cursor.execute("""
            SELECT id, seat_section, seat_row, seat_number, status,
                   reserved_by_user_id, version, reservation_expires_at
            FROM tickets
            WHERE id = ANY(%s) AND event_id = %s
            FOR UPDATE  -- Lock the rows for update
        """, (seat_ids, event_id))

        seats = cursor.fetchall()

        if len(seats) != len(seat_ids):
            return {
                'success': False,
                'error': 'seats_not_found',
                'message': 'Some requested seats do not exist'
            }

        # Step 2: Validate seat availability
        unavailable_seats = []
        seats_to_reserve = []

        current_time = datetime.now()

        for seat in seats:
            seat_id, section, row, number, status, reserved_by, version, expires_at = seat

            # Check if seat is available or has expired reservation
            if status == 'available':
                seats_to_reserve.append((seat_id, version))
            elif status == 'reserved':
                if expires_at and expires_at < current_time:
                    # Expired reservation - can be re-reserved
                    seats_to_reserve.append((seat_id, version))
                elif reserved_by == user_id:
                    # User already has this seat reserved - extend reservation
                    seats_to_reserve.append((seat_id, version))
                else:
                    # Seat is reserved by another user
                    unavailable_seats.append(f"{section}-{row}-{number}")
            else:
                # Seat is sold
                unavailable_seats.append(f"{section}-{row}-{number}")

        if unavailable_seats:
            return {
                'success': False,
                'error': 'seats_unavailable',
                'message': f'Seats no longer available: {", ".join(unavailable_seats)}',
                'unavailable_seats': unavailable_seats
            }

        # Step 3: Reserve all seats atomically using version-based OCC
        reserved_seats = []

        for seat_id, current_version in seats_to_reserve:
            cursor.execute("""
                UPDATE tickets
                SET status = 'reserved',
                    reserved_by_user_id = %s,
                    last_reserved_at = %s,
                    reservation_expires_at = %s,
                    version = version + 1,
                    updated_at = %s
                WHERE id = %s
                  AND version = %s  -- Optimistic lock check
            """, (user_id, current_time, expires_at, current_time, seat_id, current_version))

            if cursor.rowcount == 0:
                # Version mismatch - another transaction modified this seat
                # This will cause the transaction to rollback
                return {
                    'success': False,
                    'error': 'version_conflict',
                    'message': 'Seats were modified by another user. Please try again.'
                }

            reserved_seats.append(seat_id)

        return {
            'success': True,
            'reserved_seats': reserved_seats,
            'reservation_expires_at': expires_at.isoformat(),
            'message': f'Successfully reserved {len(reserved_seats)} seats'
        }
```

### How MVCC Resolves Concurrent Reservations

Let's trace through what happens when User A and User B simultaneously attempt to reserve the same seat:

#### Timeline of Concurrent Transactions

```
Time 1: User A starts transaction (sees seat as available, version=1)
Time 1: User B starts transaction (sees seat as available, version=1)

Time 2: User A reads seat A-15: status='available', version=1
Time 2: User B reads seat A-15: status='available', version=1

Time 3: User A attempts UPDATE with WHERE version=1
Time 3: User B attempts UPDATE with WHERE version=1

Time 4: User A's UPDATE succeeds (version becomes 2)
Time 4: User B's UPDATE fails (version is now 2, but B expects 1)

Time 5: User A commits successfully
Time 5: User B's transaction fails due to version mismatch
```

#### PostgreSQL MVCC Behavior

1. **Snapshot Isolation**: Both users see a consistent snapshot of the database at transaction start
2. **Non-blocking Reads**: Both can read the seat status simultaneously
3. **First-Writer-Wins**: The first user to commit their UPDATE succeeds
4. **Version Conflict Detection**: The second user's transaction fails due to version mismatch

### Advanced Patterns: Preventing Write Skew

According to DDIA, **write skew** can occur in snapshot isolation when transactions read overlapping data and make non-overlapping writes. In ticket reservation, this might happen with seat group bookings:

```python
def reserve_adjacent_seats(self, user_id: int, event_id: int, section: str, row: str, count: int):
    """
    Reserve a group of adjacent seats, preventing write skew issues.
    """
    with self.db.cursor() as cursor:
        cursor.execute("BEGIN ISOLATION LEVEL SERIALIZABLE")

        # Use SERIALIZABLE isolation to prevent write skew
        # This is stronger than snapshot isolation and prevents phantom reads

        cursor.execute("""
            SELECT id, seat_number, status
            FROM tickets
            WHERE event_id = %s AND seat_section = %s AND seat_row = %s
            ORDER BY seat_number::INTEGER
            FOR UPDATE  -- Explicit locking to prevent write skew
        """, (event_id, section, row))

        seats = cursor.fetchall()

        # Find adjacent available seats
        available_groups = self._find_adjacent_seats(seats, count)

        if not available_groups:
            cursor.execute("ROLLBACK")
            return {'success': False, 'error': 'no_adjacent_seats'}

        # Reserve the first available group
        seat_ids = available_groups[0]
        return self._attempt_reservation(cursor, user_id, event_id, seat_ids)
```

### Reservation Cleanup and Timeout Handling

```python
class ReservationCleanupService:
    def __init__(self, db_connection):
        self.db = db_connection

    def cleanup_expired_reservations(self):
        """
        Background job to clean up expired reservations.
        Runs every minute to release expired seats.
        """
        with self.db.cursor() as cursor:
            cursor.execute("""
                UPDATE tickets
                SET status = 'available',
                    reserved_by_user_id = NULL,
                    last_reserved_at = NULL,
                    reservation_expires_at = NULL,
                    version = version + 1,
                    updated_at = NOW()
                WHERE status = 'reserved'
                  AND reservation_expires_at < NOW()
            """)

            released_count = cursor.rowcount
            self.db.commit()

            if released_count > 0:
                print(f"Released {released_count} expired seat reservations")

            return released_count

    def extend_reservation(self, user_id: int, seat_ids: List[int],
                          additional_minutes: int = 5) -> dict:
        """
        Extend reservation for a user who is actively in checkout process.
        """
        with self.db.cursor() as cursor:
            new_expiry = datetime.now() + timedelta(minutes=additional_minutes)

            cursor.execute("""
                UPDATE tickets
                SET reservation_expires_at = %s,
                    version = version + 1,
                    updated_at = NOW()
                WHERE id = ANY(%s)
                  AND reserved_by_user_id = %s
                  AND status = 'reserved'
                  AND reservation_expires_at > NOW()  -- Still valid
            """, (new_expiry, seat_ids, user_id))

            extended_count = cursor.rowcount
            self.db.commit()

            return {
                'success': extended_count > 0,
                'extended_seats': extended_count,
                'new_expiry': new_expiry.isoformat()
            }
```

### Performance Considerations and Monitoring

#### Contention Metrics

```python
class ReservationMetrics:
    def __init__(self, db_connection):
        self.db = db_connection

    def track_reservation_attempt(self, event_id: int, seat_count: int,
                                success: bool, retry_count: int, duration_ms: int):
        """Track reservation attempt metrics"""
        with self.db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO reservation_metrics
                (event_id, seat_count, success, retry_count, duration_ms, timestamp)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (event_id, seat_count, success, retry_count, duration_ms))
            self.db.commit()

    def get_contention_stats(self, event_id: int) -> dict:
        """Get contention statistics for an event"""
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT
                    AVG(retry_count) as avg_retries,
                    MAX(retry_count) as max_retries,
                    COUNT(*) FILTER (WHERE retry_count > 0) as conflicted_attempts,
                    COUNT(*) as total_attempts,
                    AVG(duration_ms) as avg_duration_ms
                FROM reservation_metrics
                WHERE event_id = %s
                  AND timestamp > NOW() - INTERVAL '1 hour'
            """, (event_id,))

            return dict(zip(
                ['avg_retries', 'max_retries', 'conflicted_attempts',
                 'total_attempts', 'avg_duration_ms'],
                cursor.fetchone() or [0, 0, 0, 0, 0]
            ))
```

### Key Takeaways: MVCC and OCC in Practice

1. **Isolation Level Choice**:

   - Use `SERIALIZABLE` for critical operations to prevent write skew
   - Use `REPEATABLE READ` for better performance when write skew isn't a concern

2. **Optimistic vs Pessimistic Locking**:

   - OCC (version-based) works well for low-contention scenarios
   - Use `FOR UPDATE` (pessimistic) for high-contention situations

3. **Conflict Resolution Strategy**:

   - "First-commit-wins" is implemented automatically by PostgreSQL's MVCC
   - Application-level retry logic handles serialization failures

4. **Performance Trade-offs**:

   - Higher isolation levels provide stronger consistency but may increase conflicts
   - Version-based OCC adds minimal overhead but requires application logic

5. **Monitoring and Alerting**:
   - Track retry rates to identify high-contention events
   - Monitor reservation expiry cleanup effectiveness
   - Alert on excessive serialization failures

This approach ensures that ticket reservations are handled consistently even under high concurrency, leveraging PostgreSQL's MVCC capabilities while providing a fair "first-come, first-served" experience for users.
