
# MVCC & Optimistic Concurrency: Deep Dive + Retry Loops

> Audience: engineers designing for high-concurrency workloads on PostgreSQL, Cassandra, DynamoDB, and MongoDB (WiredTiger).  
> Scope: how MVCC avoids “version-number contention,” what actually contends, and robust retry strategies.

---

## TL;DR

- **PostgreSQL** doesn’t increment an in-place “version field.” An `UPDATE` creates a **new tuple**; the prior tuple is logically retired. Concurrency is mediated by **row locks + MVCC visibility**—so there’s no hotspot on a single counter.  
- **Cassandra** defaults to last-write-wins with timestamps. For optimistic checks, use **Lightweight Transactions (LWT)**, which run **Paxos** (linearizable compare-and-set). One proposal wins; the rest get `APPLIED = false` and should retry.  
- **DynamoDB** uses **conditional writes** and optional **ACID transactions**. The update and the “check” happen atomically; failures raise exceptions (e.g., `ConditionalCheckFailedException`).  
- **MongoDB (WiredTiger)** provides MVCC-style **snapshots**. Write conflicts surface as **`WriteConflict`** / transient transaction errors and must be **retried** by the client.

---

## 1) PostgreSQL: why there’s no “version column contention”

### How MVCC works (no in-place bump)
- Each physical row **version (tuple)** stores `xmin` (creator XID) and `xmax` (deleter/updater XID). **Every UPDATE writes a new version**; the old version’s `xmax` is set. Your snapshot rules decide which version is visible.  
  - Official docs on MVCC and system columns: [MVCC intro](https://www.postgresql.org/docs/current/mvcc-intro.html), [System columns (`xmin`, `xmax`)](https://www.postgresql.org/docs/current/ddl-system-columns.html).

### What actually contends
- **Row-level locking**: The updater that grabs the tuple lock first proceeds; others **wait** and then re-check the row after the winner commits.  
  - See: [Explicit locking & row locks](https://www.postgresql.org/docs/current/explicit-locking.html).

### Storage and cleanup details (why updates scale)
- **Tuple chains**: Conceptually, `UPDATE = DELETE + INSERT` of a new tuple version.  
- **HOT (Heap-Only Tuples)**: if no indexed column changes, PG can update on-page without touching indexes—reducing contention.  
- **Autovacuum & Visibility Map** free dead versions and enable index-only scans.  
  - Docs: [HOT](https://www.postgresql.org/docs/current/storage-hot.html), [Routine vacuuming & visibility map](https://www.postgresql.org/docs/14/routine-vacuuming.html).

### Optional: app-level OCC in PG
If you want optimistic checks **in addition** to native locking, use a predicate on a `version` column:

```sql
-- Read
SELECT id, payload, version FROM items WHERE id = $1;

-- Write (atomic compare-and-set)
UPDATE items
SET payload = $2, version = version + 1
WHERE id = $1 AND version = $3
RETURNING *;
```

**References**  
- MVCC intro (snapshot view): https://www.postgresql.org/docs/current/mvcc-intro.html  
- System columns (`xmin`/`xmax`): https://www.postgresql.org/docs/current/ddl-system-columns.html  
- Row/explicit locking: https://www.postgresql.org/docs/current/explicit-locking.html  
- HOT updates: https://www.postgresql.org/docs/current/storage-hot.html  
- Vacuum/visibility map: https://www.postgresql.org/docs/14/routine-vacuuming.html

---

## 2) Cassandra: LWT (Paxos) for optimistic checks

- Default writes are upserts with timestamps (**not** per-row MVCC). Reads reconcile versions; last-write-wins by timestamp.  
- For compare-and-set semantics, use **Lightweight Transactions** (`IF` conditions). Cassandra runs **Paxos** so **exactly one** proposal applies; others return `APPLIED=false`. This is **linearizable** on the partition.  
- Expect higher latency versus normal writes; Cassandra 4.1’s **Paxos v2** improved performance but it remains costlier than plain writes.

**Example (CQL)**
```sql
UPDATE items
SET payload = '...',
    version = 6
WHERE pk = ?
IF version = 5;      -- only one writer sees APPLIED=true
```

**Operational notes**  
- Tune **consistency** for LWT: request **SERIAL/LOCAL_SERIAL** for the Paxos phase (and QUORUM/LOCAL_QUORUM for normal phase) according to topology/SLA.  
- Watch for contention on hot partitions; use backoff and jitter.

**References**  
- LWT & Paxos (DataStax docs): https://docs.datastax.com/en/cassandra-oss/2.1/cassandra/dml/dml_ltwt_transaction_c.html  
- Apache Cassandra 4.1 docs (overview): https://cassandra.apache.org/doc/4.1/index.html  
- Guarantees / linearizable CAS: https://cassandra.apache.org/doc/4.1/cassandra/architecture/guarantees.html  
- Serial consistency (what it controls): https://docs.datastax.com/en/cql-oss/3.3/cql/cql_reference/cqlshSerialConsistency.html

---

## 3) DynamoDB: conditional writes + ACID transactions

- **Optimistic locking** pattern: keep a `version` attribute and use a **ConditionExpression** so the update and the check occur atomically. Conflicts raise `ConditionalCheckFailedException`.  
- For multi-item atomicity, use **TransactWriteItems** (ACID). You can pass a **ClientRequestToken** for **idempotency** within a 10‑minute window.

**Example (UpdateItem)**
```jsonc
// UpdateItem (pseudo-JSON for clarity)
{
  "Key": {"pk": {"S": "X"}},
  "UpdateExpression": "SET payload=:p, version = version + :one",
  "ConditionExpression": "version = :expected",
  "ExpressionAttributeValues": {":p": {"S":"..."}, ":one":{"N":"1"}, ":expected":{"N":"5"}}
}
```

**References**  
- Optimistic locking concept (Mapper): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBMapper.OptimisticLocking.html  
- `UpdateItem` and `ConditionExpression`: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateItem.html  
- Transactions and idempotency: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html and https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html

---

## 4) MongoDB (WiredTiger): MVCC snapshots + retries

- **WiredTiger uses MVCC**: operations read from a **point-in-time snapshot**; readers don’t block writers.  
- Concurrent writers on the same document can surface **`WriteConflict`**. For multi-document **transactions**, drivers recommend **retrying** on labeled transient errors and unknown commit results.
- Stronger read guarantees are selectable via **read concerns**: `majority`, and **`snapshot`** (used in transactions).

**References**  
- WiredTiger & MVCC: https://www.mongodb.com/docs/v6.1/core/wiredtiger/  
- Retryable writes & transaction retry guidance: https://www.mongodb.com/docs/manual/core/retryable-writes/ and https://www.mongodb.com/docs/manual/core/transactions-in-applications/  
- Read concern `"snapshot"`: https://www.mongodb.com/docs/manual/reference/read-concern-snapshot/

---

## 5) Robust retry loops (patterns & snippets)

### General guidance

1. **Make operations idempotent** (keys/tokens) or use **compare-and-set** conditions.  
2. **Retry only on retriable errors**; **fail fast** on validation or permission errors.  
3. Use **exponential backoff with jitter** (e.g., full jitter).  
4. Cap retries (**max attempts / max elapsed time**); add **observability** (metrics, structured logs, correlation IDs).  
5. **Budget for timeouts** and prefer **server-side timeouts** where available.

---

### PostgreSQL — retry on serialization/deadlock

Retry transactions that fail with `SQLSTATE` **`40001`** (serialization failure) or **`40P01`** (deadlock). Keep transactions **short** and **deterministic**.

```python
# psycopg (Python)
import psycopg
import time, random

RETRYABLE = {"40001", "40P01"}  # serialization_failure, deadlock_detected

def run_txn(conn, fn, max_attempts=5, base=0.01, cap=0.5):
    attempt = 0
    while True:
        attempt += 1
        try:
            with conn.transaction():
                return fn(conn)  # do your SQL here
        except psycopg.Error as e:
            code = getattr(e, "sqlstate", None)
            if code in RETRYABLE and attempt < max_attempts:
                # exponential backoff with jitter
                sleep = min(cap, base * (2 ** (attempt-1))) * random.random()
                time.sleep(sleep)
                continue
            raise
```

**Why**: PG’s Serializable Snapshot Isolation & locking may raise 40001; apps **must** be prepared to retry in these levels.  
Docs: Serialization failure handling: https://www.postgresql.org/docs/current/mvcc-serialization-failure-handling.html

---

### Cassandra — retry LWT when `APPLIED=false`

```python
# DataStax Python driver
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, ConsistencyLevel

cluster = Cluster(["c1","c2"])
session = cluster.connect("ks")

stmt = SimpleStatement(
    "UPDATE items SET payload=?, version=? WHERE pk=? IF version=?",
    consistency_level=ConsistencyLevel.QUORUM,        # normal phase
    serial_consistency_level=ConsistencyLevel.SERIAL  # Paxos phase
)

def cas_update(pk, expected, new_payload):
    attempt = 0
    while attempt < 6:
        attempt += 1
        result = session.execute(stmt, (new_payload, expected+1, pk, expected))
        row = result.one()
        if row and row.applied:
            return True
        # backoff with jitter
        import time, random
        time.sleep(min(0.5, 0.01*(2**(attempt-1))) * random.random())
        # refresh expected from DB (optional read at QUORUM)
    return False
```

Docs: LWT/Paxos & `APPLIED` semantics:  
- https://docs.datastax.com/en/cassandra-oss/2.1/cassandra/dml/dml_ltwt_transaction_c.html  
- Serial consistency: https://docs.datastax.com/en/cql-oss/3.3/cql/cql_reference/cqlshSerialConsistency.html

---

### DynamoDB — retry conditional writes & transactions

```python
import boto3, botocore, time, random
ddb = boto3.client("dynamodb")

def update_with_occ(table, key, expected_ver, payload):
    attempt = 0
    while attempt < 6:
        attempt += 1
        try:
            ddb.update_item(
              TableName=table, Key=key,
              UpdateExpression="SET payload=:p, ver = ver + :one",
              ConditionExpression="ver = :v",
              ExpressionAttributeValues={":p":{"S":payload}, ":one":{"N":"1"}, ":v":{"N":str(expected_ver)}}
            )
            return True
        except ddb.exceptions.ConditionalCheckFailedException:
            # someone else won; caller should re-read & retry (or surface conflict)
            return False
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] in ("ProvisionedThroughputExceededException",
                                               "TransactionInProgressException",
                                               "InternalServerError"):
                time.sleep(min(0.5, 0.01*(2**(attempt-1))) * random.random())
                continue
            raise
```

For multi-item atomic writes, use `TransactWriteItems` and pass a **`ClientRequestToken`** for idempotency (10‑minute window).  
Docs: Condition expressions & UpdateItem: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateItem.html  
Transactions & idempotent client tokens:  
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html  
- https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html

---

### MongoDB — retry `TransientTransactionError` / `WriteConflict`

Idiomatic driver patterns: **retry the whole transaction** on errors labeled `TransientTransactionError`; **retry commit** on `UnknownTransactionCommitResult`. For single-document operations that return **`WriteConflict`**, retry the operation.

```javascript
// Node.js (pseudocode)
async function runTxnWithRetry(session, txnFn, {max=5}={}) {
  for (let attempt=1; attempt<=max; attempt++) {
    try {
      session.startTransaction({ readConcern: {level: "snapshot"}, writeConcern: {w: "majority"} });
      const out = await txnFn(session);
      await session.commitTransaction(); // may need commit-retry if "UnknownTransactionCommitResult"
      return out;
    } catch (e) {
      const transient = e.hasErrorLabel && e.hasErrorLabel("TransientTransactionError");
      const unknownCommit = e.hasErrorLabel && e.hasErrorLabel("UnknownTransactionCommitResult");
      if (transient || unknownCommit) {
        // backoff with jitter
        const j = Math.random() * Math.min(500, 10 * (2 ** (attempt-1)));
        await new Promise(r => setTimeout(r, j));
        try { await session.abortTransaction(); } catch (_) {}
        continue;
      }
      throw e;
    }
  }
  throw new Error("transaction retries exhausted");
}
```

Docs:  
- WiredTiger MVCC snapshots: https://www.mongodb.com/docs/v6.1/core/wiredtiger/  
- Retryable writes & transaction retry guidance: https://www.mongodb.com/docs/manual/core/transactions-in-applications/ and https://www.mongodb.com/docs/manual/core/retryable-writes/  
- Read concern `snapshot`: https://www.mongodb.com/docs/manual/reference/read-concern-snapshot/

---

## 6) Quick comparison

| System      | “MVCC” Mechanism                                    | Optimistic CAS | What to Retry |
|-------------|-------------------------------------------------------|----------------|---------------|
| PostgreSQL  | Tuple versions (`xmin`/`xmax`); UPDATE creates new tuple; locks on current version; VACUUM prunes | App-level `WHERE version = ?` if desired | `40001` (serialization), `40P01` (deadlock) |
| Cassandra   | LWW + reconciliation; LWT uses Paxos (linearizable CAS) | `IF` clauses (LWT) | `APPLIED=false`, timeouts; backoff & re-read |
| DynamoDB    | Item-level atomic ops; no MVCC; conditional writes | `ConditionExpression`, Mapper optimistic locking | `ConditionalCheckFailedException` (then re-read); transient 5xx |
| MongoDB     | WiredTiger MVCC snapshots for reads; conflicts on write | App-level predicate on `version` if needed | Labeled transaction errors & `WriteConflict` |

---

## Appendix: operational checklists

- **PostgreSQL**: keep transactions short; prefer `SELECT ... FOR UPDATE` when you truly need to serialize; avoid hotspot rows; monitor `pg_locks`, deadlocks, vacuum lag.  
- **Cassandra**: keep partitions small; avoid LWT on hot keys; use `LOCAL_SERIAL` when multi‑DC isn’t required; monitor Paxos metrics.  
- **DynamoDB**: pick good partition keys to avoid hot partitions; use conditional writes; for multi-item workflows, `TransactWriteItems` with `ClientRequestToken`; set SDK retries with jitter.  
- **MongoDB**: keep transactions small (<60s); use `readConcern: "snapshot"` and `writeConcern: "majority"` when you need it; size collections/indexes to reduce conflicts; enable driver retry logic.

---

_© 2025. Links point to vendor docs where possible for long-term stability._
