## If-Match and optimistic concurrency control — deep dive with examples

### The problem: concurrent updates

In distributed systems and APIs, multiple clients may read the same resource and attempt to update it. Without coordination, a later update can accidentally overwrite an earlier update. Optimistic concurrency control (OCC) prevents lost updates by requiring the client to prove it’s editing the version it originally fetched.

### The If-Match header

`If-Match` is an HTTP precondition header that says: "perform this method only if the current resource representation matches one of these entity tags (ETags)."

- Typical usage with `PUT`, `PATCH`, or `DELETE`.
- If the server’s current ETag does not match any provided tag, the server MUST NOT apply the change and should return `412 Precondition Failed`.
- If it matches, the server proceeds and returns `200/204` (or `2xx`) with the new/unchanged ETag.

This implements OCC: the client updates only if no one else modified the resource since it was last read.

### Request flow

1. Client reads the resource and saves the `ETag`.
2. Client modifies data locally.
3. Client sends write with `If-Match: <saved-etag>`.
4. Server compares the current ETag to the provided tag:
   - If equal: apply change; return new representation with new ETag.
   - If different: reject with `412 Precondition Failed`.

### Concrete example

Initial read:

```
GET /profiles/42 HTTP/1.1
Host: api.example.com

HTTP/1.1 200 OK
Content-Type: application/json
ETag: "prof-42-v7"

{"id":42,"name":"Ava","city":"Paris"}
```

Client A prepares an update based on v7:

```
PUT /profiles/42 HTTP/1.1
Host: api.example.com
Content-Type: application/json
If-Match: "prof-42-v7"

{"city":"Lyon"}

HTTP/1.1 200 OK
ETag: "prof-42-v8"

{"id":42,"name":"Ava","city":"Lyon"}
```

Meanwhile Client B had also read v7 earlier, but now tries to update after A:

```
PUT /profiles/42 HTTP/1.1
Host: api.example.com
Content-Type: application/json
If-Match: "prof-42-v7"

{"name":"Ava Smith"}

HTTP/1.1 412 Precondition Failed
ETag: "prof-42-v8"
Content-Type: application/problem+json

{"type":"https://httpstatuses.com/412","title":"Precondition Failed","detail":"ETag mismatch. Current version is v8."}
```

Client B must re-fetch, reconcile changes, and retry with the new ETag.

### Relationship to ETag and If-None-Match

- **ETag** identifies a representation version.
- **If-None-Match** is used by clients to validate caches for GET ("send me the body only if it changed").
- **If-Match** is used by clients to protect writes ("apply change only if my version is still current").

### Design choices for ETag used with If-Match

- **Strong validator** recommended: OCC requires byte-precise or version-precise detection. Backed by a DB row-version, incrementing counter, or content hash.
- **Opaque format**: Clients should not parse ETags. Servers can change the format without breaking clients.
- **Include in write responses**: After a successful update, return the new ETag so clients can chain edits.

### Multiple ETags and wildcard

- `If-Match: "v7", "v8"` means proceed if the current tag equals either.
- `If-Match: *` means "only if the resource exists" (useful for conditional updates that should fail if the resource is missing). Complementary to `If-None-Match: *` for create-once semantics.

### Error semantics and status codes

- `412 Precondition Failed`: Server refuses to apply the method because the precondition is false.
- `428 Precondition Required`: Server requires a precondition header (e.g., to enforce OCC on writes) and the client omitted it.
- `409 Conflict`: Optional alternative when the server can’t merge concurrent changes; often used with domain-level conflicts.

### Partial updates (PATCH) and merges

For `PATCH`, the same OCC rules apply. If the server supports automatic merges, it can accept the change even if there was an intermediate update, but then it must ensure no lost updates. Most APIs keep it simple: reject on mismatch with `412` and ask clients to re-fetch and merge.

### Minimal server-side logic (illustrative)

```javascript
// Node/Express-ish pseudocode
app.put("/profiles/:id", async (req, res) => {
  const profile = await db.getProfile(req.params.id);
  const currentEtag = `"prof-${profile.id}-v${profile.version}"`;

  const ifMatch = req.headers["if-match"];
  if (!ifMatch) {
    return res.status(428).json({
      type: "https://httpstatuses.com/428",
      title: "Precondition Required",
      detail: "If-Match header is required for updates.",
    });
  }

  if (ifMatch !== currentEtag) {
    res.set("ETag", currentEtag);
    return res.status(412).json({
      type: "https://httpstatuses.com/412",
      title: "Precondition Failed",
      detail: "ETag mismatch. Fetch latest and retry.",
    });
  }

  const updated = await db.updateProfile(req.params.id, req.body);
  const newEtag = `"prof-${updated.id}-v${updated.version}"`;

  res.set("ETag", newEtag);
  return res.status(200).json(updated);
});
```

### Best practices

- **Enforce OCC for all write operations** by requiring `If-Match`; return `428` when missing.
- **Use monotonic versioning** (DB rowversion, incrementing integer) to avoid hash collisions.
- **Return ETag on all reads and writes** so clients can continue editing safely.
- **Document retry guidance**: On `412`, instruct clients to GET latest, merge, and retry with new `If-Match`.
- **Beware of caches on writes**: Set `Cache-Control: no-store` on sensitive write responses if needed; intermediaries should not cache unsafe methods.

### Comparison: If-Match vs. application-level version fields

- You can carry a `version` field in the payload (e.g., `version: 7`) and compare server-side. `If-Match` is the HTTP-native, standardized way tied to the representation, works with intermediaries, and composes with ETag-based caching.

### Key takeaways

- **If-Match** is the HTTP way to implement optimistic concurrency control for writes.
- **On mismatch, return 412** and include the current ETag to guide clients.
- **Pair with ETags** on reads so clients can safely perform conditional updates.

