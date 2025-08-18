import unittest
from datetime import date
from decimal import Decimal

from cost_explorer import CostExplorer, Subscription, Plan, FreeDaysTrialPolicy


class TestCostExplorer(unittest.TestCase):
    def test_full_month(self):
        ce = CostExplorer()
        ce.add_subscription(Subscription(product="X", plan=Plan.BASIC, start_date=date(2025, 1, 1)))
        jan = [mc for mc in ce.monthly_report(2025) if mc.month == 1][0]
        self.assertEqual(jan.amount, Decimal("9.99"))

    def test_partial_month_proration(self):
        ce = CostExplorer()
        ce.add_subscription(Subscription(product="X", plan=Plan.STANDARD, start_date=date(2025, 1, 16), end_date=date(2025, 1, 31)))
        jan = [mc for mc in ce.monthly_report(2025) if mc.month == 1][0]
        expected = (Plan.STANDARD.monthly_price * Decimal(16) / Decimal(31)).quantize(Decimal("0.01"))
        self.assertEqual(jan.amount, expected)

    def test_yearly_estimate_multiple_subs(self):
        ce = CostExplorer()
        ce.add_subscription(Subscription(product="X", plan=Plan.BASIC, start_date=date(2025, 1, 1)))
        ce.add_subscription(Subscription(product="Y", plan=Plan.PREMIUM, start_date=date(2025, 3, 15), end_date=date(2025, 6, 14)))
        total = ce.yearly_estimate(2025)
        self.assertTrue(total > Decimal("0.00"))

    def test_trial_free_days(self):
        ce = CostExplorer()
        # 10 free days starting Jan 1 => free Jan 1..Jan 10 inclusive
        ce.add_subscription(Subscription(product="X", plan=Plan.PREMIUM, start_date=date(2025, 1, 1), trial=FreeDaysTrialPolicy(10)))
        jan = [mc for mc in ce.monthly_report(2025) if mc.month == 1][0]
        # Jan has 31 days; bill for 21 days
        expected = (Plan.PREMIUM.monthly_price * Decimal(21) / Decimal(31)).quantize(Decimal("0.01"))
        self.assertEqual(jan.amount, expected)

    def test_trial_spans_month_boundary(self):
        ce = CostExplorer()
        # Start Jan 25 with 10 free days => free Jan 25-Feb 3 inclusive; no charges in Jan
        ce.add_subscription(Subscription(product="X", plan=Plan.BASIC, start_date=date(2025, 1, 25), trial=FreeDaysTrialPolicy(10)))
        jan = [mc for mc in ce.monthly_report(2025) if mc.month == 1][0]
        feb = [mc for mc in ce.monthly_report(2025) if mc.month == 2][0]
        expected_jan = Decimal("0.00")
        # Feb 2025 has 28 days; free on Feb 1..3 => 25 chargeable days
        expected_feb = (Plan.BASIC.monthly_price * Decimal(25) / Decimal(28)).quantize(Decimal("0.01"))
        self.assertEqual(jan.amount, expected_jan)
        self.assertEqual(feb.amount, expected_feb)


if __name__ == "__main__":
    unittest.main(verbosity=2) 