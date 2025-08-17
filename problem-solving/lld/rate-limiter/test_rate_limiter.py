import unittest

from rate_limiter import (
    ManualClock,
    RateLimitPolicy,
    FixedWindowStrategy,
    SlidingWindowLogStrategy,
    TokenBucketStrategy,
    RateLimiter,
)


class TestFixedWindowStrategy(unittest.TestCase):
    def test_allows_up_to_limit_then_blocks_until_next_window(self):
        clock = ManualClock(start=0.0)
        policy = RateLimitPolicy(max_requests=3, window_seconds=10.0)
        strategy = FixedWindowStrategy(clock=clock)

        # 3 allowed
        self.assertTrue(strategy.allow(1, policy))
        self.assertTrue(strategy.allow(1, policy))
        self.assertTrue(strategy.allow(1, policy))
        # 4th denied
        self.assertFalse(strategy.allow(1, policy))

        # Advance within same window -> still denied
        clock.advance(9.0)
        self.assertFalse(strategy.allow(1, policy))

        # Next window -> reset
        clock.advance(1.0)
        self.assertTrue(strategy.allow(1, policy))

    def test_isolated_customers(self):
        clock = ManualClock(start=0.0)
        policy = RateLimitPolicy(max_requests=1, window_seconds=5.0)
        strategy = FixedWindowStrategy(clock=clock)

        self.assertTrue(strategy.allow(1, policy))
        self.assertFalse(strategy.allow(1, policy))
        # Different customer unaffected
        self.assertTrue(strategy.allow(2, policy))


class TestSlidingWindowLogStrategy(unittest.TestCase):
    def test_rolling_window_eviction(self):
        clock = ManualClock(start=0.0)
        policy = RateLimitPolicy(max_requests=2, window_seconds=5.0)
        strategy = SlidingWindowLogStrategy(clock=clock)

        # t=0, allow twice
        self.assertTrue(strategy.allow(1, policy))
        self.assertTrue(strategy.allow(1, policy))
        self.assertFalse(strategy.allow(1, policy))

        # After 5s, earliest entries evicted -> allow again
        clock.advance(5.01)
        self.assertTrue(strategy.allow(1, policy))

    def test_per_customer_independence(self):
        clock = ManualClock()
        policy = RateLimitPolicy(max_requests=1, window_seconds=1.0)
        strategy = SlidingWindowLogStrategy(clock=clock)

        self.assertTrue(strategy.allow(10, policy))
        self.assertFalse(strategy.allow(10, policy))
        self.assertTrue(strategy.allow(11, policy))


class TestTokenBucketStrategy(unittest.TestCase):
    def test_burst_and_refill(self):
        clock = ManualClock(start=0.0)
        policy = RateLimitPolicy(max_requests=5, window_seconds=5.0)  # 1 token/sec, cap 5
        strategy = TokenBucketStrategy(clock=clock)

        # Initially full bucket -> allow 5
        for _ in range(5):
            self.assertTrue(strategy.allow(1, policy))
        # Next should be denied
        self.assertFalse(strategy.allow(1, policy))

        # Advance 2 seconds -> 2 tokens refill
        clock.advance(2.0)
        self.assertTrue(strategy.allow(1, policy))
        self.assertTrue(strategy.allow(1, policy))
        # No more tokens
        self.assertFalse(strategy.allow(1, policy))

    def test_separate_customers_have_separate_buckets(self):
        clock = ManualClock(start=0.0)
        policy = RateLimitPolicy(max_requests=1, window_seconds=10.0)
        strategy = TokenBucketStrategy(clock=clock)

        self.assertTrue(strategy.allow(100, policy))
        self.assertTrue(strategy.allow(101, policy))
        self.assertFalse(strategy.allow(100, policy))


class TestRateLimiterFacade(unittest.TestCase):
    def test_default_and_per_customer_policy(self):
        clock = ManualClock(start=0.0)
        default_policy = RateLimitPolicy(max_requests=2, window_seconds=10.0)
        strategy = SlidingWindowLogStrategy(clock=clock)
        limiter = RateLimiter(strategy=strategy, default_policy=default_policy)

        # Customer 1 uses default policy (2 per 10s)
        self.assertTrue(limiter.allow(1))
        self.assertTrue(limiter.allow(1))
        self.assertFalse(limiter.allow(1))

        # Override policy for customer 2
        limiter.set_policy_for_customer(2, RateLimitPolicy(max_requests=3, window_seconds=10.0))
        self.assertTrue(limiter.allow(2))
        self.assertTrue(limiter.allow(2))
        self.assertTrue(limiter.allow(2))
        self.assertFalse(limiter.allow(2))

    def test_window_progression_with_clock(self):
        clock = ManualClock(start=0.0)
        policy = RateLimitPolicy(max_requests=2, window_seconds=1.0)
        strategy = FixedWindowStrategy(clock=clock)
        limiter = RateLimiter(strategy=strategy, default_policy=policy)

        self.assertTrue(limiter.allow(42))
        self.assertTrue(limiter.allow(42))
        self.assertFalse(limiter.allow(42))

        clock.advance(1.0)
        self.assertTrue(limiter.allow(42))


if __name__ == "__main__":
    unittest.main(verbosity=2) 