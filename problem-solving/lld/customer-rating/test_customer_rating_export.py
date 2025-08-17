import unittest
import json
import os
import tempfile
from datetime import datetime, timezone

from customer_rating import CustomerRatingService, RatingBounds


class TestCustomerRatingExport(unittest.TestCase):
    def setUp(self):
        self.service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
        # Populate across months
        self.service.record_rating(1, 5, at=datetime(2025, 1, 10, tzinfo=timezone.utc))
        self.service.record_rating(1, 3, at=datetime(2025, 1, 11, tzinfo=timezone.utc))  # u1 Jan avg=4, total=8
        self.service.record_rating(2, 4, at=datetime(2025, 1, 12, tzinfo=timezone.utc))  # u2 Jan avg=4, total=4
        self.service.record_rating(1, 5, at=datetime(2025, 2, 1, tzinfo=timezone.utc))   # u1 Feb avg=5

    def test_export_csv_all_months(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            self.service.export_monthly_stats_csv(path, aggregate="average")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip().splitlines()
            # Header + 3 rows
            self.assertEqual(content[0], "user_id,year,month,average")
            # Deterministic order: (year asc, month asc, value desc, user_id asc)
            # Rows could be: u1 Jan 4.0, u2 Jan 4.0 (id asc), u1 Feb 5.0 comes after Jan
            self.assertIn("1,2025,1,4.0", content[1])
            self.assertIn("2,2025,1,4.0", content[2])
            self.assertIn("1,2025,2,5.0", content[3])
        finally:
            os.remove(path)

    def test_export_json_filtered_total(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            self.service.export_monthly_stats_json(path, aggregate="total", year=2025, month=1, pretty=False)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Expect two rows for Jan 2025
            # u1 total=8.0, u2 total=4.0
            self.assertEqual(len(data), 2)
            # Sorted by value desc then user_id asc
            self.assertEqual(data[0]["user_id"], 1)
            self.assertEqual(data[0]["value"], 8.0)
            self.assertEqual(data[1]["user_id"], 2)
            self.assertEqual(data[1]["value"], 4.0)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main(verbosity=2) 