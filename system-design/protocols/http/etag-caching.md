## HTTP ETag caching — deep dive with practical examples

### What is an ETag?

An ETag (entity tag) is a validator attached to a representation of a resource. It’s an opaque string chosen by the server that changes whenever the representation meaningfully changes. Clients and intermediaries use it to validate caches without re-downloading the full body.

- **Strong ETag**: Changes on any byte difference. Format is arbitrary, e.g., `"\"86e-7b1a9\""` or a hash like `"WzJkZj…"`.
- **Weak ETag**: Prefixed by `W/`, e.g., `W/"abc"`. Signals semantic equivalence, not byte-for-byte equality (useful when only whitespace or formatting differs).

ETags are complementary to `Last-Modified`. Use both when possible: `Last-Modified` is cheap, but second-level resolution and clock skew can cause false negatives; ETags are precise.

### Why ETags matter

- **Bandwidth reduction**: Avoids sending bodies when content hasn’t changed.
- **Latency reduction**: `304 Not Modified` is typically smaller/faster than a full `200`.
- **Cache correctness**: Reliable content validation even with CDNs/reverse proxies.

### The validation lifecycle

1. Client performs an initial GET.
   - Server returns `200 OK` with body and headers like:

```
ETag: "v1-d41d8cd98f00b204e9800998ecf8427e"
Last-Modified: Tue, 10 Sep 2024 10:00:00 GMT
Cache-Control: max-age=60, must-revalidate
Vary: Accept-Encoding
```

2. Before the cache entry expires, the client wants to revalidate without re-downloading:

   - Client sends: `If-None-Match: "v1-d41d8cd98f00b204e9800998ecf8427e"`.
   - If unchanged, server responds with `304 Not Modified` (no body), possibly updating headers like `Cache-Control`, `Expires`.
   - If changed, server responds `200 OK` with new body and a new `ETag`.

3. If the entry is still fresh (`max-age` not expired), the client can serve from cache without contacting the server. When it becomes stale, the client revalidates with `If-None-Match`.

### Strong vs. weak validators

- Use **strong ETags** when exact bytes matter (e.g., range requests, binary assets). Range requests rely on strong validators or `If-Range` correctness.
- Use **weak ETags** for representations that may differ in bytes but are semantically the same (HTML pretty-print, reordered JSON with same meaning). Be careful with compression and transformations.

### Relationship to other headers

- **Cache-Control**: Governs freshness (e.g., `max-age`, `s-maxage`, `must-revalidate`, `stale-while-revalidate`, `stale-if-error`). ETags enable efficient revalidation once entries become stale.
- **Vary**: Declares which request headers influence the representation (e.g., `Accept-Encoding`, `Accept-Language`, `Authorization`). If you compress, set `Vary: Accept-Encoding` so caches key correctly.
- **Last-Modified / If-Modified-Since**: Time-based validator; less precise than ETags. Good fallback.
- **If-Range**: For range requests; send partial content only if the validator matches.

### Example: minimal client/server exchange

Initial fetch:

```
GET /articles/123 HTTP/1.1
Host: api.example.com

HTTP/1.1 200 OK
Content-Type: application/json
ETag: "art-123-v5"
Cache-Control: max-age=120, must-revalidate

{"id":123,"title":"Intro to ETags","body":"..."}
```

Revalidation (unchanged):

```
GET /articles/123 HTTP/1.1
Host: api.example.com
If-None-Match: "art-123-v5"

HTTP/1.1 304 Not Modified
ETag: "art-123-v5"
Cache-Control: max-age=120, must-revalidate
```

Revalidation (changed):

```
GET /articles/123 HTTP/1.1
Host: api.example.com
If-None-Match: "art-123-v5"

HTTP/1.1 200 OK
Content-Type: application/json
ETag: "art-123-v6"

{"id":123,"title":"Intro to ETags (updated)","body":"..."}
```

### How to generate ETags

Common strategies (choose one; ETag is opaque to clients):

- **Content hash** of the uncompressed payload (e.g., SHA-256 of body bytes). Stable across deployments and encodings.
- **Version/timestamp field** from storage (e.g., DB row-version, monotonic counter).
- **Build fingerprint** for static assets (e.g., webpack content hash) — often paired with immutable caching: `Cache-Control: max-age=31536000, immutable`.

Recommendations:

- Prefer strong validators for binary/static assets and when supporting range requests.
- If using compression, compute ETag on the canonical representation (e.g., uncompressed) and set `Vary: Accept-Encoding`. Avoid per-encoding ETags unless you key caches carefully.

### CDN and reverse proxies

- Surrogates honor `ETag`, `Cache-Control`, and `Vary`. Use `s-maxage` to set shared-cache TTLs distinct from browser TTLs.
- With HTML or APIs, favor short freshness + ETag revalidation to ensure timely updates while still reducing bandwidth.
- For static assets: long `max-age` with fingerprinted filenames (cache-busting) and strong ETags.

### Stale-while-revalidate pattern

`Cache-Control: max-age=60, stale-while-revalidate=30` lets caches serve slightly stale content while revalidating in the background, improving tail latency. Combine with ETags so the background validation is cheap.

### Pitfalls and gotchas

- **Fingerprinting/privacy**: Avoid using ETags to track users across origins. Respect privacy; consider disabling for highly personalized responses.
- **Weak ETags with transformations**: If intermediaries re-compress, byte-level equality breaks. Set `Vary` correctly; compute ETag on a canonical form.
- **Mismatched validators**: If you send `ETag` that doesn’t change when the content does, clients will be stuck on stale content. Tie ETag to actual representation changes.
- **Authorization-sensitive content**: If the response varies by `Authorization` or cookies, ensure `Vary: Authorization` (or `Cache-Control: private`) so shared caches don’t wrongly serve content.

### Quick cURL demo

Initial fetch (capture ETag):

```bash
curl -i https://api.example.com/articles/123 | sed -n '1,20p'
```

Subsequent revalidation:

```bash
curl -i -H 'If-None-Match: "art-123-v5"' https://api.example.com/articles/123 | sed -n '1,20p'
```

### Minimal server-side logic (illustrative)

```javascript
// Node/Express-ish pseudocode
app.get("/articles/:id", async (req, res) => {
  const article = await db.getArticle(req.params.id);
  const etag = `"art-${article.id}-v${article.version}"`;

  if (req.headers["if-none-match"] === etag) {
    res.set("ETag", etag);
    res.set("Cache-Control", "max-age=120, must-revalidate");
    return res.status(304).end();
  }

  res.set("ETag", etag);
  res.set("Cache-Control", "max-age=120, must-revalidate");
  return res.json(article);
});
```

### When to choose ETag vs Last-Modified

- Use both when feasible. Prefer ETag for precision; include `Last-Modified` as a cheap fallback.
- If representations can change multiple times within one second or clocks are unreliable, ETag is safer.

### Key takeaways

- **ETag identifies a specific representation version**; clients use `If-None-Match` to validate.
- **Combine with freshness directives** (`Cache-Control`) and `Vary` for correct caching.
- **Strong validators** for exact bytes/ranges; **weak validators** for semantic sameness.
- **CDNs and browsers** leverage ETags to reduce bandwidth and latency while keeping content fresh.

