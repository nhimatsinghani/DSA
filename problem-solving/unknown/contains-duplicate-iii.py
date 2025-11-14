"""
Contains Duplicate III - LeetCode Problem Analysis
================================================

Problem Statement:
Given an integer array nums and two integers indexDiff and valueDiff, return true if there are 
two distinct indices i and j in the array such that:
1. abs(i - j) <= indexDiff
2. abs(nums[i] - nums[j]) <= valueDiff

Example:
Input: nums = [1,2,3,1], indexDiff = 3, valueDiff = 0
Output: true (indices 0 and 3 have values 1,1 with diff=0)

Input: nums = [1,5,9,1,5,9], indexDiff = 2, valueDiff = 3  
Output: false (no valid pairs within constraints)
"""

# ========================================
# SOLUTION 1: BRUTE FORCE - O(n^2)
# ========================================

class SolutionBruteForce:
    """
    Intuition: Check every pair of elements to see if they satisfy both conditions.
    Time: O(n^2), Space: O(1)
    """
    def containsNearbyAlmostDuplicate(self, nums: list[int], indexDiff: int, valueDiff: int) -> bool:
        if valueDiff < 0:
            return False
            
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                # Check index difference constraint
                if abs(i - j) > indexDiff:
                    break  # No point checking further for this i
                
                # Check value difference constraint
                if abs(nums[i] - nums[j]) <= valueDiff:
                    return True
        
        return False

# ========================================
# SOLUTION 2: SLIDING WINDOW WITH SORTING - O(n * k * log k)
# ========================================

from bisect import bisect_left
import bisect

class SolutionSlidingWindow:
    """
    Intuition: Maintain a sliding window of size indexDiff+1 and use binary search
    to find if any element in the window is within valueDiff of current element.
    
    Time: O(n * k * log k) where k = indexDiff
    Space: O(k)
    """
    def containsNearbyAlmostDuplicate(self, nums: list[int], indexDiff: int, valueDiff: int) -> bool:
        if valueDiff < 0:
            return False
            
        window = []
        
        for i, num in enumerate(nums):
            # Binary search for the range [num - valueDiff, num + valueDiff]
            left_bound = num - valueDiff
            right_bound = num + valueDiff
            
            # Find the position where left_bound would be inserted
            pos = bisect_left(window, left_bound)
            
            # Check if any element in the valid range exists
            if pos < len(window) and window[pos] <= right_bound:
                return True
            
            # Add current number to the window (maintain sorted order)
            bisect.insort(window, num)
            
            # Remove elements outside the indexDiff range
            if i >= indexDiff:
                window.remove(nums[i - indexDiff])
        
        return False

# ========================================
# SOLUTION 3: BALANCED BST (TreeSet) - O(n log k)  
# ========================================

# Note: This would use a TreeSet/SortedList, but we'll skip for now to avoid dependencies
# The idea is to maintain a self-balancing BST for efficient range queries

# ========================================
# SOLUTION 4: BUCKET SORT - O(n) OPTIMAL!
# ========================================

class Solution:
    """
    🎯 THE OPTIMAL BUCKET SORT SOLUTION 🎯
    
    INTUITION BREAKDOWN:
    ===================
    
    The key insight is to use "buckets" to group numbers that are close in value.
    
    1. BUCKET SIZE CHOICE:
       - We set bucket_size = valueDiff + 1
       - This ensures that ANY two numbers in the SAME bucket will have 
         difference ≤ valueDiff
       - Why? If both numbers are in bucket k, their values are in range 
         [k * bucket_size, (k+1) * bucket_size - 1]
       - Max difference = (k+1) * bucket_size - 1 - k * bucket_size = bucket_size - 1 = valueDiff
    
    2. BUCKET NUMBER CALCULATION:
       - For a number 'num', its bucket = num // bucket_size
       - This handles negative numbers correctly due to Python's floor division
    
    3. THREE CASES TO CHECK:
       a) SAME BUCKET: If bucket n already exists → immediate return True
          (guaranteed difference ≤ valueDiff)
       
       b) ADJACENT LEFT BUCKET (n-1): Check if |num - bucket[n-1]| ≤ valueDiff
          We only need: num - bucket[n-1] ≤ valueDiff (since num ≥ bucket[n-1])
       
       c) ADJACENT RIGHT BUCKET (n+1): Check if |bucket[n+1] - num| ≤ valueDiff  
          We only need: bucket[n+1] - num ≤ valueDiff (since bucket[n+1] ≥ num)
    
    4. SLIDING WINDOW MAINTENANCE:
       - Add current number to its bucket
       - Remove numbers outside indexDiff range to maintain window constraint
    
    WHY ONLY CHECK ADJACENT BUCKETS?
    ================================
    - If two numbers are in buckets that differ by 2 or more, their minimum 
      difference is 2 * bucket_size = 2 * (valueDiff + 1) > valueDiff
    - So we only need to check current bucket and immediate neighbors!
    
    Time: O(n), Space: O(min(n, indexDiff))
    """
    def containsNearbyAlmostDuplicate(self, nums: list[int], indexDiff: int, valueDiff: int) -> bool:
        if valueDiff < 0:
            return False
        
        buckets = {}
        bucket_size = valueDiff + 1  # Key insight: bucket size = valueDiff + 1
        
        for i, num in enumerate(nums):
            bucket_id = num // bucket_size
            
            # Case 1: Same bucket (guaranteed ≤ valueDiff difference)
            if bucket_id in buckets:
                return True
            
            # Case 2: Left adjacent bucket
            if bucket_id - 1 in buckets and num - buckets[bucket_id - 1] <= valueDiff:
                return True
            
            # Case 3: Right adjacent bucket  
            if bucket_id + 1 in buckets and buckets[bucket_id + 1] - num <= valueDiff:
                return True
            
            # Add current number to its bucket
            buckets[bucket_id] = num
            
            # Remove element outside indexDiff range (sliding window)
            if i >= indexDiff:
                old_bucket = nums[i - indexDiff] // bucket_size
                del buckets[old_bucket]
        
        return False

# ========================================
# VISUAL EXAMPLE OF BUCKET SORT APPROACH
# ========================================

def visualize_buckets(nums, valueDiff):
    """
    Helper function to visualize how numbers are distributed into buckets.
    """
    bucket_size = valueDiff + 1
    print(f"Numbers: {nums}")
    print(f"valueDiff: {valueDiff}, bucket_size: {bucket_size}")
    print("Bucket assignments:")
    
    for i, num in enumerate(nums):
        bucket_id = num // bucket_size
        print(f"  nums[{i}] = {num} → bucket {bucket_id}")
    print()

# ========================================
# DEMONSTRATION: DIFFERENT ARRAY ORDERINGS
# ========================================

def demonstrate_array_orderings():
    """
    Demonstrate that sliding window works regardless of input array ordering.
    """
    print("=" * 60)
    print("TESTING DIFFERENT ARRAY ORDERINGS")
    print("=" * 60)
    
    # Same elements, different orderings
    ascending = [1, 3, 5, 7, 9]
    descending = [9, 7, 5, 3, 1] 
    random_order = [5, 1, 9, 3, 7]
    
    indexDiff, valueDiff = 4, 2  # Allow any pair within value diff 2
    
    solution = SolutionSlidingWindow()
    
    test_cases = [
        ("Ascending", ascending),
        ("Descending", descending), 
        ("Random", random_order)
    ]
    
    for name, nums in test_cases:
        print(f"\n{name} order: {nums}")
        result = solution.containsNearbyAlmostDuplicate(nums, indexDiff, valueDiff)
        print(f"Result: {result}")
        
        # Let's trace through the internal window state
        print("Internal window evolution:")
        trace_sliding_window(nums, indexDiff, valueDiff)

def trace_sliding_window(nums, indexDiff, valueDiff):
    """
    Trace the internal state of the sliding window algorithm.
    """
    if valueDiff < 0:
        return
        
    window = []
    
    for i, num in enumerate(nums):
        left_bound = num - valueDiff
        right_bound = num + valueDiff
        
        print(f"  Step {i}: Processing num={num}")
        print(f"    Current window: {window}")
        print(f"    Looking for range [{left_bound}, {right_bound}]")
        
        # Check for match
        if window:
            pos = bisect_left(window, left_bound)
            if pos < len(window) and window[pos] <= right_bound:
                print(f"    ✅ MATCH FOUND: window[{pos}] = {window[pos]}")
                return
            else:
                print(f"    No match in current window")
        
        # Add current number (maintain sorted order)
        bisect.insort(window, num)
        print(f"    After adding {num}: {window}")
        
        # Remove element outside indexDiff range
        if i >= indexDiff:
            old_num = nums[i - indexDiff]
            window.remove(old_num)
            print(f"    Removed {old_num} (outside indexDiff): {window}")
        
        print()

# Example usage:
if __name__ == "__main__":
    # First run the ordering demonstration
    demonstrate_array_orderings()
    
    print("\n" + "="*60)
    print("ORIGINAL TEST CASES")  
    print("="*60)
    
    # Original test cases
    test_cases = [
        ([1, 2, 3, 1], 3, 0),      # Expected: True
        ([1, 5, 9, 1, 5, 9], 2, 3), # Expected: False  
        ([1, 2, 1], 1, 1),         # Expected: True
        ([1, 2], 0, 1),            # Expected: False
        ([-1, -1], 1, 0),          # Expected: True
    ]
    
    solutions = [
        ("Brute Force", SolutionBruteForce()),
        ("Sliding Window", SolutionSlidingWindow()),
        ("Bucket Sort", Solution())
    ]
    
    for nums, indexDiff, valueDiff in test_cases:
        print(f"\nTest: nums={nums}, indexDiff={indexDiff}, valueDiff={valueDiff}")
        visualize_buckets(nums, valueDiff)
        
        for name, solution in solutions:
            result = solution.containsNearbyAlmostDuplicate(nums, indexDiff, valueDiff)
            print(f"{name:15}: {result}")

# ========================================
# COMPLEXITY ANALYSIS SUMMARY
# ========================================
"""
Solution Comparison:
===================
1. Brute Force:      Time O(n²),        Space O(1)
2. Sliding Window:   Time O(n·k·log k), Space O(k)  
3. TreeSet:          Time O(n·log k),   Space O(k)
4. Bucket Sort:      Time O(n),         Space O(k)

where k = min(indexDiff, n)

The bucket sort approach is optimal because:
- It reduces the problem to constant-time lookups per element
- It only needs to check 3 buckets maximum (current + 2 adjacent)
- It maintains the sliding window constraint efficiently
"""
