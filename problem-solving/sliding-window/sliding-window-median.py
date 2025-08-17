import heapq
from collections import defaultdict
from typing import List

class Solution:
    def medianSlidingWindow(self, nums: List[int], k: int) -> List[float]:
        """
        Optimal Solution using Two Heaps with Lazy Deletion
        
        Time Complexity: O(n log k) where n = len(nums)
        Space Complexity: O(k)
        
        Approach:
        1. Use max_heap for smaller half and min_heap for larger half
        2. Maintain invariant: max_heap size == min_heap size or max_heap size == min_heap size + 1
        3. Use lazy deletion to handle element removal from sliding window
        4. Balance heaps after each addition/removal
        """
        max_heap = []  # stores smaller half (negated values for max behavior)
        min_heap = []  # stores larger half
        
        # Counter for lazy deletion - tracks elements to be removed
        to_remove = defaultdict(int)
        
        # Track actual valid sizes (excluding lazy deleted elements)
        max_heap_size = 0
        min_heap_size = 0
        
        result = []
        
        def clean_heap_tops():
            """Remove lazy deleted elements from heap tops"""
            nonlocal max_heap_size, min_heap_size
            
            # Clean max_heap top
            while max_heap and to_remove[-max_heap[0]] > 0:
                removed = -heapq.heappop(max_heap)
                to_remove[removed] -= 1
                max_heap_size -= 1
            
            # Clean min_heap top
            while min_heap and to_remove[min_heap[0]] > 0:
                removed = heapq.heappop(min_heap)
                to_remove[removed] -= 1
                min_heap_size -= 1
        
        def add_number(num):
            """Add number to appropriate heap"""
            nonlocal max_heap_size, min_heap_size
            
            # Decide which heap to add to
            if max_heap_size == 0 or num <= -max_heap[0]:
                heapq.heappush(max_heap, -num)
                max_heap_size += 1
            else:
                heapq.heappush(min_heap, num)
                min_heap_size += 1
        
        def remove_number(num):
            """Mark number for lazy deletion"""
            nonlocal max_heap_size, min_heap_size
            
            to_remove[num] += 1
            
            # Update virtual sizes
            if max_heap and num <= -max_heap[0]:
                max_heap_size -= 1
            else:
                min_heap_size -= 1
        
        def balance_heaps():
            """Balance the two heaps to maintain median property"""
            nonlocal max_heap_size, min_heap_size
            
            # Clean tops first
            clean_heap_tops()
            
            # Rebalance if needed
            if max_heap_size > min_heap_size + 1:
                # Move from max_heap to min_heap
                val = -heapq.heappop(max_heap)
                heapq.heappush(min_heap, val)
                max_heap_size -= 1
                min_heap_size += 1
            elif min_heap_size > max_heap_size:
                # Move from min_heap to max_heap
                val = heapq.heappop(min_heap)
                heapq.heappush(max_heap, -val)
                min_heap_size -= 1
                max_heap_size += 1
        
        def get_median():
            """Get median from balanced heaps"""
            clean_heap_tops()  # Ensure tops are clean
            
            if k % 2 == 1:
                return float(-max_heap[0])
            else:
                return (-max_heap[0] + min_heap[0]) / 2.0
        
        # Process sliding window
        for i in range(len(nums)):
            # Add current number
            add_number(nums[i])
            
            # Remove element going out of window
            if i >= k:
                remove_number(nums[i - k])
            
            # Balance heaps
            balance_heaps()
            
            # Add median to result when window is complete
            if i >= k - 1:
                result.append(get_median())
        
        return result


def test_solution():
    """Test the sliding window median solution"""
    solution = Solution()
    
    print("=== Sliding Window Median - Two Heaps Solution ===\n")
    
    # Test case 1
    nums1 = [1, 3, -1, -3, 5, 3, 6, 7]
    k1 = 3
    result1 = solution.medianSlidingWindow(nums1, k1)
    print(f"Test 1:")
    print(f"Input: nums = {nums1}, k = {k1}")
    print(f"Output: {result1}")
    print(f"Expected: [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]")
    print(f"Correct: {result1 == [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]}\n")
    
    # Test case 2
    nums2 = [1, 2, 3, 4]
    k2 = 4
    result2 = solution.medianSlidingWindow(nums2, k2)
    print(f"Test 2:")
    print(f"Input: nums = {nums2}, k = {k2}")
    print(f"Output: {result2}")
    print(f"Expected: [2.5]")
    print(f"Correct: {result2 == [2.5]}\n")
    
    # Test case 3: Single element window
    nums3 = [1, 4, 2, 3]
    k3 = 1
    result3 = solution.medianSlidingWindow(nums3, k3)
    print(f"Test 3:")
    print(f"Input: nums = {nums3}, k = {k3}")
    print(f"Output: {result3}")
    print(f"Expected: [1.0, 4.0, 2.0, 3.0]")
    print(f"Correct: {result3 == [1.0, 4.0, 2.0, 3.0]}\n")
    
    # Test case 4: Even window size
    nums4 = [1, 2, 3, 4, 5, 6]
    k4 = 2
    result4 = solution.medianSlidingWindow(nums4, k4)
    print(f"Test 4:")
    print(f"Input: nums = {nums4}, k = {k4}")
    print(f"Output: {result4}")
    print(f"Expected: [1.5, 2.5, 3.5, 4.5, 5.5]")
    print(f"Correct: {result4 == [1.5, 2.5, 3.5, 4.5, 5.5]}\n")


if __name__ == "__main__":
    test_solution()
    
    print("=== Algorithm Explanation ===")
    print("""
    Two Heaps Approach with Lazy Deletion:
    
    1. Data Structures:
       - max_heap: Stores smaller half of current window (using negated values)
       - min_heap: Stores larger half of current window
       - to_remove: HashMap for lazy deletion tracking
    
    2. Invariants:
       - All elements in max_heap ≤ all elements in min_heap
       - |max_heap| == |min_heap| or |max_heap| == |min_heap| + 1
    
    3. Operations:
       - Add: O(log k) - insert into appropriate heap
       - Remove: O(1) amortized - lazy deletion with cleanup
       - Balance: O(log k) - maintain heap size invariants
       - Get Median: O(1) - from heap tops
    
    4. Time Complexity: O(n log k)
       - Each element is added and removed once
       - Each heap operation takes O(log k)
    
    5. Space Complexity: O(k)
       - Heaps store at most k elements
       - Lazy deletion map stores at most k elements
    
    This approach achieves the same time complexity as SortedList
    but uses fundamental data structures (heaps) instead of
    advanced balanced tree structures.
    """)
