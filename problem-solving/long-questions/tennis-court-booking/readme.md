# Tennis Court Booking System - Complete Solution

A comprehensive solution to the tennis court scheduling problem with multiple variations and optimizations.

## Problem Overview

This is a classic **interval scheduling** problem with multiple variations. The core challenge is to efficiently assign tennis court bookings to minimize the number of courts needed while handling various constraints like maintenance time and durability.

---

## Part A: Basic Court Assignment

### Problem Statement

Given a list of tennis court bookings with start and finish times, return a plan assigning each booking to a specific court, ensuring each court is used by only one booking at a time and using the minimum number of courts.

### Data Structure

```python
class BookingRecord:
    id: int          # ID of the booking
    start_time: int  # Start time
    finish_time: int # End time
```

### Algorithm & Intuition

This is the classic **"Meeting Rooms II"** problem. The key insight is:

- **Greedy Strategy**: Always try to reuse the earliest available court
- **Heap-based approach**: Track when each court becomes available using a min-heap

**Algorithm Steps:**

1. Sort bookings by start time
2. Use min-heap to track court availability (end times)
3. For each booking:
   - If earliest court is available (end_time ≤ start_time), reuse it
   - Otherwise, allocate a new court
4. Track specific court assignments

**Time Complexity:** O(n log n) - sorting + heap operations  
**Space Complexity:** O(n) - heap and result storage

**Why This Works:**

- Sorting ensures we process bookings in chronological order
- Heap gives us the earliest available court in O(log n)
- Greedy choice is optimal: no benefit in using a later-available court when an earlier one is free

---

## Part B: Fixed Maintenance Time

### Problem Statement

After each booking, a fixed amount of time X is needed to maintain the court before it can be rented again.

### Key Modification

**Critical Insight:** When a booking finishes at time T, the court becomes available at time **T + maintenance_time** (not just T).

### Algorithm Changes

- Same basic structure as Part A
- **Only change:** Update court availability to `finish_time + maintenance_time`

**Impact Analysis:**

- Maintenance time reduces court reusability
- More courts needed when maintenance_time > gap between bookings
- With maintenance_time = 0, reduces to Part A

**Example:**

```
Bookings: [(0,10), (12,20)]
- Without maintenance: 1 court (gap = 2)
- With maintenance_time = 3: 2 courts (gap < maintenance_time)
```

---

## Part C: Durability-Based Maintenance

### Problem Statement

Courts only need maintenance after X bookings (durability). After X bookings, a court needs Y maintenance time before it can be used again.

### Advanced State Tracking

This is the most complex variant requiring per-court state management:

```python
@dataclass
class Court:
    court_id: int
    available_time: int = 0  # When court becomes available
    usage_count: int = 0     # Bookings since last maintenance
```

### Algorithm & Intuition

**Key Insights:**

- Track usage count per court
- Trigger maintenance when `usage_count >= durability`
- Reset usage count after maintenance

**Algorithm Steps:**

1. Sort bookings by start time
2. For each booking:
   - Find available court (not in maintenance)
   - Assign booking and increment usage count
   - If `usage_count >= durability`:
     - Schedule maintenance: `available_time += maintenance_time`
     - Reset usage count to 0
3. Update court availability

**Strategic Implications:**

- Higher durability = fewer maintenance periods = fewer courts needed
- Lower durability = frequent maintenance = more courts needed
- Maintenance time affects how long courts are unavailable

**Example Scenarios:**

- Durability=∞, maintenance_time=0: Same as Part A
- Durability=1, maintenance_time=X: Same as Part B
- Durability=2, maintenance_time=5: Maintenance every 2 bookings

---

## Part D: Minimum Courts Calculator

### Problem Statement

Simplified version: find the minimum number of courts needed without assigning specific bookings to courts.

### Two Efficient Approaches

#### 1. Sweep Line Algorithm (Event-Based)

**Intuition:** At any time, courts needed = number of active bookings

**Algorithm:**

1. Create START and END events for each booking
2. Sort events by time (END before START at same time)
3. Sweep through events, tracking active bookings
4. Return maximum active count

**Why END before START:** If booking ends at time T and another starts at T, they don't conflict.

#### 2. Heap-Based Approach

**Intuition:** Same as Part A but just count courts instead of tracking assignments

**Algorithm:**

1. Sort bookings by start time
2. Use heap to track court end times
3. Reuse earliest available court or create new one
4. Return heap size (total courts used)

**Time Complexity:** O(n log n) for both approaches  
**Space Complexity:** O(n)

**When to Use:**

- Sweep line: Better for theoretical understanding, handles edge cases naturally
- Heap-based: More intuitive if you understand Part A, easier to extend

---

## Part E: Conflict Detection

### Problem Statement

Check if two bookings conflict with each other.

### Interval Overlap Logic

**Key Insight:** Two intervals [a,b] and [c,d] do NOT overlap if:

- `b ≤ c` (first ends before/when second starts)
- `d ≤ a` (second ends before/when first starts)

**Simple Implementation:**

```python
def bookings_conflict(booking1, booking2):
    return not (booking1.finish_time <= booking2.start_time or
                booking2.finish_time <= booking1.start_time)
```

**Alternative (Explicit Overlap):**

```python
def bookings_conflict(booking1, booking2):
    return (booking1.start_time < booking2.finish_time and
            booking2.start_time < booking1.finish_time)
```

**Time Complexity:** O(1)  
**Space Complexity:** O(1)

**Extensions:**

- `find_all_conflicts()`: O(n²) to find all conflicting pairs
- `get_conflict_matrix()`: Useful for visualizing conflicts
- Critical for understanding why certain number of courts is needed

---

## Complexity Analysis Summary

| Part | Time Complexity | Space Complexity | Key Insight                          |
| ---- | --------------- | ---------------- | ------------------------------------ |
| A    | O(n log n)      | O(n)             | Greedy heap-based assignment         |
| B    | O(n log n)      | O(n)             | Add maintenance to availability time |
| C    | O(n log n)      | O(n)             | Track per-court usage state          |
| D    | O(n log n)      | O(n)             | Count max concurrent bookings        |
| E    | O(1)            | O(1)             | Interval overlap detection           |

---

## Real-World Applications

### Tennis Club Management

- **Part A:** Basic court scheduling system
- **Part B:** Account for cleaning/setup time between bookings
- **Part C:** Account for periodic deep maintenance (resurfacing, etc.)
- **Part D:** Quick capacity planning for court expansion
- **Part E:** Conflict resolution in booking systems

### Beyond Tennis Courts

- **Meeting room booking** (Parts A, B, D)
- **Operating room scheduling** (Parts B, C - sterilization time)
- **Server resource allocation** (Parts A, D)
- **Vehicle/equipment rental** (Parts B, C - maintenance cycles)

---

## Edge Cases & Considerations

### Time Boundary Handling

- **Adjacent bookings** (end_time = start_time): No conflict by definition
- **Zero-duration bookings**: Handle gracefully
- **Negative times**: Validate input data

### Maintenance Scenarios

- **Zero maintenance time**: Reduces to basic problem
- **Infinite durability**: No periodic maintenance needed
- **Maintenance longer than gaps**: Forces more courts

### Scale Considerations

- **Large datasets**: All algorithms are O(n log n), scale well
- **Real-time updates**: Heap-based approaches handle insertions efficiently
- **Memory constraints**: Conflict detection is most memory-efficient

---

## Implementation Files

- `part_a_basic_assignment.py` - Basic court assignment with detailed examples
- `part_b_maintenance_time.py` - Fixed maintenance time after each booking
- `part_c_durability_maintenance.py` - Maintenance after X bookings
- `part_d_minimum_courts.py` - Minimum courts calculation (two approaches)
- `part_e_conflict_detection.py` - Booking conflict detection with edge cases

Each file includes comprehensive test cases, edge case handling, and detailed output for understanding the algorithms.
