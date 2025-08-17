## Problem

Imagine we are building an application that is used by many different customers. We want to avoid one customer being able to overload the system by sending too many requests, so we enforce a per-customer rate limit. The rate limit is defined as: “Each customer can make X requests per Y seconds”.

Assuming that customer ID is extracted somehow from the request, implement:

- Signature (compatibility helper): `rate_limit(customer_id: int) -> bool`
- Object API: `RateLimiter.allow(customer_id: int) -> bool`

### Design Overview

- `RateLimitPolicy`: immutable configuration with validation
- `Clock` abstraction: `SystemClock` (prod), `ManualClock` (tests)
- `RateLimitStrategy` interface + implementations:
  - `FixedWindowStrategy`
  - `SlidingWindowLogStrategy`
  - `TokenBucketStrategy`
- `RateLimiter` facade: default and per-customer policy overrides, delegates to strategy

Files:

- `rate_limiter.py` (implementation)
- `test_rate_limiter.py` (unit tests)
- `run_tests.py` (test runner)

## Clean Code and Design Principles Applied

- **Single Responsibility (SRP)**: Each class has one reason to change.

  - `RateLimitPolicy` only models configuration and validates inputs.
  - `Clock` implements time retrieval; `ManualClock` adds test control.
  - Each `RateLimitStrategy` encapsulates exactly one algorithm (fixed window, sliding window log, token bucket).
  - `RateLimiter` coordinates policy selection and delegates enforcement to a strategy.

- **Open/Closed Principle (OCP)**: Behavior is extensible without modifying existing code.

  - Add a new strategy by implementing `RateLimitStrategy.allow(...)` and inject it into `RateLimiter`.
  - Add per-customer limits with `RateLimiter.set_policy_for_customer(...)` without touching strategy code.

- **Liskov Substitution Principle (LSP)**: Strategies are interchangeable.

  - All strategies implement the same `allow(customer_id, policy) -> bool` contract.
  - Callers depend only on the interface, not concrete implementations.

- **Interface Segregation Principle (ISP)**: Small, focused interfaces.

  - `Clock` exposes just `now()`.
  - `RateLimitStrategy` exposes just `allow(...)`.

- **Dependency Inversion Principle (DIP)**: Depend on abstractions, not concretions.

  - `RateLimitStrategy` depends on `Clock` (abstraction) rather than `time` directly.
  - `RateLimiter` depends on the `RateLimitStrategy` abstraction via constructor injection.

- **Encapsulation and Information Hiding**:

  - Internal state (maps of counters, queues, buckets, and locks) is private to each strategy.
  - Only minimal, intention-revealing public APIs are exposed: `RateLimiter.allow(...)`, `set_policy_for_customer(...)`, and a small compatibility `rate_limit(...)` function.

- **Immutability Where Appropriate**:

  - `RateLimitPolicy` is a `@dataclass(frozen=True)` to prevent accidental mutation once constructed.
  - This improves thread-safety and predictability.

- **Input Validation and Fail-Fast**:

  - `RateLimitPolicy.__post_init__` enforces `max_requests > 0` and `window_seconds > 0`.
  - `ManualClock.advance` rejects negative advances to prevent time reversals.

- **Testability by Design**:

  - Time is abstracted behind `Clock`. Tests use `ManualClock` to deterministically simulate time passage.
  - Strategies are pure with respect to external systems (no I/O), enabling fast, reliable unit tests.
  - Small, isolated units with clear contracts make behavior-driven tests straightforward.

- **Determinism and Time Source Correctness**:

  - Production code uses `time.monotonic()` via `SystemClock` to avoid issues with wall-clock changes (NTP, DST, manual adjustments).

- **Thread-Safety Considerations**:

  - Per-customer `threading.Lock` maps in strategies ensure correct updates under concurrency for a single customer.
  - Granular locking avoids global contention. (This design is suitable for process-level concurrency; a distributed store would be needed for multi-process/multi-node coordination.)

- **DRY and Reuse**:

  - Common concerns (time access, policy validation) are centralized: `Clock`, `RateLimitPolicy`.
  - The facade (`RateLimiter`) consolidates policy lookup and delegation instead of duplicating this across strategies.

- **Cohesive, Intention-Revealing Names**:

  - Verbose class, method, and variable names clarify intent (`SlidingWindowLogStrategy`, `RateLimitPolicy`, `get_policy_for_customer`).
  - Avoids abbreviations and magic values; parameters like `window_seconds` are explicit.

- **Small Public API and Symmetry**:

  - Minimal entry points: `RateLimiter.allow(...)` and `rate_limit(...)`.
  - Symmetric configuration: default policy + optional per-customer overrides via `set_policy_for_customer` and `get_policy_for_customer`.

- **Separation of Concerns**:

  - Measurement (time) is separated from policy definition and from enforcement algorithm.
  - Configuration (policies) is separated from runtime decision logic (strategies).

- **Algorithmic Trade-offs Documented and Encapsulated**:

  - `FixedWindowStrategy`: O(1) memory/time; simple but susceptible to window-boundary bursts.
  - `SlidingWindowLogStrategy`: accurate rolling window; evicts timestamps older than `window_seconds`.
  - `TokenBucketStrategy`: allows short bursts while enforcing average rate; O(1) state and time per call.
  - Choosing a strategy is a construction-time decision, not a code change.

- **Compatibility and Migration Path**:

  - Provided `rate_limit(customer_id)` as a thin wrapper over a default `RateLimiter` so legacy-style code can adopt the new design incrementally.

- **Locality and Modularity**:

  - Each strategy keeps its state and locking local, improving cache-locality and keeping modules loosely coupled.

- **Readable Tests as Living Documentation**:

  - Tests describe expected behavior: boundary conditions, per-customer isolation, bursting and refilling, and window rollovers.

- **Future Extensibility (documented path)**:
  - To support distributed limits (multi-process/multi-node), introduce a storage abstraction (e.g., `EventStore` or `BucketStore`) backed by Redis. Only the strategy implementations would change to use that store; the facade and policies remain untouched.
  - New strategies (e.g., Leaky Bucket, GCRA) can be added by implementing `RateLimitStrategy` and injecting them.

## Token Bucket: How it works and why it allows short bursts

- **Core idea**:

  - You have a bucket that can hold up to `C = max_requests` tokens (capacity).
  - Tokens are refilled at a constant rate `r = C / window_seconds` tokens per second.
  - Each request consumes exactly 1 token. A request is allowed only if there is at least 1 token available.
  - The bucket never holds more than `C` tokens (excess refills are capped).

- **Math (per request)**:

  - Let `now` be the current time and `last_refill` the time we last updated the bucket.
  - Refill: `tokens = min(C, tokens + (now - last_refill) * r)`; then set `last_refill = now`.
  - Decision: if `tokens >= 1`, allow and set `tokens -= 1`; otherwise deny.

- **Why short bursts are allowed**:

  - If the system has been idle, tokens accumulate up to capacity `C`.
  - When traffic arrives suddenly, up to `C` requests can be accepted immediately (one per token), forming a burst.
  - After the burst depletes the bucket, acceptance falls back to the average rate `r` as tokens trickle in over time.

- **Example timeline** (policy: 5 requests per 5 seconds ⇒ `C=5`, `r=1 token/sec`):

  - t=0s: bucket starts full at 5 tokens → first 5 requests are all allowed instantly.
  - Immediately after: tokens=0 → the 6th immediate request is denied.
  - t=2s: 2 tokens have refilled → 2 more requests can be accepted.
  - t=5s: bucket is full again (5 tokens) if unused → another burst of up to 5 is possible.

- **Benefits vs fixed/sliding windows**:

  - Avoids window-boundary spikes while still preserving an average rate.
  - Allows controlled bursts after idle periods (good UX and throughput under spiky workloads).
  - Constant O(1) state and time per decision (no per-event logs needed).

- **In this implementation** (see `TokenBucketStrategy` in `rate_limiter.py`):
  - State per customer: `{ tokens: float, last_refill: float }`.
  - Refill uses monotonic time to avoid clock jumps.
  - Uses fractional tokens internally for precision; each request consumes 1.0 token.

## Usage

- Construct a limiter with a chosen strategy and default policy:

```python
from rate_limiter import RateLimiter, RateLimitPolicy, SlidingWindowLogStrategy

limiter = RateLimiter(
    strategy=SlidingWindowLogStrategy(),
    default_policy=RateLimitPolicy(max_requests=5, window_seconds=1.0),
)

# Optional: override for a specific customer
limiter.set_policy_for_customer(42, RateLimitPolicy(max_requests=100, window_seconds=60.0))

# Decide a request
allowed = limiter.allow(customer_id=42)
```

- Compatibility helper that mirrors the original signature:

```python
from rate_limiter import rate_limit

if rate_limit(customer_id=123):
    # proceed
    pass
else:
    # reject / throttle
    pass
```

## Testing

Run tests:

```bash
/usr/bin/python3 /Users/nishanthimath/PycharmProjects/DSA/problem-solving/lld/rate-limiter/run_tests.py
```

Tests use `ManualClock` to deterministically model time passage, ensuring reliable, fast unit tests that are independent of the system clock.
