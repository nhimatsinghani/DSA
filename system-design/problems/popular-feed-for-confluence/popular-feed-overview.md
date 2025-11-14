
# Popular Feed for a Content Platform (Confluence-like) — System Design

Design the home screen Popular Feed that returns top pages by a metric (baseline: likes), refreshes when rankings change, renders across mobile/tablet/desktop, and later supports user-specific recommendations.

We adhere to the interview rubric (problem solving, technical proficiency, operational mindset, adaptability, decision-making) and include Mermaid diagrams in each part.

Parts
- Part 1 – Systems API -> `popular-feed-apis.md`
- Part 2 – Data Modeling -> `popular-feed-data-model.md`
- Part 3 – High-Level Architecture -> `popular-feed-architecture.md`
- Part 4 – Level Ups (Realtime refresh, personalization, scaling) -> `popular-feed-levelups.md`

---

## MVP Scope & Tenets

- Top pages by likes (fallback: views), per tenant and optionally per space.
- Real-time-ish freshness: visible within < 2–5s of like bursts.
- AuthZ-aware: only pages the user can view.
- Multi-device: server-driven UI (SDUI) card schema; responsive hints.
- Cost-effective: start with Postgres + Redis; evolve to streaming/Top-K.

```mermaid
flowchart LR
  Client[Mobile/Web/Desktop] --> API[Feed API (BFF)]
  API --> POP[Popular Service]
  POP --> Cache[(Redis ZSET/TopK)]
  POP --> DB[(Postgres)]
  POP --> Bus[(Events: likes, views)]
  Bus --> Agg[Aggregator (stream)]
  Agg --> Cache
  API --> AuthZ[AuthZ Service]
  API --> Hydrator[Page Summaries/Search]
```
