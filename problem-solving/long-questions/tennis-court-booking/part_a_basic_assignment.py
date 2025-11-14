"""
Tennis Court Booking - Part A: Basic Court Assignment

Problem: Given a list of tennis court bookings with start and finish times, 
return a plan assigning each booking to a specific court, ensuring each court 
is used by only one booking at a time and using the minimum number of courts.

Approach:
1. Sort bookings by start time
2. Use a min-heap to track when courts become available (end times)
3. For each booking:
   - If earliest available court is free (end time <= start time), reuse it
   - Otherwise, allocate a new court
4. Track assignments for each booking

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


def assign_courts(booking_records: List[BookingRecord]) -> List[CourtAssignment]:
    """
    Assigns bookings to courts using minimum number of courts.
    
    Args:
        booking_records: List of BookingRecord objects
        
    Returns:
        List of CourtAssignment objects showing which booking is assigned to which court
        
    Example:
        bookings = [
            BookingRecord(1, 0, 30),
            BookingRecord(2, 5, 10),
            BookingRecord(3, 15, 20)
        ]
        
        Result: [
            CourtAssignment(1, 0, 0, 30),   # Booking 1 -> Court 0
            CourtAssignment(2, 1, 5, 10),   # Booking 2 -> Court 1 (overlaps with booking 1)
            CourtAssignment(3, 1, 15, 20)   # Booking 3 -> Court 1 (can reuse after booking 2)
        ]
    """
    if not booking_records:
        return []
    
    # Sort bookings by start time
    sorted_bookings = sorted(booking_records, key=lambda x: x.start_time)
    
    # Min-heap to track when courts become available
    # Each element is (end_time, court_id)
    court_heap = []
    
    # Track assignments
    assignments = []
    
    # Counter for creating new court IDs
    next_court_id = 0
    
    for booking in sorted_bookings:
        # Check if any court is available (earliest end time <= booking start time)
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
        
        # Update court availability
        heapq.heappush(court_heap, (booking.finish_time, court_id))
    
    return assignments


def get_total_courts_needed(assignments: List[CourtAssignment]) -> int:
    """Helper function to get total number of courts used"""
    if not assignments:
        return 0
    return max(assignment.court_id for assignment in assignments) + 1


def print_assignment_schedule(assignments: List[CourtAssignment]):
    """Helper function to print the assignment schedule in a readable format"""
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
    print("\nSchedule:")
    for court_id in sorted(courts.keys()):
        print(f"Court {court_id}:")
        for assignment in courts[court_id]:
            print(f"  Booking {assignment.booking_id}: {assignment.start_time}-{assignment.finish_time}")


# Example usage and test cases
if __name__ == "__main__":
    # Test case 1: Basic overlapping bookings
    print("=== Test Case 1: Basic overlapping bookings ===")
    bookings1 = [
        BookingRecord(1, 0, 30),
        BookingRecord(2, 5, 10),
        BookingRecord(3, 15, 20)
    ]
    assignments1 = assign_courts(bookings1)
    print_assignment_schedule(assignments1)
    
    print("\n=== Test Case 2: No overlaps ===")
    bookings2 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 10, 20),
        BookingRecord(3, 20, 30)
    ]
    assignments2 = assign_courts(bookings2)
    print_assignment_schedule(assignments2)
    
    print("\n=== Test Case 3: All overlap at same time ===")
    bookings3 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 0, 10),
        BookingRecord(3, 0, 10)
    ]
    assignments3 = assign_courts(bookings3)
    print_assignment_schedule(assignments3)
    
    print("\n=== Test Case 4: Complex scheduling ===")
    bookings4 = [
        BookingRecord(1, 1, 3),
        BookingRecord(2, 2, 4),
        BookingRecord(3, 3, 6),
        BookingRecord(4, 5, 7),
        BookingRecord(5, 8, 9)
    ]
    assignments4 = assign_courts(bookings4)
    print_assignment_schedule(assignments4)
