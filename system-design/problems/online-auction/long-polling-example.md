### Long-polling for Online Auction: Keep users updated with latest max bid

Below is a practical implementation of long-polling to push the latest max bid to clients viewing an auction item. This uses a simple in-memory approach for clarity, plus notes on scaling.

---

### Server (Node.js + Express)

- **Key idea**: hold each client request open up to 30–40s; if a newer bid appears first, respond immediately; otherwise, timeout so the client re-polls.
- **Protocol**:
  - Client calls `GET /items/:id/max-bid/long-poll?lastVersion=123`.
  - Server responds immediately if there’s a newer version than `lastVersion`, else waits until update or timeout.
  - Bids are placed via `POST /items/:id/bid { amount }`, which updates state and wakes waiting requests.

```javascript
// server.js
const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// In-memory store (use a DB/Redis in production)
const itemState = new Map(); // itemId -> { maxBid: number, version: number }
const waiters = new Map(); // itemId -> Set<{ res, timer }>

function getState(itemId) {
  if (!itemState.has(itemId)) {
    itemState.set(itemId, { maxBid: 0, version: 0 });
  }
  return itemState.get(itemId);
}

function getWaiterSet(itemId) {
  if (!waiters.has(itemId)) {
    waiters.set(itemId, new Set());
  }
  return waiters.get(itemId);
}

function notifyWaiters(itemId) {
  const { maxBid, version } = getState(itemId);
  const ws = getWaiterSet(itemId);
  for (const w of ws) {
    clearTimeout(w.timer);
    try {
      w.res.status(200).json({ maxBid, version });
    } catch (_) {}
  }
  ws.clear();
}

// Long-poll endpoint
app.get("/items/:id/max-bid/long-poll", (req, res) => {
  const itemId = req.params.id;
  const clientVersion = Number(req.query.lastVersion || 0);
  const timeoutMs = 35000; // 35s

  const state = getState(itemId);

  // If server has newer state, return immediately
  if (state.version > clientVersion) {
    return res
      .status(200)
      .json({ maxBid: state.maxBid, version: state.version });
  }

  // Otherwise, hold the request open until new bid or timeout
  const ws = getWaiterSet(itemId);
  const waiter = { res, timer: null };

  // Cleanup if client disconnects
  req.on("close", () => {
    if (ws.has(waiter)) {
      clearTimeout(waiter.timer);
      ws.delete(waiter);
    }
  });

  waiter.timer = setTimeout(() => {
    // No change — advise client to re-poll
    try {
      res.status(204).end();
    } catch (_) {}
    ws.delete(waiter);
  }, timeoutMs);

  ws.add(waiter);
});

// Place a bid and wake any waiters
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

  // Update state (ideally, do this atomically in DB/Redis with version increment)
  state.maxBid = amount;
  state.version += 1;

  // Respond to bidder
  res.status(201).json({ maxBid: state.maxBid, version: state.version });

  // Notify long-polling clients
  notifyWaiters(itemId);
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Auction server listening on ${port}`));
```

- **What to notice**:
  - **Versioning**: `version` increments every accepted bid; clients track `lastVersion`.
  - **Fast-path**: if server `version > lastVersion` → respond immediately with latest.
  - **Waiters**: per-item `Set` of pending responses; when a new bid arrives, all are answered.
  - **Timeout**: 35s returns 204 so client re-issues request, keeping the connection fresh.
  - **Disconnect cleanup**: remove waiter on `req.close` to prevent leaks.

---

### Client (Browser, Fetch + AbortController)

- **Loop**: call long-poll with `lastVersion`; if 200, update UI and version; if 204, simply re-poll.
- **Abort**: cancel on page leave/navigation; backoff on errors.

```javascript
// auctionLongPoll.js
let lastVersion = 0;
let stop = false;
let controller = null;

function stopPolling() {
  stop = true;
  if (controller) controller.abort();
}

async function longPollMaxBid(baseUrl, itemId, onUpdate) {
  const endpoint = `${baseUrl}/items/${encodeURIComponent(
    itemId
  )}/max-bid/long-poll?lastVersion=${lastVersion}`;
  controller = new AbortController();

  try {
    const response = await fetch(endpoint, {
      signal: controller.signal,
      cache: "no-store",
    });

    if (response.status === 200) {
      const { maxBid, version } = await response.json();
      lastVersion = version;
      onUpdate({ maxBid, version });
    }
    // 204: no change — just fall through to re-poll
  } catch (err) {
    if (err.name !== "AbortError") {
      // transient error; short backoff
      await new Promise((r) => setTimeout(r, 1000));
    }
  }

  if (!stop) {
    // small jitter to avoid sync thundering herds
    const jitterMs = Math.floor(Math.random() * 150);
    await new Promise((r) => setTimeout(r, jitterMs));
    return longPollMaxBid(baseUrl, itemId, onUpdate);
  }
}

// Example usage
// longPollMaxBid('http://localhost:3000', 'item-123', ({ maxBid }) => {
//   document.querySelector('#maxBid').textContent = `$${maxBid.toFixed(2)}`;
// });
// window.addEventListener('beforeunload', stopPolling);
```

- **What to notice**:
  - **State carry**: `lastVersion` maintained locally to avoid missing updates.
  - **Status handling**: 200 → update UI; 204 → re-poll immediately; network errors → short backoff.
  - **Abortable**: cancels in-flight request on navigation to free resources.

---

### Bid Submit (Client) — minimal example

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

---

### Concurrency, correctness, and scaling notes

- **Atomicity**: protect bid updates with an atomic compare-and-set in the DB, or using Redis scripts to avoid race conditions.
- **Horizontal scaling**: in-memory waiters break across multiple instances; use a shared broker.
  - Option 1: **Redis Pub/Sub** — each instance subscribes to `item:{id}` and publishes on updates; instances wake their own local waiters.
  - Option 2: **Sticky sessions** — route the same item or user to the same instance (still need atomic writes in DB/Redis).
- **Timeout tuning**: 25–40s is common; keep under intermediary idle timeouts.
- **Fallbacks**: if the environment blocks long-poll, degrade to short poll (e.g., 2–5s interval) or upgrade to SSE/WebSocket where possible.
- **Thundering herd**: add small jitter between re-polls; consider staggering timeouts.
- **Response shape**: include `version`, `maxBid`, and optionally `itemId` and `updatedAt` for auditing.

---

### Redis Pub/Sub integration (multi-instance)

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
// Integrate with server.js (sketch)
// On bid update:
//   state.maxBid = amount; state.version += 1;
//   await publishUpdate(itemId, { maxBid: state.maxBid, version: state.version });
// At startup per instance:
//   subscribeItem('*') // pattern or subscribe per active item
//   on message: update local cache and notifyWaiters(itemId)
```

- **What to notice**:
  - Each instance handles its own HTTP long-poll connections.
  - Updates are fanned out through Redis so all instances notify their waiting clients.

---

### Test quickly

- Run server: `node server.js`
- Open two tabs on the same item; place a bid in one and observe instant update in the other.

This setup provides a clear, production-ready pathway: start with in-memory long-poll, then swap state/notifications to Redis or your DB’s notify features to scale horizontally while keeping the long-poll semantics unchanged.
