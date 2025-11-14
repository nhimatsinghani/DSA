"""
Tennis Court Booking - Part D: Minimum Number of Courts Needed

Problem: Simplified version that only finds the minimum number of courts needed
to accommodate all bookings, without assigning specific bookings to specific courts.

This is the classic "Meeting Rooms II" problem: find the maximum number of 
overlapping intervals at any point in time.

Approaches:
1. Event-based (Sweep Line): Create start/end events, sort by time, sweep and count
2. Heap-based: Similar to Part A but just count instead of tracking assignments

Time Complexity: O(n log n) - sorting
Space Complexity: O(n) - events or heap storage
"""

import heapq
from typing import List, NamedTuple, Tuple
from enum import Enum


class BookingRecord(NamedTuple):
    """Represents a tennis court booking"""
    id: int
    start_time: int
    finish_time: int


class EventType(Enum):
    """Types of events in the sweep line algorithm"""
    START = 1
    END = 2


class Event(NamedTuple):
    """Event for sweep line algorithm"""
    time: int
    event_type: EventType
    booking_id: int


def min_courts_needed_sweep_line(booking_records: List[BookingRecord]) -> int:
    """
    Find minimum courts needed using sweep line algorithm.
    
    Key Insight: At any point in time, the number of courts needed equals
    the number of ongoing bookings. We track this by processing start/end events.
    
    Algorithm:
    1. Create start and end events for each booking
    2. Sort events by time (end events before start events at same time)
    3. Sweep through events, tracking current active bookings
    4. Return maximum active bookings seen
    
    Args:
        booking_records: List of BookingRecord objects
        
    Returns:
        Minimum number of courts needed
        
    Example:
        Bookings: [(0,10), (5,15), (10,20)]
        Events: [START@0, START@5, END@10, START@10, END@15, END@20]
        Active: [1, 2, 1, 2, 1, 0]
        Max: 2 courts needed
    """
    if not booking_records:
        return 0
    
    # Create events
    events = []
    for booking in booking_records:
        events.append(Event(booking.start_time, EventType.START, booking.id))
        events.append(Event(booking.finish_time, EventType.END, booking.id))
    
    # Sort events by time, with END events before START events at same time
    # This handles the case where one booking ends exactly when another starts
    events.sort(key=lambda e: (e.time, e.event_type.value))
    
    current_active = 0
    max_courts = 0
    
    for event in events:
        if event.event_type == EventType.START:
            current_active += 1
            max_courts = max(max_courts, current_active)
        else:  # END event
            current_active -= 1
    
    return max_courts


def min_courts_needed_heap(booking_records: List[BookingRecord]) -> int:
    """
    Find minimum courts needed using heap approach (similar to Part A).
    
    Algorithm:
    1. Sort bookings by start time
    2. Use min-heap to track when courts become available
    3. For each booking, if earliest court is available, reuse it
    4. Otherwise, add a new court
    5. Return total courts created
    
    Args:
        booking_records: List of BookingRecord objects
        
    Returns:
        Minimum number of courts needed
    """
    if not booking_records:
        return 0
    
    # Sort by start time
    sorted_bookings = sorted(booking_records, key=lambda x: x.start_time)
    
    # Min-heap to track court end times
    court_end_times = []
    
    for booking in sorted_bookings:
        # If earliest court is available, reuse it
        if court_end_times and court_end_times[0] <= booking.start_time:
            heapq.heappop(court_end_times)
        
        # Add this booking's end time (either reusing court or new court)
        heapq.heappush(court_end_times, booking.finish_time)
    
    return len(court_end_times)


def analyze_booking_conflicts(booking_records: List[BookingRecord]) -> dict:
    """
    Analyze the booking conflicts to understand why certain number of courts is needed.
    
    Returns:
        Dictionary with analysis results
    """
    if not booking_records:
        return {"max_concurrent": 0, "conflict_periods": []}
    
    # Create events for analysis
    events = []
    for booking in booking_records:
        events.append((booking.start_time, 'start', booking.id))
        events.append((booking.finish_time, 'end', booking.id))
    
    # Sort events (end before start at same time)
    events.sort(key=lambda e: (e[0], e[1] == 'start'))
    
    current_bookings = set()
    max_concurrent = 0
    conflict_periods = []
    
    for time, event_type, booking_id in events:
        if event_type == 'start':
            current_bookings.add(booking_id)
            if len(current_bookings) > max_concurrent:
                max_concurrent = len(current_bookings)
                if len(current_bookings) > 1:
                    conflict_periods.append({
                        'time': time,
                        'concurrent_bookings': list(current_bookings),
                        'count': len(current_bookings)
                    })
        else:
            current_bookings.discard(booking_id)
    
    return {
        'max_concurrent': max_concurrent,
        'conflict_periods': conflict_periods
    }


def print_detailed_analysis(booking_records: List[BookingRecord]):
    """Print detailed analysis of court requirements"""
    sweep_result = min_courts_needed_sweep_line(booking_records)
    heap_result = min_courts_needed_heap(booking_records)
    analysis = analyze_booking_conflicts(booking_records)
    
    print(f"Minimum courts needed: {sweep_result}")
    print(f"Verification (heap method): {heap_result}")
    print(f"Maximum concurrent bookings: {analysis['max_concurrent']}")
    
    if analysis['conflict_periods']:
        print("\nPeak conflict periods:")
        for period in analysis['conflict_periods']:
            if period['count'] == analysis['max_concurrent']:
                print(f"  Time {period['time']}: {period['count']} concurrent bookings "
                      f"(IDs: {period['concurrent_bookings']})")


# Example usage and test cases
if __name__ == "__main__":
    print("=== Test Case 1: Basic overlapping ===")
    bookings1 = [
        BookingRecord(1, 0, 30),
        BookingRecord(2, 5, 10),
        BookingRecord(3, 15, 20)
    ]
    print("Bookings:", [(b.id, b.start_time, b.finish_time) for b in bookings1])
    print_detailed_analysis(bookings1)
    
    print("\n=== Test Case 2: No overlaps ===")
    bookings2 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 10, 20),
        BookingRecord(3, 20, 30)
    ]
    print("Bookings:", [(b.id, b.start_time, b.finish_time) for b in bookings2])
    print_detailed_analysis(bookings2)
    
    print("\n=== Test Case 3: All overlap ===")
    bookings3 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 0, 10),
        BookingRecord(3, 0, 10)
    ]
    print("Bookings:", [(b.id, b.start_time, b.finish_time) for b in bookings3])
    print_detailed_analysis(bookings3)
    
    print("\n=== Test Case 4: Complex scenario ===")
    bookings4 = [
        BookingRecord(1, 1, 5),
        BookingRecord(2, 2, 6),
        BookingRecord(3, 3, 7),
        BookingRecord(4, 4, 8),
        BookingRecord(5, 6, 9)
    ]
    print("Bookings:", [(b.id, b.start_time, b.finish_time) for b in bookings4])
    print_detailed_analysis(bookings4)
    
    print("\n=== Test Case 5: Edge case - same start/end times ===")
    bookings5 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 10, 20),  # Starts exactly when booking 1 ends
        BookingRecord(3, 5, 15)    # Overlaps with both
    ]
    print("Bookings:", [(b.id, b.start_time, b.finish_time) for b in bookings5])
    print_detailed_analysis(bookings5)
