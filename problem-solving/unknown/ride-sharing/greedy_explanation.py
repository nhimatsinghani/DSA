"""
Greedy Algorithm Intuition for Ride Sharing Problem
==================================================

The key insight: "Always pick the ride that ends earliest among available options"

WHY DOES THIS WORK?
==================

Think of it this way: You're a driver and you want to maximize the number of rides.
At any point in time, you have several ride requests to choose from.

INTUITION: If you pick a ride that ends later, you're "blocking" yourself from 
taking future rides that might start during that extended time period.

By always picking the ride that ends earliest, you:
1. Free up your schedule as soon as possible
2. Leave maximum opportunity for future rides
3. Never make a choice that could have been better

Let's visualize this with examples:
"""

def visualize_greedy_choice():
    """Demonstrate why greedy choice works with visual timeline."""
    
    print("=== VISUAL EXAMPLE 1: Why sort by END time? ===\n")
    
    requests = [[1,3], [2,5], [4,7], [8,10]]
    print("Original requests:", requests)
    print("\nTimeline visualization:")
    print("Time:  1  2  3  4  5  6  7  8  9  10")
    print("Ride1: [--1--]           ")  # [1,3]
    print("Ride2:    [----2----]    ")  # [2,5] 
    print("Ride3:          [--3--]  ")  # [4,7]
    print("Ride4:                [4]")  # [8,10]
    print()
    
    # Sort by end time
    sorted_by_end = sorted(requests, key=lambda x: x[1])
    print("After sorting by END time:", sorted_by_end)
    print("\nGreedy selection process:")
    print("1. Pick [1,3] (ends earliest) ✓")
    print("2. Consider [2,5]: starts at 2, but we're busy until 3. Skip ✗") 
    print("3. Consider [4,7]: starts at 4, we're free since 3. Pick ✓")
    print("4. Consider [8,10]: starts at 8, we're free since 7. Pick ✓")
    print("\nResult: [1,3], [4,7], [8,10] = 3 rides")
    
def show_why_other_strategies_fail():
    """Show why other greedy strategies don't work."""
    
    print("\n=== WHY OTHER STRATEGIES FAIL ===\n")
    
    requests = [[1,3], [2,5], [4,7], [8,10]]
    
    print("Strategy 1: Sort by START time")
    sorted_by_start = sorted(requests, key=lambda x: x[0])
    print("Sorted by start:", sorted_by_start)
    print("Selection: Pick [1,3], then [2,5] overlaps, skip [4,7] overlaps, pick [8,10]")
    print("Result: [1,3], [8,10] = 2 rides (SUBOPTIMAL!)")
    print()
    
    print("Strategy 2: Sort by DURATION (shortest first)")
    sorted_by_duration = sorted(requests, key=lambda x: x[1] - x[0])
    print("Sorted by duration:", sorted_by_duration)
    print("Durations:", [(req, req[1]-req[0]) for req in sorted_by_duration])
    print("This doesn't consider timing at all - could pick rides that block many others")
    print()

def prove_optimality_intuition():
    """Explain why the greedy choice is optimal."""
    
    print("=== WHY IS GREEDY OPTIMAL? ===\n")
    
    print("CLAIM: Greedy (earliest end time) gives optimal solution")
    print()
    print("PROOF INTUITION (Exchange Argument):")
    print("1. Suppose there's an optimal solution OPT that's different from greedy solution G")
    print("2. Let 'x' be the first ride where OPT and G differ")
    print("3. In OPT, some other ride 'y' is chosen instead of 'x'")
    print("4. Since greedy chose 'x', we know x ends before or same time as y")
    print("5. We can replace 'y' with 'x' in OPT without affecting other rides")
    print("6. This gives us a solution at least as good as OPT")
    print("7. By repeating this process, we can transform OPT into G")
    print("8. Therefore, G is optimal!")
    
def step_by_step_example():
    """Walk through the algorithm step by step."""
    
    print("\n=== STEP BY STEP WALKTHROUGH ===\n")
    
    requests = [[1,3], [2,5], [4,7], [8,10]]
    print(f"Input: {requests}")
    
    # Sort by end time
    sorted_requests = sorted(requests, key=lambda x: x[1])
    print(f"After sorting by end time: {sorted_requests}")
    
    print("\nSimulation:")
    print("Time:  1  2  3  4  5  6  7  8  9  10")
    print("       |  |  |  |  |  |  |  |  |  |")
    
    selected = []
    last_end = 0
    
    for i, (start, end) in enumerate(sorted_requests):
        print(f"\nStep {i+1}: Considering ride [{start},{end}]")
        print(f"   Current schedule ends at time {last_end}")
        print(f"   This ride starts at time {start}")
        
        if start >= last_end:
            selected.append([start, end])
            last_end = end
            print(f"   ✓ CAN TAKE IT! New end time: {end}")
            print(f"   Current rides: {selected}")
        else:
            print(f"   ✗ CONFLICT! We're busy until {last_end}, ride starts at {start}")
    
    print(f"\nFinal result: {selected}")
    print(f"Total rides: {len(selected)}")

def counter_example_for_start_time():
    """Show a concrete example where sorting by start time fails."""
    
    print("\n=== CONCRETE EXAMPLE: START TIME FAILS ===\n")
    
    # Example where greedy by start time is suboptimal
    requests = [[1, 10], [2, 3], [4, 5]]
    print(f"Requests: {requests}")
    print("\nTimeline:")
    print("Time:  1  2  3  4  5  6  7  8  9  10")
    print("Ride1: [--------1---------]")  # [1,10] - long ride
    print("Ride2:    [2]")                 # [2,3]  - short ride
    print("Ride3:       [3]")              # [4,5]  - short ride
    
    print("\nGreedy by START time:")
    print("1. Pick [1,10] (starts earliest)")
    print("2. Skip [2,3] and [4,5] (both conflict)")
    print("Result: 1 ride")
    
    print("\nGreedy by END time:")
    sorted_by_end = sorted(requests, key=lambda x: x[1])
    print(f"Sorted: {sorted_by_end}")
    print("1. Pick [2,3] (ends earliest)")
    print("2. Pick [4,5] (starts after [2,3] ends)")
    print("3. Skip [1,10] (conflicts with both)")
    print("Result: 2 rides (OPTIMAL!)")

if __name__ == "__main__":
    visualize_greedy_choice()
    show_why_other_strategies_fail()
    step_by_step_example()
    counter_example_for_start_time()
    prove_optimality_intuition()
    
    print("\n" + "="*60)
    print("KEY TAKEAWAY:")
    print("The magic is in sorting by END time, not start time!")
    print("By ending early, you maximize future opportunities.")
    print("="*60)


