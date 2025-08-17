## Redis failover strategies and durability deep dive

### Why this matters

- **Redis is in-memory**: fast, but volatile. Without persistence or replication, a node crash means data loss.
- **Goals**:
  - **Availability (RTO)**: keep serving reads/writes during failures.
  - **Durability (RPO)**: minimize/avoid data loss when a node or AZ fails.
  - **Consistency**: acceptable staleness during/after failover.

---

## Failure modes to plan for

- **Single node crash**: process/host crash, kernel panic, OOM.
- **AZ failure**: power/network partition affecting one AZ.
- **Disk corruption**: persistence files damaged.
- **Split brain**: multiple primaries accepting writes.
- **Network partitions**: delayed or dropped replication stream.

Define targets up front:

- **RPO** (acceptable data loss): 0, ~1s, or higher.
- **RTO** (time to recover): sub-second, seconds, minutes.

---

## Durability mechanisms (local)

Redis provides two persistence modes. You can enable either or both.

### RDB snapshots

- Periodically writes a point-in-time snapshot of all data to disk (`dump.rdb`).
- **Pros**: compact, fast restart, low write amplification.
- **Cons**: data loss = time since last snapshot. Background `BGSAVE` uses copy-on-write.
- **Config**:

```conf
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
```

### AOF (Append Only File)

- Logs each write to disk. Restarts by replaying log (or RDB preamble).
- **Fsync policies**:
  - `appendfsync always`: strongest durability, highest latency.
  - `appendfsync everysec`: default balance; RPO ≈ up to 1s.
  - `appendfsync no`: rely on OS flush; weakest.
- **Rewrite (compaction)**: background rewrite to shrink AOF. Use preamble.
- **Config**:

```conf
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-use-rdb-preamble yes
```

### RDB + AOF together

- Recommended: enable **AOF with RDB preamble** for quick restarts plus bounded RPO.
- Startup order: if AOF exists, Redis loads AOF (with preamble) by default.

### Practical RPO expectations

- **AOF everysec**: up to ~1s loss on crash.
- **AOF always**: ~0, but higher latency; often acceptable only for smaller loads.
- **RDB-only**: loss equal to snapshot interval.

---

## Replication and write safety

### Asynchronous replication (default)

- Primary streams writes to replicas over TCP.
- If primary dies before replica receives a write, that write is lost (asynchronous gap).

### Partial resync (PSYNC) and backlog

- Replication backlog enables **partial resynchronization** after transient disconnects.
- Tune backlog to cover expected network hiccups.

```conf
replication-backlog-size 64mb
repl-timeout 60
```

### Diskless replication

- Reduces disk IO during initial syncs.

```conf
repl-diskless-sync yes
repl-diskless-sync-delay 5
```

### Make writes more synchronous (lower RPO)

- Use the `WAIT` command after writes to block until N replicas acknowledge they received the write.
- Pattern: append `WAIT <numReplicas> <timeoutMs>` after a transactional batch.
- Caveat: replicas acknowledge receipt, not fsync. Combine with AOF on replicas for stronger safety.

Example (pseudo):

```text
MULTI
SET k v
INCR c
EXEC
WAIT 1 100
```

### Prevent writing when replication is unhealthy

```conf
min-replicas-to-write 1
min-replicas-max-lag 5
```

- Primary rejects writes if fewer than N replicas are up-to-date (back-pressure to protect RPO).

---

## Automatic failover options

### Option 1: Redis Sentinel (single primary, replicas)

- Components: 1 primary, N replicas, 3–5 Sentinel daemons.
- Sentinels monitor, agree (quorum), and promote a replica on failure.
- Application clients discover the new primary via Sentinel.

Key Sentinel configs (on Sentinel nodes):

```conf
port 26379
daemonize yes
sentinel monitor mymaster 10.0.0.10 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
```

- **Quorum**: at least 2 in this example; use 3 or 5 Sentinels in odd count.
- **Avoid split brain**: ensure majority can communicate; deploy across AZs.

Primary and Replica configs:

```conf
replica-read-only yes
replica-priority 100
client-output-buffer-limit replica 512mb 128mb 60
```

Client considerations:

- Connect to Sentinels, ask for current primary (`SENTINEL get-master-addr-by-name`).
- Use retry with backoff; idempotent writes.

### Option 2: Redis Cluster (sharded, built-in failover)

- 16384 hash slots, partitioned across primaries; each has one or more replicas.
- Gossip protocol detects failures; replicas promote to primary (election with epochs).
- Pros: horizontal scale + HA. Cons: multi-key ops limited unless keys share a hash tag.

Operational notes:

- Use at least 3 primaries, each with 1+ replica; spread across AZs.
- Client must be cluster-aware (redirects: `MOVED`, `ASK`).

### Option 3: Managed services

- ElastiCache/Memorystore/Redis Cloud handle Sentinel/Cluster, node swaps, patching.
- Enable Multi-AZ with Auto-Failover; choose AOF/RDB per RPO.

---

## Consistency during and after failover

- **Stale reads**: replicas are eventually consistent. Use `replica-read-only yes`. For read-your-writes, read from primary or use client-side tracking.
- **Write fencing**:
  - Combine `min-replicas-to-write` with `WAIT` for stronger guarantees.
  - Use monotonically increasing IDs or conditional writes (`WATCH`/`CAS`) to handle retries.
- **Client retries**: exponential backoff; ensure idempotency of write operations.

---

## Cross-AZ/Region and disaster recovery

- **Single region, multi-AZ**: place primary in AZ-A, replicas in AZ-B/C; Sentinels/Cluster managers across AZs.
- **Cross-region DR (open-source)**: async replica in DR region; higher RPO due to WAN latency. Periodically promote/test.
- **Active-active (multi-master)**: use Redis Enterprise CRDT-based active-active for conflict-free multi-region writes.
- **Backups**:
  - Ship RDB snapshots to durable storage (e.g., object store) on schedule.
  - Optionally ship AOF for tighter recovery points.
  - Regularly test restore into isolated env.

---

## Monitoring and alerts

- **Replication**: `master_link_status`, `slave_repl_offset`, `master_repl_offset`, `sync_partial_ok`.
- **Lag**: `slave_read_repl_offset` differences; custom heartbeat key TTLs.
- **Persistence**: `aof_current_size`, `aof_last_write_status`, `rdb_last_save_time`, `rdb_last_bgsave_status`.
- **Sentinel/Cluster**: state changes, failovers, flapping detection.
- **System**: CPU steal, disk latency, network drops, memory fragmentation (`mem_fragmentation_ratio`).

---

## Rolling upgrades with no/low downtime

- Add a new replica with the desired version/config.
- Wait to sync and warm.
- Promote replica (Sentinel/Cluster or manual `SLAVEOF NO ONE`).
- Repoint old primary as replica, drain, then remove.

---

## Reference configurations

### Balanced (most common)

```conf
# Durability
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
no-appendfsync-on-rewrite yes
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes

# Replication
replication-backlog-size 128mb
repl-diskless-sync yes
repl-diskless-sync-delay 5
min-replicas-to-write 1
min-replicas-max-lag 5
replica-read-only yes
client-output-buffer-limit replica 512mb 128mb 60

# Memory / eviction
maxmemory-policy allkeys-lru
```

### Maximum durability (accept higher latency)

```conf
appendonly yes
appendfsync always
no-appendfsync-on-rewrite no
stop-writes-on-bgsave-error yes
save ""          # Optional: disable RDB if AOF-always is sufficient
min-replicas-to-write 2
min-replicas-max-lag 2
```

### Low latency (best-effort durability)

```conf
appendonly yes
appendfsync everysec
save 900 1
save 300 10
repl-diskless-sync yes
min-replicas-to-write 0
```

### Sentinel example (3 Sentinels)

```conf
# sentinel.conf on each Sentinel node
port 26379
sentinel monitor mymaster 10.0.0.10 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
```

---

## Quick checklist

- **RPO target** chosen and enforced via `appendfsync` and `WAIT`/`min-replicas-to-write`.
- **At least 1–2 replicas** across different AZs.
- **Automatic failover** with Sentinel or Cluster; odd number of voters.
- **Persistence** enabled (AOF everysec or always; optionally RDB).
- **Backups** scheduled and restore-tested.
- **Monitoring** on replication, persistence, failovers, and resource health.
- **Client strategy**: retry with backoff, idempotency, cluster-aware if needed.

---

### Practical patterns to reduce data loss

- After critical write batches, issue `WAIT` for 1–2 replicas with a small timeout.
- Keep AOF enabled on replicas too, not just the primary.
- Use `min-replicas-to-write` to shed write traffic when replicas are lagging.
- Prefer managed Multi-AZ services for production unless you need custom control.
