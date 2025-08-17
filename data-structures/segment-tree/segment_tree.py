"""
Generic Segment Tree Implementation

This module provides a flexible segment tree implementation that can handle
various types of range queries (sum, min, max, etc.) and point updates.
"""

from typing import List, Callable, Any, Union


class SegmentTree:
    """
    A generic segment tree implementation for range queries and point updates.
    
    The segment tree can be customized with different aggregation functions
    (sum, min, max, etc.) and identity values.
    """
    
    def __init__(self, arr: List[Union[int, float]], 
                 operation: Callable[[Any, Any], Any] = lambda a, b: a + b,
                 identity: Any = 0):
        """
        Initialize the segment tree.
        
        Args:
            arr: Input array to build the segment tree from
            operation: Binary operation for combining values (default: addition)
            identity: Identity element for the operation (default: 0 for sum)
        
        Examples:
            # Sum segment tree
            st = SegmentTree([1, 2, 3, 4])
            
            # Min segment tree
            st = SegmentTree([3, 1, 4, 2], min, float('inf'))
            
            # Max segment tree
            st = SegmentTree([3, 1, 4, 2], max, float('-inf'))
        """
        self.n = len(arr)
        self.operation = operation
        self.identity = identity
        
        # We need at most 4*n nodes for the segment tree
        self.tree = [identity] * (4 * self.n)
        
        # Build the tree if array is not empty
        if self.n > 0:
            self._build(arr, 0, 0, self.n - 1)
    
    def _build(self, arr: List[Union[int, float]], node: int, start: int, end: int) -> None:
        """
        Recursively build the segment tree.
        
        Args:
            arr: Original array
            node: Current node index in the tree
            start: Start index of the range this node represents
            end: End index of the range this node represents
        """
        if start == end:
            # Leaf node - store the array element
            self.tree[node] = arr[start]
        else:
            # Internal node - build children first
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2
            
            # Recursively build left and right subtrees
            self._build(arr, left_child, start, mid)
            self._build(arr, right_child, mid + 1, end)
            
            # Current node value is the operation of its children
            self.tree[node] = self.operation(self.tree[left_child], self.tree[right_child])
    
    def update(self, index: int, value: Union[int, float]) -> None:
        """
        Update the value at the given index.
        
        Args:
            index: Index to update (0-based)
            value: New value
            
        Time Complexity: O(log n)
        """
        if 0 <= index < self.n:
            self._update(0, 0, self.n - 1, index, value)
    
    def _update(self, node: int, start: int, end: int, index: int, value: Union[int, float]) -> None:
        """
        Recursively update the segment tree.
        
        Args:
            node: Current node index
            start: Start of the range this node represents
            end: End of the range this node represents
            index: Index to update
            value: New value
        """
        if start == end:
            # Leaf node - update the value
            self.tree[node] = value
        else:
            # Internal node - update appropriate child
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2
            
            if index <= mid:
                self._update(left_child, start, mid, index, value)
            else:
                self._update(right_child, mid + 1, end, index, value)
            
            # Update current node with the operation of its children
            self.tree[node] = self.operation(self.tree[left_child], self.tree[right_child])
    
    def query(self, left: int, right: int) -> Union[int, float]:
        """
        Query the range [left, right] (inclusive).
        
        Args:
            left: Left boundary of the query range
            right: Right boundary of the query range
            
        Returns:
            Result of the operation over the range [left, right]
            
        Time Complexity: O(log n)
        """
        if left < 0 or right >= self.n or left > right:
            return self.identity
        
        return self._query(0, 0, self.n - 1, left, right)
    
    def _query(self, node: int, start: int, end: int, left: int, right: int) -> Union[int, float]:
        """
        Recursively query the segment tree.
        
        Args:
            node: Current node index
            start: Start of the range this node represents
            end: End of the range this node represents
            left: Left boundary of the query range
            right: Right boundary of the query range
            
        Returns:
            Result of the operation over the queried range
        """
        # No overlap
        if right < start or end < left:
            return self.identity
        
        # Complete overlap
        if left <= start and end <= right:
            return self.tree[node]
        
        # Partial overlap - query both children
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2
        
        left_result = self._query(left_child, start, mid, left, right)
        right_result = self._query(right_child, mid + 1, end, left, right)
        
        return self.operation(left_result, right_result)
    
    def get_tree_representation(self) -> List[Union[int, float]]:
        """
        Get the internal tree representation for debugging.
        
        Returns:
            List representing the internal tree structure
        """
        return self.tree[:4 * self.n] if self.n > 0 else []
    
    def __str__(self) -> str:
        """String representation of the segment tree."""
        if self.n == 0:
            return "Empty SegmentTree"
        
        return f"SegmentTree(size={self.n}, tree={self.get_tree_representation()[:10]}{'...' if self.n > 10 else ''})"
    
    def __repr__(self) -> str:
        """Detailed representation of the segment tree."""
        return self.__str__()


class SumSegmentTree(SegmentTree):
    """Specialized segment tree for range sum queries."""
    
    def __init__(self, arr: List[Union[int, float]]):
        super().__init__(arr, lambda a, b: a + b, 0)


class MinSegmentTree(SegmentTree):
    """Specialized segment tree for range minimum queries."""
    
    def __init__(self, arr: List[Union[int, float]]):
        super().__init__(arr, min, float('inf'))


class MaxSegmentTree(SegmentTree):
    """Specialized segment tree for range maximum queries."""
    
    def __init__(self, arr: List[Union[int, float]]):
        super().__init__(arr, max, float('-inf'))


# Example usage and demonstrations
if __name__ == "__main__":
    # Example 1: Sum Segment Tree
    print("=== Sum Segment Tree Example ===")
    arr = [1, 3, 5, 7, 9, 11]
    sum_tree = SumSegmentTree(arr)
    
    print(f"Original array: {arr}")
    print(f"Sum of range [1, 4]: {sum_tree.query(1, 4)}")  # Should be 3+5+7+9 = 24
    print(f"Sum of range [0, 2]: {sum_tree.query(0, 2)}")  # Should be 1+3+5 = 9
    
    # Update index 2 from 5 to 10
    sum_tree.update(2, 10)
    print(f"After updating index 2 to 10:")
    print(f"Sum of range [1, 4]: {sum_tree.query(1, 4)}")  # Should be 3+10+7+9 = 29
    print(f"Sum of range [0, 2]: {sum_tree.query(0, 2)}")  # Should be 1+3+10 = 14
    
    # Example 2: Min Segment Tree
    print("\n=== Min Segment Tree Example ===")
    min_tree = MinSegmentTree([3, 1, 4, 2, 5])
    print(f"Min of range [1, 3]: {min_tree.query(1, 3)}")  # Should be min(1, 4, 2) = 1
    
    # Example 3: Max Segment Tree
    print("\n=== Max Segment Tree Example ===")
    max_tree = MaxSegmentTree([3, 1, 4, 2, 5])
    print(f"Max of range [1, 4]: {max_tree.query(1, 4)}")  # Should be max(1, 4, 2, 5) = 5 