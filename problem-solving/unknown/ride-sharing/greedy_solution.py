"""
Ride Sharing Problem - Greedy Solution
=====================================

Problem: Find the maximum number of riders that can share a single vehicle.
Given: Array of ride requests [pickup_time, dropoff_time]
Goal: Maximum number of non-overlapping rides

Greedy Algorithm:
1. Sort intervals by end time (dropoff_time)
2. Greedily select intervals that don't overlap with previously selected ones
3. Time Complexity: O(n log n) due to sorting
4. Space Complexity: O(1) excluding input

This is optimal for unweighted interval scheduling.
"""

def max_pool_matches_greedy(requests):
    """
    Find maximum number of non-overlapping ride requests using greedy approach.
    
    Args:
        requests: List of [pickup_time, dropoff_time] intervals
        
    Returns:
        int: Maximum number of rides that can be served
        
    Time Complexity: O(n log n)
    Space Complexity: O(1)
    """
    if not requests:
        return 0
    
    # Sort by end time (dropoff_time) - key insight of greedy algorithm
    requests.sort(key=lambda x: x[1])
    
    count = 1  # Take the first ride
    last_end_time = requests[0][1]  # Track when last ride ends
    
    for i in range(1, len(requests)):
        pickup_time, dropoff_time = requests[i]
        
        # If current ride starts after or when the last ride ends, we can take it
        if pickup_time >= last_end_time:
            count += 1
            last_end_time = dropoff_time
    
    return count

def max_pool_matches_greedy_with_schedule(requests):
    """
    Same as above but also returns the actual schedule of rides taken.
    
    Returns:
        tuple: (count, schedule) where schedule is list of selected intervals
    """
    if not requests:
        return 0, []
    
    # Sort by end time, but keep track of original intervals
    sorted_requests = sorted(requests, key=lambda x: x[1])
    
    schedule = [sorted_requests[0]]  # Take the first ride
    last_end_time = sorted_requests[0][1]
    
    for i in range(1, len(sorted_requests)):
        pickup_time, dropoff_time = sorted_requests[i]
        
        if pickup_time >= last_end_time:
            schedule.append([pickup_time, dropoff_time])
            last_end_time = dropoff_time
    
    return len(schedule), schedule

# Test cases
def test_greedy_solution():
    """Test the greedy solution with various cases."""
    
    # Test case 1: Example from problem
    requests1 = [[1,3], [2,5], [4,7], [8,10]]
    result1 = max_pool_matches_greedy(requests1)
    count1, schedule1 = max_pool_matches_greedy_with_schedule(requests1)
    print(f"Test 1: {requests1}")
    print(f"Maximum rides: {result1}")
    print(f"Schedule: {schedule1}")
    print(f"Expected: 3, Got: {result1}\n")
    
    # Test case 2: All overlapping
    requests2 = [[1,4], [2,5], [3,6]]
    result2 = max_pool_matches_greedy(requests2)
    count2, schedule2 = max_pool_matches_greedy_with_schedule(requests2)
    print(f"Test 2: {requests2}")
    print(f"Maximum rides: {result2}")
    print(f"Schedule: {schedule2}")
    print(f"Expected: 1, Got: {result2}\n")
    
    # Test case 3: No overlapping
    requests3 = [[1,2], [3,4], [5,6], [7,8]]
    result3 = max_pool_matches_greedy(requests3)
    count3, schedule3 = max_pool_matches_greedy_with_schedule(requests3)
    print(f"Test 3: {requests3}")
    print(f"Maximum rides: {result3}")
    print(f"Schedule: {schedule3}")
    print(f"Expected: 4, Got: {result3}\n")
    
    # Test case 4: Edge case - touching intervals
    requests4 = [[1,3], [3,5], [5,7]]
    result4 = max_pool_matches_greedy(requests4)
    count4, schedule4 = max_pool_matches_greedy_with_schedule(requests4)
    print(f"Test 4: {requests4}")
    print(f"Maximum rides: {result4}")
    print(f"Schedule: {schedule4}")
    print(f"Expected: 3, Got: {result4}\n")
    
    # Test case 5: Empty input
    requests5 = []
    result5 = max_pool_matches_greedy(requests5)
    print(f"Test 5: {requests5}")
    print(f"Maximum rides: {result5}")
    print(f"Expected: 0, Got: {result5}\n")

if __name__ == "__main__":
    print("=== Ride Sharing Problem - Greedy Solution ===\n")
    test_greedy_solution()
    
    print("=== Algorithm Explanation ===")
    print("1. Sort intervals by end time (dropoff_time)")
    print("2. Greedily select intervals that don't overlap")
    print("3. This works because choosing the interval that ends earliest")
    print("   leaves the most room for future intervals")
    print("4. Proven to be optimal for unweighted interval scheduling")


