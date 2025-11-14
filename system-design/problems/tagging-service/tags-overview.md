
# Cross‑Product Tagging System — Overview (Design for Atlassian‑like Suite)

This system enables users to **tag content across multiple products** (e.g., Jira Issues, Confluence Pages, Bitbucket Pull Requests) and to **retrieve content by tags**, with **popular tags** dashboards. It is **product‑agnostic** so that adding new products requires **no schema changes** and minimal code.

We follow the interview rubric: problem breakdown, trade‑offs, operational mindset, adaptability, and clear decisions. Each part has **Mermaid diagrams**.

---

## Goals & Requirements

### Functional
1. **Add/Remove/Update tags** on product entities.  
2. **List content by tag** across products.  
3. **Popular tags dashboard** (Top‑K globally and per customer/tenant).

### Non‑Functional
- **Product‑agnostic** model (extensible to new product/entity types).  
- Tags are **free‑form** (user‑created, no predefined set).  
- **Multi‑tenant** SaaS (tenants/customers have separate data scopes).  
- Low latency reads (p95 < 200 ms) and safe writes (idempotent).  
- **Observability**, **backups**, **evolution** to high scale.

---

## Core Concepts

- **Tenant**: an organization/customer.  
- **Product**: jira, confluence, bitbucket, … (extensible).  
- **Entity**: an item within a product type (issue, page, pull_request, …).  
- **Tag**: free‑form hashtag; **canonicalized** (lowercased, trimmed, single‑spaced).  
- **Tagging**: association between **EntityRef** and **Tag** (many‑to‑many).  
- **EntityRef**: product‑agnostic canonical identifier for any entity.

**EntityRef URN format**:  
`urn:atl:{tenantId}:{product}:{entityType}:{externalEntityId}`

- Example: `urn:atl:acme:jira:issue:JRA-123`

---

## High‑Level Architecture

```mermaid
flowchart LR
  subgraph Clients
    W[Web UI] --> BFF
    I[Internal Prod UIs] --> BFF
  end

  BFF[BFF / API Gateway]
  BFF --> TAGS[Tag Service (API + DB)]
  BFF --> AUTHZ[AuthZ Service]
  TAGS --> DB[(Postgres: tags, taggings, stats)]
  TAGS --> CACHE[(Redis cache)]
  TAGS --> OUTBOX[Outbox]
  OUTBOX --> BUS[(Event Bus: Kafka/NATS)]
  BUS --> IDX[Search Indexer]
  IDX --> ES[(Search/Analytics Index: OpenSearch/ES)]
  BUS --> POP[Popularity Aggregator]
  POP --> HOT[(Top‑K Store: Redis TopK / RocksDB)]
  BFF --> ES

  subgraph Product Backends
    J[Jira Svc]:::prod
    C[Confluence Svc]:::prod
    G[Bitbucket Svc]:::prod
  end
  BFF -->|hydrate summaries| J
  BFF -->|hydrate summaries| C
  BFF -->|hydrate summaries| G

  classDef prod fill:#eef,stroke:#99f;
```

**System of record**: Postgres in **Tag Service** (tags + taggings).  
**Search**: ES/OpenSearch for cross‑product retrieval and filtering.  
**Popular tags**: stream counts to **Top‑K** store for fast dashboards.

---

## Design Tenets

- **Product‑agnostic**: EntityRef URN + catalog tables; no per‑product schema.  
- **Idempotent writes** with `Idempotency‑Key`.  
- **Event‑driven**: Outbox → stream to search index & stats.  
- **AuthZ‑aware** at read time (filter results to user permissions).  
- **Cache** for hot queries; TTL + tag‑key invalidation on writes.

---

## File Map (Deep Dives)

- **Part 1 — API Design:** `tags-api-design.md`  
- **Part 2 — Data Modeling:** `tags-data-modeling.md`  
- **Part 3 — Scaling Popular Tags:** `tags-scaling-popular.md`  
- **Part 4 — Scaling Remaining APIs:** `tags-scaling-apis.md`  
- **Part 5 — Permissions:** `tags-permissions.md`

---

## Why this is “right‑sized”

- Start with **Postgres + Redis** and a simple **search index**; evolve to streaming top‑K when needed.  
- Clear seams (Outbox, Indexer, Aggregator) let you scale without rewrites.  
- Product adapters are **plugins**; core Tag Service stays unchanged when new products arrive.
