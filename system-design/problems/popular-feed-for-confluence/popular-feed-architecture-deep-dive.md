# Popular Feed Architecture Deep Dive — Alternatives and Tradeoffs

This doc explores multiple architecture options for building a popular feed (ranked by likes, views, or composite signals) and compares their pros/cons, operational complexity, consistency, latency, and cost. The baseline approach in `popular-feed-architecture.md` uses Postgres as system-of-record, an outbox + stream aggregator, and Redis ZSET leaderboards with SSE refresh. Below are alternative designs and when to pick each.

---

## Problem recap and evaluation criteria

- Functional: rank pages by metrics (likes, views, comments, composite) over windows (1h/24h/7d/30d), filter by tenant/space/project, enforce AuthZ, return hydrated summaries, incremental refresh.
- Non-functional: p95 latency <= 150 ms at 99% availability, fresh within <= 2–5 seconds for likes, <= 10–60 seconds for views (higher volume), read-heavy R/W imbalance, multi-tenant isolation, cost efficiency.
- Evaluation axes:
  - Consistency model (eventual vs read-your-writes)
  - Freshness (seconds-minutes) and drift under backpressure
  - Read latency and tail behavior
  - Write amplification and hot-spot risk
  - Multi-window maintenance cost (1h/24h/7d/30d...)
  - Filtering and AuthZ overhead
  - Operational complexity and cost

---

## 1) DB-only ranking (naive SQL)

How it works:

- Writes land in relational `page_likes`, `page_views` (or materialized counters). Reads compute top-N via ORDER BY COUNT(\*) DESC with WHERE window AND scope filters, possibly using indexes/materialized views.

Pros:

- Simple; strong consistency post-commit. Cheap at very low scale.

Cons:

- Poor latency at scale; expensive GROUP BY/ORDER BY. Index explosion for many windows/scopes.
- DB saturation and lock contention under spikes.

When to use:

- Very small scale/internal tools.

---

## 2) Redis ZSET leaderboards (baseline)

How it works:

- Postgres is system-of-record. Outbox events consumed by a stream processor which updates Redis ZSETs per (tenant, scope, window, metric). Reads pull top-N, apply AuthZ, hydrate summaries.

Pros:

- Excellent read latency; ZSET ideal for top-K. Simple pagination/overfetch.
- Moderate complexity once event flow exists. Cost-effective if trimming.

Cons:

- Full ZSETs are memory-heavy; must trim or compact. Write amplification across windows/metrics.
- Eventual consistency; toggle conflicts to handle.

When to use:

- Read-heavy workloads with modest per-event updates or sampled views.

Design notes:

- Sample/batch high-volume metrics like views.
- Use time-bucket counters + periodic recompute for large windows.

---

## 3) Wide-column counters (Cassandra/Scylla) + periodic top-K compaction

How it works:

- Store per-page counters in a write-optimized store (partitioned by tenant/scope/window or time buckets). Periodic jobs compute top-K and publish to Redis (or serve from Cassandra partitions).

Pros:

- Very high write throughput; durable counters. Redis as thin cache.

Cons:

- Reads slower than Redis; compaction and rollups add complexity.

When to use:

- Very high write rates (views) and large multi-tenant footprint.

---

## 4) Streaming materialization (Kafka + Flink/Spark + RocksDB state)

How it works:

- Events on Kafka; keyed operators keep aggregates in RocksDB state. Top-K per segment via heavy-hitter algorithms (Space-Saving). Sink to Redis/KV.

Pros:

- Highly scalable; windowing, late data, exactly-once possible.

Cons:

- Operationally heavy: checkpoints, state, replays.

When to use:

- Large-scale, multi-window, multi-tenant with strict bounds on memory.

---

## 5) OLAP store (ClickHouse/Pinot/Druid) for serving

How it works:

- Ingest events; use materialized views/rollups. Serve GROUP BY queries with low latency.

Pros:

- Powerful ad-hoc queries, flexible filters, near-real-time ingestion.

Cons:

- Tail latency higher than Redis; tuning needed for strict SLAs.

When to use:

- Many dynamic filters/windows beyond precomputable leaderboards.

---

## 6) Search engine ranking (Elasticsearch/OpenSearch function_score)

How it works:

- Index pages with counters/freshness signals. Query with function_score combining likes, views, recency, filters.

Pros:

- Flexible scoring and filtering; good for search + popularity.

Cons:

- Index write load; refresh delay; exact top-K semantics are trickier.

When to use:

- Discovery/search-led experiences.

---

## 7) Batch snapshots + CDN

How it works:

- Offline jobs compute top-K (e.g., hourly) per segment, write JSON snapshots to object storage, serve via CDN. API reads snapshot + deltas.

Pros:

- Very cheap at scale; excellent global latency via CDN.

Cons:

- Coarse freshness unless paired with real-time deltas. Merge complexity.

When to use:

- Massive read fanout with freshness tolerance in minutes.

---

## 8) Materialized view databases (Materialize etc.)

How it works:

- Define SQL materialized views over streams; system maintains them incrementally. Serve directly or replicate to Redis.

Pros:

- SQL-first semantics; simplifies windowing/joins.

Cons:

- Operational maturity/cost vary; careful partitioning required.

When to use:

- SQL-centric teams; moderate to high scale.

---

## 9) Time-decay and windowing strategies

Options:

- Separate ZSET per window (1h/24h/7d/30d) with trimming.
- Exponential decay score: score = likes*w1 + views*w2 + exp(-lambda\*age).
- Time-bucket counters (minute/hour buckets) with periodic rollup of last N buckets.

Tradeoffs:

- Separate ZSETs: simple reads, higher write amp; bounded memory if trimmed.
- Decay: single structure; harder to reason exact windows, tunable freshness.
- Buckets: reduces per-event writes; periodic recompute.

---

## 10) Realtime delivery patterns

- Polling: simplest; higher client/network cost; OK with TTL >= 30-60s.
- Long polling: fewer redundant fetches; more stateful servers.
- SSE: uni-directional; proxy-friendly; great for version bumps.
- WebSockets: bi-directional; costlier; needed if client writes/acks.

---

## 11) AuthZ strategies for leaderboards

- Fetch then filter: overfetch top-50/100, batch AuthZ, return allowed top-N.
- Segmented leaderboards: per-tenant/space/project keys reduce filtering.
- Hybrid: global top-K + per-segment overlays; backfill when filtered out.

Tradeoffs:

- Filtering adds latency; overfetch factor grows with tighter permissions.
- Segmentation multiplies keys and write amp; control combinatorics.

---

## 12) ML ranking + feature store

- Combine popularity with recency/content/creator features; online scoring with a feature store and Redis feature cache.

Pros: better engagement. Cons: significantly higher complexity/cost.

---

## Choosing the right approach

- Low scale/internal: DB-only or snapshots.
- Read-heavy, moderate writes, tight latency: Redis ZSET + stream aggregator (baseline).
- Very high write rates: counters in Cassandra + periodic top-K -> Redis.
- Many dynamic filters/windows or analytics: OLAP or materialized views.
- Search-led discovery: Elasticsearch function_score.
- Extreme read fanout, loose freshness: snapshots + CDN with deltas.

---

## Migration path (progressive hardening)

1. Start with baseline (Redis ZSET + outbox + aggregator).
2. Add time-bucket counters and top-K compaction to curb write/memory.
3. Add segmented leaderboards for hot filters; keep global + overlays.
4. For very high writes, shift raw counters to Cassandra and compute top-K in stream.
5. For advanced analytics/filters, add OLAP or materialized views.
6. Optional: hybrid ML scorer once signals and experimentation exist.

---

## Cost and ops snapshot (qualitative)

- Lowest cost/ops: snapshots + CDN, DB-only (tiny scale), Redis baseline (bounded keys, trimmed).
- Medium: Elasticsearch, OLAP serving, materialized views.
- Highest: full streaming with heavy-hitter algorithms, per-segment ZSETs at large multi-tenancy, ML ranking.

---

References

- Baseline: `popular-feed-architecture.md`
- Capacity: `popular-feed-capacity-estimation.md`
