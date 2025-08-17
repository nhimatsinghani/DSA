## HTTP PATCH: Use Cases, Semantics, and Differences from PUT/POST

### What PATCH is for

- **Intent**: Apply a partial modification to an existing resource.
- **Granularity**: Only send the changes, not the entire representation.
- **Standard**: Defined in RFC 5789. Common JSON formats: RFC 6902 (JSON Patch) and RFC 7396 (JSON Merge Patch).

### When to use PATCH vs PUT vs POST

- **PATCH**: You want to update part of a resource. Example: change a user’s `email` and `phone` without sending all user fields.
- **PUT**: You want to completely replace a resource’s representation at a known URI (idempotent). Often requires the full resource body; omitted fields may be cleared/overwritten depending on API contract.
- **POST**: You want to create a subordinate resource under a collection, trigger a server-side command, or perform a non-idempotent processing action. URI is usually the collection or an action endpoint.

### Key differences at a glance

| Aspect                  | PATCH                                                          | PUT                                   | POST                                     |
| ----------------------- | -------------------------------------------------------------- | ------------------------------------- | ---------------------------------------- |
| **Primary purpose**     | Partial update                                                 | Full replace (or create at known URI) | Create under collection or invoke action |
| **Idempotency**         | Not guaranteed (can be designed to be)                         | Guaranteed by spec                    | Not guaranteed                           |
| **Request body**        | Diff/instructions (JSON Patch) or partial object (Merge Patch) | Full resource representation          | New resource data or action payload      |
| **Resource existence**  | Typically must exist                                           | May create or replace if allowed      | Typically creates or processes           |
| **Common status codes** | 200, 204, 409, 412, 415, 422                                   | 200, 201, 204, 409, 412               | 200, 201, 202, 303, 400                  |
| **Bandwidth**           | Minimal (only changes)                                         | Larger (entire resource)              | Varies                                   |

### Bodies and media types for PATCH

- **JSON Merge Patch (RFC 7396)**: `Content-Type: application/merge-patch+json`
  - Body is a partial JSON object. Fields present are merged into the target.
  - `null` means “remove the field.”
  - Simple and human-friendly; no per-operation metadata.
- **JSON Patch (RFC 6902)**: `Content-Type: application/json-patch+json`
  - Body is an ordered array of operations: `add`, `remove`, `replace`, `move`, `copy`, `test`.
  - Precise, supports validation (`test`) and complex paths.

### Example: JSON Merge Patch

```http
PATCH /users/123 HTTP/1.1
Content-Type: application/merge-patch+json
If-Match: "user-v15-etag"

{
  "email": "new@example.com",
  "phone": "+1-555-0100",
  "middleName": null
}
```

- Merges `email` and `phone`, removes `middleName`.
- `If-Match` enforces optimistic concurrency; server returns `412 Precondition Failed` if ETag mismatches.

### Example: JSON Patch

```http
PATCH /users/123 HTTP/1.1
Content-Type: application/json-patch+json
If-Match: "user-v15-etag"

[
  { "op": "test", "path": "/status", "value": "active" },
  { "op": "replace", "path": "/email", "value": "new@example.com" },
  { "op": "remove", "path": "/middleName" }
]
```

- Applies an ordered set of operations; fails atomically if a `test` fails.

### Idempotency and safety

- **Safety**: None of PATCH/PUT/POST are safe (they modify state).
- **Idempotency**:
  - PUT is idempotent by definition (same request can be repeated safely).
  - PATCH is not guaranteed idempotent, but try to design idempotent patches where possible (e.g., use `replace` instead of `add` if the field may already exist; deduplicate server-side by operation IDs).
  - POST is generally non-idempotent; use `Idempotency-Key` or similar to deduplicate.

### Concurrency control

- Use **ETags** with `If-Match` to prevent lost updates (optimistic locking).
- For conditional updates based on current state, JSON Patch’s `test` op helps enforce invariants.

#### How ETag + If-Match enables optimistic concurrency

- **1. Read with ETag**: Client GETs the resource and receives an `ETag` header (e.g., `"v15"`).
- **2. Conditional write**: Client sends `PATCH`/`PUT`/`DELETE` with `If-Match: "v15"`.
- **3. Server compare**: Server compares the current resource ETag with `If-Match`.
  - If equal → apply the update atomically, respond `200/204`, and include a new `ETag` (e.g., `"v16"`).
  - If different → someone else updated first; respond `412 Precondition Failed` and do not modify state.

Minimal failure example:

```http
PATCH /users/123 HTTP/1.1
If-Match: "v15"
Content-Type: application/merge-patch+json

{"email":"new@example.com"}

HTTP/1.1 412 Precondition Failed
ETag: "v16"
```

Best practices:

- Prefer **strong ETags** for write preconditions; weak ETags are intended for caching.
- Require `If-Match` on mutable resources to avoid lost updates in concurrent clients.
- Always return the current `ETag` on `GET` and after successful mutations.
- Combine with JSON Patch `test` operations for state invariants.
- `If-Unmodified-Since` is a weaker alternative and can be clock-skew prone.

### Typical responses

- **200 OK**: Updated resource returned.
- **204 No Content**: Update applied; no body returned.
- **202 Accepted**: Update accepted for async processing.
- **409 Conflict**: Semantic conflict (e.g., invalid operation sequence).
- **412 Precondition Failed**: ETag precondition not met (use `If-Match`).
- **415 Unsupported Media Type**: Wrong `Content-Type`.
- **422 Unprocessable Entity**: Validation failed for a well-formed patch.

### Design guidance and best practices

- **Choose the right patch type**:
  - Prefer **Merge Patch** for simple partial updates.
  - Use **JSON Patch** for precise, ordered operations, or when you need `test`/atomicity.
- **Validate strictly**: Reject paths to forbidden fields, immutable fields, or schema violations. Validate types and formats.
- **Define null semantics**: With Merge Patch, `null` removes fields; document clearly.
- **Use conditional requests**: Require `If-Match` on PATCH and PUT to avoid lost updates.
- **Return minimal responses**: Prefer `204` when the client doesn’t need the body.
- **Auditability**: Log operations; for JSON Patch, log the operation array as submitted.
- **Security**: Whitelist patchable fields; guard against path traversal in JSON Patch pointers; enforce authz checks per field if needed.
- **Versioning**: Consider freezing patch semantics per API version to avoid breaking clients.

### Decision checklist

- Need to update only a subset of fields on an existing resource? → **PATCH**
- Need to replace a resource entirely (or create at a known URI) with an idempotent call? → **PUT**
- Need to create under a collection or invoke a non-idempotent server-side action? → **POST**

### Notes on PUT and POST for comparison

- **PUT**
  - Replaces the resource state at the target URI with the provided representation.
  - If the resource does not exist, some APIs allow creation at the exact URI (idempotent).
  - Requires full representation unless explicitly documented as partial (which blurs semantics).
- **POST**
  - Submits data to be processed; the server decides what to do (create, enqueue, transform, etc.).
  - Commonly used to create resources under a collection (server chooses new URI).
  - Often used for custom actions/commands that don’t map neatly to CRUD.

### Summary

- **PATCH** is for targeted partial updates with minimal payloads; design with conditional requests and clear patch semantics (Merge vs JSON Patch).
- **PUT** is for full, idempotent replacement at a known URI.
- **POST** is for creation under a collection or non-idempotent actions.
