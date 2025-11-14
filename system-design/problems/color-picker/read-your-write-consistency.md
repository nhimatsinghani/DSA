
# Read-Your-Write Consistency — Postgres & DynamoDB

This document summarizes practical ways to achieve **read-your-write consistency** in systems using Postgres (with replicas) and DynamoDB (with global tables).

---

## Concept

**Read-your-write consistency** means that once a client successfully writes data, subsequent reads by the same client will see that write (no stale data).

The implementation strategy is:

- **Post-write read → strong consistency source** (primary DB or strongly consistent read).  
- **Later/public reads → replicas/caches** (eventual consistency acceptable).

---

## A. Postgres (Primary + Async Replicas)

### 1) Return on Write (zero extra read)
- On `INSERT`/`UPDATE`, return the updated row directly:
  ```sql
  UPDATE favorites
  SET color_hex = $1, updated_at = now()
  WHERE user_id = $2
  RETURNING *;
  ```
- Client UI uses this to reflect the new state immediately.

### 2) Primary TTL Routing (common approach)
- After a successful write, mark request/session with:
  ```pseudo
  ctx.strong_read_until = now() + 3s
  ```
- Middleware/router:
  ```pseudo
  if (now < ctx.strong_read_until) use PRIMARY
  else use REPLICA
  ```

### 3) LSN Token Gating (lag-aware replica reads)
- Capture WAL LSN at commit:
  ```sql
  SELECT pg_current_wal_lsn();
  ```
- On a replica:
  ```sql
  SELECT pg_last_wal_replay_lsn() >= $commit_lsn;
  ```
- If not caught up, either **wait** briefly or **fallback to primary**.

### 4) Synchronous Replication (optional)
- Configure synchronous standby and commit with:
  ```
  synchronous_commit = 'remote_apply'
  ```
- Guarantees replicas see writes immediately, at cost of higher latency.

---

## B. DynamoDB

### 1) Strong Reads
- Use `GetItem/Query` with `ConsistentRead = true`.  
- Transactions (`TransactWriteItems`) also return authoritative state.

### 2) Return on Write
- `PutItem/UpdateItem` with `ReturnValues = 'ALL_NEW'`:
  ```json
  {
    "TableName": "Favorites",
    "Key": {"UserId": {"S": "u123"}},
    "UpdateExpression": "SET ColorHex = :c",
    "ExpressionAttributeValues": {":c": {"S":"#FF0000"}},
    "ReturnValues": "ALL_NEW"
  }
  ```

### 3) Global Tables
- Strongly consistent reads are **per-region only**.  
- For post-write reads, route to the **writer’s home region**.  
- Other regions will see data eventually.

### 4) Caching (DAX)
- DAX is eventually consistent.  
- For strong reads, bypass DAX and use Dynamo with `ConsistentRead=true`.

---

## C. Glue Code Pattern

```pseudo
// After write
ctx.consistency = {
  mode: "strong",
  source: "postgres|dynamo",
  expiresAt: now + 3s,
  token: commit_lsn | null
}

// Read routing
if ctx.source == "postgres":
   if now < ctx.expiresAt: return PRIMARY
   if ctx.token && replicaCaughtUp(ctx.token): return REPLICA
   return REPLICA
if ctx.source == "dynamo":
   if now < ctx.expiresAt: return DDB_STRONG_READ
   return DDB_EVENTUAL_READ
```

---

## D. Practical Guidance

- **Default**: Return on write + session TTL routing.  
- **Postgres advanced**: Add LSN gating if replicas must serve fresher reads.  
- **High guarantees**: Synchronous replication (`remote_apply`).  
- **DynamoDB**: Always use `ConsistentRead=true` in writer’s region for post-write reads; otherwise use eventual.  

---

*End of document.*
