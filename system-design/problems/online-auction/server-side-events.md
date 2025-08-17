### Server-Sent Events (SSE) for Online Auction: streaming latest max bid

SSE lets the server push events to the client over a single long-lived HTTP connection. Perfect for broadcasting the latest max bid to everyone viewing an item.

---

### Core concepts for this use case

- **One-way stream (server ➜ client)**: Clients subscribe; server pushes updates. Clients still place bids over normal HTTP `POST`.
- **Auto-reconnect**: Browsers reconnect SSE automatically. You can suggest a retry delay with `retry:`.
- **Event format**: Lines like `event: <type>`, `id: <eventId>`, `data: <json>` ended by a blank line.
- **Resume with Last-Event-ID**: Client sends `Last-Event-ID` header; server can use it to send the latest state.
- **Heartbeats**: Send comments (`: ping`) to keep intermediaries from closing idle streams.

---

### Server (Node.js + Express)

- **Endpoints**:
  - `GET /items/:id/max-bid/sse`: open an `text/event-stream` and keep it alive; push updates.
  - `POST /items/:id/bid { amount }`: validate and update state, broadcast to all SSE clients for that item.
- **State**:
  - Per-item `{ maxBid, version }` (version increments per accepted bid).
  - Per-item `Set` of subscribers holding their `res` and heartbeat timer.

```javascript
// sse-server.js
const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// In-memory state (replace with DB/Redis in production)
const itemState = new Map(); // itemId -> { maxBid: number, version: number }
const subscribers = new Map(); // itemId -> Set<{ res, heartbeat }>

function getState(itemId) {
  if (!itemState.has(itemId)) {
    itemState.set(itemId, { maxBid: 0, version: 0 });
  }
  return itemState.get(itemId);
}

function getSubs(itemId) {
  if (!subscribers.has(itemId)) {
    subscribers.set(itemId, new Set());
  }
  return subscribers.get(itemId);
}

function sseWrite(res, lines) {
  // lines: array of strings without trailing newlines
  res.write(lines.join("\n") + "\n\n");
}

function broadcastMaxBid(itemId) {
  const { maxBid, version } = getState(itemId);
  const subs = getSubs(itemId);
  for (const sub of subs) {
    try {
      sseWrite(sub.res, [
        "event: maxBid",
        `id: ${version}`,
        `data: ${JSON.stringify({ itemId, maxBid, version })}`,
      ]);
    } catch (_) {
      // Ignore write errors; close will clean up
    }
  }
}

app.get("/items/:id/max-bid/sse", (req, res) => {
  const itemId = req.params.id;
  const { maxBid, version } = getState(itemId);
  const lastEventId = req.get("Last-Event-ID") || req.query.lastVersion;

  // Set SSE headers
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache, no-transform");
  res.setHeader("Connection", "keep-alive");
  // If using a reverse proxy, ensure it does not buffer; disable gzip.

  // Flush headers so client starts processing
  if (res.flushHeaders) res.flushHeaders();

  // Register subscriber
  const subs = getSubs(itemId);
  const subscriber = { res, heartbeat: null };
  subs.add(subscriber);

  // On disconnect, cleanup to avoid leaks
  req.on("close", () => {
    clearInterval(subscriber.heartbeat);
    subs.delete(subscriber);
    try {
      res.end();
    } catch (_) {}
  });

  // Initial retry suggestion (client can override)
  sseWrite(res, ["retry: 5000"]); // 5s reconnect hint

  // Heartbeat every 15s to keep connection open through proxies
  subscriber.heartbeat = setInterval(() => {
    try {
      res.write(": ping\n\n");
    } catch (_) {}
  }, 15000);

  // Send the latest snapshot immediately if the client is behind
  const clientVersion = Number(lastEventId || 0);
  if (version > clientVersion) {
    sseWrite(res, [
      "event: maxBid",
      `id: ${version}`,
      `data: ${JSON.stringify({ itemId, maxBid, version })}`,
    ]);
  }
});

app.post("/items/:id/bid", (req, res) => {
  const itemId = req.params.id;
  const { amount } = req.body;

  if (typeof amount !== "number" || amount <= 0) {
    return res.status(400).json({ error: "Invalid amount" });
  }

  const state = getState(itemId);
  if (amount <= state.maxBid) {
    return res
      .status(409)
      .json({
        error: "Bid must be greater than current max bid",
        currentMaxBid: state.maxBid,
      });
  }

  // Update state atomically in real systems
  state.maxBid = amount;
  state.version += 1;

  res.status(201).json({ maxBid: state.maxBid, version: state.version });

  // Push to all subscribers
  broadcastMaxBid(itemId);
});

const port = process.env.PORT || 3001;
app.listen(port, () => console.log(`SSE auction server listening on ${port}`));
```

- **What to notice**:
  - **SSE headers**: `Content-Type: text/event-stream`, `Connection: keep-alive`, `Cache-Control: no-cache`.
  - **Event format**: `event`, `id`, `data` lines, blank line terminator. `id` set to `version` so clients can resume.
  - **Heartbeat**: `: ping` comments to avoid idle timeouts.
  - **Immediate snapshot**: on connect, if server `version` > client’s `Last-Event-ID`, send the latest state.
  - **Broadcast**: iterate all subscribers for an item and `res.write` the event.

---

### Client (Browser EventSource)

- **Subscribe**: one `EventSource` per item stream.
- **Handlers**: listen for `maxBid` events; handle reconnects; close on navigation.
- **Resume**: Browser sends `Last-Event-ID` automatically if the server sets `id:` on events.

```html
<!-- index.html -->
<div>Max Bid: <span id="maxBid">$0.00</span></div>
<script>
  const baseUrl = "http://localhost:3001";
  const itemId = "item-123";

  const es = new EventSource(
    `${baseUrl}/items/${encodeURIComponent(itemId)}/max-bid/sse`
  );

  es.addEventListener("open", () => {
    console.log("SSE connected");
  });

  es.addEventListener("maxBid", (evt) => {
    const payload = JSON.parse(evt.data);
    document.querySelector("#maxBid").textContent = `$${Number(
      payload.maxBid
    ).toFixed(2)}`;
    // evt.lastEventId === payload.version (as string)
  });

  es.addEventListener("error", (err) => {
    // Browser will auto-reconnect based on server 'retry:' hint; no need to manual loop
    console.warn("SSE error, will retry automatically", err);
  });

  window.addEventListener("beforeunload", () => es.close());
</script>
```

- **What to notice**:
  - **`EventSource`**: native browser API; handles reconnects and `Last-Event-ID`.
  - **Typed events**: using `event: maxBid` enables `addEventListener('maxBid', ...)`.
  - **Close**: call `es.close()` to release the connection when leaving the page.

---

### Placing bids (Client)

```javascript
async function placeBid(baseUrl, itemId, amount) {
  const res = await fetch(
    `${baseUrl}/items/${encodeURIComponent(itemId)}/bid`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Failed with ${res.status}`);
  }
  return res.json();
}
```

- **What to notice**:
  - **SSE is one-way**; use normal HTTP for writes.
  - On success, all viewers receive `maxBid` events instantly.

---

### Operational considerations and scaling

- **Concurrency/atomicity**: Use a DB transaction or Redis script to ensure only strictly higher bids are accepted and `version` increments atomically.
- **Horizontal scaling**: Share updates across instances.
  - Option 1: **Redis Pub/Sub** for fanout; each instance subscribes and broadcasts to its local SSE clients.
  - Option 2: **Message broker** (Kafka/NATS) with a consumer per instance.
- **Reverse proxy timeouts**: Increase idle/read timeouts (e.g., Nginx `proxy_read_timeout 60s+`). Disable buffering for SSE.
- **Compression**: Do not gzip SSE; many proxies buffer compressed responses which breaks streaming.
- **Connection limits**: Browsers limit concurrent HTTP/2 streams/tabs; consider sharding pages or using a single multiplexed stream per user if needed.
- **Auth**: Send a bearer token/cookie on initial request; validate and keep connection. Rotate tokens via reconnect.
- **Backpressure**: SSE is text-based and push-only; for extremely high update rates, consider coalescing (send latest snapshot, not every intermediate version).

---

### Redis Pub/Sub sketch (multi-instance)

```javascript
// pubsub.js
const { createClient } = require("redis");

const pub = createClient({ url: process.env.REDIS_URL });
const sub = createClient({ url: process.env.REDIS_URL });
await pub.connect();
await sub.connect();

function topic(itemId) {
  return `auction:item:${itemId}`;
}

async function publishUpdate(itemId, payload) {
  await pub.publish(topic(itemId), JSON.stringify(payload));
}

function subscribeItem(itemId, onMessage) {
  return sub.subscribe(topic(itemId), (msg) => onMessage(JSON.parse(msg)));
}

module.exports = { publishUpdate, subscribeItem };
```

```javascript
// sse-server.js integration (sketch)
// On bid acceptance:
//   state.maxBid = amount; state.version += 1;
//   await publishUpdate(itemId, { itemId, maxBid: state.maxBid, version: state.version });
// On instance startup:
//   subscribeItem('*') // or subscribe per active item
//   On message: update local cache and broadcastMaxBid(itemId)
```

- **What to notice**:
  - Each instance keeps its own subscriber sets.
  - Updates are fanned out via Redis so all instances push to their connected clients.

---

### Quick test

- Run server: `node sse-server.js`
- Connect from a browser to `http://localhost:3001/items/item-123/max-bid/sse` (watch console).
- `curl -X POST -H 'Content-Type: application/json' \
-d '{"amount": 101.5}' http://localhost:3001/items/item-123/bid`
- Observe the browser updates immediately.

---

### SSE vs Long-polling (quick notes)

- **Latency**: Both are low-latency; SSE avoids repeated request overhead.
- **Load**: SSE maintains 1 open TCP/HTTP stream; long-poll cycles every 25–40s.
- **Compatibility**: SSE is widely supported on modern browsers; fallback to long-poll for legacy/locked-down environments.
- **Directionality**: SSE is server➜client only; use HTTP/WebSocket for client➜server.

This example gives you production-ready patterns for implementing SSE in an online auction, including correctness, resource management, and horizontal scaling.
