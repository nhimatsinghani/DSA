# Virtual Waiting Queue: Deep Dive Implementation Analysis

## Overview

A virtual waiting queue is a critical component for handling traffic spikes during high-demand ticket releases. When thousands of users simultaneously attempt to purchase tickets for popular events, the system needs to:

1. **Prevent system overload** - Limit concurrent users accessing the booking flow
2. **Maintain fairness** - First-come, first-served ordering
3. **Provide transparency** - Real-time position and wait time estimates
4. **Ensure reliability** - Handle failures gracefully without losing user positions

## Core Requirements

### Functional Requirements

- **Queue Management**: Add users to queue, process in batches, remove completed users
- **Position Tracking**: Real-time queue position for each user
- **Wait Time Estimation**: Dynamic calculation based on queue size and processing rate
- **Batch Processing**: Release users in configurable batches (e.g., 100 users)
- **Session Management**: Handle user disconnections and reconnections
- **Event-Specific**: Activate only for designated high-demand events

### Non-Functional Requirements

- **Scalability**: Handle 100k+ concurrent users in queue
- **Low Latency**: Position updates < 1 second
- **High Availability**: 99.9% uptime during critical events
- **Fairness**: Strict FIFO ordering with minimal position jumping
- **Resilience**: Survive node failures without losing queue state

---

## Implementation Approaches

## 1. Redis-Based In-Memory Queue

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│Load Balancer│───▶│Queue Service│
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
                                      ┌─────────────┐
                                      │   Redis     │
                                      │  Cluster    │
                                      └─────────────┘
```

### Implementation Details

**Core Data Structures:**

```redis
# Main queue (sorted set for FIFO with timestamps)
ZADD event:123:queue <timestamp> <user_id>

# User metadata
HSET event:123:users <user_id> '{"joined_at": 1234567890, "position": 1000}'

# Active users currently in booking flow
SADD event:123:active <user_id>

# Processing counters
SET event:123:processed_count 0
SET event:123:batch_size 100
```

**Queue Operations:**

```python
class RedisWaitingQueue:
    def __init__(self, redis_client, event_id):
        self.redis = redis_client
        self.event_id = event_id
        self.queue_key = f"event:{event_id}:queue"
        self.users_key = f"event:{event_id}:users"
        self.active_key = f"event:{event_id}:active"

    def join_queue(self, user_id):
        timestamp = time.time()
        pipeline = self.redis.pipeline()
        pipeline.zadd(self.queue_key, {user_id: timestamp})
        pipeline.hset(self.users_key, user_id, json.dumps({
            "joined_at": timestamp,
            "status": "waiting"
        }))
        pipeline.execute()
        return self.get_position(user_id)

    def get_position(self, user_id):
        rank = self.redis.zrank(self.queue_key, user_id)
        return rank + 1 if rank is not None else None

    def process_batch(self, batch_size=100):
        # Get next batch of users
        users = self.redis.zrange(self.queue_key, 0, batch_size-1)
        if not users:
            return []

        pipeline = self.redis.pipeline()
        # Remove from queue
        pipeline.zrem(self.queue_key, *users)
        # Add to active set
        pipeline.sadd(self.active_key, *users)
        # Update user status
        for user in users:
            pipeline.hset(self.users_key, user, json.dumps({
                "status": "active",
                "activated_at": time.time()
            }))
        pipeline.execute()
        return users
```

### Pros

✅ **Ultra-low latency** - Sub-millisecond operations
✅ **Simple implementation** - Redis operations are straightforward
✅ **Real-time updates** - Instant position calculations
✅ **Atomic operations** - Redis ensures consistency
✅ **Memory efficiency** - Compact data structures

### Cons

❌ **Memory limitations** - All data must fit in RAM
❌ **Persistence concerns** - Risk of data loss on crashes
❌ **Single point of failure** - Without proper clustering
❌ **Limited durability** - Redis persistence has trade-offs
❌ **Network partitions** - Can lead to split-brain scenarios

### Best For

- Events with < 500K concurrent users
- When ultra-low latency is critical
- Systems with strong Redis clustering expertise

---

## 2. Database-Based Persistent Queue

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│Queue Service│───▶│  Database   │
└─────────────┘    └─────────────┘    │  (Primary)  │
                           │           └─────────────┘
                           │                   │
                           ▼                   │ Replication
                   ┌─────────────┐             ▼
                   │   Cache     │    ┌─────────────┐
                   │  (Redis)    │    │  Database   │
                   └─────────────┘    │ (Read Only) │
                                      └─────────────┘
```

### Schema Design

```sql
CREATE TABLE waiting_queue (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
    position BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'waiting',
    activated_at TIMESTAMP,

    INDEX idx_event_position (event_id, position),
    INDEX idx_user_event (user_id, event_id),
    UNIQUE KEY uk_user_event (user_id, event_id)
);

CREATE TABLE queue_metadata (
    event_id BIGINT PRIMARY KEY,
    total_users BIGINT NOT NULL DEFAULT 0,
    processed_users BIGINT NOT NULL DEFAULT 0,
    batch_size INT NOT NULL DEFAULT 100,
    processing_rate DECIMAL(10,2), -- users per minute
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Implementation

```python
class DatabaseWaitingQueue:
    def __init__(self, db_connection):
        self.db = db_connection

    def join_queue(self, user_id, event_id):
        with self.db.transaction():
            # Get next position
            result = self.db.execute("""
                SELECT COALESCE(MAX(position), 0) + 1 as next_position
                FROM waiting_queue
                WHERE event_id = %s
            """, [event_id])
            position = result.fetchone()[0]

            # Insert user
            self.db.execute("""
                INSERT INTO waiting_queue
                (user_id, event_id, position)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, event_id)
                DO NOTHING
            """, [user_id, event_id, position])

            # Update metadata
            self.db.execute("""
                INSERT INTO queue_metadata (event_id, total_users)
                VALUES (%s, 1)
                ON CONFLICT (event_id)
                DO UPDATE SET total_users = total_users + 1
            """, [event_id])

            return position

    def process_batch(self, event_id, batch_size):
        with self.db.transaction():
            # Get next batch
            users = self.db.execute("""
                SELECT user_id, position
                FROM waiting_queue
                WHERE event_id = %s AND status = 'waiting'
                ORDER BY position
                LIMIT %s
                FOR UPDATE SKIP LOCKED
            """, [event_id, batch_size]).fetchall()

            if not users:
                return []

            user_ids = [u[0] for u in users]

            # Update status
            self.db.execute("""
                UPDATE waiting_queue
                SET status = 'active', activated_at = NOW()
                WHERE user_id = ANY(%s) AND event_id = %s
            """, [user_ids, event_id])

            return user_ids
```

### Advanced Optimizations

**Read Replicas for Position Queries:**

```python
def get_position_optimized(self, user_id, event_id):
    # Use read replica for position queries
    position = self.read_replica.execute("""
        SELECT position,
               (SELECT COUNT(*)
                FROM waiting_queue w2
                WHERE w2.event_id = w1.event_id
                  AND w2.position < w1.position
                  AND w2.status = 'waiting') as queue_position
        FROM waiting_queue w1
        WHERE user_id = %s AND event_id = %s
    """, [user_id, event_id]).fetchone()

    return position[1] + 1 if position else None
```

**Materialized Queue Positions:**

```sql
-- Periodically refresh queue positions
REFRESH MATERIALIZED VIEW CONCURRENTLY queue_positions_mv;

CREATE MATERIALIZED VIEW queue_positions_mv AS
SELECT
    user_id,
    event_id,
    ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY position) as current_position,
    position as original_position
FROM waiting_queue
WHERE status = 'waiting';
```

### Pros

✅ **Strong consistency** - ACID transactions guarantee correctness
✅ **Durability** - Data survives crashes and failures
✅ **Complex queries** - Rich SQL capabilities for analytics
✅ **Mature tooling** - Extensive monitoring and backup solutions
✅ **Regulatory compliance** - Easier auditing and data governance

### Cons

❌ **Higher latency** - Disk I/O and network overhead
❌ **Scalability limits** - Write throughput bottlenecks
❌ **Hot spots** - Sequential IDs can create contention
❌ **Complex scaling** - Sharding queue data is challenging
❌ **Resource intensive** - Higher CPU and memory usage

### Best For

- Events requiring strong consistency guarantees
- Systems with existing database infrastructure
- Scenarios where auditability is crucial

---

## 3. Message Queue-Based System (Amazon SQS/Kafka)

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│Queue Service│───▶│   Message   │
└─────────────┘    └─────────────┘    │   Queue     │
                                      │ (SQS/Kafka) │
                                      └─────────────┘
                                              │
                                              ▼
                                      ┌─────────────┐
                                      │  Position   │
                                      │   Service   │
                                      │  (Redis)    │
                                      └─────────────┘
```

### Amazon SQS Implementation

```python
import boto3
import time
from dataclasses import dataclass

@dataclass
class QueuePosition:
    user_id: str
    position: int
    estimated_wait_minutes: int

class SQSWaitingQueue:
    def __init__(self, event_id):
        self.sqs = boto3.client('sqs')
        self.redis = redis.Redis()
        self.queue_url = f"https://sqs.region.amazonaws.com/account/event-{event_id}-queue"
        self.position_key = f"event:{event_id}:positions"

    def join_queue(self, user_id):
        # Add to SQS queue
        message_body = json.dumps({
            "user_id": user_id,
            "joined_at": time.time(),
            "event_id": self.event_id
        })

        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message_body,
            MessageAttributes={
                'user_id': {'StringValue': user_id, 'DataType': 'String'}
            }
        )

        # Track position in Redis
        position = self.redis.incr(f"{self.position_key}:counter")
        self.redis.hset(self.position_key, user_id, position)

        return position

    def process_batch(self, batch_size=100):
        # Receive messages from SQS
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=min(batch_size, 10),  # SQS limit
            WaitTimeSeconds=20,  # Long polling
            MessageAttributeNames=['All']
        )

        messages = response.get('Messages', [])
        processed_users = []

        for message in messages:
            user_data = json.loads(message['Body'])
            user_id = user_data['user_id']

            # Process user (send to booking flow)
            self.activate_user_session(user_id)
            processed_users.append(user_id)

            # Delete from queue
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )

            # Remove from position tracking
            self.redis.hdel(self.position_key, user_id)

        return processed_users

    def get_position(self, user_id):
        position = self.redis.hget(self.position_key, user_id)
        if not position:
            return None

        # Get queue length for wait estimation
        queue_attributes = self.sqs.get_queue_attributes(
            QueueUrl=self.queue_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )

        queue_length = int(queue_attributes['Attributes']['ApproximateNumberOfMessages'])
        estimated_wait = (int(position) * 2) // 100  # 2 minutes per 100 users

        return QueuePosition(
            user_id=user_id,
            position=int(position),
            estimated_wait_minutes=estimated_wait
        )
```

### Kafka Implementation (for higher throughput)

```python
from kafka import KafkaProducer, KafkaConsumer
import json

class KafkaWaitingQueue:
    def __init__(self, event_id):
        self.event_id = event_id
        self.topic = f"waiting-queue-{event_id}"
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8')
        )

    def join_queue(self, user_id):
        message = {
            "user_id": user_id,
            "joined_at": time.time(),
            "event_id": self.event_id
        }

        # Send to Kafka (partition by user_id for ordering)
        future = self.producer.send(
            self.topic,
            key=user_id,
            value=message
        )

        # Get offset as position indicator
        record_metadata = future.get(timeout=10)
        return record_metadata.offset

    def process_batch_consumer(self, batch_size=100):
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=False,
            max_poll_records=batch_size
        )

        messages = consumer.poll(timeout_ms=1000)
        processed_users = []

        for topic_partition, msgs in messages.items():
            for message in msgs:
                user_data = message.value
                user_id = user_data['user_id']

                # Process user
                self.activate_user_session(user_id)
                processed_users.append(user_id)

            # Commit offsets
            consumer.commit()

        return processed_users
```

### Pros

✅ **Managed infrastructure** - Cloud providers handle scaling
✅ **High throughput** - Kafka can handle millions of messages/second
✅ **Reliability** - Built-in replication and durability
✅ **Dead letter queues** - Handle failed message processing
✅ **Monitoring** - Rich metrics and alerting capabilities

### Cons

❌ **Position ambiguity** - Queue position not immediately available
❌ **Complex setup** - Requires additional infrastructure
❌ **Message ordering** - Can be challenging in distributed scenarios
❌ **Cost** - Cloud messaging services can be expensive at scale
❌ **Latency overhead** - Network hops add delay

### Best For

- Very high throughput scenarios (1M+ users)
- Teams with strong messaging infrastructure expertise
- When you need guaranteed message delivery

---

## 4. Hybrid Token-Based System

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│ Token API   │───▶│Coordination │
└─────────────┘    └─────────────┘    │  Service    │
       │                               └─────────────┘
       │ JWT Token                             │
       │ (queue position)                      ▼
       ▼                               ┌─────────────┐
┌─────────────┐                       │   Redis     │
│   Browser   │                       │ (Global     │
│   Storage   │                       │  Counter)   │
└─────────────┘                       └─────────────┘
```

### Implementation

```python
import jwt
import time
from dataclasses import dataclass

@dataclass
class QueueToken:
    user_id: str
    event_id: str
    position: int
    issued_at: int
    expires_at: int

class TokenBasedQueue:
    def __init__(self, secret_key, event_id):
        self.secret_key = secret_key
        self.event_id = event_id
        self.redis = redis.Redis()
        self.position_counter_key = f"event:{event_id}:position_counter"
        self.active_positions_key = f"event:{event_id}:active_positions"

    def join_queue(self, user_id):
        # Get next position atomically
        position = self.redis.incr(self.position_counter_key)

        # Create JWT token
        now = int(time.time())
        token_data = {
            "user_id": user_id,
            "event_id": self.event_id,
            "position": position,
            "iat": now,
            "exp": now + (24 * 3600),  # 24 hours
            "type": "queue_token"
        }

        token = jwt.encode(token_data, self.secret_key, algorithm='HS256')
        return token, position

    def validate_token_and_check_turn(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])

            # Check if it's this user's turn
            current_active_position = self.redis.get(self.active_positions_key)
            current_active_position = int(current_active_position) if current_active_position else 0

            user_position = payload['position']

            if user_position <= current_active_position:
                return {
                    "status": "active",
                    "user_id": payload['user_id'],
                    "position": user_position
                }
            else:
                return {
                    "status": "waiting",
                    "user_id": payload['user_id'],
                    "position": user_position,
                    "queue_ahead": user_position - current_active_position
                }

        except jwt.ExpiredSignatureError:
            return {"status": "expired"}
        except jwt.InvalidTokenError:
            return {"status": "invalid"}

    def process_next_batch(self, batch_size=100):
        # Update the active position pointer
        new_active_position = self.redis.incrby(
            self.active_positions_key,
            batch_size
        )

        return {
            "processed_up_to_position": new_active_position,
            "batch_size": batch_size
        }
```

### Advanced Token Features

```python
class AdvancedTokenQueue:
    def create_priority_token(self, user_id, priority_level=0):
        """Create tokens with priority levels for VIP users"""
        base_position = self.redis.incr(self.position_counter_key)

        # Adjust position based on priority
        adjusted_position = base_position - (priority_level * 1000)

        token_data = {
            "user_id": user_id,
            "event_id": self.event_id,
            "position": max(1, adjusted_position),
            "priority": priority_level,
            "iat": int(time.time()),
            "exp": int(time.time()) + (24 * 3600)
        }

        return jwt.encode(token_data, self.secret_key, algorithm='HS256')

    def refresh_token_position(self, token):
        """Allow position updates for long queues"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])

            # Create new token with updated timestamp
            new_payload = payload.copy()
            new_payload['iat'] = int(time.time())
            new_payload['exp'] = int(time.time()) + (24 * 3600)

            return jwt.encode(new_payload, self.secret_key, algorithm='HS256')

        except jwt.InvalidTokenError:
            return None
```

### Pros

✅ **Stateless design** - No server-side queue state to manage
✅ **Horizontal scaling** - Easy to add more API servers
✅ **Client-side persistence** - Users can close/reopen browser
✅ **Low infrastructure cost** - Minimal server resources needed
✅ **Simple failover** - No queue state to replicate

### Cons

❌ **Security concerns** - Tokens can be manipulated if not properly secured
❌ **Limited real-time updates** - Requires polling for position updates
❌ **Coordination complexity** - Global counter becomes bottleneck
❌ **Clock synchronization** - Server time drift can cause issues
❌ **No natural ordering** - Race conditions in token generation

### Best For

- Systems requiring high availability with minimal state
- Mobile applications that need offline capability
- Cost-sensitive implementations

---

## 5. Sharded Queue System

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│Load Balancer│───▶│Shard Router │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
                        ▼                     ▼                     ▼
                ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
                │   Shard 1   │       │   Shard 2   │       │   Shard 3   │
                │   (Redis)   │       │   (Redis)   │       │   (Redis)   │
                └─────────────┘       └─────────────┘       └─────────────┘
                        │                     │                     │
                        ▼                     ▼                     ▼
                ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
                │ Queue Proc  │       │ Queue Proc  │       │ Queue Proc  │
                │  Service 1  │       │  Service 2  │       │  Service 3  │
                └─────────────┘       └─────────────┘       └─────────────┘
```

### Implementation

```python
import hashlib
import bisect

class ShardedWaitingQueue:
    def __init__(self, shards, event_id):
        self.shards = shards  # List of Redis connections
        self.event_id = event_id
        self.shard_count = len(shards)

        # Consistent hashing ring
        self.hash_ring = []
        for i, shard in enumerate(shards):
            for j in range(100):  # Virtual nodes for better distribution
                hash_key = f"shard_{i}_vnode_{j}"
                hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
                self.hash_ring.append((hash_value, i))

        self.hash_ring.sort()

    def get_shard_for_user(self, user_id):
        """Use consistent hashing to determine shard"""
        user_hash = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        idx = bisect.bisect_right(self.hash_ring, (user_hash, 0))
        if idx == len(self.hash_ring):
            idx = 0
        return self.hash_ring[idx][1]

    def join_queue(self, user_id):
        shard_idx = self.get_shard_for_user(user_id)
        shard = self.shards[shard_idx]

        # Get position within this shard
        local_position = shard.zcard(f"event:{self.event_id}:queue") + 1

        # Calculate global position
        global_position = self.calculate_global_position(shard_idx, local_position)

        # Add to shard queue
        shard.zadd(
            f"event:{self.event_id}:queue",
            {user_id: time.time()}
        )

        shard.hset(
            f"event:{self.event_id}:users",
            user_id,
            json.dumps({
                "shard": shard_idx,
                "local_position": local_position,
                "global_position": global_position,
                "joined_at": time.time()
            })
        )

        return global_position

    def calculate_global_position(self, target_shard_idx, local_position):
        """Calculate global position across all shards"""
        total_before = 0

        for i in range(target_shard_idx):
            shard_size = self.shards[i].zcard(f"event:{self.event_id}:queue")
            total_before += shard_size

        return total_before + local_position

    def process_batch_round_robin(self, batch_size=100):
        """Process users from all shards in round-robin fashion"""
        users_per_shard = batch_size // self.shard_count
        remainder = batch_size % self.shard_count

        processed_users = []

        for i, shard in enumerate(self.shards):
            shard_batch_size = users_per_shard
            if i < remainder:
                shard_batch_size += 1

            if shard_batch_size > 0:
                users = shard.zrange(
                    f"event:{self.event_id}:queue",
                    0, shard_batch_size - 1
                )

                if users:
                    # Remove from queue
                    shard.zrem(f"event:{self.event_id}:queue", *users)

                    # Add to active
                    shard.sadd(f"event:{self.event_id}:active", *users)

                    processed_users.extend(users)

        return processed_users
```

### Global Position Coordination

```python
class GlobalPositionTracker:
    def __init__(self, coordinator_redis):
        self.coordinator = coordinator_redis

    def update_shard_sizes(self, event_id, shard_sizes):
        """Update global view of shard sizes"""
        pipeline = self.coordinator.pipeline()
        for shard_idx, size in enumerate(shard_sizes):
            pipeline.hset(
                f"event:{event_id}:shard_sizes",
                shard_idx,
                size
            )
        pipeline.execute()

    def get_global_position(self, event_id, user_shard, local_position):
        """Calculate exact global position"""
        shard_sizes = self.coordinator.hgetall(f"event:{event_id}:shard_sizes")

        total_before = 0
        for i in range(user_shard):
            total_before += int(shard_sizes.get(str(i), 0))

        return total_before + local_position
```

### Pros

✅ **Horizontal scalability** - Linear scale with more shards
✅ **Isolation** - Shard failures don't affect entire queue
✅ **Performance** - Parallel processing across shards
✅ **Load distribution** - Even spread of users across shards
✅ **Cost efficiency** - Scale resources based on demand

### Cons

❌ **Complex coordination** - Global ordering requires careful design
❌ **Shard rebalancing** - Adding/removing shards is complex
❌ **Hot shards** - Some shards may become overloaded
❌ **Global position accuracy** - Requires coordination overhead
❌ **Operational complexity** - More moving parts to monitor

### Best For

- Very large scale events (1M+ concurrent users)
- Systems that can tolerate slight position inaccuracies
- Teams with strong distributed systems expertise

---

## Comparison Matrix

| Approach        | Scalability | Consistency | Latency    | Complexity | Cost       |
| --------------- | ----------- | ----------- | ---------- | ---------- | ---------- |
| Redis In-Memory | ⭐⭐⭐      | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐ | ⭐⭐       | ⭐⭐⭐     |
| Database-Based  | ⭐⭐        | ⭐⭐⭐⭐⭐  | ⭐⭐       | ⭐⭐⭐     | ⭐⭐       |
| Message Queue   | ⭐⭐⭐⭐    | ⭐⭐⭐      | ⭐⭐⭐     | ⭐⭐⭐⭐   | ⭐         |
| Token-Based     | ⭐⭐⭐⭐⭐  | ⭐⭐        | ⭐⭐⭐     | ⭐⭐       | ⭐⭐⭐⭐⭐ |
| Sharded System  | ⭐⭐⭐⭐⭐  | ⭐⭐⭐      | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | ⭐⭐       |

---

## User Experience Optimizations

### Real-Time Position Updates

```javascript
// WebSocket connection for live updates
const socket = new WebSocket(
  "wss://api.ticketmaster.com/queue/events/123/updates"
);

socket.onmessage = function (event) {
  const update = JSON.parse(event.data);
  updateQueuePosition(update.position, update.estimatedWait);
};

function updateQueuePosition(position, estimatedWait) {
  document.getElementById("queue-position").textContent = position;
  document.getElementById("estimated-wait").textContent = estimatedWait;

  // Update progress bar
  const progress = Math.max(0, 100 - (position / totalQueueSize) * 100);
  document.getElementById("progress-bar").style.width = progress + "%";
}
```

### Smart Wait Time Estimation

```python
class WaitTimeEstimator:
    def __init__(self, redis_client):
        self.redis = redis_client

    def estimate_wait_time(self, event_id, user_position):
        # Get historical processing rate
        processing_rates = self.redis.lrange(
            f"event:{event_id}:processing_rates",
            0, 10
        )

        if processing_rates:
            # Calculate average processing rate (users per minute)
            avg_rate = sum(float(rate) for rate in processing_rates) / len(processing_rates)
        else:
            # Default assumption: 100 users per 2 minutes
            avg_rate = 50.0

        # Calculate estimated wait time
        estimated_minutes = (user_position - 1) / avg_rate

        # Add buffer for conservative estimate
        buffered_estimate = estimated_minutes * 1.2

        return {
            "estimated_minutes": int(buffered_estimate),
            "estimated_seconds": int(buffered_estimate * 60),
            "confidence": min(len(processing_rates) / 10.0, 1.0)
        }

    def update_processing_rate(self, event_id, users_processed, time_taken):
        rate = users_processed / (time_taken / 60.0)  # users per minute

        # Store recent rates for moving average
        self.redis.lpush(f"event:{event_id}:processing_rates", rate)
        self.redis.ltrim(f"event:{event_id}:processing_rates", 0, 19)  # Keep last 20
```

### Progressive Loading and Caching

```python
class QueuePositionCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def cache_user_position(self, user_id, event_id, position_data, ttl=30):
        """Cache position data with short TTL for quick responses"""
        cache_key = f"position_cache:{event_id}:{user_id}"
        self.redis.setex(
            cache_key,
            ttl,
            json.dumps(position_data)
        )

    def get_cached_position(self, user_id, event_id):
        """Get cached position if available"""
        cache_key = f"position_cache:{event_id}:{user_id}"
        cached_data = self.redis.get(cache_key)

        if cached_data:
            return json.loads(cached_data)
        return None

    def bulk_cache_positions(self, event_id, position_updates):
        """Efficiently cache multiple position updates"""
        pipeline = self.redis.pipeline()

        for user_id, position_data in position_updates.items():
            cache_key = f"position_cache:{event_id}:{user_id}"
            pipeline.setex(
                cache_key,
                30,
                json.dumps(position_data)
            )

        pipeline.execute()
```

---

## Monitoring and Observability

### Key Metrics to Track

```python
class QueueMetrics:
    def __init__(self, metrics_client):
        self.metrics = metrics_client

    def track_queue_metrics(self, event_id):
        """Track comprehensive queue metrics"""

        # Queue size metrics
        total_waiting = self.get_total_waiting_users(event_id)
        total_active = self.get_total_active_users(event_id)

        self.metrics.gauge('queue.waiting_users', total_waiting, tags=[f'event:{event_id}'])
        self.metrics.gauge('queue.active_users', total_active, tags=[f'event:{event_id}'])

        # Processing rate metrics
        processing_rate = self.get_processing_rate(event_id)
        self.metrics.gauge('queue.processing_rate', processing_rate, tags=[f'event:{event_id}'])

        # Wait time metrics
        avg_wait_time = self.get_average_wait_time(event_id)
        self.metrics.gauge('queue.avg_wait_time', avg_wait_time, tags=[f'event:{event_id}'])

        # System health metrics
        queue_latency = self.measure_queue_operation_latency(event_id)
        self.metrics.histogram('queue.operation_latency', queue_latency, tags=[f'event:{event_id}'])
```

### Alerting Rules

```yaml
# Example Prometheus alerting rules
groups:
  - name: queue_alerts
    rules:
      - alert: QueueGrowthRate
        expr: increase(queue_waiting_users[5m]) > 1000
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Queue growing rapidly for event {{ $labels.event }}"

      - alert: QueueProcessingStalled
        expr: rate(queue_users_processed[5m]) < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Queue processing stalled for event {{ $labels.event }}"

      - alert: HighQueueLatency
        expr: queue_operation_latency_p95 > 1000
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High queue operation latency for event {{ $labels.event }}"
```

---

## Recommendations by Use Case

### Small-Medium Events (< 100K users)

**Recommended: Redis-Based In-Memory Queue**

- Simple to implement and operate
- Excellent performance characteristics
- Cost-effective for moderate scale
- Easy to debug and monitor

### Large Events (100K - 500K users)

**Recommended: Hybrid Redis + Database**

- Redis for real-time operations
- Database for persistence and analytics
- Best balance of performance and reliability
- Good operational complexity vs. benefit ratio

### Mega Events (500K+ users)

**Recommended: Sharded Redis + Message Queue**

- Horizontal scalability for extreme loads
- Message queue for reliable batch processing
- Multiple layers of redundancy
- Worth the operational complexity at this scale

### Cost-Sensitive Deployments

**Recommended: Token-Based System**

- Minimal infrastructure requirements
- Scales well with load balancers
- Good for startups or budget constraints
- Acceptable trade-offs for most use cases

### High-Compliance Environments

**Recommended: Database-Based with Audit Trail**

- Strong consistency guarantees
- Complete audit trail
- Regulatory compliance features
- Worth the performance trade-offs for compliance

---

## Implementation Timeline

### Phase 1: MVP (2-3 weeks)

1. **Basic Redis queue implementation**
2. **Simple position tracking**
3. **Basic wait time estimation**
4. **WebSocket updates**

### Phase 2: Production Ready (4-6 weeks)

1. **Add persistence layer**
2. **Implement batch processing**
3. **Add comprehensive monitoring**
4. **Load testing and optimization**

### Phase 3: Scale Optimization (6-8 weeks)

1. **Implement sharding if needed**
2. **Advanced caching strategies**
3. **Machine learning for wait time prediction**
4. **A/B testing framework for UX optimization**

This deep dive should give you a comprehensive understanding of the different approaches to implementing a virtual waiting queue. Each approach has its sweet spot depending on your specific requirements, scale, and operational constraints.
