
# Collaborative Board System (Jira‑like) — System Design

**Goal:** Design a Kanban/Scrum-style collaborative board system (think “Jira-lite”).  
Phase 1 supports a **single user** workflow.  
Phase 2 extends to **multi-user real‑time collaboration** at team/organization scale.

---

## Table of Contents

1. [Interview Framing & Strategy](#interview-framing--strategy)  
2. [Requirements](#requirements)  
   2.1 [Functional (Phase 1 → Phase 2)](#functional-requirements)  
   2.2 [Non‑Functional](#non-functional-requirements)  
   2.3 [Assumptions](#assumptions)  
3. [High-Level Architecture](#high-level-architecture)  
   3.1 [Phase 1 (Single User — Modular Monolith)](#phase-1-single-user--modular-monolith)  
   3.2 [Phase 2 (Multi-User — Real-time & Services)](#phase-2-multi-user--real-time--services)  
4. [Domain Model & Data Architecture](#domain-model--data-architecture)  
   4.1 [Core Entities](#core-entities)  
   4.2 [Schema Sketch (PostgreSQL)](#schema-sketch-postgresql)  
   4.3 [Ordering (Rank Keys / Lexicographic)](#ordering-rank-keys--lexicographic)  
   4.4 [Search & Indexing](#search--indexing)  
   4.5 [Multi-Tenancy](#multi-tenancy)  
5. [API Design](#api-design)  
6. [Collaboration & Consistency](#collaboration--consistency)  
   6.1 [Optimistic Concurrency & Idempotency](#optimistic-concurrency--idempotency)  
   6.2 [Real-time Delivery](#real-time-delivery)  
   6.3 [Concurrent Editing (CRDT vs OT)](#concurrent-editing-crdt-vs-ot)  
   6.4 [Reordering Concurrency](#reordering-concurrency)  
7. [Scalability & Performance](#scalability--performance)  
   7.1 [Traffic Estimates & Capacity Planning](#traffic-estimates--capacity-planning)  
   7.2 [Caching Strategy](#caching-strategy)  
   7.3 [Sharding & Partitioning](#sharding--partitioning)  
   7.4 [Backpressure & Rate Limiting](#backpressure--rate-limiting)  
8. [Reliability, Operations & Security](#reliability-operations--security)  
   8.1 [Observability](#observability)  
   8.2 [Failure Modes & Fault Tolerance](#failure-modes--fault-tolerance)  
   8.3 [Security, RBAC & Audit](#security-rbac--audit)  
   8.4 [Data Protection & Compliance](#data-protection--compliance)  
   8.5 [Deployability](#deployability)  
9. [Tradeoffs & Tech Choices](#tradeoffs--tech-choices)  
10. [Evolvability: Adding Features Later](#evolvability-adding-features-later)  
11. [Testing Strategy](#testing-strategy)  
12. [What Breaks When (Limits & Red Flags)](#what-breaks-when-limits--red-flags)  
13. [How to Present in an Interview](#how-to-present-in-an-interview)  
14. [Appendix](#appendix)  
   - [Mermaid Diagrams](#mermaid-diagrams)  
   - [Pseudo-code: Rank-Key Insert](#pseudo-code-rank-key-insert)

---

## 1) Interview Framing & Strategy

**What the interviewer is looking for (explicitly mapping to the rubric):**

- **Problem Solving — Analytical**
  - Clarify MVP scope → avoid over-engineering, but design for evolution.
  - Break into *domain*, *storage*, *API*, *realtime*, *search*, *ops*.
  - Identify constraints & justify choices (e.g., why a cache? why Postgres?).
- **Technical Proficiency**
  - Explain concurrency (optimistic locking), idempotency, ordering, search indexing, eventing.
  - State limits & failure modes; show where the design trades off consistency/latency/cost.
- **Operational Mindset**
  - SLOs, incident paths, observability, backfills, migration tactics, backups.
- **Tech Adaptability**
  - Start modular monolith → carve out services when needed.
  - Accommodate CRDT/OT later without redesigning everything.
- **Decision Making**
  - Present at least two options for DB/search/eventing and compare.
  - Explain why the chosen path is “just enough” now, and how it evolves.

---

## 2) Requirements

### Functional Requirements

**Phase 1 (Single User)**
- Create/read/update/delete (CRUD) for:
  - Boards (Kanban-style), columns (statuses), tasks/issues (title, description, assignee, due date, labels, attachments).
  - Reorder tasks within/between columns.
  - Basic search/filter (by status/label/assignee/text).
  - Activity history on tasks (audit log).
  - Local notifications (e.g., email on due soon).
- Offline-friendly client (optional stretch), client-side optimistic UI.

**Phase 2 (Multi-User Collaboration)**
- Users, organizations/teams, projects, roles (admin/member/viewer).
- Real-time updates to boards and tasks (presence, typing indicators optional).
- Commenting, mentions, watchers, @notifications.
- Rich-text editing for descriptions/comments.
- Webhooks/integrations (e.g., Slack, CI).
- Full-text search across projects; filters & saved views.
- Attachments via object storage (pre-signed URLs).
- Sprints (optional), backlog, epics (optional).

### Non-Functional Requirements
- **SLO targets (example)**: p95 read < 200 ms, p95 write < 300 ms, 99.9% monthly availability.
- **Consistency**: Strong for single-item writes; eventual for derived views (search, analytics).
- **Scale goals**: 
  - Phase 1: ~1 board, ~1–5k tasks.  
  - Phase 2: 100k organizations, 1M+ boards, 100M+ tasks, 1–10k concurrent websockets per node.
- **Cost**: Minimize infra until usage grows; cloud-native primitives.

### Assumptions
- Multi-tenant SaaS by default (orgs contain users/projects/boards).
- Attachments stored out of DB (object storage).
- Modern web client; mobile later.

---

## 3) High-Level Architecture

### Phase 1 (Single User — Modular Monolith)

- **Client**: SPA (React/Vue/Svelte) talks to REST/GraphQL.
- **App**: Modular monolith with clear domains (User, Board, Issue, Comment, Search).
- **DB**: PostgreSQL (normalized core + JSONB for flexible fields).
- **Cache**: Redis for hot board reads & idempotency tokens.
- **Background worker**: for email notifications, search indexing.
- **Object storage**: S3/GCS with pre-signed upload/download.

Key reasons: fastest delivery, simplest ops, strong consistency, flexible schema.

### Phase 2 (Multi-User — Real-time & Services)

Carve out seams when bottlenecks appear:

- **API Gateway**
- **Auth & Org Service**
- **Board/Issue Service** (primary data owner, Postgres)
- **Search Service** (Elasticsearch/OpenSearch; consumes CDC/outbox)
- **Notification Service** (email/push/webhooks; consumes events)
- **Realtime Gateway** (WebSocket fanout; backed by Redis pub/sub or NATS)
- **File Service** (pre-signed URLs; antivirus/metadata)
- **Event Backbone** (Kafka/NATS/Kinesis; outbox pattern from OLTP DB)

> Keep the Board/Issue service the “system of record”. All others derive.

---

## 4) Domain Model & Data Architecture

### Core Entities

- **Organization** (multi-tenant boundary)
- **User** (belongs to org via membership)
- **Project** (optional; groups boards/issues)
- **Board** (view over issues; has ordered **Columns** / **Statuses**)
- **Issue/Task** (title, description, status, assignee, labels, story points, due, rank)
- **Comment** (rich-text; mentions)
- **Attachment** (object storage key)
- **Label/Tag** (many-to-many with issues)
- **Watcher** (user subscriptions)
- **Sprint** (optional), **Epic** (optional)
- **AuditEvent** (append-only)

### Schema Sketch (PostgreSQL)

```sql
-- Multi-tenancy core
CREATE TABLE organizations (
  id           BIGSERIAL PRIMARY KEY,
  name         TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id           BIGSERIAL PRIMARY KEY,
  email        CITEXT UNIQUE NOT NULL,
  name         TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE org_memberships (
  org_id       BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
  user_id      BIGINT REFERENCES users(id) ON DELETE CASCADE,
  role         TEXT CHECK (role IN ('admin','member','viewer')) NOT NULL,
  PRIMARY KEY (org_id, user_id)
);

CREATE TABLE projects (
  id           BIGSERIAL PRIMARY KEY,
  org_id       BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  key          TEXT NOT NULL, -- e.g., "PAY"
  name         TEXT NOT NULL,
  UNIQUE (org_id, key)
);

CREATE TABLE boards (
  id           BIGSERIAL PRIMARY KEY,
  org_id       BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  project_id   BIGINT REFERENCES projects(id),
  name         TEXT NOT NULL,
  created_by   BIGINT REFERENCES users(id),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE board_columns (
  id           BIGSERIAL PRIMARY KEY,
  board_id     BIGINT NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
  name         TEXT NOT NULL,
  wip_limit    INT,
  order_key    TEXT NOT NULL, -- lexicographic rank key
  UNIQUE (board_id, order_key)
);

CREATE TABLE issues (
  id           BIGSERIAL PRIMARY KEY,
  org_id       BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  project_id   BIGINT REFERENCES projects(id),
  board_id     BIGINT REFERENCES boards(id),
  key          TEXT, -- optional human-friendly, e.g., PAY-123
  title        TEXT NOT NULL,
  description  TEXT,     -- or store rich-text JSON
  status_col_id BIGINT REFERENCES board_columns(id),
  assignee_id  BIGINT REFERENCES users(id),
  reporter_id  BIGINT REFERENCES users(id),
  priority     TEXT CHECK (priority IN ('P0','P1','P2','P3')) DEFAULT 'P2',
  due_date     DATE,
  story_points NUMERIC(5,1),
  rank_key     TEXT NOT NULL, -- lexicographic rank key within column
  labels       TEXT[] DEFAULT '{}', -- fast MVP; normalize later if needed
  custom       JSONB DEFAULT '{}'::jsonb, -- for custom fields
  version      INT NOT NULL DEFAULT 1, -- optimistic concurrency
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (board_id, rank_key)
);

CREATE TABLE comments (
  id           BIGSERIAL PRIMARY KEY,
  issue_id     BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  author_id    BIGINT REFERENCES users(id),
  body         TEXT NOT NULL, -- rich-text JSON string if needed
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE attachments (
  id           BIGSERIAL PRIMARY KEY,
  issue_id     BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  object_key   TEXT NOT NULL,  -- S3/GCS key
  filename     TEXT NOT NULL,
  size_bytes   BIGINT NOT NULL,
  content_type TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE watchers (
  issue_id     BIGINT REFERENCES issues(id) ON DELETE CASCADE,
  user_id      BIGINT REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (issue_id, user_id)
);

CREATE TABLE audit_events (
  id           BIGSERIAL PRIMARY KEY,
  org_id       BIGINT NOT NULL,
  actor_id     BIGINT,
  entity_type  TEXT NOT NULL,  -- 'issue','comment', etc.
  entity_id    BIGINT NOT NULL,
  action       TEXT NOT NULL,  -- 'create','update','move','delete'
  before       JSONB,
  after        JSONB,
  metadata     JSONB,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Helpful indexes
CREATE INDEX idx_issues_org_board_col ON issues(org_id, board_id, status_col_id);
CREATE INDEX idx_issues_text ON issues USING GIN (to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(description,'')));
CREATE INDEX idx_audit_org_time ON audit_events(org_id, created_at);
```

> **Why Postgres?** Strong consistency & transactions for core domain, good indexing, JSONB for custom fields, easy migrations. Up to hundreds of millions of rows with partitioning and read replicas.

### Ordering (Rank Keys / Lexicographic)

- Use **rank keys** (base‑36/62 strings) to order columns and issues within a column.
- To insert between A and B, compute a key between `rank(A)` and `rank(B)` → **no mass reindexing**.
- When gaps become too small, **re-balance** (background job) on that column/board only.

**Tradeoffs vs integer positions**
- Integers require shifting many rows on reorder (O(n)); rank keys make inserts **O(1)** average.
- Rank keys add complexity (string math) and require occasional rebalancing.

### Search & Indexing

- Phase 1: Postgres full‑text + trigram for simple search.
- Phase 2: Dedicated search index (OpenSearch/Elasticsearch).
  - **Write path**: Issue write → DB transaction commits → Outbox row → Async consumer publishes to index.
  - **Read path**: Search queries hit search cluster; return IDs; hydrate from DB if needed.

**Consistency:** eventual (seconds). Use **version** or **seqno** to prevent stale overwrites in index.

### Multi-Tenancy

- Every row carries `org_id`.
- Row‑level authorization: (org_id, role) + optional per-project ACL.
- **Sharding strategy:** hash(org_id) → shard; co‑locate board/issues for locality.  
  Start with single cluster; add shards as orgs grow.

---

## 5) API Design

**REST (MVP-friendly):**

```
POST   /auth/login
GET    /orgs/:orgId/projects
POST   /orgs/:orgId/projects
GET    /orgs/:orgId/projects/:projectId/boards
POST   /orgs/:orgId/projects/:projectId/boards

GET    /boards/:boardId
PATCH  /boards/:boardId
POST   /boards/:boardId/columns
PATCH  /boards/:boardId/columns/:colId
POST   /boards/:boardId/columns/:colId/move   # reorders column
POST   /boards/:boardId/issues                # create
GET    /boards/:boardId/issues?status=&q=
PATCH  /issues/:issueId
POST   /issues/:issueId/move                  # move between columns; set rank_key
POST   /issues/:issueId/comments
POST   /issues/:issueId/watchers
POST   /issues/:issueId/attachments/presign   # returns pre-signed URL
GET    /search?q=&projectId=&boardId=
```

**Notes**
- **ETags / If‑Match** on `PATCH` for optimistic concurrency using `issues.version`.
- **Idempotency-Key** header on `POST` to guard retries.
- **WebSocket** endpoint: `/rt/connect?token=...` subscribe to `board:{id}` channels.

**GraphQL** is also viable for rich client queries but is optional until complexity justifies it.

---

## 6) Collaboration & Consistency

### Optimistic Concurrency & Idempotency

- Include `version` column on mutable rows (`issues.version`).
- `PATCH /issues/:id` requires `If-Match: "<version>"`; server increments on success.
- If mismatch, return `409 Conflict` with diff hints for client reconciliation.
- `Idempotency-Key` (UUID) + Redis: de-duplicate retried creates/moves.

### Real-time Delivery

- **Server**: Realtime Gateway (WS) + Redis pub/sub (or NATS) for fanout.
- **Channels**: `board:{id}`, `issue:{id}`; publish after DB commit.
- **Presence**: ephemeral keys in Redis with TTL.
- **Backoff**: exponential reconnect; fall back to SSE/long-poll.

### Concurrent Editing (CRDT vs OT)

- **Descriptions/Comments**:
  - Start with **last‑write‑wins** (simple).
  - Upgrade to **CRDT** (e.g., Y.js/Automerge) for true co‑editing:
    - Pros: offline‑first, merges without central locks.
    - Cons: state size grows, more complex client logic.
  - **OT** (Operational Transform): alternative; server becomes transformation core.
- Choose CRDT if Confluence-like rich co-authoring is a goal; otherwise defer.

### Reordering Concurrency

- Moves set new `rank_key`; if two concurrent moves collide:
  - Detect via unique `(board_id, rank_key)` constraint → retry recompute with new neighbors.
  - Use short critical section (transaction) scoped to the affected column only.

---

## 7) Scalability & Performance

### Traffic Estimates & Capacity Planning

_Example planning for a medium org:_
- 200 active users, 5 boards, 50k issues total.
- Hot board page: 200 reads/min (3–4 issues per read), 20 writes/min (moves/comments/edits).
- Websockets: ~100–400 concurrent.

**Capacity**
- Postgres: primary + 1–2 read replicas; partition `issues` by `org_id` or time when >100M rows.
- Redis: 1 small cluster (cache + presence + idempotency).
- Realtime nodes: 2–3 pods (10k sockets per pod typical), autoscale on connections.

### Caching Strategy

- **Board view cache**: board metadata + column order in Redis.
- **Query result cache**: top filters; short TTL (30–60s) to avoid staleness headaches.
- **Negative caching** for 404 lookups.
- **Do not cache** highly personalized/rapidly mutating data (per-user drafts).

### Sharding & Partitioning

- Start unsharded; add **logical shards by `org_id`** when needed.
- Keep **secondary indexes** aligned with shard key.
- If global reports become heavy, move to **columnar/warehouse** (BigQuery/Snowflake) via CDC.

### Backpressure & Rate Limiting

- Per-IP and per-user **rate limits** on writes.
- **Queue length**/lag SLOs for search indexer & notifier; shed load before saturation.
- Apply **WIP limits** on board columns at business layer (errors with hints).

---

## 8) Reliability, Operations & Security

### Observability

- **Metrics**: p50/p95 latency by endpoint, WS connection count, fanout delay, DB CPU/IO, queue lag.
- **Logs**: structured JSON with correlation IDs; redact PII.
- **Tracing**: OpenTelemetry across API → DB → queue → consumers.
- **Dashboards & Alerts**: SLO burn-rate alerts; WS disconnect spikes; indexer lag.

### Failure Modes & Fault Tolerance

- **DB primary failure** → promote replica; use connection retries & circuit breakers.
- **Cache miss / Redis down** → degrade gracefully; fetch from DB.
- **Event bus lag** → search/notifications stale; show “Index catching up…” banner.
- **Realtime outage** → fall back to polling with “live updates paused”.
- **Rank-key saturation** → background rebalancer throttled; UI still functional.

### Security, RBAC & Audit

- **Auth**: OAuth/OIDC/JWT, short-lived access + refresh.
- **RBAC**: org‑level roles + project overrides (admin/member/viewer).  
  Row filters: always constrain by `org_id`.
- **Audit**: append-only `audit_events`; capture actor, before/after, IP/UA.
- **Attachments**: pre-signed URLs; AV scan; size/type limits.

### Data Protection & Compliance

- **Encryption**: TLS in transit; KMS at rest.  
- **PII**: minimal storage; right-to-be-forgotten (soft+hard delete strategies).
- **Backups**: PITR for Postgres; test restores quarterly.
- **Retention**: lifecycle rules for attachments; archive closed issues after N days.

### Deployability

- **Pipelines**: CI with unit/integration; CD with canary + feature flags.
- **Migrations**: online (gh-ost/pg-osc); avoid long exclusive locks.
- **Infra as Code**: Terraform; secrets in vault.

---

## 9) Tradeoffs & Tech Choices

**DB**
- **PostgreSQL (chosen)**: ACID, JSONB, rich indexes, simpler ops.  
  **Limits**: vertical scaling ceiling; partitioning adds complexity.
- **DynamoDB/Spanner**: horizontal scale, global consistency (Spanner).  
  **Tradeoffs**: cost, vendor lock-in, schema/query constraints.
- **Cassandra**: write scalability, HA.  
  **Tradeoffs**: data modeling rigid; cross-row transactions absent.

**Messaging**
- **Kafka/NATS (chosen later)**: high throughput, consumer groups.  
  **Tradeoffs**: operational complexity.
- **RabbitMQ/SQS**: simpler; great for work queues, not as great for durable streams.

**Search**
- **OpenSearch/Elasticsearch**: text relevance, aggregations.  
  **Tradeoffs**: cluster tuning, eventual consistency.

**Realtime**
- **Native WS + Redis pub/sub**: simple, cost-effective.  
  **Tradeoffs**: cross-DC fanout harder; consider NATS or vendor (Ably/Pusher) if global.

**API**
- **REST first** (simpler caching, debuggable).  
  **GraphQL** for selective hydration when client queries get complex.

---

## 10) Evolvability: Adding Features Later

- **Automation rules**: trigger on state changes (DSL) → handled by Notification/Rules service.
- **Sprints/Epics**: new tables; reuse `issues` via relationships.
- **Custom fields**: enrich `issues.custom`; add config table; index hot fields.
- **Permissions**: row-level ACLs per project/board if needed.
- **Webhooks**: durable delivery with retries & signing; expose event catalog.
- **Mobile**: reuse API; add push notifications.

---

## 11) Testing Strategy

- **Unit**: rank-key math; validators; permission checks.
- **Integration**: DB tx + outbox + consumers; WS publish/subscribe roundtrip.
- **Contract**: API schemas with backward compatibility checks.
- **Property-based**: reordering under random concurrent moves.
- **Load**: soak tests on hot boards; WS connection churn.
- **Chaos**: kill Redis/Search; ensure graceful degradation.

---

## 12) What Breaks When (Limits & Red Flags)

- **Board with >50k visible issues**: DOM/rendering & network load.  
  _Mitigation_: virtualized lists, pagination, server-side windowing.
- **Hotspot org** (>1k writes/s on a single board): Postgres row-level contention.  
  _Mitigation_: split boards, batch writes, tune autovacuum, consider sharding.
- **Search cluster under-provisioned**: indexing lag → stale results.  
  _Mitigation_: backpressure; index only changed fields; tune refresh interval.
- **CRDT doc bloat**: large history.  
  _Mitigation_: snapshotting, GC of CRDT tombstones.

---

## 13) How to Present in an Interview

- Start with **use cases** → **MVP** → **phase 2**.  
- Draw the **architecture** and clearly call out **system of record** vs **derived systems**.
- For every choice, give **2 alternatives** + **why not**.
- Call out **consistency model** (strong for writes, eventual for search/notifications).  
- Show **operational thinking**: migrations, backfills, SLOs, incident playbooks.  
- End with **“what breaks when”** and **evolution path**.

---

## 14) Appendix

### Mermaid Diagrams

```mermaid
flowchart LR
  subgraph Client
    A[SPA / Mobile]
  end

  A -->|REST/GraphQL| B(API Gateway)
  B --> C[Auth & Org Service]
  B --> D[Board & Issue Service (Postgres)]
  B --> E[Realtime Gateway (WebSocket)]
  D --> F[(Postgres)]
  D --> G[Outbox]
  G --> H[(Event Bus: Kafka/NATS)]
  H --> I[Search Indexer]
  I --> J[(OpenSearch)]
  H --> K[Notification Service]
  K --> L[Email/Slack/Webhooks]
  B --> M[File Service]
  M --> N[(Object Storage)]
  E <-->|pub/sub| O[(Redis/NATS)]

  style F fill:#fff,stroke:#333,stroke-width:1px
  style J fill:#fff,stroke:#333,stroke-width:1px
  style N fill:#fff,stroke:#333,stroke-width:1px
```

### Pseudo-code: Rank-Key Insert

```python
# Assume rank keys are base-62 strings of fixed length, e.g., 'a000', 'a0zz', ...
# Given optional neighbors left=L, right=R (None means start or end), produce a new key.

def mid_key(left: str | None, right: str | None, width=8) -> str:
    MIN = "0" * width
    MAX = "z" * width
    if left is None and right is None:
        return "m" * width  # middle of space
    if left is None:
        # choose a key < right
        return decrement(right)
    if right is None:
        # choose a key > left
        return increment(left)
    if left >= right:
        # neighbors invalid, caller must refresh neighbors then retry
        raise ValueError("left >= right")
    return average_string(left, right)  # digit-wise midpoint in base-62

# Background job detects dense ranges and rebalances a column:
# SELECT issues ORDER BY rank_key; assign evenly spaced rank_keys; run in small batches.
```

---

### Why this design “neither under-solves nor over-engineers”

- Starts simple (monolith, Postgres, Redis) to deliver value fast.
- Bakes in **seams** (outbox, event bus, WS gateway, rank keys) so scale features are add-ons, not rewrites.
- Clearly documented tradeoffs, failure modes, and evolution path.

