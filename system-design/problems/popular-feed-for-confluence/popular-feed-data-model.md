
# Part 2 — Data Modeling

We track pages, likes, views, and maintain aggregated counters and leaderboards. System of record: Postgres. Hot ranking: Redis.

---

## Tables (PostgreSQL)

```sql
CREATE TABLE tenants (
  id text PRIMARY KEY,
  name text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE pages (
  id           bigserial PRIMARY KEY,
  tenant_id    text NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  space_key    text NOT NULL,
  title        text NOT NULL,
  url          text NOT NULL,
  owner_user_id bigint,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  visibility   text NOT NULL DEFAULT 'private'
);
CREATE INDEX idx_pages_tenant_space ON pages(tenant_id, space_key);

CREATE TABLE page_likes (
  page_id     bigint NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
  user_id     bigint NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (page_id, user_id)
);

-- Optional batched page views
CREATE TABLE page_views_hour (
  page_id     bigint NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
  bucket_hour timestamptz NOT NULL,  -- truncated to hour
  views       bigint NOT NULL,
  PRIMARY KEY (page_id, bucket_hour)
);

-- Aggregated counters (authoritative; updated by stream or cron)
CREATE TABLE page_stats (
  page_id     bigint PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
  likes_all   bigint NOT NULL DEFAULT 0,
  likes_7d    bigint NOT NULL DEFAULT 0,
  likes_1d    bigint NOT NULL DEFAULT 0,
  views_7d    bigint NOT NULL DEFAULT 0,
  score       double precision NOT NULL DEFAULT 0.0,
  as_of       timestamptz NOT NULL DEFAULT now()
);

-- Snapshot of leaderboards (fallback exact)
CREATE TABLE leaderboard_snapshots (
  tenant_id  text NOT NULL,
  scope      text NOT NULL,  -- 'global'|'tenant'|'space:<key>'
  window     text NOT NULL,  -- '1d','7d','30d','all'
  metric     text NOT NULL,  -- 'likes','views','score'
  rank       int  NOT NULL,
  page_id    bigint NOT NULL,
  count      bigint NOT NULL,
  as_of      timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, scope, window, metric, rank)
);
```

Indexes
- page_likes(page_id), page_likes(user_id) for toggles and audits.  
- leaderboard_snapshots clustered by (tenant, scope, window, metric).

---

## Hot Stores (Redis)

- Sorted sets (ZSET) per (tenant, scope, window, metric) with score = likes or composite score and member = page_id.  
  - Key: `lb:{tenant}:{scope}:{window}:{metric}`  
- Hash: `pgs:{page_id}` -> small summary cache.  
- Pub/Sub or Streams: feed versioning and invalidation.

Why Redis ZSET? Native sorted ranking, O(log N) update; easy top-N queries. For very high cardinality, consider TopK module or sharded ZSETs.
