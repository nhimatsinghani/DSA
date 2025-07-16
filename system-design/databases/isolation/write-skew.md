# Write Skew: A Subtle Database Anomaly

## What is Write Skew?

**Write skew** is an anomaly where:

1. Two transactions read overlapping data
2. Each transaction updates **different** items (no direct write-write conflict)
3. But the combined result violates a business constraint
4. Each transaction individually appears correct, but together they create an inconsistency

**Key insight:** It's about **constraint violations** that arise from the interaction between transactions, not individual transaction problems.

## Why Write Skew Occurs in Repeatable Read

**Repeatable Read guarantees:**

- If you read the same item twice, you get the same value
- You see a consistent snapshot of data

**What Repeatable Read DOESN'T prevent:**

- Constraint violations across multiple items
- Interactions between different transactions' write sets
- Business rule violations that depend on the combination of changes

## Classic Example: Hospital Doctor Shifts

Let me walk through this step by step:

```sql
-- Setup: Hospital rule - at least one doctor must be on call
CREATE TABLE doctors (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    on_call BOOLEAN
);

INSERT INTO doctors VALUES
    (1, 'Dr. Smith', TRUE),
    (2, 'Dr. Jones', TRUE);

-- Business rule: COUNT(*) WHERE on_call = TRUE must be >= 1
```

### Write Skew in Repeatable Read:

```sql
-- Both doctors want to go off-call simultaneously

-- Transaction 1 (Dr. Smith)
BEGIN; -- T1
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE;
-- Returns 2 (sees Dr. Smith=TRUE, Dr. Jones=TRUE)
-- Thinks: "2 doctors on call, safe for me to go off"

-- Transaction 2 (Dr. Jones) - runs concurrently
BEGIN; -- T2
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE;
-- Returns 2 (sees Dr. Smith=TRUE, Dr. Jones=TRUE)
-- Thinks: "2 doctors on call, safe for me to go off"

-- Both proceed to update DIFFERENT rows
UPDATE doctors SET on_call = FALSE WHERE id = 1; -- T1 (Dr. Smith)
UPDATE doctors SET on_call = FALSE WHERE id = 2; -- T2 (Dr. Jones)

COMMIT; -- T1
COMMIT; -- T2

-- RESULT: No doctors on call! Business rule violated!
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE; -- Returns 0
```

**Why Repeatable Read allows this:**

- Each transaction sees a consistent snapshot
- No direct write-write conflicts (updating different rows)
- The constraint violation emerges from the **combination** of both transactions

## More Examples of Write Skew

### Example 1: Meeting Room Booking

```sql
-- Setup: Meeting rooms with capacity limits
CREATE TABLE bookings (
    room_id INT,
    time_slot VARCHAR(20),
    user_id INT,
    attendees INT
);

CREATE TABLE rooms (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    capacity INT
);

INSERT INTO rooms VALUES (1, 'Conference Room A', 10);
-- Business rule: SUM(attendees) per room per time slot <= capacity
```

**Write Skew scenario:**

```sql
-- Two teams book the same room for the same time

-- Transaction 1 (Team A books for 8 people)
BEGIN; -- T1
SELECT SUM(attendees) FROM bookings
WHERE room_id = 1 AND time_slot = '9:00-10:00';
-- Returns 0 (no bookings yet)
-- Thinks: "Room is free, can book for 8 people"

-- Transaction 2 (Team B books for 6 people)
BEGIN; -- T2
SELECT SUM(attendees) FROM bookings
WHERE room_id = 1 AND time_slot = '9:00-10:00';
-- Returns 0 (no bookings yet)
-- Thinks: "Room is free, can book for 6 people"

-- Both insert their bookings
INSERT INTO bookings VALUES (1, '9:00-10:00', 'TeamA', 8); -- T1
INSERT INTO bookings VALUES (1, '9:00-10:00', 'TeamB', 6); -- T2

COMMIT; -- T1
COMMIT; -- T2

-- RESULT: 14 people booked in a room with capacity 10!
```

### Example 2: Budget Allocation

```sql
-- Setup: Department budget allocation
CREATE TABLE budget_allocations (
    department_id INT,
    project_id INT,
    amount DECIMAL(10,2)
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    total_budget DECIMAL(10,2)
);

INSERT INTO departments VALUES (1, 'Engineering', 100000);
-- Business rule: SUM(amount) per department <= total_budget
```

**Write Skew scenario:**

```sql
-- Two managers allocate budget simultaneously

-- Transaction 1 (Manager A allocates $60K)
BEGIN; -- T1
SELECT SUM(amount) FROM budget_allocations WHERE department_id = 1;
-- Returns 40000 (existing allocations)
-- Thinks: "40K used, 60K available, can allocate 60K"

-- Transaction 2 (Manager B allocates $70K)
BEGIN; -- T2
SELECT SUM(amount) FROM budget_allocations WHERE department_id = 1;
-- Returns 40000 (existing allocations)
-- Thinks: "40K used, 60K available, can allocate 70K"

-- Both insert their allocations
INSERT INTO budget_allocations VALUES (1, 'ProjectX', 60000); -- T1
INSERT INTO budget_allocations VALUES (1, 'ProjectY', 70000); -- T2

COMMIT; -- T1
COMMIT; -- T2

-- RESULT: 170K allocated from 100K budget!
```

### Example 3: Username Uniqueness

```sql
-- Setup: User registration system
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100)
);

-- Business rule: usernames must be unique
```

**Write Skew scenario:**

```sql
-- Two users try to register with same username

-- Transaction 1 (User A)
BEGIN; -- T1
SELECT COUNT(*) FROM users WHERE username = 'john_doe';
-- Returns 0 (username available)
-- Thinks: "Username is free, can register"

-- Transaction 2 (User B)
BEGIN; -- T2
SELECT COUNT(*) FROM users WHERE username = 'john_doe';
-- Returns 0 (username available)
-- Thinks: "Username is free, can register"

-- Both try to insert
INSERT INTO users VALUES (1, 'john_doe', 'userA@email.com'); -- T1
INSERT INTO users VALUES (2, 'john_doe', 'userB@email.com'); -- T2

COMMIT; -- T1
COMMIT; -- T2 (fails with unique constraint violation)

-- In this case, the database constraint prevents the violation
-- But without the UNIQUE constraint, we'd have duplicate usernames
```

## How Serializable Prevents Write Skew

**Serializable isolation** ensures that transactions appear to execute in some serial order. This prevents write skew through several mechanisms:

### 1. Predicate Locking / Serialization Graph Testing

```sql
-- Back to the doctor example in SERIALIZABLE mode

-- Transaction 1 (Dr. Smith)
BEGIN; -- T1
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE;
-- Database notes: T1 depends on the result of this predicate

-- Transaction 2 (Dr. Jones)
BEGIN; -- T2
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE;
-- Database notes: T2 also depends on the same predicate

-- When T1 tries to update:
UPDATE doctors SET on_call = FALSE WHERE id = 1; -- T1
-- Database detects: This update affects the predicate that T2 read!

-- When T2 tries to update:
UPDATE doctors SET on_call = FALSE WHERE id = 2; -- T2
-- Database detects: Serialization cycle! T1 → T2 → T1

-- Result: One transaction gets a serialization error
COMMIT; -- T1 (succeeds)
COMMIT; -- T2 (fails with serialization error)
```

### 2. Possible Outcomes in Serializable

**Outcome 1: Sequential execution**

```sql
-- T1 completes first
T1: SELECT COUNT(*) → 2, UPDATE id=1 → FALSE, COMMIT
T2: SELECT COUNT(*) → 1, decides not to update, COMMIT
-- Result: 1 doctor on call (constraint maintained)
```

**Outcome 2: Serialization error**

```sql
-- T1 and T2 run concurrently
T1: SELECT COUNT(*) → 2, UPDATE id=1 → FALSE
T2: SELECT COUNT(*) → 2, UPDATE id=2 → FALSE
-- Database detects conflict, one transaction gets serialization error
-- Application must retry the failed transaction
```

**Outcome 3: Blocking**

```sql
-- T2 blocks until T1 commits
T1: SELECT COUNT(*) → 2, UPDATE id=1 → FALSE, COMMIT
T2: (blocked) → wakes up, SELECT COUNT(*) → 1, decides not to update
-- Result: 1 doctor on call (constraint maintained)
```

## Detection Mechanisms in Serializable

### 1. Serializable Snapshot Isolation (SSI)

Used by PostgreSQL's SERIALIZABLE level:

```sql
-- PostgreSQL example
BEGIN ISOLATION LEVEL SERIALIZABLE; -- T1
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE;
-- SSI tracks this read predicate

-- If another transaction modifies data that affects this predicate:
-- PostgreSQL will detect the conflict and abort one transaction
```

### 2. Two-Phase Locking (2PL)

Traditional approach:

```sql
-- Acquires shared locks on all read data
-- Acquires exclusive locks on all written data
-- Holds all locks until commit/rollback
-- Prevents conflicts but can cause deadlocks
```

### 3. Optimistic Concurrency Control

Used in some systems:

```sql
-- Allow transactions to proceed optimistically
-- Check for conflicts at commit time
-- Retry failed transactions
-- Higher concurrency but potential retries
```

## Key Differences: Repeatable Read vs Serializable

| Aspect            | Repeatable Read                             | Serializable                            |
| ----------------- | ------------------------------------------- | --------------------------------------- |
| **Focus**         | Item-level consistency                      | Transaction-level consistency           |
| **Guarantees**    | Same item reads return same value           | Transactions appear serial              |
| **Write Skew**    | **Allows** (constraint violations possible) | **Prevents** (no constraint violations) |
| **Performance**   | Better (less blocking/retries)              | Worse (more blocking/retries)           |
| **Complexity**    | Simpler conflict detection                  | Complex cycle detection                 |
| **Phantom Reads** | May prevent (depends on implementation)     | Always prevents                         |
| **Deadlocks**     | Fewer                                       | More likely                             |

## Practical Implications

### When to Use Repeatable Read

- Most applications where write skew is unlikely
- Performance is important
- Can handle constraint violations at application level
- Simple business rules

### When to Use Serializable

- Financial systems
- Inventory management
- Any system with complex business constraints
- When correctness is more important than performance
- Multi-step business processes

### Application-Level Solutions for Write Skew

Even with Repeatable Read, you can prevent write skew:

#### 1. Explicit Locking

```sql
-- Use explicit locking to prevent concurrent modifications
BEGIN; -- T1
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE FOR UPDATE;
-- This creates a lock that prevents concurrent modifications
UPDATE doctors SET on_call = FALSE WHERE id = 1;
COMMIT;
```

#### 2. Application-Level Constraints

```sql
-- Check constraints in application code before committing
BEGIN; -- T1
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE;
UPDATE doctors SET on_call = FALSE WHERE id = 1;
-- Before commit, recheck constraint
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE;
-- If constraint would be violated, rollback
COMMIT;
```

#### 3. Optimistic Locking with Versions

```sql
-- Use version numbers to detect conflicts
CREATE TABLE doctors (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    on_call BOOLEAN,
    version INT DEFAULT 0
);

-- Application logic:
-- 1. Read current version
-- 2. Perform business logic
-- 3. Update with version check
UPDATE doctors
SET on_call = FALSE, version = version + 1
WHERE id = 1 AND version = @original_version;
-- If no rows updated, another transaction modified the data
```

## Real-World Write Skew Scenarios

### 1. E-commerce Inventory

```sql
-- Product inventory management
-- Rule: Can't sell more items than in stock
-- Write skew: Two customers buy the last item simultaneously
```

### 2. Bank Account Transfers

```sql
-- Account balance management
-- Rule: Account balance can't go negative
-- Write skew: Two transfers from same account exceed balance
```

### 3. Course Registration

```sql
-- Student course enrollment
-- Rule: Course enrollment can't exceed capacity
-- Write skew: Multiple students enroll in a full course
```

### 4. Resource Allocation

```sql
-- Server resource allocation
-- Rule: Total allocated resources can't exceed available
-- Write skew: Multiple processes allocate more than available
```

## Summary

**Write skew** is a subtle anomaly where individually correct transactions combine to violate constraints. It happens in Repeatable Read because:

- Each transaction sees consistent data
- No direct write conflicts occur
- But the interaction between transactions creates problems

**Serializable** prevents this by ensuring transactions appear to run in serial order, detecting conflicts through:

- Predicate locking
- Serialization graph testing
- Optimistic concurrency control

**The trade-off is performance vs correctness** - choose based on your application's requirements:

- Use Repeatable Read for most applications with simple constraints
- Use Serializable for critical systems with complex business rules
- Consider application-level solutions for specific constraint enforcement

Understanding write skew is crucial for designing robust database applications, especially in systems with complex business rules and high concurrency requirements.
