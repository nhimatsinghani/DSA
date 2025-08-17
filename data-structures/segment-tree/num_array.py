"""
NumArray Implementation using Segment Tree

This module implements the NumArray class for the LeetCode problem:
"Range Sum Query - Mutable" using a segment tree data structure.

Problem Statement:
Given an integer array nums, handle multiple queries of the following types:
1. Update the value of an element in nums.
2. Calculate the sum of the elements of nums between indices left and right inclusive.

Time Complexity:
- Initialization: O(n)
- Update: O(log n)
- Sum Range Query: O(log n)

Space Complexity: O(n)
"""

from typing import List
try:
    from .segment_tree import SumSegmentTree
except ImportError:
    # Handle relative imports when running from different directories
    from segment_tree import SumSegmentTree


class NumArray:
    """
    Implementation of NumArray using Segment Tree for efficient range sum queries
    and point updates.
    
    This is the optimal solution for the "Range Sum Query - Mutable" problem,
    providing O(log n) time complexity for both updates and queries.
    """
    
    def __init__(self, nums: List[int]):
        """
        Initialize the NumArray with the given array.
        
        Args:
            nums: List of integers to initialize the data structure
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        self.nums = nums[:]  # Keep a copy of the original array for reference
        self.segment_tree = SumSegmentTree(nums)
    
    def update(self, index: int, val: int) -> None:
        """
        Update nums[index] to be val.
        
        Args:
            index: Index to update (0-based)
            val: New value to set at the index
            
        Time Complexity: O(log n)
        Space Complexity: O(1) auxiliary space, O(log n) recursion stack
        """
        if 0 <= index < len(self.nums):
            self.nums[index] = val  # Update our reference array
            self.segment_tree.update(index, val)  # Update the segment tree
    
    def sumRange(self, left: int, right: int) -> int:
        """
        Return the sum of elements between indices left and right inclusive.
        
        Args:
            left: Left boundary of the range (inclusive)
            right: Right boundary of the range (inclusive)
            
        Returns:
            Sum of elements in the range [left, right]
            
        Time Complexity: O(log n)
        Space Complexity: O(1) auxiliary space, O(log n) recursion stack
        """
        return self.segment_tree.query(left, right)
    
    def get_array(self) -> List[int]:
        """
        Get the current state of the array.
        
        Returns:
            Current array after all updates
            
        Time Complexity: O(1)
        """
        return self.nums[:]
    
    def __str__(self) -> str:
        """String representation of the NumArray."""
        return f"NumArray({self.nums})"
    
    def __repr__(self) -> str:
        """Detailed representation of the NumArray."""
        return self.__str__()


class NumArrayAlternative:
    """
    Alternative implementation with embedded segment tree logic.
    
    This version doesn't rely on the separate SumSegmentTree class
    and implements the segment tree logic directly within the NumArray class.
    """
    
    def __init__(self, nums: List[int]):
        """Initialize with embedded segment tree."""
        self.n = len(nums)
        self.nums = nums[:]
        
        # Initialize segment tree array
        self.tree = [0] * (4 * self.n) if self.n > 0 else []
        
        # Build the segment tree
        if self.n > 0:
            self._build(nums, 0, 0, self.n - 1)
    
    def _build(self, arr: List[int], node: int, start: int, end: int) -> None:
        """Build the segment tree recursively."""
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2
            
            self._build(arr, left_child, start, mid)
            self._build(arr, right_child, mid + 1, end)
            
            self.tree[node] = self.tree[left_child] + self.tree[right_child]
    
    def update(self, index: int, val: int) -> None:
        """Update value at index."""
        if 0 <= index < self.n:
            self.nums[index] = val
            self._update(0, 0, self.n - 1, index, val)
    
    def _update(self, node: int, start: int, end: int, index: int, val: int) -> None:
        """Update segment tree recursively."""
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2
            
            if index <= mid:
                self._update(left_child, start, mid, index, val)
            else:
                self._update(right_child, mid + 1, end, index, val)
            
            self.tree[node] = self.tree[left_child] + self.tree[right_child]
    
    def sumRange(self, left: int, right: int) -> int:
        """Query sum in range [left, right]."""
        if self.n == 0 or left < 0 or right >= self.n or left > right:
            return 0
        return self._query(0, 0, self.n - 1, left, right)
    
    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        """Query segment tree recursively."""
        # No overlap
        if right < start or end < left:
            return 0
        
        # Complete overlap
        if left <= start and end <= right:
            return self.tree[node]
        
        # Partial overlap
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2
        
        left_sum = self._query(left_child, start, mid, left, right)
        right_sum = self._query(right_child, mid + 1, end, left, right)
        
        return left_sum + right_sum


def compare_approaches(nums: List[int], operations: List[tuple]) -> None:
    """
    Compare different approaches for the NumArray problem.
    
    Args:
        nums: Initial array
        operations: List of ('update', index, val) or ('query', left, right) operations
    """
    import time
    
    print("=== Approach Comparison ===")
    print(f"Initial array: {nums}")
    print(f"Number of operations: {len(operations)}")
    
    # Approach 1: Segment Tree (Our solution)
    start_time = time.time()
    num_array_st = NumArray(nums)
    
    for op in operations:
        if op[0] == 'update':
            num_array_st.update(op[1], op[2])
        elif op[0] == 'query':
            result = num_array_st.sumRange(op[1], op[2])
    
    st_time = time.time() - start_time
    
    # Approach 2: Naive approach (for comparison)
    class NumArrayNaive:
        def __init__(self, nums):
            self.nums = nums[:]
        
        def update(self, index, val):
            self.nums[index] = val
        
        def sumRange(self, left, right):
            return sum(self.nums[left:right+1])
    
    start_time = time.time()
    num_array_naive = NumArrayNaive(nums)
    
    for op in operations:
        if op[0] == 'update':
            num_array_naive.update(op[1], op[2])
        elif op[0] == 'query':
            result = num_array_naive.sumRange(op[1], op[2])
    
    naive_time = time.time() - start_time
    
    print(f"Segment Tree time: {st_time:.6f} seconds")
    print(f"Naive approach time: {naive_time:.6f} seconds")
    print(f"Speedup: {naive_time / st_time:.2f}x" if st_time > 0 else "N/A")


# Example usage and testing
if __name__ == "__main__":
    # Example from the problem statement
    print("=== NumArray Example ===")
    
    # Initialize
    nums = [1, 3, 5]
    num_array = NumArray(nums)
    print(f"Initialized NumArray with: {nums}")
    
    # Query operations
    print(f"sumRange(0, 2) = {num_array.sumRange(0, 2)}")  # Should return 9 (1+3+5)
    
    # Update operation
    num_array.update(1, 2)  # Update index 1 to value 2
    print(f"After update(1, 2): {num_array.get_array()}")
    
    # Query after update
    print(f"sumRange(0, 2) = {num_array.sumRange(0, 2)}")  # Should return 8 (1+2+5)
    
    # More complex example
    print("\n=== Complex Example ===")
    large_nums = list(range(1, 11))  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    num_array2 = NumArray(large_nums)
    print(f"Array: {large_nums}")
    
    print(f"Sum[2, 7] = {num_array2.sumRange(2, 7)}")  # 3+4+5+6+7+8 = 33
    print(f"Sum[0, 4] = {num_array2.sumRange(0, 4)}")  # 1+2+3+4+5 = 15
    
    # Multiple updates
    num_array2.update(5, 100)  # Change 6 to 100
    num_array2.update(2, 0)    # Change 3 to 0
    
    print(f"After updates: {num_array2.get_array()}")
    print(f"Sum[2, 7] = {num_array2.sumRange(2, 7)}")  # 0+4+5+100+7+8 = 124
    
    # Performance comparison
    print("\n=== Performance Test ===")
    test_nums = list(range(1000))
    test_operations = [('query', i, i+10) for i in range(0, 990, 10)]
    test_operations += [('update', i, i*2) for i in range(0, 1000, 50)]
    
    compare_approaches(test_nums, test_operations) 