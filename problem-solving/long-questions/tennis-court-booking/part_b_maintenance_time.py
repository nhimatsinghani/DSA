"""
Tennis Court Booking - Part B: Court Assignment with Maintenance Time

Problem: After each booking, a fixed amount of time X is needed to maintain 
the court before it can be rented again. Modify the court assignment to 
account for this maintenance time.

Key Insight: When a booking finishes at time T, the court becomes available 
at time T + maintenance_time (not just T).

Approach:
1. Sort bookings by start time (same as part A)
2. Use a min-heap to track when courts become available AFTER maintenance
3. For each booking:
   - Check if earliest available court is free (available_time <= start_time)
   - If yes, reuse it; if no, allocate new court
   - Update court availability to finish_time + maintenance_time

Time Complexity: O(n log n) - sorting + heap operations
Space Complexity: O(n) - heap and result storage
"""

import heapq
from typing import List, NamedTuple


class BookingRecord(NamedTuple):
    """Represents a tennis court booking"""
    id: int
    start_time: int
    finish_time: int


class CourtAssignment(NamedTuple):
    """Represents the assignment of a booking to a court"""
    booking_id: int
    court_id: int
    start_time: int
    finish_time: int


def assign_courts_with_maintenance(booking_records: List[BookingRecord], 
                                 maintenance_time: int) -> List[CourtAssignment]:
    """
    Assigns bookings to courts with maintenance time consideration.
    
    Args:
        booking_records: List of BookingRecord objects
        maintenance_time: Fixed maintenance time needed after each booking
        
    Returns:
        List of CourtAssignment objects showing which booking is assigned to which court
        
    Example:
        bookings = [
            BookingRecord(1, 0, 10),
            BookingRecord(2, 12, 20),  # Can reuse court 0 if maintenance_time <= 2
            BookingRecord(3, 5, 15)    # Overlaps with booking 1, needs new court
        ]
        
        With maintenance_time = 2:
        - Booking 1: Court 0 (0-10), available after 10+2=12
        - Booking 3: Court 1 (5-15), available after 15+2=17  
        - Booking 2: Court 0 (12-20), can reuse since 12 >= 12
    """
    if not booking_records:
        return []
    
    # Sort bookings by start time
    sorted_bookings = sorted(booking_records, key=lambda x: x.start_time)
    
    # Min-heap to track when courts become available AFTER maintenance
    # Each element is (available_time, court_id)
    court_heap = []
    
    # Track assignments
    assignments = []
    
    # Counter for creating new court IDs
    next_court_id = 0
    
    for booking in sorted_bookings:
        # Check if any court is available (earliest available time <= booking start time)
        if court_heap and court_heap[0][0] <= booking.start_time:
            # Reuse the earliest available court
            _, court_id = heapq.heappop(court_heap)
        else:
            # Need a new court
            court_id = next_court_id
            next_court_id += 1
        
        # Assign booking to court
        assignments.append(CourtAssignment(
            booking_id=booking.id,
            court_id=court_id,
            start_time=booking.start_time,
            finish_time=booking.finish_time
        ))
        
        # Update court availability: available after finish_time + maintenance_time
        available_time = booking.finish_time + maintenance_time
        heapq.heappush(court_heap, (available_time, court_id))
    
    return assignments


def get_total_courts_needed(assignments: List[CourtAssignment]) -> int:
    """Helper function to get total number of courts used"""
    if not assignments:
        return 0
    return max(assignment.court_id for assignment in assignments) + 1


def print_assignment_schedule_with_maintenance(assignments: List[CourtAssignment], 
                                             maintenance_time: int):
    """Helper function to print the assignment schedule with maintenance info"""
    if not assignments:
        print("No bookings to assign")
        return
    
    # Group by court
    courts = {}
    for assignment in assignments:
        if assignment.court_id not in courts:
            courts[assignment.court_id] = []
        courts[assignment.court_id].append(assignment)
    
    # Sort bookings within each court by start time
    for court_id in courts:
        courts[court_id].sort(key=lambda x: x.start_time)
    
    print(f"Total courts needed: {get_total_courts_needed(assignments)}")
    print(f"Maintenance time after each booking: {maintenance_time}")
    print("\nSchedule (showing booking time + maintenance period):")
    
    for court_id in sorted(courts.keys()):
        print(f"Court {court_id}:")
        for assignment in courts[court_id]:
            maintenance_end = assignment.finish_time + maintenance_time
            print(f"  Booking {assignment.booking_id}: {assignment.start_time}-{assignment.finish_time} "
                  f"(maintenance until {maintenance_end})")


def compare_with_and_without_maintenance(bookings: List[BookingRecord], 
                                       maintenance_time: int):
    """Compare court allocation with and without maintenance time"""
    # Import from part A
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from part_a_basic_assignment import assign_courts
    
    assignments_without = assign_courts(bookings)
    assignments_with = assign_courts_with_maintenance(bookings, maintenance_time)
    
    courts_without = get_total_courts_needed(assignments_without)
    courts_with = get_total_courts_needed(assignments_with)
    
    print(f"Courts needed WITHOUT maintenance: {courts_without}")
    print(f"Courts needed WITH maintenance time {maintenance_time}: {courts_with}")
    print(f"Additional courts needed: {courts_with - courts_without}")


# Example usage and test cases
if __name__ == "__main__":
    print("=== Test Case 1: Small maintenance time (allows reuse) ===")
    bookings1 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 12, 20),  # Can reuse if maintenance <= 2
        BookingRecord(3, 5, 15)    # Overlaps, needs new court
    ]
    assignments1 = assign_courts_with_maintenance(bookings1, maintenance_time=2)
    print_assignment_schedule_with_maintenance(assignments1, 2)
    
    print("\n=== Test Case 2: Large maintenance time (prevents reuse) ===")
    assignments2 = assign_courts_with_maintenance(bookings1, maintenance_time=5)
    print_assignment_schedule_with_maintenance(assignments2, 5)
    
    print("\n=== Test Case 3: Comparison with and without maintenance ===")
    bookings3 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 10, 20),  # Exactly adjacent
        BookingRecord(3, 20, 30),  # Exactly adjacent
        BookingRecord(4, 5, 15)    # Overlaps with booking 1
    ]
    
    print("With maintenance time = 0:")
    assignments3a = assign_courts_with_maintenance(bookings3, maintenance_time=0)
    print_assignment_schedule_with_maintenance(assignments3a, 0)
    
    print("\nWith maintenance time = 3:")
    assignments3b = assign_courts_with_maintenance(bookings3, maintenance_time=3)
    print_assignment_schedule_with_maintenance(assignments3b, 3)
    
    print("\n=== Comparison Summary ===")
    compare_with_and_without_maintenance(bookings3, 3)
