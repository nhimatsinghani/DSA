import unittest
from datetime import datetime, timezone

from customer_rating import CustomerRatingService, RatingBounds

try:
    from sortedcontainers import SortedList  # type: ignore
    HAS_SORTED = True
except Exception:  # pragma: no cover
    HAS_SORTED = False


class TestCustomerRatingMonthly(unittest.TestCase):
    def setUp(self):
        self.service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))

    def test_monthly_averages_and_totals(self):
        # Jan ratings for user 1 -> avg 4.0, total 8.0
        self.service.record_rating(1, 5, at=datetime(2025, 1, 10, tzinfo=timezone.utc))
        self.service.record_rating(1, 3, at=datetime(2025, 1, 20, tzinfo=timezone.utc))
        # Jan ratings for user 2 -> avg 3.0, total 3.0
        self.service.record_rating(2, 3, at=datetime(2025, 1, 15, tzinfo=timezone.utc))
        # Feb ratings for user 1 -> avg 5.0
        self.service.record_rating(1, 5, at=datetime(2025, 2, 1, tzinfo=timezone.utc))

        jan_avg = self.service.get_monthly_stats(2025, 1, aggregate="average", sorted=True)
        self.assertEqual(jan_avg, [(1, 4.0), (2, 3.0)])

        jan_total = self.service.get_monthly_stats(2025, 1, aggregate="total", sorted=True)
        self.assertEqual(jan_total, [(1, 8.0), (2, 3.0)])

        feb_avg = self.service.get_monthly_stats(2025, 2, aggregate="average", sorted=True)
        self.assertEqual(feb_avg, [(1, 5.0)])

    def test_monthly_best_agents_top_k(self):
        # Create Jan ratings
        self.service.record_rating(1, 5, at=datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.service.record_rating(2, 4, at=datetime(2025, 1, 2, tzinfo=timezone.utc))
        self.service.record_rating(3, 5, at=datetime(2025, 1, 3, tzinfo=timezone.utc))
        self.service.record_rating(3, 3, at=datetime(2025, 1, 4, tzinfo=timezone.utc))
        # Averages: u1=5.0, u2=4.0, u3=4.0 (tie => id ascending)

        top1 = self.service.get_best_agents_for_month(2025, 1, top_k=1)
        self.assertEqual(top1, [(1, 5.0)])

        full = self.service.get_best_agents_for_month(2025, 1, top_k=None)
        self.assertEqual(full, [(1, 5.0), (2, 4.0), (3, 4.0)])

    def test_monthly_best_agents_top_k_optimized(self):
        # Ratings for January
        self.service.record_rating(1, 5, at=datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.service.record_rating(2, 4, at=datetime(2025, 1, 2, tzinfo=timezone.utc))
        self.service.record_rating(3, 4, at=datetime(2025, 1, 3, tzinfo=timezone.utc))
        # Update u2 to increase avg and challenge heap
        self.service.record_rating(2, 5, at=datetime(2025, 1, 5, tzinfo=timezone.utc))  # u2 avg = 4.5

        top2 = self.service.get_best_agents_for_month_optimized(2025, 1, top_k=2)
        self.assertEqual(top2, [(1, 5.0), (2, 4.5)])

    @unittest.skipUnless(HAS_SORTED, "sortedcontainers is not installed")
    def test_monthly_full_rank_sortedlist(self):
        self.service.record_rating(10, 5, at=datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.service.record_rating(20, 3, at=datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.service.record_rating(30, 5, at=datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.service.record_rating(30, 3, at=datetime(2025, 1, 2, tzinfo=timezone.utc))
        # avgs for Jan: u10=5.0, u30=4.0, u20=3.0
        rank = self.service.get_monthly_stats_optimized_v2(2025, 1)
        self.assertEqual(rank, [(10, 5.0), (30, 4.0), (20, 3.0)])


if __name__ == "__main__":
    unittest.main(verbosity=2) 