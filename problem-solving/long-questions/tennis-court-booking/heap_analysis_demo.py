"""
Detailed Analysis: Why Heap Size = Minimum Courts Needed

This demonstrates step-by-step how the heap tracks active courts
and why len(heap) gives us the minimum number of courts.
"""

import heapq
from typing import List, NamedTuple


class BookingRecord(NamedTuple):
    id: int
    start_time: int
    finish_time: int


def analyze_heap_approach_step_by_step(booking_records: List[BookingRecord]):
    """
    Detailed step-by-step analysis of the heap approach
    """
    print("=== STEP-BY-STEP HEAP ANALYSIS ===")
    print("Bookings:", [(b.id, b.start_time, b.finish_time) for b in booking_records])
    print()
    
    # Sort bookings by start time
    sorted_bookings = sorted(booking_records, key=lambda x: x.start_time)
    
    # Min-heap to track court end times
    court_end_times = []
    max_courts_needed = 0
    
    for i, booking in enumerate(sorted_bookings):
        print(f"Step {i+1}: Processing Booking {booking.id} ({booking.start_time}-{booking.finish_time})")
        print(f"  Current heap: {court_end_times}")
        
        # Check if any court is available
        if court_end_times and court_end_times[0] <= booking.start_time:
            earliest_available = heapq.heappop(court_end_times)
            print(f"  ✅ REUSE court (was free at {earliest_available}, booking starts at {booking.start_time})")
            action = "REUSED"
        else:
            if court_end_times:
                print(f"  ❌ NEW court needed (earliest free at {court_end_times[0]}, booking starts at {booking.start_time})")
            else:
                print(f"  ❌ NEW court needed (no courts exist yet)")
            action = "NEW"
        
        # Add this booking's end time
        heapq.heappush(court_end_times, booking.finish_time)
        
        print(f"  Action: {action} court")
        print(f"  Updated heap: {court_end_times}")
        print(f"  Active courts: {len(court_end_times)}")
        
        max_courts_needed = max(max_courts_needed, len(court_end_times))
        print(f"  Max courts so far: {max_courts_needed}")
        print()
    
    print(f"FINAL RESULT: {len(court_end_times)} courts needed")
    return len(court_end_times)


def demonstrate_why_heap_size_works():
    """
    Demonstrate the key insight: heap size = simultaneous active courts
    """
    print("\n" + "="*60)
    print("WHY HEAP SIZE = MINIMUM COURTS NEEDED")
    print("="*60)
    
    print("""
KEY INSIGHTS:

1. 🏗️  HEAP INVARIANT: At any time, heap contains end times of ALL currently active courts
   
2. 🔄 GREEDY REUSE: We always try to reuse the earliest available court
   - If heap[0] <= start_time: reuse that court (pop + push)
   - Otherwise: all courts busy, need NEW court (just push)

3. 📊 HEAP SIZE = ACTIVE COURTS: len(heap) = number of courts currently in use

4. 🎯 MAXIMUM = ANSWER: The maximum heap size during processing = minimum courts needed
""")


def visual_timeline_analysis(booking_records: List[BookingRecord]):
    """
    Show a timeline view to visualize why heap size works
    """
    print("\n" + "="*60)
    print("TIMELINE VISUALIZATION")
    print("="*60)
    
    # Create timeline events
    events = []
    for booking in booking_records:
        events.append((booking.start_time, 'START', booking.id))
        events.append((booking.finish_time, 'END', booking.id))
    
    events.sort(key=lambda x: (x[0], x[1] == 'END'))  # END before START at same time
    
    active_bookings = set()
    max_concurrent = 0
    
    print("Time | Event      | Active Bookings | Active Count")
    print("-" * 50)
    
    for time, event_type, booking_id in events:
        if event_type == 'START':
            active_bookings.add(booking_id)
            action = f"START B{booking_id}"
        else:
            active_bookings.discard(booking_id)
            action = f"END B{booking_id}  "
        
        max_concurrent = max(max_concurrent, len(active_bookings))
        print(f"{time:4} | {action:10} | {sorted(active_bookings)!s:15} | {len(active_bookings)}")
    
    print(f"\nMaximum concurrent bookings: {max_concurrent}")
    print(f"This equals the minimum courts needed!")


# Test with different scenarios
if __name__ == "__main__":
    # Example 1: Progressive overlap
    print("EXAMPLE 1: Progressive Overlap")
    bookings1 = [
        BookingRecord(1, 1, 5),   # Court 1
        BookingRecord(2, 2, 6),   # Court 2 (overlaps with 1) 
        BookingRecord(3, 3, 7),   # Court 3 (overlaps with 1,2)
        BookingRecord(4, 8, 10),  # Court 1 (can reuse after 1 ends)
    ]
    
    result1 = analyze_heap_approach_step_by_step(bookings1)
    visual_timeline_analysis(bookings1)
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Adjacent Bookings")
    bookings2 = [
        BookingRecord(1, 0, 10),
        BookingRecord(2, 10, 20),  # Starts exactly when 1 ends
        BookingRecord(3, 20, 30),  # Starts exactly when 2 ends
    ]
    
    result2 = analyze_heap_approach_step_by_step(bookings2)
    visual_timeline_analysis(bookings2)
    
    demonstrate_why_heap_size_works()
