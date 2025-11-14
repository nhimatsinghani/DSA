"""
Tennis Court Booking - Part E: Booking Conflict Detection

Problem: Write a function that checks if two bookings conflict with each other.

Two bookings conflict if their time intervals overlap. This is a fundamental
interval overlap problem.

Key Insight: Two intervals [a,b] and [c,d] do NOT overlap if:
- b <= c (first ends before or when second starts)
- d <= a (second ends before or when first starts)

If neither condition is true, they overlap.

Time Complexity: O(1) - constant time comparison
Space Complexity: O(1) - no extra space needed
"""

from typing import NamedTuple, List, Tuple


class BookingRecord(NamedTuple):
    """Represents a tennis court booking"""
    id: int
    start_time: int
    finish_time: int


def bookings_conflict(booking1: BookingRecord, booking2: BookingRecord) -> bool:
    """
    Check if two bookings have conflicting time periods.
    
    Args:
        booking1: First booking
        booking2: Second booking
        
    Returns:
        True if bookings conflict (overlap in time), False otherwise
        
    Examples:
        BookingRecord(1, 0, 10) vs BookingRecord(2, 5, 15) -> True (overlap 5-10)
        BookingRecord(1, 0, 10) vs BookingRecord(2, 10, 20) -> False (adjacent, no overlap)
        BookingRecord(1, 0, 10) vs BookingRecord(2, 15, 20) -> False (gap between them)
    """
    # Two intervals [a,b] and [c,d] do NOT overlap if:
    # - b <= c (first ends before or when second starts)
    # - d <= a (second ends before or when first starts)
    
    # Check if they DON'T overlap
    no_overlap = (booking1.finish_time <= booking2.start_time or 
                  booking2.finish_time <= booking1.start_time)
    
    # They conflict if they DO overlap
    return not no_overlap


def bookings_conflict_explicit(booking1: BookingRecord, booking2: BookingRecord) -> bool:
    """
    Alternative implementation with explicit overlap conditions.
    Same result as bookings_conflict() but written more explicitly.
    """
    # Overlap conditions:
    # - booking1 starts before booking2 ends: booking1.start_time < booking2.finish_time
    # - booking2 starts before booking1 ends: booking2.start_time < booking1.finish_time
    
    return (booking1.start_time < booking2.finish_time and 
            booking2.start_time < booking1.finish_time)


def find_all_conflicts(booking_records: List[BookingRecord]) -> List[Tuple[BookingRecord, BookingRecord]]:
    """
    Find all pairs of bookings that conflict with each other.
    
    Args:
        booking_records: List of bookings to check
        
    Returns:
        List of tuples containing conflicting booking pairs
        
    Time Complexity: O(n²) where n is number of bookings
    """
    conflicts = []
    
    for i in range(len(booking_records)):
        for j in range(i + 1, len(booking_records)):
            if bookings_conflict(booking_records[i], booking_records[j]):
                conflicts.append((booking_records[i], booking_records[j]))
    
    return conflicts


def get_conflict_matrix(booking_records: List[BookingRecord]) -> List[List[bool]]:
    """
    Create a conflict matrix showing which bookings conflict with each other.
    
    Args:
        booking_records: List of bookings
        
    Returns:
        2D matrix where matrix[i][j] = True if booking i conflicts with booking j
    """
    n = len(booking_records)
    matrix = [[False] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j:  # A booking doesn't conflict with itself
                matrix[i][j] = bookings_conflict(booking_records[i], booking_records[j])
    
    return matrix


def print_conflict_analysis(booking_records: List[BookingRecord]):
    """Print detailed conflict analysis for a set of bookings"""
    print("Booking Details:")
    for booking in booking_records:
        print(f"  Booking {booking.id}: {booking.start_time}-{booking.finish_time}")
    
    conflicts = find_all_conflicts(booking_records)
    
    print(f"\nTotal conflicts found: {len(conflicts)}")
    
    if conflicts:
        print("Conflicting pairs:")
        for booking1, booking2 in conflicts:
            overlap_start = max(booking1.start_time, booking2.start_time)
            overlap_end = min(booking1.finish_time, booking2.finish_time)
            print(f"  Booking {booking1.id} ({booking1.start_time}-{booking1.finish_time}) "
                  f"conflicts with Booking {booking2.id} ({booking2.start_time}-{booking2.finish_time})")
            print(f"    Overlap period: {overlap_start}-{overlap_end}")
    else:
        print("No conflicts found - all bookings can use the same court!")
    
    # Print conflict matrix for small sets
    if len(booking_records) <= 5:
        print("\nConflict Matrix (rows=bookings, cols=bookings):")
        matrix = get_conflict_matrix(booking_records)
        
        # Header
        print("   ", end="")
        for booking in booking_records:
            print(f"B{booking.id:2}", end=" ")
        print()
        
        # Matrix rows
        for i, booking in enumerate(booking_records):
            print(f"B{booking.id:2}", end=" ")
            for j in range(len(booking_records)):
                print(" X " if matrix[i][j] else " - ", end=" ")
            print()


def test_edge_cases():
    """Test various edge cases for conflict detection"""
    test_cases = [
        # (booking1, booking2, expected_conflict, description)
        (BookingRecord(1, 0, 10), BookingRecord(2, 10, 20), False, "Adjacent bookings"),
        (BookingRecord(1, 0, 10), BookingRecord(2, 5, 15), True, "Partial overlap"),
        (BookingRecord(1, 0, 20), BookingRecord(2, 5, 15), True, "One contains other"),
        (BookingRecord(1, 5, 15), BookingRecord(2, 0, 20), True, "One is contained"),
        (BookingRecord(1, 0, 10), BookingRecord(2, 15, 25), False, "No overlap with gap"),
        (BookingRecord(1, 10, 20), BookingRecord(2, 0, 10), False, "Adjacent (reverse order)"),
        (BookingRecord(1, 5, 10), BookingRecord(2, 5, 10), True, "Identical intervals"),
        (BookingRecord(1, 0, 5), BookingRecord(2, 3, 8), True, "Overlap at end/start"),
    ]
    
    print("=== Edge Case Testing ===")
    for booking1, booking2, expected, description in test_cases:
        result = bookings_conflict(booking1, booking2)
        result_explicit = bookings_conflict_explicit(booking1, booking2)
        
        status = "✓" if result == expected else "✗"
        consistency = "✓" if result == result_explicit else "✗"
        
        print(f"{status} {description}")
        print(f"  B{booking1.id}({booking1.start_time}-{booking1.finish_time}) vs "
              f"B{booking2.id}({booking2.start_time}-{booking2.finish_time})")
        print(f"  Expected: {expected}, Got: {result}, Consistent: {consistency}")
        print()


# Example usage and test cases
if __name__ == "__main__":
    test_edge_cases()
    
    print("=== Test Case 1: Mixed conflicts ===")
    bookings1 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 5, 15),   # Conflicts with 1
        BookingRecord(3, 20, 30),  # No conflicts
        BookingRecord(4, 12, 18)   # Conflicts with 2
    ]
    print_conflict_analysis(bookings1)
    
    print("\n=== Test Case 2: No conflicts ===")
    bookings2 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 10, 20),
        BookingRecord(3, 20, 30)
    ]
    print_conflict_analysis(bookings2)
    
    print("\n=== Test Case 3: All conflict ===")
    bookings3 = [
        BookingRecord(1, 0, 15),
        BookingRecord(2, 5, 20),
        BookingRecord(3, 10, 25)
    ]
    print_conflict_analysis(bookings3)
