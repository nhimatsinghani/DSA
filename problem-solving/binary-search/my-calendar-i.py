# You are implementing a program to use as your calendar. We can add a new event if adding the event will not cause a double booking.

# A double booking happens when two events have some non-empty intersection (i.e., some moment is common to both events.).

# The event can be represented as a pair of integers startTime and endTime that represents a booking on the half-open interval [startTime, endTime), the range of real numbers x such that startTime <= x < endTime.

# Implement the MyCalendar class:

# MyCalendar() Initializes the calendar object.
# boolean book(int startTime, int endTime) Returns true if the event can be added to the calendar successfully without causing a double booking. Otherwise, return false and do not add the event to the calendar.

from typing import Tuple
from sortedcontainers import SortedList


class MyCalendar:
    """Book non-overlapping half-open intervals [start, end).

    Strategy: maintain a SortedList of (start, end) pairs sorted by start time.
    To book a new interval, binary-search the first interval with start >= new_start.
    Check for overlap against its predecessor and itself; insert if safe.
    """

    def __init__(self) -> None:
        # Store (start, end) tuples; SortedList maintains lexicographic order by start then end
        self.intervals: SortedList[Tuple[int, int]] = SortedList()

    def _lower_bound_by_start(self, target_start: int) -> int:
        """First index i with intervals[i].start >= target_start using raw binary search."""
        lo = 0
        hi = len(self.intervals)
        while lo < hi:
            mid = (lo + hi) // 2
            mid_start = self.intervals[mid][0]
            if mid_start < target_start:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def book(self, start: int, end: int) -> bool:
        if end <= start:
            # Degenerate or invalid interval cannot cause double booking if ignored.
            # Per LeetCode convention, usually inputs satisfy start < end, but guard anyway.
            return False

        # Find insertion position: first interval whose start >= start
        idx = self._lower_bound_by_start(start)

        # Check overlap with the previous interval
        if idx > 0:
            prev_start, prev_end = self.intervals[idx - 1]
            if prev_end > start:  # overlap since [prev_start, prev_end) intersects start
                return False

        # Check overlap with the next interval at idx
        if idx < len(self.intervals):
            next_start, next_end = self.intervals[idx]
            if next_start < end:  # overlap since next starts before new end
                return False

        # Safe to insert
        self.intervals.add((start, end))
        return True


if __name__ == "__main__":
    # Simple sanity check
    cal = MyCalendar()
    print(cal.book(10, 20))  # True
    print(cal.book(15, 25))  # False (overlaps)
    print(cal.book(20, 30))  # True (touching is OK: [10,20) and [20,30))