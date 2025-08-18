from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, getcontext
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple
import calendar

# Set decimal precision sufficient for currency calculations
getcontext().prec = 28


class Plan(Enum):
    BASIC = Decimal("9.99")
    STANDARD = Decimal("49.99")
    PREMIUM = Decimal("249.99")

    @property
    def monthly_price(self) -> Decimal:
        return self.value


class TrialPolicy:
    def daily_multiplier(self, sub: "Subscription", on: date) -> Decimal:
        """Return a multiplier [0,1] to apply to that day's price.

        Default: 1 (no trial).
        """
        return Decimal("1")


class NoTrialPolicy(TrialPolicy):
    pass


class FreeDaysTrialPolicy(TrialPolicy):
    def __init__(self, free_days: int) -> None:
        if free_days < 0:
            raise ValueError("free_days must be non-negative")
        self._free_days = free_days

    def daily_multiplier(self, sub: "Subscription", on: date) -> Decimal:
        if on < sub.start_date:
            return Decimal("1")  # outside active window; caller ignores anyway
        # Free window: [start_date, start_date + free_days - 1]
        trial_end = sub.start_date + timedelta(days=self._free_days - 1) if self._free_days > 0 else sub.start_date - timedelta(days=1)
        if self._free_days > 0 and on <= trial_end:
            return Decimal("0")
        return Decimal("1")


@dataclass(frozen=True)
class Subscription:
    product: str
    plan: Plan
    start_date: date
    end_date: Optional[date] = None  # inclusive end; None means ongoing
    trial: TrialPolicy = NoTrialPolicy()


class BillingStrategy:
    def compute_month_charge(self, sub: Subscription, year: int, month: int) -> Decimal:
        raise NotImplementedError


class DailyProratedBillingStrategy(BillingStrategy):
    """Charges by daily proration within each calendar month with trial support.

    For each active day in the month:
      daily_price = monthly_price / days_in_month
      charge += daily_price * trial.daily_multiplier(...)
    """

    def compute_month_charge(self, sub: Subscription, year: int, month: int) -> Decimal:
        month_days = calendar.monthrange(year, month)[1]
        month_start = date(year, month, 1)
        month_end = date(year, month, month_days)

        total = Decimal("0.00")
        daily_price = sub.plan.monthly_price / Decimal(month_days)

        current = month_start
        while current <= month_end:
            # Active if within [start_date, end_date or +inf]
            if current >= sub.start_date and (sub.end_date is None or current <= sub.end_date):
                mult = sub.trial.daily_multiplier(sub, current)
                if mult:
                    total += (daily_price * mult)
            current += timedelta(days=1)

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class MonthCharge:
    year: int
    month: int
    amount: Decimal


class CostExplorer:
    def __init__(self, billing: Optional[BillingStrategy] = None) -> None:
        self._billing = billing or DailyProratedBillingStrategy()
        self._subscriptions: List[Subscription] = []

    def add_subscription(self, subscription: Subscription) -> None:
        self._subscriptions.append(subscription)

    def add_subscriptions(self, subscriptions: Iterable[Subscription]) -> None:
        for s in subscriptions:
            self.add_subscription(s)

    def monthly_report(self, year: int) -> List[MonthCharge]:
        """Return month-by-month charges for the given calendar year, summing all subscriptions."""
        report: List[MonthCharge] = []
        for m in range(1, 13):
            total = Decimal("0.00")
            for sub in self._subscriptions:
                total += self._billing.compute_month_charge(sub, year, m)
            total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            report.append(MonthCharge(year=year, month=m, amount=total))
        return report

    def yearly_estimate(self, year: int) -> Decimal:
        total = sum((mc.amount for mc in self.monthly_report(year)), Decimal("0.00"))
        return Decimal(total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) 