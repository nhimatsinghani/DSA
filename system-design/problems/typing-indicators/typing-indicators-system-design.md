
# Typing Indicators (WhatsApp / Slack): A System Design Deep-Dive

**TL;DR**: Typing indicators are **ephemeral, best-effort, low-latency** events. Clients emit “start/heartbeat/stop” signals; a real‑time backend (usually WebSockets) fans them out to other participants currently **observing** the conversation. Indicators are **not persisted** (or are stored with a short TTL), are **aggressively rate‑limited and debounced**, and in E2EE systems may be **encrypted control messages**. Treat them as **transient load** with strict SLOs (<250–500 ms end‑to‑end) and graceful degradation.

---

## 1) Product & UX goals (why this feature exists)
- Give **immediacy**: “someone is composing” reduces perceived latency.
- Avoid **false promises**: indicators must auto‑expire quickly when the sender stops typing or navigates away.
- Respect **privacy**: indicators are optional in some apps (e.g., Signal lets users disable them). See references.
- **Scope of visibility**:
  - 1:1 chats: only the peer sees it.
  - Group chats: **aggregate** and limit display (“Alice, Bob, +3 are typing…”), avoid spamming the UI.
- Don’t distract: hide indicators if the recipient **isn’t viewing** that conversation.

---

## 2) Functional requirements
- **Emit**: The typing user’s device sends `typing_start` on first keystroke after idle, then **heartbeats** (e.g., every 3–5 s) while typing, and `typing_stop` on send/blur/idle.
- **Fan‑out**: Server broadcasts typing state to **currently‑subscribed** members of the conversation (e.g., those with the chat open and online).
- **Auto‑expiry**: Recipients auto‑clear the UI if no heartbeat is received within a short TTL (e.g., 5–10 s; platform‑specific).
- **Best‑effort semantics**: Missing events must not break UX (UI times out). No delivery or persistence guarantees required.
- **Rate‑limited**: Throttle outbound events per user+conversation; collapse duplicates.
- **Privacy & controls**: Honor per‑user settings (off/blocked/muted), org policy (enterprise), and E2EE design (see §7).

Non‑goals:
- Persisting typing history, audit logs, or searchability.
- Accurate “who is typing” for **everyone** in massive channels; UX typically caps at a small number and aggregates.

---

## 3) High‑level architecture

```
+---------+       WebSocket        +-----------+     Pub/Sub     +-----------+
| ClientA | <--------------------> |  Gateway  |  <----------->  | Channel   |
| (typing)|                        |  Servers  |                 | Servers   |
+---------+                        +-----------+                  +-----------+
      |                                    |                              |
      | typing_start/heartbeat/stop        |                              |
      |----------------------------------->|                              |
      |                                    |   fan-out to subscribers     |
      |                                    |----------------------------->|
      |                                    |                              |
      |                              +-----------+                        |
      |                              | Presence | (optional for gating)   |
      |                              | /Typing  |-------------------------+
      |                              +-----------+
```
**Slack’s** real-time stack publicly describes Gateway Servers (edge WebSocket), Channel Servers (stateful fan‑out), and **transient events** (not persisted) that include **user typing**; transient events follow a slightly different, lightweight path than messages. *See references.*

Key services:
- **Gateway** (edge, multi‑region): terminates WebSockets, authenticates, multiplexes, back‑pressure.
- **Channel/Conversation** service: manages membership, subscriptions, and event fan‑out.
- **Presence/Typing** service: optional ephemeral store for de‑dupe + TTL (e.g., Redis).
- **Membership/ACL**: checks blocklists, DND, org policies.
- **Metrics/Feature flags**: turn off indicators under load; track rate/latency/timeout %.

---

## 4) Client protocol & event model

**Event types** (example):
```jsonc
// From client -> server over WebSocket
{ "type": "typing_start", "conversation_id": "c_123", "user_id": "u_42", "device_id": "d_9", "ts": 1736711112345, "ttl_ms": 8000 }
{ "type": "typing_heartbeat", "conversation_id": "c_123", "user_id": "u_42", "device_id": "d_9", "ts": 1736711118345, "ttl_ms": 8000 }
{ "type": "typing_stop", "conversation_id": "c_123", "user_id": "u_42", "device_id": "d_9", "ts": 1736711120345 }
```
**Server -> recipients** (example broadcast):
```jsonc
{ "type": "user_typing", "conversation_id": "c_123", "user_id": "u_42", "until": 1736711126345 /* client clears after this */ }
```

**Debounce/heartbeat** strategy (typical defaults):
- Fire `typing_start` on first key after **≥2 s idle**.
- Send **heartbeat every 3–5 s** while keystrokes occur; **client clears** after ~8–10 s without heartbeat.
- Send `typing_stop` on send, blur, or **≥5 s idle**.

**Rate limits** (illustrative):
- Per (user, conversation): max 1 `typing_start` per 3 s; heartbeats ≥3 s apart; `typing_stop` always allowed.
- Per connection: cap events/sec to protect Gateway.
- Server drops duplicate starts within TTL; clients ignore repeated events.

---

## 5) Server‑side handling (ephemeral, scalable)

**Recommended semantics**: **at‑most‑once**, **best‑effort**, **non‑persistent**.
- Maintain ephemeral state in Redis (or in‑memory shard) with **keyed TTL**:
  - Key: `typing:{conversation_id}:{user_id}` → value: `{device_id, until_ts}`; `SETEX` with TTL (e.g., 8–10 s).
- On `typing_start`/heartbeat: upsert + publish `user_typing` to the conversation topic; suppress if already “active” and TTL far from expiry (reduces fan‑out).
- On `typing_stop`: delete key and publish `user_typing_clear` (optional); clients also **self‑expire** if missed.
- **Fan‑out policy**:
  - Only to **subscribed/visible** recipients (those with the conversation open + online).
  - For **large channels**: down‑sample (e.g., send top N typers), or aggregate server‑side (“3 people are typing”).
  - Cross‑region: forward via inter‑region bus; prefer **regional GS** delivery first to minimize RTT.

**Failure modes**:
- Dropped event? UI auto‑times‑out.  
- Duplicate event? De‑dupe by (user, conversation) key.  
- Slow consumers? Skip/replace older typing states; keep **latest only**.

---

## 6) Group chats & aggregation

- Keep **cap N** (e.g., show at most 3 names; then “+X more”).  
- **Order**: last activity time.  
- **Sampling**: in channels with hundreds/thousands online, send **aggregate** events at a fixed cadence (e.g., 1 Hz) instead of per‑user updates.  
- **Privacy**: never reveal users to folks who lack access; suppress for muted/ignored members.

---

## 7) E2EE implications (Signal/WhatsApp style)

- **What is encrypted?** In some E2EE messengers, typing indicators are **control messages encrypted on the same channel** as messages (using the conversation or sender keys), so servers can route but **can’t read content** beyond metadata.  
- **Trade‑off**: Encrypting typing can add envelope overhead and require key availability; when recipients are offline, indicators may be silently dropped.  
- **User controls**: many E2EE apps allow disabling typing and read receipts; if either party disables, **don’t send or show**.

**Design**: Place typing as a “low‑priority, non‑retrying” message class in the end‑to‑end transport with **short validity** (drop if not delivered promptly).

---

## 8) API designs (examples & real APIs)

### 8.1 Slack (concept & docs)
- Slack emits a `user_typing` event to clients in the channel via its WebSocket‑based real‑time path. Minimal payload:
```json
{ "type": "user_typing", "channel": "C123456", "user": "U234567" }
```
- Slack categorizes **transient events** (like typing) as **non‑persisted** and routes them through a lightweight fan‑out path alongside real‑time messaging.

### 8.2 WhatsApp Cloud API (Meta)
- Official Cloud API supports **typing indicators** for business integrations by sending a `typing_indicator` field **alongside** other actions (commonly a read receipt) to the `/messages` Graph endpoint, e.g.:
```json
POST /{{Phone-Number-ID}}/messages
{
  "messaging_product": "whatsapp",
  "status": "read",
  "message_id": "<wamid>",
  "typing_indicator": { "type": "text" } // or media-specific
}
```
- For consumer WhatsApp apps, typing indicators are part of the proprietary mobile protocol; specifics aren’t publicly documented, but behavior mirrors the model here: short‑TTL, best‑effort, fan‑out to active participants.

### 8.3 Standards you can learn from
- **XMPP XEP‑0085** defines the canonical **chat states**: `composing`, `paused`, `active`, `inactive`, `gone`, with guidance to **not store offline** and to treat them as chat‑specific presence.
- **IETF RFC‑3994** defines “**is‑composing**” status for instant messaging (SIP/SIMPLE), including refresh/expiry patterns.
- **Matrix** treats typing as **ephemeral** events; client‑server APIs include a `/typing` endpoint with a `timeout` (clients tell “I’m typing in room R for up to T ms”), and server‑server federation sends typing as **EDUs** (ephemeral data units).

### 8.4 Telegram (bots)
- `sendChatAction` (typing/uploading/recording…) is an HTTP call bots use to show activity; the indicator **auto‑expires after a few seconds** unless refreshed. This is a concrete example of **heartbeat + TTL** in practice.

---

## 9) Multi‑device, presence gating, and UI rules

- **Presence gating**: only emit/forward indicators when **both** sides are online and actively viewing the conversation.
- **Multi‑device**: consolidate per user:
  - Server stores one `typing` record per (user, conversation) with **latest device’s** `until`.
  - If one device stops but another continues, heartbeats keep the single record fresh.
- **UI**:
  - Never show indicators if the thread is **backgrounded**.
  - Clear on **send** (outgoing message) or on **timeout** (no heartbeat).
  - In groups, cap the number of names; prefer an **aggregate** string to reduce churn.

---

## 10) Performance, scaling & capacity planning (back‑of‑envelope)

- Assume **1,000,000** concurrent users with **10%** actively typing at any moment → **100,000** active typers.
- If each sends a heartbeat every **4 s**, inbound rate ≈ **25,000 events/s**.  
- For groups with avg **k** recipients viewing, naive fan‑out could be **O(k)** per event. Mitigation:
  - **Presence‑gating** cuts k to those with the chat open (often **≪** total members).
  - **Aggregate** updates in big rooms (e.g., emit once per second per room).
  - **CDN‑like edges**: keep WebSockets regional and do cross‑region fan‑out **once** per event.

**Latency SLOs**: aim for **p95 < 250–500 ms** end‑to‑end (sender keypress → recipient UI update).

---

## 11) Reliability, abuse, and privacy

- **Abuse control**: per‑IP/app‑token throttles; drop events when CPU/back‑pressure crosses thresholds; feature‑flag to disable globally.
- **Privacy**: honor user/org settings; do not emit to blocked users; for E2EE, encrypt control messages; don’t leak membership via indicators to non‑members.
- **Storage**: no long‑term storage; ephemeral keys only; ensure logs don’t capture PII beyond necessary IDs/timestamps.

---

## 12) Implementation sketch (server)

```python
# Pseudocode
def handle_typing_event(evt):
    key = f"typing:{evt.conversation_id}:{evt.user_id}"
    if evt.type in ("typing_start", "typing_heartbeat"):
        ttl = clamp(evt.ttl_ms or 8000, 2000, 15000)
        upsert_ephemeral(key, ttl)  # Redis SETEX
        if should_broadcast(key):   # basic coalescing
            publish("conv:"+evt.conversation_id, {
                "type": "user_typing",
                "user_id": evt.user_id,
                "until": now_ms() + ttl
            })
    elif evt.type == "typing_stop":
        delete(key)
        publish("conv:"+evt.conversation_id, {"type": "user_typing_clear", "user_id": evt.user_id})
```

---

## 13) What interviewers often probe

- **Transport choice**: WebSockets vs. long‑polling vs. server‑sent events; mobile background limits.
- **Fan‑out**: per‑room shards, consistent hashing, regional gateways.
- **Ephemeral store**: Redis (SETEX), in‑memory shards; why **not** Kafka?
- **Semantics**: why best‑effort? why at‑most‑once? how do clients self‑heal?
- **Rate‑limits** and **coalescing** policy: concrete numbers and rationale.
- **E2EE**: do you encrypt typing? what metadata remains visible? trade‑offs.
- **Group scaling**: aggregation strategies + UI compromise.
- **Back‑pressure**: when do you drop vs. delay? feature‑flags & graceful degradation.
- **Testing**: chaos (drop 10–30% events), soak tests, mobile battery/CPU impact.

---

## References & further reading

**Slack**  
- Slack Engineering: *Real‑time Messaging* (transient events such as typing; Gateway/Channel/Presence servers, fan‑out, multi‑region). https://slack.engineering/real-time-messaging/  
- Slack Developer Docs: `user_typing` event reference. https://docs.slack.dev/reference/events/user_typing/  
- Slack Developer Docs: Socket Mode / Events over WebSockets (how Slack delivers events in real‑time). https://docs.slack.dev/apis/events-api/using-socket-mode/

**WhatsApp (Cloud API, official Postman collection by Meta)**  
- *Typing indicators* (request sample with `typing_indicator` on `/messages`). https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api?entity=folder-13382743-9e33ab43-48df-4b61-9a1e-3e70fb8cf29f

**Standards & open protocols**  
- XMPP XEP‑0085: *Chat State Notifications* (composing/paused/active/inactive/gone; servers should not store offline). https://xmpp.org/extensions/xep-0085.html  
- IETF RFC‑3994: *Indication of Message Composition for Instant Messaging* (is‑composing, refresh/expiry). https://www.rfc-editor.org/rfc/rfc3994

**Matrix**  
- Matrix spec (client‑server & server‑server): typing as **ephemeral** EDU over federation; `/typing` client endpoint with timeout semantics is described across spec/issues. Start at client‑server API & EDU overview.  
  - Client‑Server API (index): https://spec.matrix.org/latest/client-server-api/  
  - Server‑Server API (EDUs; typing notifications are ephemeral): https://spec.matrix.org/v1.14/server-server-api/  
  - Context from spec discussion referencing `/rooms/{roomId}/typing/{userId}` with `timeout`: https://github.com/matrix-org/matrix-spec/issues/411

**Signal (E2EE example)**  
- Signal Support: *Typing Indicators* (encrypted via Signal Protocol; sealed sender when possible; user‑controllable). https://support.signal.org/hc/en-us/articles/360020798451-Typing-Indicators

**Telegram (bot example of TTL/heartbeat semantics)**  
- Bot API: `sendChatAction` (typing/uploading/recording actions). https://core.telegram.org/bots/api  
- Helpful summary of the auto‑expiry behavior (typing status ~5 s unless refreshed): https://rdrr.io/cran/telegram.bot/man/sendChatAction.html

---

## Appendix: Quick comparison table

| Aspect | Slack‑like enterprise chat | WhatsApp/Signal‑like E2EE | Bot platforms (Telegram) |
|---|---|---|---|
| Transport | WebSocket gateway + channel shards | App‑specific encrypted control messages + push or socket | HTTPS API calls to show activity |
| Persistence | **None** (transient events) | **None** (dropped if late) | **None**; expires in seconds |
| Fan‑out scope | Only subscribers viewing the thread | Only active participants; server may not read content | Only the target user(s) of the bot |
| Rate‑limits | Strict throttles + coalescing | Strict throttles; often not retried | Must refresh action every few seconds |
| E2EE | Typically not (unless product supports) | Yes; encrypted typing control messages | N/A (bots), server‑side controlled |

---

*Prepared for system design interviews: contains architecture, event semantics, scaling math, E2EE trade‑offs, and links to primary sources.*
