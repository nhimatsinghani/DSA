# Seeing is Believing: A Client-Centric Specification of Database Isolation

## Introduction

The traditional ANSI SQL isolation levels (READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE) are defined by the anomalies they prevent. This paper by Crooks et al. introduces a **client-centric** approach that's much more intuitive - focusing on what a client can observe rather than what anomalies are prevented.

## Why Client-Centric Matters

**Traditional approach:** "REPEATABLE READ prevents non-repeatable reads"
**Client-centric approach:** "In REPEATABLE READ, if you read the same item twice, you get the same value"

The client-centric view is much more practical for developers!

## Core Concepts

### 1. Client Sessions and Transactions

- **Client session**: A sequence of transactions from a single client
- **Transaction**: A unit of work that reads/writes data
- **Real-time ordering**: The actual order events happen in wall-clock time

### 2. Key Principles

**Principle 1: Item Cut Isolation**

- Each item (row) appears to have a linear version history
- Different clients may see different cuts of this history
- But within a transaction, the cut is consistent

**Principle 2: Session Order**

- Effects of committed transactions appear in session order
- Later transactions in a session see effects of earlier ones

## Isolation Levels Explained

### 1. READ UNCOMMITTED (RU)

**What the client sees:**

- Can read uncommitted (dirty) data
- No guarantees about consistency
- Weakest isolation level

**Example:**

```sql
-- Setup
CREATE TABLE accounts (id INT, balance INT);
INSERT INTO accounts VALUES (1, 1000), (2, 500);

-- Timeline:
-- T1 (Client A): Transfer $200 from account 1 to account 2
-- T2 (Client B): Read both accounts

-- T1 starts
BEGIN; -- T1
UPDATE accounts SET balance = balance - 200 WHERE id = 1;
-- Account 1 now has $800 (uncommitted)

-- T2 reads dirty data
SELECT * FROM accounts WHERE id = 1; -- Returns $800 (dirty read!)
SELECT * FROM accounts WHERE id = 2; -- Returns $500

-- T1 rolls back
ROLLBACK; -- T1
-- Account 1 is back to $1000

-- T2 saw inconsistent state: $800 + $500 = $1300 (should be $1500)
```

**Client observation:** Can see uncommitted changes that might be rolled back.

### 2. READ COMMITTED (RC)

**What the client sees:**

- Only reads committed data
- Each statement sees a fresh snapshot
- Can observe changes between statements in the same transaction

**Example:**

```sql
-- Setup: Same as above

-- Timeline:
-- T1: Transfer money (commits between T2's reads)
-- T2: Read accounts twice in same transaction

-- T2 starts
BEGIN; -- T2
SELECT balance FROM accounts WHERE id = 1; -- Returns $1000

-- T1 executes and commits
BEGIN; -- T1
UPDATE accounts SET balance = balance - 200 WHERE id = 1;
UPDATE accounts SET balance = balance + 200 WHERE id = 2;
COMMIT; -- T1

-- T2 continues in same transaction
SELECT balance FROM accounts WHERE id = 1; -- Returns $800 (different!)
COMMIT; -- T2
```

**Client observation:** Within the same transaction, you can see different values for the same item if another transaction commits between your reads.

### 3. REPEATABLE READ (RR)

**What the client sees:**

- If you read the same item twice, you get the same value
- Snapshot taken at transaction start
- Prevents phantom reads in some implementations

**Example:**

```sql
-- Setup: Same as above

-- Timeline:
-- T1: Transfer money
-- T2: Read accounts multiple times

-- T2 starts and takes snapshot
BEGIN; -- T2
SELECT balance FROM accounts WHERE id = 1; -- Returns $1000

-- T1 executes and commits (but T2 doesn't see it)
BEGIN; -- T1
UPDATE accounts SET balance = balance - 200 WHERE id = 1;
UPDATE accounts SET balance = balance + 200 WHERE id = 2;
COMMIT; -- T1

-- T2 reads again - sees same values as before
SELECT balance FROM accounts WHERE id = 1; -- Still returns $1000
SELECT balance FROM accounts WHERE id = 2; -- Still returns $500
COMMIT; -- T2
```

**Client observation:** You see a consistent snapshot throughout your transaction, even if other transactions commit changes.

### 4. SERIALIZABLE

**What the client sees:**

- Transactions appear to execute in some serial order
- No concurrency anomalies possible
- Strongest isolation level

**Example:**

```sql
-- Setup: Same as above

-- Timeline:
-- T1: Transfer money
-- T2: Check total balance

-- Both transactions start
BEGIN; -- T1
BEGIN; -- T2

-- T1 tries to update
UPDATE accounts SET balance = balance - 200 WHERE id = 1; -- T1

-- T2 tries to read
SELECT SUM(balance) FROM accounts; -- T2 may block or get serialization error

-- One of these outcomes:
-- Option 1: T2 blocks until T1 commits, then sees new values
-- Option 2: T2 gets serialization error and must retry
-- Option 3: T1 gets serialization error and must retry

COMMIT; -- T1
COMMIT; -- T2
```

**Client observation:** Either you wait for conflicting transactions or get serialization errors. The final result is as if transactions executed one after another.

## Advanced Examples

### Phantom Reads Example

**Setup:**

```sql
CREATE TABLE employees (id INT, department VARCHAR(50), salary INT);
INSERT INTO employees VALUES
  (1, 'Engineering', 80000),
  (2, 'Engineering', 90000),
  (3, 'Marketing', 70000);
```

**READ COMMITTED (allows phantoms):**

```sql
-- T1: Calculate average engineering salary
BEGIN; -- T1
SELECT AVG(salary) FROM employees WHERE department = 'Engineering';
-- Returns 85000 (average of 80000 and 90000)

-- T2: Add new engineer
BEGIN; -- T2
INSERT INTO employees VALUES (4, 'Engineering', 100000);
COMMIT; -- T2

-- T1 reads again
SELECT AVG(salary) FROM employees WHERE department = 'Engineering';
-- Returns 90000 (average of 80000, 90000, and 100000) - PHANTOM!
COMMIT; -- T1
```

**REPEATABLE READ (prevents phantoms):**

```sql
-- T1: Calculate average engineering salary
BEGIN; -- T1
SELECT AVG(salary) FROM employees WHERE department = 'Engineering';
-- Returns 85000

-- T2: Add new engineer
BEGIN; -- T2
INSERT INTO employees VALUES (4, 'Engineering', 100000);
COMMIT; -- T2

-- T1 reads again - sees same result
SELECT AVG(salary) FROM employees WHERE department = 'Engineering';
-- Still returns 85000 (no phantom)
COMMIT; -- T1
```

### Write Skew Example (SERIALIZABLE prevents this)

```sql
-- Setup: Hospital shifts (at least one doctor must be on call)
CREATE TABLE doctors (id INT, name VARCHAR(50), on_call BOOLEAN);
INSERT INTO doctors VALUES
  (1, 'Dr. Smith', TRUE),
  (2, 'Dr. Jones', TRUE);

-- Both doctors try to go off-call simultaneously
-- T1: Dr. Smith goes off-call
BEGIN; -- T1
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE; -- Returns 2
-- Thinks: "2 doctors on call, safe for me to go off"

-- T2: Dr. Jones goes off-call
BEGIN; -- T2
SELECT COUNT(*) FROM doctors WHERE on_call = TRUE; -- Returns 2
-- Thinks: "2 doctors on call, safe for me to go off"

-- Both update
UPDATE doctors SET on_call = FALSE WHERE id = 1; -- T1
UPDATE doctors SET on_call = FALSE WHERE id = 2; -- T2

COMMIT; -- T1
COMMIT; -- T2

-- Result: No doctors on call! (Business rule violated)
```

**In SERIALIZABLE:** One transaction would block or get a serialization error.

## Practical Implications

### Performance vs Consistency Trade-offs

| Isolation Level  | Performance | Consistency | Use Cases                                         |
| ---------------- | ----------- | ----------- | ------------------------------------------------- |
| READ UNCOMMITTED | Highest     | Lowest      | Analytics, reporting where approximate data is OK |
| READ COMMITTED   | High        | Medium      | Most web applications, default for many databases |
| REPEATABLE READ  | Medium      | High        | Financial systems, inventory management           |
| SERIALIZABLE     | Lowest      | Highest     | Critical systems, complex business logic          |

### Choosing the Right Level

**READ COMMITTED** is often the sweet spot:

- Prevents dirty reads (most important)
- Good performance
- Sufficient for many applications

**REPEATABLE READ** when you need:

- Consistent snapshots
- Complex calculations across multiple reads
- Audit trails

**SERIALIZABLE** when you need:

- Strict correctness
- Complex business rules
- Can tolerate retries and blocking

## Client-Centric Benefits

1. **Easier to reason about**: Focus on what you observe, not what's prevented
2. **Better testing**: You can write tests based on expected observations
3. **Clearer debugging**: Anomalies are described in terms of what clients see

## Key Takeaways

1. **Client-centric thinking** makes isolation levels much more intuitive
2. **Higher isolation = more consistency, less performance**
3. **Most applications work fine with READ COMMITTED**
4. **Test your application** under the isolation level you choose
5. **Consider retries** for serialization errors at higher levels

The "Seeing is Believing" approach transforms isolation levels from abstract concepts into practical, observable behaviors that developers can easily understand and work with.
