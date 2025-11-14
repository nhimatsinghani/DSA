"""
Weighted Interval Scheduling - Maximize Earnings
===============================================

Follow-up: What if drivers get paid more for longer rides? 
How would you maximize earnings instead of ride count?

This transforms the problem from unweighted to weighted interval scheduling.
We'll implement both recursive-memoized and bottom-up DP solutions.

Earnings Model: 
- Base fare: $5 per ride
- Distance fare: $2 per minute of ride duration
- Total earnings = base_fare + (duration * distance_rate)

Two approaches:
1. Recursive with Memoization (Top-Down DP)
2. Bottom-Up Dynamic Programming
"""

def calculate_earnings(start, end, base_fare=5, distance_rate=2):
    """
    Calculate earnings for a ride based on duration.
    
    Args:
        start: Pickup time
        end: Dropoff time  
        base_fare: Fixed amount per ride
        distance_rate: Amount per minute
        
    Returns:
        float: Total earnings for this ride
    """
    duration = end - start
    return base_fare + (duration * distance_rate)

def find_latest_non_overlapping_by_end(intervals, i):
    """
    Find latest interval that doesn't overlap with interval i.
    Assumes intervals are sorted by END time.
    
    Args:
        intervals: List of (start, end, earnings) sorted by end time
        i: Current interval index
        
    Returns:
        Index of latest non-overlapping interval, or -1 if none
    """
    # Binary search for rightmost interval that ends <= intervals[i].start
    target_start = intervals[i][0]
    left, right = 0, i - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        if intervals[mid][1] <= target_start:
            result = mid
            left = mid + 1
        else:
            right = mid - 1
    
    return result

# =============================================================================
# APPROACH 1: RECURSIVE WITH MEMOIZATION (TOP-DOWN DP)
# =============================================================================

def max_earnings_recursive_memo(requests, base_fare=5, distance_rate=2):
    """
    Find maximum earnings using recursive approach with memoization.
    
    Args:
        requests: List of [pickup_time, dropoff_time] intervals
        base_fare: Fixed earning per ride
        distance_rate: Earning per minute
        
    Returns:
        tuple: (max_earnings, selected_rides)
    """
    if not requests:
        return 0, []
    
    # Create intervals with earnings: (start, end, earnings)
    intervals = []
    for start, end in requests:
        earnings = calculate_earnings(start, end, base_fare, distance_rate)
        intervals.append((start, end, earnings))
    
    # Sort by end time (classic weighted interval scheduling)
    intervals.sort(key=lambda x: x[1])
    
    n = len(intervals)
    memo = {}
    
    def solve(i):
        """
        Recursive function: maximum earnings from intervals i to n-1
        
        Args:
            i: Starting index
            
        Returns:
            tuple: (max_earnings, list_of_selected_intervals)
        """
        if i >= n:
            return 0, []
        
        if i in memo:
            return memo[i]
        
        # Option 1: Skip current interval
        skip_earnings, skip_intervals = solve(i + 1)
        
        # Option 2: Take current interval
        current_earnings = intervals[i][2]  # earnings of interval i
        
        # Find next non-overlapping interval
        next_i = i + 1
        while next_i < n and intervals[next_i][0] < intervals[i][1]:
            next_i += 1
        
        take_future_earnings, take_future_intervals = solve(next_i)
        take_total_earnings = current_earnings + take_future_earnings
        take_intervals = [intervals[i]] + take_future_intervals
        
        # Choose the better option
        if take_total_earnings > skip_earnings:
            result = (take_total_earnings, take_intervals)
        else:
            result = (skip_earnings, skip_intervals)
        
        memo[i] = result
        return result
    
    return solve(0)

# =============================================================================
# APPROACH 2: BOTTOM-UP DYNAMIC PROGRAMMING
# =============================================================================

def max_earnings_dp(requests, base_fare=5, distance_rate=2):
    """
    Find maximum earnings using bottom-up DP.
    
    Args:
        requests: List of [pickup_time, dropoff_time] intervals
        base_fare: Fixed earning per ride  
        distance_rate: Earning per minute
        
    Returns:
        tuple: (max_earnings, selected_rides)
    """
    if not requests:
        return 0, []
    
    # Create intervals with earnings
    intervals = []
    for start, end in requests:
        earnings = calculate_earnings(start, end, base_fare, distance_rate)
        intervals.append((start, end, earnings))
    
    # Sort by end time
    intervals.sort(key=lambda x: x[1])
    
    n = len(intervals)
    
    # DP arrays
    dp = [0] * n  # dp[i] = max earnings from intervals 0..i
    take = [False] * n  # whether we take interval i in optimal solution
    
    # Base case
    dp[0] = intervals[0][2]
    take[0] = True
    
    # Fill DP table
    for i in range(1, n):
        # Option 1: Don't take current interval
        dont_take = dp[i-1]
        
        # Option 2: Take current interval
        current_earnings = intervals[i][2]
        
        # Find latest non-overlapping interval
        j = find_latest_non_overlapping_by_end(intervals, i)
        
        if j == -1:
            # No previous non-overlapping intervals
            take_earnings = current_earnings
        else:
            take_earnings = current_earnings + dp[j]
        
        # Choose better option
        if take_earnings > dont_take:
            dp[i] = take_earnings
            take[i] = True
        else:
            dp[i] = dont_take
            take[i] = False
    
    # Reconstruct solution
    selected = []
    i = n - 1
    while i >= 0:
        if take[i]:
            selected.append(intervals[i])
            # Jump to latest non-overlapping
            i = find_latest_non_overlapping_by_end(intervals, i)
        else:
            i -= 1
    
    selected.reverse()
    return dp[n-1], selected

# =============================================================================
# COMPARISON AND TESTING
# =============================================================================

def compare_approaches():
    """Compare recursive vs DP approaches."""
    
    print("=== WEIGHTED INTERVAL SCHEDULING COMPARISON ===\n")
    
    test_cases = [
        [[1,3], [2,5], [4,7], [8,10]],  # Original example
        [[1,10], [2,3], [4,5]],         # Long vs short rides
        [[1,2], [2,4], [4,6], [6,8]],   # No overlaps
        [[1,8], [2,4], [3,5], [6,7]]    # Various overlaps
    ]
    
    for i, requests in enumerate(test_cases):
        print(f"Test Case {i+1}: {requests}")
        
        # Show earnings for each ride
        print("Individual ride earnings:")
        for start, end in requests:
            earnings = calculate_earnings(start, end)
            duration = end - start
            print(f"  [{start},{end}]: {duration} min -> ${earnings}")
        
        # Recursive solution
        recursive_earnings, recursive_rides = max_earnings_recursive_memo(requests)
        
        # DP solution  
        dp_earnings, dp_rides = max_earnings_dp(requests)
        
        print(f"\nRecursive solution: ${recursive_earnings}")
        print(f"  Selected rides: {[(r[0], r[1]) for r in recursive_rides]}")
        print(f"  Total duration: {sum(r[1] - r[0] for r in recursive_rides)} min")
        
        print(f"DP solution: ${dp_earnings}")
        print(f"  Selected rides: {[(r[0], r[1]) for r in dp_rides]}")
        print(f"  Total duration: {sum(r[1] - r[0] for r in dp_rides)} min")
        
        print(f"Results match: {recursive_earnings == dp_earnings}")
        print("-" * 50)

def compare_with_unweighted():
    """Compare weighted vs unweighted solutions."""
    
    print("\n=== WEIGHTED vs UNWEIGHTED COMPARISON ===\n")
    
    # Import unweighted solution
    from greedy_solution import max_pool_matches_greedy_with_schedule
    
    requests = [[1,3], [2,8], [4,5]]  # Short-long-short pattern
    
    print(f"Requests: {requests}")
    print("Ride details:")
    for start, end in requests:
        earnings = calculate_earnings(start, end)
        duration = end - start
        print(f"  [{start},{end}]: {duration} min -> ${earnings}")
    
    # Unweighted (maximize count)
    unweighted_count, unweighted_rides = max_pool_matches_greedy_with_schedule(requests)
    
    # Weighted (maximize earnings)
    weighted_earnings, weighted_rides = max_earnings_dp(requests)
    
    print(f"\nUNWEIGHTED (maximize ride count):")
    print(f"  Rides taken: {unweighted_rides}")
    print(f"  Count: {unweighted_count}")
    print(f"  Total earnings: ${sum(calculate_earnings(r[0], r[1]) for r in unweighted_rides)}")
    
    print(f"\nWEIGHTED (maximize earnings):")
    print(f"  Rides taken: {[(r[0], r[1]) for r in weighted_rides]}")
    print(f"  Count: {len(weighted_rides)}")
    print(f"  Total earnings: ${weighted_earnings}")
    
    print(f"\nKey insight: Weighted approach chose {'same' if len(weighted_rides) == unweighted_count else 'different'} rides!")

def visualize_weighted_process():
    """Show step-by-step process for weighted DP."""
    
    print("\n=== WEIGHTED DP STEP-BY-STEP ===\n")
    
    requests = [[1,3], [2,5], [4,7]]
    print(f"Requests: {requests}")
    
    # Create intervals with earnings
    intervals = []
    for start, end in requests:
        earnings = calculate_earnings(start, end)
        intervals.append((start, end, earnings))
        print(f"  [{start},{end}] -> ${earnings} (duration: {end-start} min)")
    
    # Sort by end time
    intervals.sort(key=lambda x: x[1])
    print(f"\nSorted by end time: {intervals}")
    
    print(f"\nDP Process:")
    print("dp[i] = max(dp[i-1], earnings[i] + dp[j]) where j is latest non-overlapping")
    
    n = len(intervals)
    dp = [0] * n
    
    dp[0] = intervals[0][2]
    print(f"dp[0] = {dp[0]} (take first interval)")
    
    for i in range(1, n):
        dont_take = dp[i-1]
        current_earnings = intervals[i][2]
        
        j = find_latest_non_overlapping_by_end(intervals, i)
        if j == -1:
            take_earnings = current_earnings
            print(f"\nInterval {i}: {intervals[i]}")
            print(f"  No non-overlapping previous intervals")
            print(f"  Don't take: {dont_take}")
            print(f"  Take: {current_earnings}")
        else:
            take_earnings = current_earnings + dp[j]
            print(f"\nInterval {i}: {intervals[i]}")
            print(f"  Latest non-overlapping: index {j} = {intervals[j]}")
            print(f"  Don't take: {dont_take}")
            print(f"  Take: {current_earnings} + {dp[j]} = {take_earnings}")
        
        dp[i] = max(dont_take, take_earnings)
        choice = "TAKE" if take_earnings > dont_take else "DON'T TAKE"
        print(f"  Decision: {choice} -> dp[{i}] = {dp[i]}")
    
    print(f"\nFinal DP array: {dp}")
    print(f"Maximum earnings: ${dp[n-1]}")

if __name__ == "__main__":
    print("=== RIDE SHARING: MAXIMIZE EARNINGS ===\n")
    
    visualize_weighted_process()
    compare_approaches()
    compare_with_unweighted()
    
    print("\n=== ALGORITHM SUMMARY ===")
    print("RECURSIVE APPROACH:")
    print("1. Sort by end time")
    print("2. For each interval: max(skip, take + solve_rest)")
    print("3. Use memoization to avoid recomputation")
    print("4. Time: O(n²) worst case, O(n log n) average")
    print()
    print("DP APPROACH:")
    print("1. Sort by end time") 
    print("2. dp[i] = max(dp[i-1], earnings[i] + dp[j])")
    print("3. j = latest non-overlapping interval")
    print("4. Time: O(n log n), Space: O(n)")
    print()
    print("KEY DIFFERENCE FROM UNWEIGHTED:")
    print("- Greedy doesn't work for weighted version!")
    print("- Must consider earnings, not just count")
    print("- Longer rides might be worth taking over multiple short ones")

