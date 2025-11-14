
# Part 1 — Systems API (Popular Feed)

Design APIs that are device-agnostic and AuthZ-aware. All write APIs accept Idempotency-Key.

---

## Feed Retrieval

```
GET /v1/feed/popular
  ?tenantId=acme
  &scope=global|tenant|space:SPACE_KEY
  &metric=likes|views|score
  &window=1d|7d|30d|all
  &limit=20
  &cursor=ver:...    # server version for delta/e-tag
  &mode=approx|hybrid|exact  # choose path (see Level Ups)
```

Response (Server-Driven UI / Card schema)

```json
{
  "asOf": "2025-08-26T12:03:11Z",
  "version": "ver:tenant:acme:7d:likes:1700000012",
  "items": [
    {
      "urn": "urn:conf:acme:page:98765",
      "title": "Quarterly Planning",
      "subtitle": "Space: ENG • 241 likes",
      "thumbnail": {"url": "https://cdn/.../thumb.jpg", "aspect": "16:9"},
      "badges": [{"text": "NEW"}, {"text": "Top 1%"}],
      "actions": [{"type":"open","url":"https://conf/..."}],
      "metrics": {"likes": 241, "views7d": 5091, "score": 0.912},
      "display": {"density": "comfortable", "minWidth": 280}
    }
  ],
  "nextCursor": null
}
```

- `version`: changes when leaderboard composition or ordering changes. Used for delta refresh and cache revalidation (ETag).

### Delta Refresh

```
GET /v1/feed/popular/delta?version=ver:...&limit=50
→ 200 { adds:[...], updates:[...], removes:[urn,...], version:"ver:..." }
```

### Realtime Subscribe (SSE; WS optional)

```
GET /v1/feed/popular/stream?tenantId=acme&scope=tenant&window=7d&metric=likes
→ Server-Sent Events: {event:"version", data:{version:"ver:..."}}
```

Client compares version -> if different, call `/delta` (lightweight) or refresh first page.

---

## Engagement Write APIs

```
POST /v1/pages/{pageId}/like       # toggle like on/off
POST /v1/events/view               # page view event (batched)
```

Like Response

```json
{"pageId":"98765","liked":true,"likes":242,"version":"ver:tenant:acme:7d:likes:1700000101"}
```

---

## Page Summary (Hydration)

```
GET /v1/pages/{id}/summary
→ { urn, title, url, spaceKey, owner, createdAt, updatedAt, preview, metrics }
```

---

## Errors & Policies

- 403 forbidden (AuthZ).  
- 409 idempotency conflict on like toggles.  
- Rate limits: POST /like per user; GET /feed per IP/tenant; streaming connections per user.  

ETag/If-None-Match supported on GET /feed/popular: ETag = version.
