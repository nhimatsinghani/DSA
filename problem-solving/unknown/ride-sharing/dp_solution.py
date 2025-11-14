"""
Ride Sharing Problem - Dynamic Programming Solution
==================================================

While greedy is optimal for unweighted intervals, DP shows a different approach
and easily extends to weighted intervals (which we'll need for the follow-up).

Algorithm:
1. Sort intervals by START time (not end time like greedy)
2. For each interval i, decide: include it or exclude it
3. If include: find latest non-overlapping interval using binary search
4. DP[i] = max(DP[i-1], 1 + DP[j]) where j is latest non-overlapping
5. Time: O(n log n), Space: O(n)

Key insight: Optimal substructure - solution for intervals 0..i depends on
optimal solutions for smaller subproblems.
"""

def find_latest_non_overlapping(intervals, i):
    """
    Find the latest interval that doesn't overlap with interval i.
    Uses binary search for O(log n) complexity.
    
    Args:
        intervals: List of [start, end] sorted by start time
        i: Current interval index
        
    Returns:
        Index of latest non-overlapping interval, or -1 if none
    """
    # We need intervals that END before or when interval i STARTS
    target_start = intervals[i][0]
    
    # Binary search for rightmost interval that ends <= target_start
    left, right = 0, i - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        if intervals[mid][1] <= target_start:
            result = mid  # This interval works, try to find a later one
            left = mid + 1
        else:
            right = mid - 1  # This interval overlaps, go left
    
    return result

def max_pool_matches_dp(requests):
    """
    Find maximum number of non-overlapping intervals using DP.
    
    Args:
        requests: List of [pickup_time, dropoff_time] intervals
        
    Returns:
        int: Maximum number of rides that can be served
        
    Time Complexity: O(n log n) - sorting + n binary searches
    Space Complexity: O(n) - DP array
    """
    if not requests:
        return 0
    
    n = len(requests)
    
    # Sort by START time (different from greedy!)
    intervals = sorted(requests, key=lambda x: x[0])
    
    # dp[i] = maximum rides we can get from intervals 0..i
    dp = [0] * n
    
    # Base case: first interval
    dp[0] = 1
    
    for i in range(1, n):
        # Option 1: Don't take current interval
        exclude_current = dp[i-1]
        
        # Option 2: Take current interval
        include_current = 1
        
        # Find latest non-overlapping interval
        j = find_latest_non_overlapping(intervals, i)
        if j != -1:
            include_current += dp[j]
        
        # Take the maximum
        dp[i] = max(exclude_current, include_current)
    
    return dp[n-1]

def max_pool_matches_dp_with_solution(requests):
    """
    DP solution that also returns the actual intervals selected.
    
    Returns:
        tuple: (count, selected_intervals)
    """
    if not requests:
        return 0, []
    
    n = len(requests)
    intervals = sorted(requests, key=lambda x: x[0])
    
    # DP array and decision tracking
    dp = [0] * n
    take = [False] * n  # Whether we take interval i in optimal solution
    
    dp[0] = 1
    take[0] = True
    
    for i in range(1, n):
        exclude_current = dp[i-1]
        include_current = 1
        
        j = find_latest_non_overlapping(intervals, i)
        if j != -1:
            include_current += dp[j]
        
        if include_current > exclude_current:
            dp[i] = include_current
            take[i] = True
        else:
            dp[i] = exclude_current
            take[i] = False
    
    # Reconstruct solution
    selected = []
    i = n - 1
    while i >= 0:
        if take[i]:
            selected.append(intervals[i])
            # Jump to latest non-overlapping
            i = find_latest_non_overlapping(intervals, i)
        else:
            i -= 1
    
    selected.reverse()  # We built it backwards
    return dp[n-1], selected

def visualize_dp_process():
    """Demonstrate the DP process step by step."""
    
    print("=== DYNAMIC PROGRAMMING WALKTHROUGH ===\n")
    
    requests = [[1,3], [2,5], [4,7], [8,10]]
    print(f"Original requests: {requests}")
    
    # Sort by start time
    intervals = sorted(requests, key=lambda x: x[0])
    print(f"Sorted by START time: {intervals}")
    
    n = len(intervals)
    dp = [0] * n
    
    print(f"\nDP Process:")
    print("For each interval, decide: include it or exclude it")
    print("dp[i] = max(dp[i-1], 1 + dp[j]) where j is latest non-overlapping\n")
    
    # Process each interval
    dp[0] = 1
    print(f"dp[0] = 1 (base case: take first interval {intervals[0]})")
    
    for i in range(1, n):
        exclude = dp[i-1]
        include = 1
        
        j = find_latest_non_overlapping(intervals, i)
        if j != -1:
            include += dp[j]
            print(f"\nInterval {i}: {intervals[i]}")
            print(f"  Latest non-overlapping: index {j} = {intervals[j]}")
            print(f"  Exclude current: dp[{i-1}] = {exclude}")
            print(f"  Include current: 1 + dp[{j}] = 1 + {dp[j]} = {include}")
        else:
            print(f"\nInterval {i}: {intervals[i]}")
            print(f"  No non-overlapping intervals before it")
            print(f"  Exclude current: dp[{i-1}] = {exclude}")
            print(f"  Include current: 1 + 0 = {include}")
        
        dp[i] = max(exclude, include)
        choice = "INCLUDE" if include > exclude else "EXCLUDE"
        print(f"  Decision: {choice} -> dp[{i}] = {dp[i]}")
    
    print(f"\nFinal DP array: {dp}")
    print(f"Maximum rides: {dp[n-1]}")

def compare_with_greedy():
    """Compare DP and greedy approaches."""
    
    print("\n=== COMPARISON: DP vs GREEDY ===\n")
    
    test_cases = [
        [[1,3], [2,5], [4,7], [8,10]],
        [[1,4], [2,3], [5,6]],
        [[1,2], [2,3], [3,4], [4,5]],
        [[1,10], [2,3], [4,5]]
    ]
    
    for i, requests in enumerate(test_cases):
        print(f"Test Case {i+1}: {requests}")
        
        # DP solution
        dp_count, dp_solution = max_pool_matches_dp_with_solution(requests)
        
        # Greedy solution (from previous file)
        from greedy_solution import max_pool_matches_greedy_with_schedule
        greedy_count, greedy_solution = max_pool_matches_greedy_with_schedule(requests)
        
        print(f"  DP solution:     {dp_count} rides -> {dp_solution}")
        print(f"  Greedy solution: {greedy_count} rides -> {greedy_solution}")
        print(f"  Same result: {dp_count == greedy_count}")
        print()

def test_dp_solution():
    """Test the DP implementation."""
    
    print("=== TESTING DP SOLUTION ===\n")
    
    test_cases = [
        ([[1,3], [2,5], [4,7], [8,10]], 3),
        ([[1,4], [2,5], [3,6]], 1),
        ([[1,2], [3,4], [5,6], [7,8]], 4),
        ([[1,3], [3,5], [5,7]], 3),
        ([], 0),
        ([[1,2]], 1)
    ]
    
    for requests, expected in test_cases:
        result = max_pool_matches_dp(requests)
        count, solution = max_pool_matches_dp_with_solution(requests)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: {requests}")
        print(f"   Expected: {expected}, Got: {result}")
        print(f"   Solution: {solution}")
        print()

if __name__ == "__main__":
    print("=== RIDE SHARING PROBLEM - DYNAMIC PROGRAMMING ===\n")
    
    test_dp_solution()
    visualize_dp_process()
    compare_with_greedy()
    
    print("=== ALGORITHM SUMMARY ===")
    print("1. Sort intervals by START time")
    print("2. For each interval: max(exclude, include)")
    print("3. Use binary search to find latest non-overlapping")
    print("4. Build up solution using optimal substructure")
    print("5. Same O(n log n) complexity as greedy, but different approach")
    print("6. Easily extends to weighted intervals!")


