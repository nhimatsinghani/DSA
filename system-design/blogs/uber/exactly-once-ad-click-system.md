Source : https://www.uber.com/en-IN/blog/real-time-exactly-once-ad-event-processing/

Exactly-Once
As mentioned above, a primary constraint that we’re working with is requiring exactly-once semantics across the system. It is one of the hardest problems in distributed systems, but we were able to solve it through a combination of efforts.

First, we rely on the exactly-once configuration in Flink and Kafka to ensure that any messages processed through Flink and sunk to Kafka are done so transactionally. Flink uses a KafkaConsumer with “read_committed” mode enabled, where it will only read transactional messages. This feature was enabled at Uber as a direct result of the work discussed in this blog. Secondly, we generate unique identifiers for every record produced by the Aggregation job which will be detailed below. The identifiers are used for idempotency and deduplication purposes in the downstream consumers.

The first Flink job, Aggregation, consumes raw events from Kafka and aggregates them into buckets by minute. This is done by truncating a timestamp field of the message to a minute and using it as a part of the composite key along with the ad identifier. At this step, we also generate a random unique identifier (record UUID) for every aggregated result.

Every minute the tumbling window triggers sending aggregated results to a Kafka sink in an “uncommitted” state until the next Flink checkpoint triggers. When the next checkpointing triggers (every 2 minutes), the messages are converted to the “committed” state using the two-phase commit protocol. This ensures that Kafka read-offsets stored in the checkpoint are always in line with the committed messages.

Consumers of the Kafka topic (e.g., Ad Budget Service and Union & Load Job) are configured to read committed events only. This means that all uncommitted events that could be caused by Flink failures are ignored. So when Flink recovers, it re-processes them again, generates new aggregation results, commits them to Kafka, and then they become available to the consumers for processing.

A record UUID is used as an idempotency key in ad-budget service. For Hive it is used as an identifier for deduplication purposes. In Pinot, we leverage the upsert feature to ensure that we never duplicate records with the same identifier.

---

Deep Dive: How "Exactly-Once" Is Achieved (with examples)

At a high level, Uber combines three mechanisms to deliver end-to-end exactly-once semantics from raw click events to downstream consumers and stores:

1. Transactional processing and sinks in Flink coordinated by checkpoints (two-phase commit).
2. Kafka transactional topics with producers using transactional IDs, and consumers configured with `isolation.level=read_committed`.
3. A stable, per-record identifier (record UUID) that downstream services use for idempotency and deduplication.

Putting these together prevents duplicates and gaps from being observed by consumers in both normal operation and across failures.

What happens each minute

- Aggregation job windows events into 1-minute buckets by (minute(ad_timestamp), ad_id).
- For each bucket, it computes aggregates (e.g., impressions=100, clicks=7) and prepares a message like:

  {"bucket_minute":"2024-05-01T12:34:00Z","ad_id":"A42","impressions":100,"clicks":7,"record_uuid":"b7c9..."}

- These aggregated results are written to a Kafka topic transactionally. Until a Flink checkpoint completes, all produced messages remain "uncommitted" in Kafka.
- On checkpoint (every 2 minutes here), Flink executes a two-phase commit:
  - Pre-commit: all aggregator operators flush their pending transactional writes
  - Commit: Flink atomically persists source offsets + operator state and commits the Kafka transactions
- Because commit of offsets and commit of output happen together, recovery never reprocesses already-committed input without also having the corresponding outputs already committed.

Why read_committed matters

- Consumers like Ad Budget Service and the Union & Load job subscribe with `read_committed`.
- This hides any uncommitted transactional messages. So if Flink crashes mid-window, partially produced results are invisible; consumers only see committed, checkpoint-aligned state.

Role of record UUID

- Each aggregated output carries a unique `record_uuid`.
- Downstream systems use it as an idempotency key:
  - Ad Budget Service: ignores repeats with the same UUID
  - Hive: de-duplicates by UUID when ingesting
  - Pinot: uses upsert keyed by UUID, so the latest write replaces any prior one

End-to-end example timeline

Assume 2-minute checkpoints and 1-minute tumbling windows.

T=12:00:00–12:00:59

- Aggregation window [12:00 minute] collecting events for ad_id=A42.
  T=12:01:00
- Window fires; Flink writes aggregated record for [12:00, A42] into Kafka within TXN #123, but leaves it uncommitted.
  T=12:02:00 (checkpoint)
- Flink checkpoint succeeds; it commits TXN #123 and persists source offsets. Now consumers with `read_committed` see the [12:00, A42] aggregate exactly once.

If a failure happens before the commit

- Crash at T=12:01:30 after writing to Kafka but before checkpoint.
- Kafka holds the messages as uncommitted → consumers with `read_committed` do not see them.
- Flink restarts from the last successful checkpoint (which did not include these outputs), reprocesses source data, reproduces the same aggregates, writes a new transaction, and commits them.
- Consumers now see the results once. No duplicates leak because the earlier writes never became committed/visible.

If a failure happens after the commit

- Crash at T=12:02:10, after both offsets and TXN #123 were committed.
- On recovery, Flink resumes from the checkpoint that already included the committed offsets.
- It will not re-read or re-emit the [12:00, A42] aggregate, so no duplicates are produced.

If failure happens during the commit

- Flink uses Kafka’s transactional producer with a stable transactional ID per task.
- Kafka’s transaction coordinator ensures a transaction is either fully committed or aborted. On recovery, Flink reuses the same transactional ID; ambiguous in-flight transactions are resolved by Kafka (commit completes or is aborted).
- Consumers still only see committed messages; uncommitted ones remain hidden.

Downstream idempotency and dedup

- Even with strong guarantees, retries and replays can still happen in complex topologies. The `record_uuid` ensures that if a downstream service sees the same logical record again, it can perform an idempotent write.
- Examples:
  - Ad Budget Service persists budget deltas keyed by `record_uuid`. A second arrival with the same UUID is a no-op.
  - Hive tables keep only one row per `record_uuid`.
  - Pinot is configured for upserts; a second write with the same primary key replaces the first.

What about late or out-of-order events?

- The job aggregates by event time into 1-minute tumbling windows. With appropriate watermarks and allowed lateness, late events can be incorporated deterministically.
- Exactly-once still holds because only the final, checkpoint-committed aggregate for a given window becomes visible to consumers.

Key takeaways (cheat-sheet)

- Flink aligns source offsets and sink commits under a single checkpoint (2PC).
- Kafka exposes only committed transactions to `read_committed` consumers.
- On failures before commit: uncommitted outputs are invisible; job reprocesses and commits once.
- On failures after commit: offsets guarantee no re-emission; no duplicates.
- On ambiguous commit: Kafka transactions resolve to commit or abort; `read_committed` guarantees safety.
- `record_uuid` enables downstream idempotency and dedup across services.

This combination provides end-to-end exactly-once semantics for aggregated ad events, even across crashes, restarts, and partial writes.

Input Side: Kafka → Flink exactly-once consumption

Problem statement

- Kafka provides at-least-once delivery to consumers; a consumer can see the same message more than once (e.g., after a crash and offset rollback).
- How does Flink ensure that even if Kafka redelivers, the job still processes each logical input exactly once in the resulting outputs?

Mechanisms in play

- Flink checkpoints source offsets as part of its consistent checkpoint state. At checkpoint N, for each Kafka partition, Flink records the precise next-offset-to-read.
- On recovery, Flink restores operator state and resets Kafka consumers to those checkpointed offsets. This can cause re-reading messages that were read after the last successful checkpoint but whose outputs were not committed.
- The two-phase commit sink ties visibility of outputs to the same checkpoint barrier: outputs become visible if and only if the checkpoint is successful. Hence, re-reading is harmless because earlier outputs were not committed.

Illustrative timeline (single partition, simplified)

- Offsets in Kafka partition P0: ... 100, 101, 102, 103, ...
- Checkpoint N completes with next-offset=101 recorded in Flink state.
- Flink reads messages 101 and 102, produces corresponding aggregates, starts TXN #200 to the sink.
- Crash occurs before checkpoint N+1 completes.
- Recovery:
  - Flink restores next-offset=101 from checkpoint N and rewinds consumer to 101.
  - It re-reads messages 101 and 102.
  - It recomputes aggregates and writes a new transaction (e.g., TXN #201).
  - On checkpoint N+1 (post-recovery) success, TXN #201 is committed and becomes visible.
- Why no duplicate? Because TXN #200 was never committed; consumers use `read_committed` so only TXN #201’s outputs are visible.

Handling Kafka producer duplicates (upstream)

- If the upstream producer to Kafka is idempotent or transactional, Kafka ensures log-level deduplication per partition via sequence numbers. If not, true duplicate events may exist in the topic.
- Flink will faithfully read duplicates from Kafka; end-to-end exactly-once refers to processing consistency, not semantic dedup of upstream duplicate business events.
- Where needed, uber’s flow relies on downstream dedup/idempotency by `record_uuid` to handle logical duplicates in the aggregated layer.

Failure scenarios on the input side

1. Crash after reading, before checkpoint

   - Symptoms: Messages re-read on recovery.
   - Safety: Prior outputs were uncommitted; recomputation leads to a single committed result.

2. Crash after checkpoint commits offsets but before sink commit

   - Flink integrates source offsets and sink transactions under the same checkpoint. The checkpoint does not complete until the sink pre-commits and the job persists the linkage.
   - On recovery, any ambiguous sink transactions are resolved using Kafka’s transaction coordinator and the same transactional IDs; offsets and outputs remain consistent.

3. Consumer group rebalances
   - During rebalance, partitions can move between subtasks. Flink’s checkpointed offsets per partition ensure the new owner resumes from the last committed checkpointed position.
   - Re-reading is possible, but again harmless because visibility of outputs is tied to checkpoint success.

Key input-side takeaways

- Flink records the exact next offset per partition in checkpoints and restores from it.
- Re-reading after failures is expected; outputs from the earlier attempt are not visible unless their checkpoint succeeded.
- Together with transactional sinks and `read_committed`, this yields exactly-once effects from Kafka input to committed outputs.
