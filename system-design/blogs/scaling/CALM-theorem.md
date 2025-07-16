# Keeping CALM: When Distributed Consistency is Easy

## The Core Idea: CALM Theorem

**CALM Theorem:** A program can be computed consistently in a distributed system without coordination if and only if it is **monotonic**.

## What is Monotonicity?

**Monotonic** means "only growing, never shrinking" - once something becomes true, it stays true. You can only add facts, never remove them.

**Simple analogy:** Think of a bucket that you can only pour water into, never take water out. The water level is monotonic - it only goes up (or stays the same).

## Examples of Monotonic vs Non-Monotonic Operations

### Monotonic Operations (No Coordination Needed)

**1. Set Union**

```python
# Node A has: {1, 2, 3}
# Node B has: {2, 3, 4}
# Union result: {1, 2, 3, 4}

# Even with network delays, eventual result is always {1, 2, 3, 4}
# Order of operations doesn't matter!
```

**2. Shopping Cart (Add-only)**

```python
# User adds items to cart from different devices
# Phone adds: [milk, bread]
# Laptop adds: [eggs, cheese]
# Final cart: [milk, bread, eggs, cheese]

# No coordination needed - just merge all additions
```

**3. Log Append**

```python
# Server A appends: "User login at 10:00"
# Server B appends: "User logout at 10:05"
# Both events are preserved in the log
```

### Non-Monotonic Operations (Coordination Required)

**1. Bank Account Balance**

```python
# Account starts with $100
# Transaction A: withdraw $60
# Transaction B: withdraw $60

# Without coordination:
# - Both see $100, both approve
# - Result: -$20 (overdraft!)

# Need coordination to prevent this
```

**2. Inventory Management**

```python
# Store has 5 items in stock
# Customer A wants to buy 3 items
# Customer B wants to buy 3 items

# Without coordination:
# - Both see 5 items available
# - Both purchases approved
# - Result: -1 items (impossible!)
```

**3. Unique Username Assignment**

```python
# User A tries to register "john123"
# User B tries to register "john123"

# Without coordination:
# - Both see username available
# - Both get approved
# - Result: duplicate usernames (violation!)
```

## Why Monotonic Operations Don't Need Coordination

Let's use a **distributed vote counting** example:

### Monotonic Version (Vote Counting)

```python
# Election with 3 voting locations
# Location A: 100 votes for Alice, 50 for Bob
# Location B: 80 votes for Alice, 70 for Bob
# Location C: 60 votes for Alice, 90 for Bob

# Each location can send results independently
# Order doesn't matter:
# - A+B first: Alice=180, Bob=120
# - Then +C: Alice=240, Bob=210

# OR
# - B+C first: Alice=140, Bob=160
# - Then +A: Alice=240, Bob=210

# Same final result regardless of order!
```

### Non-Monotonic Version (Max Votes per Person)

```python
# Rule: Each person can vote maximum once
# Person tries to vote at multiple locations

# Without coordination:
# Location A: "John hasn't voted yet, approve"
# Location B: "John hasn't voted yet, approve"
# Result: John voted twice (violation!)

# Need coordination to track who already voted
```

## The CALM Principle in Practice

### Example 1: Social Media "Likes" (Monotonic)

```python
# User can like a post multiple times from different devices
# Each "like" is just added to the set
# Duplicates are automatically handled by set semantics

# Timeline:
# Phone: adds like from user123
# Laptop: adds like from user123 (duplicate)
# Result: {user123} - still just one like

# No coordination needed!
```

### Example 2: Social Media "Unlike" (Non-Monotonic)

```python
# User wants to unlike a post
# This removes their like from the set
# Requires coordination to ensure consistency

# Without coordination:
# Phone: sees like exists, removes it
# Laptop: sees like exists, removes it
# Network delay causes both to process
# Result: user's like status is inconsistent
```

## Real-World Applications

### Systems That Embrace Monotonicity

**1. Git Version Control**

```python
# Git commits are monotonic
# You can only add commits, never remove them
# Merging is just combining commit histories
# No coordination needed for basic operations
```

**2. Apache Kafka**

```python
# Messages are append-only (monotonic)
# Producers can write independently
# Consumers see eventually consistent view
# No coordination needed between producers
```

**3. DNS Resolution**

```python
# DNS records are eventually consistent
# Adding records is monotonic
# Deleting records requires coordination/TTL
```

### Making Non-Monotonic Operations Monotonic

**Instead of:** Direct account balance updates

```python
# Non-monotonic: balance = balance - amount
account.balance -= 50  # Requires coordination
```

**Use:** Event sourcing (monotonic)

```python
# Monotonic: append transaction events
events.append(Withdrawal(amount=50, timestamp=now))
# Balance computed from event history
# Events are append-only = monotonic!
```

## Advanced Examples: Non-Monotonic Operations and Monotonic Alternatives

### 1. Seat Reservation System

**Non-Monotonic Approach:**

```python
# Traditional seat reservation (requires coordination)
class SeatReservation:
    def reserve_seat(self, flight_id, seat_number, user_id):
        seat = get_seat(flight_id, seat_number)
        if seat.status == "available":
            seat.status = "reserved"
            seat.user_id = user_id
            return "success"
        return "seat_taken"
```

**Problems:** Race conditions, requires locking, doesn't scale well.

**Monotonic Alternative - Event Sourcing:**

```python
# Event-based seat reservation (monotonic)
class SeatReservationEvents:
    def attempt_reservation(self, flight_id, seat_number, user_id, timestamp):
        # Just append the reservation attempt - always monotonic
        events.append(ReservationAttempt(
            flight_id=flight_id,
            seat_number=seat_number,
            user_id=user_id,
            timestamp=timestamp
        ))

    def get_seat_status(self, flight_id, seat_number):
        # Compute current status from all events
        attempts = get_events_for_seat(flight_id, seat_number)
        earliest_attempt = min(attempts, key=lambda x: x.timestamp)
        return earliest_attempt.user_id if earliest_attempt else "available"
```

### 2. Online Auction System

**Non-Monotonic Approach:**

```python
# Traditional auction (requires coordination)
class Auction:
    def place_bid(self, auction_id, user_id, amount):
        current_bid = get_current_highest_bid(auction_id)
        if amount > current_bid.amount:
            current_bid.amount = amount
            current_bid.user_id = user_id
            return "bid_accepted"
        return "bid_too_low"
```

**Monotonic Alternative - Append-Only Bids:**

```python
# Event-based auction (monotonic)
class AuctionEvents:
    def place_bid(self, auction_id, user_id, amount, timestamp):
        # Always append bid - never reject
        bids.append(Bid(
            auction_id=auction_id,
            user_id=user_id,
            amount=amount,
            timestamp=timestamp
        ))

    def get_winning_bid(self, auction_id):
        # Compute winner from all bids
        auction_bids = get_bids_for_auction(auction_id)
        return max(auction_bids, key=lambda x: x.amount)
```

### 3. Content Moderation System

**Non-Monotonic Approach:**

```python
# Traditional moderation (requires coordination)
class ContentModeration:
    def moderate_post(self, post_id, moderator_id, action):
        post = get_post(post_id)
        if action == "approve":
            post.status = "approved"
        elif action == "reject":
            post.status = "rejected"
        # What if two moderators decide differently?
```

**Monotonic Alternative - Voting System:**

```python
# Vote-based moderation (monotonic)
class ModerationVotes:
    def cast_vote(self, post_id, moderator_id, vote, timestamp):
        # Append all votes - never overwrite
        votes.append(ModerationVote(
            post_id=post_id,
            moderator_id=moderator_id,
            vote=vote,  # "approve" or "reject"
            timestamp=timestamp
        ))

    def get_moderation_decision(self, post_id):
        # Compute decision from all votes
        post_votes = get_votes_for_post(post_id)
        approve_count = sum(1 for v in post_votes if v.vote == "approve")
        reject_count = sum(1 for v in post_votes if v.vote == "reject")
        return "approved" if approve_count > reject_count else "rejected"
```

### 4. Real-Time Gaming Leaderboard

**Non-Monotonic Approach:**

```python
# Traditional leaderboard (requires coordination)
class Leaderboard:
    def update_score(self, user_id, new_score):
        current_score = get_user_score(user_id)
        if new_score > current_score:
            set_user_score(user_id, new_score)
            recompute_rankings()  # Expensive!
```

**Monotonic Alternative - Score Events:**

```python
# Event-based leaderboard (monotonic)
class LeaderboardEvents:
    def record_score(self, user_id, score, game_id, timestamp):
        # Always append score achievements
        scores.append(ScoreEvent(
            user_id=user_id,
            score=score,
            game_id=game_id,
            timestamp=timestamp
        ))

    def get_user_best_score(self, user_id):
        # Compute best score from all events
        user_scores = get_scores_for_user(user_id)
        return max(user_scores, key=lambda x: x.score)
```

### 5. Configuration Management System

**Non-Monotonic Approach:**

```python
# Traditional config (requires coordination)
class ConfigManager:
    def update_config(self, key, value):
        config[key] = value  # Overwrites previous value
        # What if multiple updates happen simultaneously?
```

**Monotonic Alternative - Configuration History:**

```python
# Versioned config (monotonic)
class ConfigHistory:
    def set_config(self, key, value, version, timestamp):
        # Always append new config versions
        configs.append(ConfigUpdate(
            key=key,
            value=value,
            version=version,
            timestamp=timestamp
        ))

    def get_current_config(self, key):
        # Get latest version of config
        key_configs = get_configs_for_key(key)
        return max(key_configs, key=lambda x: x.version)
```

## Design Patterns for Monotonic Systems

### 1. Event Sourcing Pattern

- Store events, not state
- State is computed from events
- Events are append-only (monotonic)

### 2. CRDT (Conflict-free Replicated Data Types)

- Data structures that merge automatically
- Examples: G-Sets (grow-only sets), PN-Counters
- Operations are inherently monotonic

### 3. Append-Only Architectures

- Immutable data structures
- New versions don't overwrite old ones
- Time-based versioning

### 4. Consensus-Free Voting

- Collect all votes/opinions
- Compute decisions from complete information
- No need to coordinate individual votes

## Key Takeaways

1. **Monotonic operations** = can be done without coordination
2. **Non-monotonic operations** = require coordination for consistency
3. **Design insight:** Try to make your operations monotonic when possible
4. **Practical benefit:** Monotonic systems are more scalable and fault-tolerant
5. **Trade-offs:** Monotonic systems may use more storage and computation
6. **Implementation:** Event sourcing and CRDTs are common patterns

The CALM theorem gives us a precise way to reason about when distributed systems can avoid expensive coordination, leading to better performance and availability.

## References

- "Keeping CALM: When Distributed Consistency is Easy" - Neil Conway et al.
- "Consistency Analysis in Bloom: a CALM and Collected Approach" - Ameloot et al.
- "Coordination Avoidance in Database Systems" - Bailis et al.
