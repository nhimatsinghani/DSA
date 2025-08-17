from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional


# ---------- Time Abstraction ----------

class Clock(ABC):
    """Abstraction over time source for deterministic testing."""

    @abstractmethod
    def now(self) -> float:
        """Return current time in seconds (monotonic preferred)."""
        raise NotImplementedError


class SystemClock(Clock):
    def now(self) -> float:
        # Use monotonic to avoid issues when system clock changes
        return time.monotonic()


class ManualClock(Clock):
    """Manually controlled clock for tests."""

    def __init__(self, start: float = 0.0) -> None:
        self._t = start

    def now(self) -> float:
        return self._t

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("Cannot go back in time")
        self._t += seconds


# ---------- Policy ----------

@dataclass(frozen=True)
class RateLimitPolicy:
    max_requests: int
    window_seconds: float

    def __post_init__(self) -> None:
        if self.max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")


# ---------- Strategy Abstraction ----------

class RateLimitStrategy(ABC):
    """Strategy determines how the allowance within a window is computed."""

    def __init__(self, clock: Optional[Clock] = None) -> None:
        self._clock: Clock = clock or SystemClock()

    @abstractmethod
    def allow(self, customer_id: int, policy: RateLimitPolicy) -> bool:
        """Return True if the request is allowed, False otherwise."""
        raise NotImplementedError


# ---------- Fixed Window Counter ----------

class FixedWindowStrategy(RateLimitStrategy):
    """Simple 'X requests per Y seconds' using fixed windows.

    Pros: Very fast and memory efficient
    Cons: Boundary effects at window edges
    """

    def __init__(self, clock: Optional[Clock] = None) -> None:
        super().__init__(clock)
        self._window_start_by_customer: Dict[int, float] = {}
        self._count_by_customer: Dict[int, int] = defaultdict(int)
        self._locks: Dict[int, threading.Lock] = defaultdict(threading.Lock)

    def allow(self, customer_id: int, policy: RateLimitPolicy) -> bool:
        lock = self._locks[customer_id]
        with lock:
            now = self._clock.now()
            window_start = self._window_start_by_customer.get(customer_id)

            if window_start is None or now - window_start >= policy.window_seconds:
                self._window_start_by_customer[customer_id] = now
                self._count_by_customer[customer_id] = 0

            current_count = self._count_by_customer[customer_id]
            if current_count < policy.max_requests:
                self._count_by_customer[customer_id] = current_count + 1
                return True
            return False


# ---------- Sliding Window Log ----------

class SlidingWindowLogStrategy(RateLimitStrategy):
    """Tracks timestamps in a sliding window to avoid boundary spikes.

    Pros: Accurate rolling window
    Cons: Memory grows with number of events within window
    """

    def __init__(self, clock: Optional[Clock] = None) -> None:
        super().__init__(clock)
        self._events_by_customer: Dict[int, Deque[float]] = defaultdict(deque)
        self._locks: Dict[int, threading.Lock] = defaultdict(threading.Lock)

    def allow(self, customer_id: int, policy: RateLimitPolicy) -> bool:
        lock = self._locks[customer_id]
        with lock:
            now = self._clock.now()
            cutoff = now - policy.window_seconds
            q = self._events_by_customer[customer_id]

            # Evict old events
            while q and q[0] <= cutoff:
                q.popleft()

            if len(q) < policy.max_requests:
                q.append(now)
                return True
            return False


# ---------- Token Bucket ----------

@dataclass
class _Bucket:
    tokens: float
    last_refill: float


class TokenBucketStrategy(RateLimitStrategy):
    """Token bucket rate limiter.

    Allows short bursts while enforcing average rate of X per Y seconds.
    """

    def __init__(self, clock: Optional[Clock] = None) -> None:
        super().__init__(clock)
        self._bucket_by_customer: Dict[int, _Bucket] = {}
        self._locks: Dict[int, threading.Lock] = defaultdict(threading.Lock)

    def allow(self, customer_id: int, policy: RateLimitPolicy) -> bool:
        lock = self._locks[customer_id]
        with lock:
            now = self._clock.now()
            capacity = float(policy.max_requests)
            rate_per_sec = capacity / policy.window_seconds

            bucket = self._bucket_by_customer.get(customer_id)
            if bucket is None:
                bucket = _Bucket(tokens=capacity, last_refill=now)
                self._bucket_by_customer[customer_id] = bucket

            # Refill tokens
            elapsed = max(0.0, now - bucket.last_refill)
            if elapsed > 0:
                bucket.tokens = min(capacity, bucket.tokens + elapsed * rate_per_sec)
                bucket.last_refill = now

            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True
            return False


# ---------- Facade ----------

class RateLimiter:
    """High-level facade that delegates to a chosen strategy.

    Supports a default policy and optional per-customer overrides.
    Thread-safe per customer via internal locks used by the strategies.
    """

    def __init__(
        self,
        strategy: RateLimitStrategy,
        default_policy: RateLimitPolicy,
        per_customer_policy: Optional[Dict[int, RateLimitPolicy]] = None,
    ) -> None:
        self._strategy = strategy
        self._default_policy = default_policy
        self._per_customer_policy = per_customer_policy or {}

    def set_policy_for_customer(self, customer_id: int, policy: RateLimitPolicy) -> None:
        self._per_customer_policy[customer_id] = policy

    def get_policy_for_customer(self, customer_id: int) -> RateLimitPolicy:
        return self._per_customer_policy.get(customer_id, self._default_policy)

    def allow(self, customer_id: int) -> bool:
        policy = self.get_policy_for_customer(customer_id)
        return self._strategy.allow(customer_id, policy)


# ---------- Simple compatibility API (as in README) ----------

# For convenience, expose a simple module-level function with a default limiter
# This mirrors: boolean rateLimit(int customerId)
_default_limiter: Optional[RateLimiter] = None


def _get_default_limiter() -> RateLimiter:
    global _default_limiter
    if _default_limiter is None:
        # Default: 5 requests per 1 second using sliding window log
        default_policy = RateLimitPolicy(max_requests=5, window_seconds=1.0)
        _default_limiter = RateLimiter(
            strategy=SlidingWindowLogStrategy(),
            default_policy=default_policy,
        )
    return _default_limiter


def rate_limit(customer_id: int) -> bool:
    """Compatibility helper. Configure using _get_default_limiter if needed."""
    return _get_default_limiter().allow(customer_id) 