"""
Problem: Minimize Maximum Difference Among p Pairs

Given a 0-indexed integer array nums and an integer p, find p pairs of indices 
such that the maximum difference amongst all pairs is minimized.
No index should appear more than once.

Key Insights and Intuition:
1. **Why sort first?** 
   - If we sort the array, pairing adjacent elements gives smaller differences
   - Any optimal solution can be rearranged to use only "locally optimal" pairs
   
2. **Why try all combinations?**
   - We need exactly p pairs, and each element can be used at most once
   - Different combinations of pairs might yield different maximum differences
   - We need to explore possibilities to find the minimum of these maximums

3. **State space exploration:**
   - At each position, we decide: skip this element, or pair it with a previous one
   - This creates a tree of decisions that we can explore recursively
"""

def minimize_max_difference_brute_force(nums, p):
    """
    Brute Force Approach: Try all possible combinations of p pairs
    
    Time Complexity: O(C(n,2p) * p) - extremely expensive
    Space Complexity: O(p) for recursion stack
    
    This approach explores all ways to choose p pairs from the array.
    """
    if p == 0:
        return 0
    
    nums.sort()  # Sort to make pairing logic clearer
    n = len(nums)
    
    def backtrack(index, pairs_formed, used, current_max_diff):
        # Base case: formed enough pairs
        if pairs_formed == p:
            return current_max_diff
            
        # Base case: not enough elements left to form remaining pairs
        remaining_elements = sum(1 for i in range(index, n) if not used[i])
        remaining_pairs_needed = p - pairs_formed
        if remaining_elements < 2 * remaining_pairs_needed:
            return float('inf')
        
        min_max_diff = float('inf')
        
        # Try pairing current element with any previous unused element
        if index < n and not used[index]:
            for prev_idx in range(index):
                if not used[prev_idx]:
                    # Form a pair between prev_idx and index
                    pair_diff = abs(nums[index] - nums[prev_idx])
                    new_max_diff = max(current_max_diff, pair_diff)
                    
                    # Mark both elements as used
                    used[prev_idx] = used[index] = True
                    
                    # Recurse to next position
                    result = backtrack(index + 1, pairs_formed + 1, used, new_max_diff)
                    min_max_diff = min(min_max_diff, result)
                    
                    # Backtrack
                    used[prev_idx] = used[index] = False
        
        # Try skipping current element
        if index < n:
            result = backtrack(index + 1, pairs_formed, used, current_max_diff)
            min_max_diff = min(min_max_diff, result)
        
        return min_max_diff
    
    used = [False] * n
    return backtrack(0, 0, used, 0)


def minimize_max_difference_dp_approach1(nums, p):
    """
    DP Approach 1: State-based DP with memoization
    
    State: (index, pairs_formed, used_mask) -> minimum maximum difference
    
    Time Complexity: O(n * p * 2^n) - still exponential due to used_mask
    Space Complexity: O(n * p * 2^n)
    
    This is still not optimal but shows the DP transition clearly.
    """
    if p == 0:
        return 0
    
    nums.sort()
    n = len(nums)
    
    from functools import lru_cache
    
    @lru_cache(maxsize=None)
    def dp(index, pairs_formed, used_mask):
        if pairs_formed == p:
            return 0
            
        if index >= n:
            return float('inf')
        
        min_max_diff = float('inf')
        
        # Option 1: Skip current element
        min_max_diff = min(min_max_diff, dp(index + 1, pairs_formed, used_mask))
        
        # Option 2: Pair current element with a previous unused element
        if not (used_mask & (1 << index)):  # Current element not used
            for prev_idx in range(index):
                if not (used_mask & (1 << prev_idx)):  # Previous element not used
                    pair_diff = abs(nums[index] - nums[prev_idx])
                    new_mask = used_mask | (1 << index) | (1 << prev_idx)
                    
                    remaining_result = dp(index + 1, pairs_formed + 1, new_mask)
                    if remaining_result != float('inf'):
                        min_max_diff = min(min_max_diff, max(pair_diff, remaining_result))
        
        return min_max_diff
    
    return dp(0, 0, 0)


def minimize_max_difference_optimized_dp(nums, p):
    """
    Optimized DP Approach: Key insight - only adjacent elements matter after sorting
    
    After sorting, in any optimal solution, we can assume elements are paired
    with adjacent or nearby elements. This drastically reduces the search space.
    
    State: dp[i][j] = minimum maximum difference using first i elements to form j pairs
    
    Time Complexity: O(n^2 * p)
    Space Complexity: O(n * p)
    """
    if p == 0:
        return 0
    
    nums.sort()
    n = len(nums)
    
    # dp[i][j] = minimum maximum difference using elements [0...i-1] to form exactly j pairs
    dp = [[float('inf')] * (p + 1) for _ in range(n + 1)]
    
    # Base case: 0 pairs needed = 0 maximum difference
    for i in range(n + 1):
        dp[i][0] = 0
    
    for i in range(1, n + 1):
        for j in range(1, min(i // 2, p) + 1):  # Can't form more than i//2 pairs with i elements
            # Option 1: Don't use element i-1 (0-indexed: nums[i-1])
            dp[i][j] = dp[i-1][j]
            
            # Option 2: Pair element i-1 with some previous element k
            for k in range(i-1):  # k goes from 0 to i-2
                if j == 1:
                    # First pair - just the difference between these two elements
                    pair_diff = abs(nums[i-1] - nums[k])
                    dp[i][j] = min(dp[i][j], pair_diff)
                else:
                    # Need to check if we can form j-1 pairs with remaining elements
                    # We need to be careful about which elements are available
                    # This approach has complexity but demonstrates the concept
                    pair_diff = abs(nums[i-1] - nums[k])
                    
                    # Find minimum max diff for j-1 pairs excluding elements k and i-1
                    prev_max = dp[k][j-1]  # This is an approximation
                    if prev_max != float('inf'):
                        dp[i][j] = min(dp[i][j], max(pair_diff, prev_max))
    
    return dp[n][p] if dp[n][p] != float('inf') else 0


def minimize_max_difference_greedy_optimal(nums, p):
    """
    Most Efficient Approach: Binary Search + Greedy
    
    Key Insight: If we can form p pairs with max difference ≤ x, 
    then we can also form p pairs with max difference ≤ y where y > x.
    
    This monotonicity allows us to binary search on the answer.
    
    Time Complexity: O(n log n + n log(max_diff))
    Space Complexity: O(1)
    """
    if p == 0:
        return 0
    
    nums.sort()
    n = len(nums)
    
    def can_form_p_pairs_with_max_diff(max_diff):
        """
        Check if we can form at least p pairs with maximum difference ≤ max_diff
        
        WHY WE DON'T CHECK nums[i-1]:
        
        The algorithm processes elements left-to-right with this invariant:
        - When at position i, all elements before i have been "finalized"
        - "Finalized" means: either paired or permanently unpaired
        
        If nums[i-1] is still unpaired when we reach position i, it means:
        1. When we were at position i-1, we checked nums[i-1] vs nums[i]
        2. Since nums[i-1] is still unpaired, they couldn't be paired due to max_diff constraint
        3. So checking backwards now would still fail the same constraint!
        
        Example with nums = [1, 5, 6], max_diff = 3:
        - At i=0: Check nums[0]=1 vs nums[1]=5. Diff = 4 > 3. Can't pair. Move to i=1.
        - At i=1: Check nums[1]=5 vs nums[2]=6. Diff = 1 ≤ 3. Pair them! 
        - We don't need to check nums[1] vs nums[0] again because we already know diff=4 > 3
        
        The greedy "forward-only" approach works because:
        1. We make irrevocable decisions (pair immediately when possible)
        2. If we skip a pairing opportunity, there's no benefit to reconsidering it later
        3. Adjacent elements always give the smallest possible differences in sorted array
        """
        pairs = 0
        i = 0
        while i < n - 1:
            if nums[i + 1] - nums[i] <= max_diff:
                pairs += 1
                i += 2  # Skip both elements as they're now paired
                if pairs >= p:
                    return True
            else:
                i += 1  # nums[i] is now "abandoned" - we'll never reconsider it
        return pairs >= p
    
    # Binary search on the answer
    left, right = 0, nums[-1] - nums[0]
    
    while left < right:
        mid = (left + right) // 2
        if can_form_p_pairs_with_max_diff(mid):
            right = mid
        else:
            left = mid + 1
    
    return left


def demonstrate_why_no_backward_checking():
    """
    Demonstration of why we don't need to check nums[i-1]
    """
    print("=== Why We Don't Check nums[i-1] ===\n")
    
    # Example 1: Forward pairing works optimally
    nums1 = [1, 3, 4, 6, 8]
    max_diff = 3
    print(f"Example 1: nums = {nums1}, max_diff = {max_diff}")
    print("Simulation of algorithm:")
    
    pairs = 0
    i = 0
    n = len(nums1)
    
    while i < n - 1:
        print(f"  At i={i}: Checking nums[{i}]={nums1[i]} vs nums[{i+1}]={nums1[i+1]}")
        if nums1[i + 1] - nums1[i] <= max_diff:
            print(f"    Difference = {nums1[i+1] - nums1[i]} ≤ {max_diff}. PAIR THEM!")
            pairs += 1
            i += 2
        else:
            print(f"    Difference = {nums1[i+1] - nums1[i]} > {max_diff}. Skip nums[{i}]")
            i += 1
    
    print(f"  Total pairs found: {pairs}\n")
    
    # Example 2: Why backward checking is unnecessary
    nums2 = [1, 5, 6]  
    max_diff = 3
    print(f"Example 2: nums = {nums2}, max_diff = {max_diff}")
    print("What if we tried backward checking?")
    
    print(f"  At i=0: nums[0]=1 vs nums[1]=5. Diff = 4 > 3. Can't pair.")
    print(f"  At i=1: nums[1]=5 vs nums[2]=6. Diff = 1 ≤ 3. Could pair.")
    print(f"  But what about nums[1]=5 vs nums[0]=1? Diff = 4 > 3. Still can't pair!")
    print(f"  Conclusion: Backward checking gives the same result.\n")
    
    # Example 3: Greedy choice is optimal
    nums3 = [1, 2, 4, 5]
    max_diff = 2  
    print(f"Example 3: nums = {nums3}, max_diff = {max_diff}")
    print("Greedy approach:")
    print(f"  Pair (1,2) with diff=1, then pair (4,5) with diff=1. Total: 2 pairs")
    print("Alternative approach:")  
    print(f"  Pair (1,4) with diff=3 > 2? NO. Pair (2,4) with diff=2? YES.")
    print(f"  Then (1,5) with diff=4 > 2? NO. Total: 1 pair")
    print(f"  Greedy is better!\n")


def minimize_max_difference_clean_dp(nums, p):
    """
    Clean DP Solution: Focus on adjacent pairs after sorting
    
    Key insight: After sorting, in optimal solution, most pairs will be adjacent
    or very close to each other.
    
    State: dp[i][j] = minimum maximum difference when we've processed first i elements
    and formed exactly j pairs
    
    Transition: At position i, we can:
    1. Skip element i: dp[i+1][j] = dp[i][j]
    2. Pair element i with element i-1: dp[i+1][j+1] = min(dp[i+1][j+1], max(dp[i-1][j], nums[i] - nums[i-1]))
    """
    if p == 0:
        return 0
    
    nums.sort()
    n = len(nums)
    
    # dp[i][j] = minimum maximum difference using first i elements to form j pairs
    INF = float('inf')
    dp = [[INF] * (p + 1) for _ in range(n + 1)]
    
    # Base case
    for i in range(n + 1):
        dp[i][0] = 0
    
    for i in range(2, n + 1):  # Need at least 2 elements to form a pair
        for j in range(1, min(i // 2, p) + 1):
            # Option 1: Don't include element at index i-1
            dp[i][j] = dp[i-1][j]
            
            # Option 2: Pair elements at indices i-2 and i-1 (adjacent pair)
            if dp[i-2][j-1] != INF:
                pair_diff = nums[i-1] - nums[i-2]  # Already sorted, so this is positive
                dp[i][j] = min(dp[i][j], max(dp[i-2][j-1], pair_diff))
    
    return dp[n][p]


# Test cases and examples
if __name__ == "__main__":
    # Show why backward checking isn't needed
    demonstrate_why_no_backward_checking()
    
    print("=== Original Test Cases ===\n")
    # Test case 1
    nums1 = [10, 1, 2, 7, 1, 3]
    p1 = 2
    print(f"Input: nums = {nums1}, p = {p1}")
    print(f"Expected output: 1")
    print(f"Greedy solution: {minimize_max_difference_greedy_optimal(nums1, p1)}")
    print(f"Clean DP solution: {minimize_max_difference_clean_dp(nums1, p1)}")
    print()
    
    # Test case 2
    nums2 = [4, 2, 1, 2]
    p2 = 1
    print(f"Input: nums = {nums2}, p = {p2}")
    print(f"Expected output: 0")
    print(f"Greedy solution: {minimize_max_difference_greedy_optimal(nums2, p2)}")
    print(f"Clean DP solution: {minimize_max_difference_clean_dp(nums2, p2)}")
    print()
    
    # Test case 3
    nums3 = [0, 3, 4, 5]
    p3 = 2
    print(f"Input: nums = {nums3}, p = {p3}")
    print(f"Expected output: 1")
    print(f"Greedy solution: {minimize_max_difference_greedy_optimal(nums3, p3)}")
    print(f"Clean DP solution: {minimize_max_difference_clean_dp(nums3, p3)}")
