
# Stock Price Alert System — High‑Scale System Design

**Version:** 1.0  
**Date:** 2025‑09‑13

> Goal: Build a service that ingests real‑time stock prices, detects when a stock’s **current price** deviates by **±5%** from its **prior closing price**, and **push‑notifies every user subscribed** to that stock. Each user must receive **at most one notification per stock per day**.

---

## Table of Contents

1. [Scope & Definitions](#scope--definitions)  
2. [Assumptions](#assumptions)  
3. [Functional Requirements](#functional-requirements)  
4. [Non‑Functional Requirements (NFRs)](#non-functional-requirements-nfrs)  
5. [Back‑of‑the‑Envelope Sizing](#back-of-the-envelope-sizing)  
6. [Domain Model](#domain-model)  
7. [High‑Level Architecture](#high-level-architecture)  
8. [Data Contracts & Schemas](#data-contracts--schemas)  
9. [Detection Logic & Idempotency](#detection-logic--idempotency)  
10. [API Design (User/Subscription/Notification)](#api-design-usersubscriptionnotification)  
11. [Storage Choices & Partitioning](#storage-choices--partitioning)  
12. [Scaling Challenges & Mitigations](#scaling-challenges--mitigations)  
13. [Multi‑Region & Disaster Recovery](#multi-region--disaster-recovery)  
14. [Observability, Runbooks, SLOs](#observability-runbooks-slos)  
15. [Security & Compliance](#security--compliance)  
16. [Testing Strategy](#testing-strategy)  
17. [Cost & Efficiency Considerations](#cost--efficiency-considerations)  
18. [Future Extensions](#future-extensions)  
19. [Appendix: Pseudocode, Examples, Edge Cases](#appendix-pseudocode-examples-edge-cases)

---

## 1) Scope & Definitions

- **Input feed:** An external provider (e.g., NASDAQ, NYSE, a data broker) sends price ticks of the form:
  ```json
  {
    "symbol": "UBER",
    "price": 99.01,
    "closing_price": 85.04
  }
  ```
- **Rule:** Trigger when `abs(price - closing_price) / closing_price >= 0.05` (≥ 5%).  
- **Subscribers:** Users subscribe to one or more symbols (e.g., AAPL, UBER).  
- **Action:** Send push notification to **all users subscribed** to the stock.  
- **Once‑per‑day constraint:** A user may receive **at most one** alert for a given stock **per day** (even if the price crosses the threshold multiple times).

**What is a “day”?** Unless otherwise specified, the day is defined by the **primary exchange’s local trading calendar** for the symbol (see [Assumptions](#assumptions)).

---

## 2) Assumptions

1. **Feed characteristics**
   - Provider sends ticks continuously via resilient transport (e.g., WebSocket, gRPC stream, or Kafka).  
   - `closing_price` is the prior **regular session** close, not adjusted intraday; corporate actions may update it (see [Edge Cases](#edge-cases)).
2. **Trading sessions**  
   - We notify on **regular and extended hours** by default. This is configurable per market.
3. **User state**
   - Users may subscribe/unsubscribe anytime. We **do not** send retroactive alerts for users who subscribed **after** a breach already occurred that day.
4. **Notification boundary (“once per day”)**  
   - “Day” == **exchange‑local trading day**: from **market open** on Day T to **next market open** on Day T+1. (Alternative: midnight boundary; see [Design Alternatives](#design-alternatives-for-day-boundary).)
5. **Push channels**
   - We use APNs (iOS) and FCM (Android), potentially an internal Push Gateway (e.g., AWS SNS + SQS) for fan‑out buffering.
6. **Scale targets** (for design headroom; see [Sizing](#back-of-the-envelope-sizing)):
   - 20M MAU, 150M total device tokens, 8K–12K active US symbols, bursts of 200K–1M ticks/min, black‑swan days higher.
7. **Idempotency model**
   - **At‑least‑once** processing in the stream; we enforce **idempotent alert emission** with a **ledger** and **idempotency keys**.

---

## 3) Functional Requirements

- **Subscription management**
  - Create/delete list of user subscriptions to symbols.  
  - List a user’s subscriptions.  
  - Validate symbols (mapping to canonical instrument IDs).
- **Price ingestion**
  - Consume real‑time ticks; recover from disconnects; reorder/duplicate tolerant.  
  - Persist offsets for replay.
- **Threshold detection**
  - Compute ±5% change from prior close; detect first breach per symbol/day.  
  - Support per‑market configs (what is the day boundary, include pre/post market or not).
- **Notification fan‑out**
  - For a breached symbol/day, notify **all currently subscribed users**, respecting once‑per‑day/user/stock dedupe.
- **Idempotency & dedupe**
  - Ensure a user never gets more than one alert for the same stock/day even with retries, duplicates, or replays.
- **Administrative & analytics**
  - Audit trail of alerts, delivery metrics, per‑user opt‑outs, rate limits, experiments (A/B message text).

---

## 4) Non‑Functional Requirements (NFRs)

- **Latency:** P50 end‑to‑end ≤ 2s; P99 ≤ 8s from tick to push delivery attempt.  
- **Availability:** 99.9% for ingestion and detection; 99.5% overall (push providers may be lower).  
- **Durability:** No loss of alert decisions; at‑least‑once notification attempts with idempotency.  
- **Scalability:** Handle black‑swan surfaces (e.g., 100+ symbols breach simultaneously).  
- **Accuracy:** No over‑notification beyond once/day/user/stock; false positives < 0.1% daily.  
- **Observability:** Tracing across ingestion → detection → fan‑out → provider → device callbacks.  
- **Security & Privacy:** Encrypt PII & tokens in transit/at rest. Least‑privilege. GDPR/CCPA deletion.  
- **Cost efficiency:** Storage tiering, compaction, and batch fan‑out optimizations.

---

## 5) Back‑of‑the‑Envelope Sizing

> Use to drive partitioning and capacity, not as strict truth.

- **Symbols:** ~10K listed (active subset ~6–8K).  
- **Ticks:** Typical: 10–50 ticks/s for most liquid names; thin names much lower; peak market‑open bursts.  
- **Peak ingestion:** 500K ticks/minute (8.3K/s) steady; **burst** 2–5M/min (33–83K/s) on volatile open.  
- **Subscribers:** 20M MAU, median 6 subs → **120M subscriptions**.  
- **Breach fan‑out:** If 100 symbols breach around open, and each symbol averages 4M subscribers (long tail!): naive fan‑out could be **hundreds of millions** of pushes in minutes → must **throttle + shard**.

---

## 6) Domain Model

**Core entities**

- **User** `(user_id, locale, tz, created_at, …)`  
- **DeviceEndpoint** `(device_id, user_id, provider, push_token, status, updated_at, …)`  
- **Symbol** `(symbol, exchange, canonical_instrument_id, decimals, status)`  
- **Subscription** `(user_id, canonical_instrument_id, created_at)`  
- **PriceTick** `(instrument_id, ts, price, closing_price, provider_seq, …)`  
- **BreachEvent** `(instrument_id, trading_day, ts_first_breach, direction, rule_version)`  
- **NotificationLedger** `(user_id, trading_day, instrument_id, alert_id, sent_at, channel, payload_hash)` — **TTL** beyond the day boundary for cleanup.  
- **RuleConfig** `(rule_id, threshold_pct=0.05, include_ext_hours=true, day_boundary='market_open', …)`  
- **Outbox / DeliveryAttempt** `(attempt_id, alert_id, device_id, status, retry_count, last_error, …)`

**Relationships**

- `User 1—N DeviceEndpoint`  
- `User N—M Symbol` via `Subscription`  
- `Symbol 1—1 canonical_instrument_id` (normalize; symbols can be reused)  
- `BreachEvent 1—N DeliveryAttempt`

**Notes**

- Use **canonical instrument ID** (e.g., FIGI) internally; keep `symbol` for UX.  
- `NotificationLedger` enforces **once/day/user/stock** semantics.

---

## 7) High‑Level Architecture

```mermaid
flowchart LR
  subgraph Provider
    S1[Market Data Stream] -->|ticks| GW
  end

  subgraph OurCloud
    GW[Ingestion Gateway] --> Q[(Kafka / PubSub)]
    Q --> DETECT[Stream Processor<br/>(Flink/Kafka Streams)]
    DETECT -->|BreachEvent| BREACH[(Compacted Topic)]
    BREACH --> FANOUT[Fan-out Service]
    FANOUT --> LEDGER[(Notification Ledger<br/>DynamoDB/Redis+RDB)]
    FANOUT --> OUTBOX[(Delivery Queue<br/>SQS/Kafka)]
    OUTBOX --> PUSH[Push Workers]
    PUSH --> APNs
    PUSH --> FCM
    APNs --> CALLBACKS[Delivery Callbacks]
    FCM --> CALLBACKS
    CALLBACKS --> METRICS[Metrics & Audit]
    subgraph ControlPlane
      API[User+Subscription API] --> DB[(Users/Subscriptions DB)]
      API --> CFG[Rule Config]
      DETECT --> CFG
      FANOUT --> CFG
    end
    METRICS --> OBS[Observability Stack]
  end
```

**Key ideas**

- **Decouple** ingestion, detection, breach publication, and push delivery with **durable topics/queues**.  
- **Compacted `BreachEvent` topic** stores only the **first breach per instrument/day** (latest wins), simplifying replays.  
- **Fan‑out** reads `BreachEvent`, fetches subscribers in **shards**, and writes **idempotent** delivery intents to Outbox.  
- **Ledger** enforces once/day/user/stock with **conditional writes**.

---

## 8) Data Contracts & Schemas

**PriceTick (protobuf/JSON)**
```json
{
  "instrument_id": "BBG000R7Z112",          // canonical ID
  "symbol": "UBER",
  "exchange": "NYSE",
  "ts": "2025-09-13T14:31:02.123Z",
  "seq": 9832145,                           // provider sequence if available
  "price": 99.01,
  "closing_price": 85.04,
  "source": "providerA"
}
```

**BreachEvent**  (first breach per instrument/day; direction optional for this requirement)
```json
{
  "alert_id": "2025-09-13_NYSE_BBG000R7Z112_rulev1",
  "instrument_id": "BBG000R7Z112",
  "symbol": "UBER",
  "exchange": "NYSE",
  "trading_day": "2025-09-13",
  "direction": "up",                         // "up"|"down" (informational)
  "pct_change": 0.164,                       // at first breach crossing
  "ts_first_breach": "2025-09-13T14:31:02.123Z",
  "rule_version": "v1",
  "config_hash": "…"
}
```

**NotificationLedger (idempotency)** — logical key
```
PK: user_id
SK: trading_day#instrument_id
Attributes: alert_id, sent_at, channel, payload_hash, ttl
Condition: if_not_exists(SK) on write
```

**DeliveryAttempt (Outbox / queue payload)**
```json
{
  "attempt_id": "uuid",
  "alert_id": "2025-09-13_NYSE_BBG000R7Z112_rulev1",
  "user_id": "u_123",
  "device_id": "d_987",
  "push_provider": "APNs",
  "payload": {
    "title": "UBER up 16.4% vs close",
    "body": "Now $99.01 (prev close $85.04).",
    "deeplink": "app://symbol/UBER"
  },
  "idempotency_key": "u_123#2025-09-13#BBG000R7Z112",
  "ts_enqueued": "…"
}
```

---

## 9) Detection Logic & Idempotency

**Computation**  
- For each tick per instrument/day:
  ```text
  pct_change = (price - closing_price) / closing_price
  breach if abs(pct_change) >= 0.05
  ```

**State & gating**  
- Maintain per `instrument_id` + `trading_day` state (`has_breached`, `ts_first_breach`, `direction`).  
- On first breach, emit a **BreachEvent** with deterministic `alert_id`.  
- Subsequent ticks for same instrument/day are ignored for breach publishing (but logged/metrics).

**Why a global breach gate?**  
- Prevents issuing billions of redundant records during oscillations.  
- Still compatible with **per‑user once/day** via the **Ledger**.  
- New subscribers after the first breach on that day **do not** get retroactive alerts (as per assumptions).

**Idempotent fan‑out**  
- For each `(user, instrument, trading_day)` compute **idempotency_key** = `user_id#day#instrument_id`.  
- **Conditional write** to `NotificationLedger`: if key exists → **skip**; else write and enqueue delivery.  
- **Outbox workers** also de‑duplicate using the same key to render retry loops safe.

**Edge: direction‑specific dedupe**  
- Requirement says “only once per day per stock”, independent of up/down.  
- If you wanted **per‑direction** dedupe, include `direction` in the key.

---

## 10) API Design (User/Subscription/Notification)

**User/Subscription API (REST/JSON)**
- `POST /v1/users/{user_id}/subscriptions`  
  - Body: `{ "symbols": ["AAPL","UBER"] }` (or canonical IDs)  
- `DELETE /v1/users/{user_id}/subscriptions/{symbol}`  
- `GET /v1/users/{user_id}/subscriptions`  
- `PUT /v1/devices` register/update push tokens  
- `DELETE /v1/devices/{device_id}`

**Admin/Config**
- `PUT /v1/rules/price-breach` → threshold, inclusion of ext hours, rule_version.  
- `PUT /v1/markets/{exchange}/calendar` → open/close times, holidays.

**Webhook / Callbacks**  
- `/v1/push/callbacks` to receive delivery receipts and token invalidations.

---

## 11) Storage Choices & Partitioning

| Data | Access Pattern | Store | Partitioning |
|---|---|---|---|
| Users | OLTP; strong consistency | SQL (Postgres) or DynamoDB | `user_id` |
| Devices | Write‑heavy updates; lookup by user | SQL/DynamoDB | `user_id` |
| Subscriptions | Massive N; query by symbol → users; and by user | **Two shapes**: (1) SQL with inverted index; (2) KV/NoSQL sharded by symbol for **fan‑out** | For fan‑out: partition on `instrument_id` and shard into buckets (e.g., `instrument_id#shard_n`) |
| Price ticks | Append‑only stream | Kafka / PubSub | Topic partitioned by `instrument_id` hash |
| BreachEvent | First breach per instrument/day | Kafka compacted topic | Partition by `instrument_id` |
| NotificationLedger | Hot writes at breach | DynamoDB/Scylla/Redis (with AOF) | PK `user_id`; SK `day#instrument`; conditional put |
| Outbox | High QPS | SQS/Kafka | Partition by `device_id` or `user_id` |

**Why KV/NoSQL for fan‑out?**  
- On breach, we need to enumerate **all subscribers for a symbol** quickly. Store pre‑sharded subscription sets per instrument (e.g., 64 shards per instrument) to enable parallel reads across shards.

**Cache**  
- Redis for hot symbol configs, market calendar cache, and per‑instrument breach state mirrors (optional).

---

## 12) Scaling Challenges & Mitigations

### A) Ingestion bursts & ordering
- **Problem:** At market open, tick rates spike; packets reorder; provider reconnects.  
- **Mitigations:**  
  - Partition streams by `instrument_id`.  
  - Use **idempotent producers** and **exactly‑once** *processing semantics* where available (Kafka Streams/Flink checkpoints) but rely on **at‑least‑once + idempotent sinks**.  
  - Persist provider **sequence**/**offset** for replay.

### B) Oscillation around 5% line
- **Problem:** Price crosses the threshold multiple times; could flood.  
- **Mitigations:**  
  - **Global gate** per instrument/day: emit only the **first** BreachEvent.  
  - Optional **hysteresis** (e.g., require 5% ± ε or N ticks confirmation) if false positives observed.

### C) Fan‑out storm (thundering herd)
- **Problem:** When a mega‑cap breaches, millions of notifications must be sent quickly.  
- **Mitigations:**  
  - Pre‑shard subscriber lists (e.g., 64–256 shards per instrument).  
  - Use **batching** to push provider (where possible).  
  - **Rate limit per provider region**; spread over a 1–5 minute window while staying within latency SLO.  
  - Use **token dedup** (many devices per user; send to top active device or all per policy).

### D) Once‑per‑day enforcement under retries
- **Problem:** At‑least‑once delivery and retries can double‑send.  
- **Mitigations:**  
  - **NotificationLedger** with conditional write `if_not_exists`.  
  - **Idempotency key** in outbox and push payload.  
  - **Stateless workers** + **exactly‑once‑effect** at the ledger layer.

### E) Multi‑region consistency
- **Problem:** Cross‑region duplicate alerts if both detect first breach.  
- **Mitigations:**  
  - Single writer region for **BreachEvent** topic, or **global compaction** with tie‑break (min timestamp).  
  - If active‑active, use **Redis SETNX** or **DynamoDB conditional** on a **global key** `instrument_id#trading_day` before publishing.

### F) Corporate actions & closing price corrections
- **Problem:** Splits/dividends/corrections invalidate `closing_price`.  
- **Mitigations:**  
  - Ingest corporate action feed; compute **adjustment factors**; update **rule config** for affected symbols **atomically**.  
  - If closing price changes intraday, **recompute** breach state (don’t republish if already breached unless rule_version increments).

### G) Token churn & provider limits
- **Problem:** Invalid/expired push tokens; FCM/APNs rate limits.  
- **Mitigations:**  
  - Maintain **token status**; remove invalid on callback.  
  - **Exponential backoff** with capped retries; drop after N failures.  
  - Regionalize workers close to provider endpoints.

### H) Trading calendar & DST
- **Problem:** Day boundary ambiguity across exchanges and DST shifts.  
- **Mitigations:**  
  - **Exchange calendar service** with authoritative open/close times and holidays.  
  - Define day boundary per exchange and include it in `alert_id`.  
  - Reset **ledger TTL** at next market open + grace.

---

## 13) Multi‑Region & Disaster Recovery

- **Topology:** Active‑active for read APIs; **active‑passive** or **single‑writer** for detection & `BreachEvent` to avoid split‑brain.  
- **Data:**  
  - Kafka with cross‑region replication for ticks and breach topics.  
  - DynamoDB global tables or per‑region tables with **conflict‑free keys** (idempotency keys are deterministic).  
- **RPO/RTO:** RPO < 1 min (stream replication); RTO < 15 min (failover runbook).  
- **DR drills:** Quarterly game days with synthetic tick replays.

---

## 14) Observability, Runbooks, SLOs

**Metrics**
- Ingestion: ticks/s, lag, reconnects, message duplication rate.  
- Detection: breach rate by instrument, first‑breach latency, false‑positive ratio.  
- Fan‑out: queue depth, shard read latency, users targeted, devices sent.  
- Delivery: success rate per provider, retries, device invalidations.  
- Ledger: conditional write success/dup rate, p95 latency.  
- End‑to‑end: tick→push latency histogram.

**Tracing**
- Correlate `alert_id` through ingestion → detection → fan‑out → push → callback.

**Runbooks**
- Provider outage (switch to backup feed).  
- Kafka lag spike (scale consumers; backpressure).  
- Push provider degradation (shift throughput, widen backoff).  
- Calendar mismatch (hotfix boundary; rekey future alerts).

**SLOs**
- 99% of alerts initiated within 3s of first breach tick.  
- <0.1% users receive duplicate per stock/day.

---

## 15) Security & Compliance

- **Secrets** in HSM/KMS; rotate regularly.  
- **PII** and push tokens encrypted at rest; field‑level encryption.  
- **Access control** via IAM; principle of least privilege.  
- **Data retention**:  
  - Ledger TTL: `next_open + 7 days`.  
  - Delivery attempts: 30–90 days for audit.  
- **Privacy**: GDPR/CCPA deletion workflows; consent and opt‑out.

---

## 16) Testing Strategy

- **Unit & property tests** for breach math (edge around 5%).  
- **Simulated tick streams** with recorded historical days.  
- **Chaos tests**: disconnects, duplicates, out‑of‑order ticks.  
- **Load tests**: fan‑out storms (100+ symbols; 100M+ deliveries).  
- **Idempotency tests**: replay same BreachEvent N times; assert single ledger entry/user.  
- **Soak tests** during market hours.

---

## 17) Cost & Efficiency Considerations

- **Compacted topics** for `BreachEvent` to keep storage small.  
- **Sharded subscription sets** to bound hot partitions.  
- **Batch device sends** (where supported) and compress payload.  
- **Tiered storage** for old ticks; data lake for analytics.  
- **Downsample ticks** if provider sends ultra‑high frequency and it doesn’t change breach decisions (configurable).

---

## 18) Future Extensions

- **User thresholds** (per‑user custom %).  
- **Direction‑specific dedupe** (up vs down).  
- **Web/email channels** with per‑channel dedupe.  
- **Alert windows** (“only during regular hours”).  
- **Per‑user quiet hours** with queue‑until‑open delivery.

---

## 19) Appendix: Pseudocode, Examples, Edge Cases

### A) Stream detection (Kafka Streams/Flink‑like pseudocode)

```pseudo
// keyBy instrument_id
process tick(t):
  day = trading_day_for(t.exchange, t.ts)
  state = get_state(instrument_id, day)
  pct = (t.price - t.closing_price) / t.closing_price
  if not state.has_breached and abs(pct) >= threshold:
      direction = "up" if pct >= 0 else "down"
      alert_id = f"{day}_{t.exchange}_{t.instrument_id}_rule{rule_version}"
      emit BreachEvent(alert_id, instrument_id, t.symbol, t.exchange, day, direction, pct, t.ts)
      state.has_breached = true
      state.ts_first = t.ts
      save_state(state)
```

### B) Fan‑out + Ledger enforcement

```pseudo
on BreachEvent(be):
  for shard in subscription_shards(be.instrument_id): // parallel
      users = fetch_users_for_shard(be.instrument_id, shard)
      for user in users: // parallel/batched
          key = f"{user.id}#{be.trading_day}#{be.instrument_id}"
          if ledger.conditional_put(user.id, be.trading_day, be.instrument_id, be.alert_id): // if_not_exists
              for device in devices(user.id):
                  enqueue_outbox({
                    attempt_id: uuid(),
                    alert_id: be.alert_id,
                    user_id: user.id,
                    device_id: device.id,
                    idempotency_key: key,
                    payload: render_payload(be, user.locale)
                  })
          else:
              // already notified today for this stock; skip
              continue
```

### C) Example payloads

- **Message title:** `UBER up 16.4% vs yesterday’s close`  
- **Message body:** `Now $99.01 (prev close $85.04).`  
- **Deep link:** `app://symbol/UBER`

### D) Edge cases

1. **Symbol change / ticker reuse** — use **canonical instrument_id**; keep alias list.  
2. **Trading halt** — if price resumes and crosses threshold, treat as normal.  
3. **Close price correction** — if provider updates, **do not** emit a new BreachEvent unless the rule version or config hash changes; just update future days.  
4. **Zero/near‑zero close** — guard division by zero; drop ticks with invalid data; alert ops.  
5. **DST shift** — day boundary service must handle timezone transitions precisely.  
6. **User with 10 devices** — policy: send to all active devices or **primary device only**; document policy.  
7. **Partial outages** — degraded mode: if ledger store unavailable, **fail‑closed** (pause fan‑out) to preserve dedupe guarantees.

---

## Design Alternatives for Day Boundary

- **Market‑open to market‑open (default):** aligns with trading activity; avoids midnight boundary issues for extended hours.  
- **Calendar day (00:00–23:59 local):** simpler but can create surprises around pre/post market events.  
- **UTC day:** consistent globally but decoupled from exchange behavior.

> The chosen approach should be included in `alert_id` derivation to avoid cross‑config duplication.

---

## Summary

This design ingests real‑time ticks, **publishes a single compacted breach event per symbol/day**, and then **idempotently fans out** notifications using a **per‑user ledger** keyed by `(user, day, instrument)`. It meets the **once‑per‑day per stock** requirement under **at‑least‑once** processing, scales to market‑open storms via **sharded subscription sets** and **rate‑limited push workers**, and remains robust to provider anomalies, corporate actions, multi‑region failover, and DST complexities.
