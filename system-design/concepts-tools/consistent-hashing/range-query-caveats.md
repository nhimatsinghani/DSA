## Range queries and consistent hashing: caveats and examples

Consistent hashing optimizes for uniform distribution and minimal data movement during scaling, not for ordered access. As a result, it tends to harm range-scan workloads compared to range-based sharding.

### Why performance can drop for range scans

- **Key scattering**: Hashing destroys key locality. Keys that are adjacent in natural order are spread across many shards. A single range query (e.g., `user_id in [1000, 2000]` or `timestamp in last 10min`) touches many shards.
- **Fan-out and coordination**: The query must be sent to every shard that might contain a matching key. That increases RPC fan-out, coordination overhead, and tail latency (you wait for the slowest shard or need speculative retries).
- **I/O amplification**: Each shard may perform small, partial scans, causing many short seeks instead of one contiguous range scan. Cache locality diminishes, increasing I/O per result.
- **Result merging**: Results come back out of order and must be merged/sorted at the coordinator, adding CPU and memory pressure.

### Concrete example: time-series reads

- **Workload**: “Give me all events for `device_id = D` between 12:00–12:05.”
- **Range-based sharding**: If you shard by time ranges (or partition by day/hour), all relevant rows reside on one or a small number of shards. One sequential read per shard; low fan-out.
- **Consistent-hash sharding by (device_id, timestamp)**: If the partition key is `hash(device_id)` only, events for the time window are spread across most shards. The coordinator must query many shards, increasing tail latency. If the partition key is `hash(device_id, bucket(timestamp))`, you reduce fan-out but still lose fine-grained locality within the bucket.

### Concrete example: leaderboards and sorted sets

- **Workload**: “Top N users by score between 1000 and 2000.”
- **Range-based sharding**: Store by score ranges; one shard (or a small set) can answer via a contiguous scan.
- **Consistent hashing by user_id**: Users with scores in the target range are scattered. You must query many shards and merge-sort partially ordered results, which is slower and more expensive.

### Typical mitigations

- **Compound partitioning with bucketing**: Use a hash of a stable dimension to balance load and a coarse time/score bucket to limit fan-out. Example key: `(hash(user_id), day)` or `(hash(metric), hour)`. This preserves balance while bounding the number of shards per query.
- **Secondary indexes per shard**: Keep local order (e.g., by timestamp) within each shard. You still fan out, but each shard can serve sorted slices efficiently. Use a coordinator to merge.
- **Directory/metadata routing**: Maintain a metadata service that maps a specific range to a small subset of shards (micro-shards). The application first consults metadata to avoid full fan-out.
- **Hybrid layout**: Hot-write path uses consistent hashing; a background job creates range-optimized projections (e.g., time-partitioned files in object storage) for analytics and large scans.
- **Time-windowed salt**: For hot keys, add a small salt or bucket per time window to spread writes but keep a bounded set of target shards for range reads.

### When consistent hashing is still a good fit

- High-throughput point lookups and key-value access dominate
- Write load is skewed or bursty (avoids hot partitions)
- Low-churn scaling and partial rebalancing are critical

### When to prefer range-based sharding (or hybrids)

- Range scans are first-class (time-series analytics, ordered leaderboards)
- Queries often filter by a monotonic attribute (time, sequence ID, score)
- You can tolerate periodic rebalancing and have tools to migrate ranges

### Quick rule of thumb

- If your primary access pattern is point lookups by key, choose consistent hashing (+ vnodes, replication).
- If your primary access pattern is range scans/sorting, choose range-based sharding or a hybrid: hash for writes, project for reads.
