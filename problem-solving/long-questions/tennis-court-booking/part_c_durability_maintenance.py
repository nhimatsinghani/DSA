"""
Tennis Court Booking - Part C: Court Assignment with Durability-Based Maintenance

Problem: Courts only need maintenance after X amount of usage (durability).
After X bookings, a court needs Y maintenance time before it can be used again.

Key Insights:
1. Track usage count for each court
2. When court reaches durability limit, it needs maintenance
3. During maintenance, court is unavailable
4. After maintenance, usage count resets to 0

Approach:
1. Sort bookings by start time
2. Track each court's state: (available_time, usage_count, court_id)
3. For each booking:
   - Find courts available and not in maintenance
   - If court reaches durability after this booking, schedule maintenance
   - Assign to earliest available court
   - Update court state

Time Complexity: O(n log n) - sorting + heap operations  
Space Complexity: O(n) - court tracking and result storage
"""

import heapq
from typing import List, NamedTuple, Optional
from dataclasses import dataclass


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


@dataclass
class Court:
    """Represents a court with its current state"""
    court_id: int
    available_time: int = 0  # When court becomes available for next booking
    usage_count: int = 0     # Number of bookings since last maintenance
    
    def __lt__(self, other):
        """For heap ordering - prioritize by available_time"""
        return self.available_time < other.available_time


def assign_courts_with_durability_maintenance(
    booking_records: List[BookingRecord],
    maintenance_time: int,
    durability: int
) -> List[CourtAssignment]:
    """
    Assigns bookings to courts with durability-based maintenance.
    
    Args:
        booking_records: List of BookingRecord objects
        maintenance_time: Time needed for maintenance when durability is reached
        durability: Number of bookings a court can handle before needing maintenance
        
    Returns:
        List of CourtAssignment objects
        
    Example:
        With durability=2, maintenance_time=5:
        - Court can handle 2 bookings, then needs 5 time units of maintenance
        - After maintenance, usage count resets and court can handle 2 more bookings
    """
    if not booking_records:
        return []
    
    if durability <= 0:
        raise ValueError("Durability must be positive")
    
    # Sort bookings by start time
    sorted_bookings = sorted(booking_records, key=lambda x: x.start_time)
    
    # Min-heap to track available courts
    # Each element is a Court object
    available_courts = []
    
    # Track assignments
    assignments = []
    
    # Counter for creating new court IDs
    next_court_id = 0
    
    for booking in sorted_bookings:
        # Find an available court (available_time <= booking start_time)
        court = None
        
        # Check if any existing court is available
        if available_courts and available_courts[0].available_time <= booking.start_time:
            court = heapq.heappop(available_courts)
        else:
            # Need a new court
            court = Court(court_id=next_court_id)
            next_court_id += 1
        
        # Assign booking to court
        assignments.append(CourtAssignment(
            booking_id=booking.id,
            court_id=court.court_id,
            start_time=booking.start_time,
            finish_time=booking.finish_time
        ))
        
        # Update court state
        court.available_time = booking.finish_time
        court.usage_count += 1
        
        # Check if court needs maintenance after this booking
        if court.usage_count >= durability:
            # Schedule maintenance
            court.available_time += maintenance_time
            court.usage_count = 0  # Reset usage count after maintenance
        
        # Put court back in the heap
        heapq.heappush(available_courts, court)
    
    return assignments


def get_total_courts_needed(assignments: List[CourtAssignment]) -> int:
    """Helper function to get total number of courts used"""
    if not assignments:
        return 0
    return max(assignment.court_id for assignment in assignments) + 1


def print_detailed_schedule(assignments: List[CourtAssignment], 
                          maintenance_time: int, 
                          durability: int):
    """Print detailed schedule showing maintenance periods"""
    if not assignments:
        print("No bookings to assign")
        return
    
    # Group by court and sort by time
    courts = {}
    for assignment in assignments:
        if assignment.court_id not in courts:
            courts[assignment.court_id] = []
        courts[assignment.court_id].append(assignment)
    
    for court_id in courts:
        courts[court_id].sort(key=lambda x: x.start_time)
    
    print(f"Total courts needed: {get_total_courts_needed(assignments)}")
    print(f"Durability: {durability} bookings")
    print(f"Maintenance time: {maintenance_time}")
    print("\nDetailed Schedule:")
    
    for court_id in sorted(courts.keys()):
        print(f"\nCourt {court_id}:")
        usage_count = 0
        
        for i, assignment in enumerate(courts[court_id]):
            usage_count += 1
            print(f"  Booking {assignment.booking_id}: {assignment.start_time}-{assignment.finish_time} "
                  f"(usage: {usage_count}/{durability})")
            
            # Check if maintenance happens after this booking
            if usage_count >= durability:
                maintenance_end = assignment.finish_time + maintenance_time
                print(f"    → Maintenance: {assignment.finish_time}-{maintenance_end}")
                usage_count = 0  # Reset after maintenance


def compare_durability_scenarios(bookings: List[BookingRecord]):
    """Compare different durability and maintenance time scenarios"""
    scenarios = [
        (0, 1),   # No maintenance (infinite durability)
        (2, 2),   # Maintenance every 2 bookings, 2 time units
        (1, 5),   # Maintenance after every booking, 5 time units  
        (3, 3),   # Maintenance every 3 bookings, 3 time units
    ]
    
    print("=== Comparison of Different Durability Scenarios ===")
    for durability, maintenance_time in scenarios:
        if durability == 0:
            # Special case: no maintenance needed
            from part_a_basic_assignment import assign_courts
            assignments = assign_courts(bookings)
            courts_needed = get_total_courts_needed(assignments)
            print(f"No maintenance: {courts_needed} courts")
        else:
            assignments = assign_courts_with_durability_maintenance(
                bookings, maintenance_time, durability
            )
            courts_needed = get_total_courts_needed(assignments)
            print(f"Durability {durability}, Maintenance {maintenance_time}: {courts_needed} courts")


# Example usage and test cases
if __name__ == "__main__":
    print("=== Test Case 1: Basic durability maintenance ===")
    bookings1 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 10, 20),  # Same court, usage = 2
        BookingRecord(3, 20, 30),  # Would trigger maintenance
        BookingRecord(4, 25, 35),  # Overlaps, needs different court
    ]
    
    assignments1 = assign_courts_with_durability_maintenance(
        bookings1, maintenance_time=5, durability=2
    )
    print_detailed_schedule(assignments1, maintenance_time=5, durability=2)
    
    print("\n=== Test Case 2: High durability (no maintenance needed) ===")
    assignments2 = assign_courts_with_durability_maintenance(
        bookings1, maintenance_time=10, durability=10
    )
    print_detailed_schedule(assignments2, maintenance_time=10, durability=10)
    
    print("\n=== Test Case 3: Low durability (frequent maintenance) ===")
    assignments3 = assign_courts_with_durability_maintenance(
        bookings1, maintenance_time=3, durability=1
    )
    print_detailed_schedule(assignments3, maintenance_time=3, durability=1)
    
    print("\n=== Test Case 4: Complex scenario ===")
    bookings4 = [
        BookingRecord(1, 0, 5),
        BookingRecord(2, 5, 10),
        BookingRecord(3, 10, 15),  # 3rd booking on same court -> maintenance
        BookingRecord(4, 12, 17),  # Overlaps, different court
        BookingRecord(5, 20, 25),  # Can use court 0 after maintenance
        BookingRecord(6, 17, 22),  # Can use court 1
    ]
    
    assignments4 = assign_courts_with_durability_maintenance(
        bookings4, maintenance_time=4, durability=2
    )
    print_detailed_schedule(assignments4, maintenance_time=4, durability=2)
    
    print("\n")
    compare_durability_scenarios(bookings4)
