import unittest

from customer_rating import (
    CustomerRatingService,
    InMemoryRatingStore,
    RatingBounds,
    record_user_rating,
    get_user_average,
    get_ranking,
)

try:
    from sortedcontainers import SortedList  # type: ignore
    HAS_SORTED = True
except Exception:  # pragma: no cover
    HAS_SORTED = False


class TestCustomerRatingService(unittest.TestCase):
    def test_record_and_average(self):
        service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
        service.record_rating(1, 5)
        service.record_rating(1, 3)
        self.assertAlmostEqual(service.get_average(1), 4.0)

    def test_bounds_validation(self):
        service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
        with self.assertRaises(ValueError):
            service.record_rating(2, 0.5)
        with self.assertRaises(ValueError):
            service.record_rating(2, 5.5)

    def test_ranking_descending(self):
        service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
        # user 1: avg 4.0
        service.record_rating(1, 5)
        service.record_rating(1, 3)
        # user 2: avg 3.0
        service.record_rating(2, 3)
        # user 3: avg 4.0 (same as user 1) -> tie-break by user_id ascending
        service.record_rating(3, 4)

        ranking = service.get_ranked_users(descending=True)
        self.assertEqual(ranking, [(1, 4.0), (3, 4.0), (2, 3.0)])

    def test_global_convenience_api(self):
        # Use global service convenience API
        record_user_rating(100, 5)
        record_user_rating(100, 1)
        avg = get_user_average(100)
        self.assertAlmostEqual(avg, 3.0)
        ranking = get_ranking()
        # Ensure user 100 is present
        ids = [u for (u, _) in ranking]
        self.assertIn(100, ids)

    def test_top_k_optimized(self):
        service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
        # Create users with different averages
        # u1: 4.5, u2: 4.0, u3: 3.0, u4: 5.0, u5: 2.0
        service.record_rating(1, 4)
        service.record_rating(1, 5)
        service.record_rating(2, 4)
        service.record_rating(3, 3)
        service.record_rating(4, 5)
        service.record_rating(5, 2)

        top3 = service.get_ranked_users_optimized(top_k=3)
        self.assertEqual(top3, [(4, 5.0), (1, 4.5), (2, 4.0)])

        # Update ratings to change order and ensure heap handles invalidation
        service.record_rating(2, 5)  # u2 avg -> (4 + 5)/2 = 4.5 ties with u1
        # Now top3 should be u4=5.0, u1=4.5, u2=4.5 (tie break user_id ascending)
        top3_after = service.get_ranked_users_optimized(top_k=3)
        self.assertEqual(top3_after, [(4, 5.0), (1, 4.5), (2, 4.5)])

    @unittest.skipUnless(HAS_SORTED, "sortedcontainers is not installed")
    def test_full_ranking_sortedlist(self):
        service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
        service.record_rating(10, 5)
        service.record_rating(20, 3)
        service.record_rating(30, 5)
        service.record_rating(30, 3)
        # avgs: u10=5.0, u30=4.0, u20=3.0
        full_rank = service.get_ranked_users_optimized_v2()
        self.assertEqual(full_rank, [(10, 5.0), (30, 4.0), (20, 3.0)])


if __name__ == "__main__":
    unittest.main(verbosity=2) 