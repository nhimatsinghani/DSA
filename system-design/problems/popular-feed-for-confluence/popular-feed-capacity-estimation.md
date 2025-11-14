# Popular Feed Capacity Estimation

This doc estimates capacity for the popular feed and highlights how scale impacts architectural choices.

---

## 1) Definitions and inputs

- Tenants (T), Pages per tenant (P_t), Active pages in window (A): pages that received at least 1 event in window.
- Metrics: likes (toggle), views (high-volume), comments (optional), composite score.
- Windows: 1h, 24h, 7d, 30d (W variants); sometimes exponential decay instead.
- Segmentation: tenant, space/project; assume S segments per tenant included in feed.
- Leaderboards kept: K entries per key (trimmed), overfetch factor F for AuthZ (e.g., 2x-3x).
- Read page size: N (e.g., 20), pagination up to M pages.
- Realtime: SSE clients (C_sse) connected concurrently.

We will estimate: write/update rate to aggregators, Redis ops/sec and memory, event bus throughput, database load, and network.

---

## 2) Formulas

- Events per second (global): E_like, E_view. Total E = E_like + E_view.
- Updates per event to leaderboards:
  - Separate windows: U*per_event = (#metrics updated) * (#windows W) \_ (#segments per page S_p).
  - With time buckets + periodic recompute: per-event updates drop; batch job cost rises.
- Aggregator RPS: R_agg = E \* U_per_event (if direct ZINCRBY) or R_agg << E if batching.
- Redis ops/sec (writes): roughly R_redis_w = R_agg (ZINCRBY/ ZADD) + trimming/expiry.
- Redis ops/sec (reads): R_redis_r ≈ Q_feed \* F_overfetch, where Q_feed is feed QPS.
- Leaderboard keys: L = T _ S _ W \* M_metrics.
- Memory per leaderboard: if trimmed to K, approximate ZSET memory ~ 200–300 bytes per entry (member + score + skiplist + dict; varies by Redis version and member length). Use 250 bytes as a rough median.
  - Mem*per_LB ≈ K * 250 bytes; Total ≈ L \_ K \* 250 bytes.
- SSE fanout: Outbound messages/sec ≈ distinct leaderboard versions/sec \* subscribers per key. With coalescing, use per-version broadcast.
- Kafka throughput: bytes/sec ≈ E \* avg_event_bytes (e.g., 200B–500B) + replication factor overhead.

---

## 3) Example scenarios

Assumptions common across scenarios unless stated:

- Windows W=4 (1h/24h/7d/30d), Metrics=2 (likes, views), S=2 segments (tenant + space), K=1000, F=2.5, N=20, M=5 pages.
- Avg event bytes 300B; Kafka RF=3.
- Overfetch factor rises with stricter AuthZ (assume 2.5x baseline).

### Small

- Tenants T=100, Active pages in window A=50k, Q_feed=100 QPS.
- E_like=5/s, E_view=500/s (sampled 1/10 => 50/s effective). E=55/s.
- U*per_event = 2 metrics * 4 windows \_ 2 segments = 16.
- R_agg ≈ 55 \* 16 ≈ 880 ops/s (ZINCRBY).
- Redis writes ≈ 880 ops/s; reads ≈ 100 \* 2.5 = 250 ops/s.
- Leaderboards L = 100 _ 2 _ 4 \* 2 = 1600 keys.
- Memory ≈ 1600 _ 1000 _ 250B ≈ 400 MB (plus overhead, say ~1 GB incl. metadata/replica).
- Kafka ingress ≈ 55 _ 300B _ RF3 ≈ ~50 KB/s.

Observations: single Redis node or small cluster suffices; baseline design is fine.

### Medium

- T=1000, A=1M, Q_feed=2000 QPS.
- E_like=100/s, E_view=10k/s (sampled 1/20 => 500/s). E=600/s.
- U_per_event = 16 => R_agg ≈ 9600 ops/s.
- Redis writes ≈ 9.6k ops/s; reads ≈ 2000 \* 2.5 = 5k ops/s.
- L = 1000 _ 2 _ 4 \* 2 = 16k keys.
- Memory ≈ 16k _ 1000 _ 250B ≈ 4 GB (estimate 8–10 GB incl. overhead/replication).
- Kafka ingress ≈ 600 _ 300B _ RF3 ≈ ~540 KB/s.

Observations: shard Redis (e.g., 3–6 shards). Add batching/async pipelines in aggregator. Consider time-buckets for 7d/30d to reduce write amp.

### Large

- T=10k, A=50M, Q_feed=20k QPS.
- E_like=1k/s, E_view=100k/s (sampled 1/50 => 2k/s). E=3k/s.
- U_per_event = 16 => R_agg ≈ 48k ops/s (direct). With batching (100ms), effective ≈ 10–20k ops/s.
- Redis writes 20–50k ops/s; reads ≈ 20k \* 2.5 = 50k ops/s.
- L = 10k _ 2 _ 4 \* 2 = 160k keys.
- Memory ≈ 160k _ 1000 _ 250B ≈ 40 GB (estimate 80–100 GB incl. overhead/replication).
- Kafka ingress ≈ 3000 _ 300B _ RF3 ≈ ~2.7 MB/s.

Observations: multi-shard Redis (10–20 shards). Strongly consider moving raw counters to Cassandra and computing top-K in stream (or materialized OLAP) to curb write amp and memory. Use heavy-hitter algorithms, per-key trimming, and compacted time buckets.

---

## 4) Postgres load

- OLTP writes: toggling likes is cheap with proper PK/unique indexes. Expect write QPS ~ E_like with transaction latency < 10 ms at moderate scale.
- Avoid views-as-writes in OLTP; use outbox for reliability. Partition large tables by tenant/time where needed.

---

## 5) Network and SSE

- SSE connections: C_sse concurrent; assume 40 KB per idle connection (HTTP/TCP state) and occasional bursts on version bump. For 50k clients, plan a few GB of server memory and horizontal scaling behind an ELB/NGINX.
- Version topics per leaderboard reduce broadcast; clients fetch /delta to limit payload.

---

## 6) Latency targets and budgets

- Read path: Redis 1–5 ms, AuthZ batch 10–30 ms, summaries 5–20 ms, network 20–50 ms => p95 ~ 80–120 ms if caches are warm.
- Write freshness: outbox->bus<50 ms, consumer<100 ms, Redis update<20 ms => end-to-end freshness 0.2–0.5 s under normal load.

---

## 7) Design implications by scale

- Small: Baseline (Redis ZSET) with trimming and modest shards; sampling for views; SSE optional.
- Medium: Introduce time-bucket counters for long windows; batch/pipeline writes; shard Redis; backpressure on aggregator.
- Large: Store raw counters in Cassandra/Scylla; compute top-K via stream processing (heavy-hitters) and publish to Redis. Consider OLAP for flexible filters. Tighten AuthZ overfetch with more segmentation to avoid filtering waste.

---

## 8) Capacity risk checklist

- Key explosion from combinatoric segments (tenant x space x window x metric).
- Hot keys during spikes (celebrity pages): enable client-side hashing and key distribution.
- Memory blow-up: always trim to K and expire old windows; snapshot and compact.
- Overfetch amplification due to AuthZ: monitor allowed ratio; adapt overfetch.
- Backfill lag: ensure ability to read beyond top-K to fill pages after filtering.
- Replay/backfill safety: idempotent updates, deterministic toggles, versioning.

---

## 9) What to measure in production

- Aggregator lag and throughput, Kafka consumer lag.
- Redis per-shard ops/sec, p99 latency, memory/headroom, evictions.
- Allowed ratio after AuthZ; overfetch factor used.
- Read latency broken down by Redis, AuthZ, summary fetch; cache hit rates.
- Freshness: time from event to visible rank update.

---

## 10) TL;DR

- If E and L are small-to-medium, trimmed ZSET leaderboards are the simplest and cheapest.
- If E_view dominates and grows large, move raw counters to a write-optimized store and compute top-K in stream or batch, publishing only K entries per key to Redis.
- If filters and windows explode, consider OLAP/materialized views for serving (with caching), accepting a higher tail latency.
