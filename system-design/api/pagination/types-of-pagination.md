## Types of API Pagination (Complete Guide)

This guide catalogs common pagination techniques for APIs, explains how they work, compares trade‑offs, and provides guidance on when to use each. It includes HTTP shapes, database query patterns, and a decision matrix.

### Core goals pagination tries to balance

- **Performance**: Avoid heavy scans and large `OFFSET` skips.
- **Consistency**: Prevent duplicates/missing items during concurrent writes.
- **Developer ergonomics**: Easy to implement and consume.
- **UX needs**: Jump to page N vs infinite scroll vs “load more”.
- **Observability**: Total counts, next/prev links, stable order.

---

## Pagination Techniques

### 1) Page-number pagination (page + size)

- **How it works**: Client requests `?page=5&size=25`. Server translates to `LIMIT` and `OFFSET`.
- **Typical HTTP**: `GET /items?page=5&size=25`
- **Typical SQL**:

```sql
SELECT *
FROM items
ORDER BY created_at DESC, id DESC
LIMIT 25 OFFSET (5 - 1) * 25;
```

- **Pros**
  - Simple mental model, great for admin dashboards.
  - Easy to link to a specific page.
  - Works with most databases and ORMs.
- **Cons**
  - Deep pages are slow: `OFFSET` N requires scanning and discarding N rows.
  - Inconsistent under writes: inserts/deletes between requests cause duplicates/misses.
  - Expensive count queries if you display total pages.
- **Best for**
  - Small/medium datasets, low write rates, need to jump to page N.

### 2) Offset-based pagination (offset + limit)

- **How it works**: Client requests `?offset=1000&limit=50`. Server does `LIMIT 50 OFFSET 1000`.
- **Pros**
  - Simple and ubiquitous.
  - Random access by offset.
- **Cons**
  - Same deep pagination and inconsistency issues as page-number pagination.
  - Offset can be expensive on large tables even with indexes.
- **Best for**
  - Internal tools, small data, or when random access by offset is mandatory.

### 3) Cursor-based (a.k.a. keyset or seek) pagination

- **How it works**: Use a stable sort key (or composite keys). Client passes a cursor representing the last seen key; server uses a `WHERE key < last_key` (or `>` for ascending) instead of `OFFSET`.
- **Typical HTTP**: `GET /items?limit=25&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0yNVQxMjowMDowMFoiLCJpZCI6IjEyMzQifQ` (opaque base64-encoded cursor)
- **Typical SQL**:

```sql
-- Descending by (created_at, id) to ensure uniqueness and stability
SELECT *
FROM items
WHERE (created_at, id) < (:cursor_created_at, :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 25;
```

- **Pros**
  - O(1) page fetch cost; no deep `OFFSET` scans.
  - Stable results with concurrent writes; avoids duplicates/misses when keys are unique and order is immutable.
  - Scales very well for feeds/infinite scroll.
- **Cons**
  - Hard to jump to page N directly.
  - Requires careful choice of unique, indexed sort keys (often composite like `(created_at, id)`).
  - Backwards navigation needs bidirectional cursors or reverse queries.
- **Best for**
  - Large datasets, high write rates, feed-like experiences, performance-critical endpoints.

### 4) Time-based pagination (since/until)

- **How it works**: Paginate by timestamp windows: `?since=2025-08-25T12:00:00Z&limit=100`. Often a special case of cursor using time as the key.
- **Pros**
  - Natural for time-ordered logs/feeds.
  - Easy incremental fetching (e.g., ETL, sync jobs).
- **Cons**
  - Requires a unique tiebreaker for stability (combine with ID to avoid duplicates when equal timestamps).
  - Backfilling or clock skew can cause subtle gaps without careful handling.
- **Best for**
  - Event logs, audit trails, append-only feeds.

### 5) Opaque continuation tokens (server-driven tokens)

- **How it works**: Server returns a `nextPageToken` that encodes the state (last key, filters, sort). Client sends it back verbatim. Token contents are opaque and may expire.
- **Typical HTTP**

```http
GET /items?limit=50

200 OK
{
  "items": [...],
  "nextPageToken": "eyJsYXN0S2V5IjoiMjAyNS0wOC0yNVQxMi4wMC4wMFoiLCJpZCI6IjEyMzQifQ=="
}
```

- **Pros**
  - Server can evolve internals without breaking clients.
  - Encodes complex state (filters, sorts, shards) securely.
  - Great for distributed stores or gateways (e.g., S3 `ContinuationToken`).
- **Cons**
  - Hard to link/share specific pages; tokens are transient.
  - Requires server-side validation/expiration logic.
- **Best for**
  - Public APIs, multi-tenant backends, or when implementation details must remain hidden.

### 6) GraphQL Relay-style connections (edges/nodes + cursors)

- **How it works**: Standard GraphQL pattern using `after/before` cursors with `first/last`. Returns `pageInfo { hasNextPage, hasPreviousPage, startCursor, endCursor }`.
- **Example schema**

```graphql
type ItemEdge {
  cursor: String!
  node: Item!
}
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
type ItemConnection {
  edges: [ItemEdge!]!
  pageInfo: PageInfo!
}

type Query {
  items(first: Int, after: String, last: Int, before: String): ItemConnection!
}
```

- **Pros**
  - Well-understood, tooling-friendly; maps to keyset under the hood.
  - Supports forward and backward pagination primitives.
- **Cons**
  - Slightly verbose payloads.
  - Requires discipline to ensure stable sort keys.
- **Best for**
  - GraphQL APIs where client libraries expect Relay connections.

### 7) Search-engine style: `search_after` (Elasticsearch, OpenSearch)

- **How it works**: Provide the sort values of the last document (`search_after: [last_created_at, last_id]`) to fetch the next page. Prefer over deep `from+size`.
- **Pros**
  - Scales to deep pagination without heavy skips.
  - Works with distributed indices.
- **Cons**
  - Requires consistent sort values and index mappings.
  - Not a generic SQL pattern.
- **Best for**
  - Full-text or analytics backends.

### 8) HTTP Link/Content-Range driven pagination

- **How it works**: Use `Link` headers with `rel="next"|"prev"|"first"|"last"` and/or `Content-Range` to communicate navigation. Underlying selection can be offset or cursor.
- **Example headers**

```http
Link: <https://api.example.com/items?cursor=abc>; rel="next", <https://api.example.com/items>; rel="first"
Content-Range: items 0-24/1000
```

- **Pros**
  - Standards-friendly; decouples navigation hints from body.
  - Plays nicely with caches and generic HTTP clients.
- **Cons**
  - Still needs a robust underlying pagination strategy.
  - `Content-Range` requires computing totals, which can be expensive.
- **Best for**
  - REST APIs emphasizing HATEOAS and intermediaries.

### 9) ID-based seek (monotonic IDs)

- **How it works**: Use `WHERE id > :last_id ORDER BY id ASC LIMIT :n`. Works if IDs are dense/monotonic.
- **Pros**
  - Very fast with an index on `id`.
  - Simple cursor semantics.
- **Cons**
  - Breaks if IDs are non-monotonic or heavily sparse after deletes.
  - Sorting by something else (e.g., `created_at`) needs composite keys.
- **Best for**
  - Append-mostly tables where `id` correlates with creation time.

### 10) Snapshot/point-in-time pagination

- **How it works**: Create a consistent snapshot (e.g., MVCC timestamp, materialized view, PIT search) and paginate over that snapshot using offset or cursor.
- **Pros**
  - Perfect consistency across pages; no duplicates or gaps.
  - Enables deterministic exports/reports.
- **Cons**
  - Operationally heavier (snapshot creation, storage, invalidation).
  - Complex to build for hot, mutable datasets.
- **Best for**
  - Reporting/exports, billing statements, compliance views.

### 11) Partition-aware pagination (sharded/backends)

- **How it works**: Maintain per-partition cursors and merge results (k-way merge by sort key). Often hidden behind a continuation token.
- **Pros**
  - Horizontal scalability and even load distribution.
  - Works with multi-region or multi-index systems.
- **Cons**
  - Complex to implement; requires careful ordering and deduplication.
- **Best for**
  - Large-scale systems with sharding or fan-out reads.

---

## Pros, Cons, and When to Use Which

- **Offset/Page-number**

  - **Use when**: Small datasets, low write rates, need direct page access.
  - **Pros**: Simple, random access, easy to implement.
  - **Cons**: Slow deep pages, inconsistencies under writes, costly counts.

- **Cursor/Keyset (Seek)**

  - **Use when**: Large/fast-changing datasets, infinite scroll, performance-critical.
  - **Pros**: Stable, fast, no deep scans, great for feeds.
  - **Cons**: Hard to jump to page N, requires unique stable sort keys.

- **Time-based**

  - **Use when**: Logs/events, incremental syncs.
  - **Pros**: Natural model for time-ordered data.
  - **Cons**: Clock issues, needs tie-breaker to avoid duplicates.

- **Opaque tokens**

  - **Use when**: Public APIs, evolving internals, distributed merges.
  - **Pros**: Hides complexity, flexible, secure.
  - **Cons**: Not bookmarkable, token lifecycle management.

- **GraphQL Relay**

  - **Use when**: GraphQL clients expect Relay connections.
  - **Pros**: Standardized, bi-directional support.
  - **Cons**: Verbose, still needs stable sorting.

- **Search `search_after`**

  - **Use when**: Elasticsearch/OpenSearch, deep pagination.
  - **Pros**: Scales deep, avoids `from+size` costs.
  - **Cons**: Backend-specific, requires sort discipline.

- **Snapshot (point-in-time)**

  - **Use when**: Reports/exports must be consistent.
  - **Pros**: Perfect cross-page consistency.
  - **Cons**: Operational overhead.

- **ID-based seek**

  - **Use when**: Monotonic IDs approximate time, simple feeds.
  - **Pros**: Very fast and simple.
  - **Cons**: Not suitable for arbitrary sort orders.

- **Partition-aware**
  - **Use when**: Sharded/multi-backend data.
  - **Pros**: Scales out, resilient.
  - **Cons**: Complex orchestration.

---

## Implementation Patterns and Examples

### REST: Offset vs Cursor responses

```http
GET /items?page=2&size=25

200 OK
{
  "items": [ ... 25 items ... ],
  "page": 2,
  "size": 25,
  "total": 1042,
  "links": {
    "self": "/items?page=2&size=25",
    "next": "/items?page=3&size=25",
    "prev": "/items?page=1&size=25"
  }
}
```

```http
GET /items?limit=25&cursor=eyJjIjoiMjAyNS0wOC0yNVQxMiIsImlkIjoiMTIzNCJ9

200 OK
{
  "items": [ ... 25 items ... ],
  "limit": 25,
  "nextCursor": "eyJjIjoiMjAyNS0wOC0yNVQxMSIsImlkIjoiMTEwMCJ9",
  "pageInfo": { "hasNextPage": true }
}
```

### SQL: Keyset with composite sort

```sql
-- Forward (older items) with descending order
SELECT *
FROM items
WHERE (created_at, id) < (:cursor_created_at, :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT :limit;

-- Backward (newer items)
SELECT *
FROM items
WHERE (created_at, id) > (:cursor_created_at, :cursor_id)
ORDER BY created_at ASC, id ASC
LIMIT :limit;
```

### GraphQL: Relay connection example

```graphql
query {
  items(first: 20, after: "ENDCURSOR") {
    edges {
      cursor
      node {
        id
        title
        createdAt
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

---

## Decision Matrix (Quick Guide)

| Requirement                                     | Recommended Technique                     |
| ----------------------------------------------- | ----------------------------------------- |
| Large dataset, high write rate, infinite scroll | Cursor/keyset or opaque token             |
| Need deep pagination without slowdown           | Cursor/keyset; search_after (ES)          |
| Must jump to arbitrary page N                   | Page-number/offset, or snapshot + offset  |
| Public API, hide internals, evolve over time    | Opaque continuation token                 |
| GraphQL clients and libraries                   | Relay connection (cursor)                 |
| Consistent export/report across pages           | Snapshot/point-in-time + offset or cursor |
| Append-only table with monotonic IDs            | ID-based seek                             |
| Sharded/multi-region dataset                    | Partition-aware with server token         |

---

## Best Practices

- **Choose a stable, unique order**: Use composite keys (e.g., `(created_at, id)`) to avoid ties.
- **Index the sort keys**: Ensure covering indexes for the `ORDER BY` and filters.
- **Cap page size**: Enforce a maximum `limit` (e.g., 100 or 1000 depending on payloads).
- **Expose navigation links**: Use `Link` headers or body `links`/`pageInfo`.
- **Support both directions**: Provide forward and backward pagination when UX needs it.
- **Handle duplicates & gaps**: For mutable data, prefer cursors; for exact consistency, use snapshots.
- **Return counts thoughtfully**: `total` can be approximate or omitted for performance; consider a separate endpoint.
- **Make tokens opaque**: Sign/encrypt to prevent tampering; set expirations.
- **Validate client input**: Clamp `limit`, disallow unindexed `sort` fields.
- **Document guarantees**: Explicitly state order, stability, token validity, and consistency model.

---

## Common Pitfalls

- **Deep `OFFSET` performance**: Avoid for large `page` values; use keyset instead.
- **Unstable ordering**: Sorting by non-unique fields causes duplicates/misses.
- **Changing filters mid-stream**: Invalidate cursors/tokens when filters change.
- **Backwards pagination**: Requires reversed order or storing both `startCursor` and `endCursor`.
- **Timezone/clock issues**: Use UTC ISO 8601 timestamps; combine with IDs as tiebreakers.
- **Leaking internals**: Avoid exposing raw primary keys in cursors unless acceptable; prefer opaque tokens.

---

## Quick Recommendations

- Building a feed/infinite scroll for a large, changing dataset? → **Cursor/keyset**.
- Public API with complex backends or sharding? → **Opaque continuation tokens**.
- Admin table with stable data and page jump? → **Page-number/offset**.
- Logs/events or ETL incremental sync? → **Time-based cursors**.
- Elasticsearch/OpenSearch? → **`search_after`**, avoid deep `from+size`.
- Compliance report/export with exact consistency? → **Snapshot + offset/cursor**.

