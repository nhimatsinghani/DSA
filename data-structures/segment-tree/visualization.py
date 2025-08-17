"""
Segment Tree Visualization

This module provides simple ASCII-based visualization tools to help understand
how segment trees work internally.
"""

from typing import List, Optional
from segment_tree import SumSegmentTree
import math


def visualize_segment_tree(arr: List[int], max_depth: int = 4) -> None:
    """
    Create an ASCII visualization of a segment tree.
    
    Args:
        arr: Input array to visualize
        max_depth: Maximum depth to show (to avoid overwhelming output)
    """
    if not arr:
        print("Empty array - no tree to visualize")
        return
    
    if len(arr) > 16:
        print(f"Array too large ({len(arr)} elements). Showing first 8 elements only.")
        arr = arr[:8]
    
    st = SumSegmentTree(arr)
    tree = st.get_tree_representation()
    
    print(f"Original Array: {arr}")
    print(f"Array Indices:  {list(range(len(arr)))}")
    print()
    
    # Calculate tree properties
    n = len(arr)
    height = math.ceil(math.log2(n)) + 1 if n > 1 else 1
    max_width = 2 ** (height - 1)
    
    print("Segment Tree Visualization:")
    print("(Format: [start,end] value)")
    print()
    
    # Draw tree level by level
    for level in range(min(height, max_depth)):
        nodes_in_level = 2 ** level
        start_index = (2 ** level) - 1
        spacing = max_width // (2 ** level)
        
        line = ""
        for i in range(nodes_in_level):
            node_index = start_index + i
            
            if node_index < len(tree) and (node_index == 0 or tree[node_index] != 0):
                # Calculate the range this node represents
                level_size = n // (2 ** level)
                remainder = n % (2 ** level)
                
                if level == 0:
                    range_str = f"[0,{n-1}]"
                    value = tree[node_index]
                else:
                    # This is a simplified range calculation
                    # In practice, you'd track ranges more precisely
                    range_str = f"[?,?]"
                    value = tree[node_index]
                
                if node_index == 0:  # Root
                    range_str = f"[0,{n-1}]"
                elif level == 1:  # First level children
                    if i == 0:  # Left child
                        range_str = f"[0,{n//2-1}]"
                    else:  # Right child
                        range_str = f"[{n//2},{n-1}]"
                
                node_str = f"{range_str} {value}"
            else:
                node_str = ""
            
            # Add spacing
            if i > 0:
                line += " " * (spacing * 2)
            line += node_str.center(spacing * 2)
        
        print(f"Level {level}: {line}")
        
        if level < min(height, max_depth) - 1:
            print()
    
    if height > max_depth:
        print(f"... (showing only first {max_depth} levels)")
    
    # Show some leaf nodes for clarity
    print(f"\nLeaf values (last level): {arr}")
    print(f"Internal tree array: {tree[:min(20, len(tree))]}")


def trace_query(arr: List[int], left: int, right: int) -> None:
    """
    Trace through a range query step by step.
    
    Args:
        arr: Input array
        left: Left boundary of query
        right: Right boundary of query
    """
    if not arr or left < 0 or right >= len(arr) or left > right:
        print("Invalid query parameters")
        return
    
    print(f"Tracing query sumRange({left}, {right}) on array {arr}")
    print(f"Expected result: {sum(arr[left:right+1])}")
    print()
    
    st = SumSegmentTree(arr)
    
    # This is a simplified trace - in practice you'd need to modify
    # the segment tree to add logging
    class TracingSegmentTree(SumSegmentTree):
        def __init__(self, arr):
            super().__init__(arr)
            self.trace_level = 0
        
        def _query(self, node, start, end, left, right):
            indent = "  " * self.trace_level
            print(f"{indent}Visiting node {node}: range [{start},{end}], tree_value={self.tree[node]}")
            
            # No overlap
            if right < start or end < left:
                print(f"{indent}→ No overlap, returning 0")
                return 0
            
            # Complete overlap
            if left <= start and end <= right:
                print(f"{indent}→ Complete overlap, returning {self.tree[node]}")
                return self.tree[node]
            
            # Partial overlap
            print(f"{indent}→ Partial overlap, querying children")
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2
            
            self.trace_level += 1
            left_result = self._query(left_child, start, mid, left, right)
            right_result = self._query(right_child, mid + 1, end, left, right)
            self.trace_level -= 1
            
            result = left_result + right_result
            print(f"{indent}→ Combining: {left_result} + {right_result} = {result}")
            return result
    
    tracing_st = TracingSegmentTree(arr)
    print("Query trace:")
    result = tracing_st.query(left, right)
    print(f"\nFinal result: {result}")


def trace_update(arr: List[int], index: int, new_value: int) -> None:
    """
    Trace through an update operation step by step.
    
    Args:
        arr: Input array
        index: Index to update
        new_value: New value to set
    """
    if not arr or index < 0 or index >= len(arr):
        print("Invalid update parameters")
        return
    
    print(f"Tracing update({index}, {new_value}) on array {arr}")
    print(f"Changing index {index} from {arr[index]} to {new_value}")
    print()
    
    class TracingSegmentTree(SumSegmentTree):
        def __init__(self, arr):
            super().__init__(arr)
            self.trace_level = 0
        
        def _update(self, node, start, end, index, value):
            indent = "  " * self.trace_level
            print(f"{indent}Visiting node {node}: range [{start},{end}], current_value={self.tree[node]}")
            
            if start == end:
                old_value = self.tree[node]
                self.tree[node] = value
                print(f"{indent}→ Leaf node: updating {old_value} → {value}")
            else:
                mid = (start + end) // 2
                left_child = 2 * node + 1
                right_child = 2 * node + 2
                
                if index <= mid:
                    print(f"{indent}→ Going to left child (index {index} <= mid {mid})")
                    self.trace_level += 1
                    self._update(left_child, start, mid, index, value)
                    self.trace_level -= 1
                else:
                    print(f"{indent}→ Going to right child (index {index} > mid {mid})")
                    self.trace_level += 1
                    self._update(right_child, mid + 1, end, index, value)
                    self.trace_level -= 1
                
                old_value = self.tree[node]
                self.tree[node] = self.tree[left_child] + self.tree[right_child]
                print(f"{indent}→ Updated node: {old_value} → {self.tree[node]} "
                      f"(sum of children: {self.tree[left_child]} + {self.tree[right_child]})")
    
    tracing_st = TracingSegmentTree(arr)
    print("Update trace:")
    tracing_st.update(index, new_value)
    print(f"\nUpdate complete!")


def interactive_demo():
    """Run an interactive segment tree demo."""
    print("🌳 Interactive Segment Tree Demo")
    print("=" * 40)
    
    # Get array from user or use default
    try:
        user_input = input("Enter array elements (space-separated) or press Enter for default [1,3,5,7]: ")
        if user_input.strip():
            arr = [int(x) for x in user_input.split()]
        else:
            arr = [1, 3, 5, 7]
    except ValueError:
        print("Invalid input, using default array [1,3,5,7]")
        arr = [1, 3, 5, 7]
    
    print(f"\nWorking with array: {arr}")
    visualize_segment_tree(arr)
    
    while True:
        print("\nOptions:")
        print("1. Query range sum")
        print("2. Update value")
        print("3. Show tree visualization")
        print("4. Trace a query")
        print("5. Trace an update")
        print("6. Exit")
        
        choice = input("Choose an option (1-6): ").strip()
        
        if choice == '1':
            try:
                left = int(input("Enter left index: "))
                right = int(input("Enter right index: "))
                st = SumSegmentTree(arr)
                result = st.query(left, right)
                expected = sum(arr[left:right+1]) if 0 <= left <= right < len(arr) else 0
                print(f"Sum of range [{left}, {right}]: {result}")
                print(f"Manual calculation: {expected}")
                print("✓ Correct!" if result == expected else "❌ Error!")
            except (ValueError, IndexError):
                print("Invalid input!")
        
        elif choice == '2':
            try:
                index = int(input("Enter index to update: "))
                value = int(input("Enter new value: "))
                if 0 <= index < len(arr):
                    print(f"Updating index {index} from {arr[index]} to {value}")
                    arr[index] = value
                    print(f"New array: {arr}")
                else:
                    print("Index out of bounds!")
            except ValueError:
                print("Invalid input!")
        
        elif choice == '3':
            visualize_segment_tree(arr)
        
        elif choice == '4':
            try:
                left = int(input("Enter left index for trace: "))
                right = int(input("Enter right index for trace: "))
                trace_query(arr, left, right)
            except ValueError:
                print("Invalid input!")
        
        elif choice == '5':
            try:
                index = int(input("Enter index to update for trace: "))
                value = int(input("Enter new value for trace: "))
                trace_update(arr, index, value)
                # Don't actually update the array for tracing
            except ValueError:
                print("Invalid input!")
        
        elif choice == '6':
            print("Thanks for using the segment tree demo! 🌳")
            break
        
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    # Run some examples
    # print("🌳 Segment Tree Visualization Examples\n")
    
    # # Example 1: Small array
    # print("Example 1: Array [1, 3, 5, 7]")
    # visualize_segment_tree([1, 3, 5, 7])
    # print("\n" + "="*50 + "\n")
    
    # # Example 2: Trace a query
    # print("Example 2: Tracing sumRange(1, 3) on [1, 3, 5, 7]")
    # trace_query([1, 3, 5, 7], 1, 3)
    # print("\n" + "="*50 + "\n")
    
    # # Example 3: Trace an update
    # print("Example 3: Tracing update(2, 10) on [1, 3, 5, 7]")
    # trace_update([1, 3, 5, 7], 2, 10)
    # print("\n" + "="*50 + "\n")
    
    # # Example 4: Larger array
    # print("Example 4: Array [1, 2, 3, 4, 5, 6, 7, 8]")
    # visualize_segment_tree([1, 2, 3, 4, 5, 6, 7, 8])
    
    # Uncomment to run interactive demo
    print("\n" + "="*50 + "\n")
    interactive_demo() 