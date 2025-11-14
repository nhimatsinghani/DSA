## Postgres Write Scaling: Deep Dive (Partitioning, Sharding, and NoSQL Comparison)

### TL;DR

- **Start** with single-node optimizations (indexes, batching, WAL/FS tuning, connection pooling).
- **Use native partitioning** to reduce write/index contention and improve maintenance; it scales within one node.
- **Scale reads** with replicas; does not increase write capacity.
- **Scale writes horizontally** with sharding (application-layer, Citus, FDW-based), accepting cross-shard trade-offs.
- **Cassandra/DynamoDB scale writes more easily** because they are built for partitioned, eventually-consistent, non-transactional workloads using LSM trees and consistent hashing. Postgres offers richer semantics but requires design work to shard safely.

---

## 1) Foundations: How Postgres handles writes

Understanding the write path clarifies what limits throughput and how each strategy helps.

- **WAL-first durable log**: Every commit must append to the Write-Ahead Log (WAL) and fsync based on `synchronous_commit`. This ensures durability but adds latency.
- **Index maintenance**: Each insert/update must update relevant indexes. Many or wide indexes make writes slower; hotspots form on index pages.
- **Row versioning (MVCC)**: Updates create new row versions; dead tuples require vacuuming. Heavy-write tables need healthy autovacuum.
- **Locking and contention**: Sequences, hot pages, and constraints can create contention. Connection spikes hurt.
- **I/O characteristics**: B-Tree updates and random I/O; SSDs help; LSM-like systems (Cassandra/DynamoDB) are more sequential on write.

Implications:

- Reduce per-row work (few indexes, smaller rows, batch writes).
- Spread writes to reduce page/sequence hotspots.
- Keep vacuum ahead of dead tuples; set `autovacuum_*` appropriately.
- Use connection pooling (PgBouncer) to cap concurrent sessions.

---

## 2) Scaling axes for writes

1. **Vertical (scale-up)**: Bigger box, faster storage, more RAM/CPU. Easiest, often cheapest up to a point.
2. **Intra-node scale-out via partitioning**: Multiple partitions inside one database instance. Helps concurrency, index size, vacuum, and maintenance windows; total write cap still bounded by a single node.
3. **Inter-node scale-out via sharding**: Data split across multiple nodes. Raises total write ceiling at the cost of distributed-systems complexity.

You can and often should combine these (e.g., partition first, then shard by tenant).

---

## 3) Native table partitioning in Postgres

Postgres supports declarative partitioning: `RANGE`, `LIST`, `HASH`. Typical goals:

- **Insert throughput and concurrency**: Partition pruning reduces index bloat per partition; concurrent inserts land on different child tables.
- **Operational efficiency**: Partition-local maintenance (reindex, vacuum), and fast drop/attach for archival.
- **Query performance**: Partition pruning reduces scanned data.

Common schemes:

- **Time-based RANGE**: e.g., daily or hourly partitions for event logs, metrics. Simplest operationally; pair with retention.
- **LIST by tenant/account**: Good for multi-tenant isolation when tenant count is modest.
- **HASH**: Evenly spreads writes when no natural range exists. Useful to avoid single-partition hotspots.
- **Composite**: e.g., LIST(tenant) → RANGE(time) within each tenant; or HASH(user_id) → RANGE(time).

Partitioning best practices:

- Choose partition granularity so each child stays in the tens of GBs (operational sweet spot varies by infra).
- Keep only necessary indexes on hot partitions; create broader indexes on colder partitions if needed.
- Use `UNLOGGED` tables for transient staging (not durable across crash/replica).
- Automate creation/attach/drop using schedulers or extensions (e.g., `pg_partman`).
- Watch `autovacuum` and `freeze` settings per partition; adjust `fillfactor` to reduce page splits on hot writes.

When to use partitioning:

- Single-node still viable but you need higher write concurrency, smaller indexes, or easier maintenance.
- Time-series/event workloads that age out.
- You want prune-friendly queries and operational lifecycle management.

Limitations:

- Does not exceed single-node WAL/CPU/IO limits.
- Cross-partition unique constraints and foreign keys are limited; per-partition constraints are straightforward, global ones are not.

---

## 4) Sharding Postgres (horizontal write scaling across nodes)

Sharding splits data across multiple servers to increase aggregate write capacity. Trade-offs: cross-shard joins, transactions, and global constraints become hard.

Key design choices:

- **Shard key**: Pick a column/set used on nearly all writes/reads. It must distribute load and support locality. Common: `tenant_id`, `user_id`, or composite `(tenant_id, time_bucket)`.
- **Routing**: Client library/service maps shard key → shard. Use consistent hashing with many virtual shards to enable rebalancing.
- **Co-location**: Co-locate related data using same shard key to avoid cross-shard joins.
- **Global objects**: Small reference tables can be replicated to all shards.

Approaches:

1. **Application-layer sharding (DIY)**

- You run N independent Postgres clusters. The app routes queries based on the shard key.
- Pros: Maximum control, simplest runtime dependencies, easy to apply per-shard tuning. No single distributed query planner.
- Cons: Cross-shard queries/transactions are on you; migrations and rebalancing require orchestration.

2. **Citus (distributed Postgres)**

- Citus distributes tables by a shard key, manages placement, co-location, rebalancing, and provides distributed SQL (coordinator + workers).
- Pros: Mature, operational tooling, colocated joins, reference tables, rebalance, good for multi-tenant and time-series.
- Cons: Not every Postgres feature works identically in distributed context; cross-shard transactions and global constraints have caveats.

3. **FDW-based federation (postgres_fdw)**

- A central node uses foreign tables to reach per-tenant/per-shard Postgres instances.
- Pros: Leverages core Postgres, simple to prototype, can emulate a single logical view.
- Cons: Planner is not a full distributed optimizer; performance and transactional guarantees across servers are limited.

4. Other ecosystems (evaluate carefully)

- Postgres-XL/PGXC, Babelfish-compatible clusters, logical replication topologies, or vendor-specific offerings. Check maturity/operational story.

Cross-shard concerns and patterns:

- **Transactions**: Avoid multi-shard write transactions. Prefer per-shard ACID with application-level Sagas/outbox for cross-entity workflows.
- **Uniqueness**: No native global unique index. Enforce uniqueness within shard key; for truly global uniqueness, use IDs like Snowflake/ULID and check in a dedicated authority service.
- **Secondary indexes**: Local to shard. Global search/analytics go to separate systems (Elasticsearch, OLAP warehouse).
- **Rebalancing**: Use virtual shards (e.g., 1024 buckets). Move buckets between nodes online using logical replication or Citus rebalance.
- **Backfills**: Write-ahead dual-write or “shadow traffic” approach; verify, then cut over.

When to shard:

- Write throughput or storage exceeds a single node even after vertical scale and partitioning.
- Tenant isolation/SLOs demand siloing noisy neighbors.
- Regulatory or geographic placement requires data residency per region.

Costs of sharding:

- Application complexity, operational tooling, more failure modes.
- Loss of simple global constraints/joins; analytical queries require aggregation layer.

---

## 5) Operational tuning for high write rates (pre-sharding)

- **Connection pooling**: PgBouncer in transaction mode; keep active connections modest (e.g., 100–300 per node depending on hardware).
- **Index hygiene**: Minimize indexes on hot tables; defer or create concurrently on cold data. Prefer covering partial indexes for common predicates.
- **Batching**: Use multi-row `INSERT`, `COPY`, or `COPY FREEZE` for bulk loads; group small writes.
- **WAL and sync**: Consider `synchronous_commit = off` for non-critical writes; place WAL on fast disks; ensure good `wal_buffers`, `checkpoint_timeout`, and `max_wal_size`.
- **Autovacuum**: Increase workers and thresholds for hot tables; adjust `freeze_min_age` only with care. Monitor bloat.
- **Fillfactor**: Lower on hot update tables to reduce page splits; consider `HOT` updates (update columns that are not indexed).
- **Sequences/IDs**: Use `bigint`, enable sequence `CACHE` to reduce contention; consider client-side IDs (ULID/Snowflake).
- **Avoid hot single rows**: Use counters with CRDT/outbox/queue patterns instead of updating the same row.

---

## 6) Partitioning vs Sharding: What to use when

Use this decision guide:

- If a bigger box still fits budget and removes pressure → **Vertical scale**.
- If you need easier maintenance, smaller indexes, predictable lifecycles, and your total write volume fits one node → **Partition**.
- If reads are the issue, not writes → **Replicas** (understand replica lag for read-your-writes).
- If a single node cannot keep up with sustained writes even after partitioning/tuning → **Shard**.
- If most access is tenant-scoped and cross-tenant joins are rare → **Shard by tenant** (possibly plus time partitioning per shard).
- If workload is pure time-series/logs with massive ingest and simple queries → Consider **Citus distributed, Timescale (partitioning + compression), or move warm/cold tiers to OLAP**.

Pros and cons summary:

Partitioning (intra-node)

- Pros: Simpler than sharding; better maintenance; partition pruning; hot partitions smaller; easy archival.
- Cons: Still one-node write ceiling; limited global constraints across partitions.

Sharding (inter-node)

- Pros: Linear-ish write scale-out; failure blast radius smaller; per-tenant isolation.
- Cons: Harder joins/transactions; global uniqueness/constraints absent; heavier ops.

---

## 7) Why Cassandra/DynamoDB are easier to scale for writes (and comparison)

Design choices in NoSQL systems make write scaling straightforward:

- **Always-partitioned data model**: A mandatory partition (hash) key maps items to nodes; data is spread by design.
- **Consistent hashing + virtual nodes**: Smooth distribution and painless rebalancing by moving token ranges.
- **LSM-tree storage engines**: Writes are sequential (memtable + WAL → SSTables), making sustained high write throughput easier than B-Tree updates.
- **Tunable consistency / eventual consistency**: Avoid distributed transactions; choose consistency per request (e.g., QUORUM). Conflicts are managed with last-write-wins or app reconciliation.
- **Limited cross-partition features**: Joins, multi-item transactions, and global secondary indexes are constrained or absent. This reduces coordination and unlocks scale.

Comparison to Postgres sharding:

- Postgres provides rich SQL, ACID transactions, complex joins, referential integrity. Once sharded, you must emulate many of these across nodes (or accept limits). That added coordination limits easy linear scaling.
- NoSQL systems trade those features for predictable partitioned writes, fewer coordination points, and storage engines optimized for ingest.

When to prefer NoSQL for writes:

- Very high, sustained ingest where strict relational features are not needed.
- Access patterns fit single-partition lookups with narrow queries.
- You can model data to avoid cross-partition operations and accept eventual consistency or limited transactions.

---

## 8) Practical sharding recipes for Postgres

- **Tenant sharding + reference tables**: Distribute tenant-scoped tables by `tenant_id`. Replicate small lookup tables to all shards. Enforce uniqueness per tenant, not globally.
- **Time + hash composite**: For event streams, hash on `entity_id` to avoid hotspots and range on time within shard for pruning and lifecycle.
- **Write fan-in buffer**: Accept writes to a queue/outbox per shard; workers batch into the main tables to reduce per-row overhead.
- **Virtual shards (buckets)**: Pre-create many buckets; map bucket → physical shard. Rebalance by remapping buckets, not by splitting large physical tables.
- **Online re-sharding**: Dual-write during move, use logical replication, validate checksums/counts, then cut over with a short lock.

---

## 9) Migration and rebalancing checklist

1. Define shard key and validate distribution on real data (cardinality, skew, hotspot risk).
2. Introduce virtual bucket layer; store bucket in tables for traceability.
3. Build routing library/service; add observability (per-bucket QPS/latency/errors).
4. Make cross-tenant queries go through analytics/OLAP or search; duplicate small reference data.
5. Implement outbox/Saga for multi-entity workflows; avoid cross-shard TX.
6. Plan online move playbook: dual-write, backfill, verify, promote, deprecate.
7. Test failure modes (partial outage, replica lag, split brain) and rate limits.

---

## 10) Quick reference tables

When to use what

| Situation                            | Best-first action                               |
| ------------------------------------ | ----------------------------------------------- |
| Moderate write pressure; one node OK | Vertical scale + tuning                         |
| Large hot table, maintenance pain    | Partitioning                                    |
| Read-heavy with some lag OK          | Read replicas                                   |
| Sustained writes exceed one node     | Sharding (DIY or Citus)                         |
| Massive time-series ingest           | Partitioning + compression (Timescale) or Citus |
| Global queries/analytics             | OLAP warehouse or search index                  |

Sharding options

| Option             | Pros                                             | Cons                                    |
| ------------------ | ------------------------------------------------ | --------------------------------------- |
| App-layer sharding | Full control, simple runtime                     | Cross-shard ops are manual              |
| Citus              | Managed distribution, colocated joins, rebalance | Feature caveats, coordinator dependency |
| postgres_fdw       | Easy to start, single logical view               | Limited optimizer, weaker TX semantics  |

---

## 11) Final guidance

1. Exhaust single-node optimizations and partitioning first.
2. If write ceiling remains, choose a shard key that matches access patterns and isolate tenants/entities.
3. Prefer colocated operations; push cross-entity analytics to OLAP systems.
4. If the workload is naturally partitioned and relational guarantees are not required, evaluate Cassandra/DynamoDB for simpler write scaling.

This approach preserves Postgres strengths where they matter and introduces sharding only when it offers clear, material benefit.
