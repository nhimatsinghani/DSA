"""
Segment Tree Demonstration and Examples

This module provides comprehensive demonstrations of segment tree functionality,
including step-by-step walkthroughs, visualizations, and performance comparisons.
"""

import time
import random
from typing import List, Tuple
try:
    from segment_tree import SegmentTree, SumSegmentTree, MinSegmentTree, MaxSegmentTree
    from num_array import NumArray, NumArrayAlternative
except ImportError:
    # Handle relative imports when running from different directories
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from segment_tree import SegmentTree, SumSegmentTree, MinSegmentTree, MaxSegmentTree
    from num_array import NumArray, NumArrayAlternative


def print_separator(title: str) -> None:
    """Print a formatted separator for demo sections."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def visualize_tree_structure(arr: List[int]) -> None:
    """
    Visualize the segment tree structure for a given array.
    
    Args:
        arr: Input array to visualize
    """
    print(f"Original Array: {arr}")
    print(f"Array indices:  {list(range(len(arr)))}")
    
    # Create segment tree
    st = SumSegmentTree(arr)
    tree = st.get_tree_representation()
    
    print("\nSegment Tree Structure:")
    print("(Format: [range] value)")
    
    # For small arrays, show the tree structure manually
    if len(arr) <= 8:
        n = len(arr)
        print(f"\nLevel 0 (Root):     [0,{n-1}] {tree[0]}")
        
        if n > 1:
            print(f"Level 1:        [0,{n//2-1}] {tree[1]}    [{n//2},{n-1}] {tree[2]}")
        
        if n > 2:
            level = 2
            nodes_in_level = 4
            start_idx = 3
            for i in range(min(nodes_in_level, len(tree) - start_idx)):
                # Calculate range for this node
                node_idx = start_idx + i
                if node_idx < len(tree) and tree[node_idx] != 0:
                    # This is a simplified visualization - in practice, 
                    # you'd need to track the actual ranges
                    print(f"Level {level} node {i}: {tree[node_idx]}")
    
    print(f"\nInternal tree array: {tree[:min(20, len(tree))]}")
    if len(tree) > 20:
        print("... (truncated)")


def step_by_step_walkthrough() -> None:
    """
    Demonstrate step-by-step execution of segment tree operations.
    """
    print_separator("Step-by-Step Walkthrough")
    
    # Example array
    arr = [1, 3, 5, 7, 9, 11]
    print(f"Working with array: {arr}")
    
    # Create NumArray
    num_array = NumArray(arr)
    
    print("\n1. INITIALIZATION")
    print("   - Built segment tree with O(n) time complexity")
    print("   - Tree height: O(log n)")
    print("   - Space used: O(4n) ≈ O(n)")
    
    print("\n2. RANGE SUM QUERIES")
    
    # Query 1: sumRange(1, 4)
    print(f"\n   Query: sumRange(1, 4)")
    print(f"   Range: indices 1 to 4 → elements [{arr[1]}, {arr[2]}, {arr[3]}, {arr[4]}]")
    result = num_array.sumRange(1, 4)
    expected = sum(arr[1:5])
    print(f"   Expected: {arr[1]} + {arr[2]} + {arr[3]} + {arr[4]} = {expected}")
    print(f"   Actual:   {result}")
    print(f"   ✓ Correct: {result == expected}")
    
    # Query 2: sumRange(0, 2)
    print(f"\n   Query: sumRange(0, 2)")
    print(f"   Range: indices 0 to 2 → elements [{arr[0]}, {arr[1]}, {arr[2]}]")
    result2 = num_array.sumRange(0, 2)
    expected2 = sum(arr[0:3])
    print(f"   Expected: {arr[0]} + {arr[1]} + {arr[2]} = {expected2}")
    print(f"   Actual:   {result2}")
    print(f"   ✓ Correct: {result2 == expected2}")
    
    print("\n3. UPDATE OPERATION")
    
    # Update: change index 2 from 5 to 10
    old_val = arr[2]
    new_val = 10
    print(f"\n   Update: change index 2 from {old_val} to {new_val}")
    print(f"   Before: {num_array.get_array()}")
    
    num_array.update(2, new_val)
    updated_arr = num_array.get_array()
    print(f"   After:  {updated_arr}")
    
    print("\n4. QUERIES AFTER UPDATE")
    
    # Query the same ranges after update
    print(f"\n   Query: sumRange(1, 4) after update")
    print(f"   Range: indices 1 to 4 → elements [{updated_arr[1]}, {updated_arr[2]}, {updated_arr[3]}, {updated_arr[4]}]")
    result3 = num_array.sumRange(1, 4)
    expected3 = sum(updated_arr[1:5])
    print(f"   Expected: {updated_arr[1]} + {updated_arr[2]} + {updated_arr[3]} + {updated_arr[4]} = {expected3}")
    print(f"   Actual:   {result3}")
    print(f"   ✓ Correct: {result3 == expected3}")
    
    print(f"\n   Query: sumRange(0, 2) after update")
    result4 = num_array.sumRange(0, 2)
    expected4 = sum(updated_arr[0:3])
    print(f"   Expected: {updated_arr[0]} + {updated_arr[1]} + {updated_arr[2]} = {expected4}")
    print(f"   Actual:   {result4}")
    print(f"   ✓ Correct: {result4 == expected4}")


def demonstrate_different_operations() -> None:
    """
    Demonstrate segment trees with different operations (sum, min, max).
    """
    print_separator("Different Segment Tree Operations")
    
    arr = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"Array: {arr}")
    
    # Sum Segment Tree
    print("\n1. SUM SEGMENT TREE")
    sum_tree = SumSegmentTree(arr)
    print(f"   Sum of range [2, 5]: {sum_tree.query(2, 5)}")  # 4+1+5+9 = 19
    print(f"   Sum of range [0, 3]: {sum_tree.query(0, 3)}")  # 3+1+4+1 = 9
    
    sum_tree.update(4, 10)  # Change 5 to 10
    print(f"   After updating index 4 to 10:")
    print(f"   Sum of range [2, 5]: {sum_tree.query(2, 5)}")  # 4+1+10+9 = 24
    
    # Min Segment Tree
    print("\n2. MIN SEGMENT TREE")
    min_tree = MinSegmentTree(arr)
    print(f"   Min of range [2, 5]: {min_tree.query(2, 5)}")  # min(4,1,5,9) = 1
    print(f"   Min of range [0, 3]: {min_tree.query(0, 3)}")  # min(3,1,4,1) = 1
    
    min_tree.update(3, 0)  # Change second 1 to 0
    print(f"   After updating index 3 to 0:")
    print(f"   Min of range [2, 5]: {min_tree.query(2, 5)}")  # min(4,0,5,9) = 0
    
    # Max Segment Tree
    print("\n3. MAX SEGMENT TREE")
    max_tree = MaxSegmentTree(arr)
    print(f"   Max of range [2, 5]: {max_tree.query(2, 5)}")  # max(4,1,5,9) = 9
    print(f"   Max of range [0, 3]: {max_tree.query(0, 3)}")  # max(3,1,4,1) = 4
    
    max_tree.update(1, 15)  # Change first 1 to 15
    print(f"   After updating index 1 to 15:")
    print(f"   Max of range [0, 3]: {max_tree.query(0, 3)}")  # max(3,15,4,1) = 15


def performance_analysis() -> None:
    """
    Analyze performance of different approaches for range sum queries.
    """
    print_separator("Performance Analysis")
    
    # Test different array sizes
    sizes = [100, 1000, 10000]
    
    for size in sizes:
        print(f"\n--- Array Size: {size} ---")
        
        # Generate random array
        arr = [random.randint(1, 100) for _ in range(size)]
        
        # Generate random operations
        num_ops = min(1000, size)
        operations = []
        for _ in range(num_ops):
            if random.random() < 0.7:  # 70% queries, 30% updates
                left = random.randint(0, size - 1)
                right = random.randint(left, size - 1)
                operations.append(('query', left, right))
            else:
                index = random.randint(0, size - 1)
                value = random.randint(1, 100)
                operations.append(('update', index, value))
        
        print(f"Operations: {len(operations)} ({len([op for op in operations if op[0] == 'query'])} queries, {len([op for op in operations if op[0] == 'update'])} updates)")
        
        # Test Segment Tree approach
        start_time = time.time()
        num_array = NumArray(arr)
        
        for op in operations:
            if op[0] == 'query':
                result = num_array.sumRange(op[1], op[2])
            else:
                num_array.update(op[1], op[2])
        
        st_time = time.time() - start_time
        
        # Test Naive approach (only for smaller sizes)
        if size <= 1000:
            class NaiveNumArray:
                def __init__(self, nums):
                    self.nums = nums[:]
                
                def update(self, index, val):
                    self.nums[index] = val
                
                def sumRange(self, left, right):
                    return sum(self.nums[left:right+1])
            
            start_time = time.time()
            naive_array = NaiveNumArray(arr)
            
            for op in operations:
                if op[0] == 'query':
                    result = naive_array.sumRange(op[1], op[2])
                else:
                    naive_array.update(op[1], op[2])
            
            naive_time = time.time() - start_time
            
            print(f"Segment Tree: {st_time:.6f} seconds")
            print(f"Naive Array:  {naive_time:.6f} seconds")
            print(f"Speedup:      {naive_time / st_time:.2f}x")
        else:
            print(f"Segment Tree: {st_time:.6f} seconds")
            print(f"Naive Array:  (too slow for this size)")


def edge_cases_demonstration() -> None:
    """
    Demonstrate handling of edge cases.
    """
    print_separator("Edge Cases")
    
    print("1. SINGLE ELEMENT ARRAY")
    single = NumArray([42])
    print(f"   Array: [42]")
    print(f"   sumRange(0, 0): {single.sumRange(0, 0)}")  # Should be 42
    single.update(0, 100)
    print(f"   After update(0, 100): {single.sumRange(0, 0)}")  # Should be 100
    
    print("\n2. TWO ELEMENT ARRAY")
    double = NumArray([1, 2])
    print(f"   Array: [1, 2]")
    print(f"   sumRange(0, 1): {double.sumRange(0, 1)}")  # Should be 3
    print(f"   sumRange(0, 0): {double.sumRange(0, 0)}")  # Should be 1
    print(f"   sumRange(1, 1): {double.sumRange(1, 1)}")  # Should be 2
    
    print("\n3. LARGE VALUES")
    large_vals = NumArray([1000000, 2000000, 3000000])
    print(f"   Array: [1000000, 2000000, 3000000]")
    print(f"   sumRange(0, 2): {large_vals.sumRange(0, 2)}")  # Should be 6000000
    
    print("\n4. NEGATIVE VALUES")
    negative = NumArray([-1, -2, 3, -4, 5])
    print(f"   Array: [-1, -2, 3, -4, 5]")
    print(f"   sumRange(0, 4): {negative.sumRange(0, 4)}")  # Should be 1
    print(f"   sumRange(2, 4): {negative.sumRange(2, 4)}")  # Should be 4


def real_world_example() -> None:
    """
    Demonstrate a real-world use case scenario.
    """
    print_separator("Real-World Example: Stock Price Analysis")
    
    # Simulate daily stock prices for a month
    stock_prices = [100, 102, 98, 105, 110, 108, 112, 115, 113, 118,
                   120, 117, 122, 125, 123, 128, 130, 127, 132, 135,
                   133, 138, 140, 137, 142, 145, 143, 148, 150, 147]
    
    print("Stock Price Monitoring System")
    print(f"Daily prices for 30 days: {stock_prices[:10]}... (showing first 10)")
    
    price_tracker = NumArray(stock_prices)
    
    print("\nAnalyzing price trends:")
    
    # Week 1 total
    week1_sum = price_tracker.sumRange(0, 6)
    print(f"Week 1 (days 0-6) total: ${week1_sum}")
    print(f"Week 1 average: ${week1_sum / 7:.2f}")
    
    # Week 2 total
    week2_sum = price_tracker.sumRange(7, 13)
    print(f"Week 2 (days 7-13) total: ${week2_sum}")
    print(f"Week 2 average: ${week2_sum / 7:.2f}")
    
    # Price correction simulation
    print(f"\nPrice correction on day 10: ${stock_prices[10]} → $115")
    price_tracker.update(10, 115)
    
    # Recalculate week 2 after correction
    week2_corrected = price_tracker.sumRange(7, 13)
    print(f"Week 2 after correction: ${week2_corrected}")
    print(f"Week 2 corrected average: ${week2_corrected / 7:.2f}")
    
    # Quarterly analysis (first 21 days ≈ 3 weeks)
    quarter_total = price_tracker.sumRange(0, 20)
    print(f"\nFirst 21 days total: ${quarter_total}")
    print(f"First 21 days average: ${quarter_total / 21:.2f}")


def comparison_with_alternatives() -> None:
    """
    Compare segment trees with alternative data structures.
    """
    print_separator("Comparison with Alternative Data Structures")
    
    print("For the Range Sum Query with Updates problem:\n")
    
    approaches = [
        ("Naive Array", "O(1)", "O(n)", "O(1)", "Simple but slow queries"),
        ("Prefix Sum", "O(n)", "O(1)", "O(n)", "Fast queries but slow updates"),
        ("Segment Tree", "O(log n)", "O(log n)", "O(n)", "Balanced performance"),
        ("Fenwick Tree", "O(log n)", "O(log n)", "O(n)", "More memory efficient"),
        ("Square Root Decomp", "O(√n)", "O(√n)", "O(n)", "Simpler implementation")
    ]
    
    print(f"{'Approach':<20} {'Update':<10} {'Query':<10} {'Space':<8} {'Notes'}")
    print("-" * 80)
    
    for approach, update_time, query_time, space, notes in approaches:
        print(f"{approach:<20} {update_time:<10} {query_time:<10} {space:<8} {notes}")
    
    print(f"\n{'Recommendation:':<15} Use Segment Tree for balanced performance")
    print(f"{'Alternative:':<15} Use Fenwick Tree if memory is critical")
    print(f"{'Simple case:':<15} Use Prefix Sum if no updates needed")


# Main demonstration function
def run_complete_demo() -> None:
    """Run the complete segment tree demonstration."""
    print("🌳 SEGMENT TREE COMPREHENSIVE DEMONSTRATION 🌳")
    
    # Run all demo sections
    step_by_step_walkthrough()
    
    demonstrate_different_operations()
    
    # Visualize a small example
    print_separator("Tree Structure Visualization")
    visualize_tree_structure([1, 3, 5, 7])
    
    edge_cases_demonstration()
    
    real_world_example()
    
    comparison_with_alternatives()
    
    performance_analysis()
    
    print_separator("Demo Complete")
    print("✅ All demonstrations completed successfully!")
    print("\nKey takeaways:")
    print("• Segment Trees provide O(log n) for both updates and queries")
    print("• They're versatile and work for sum, min, max, and other operations")
    print("• Space complexity is O(n) with good practical performance")
    print("• Ideal for problems requiring frequent range queries AND updates")


if __name__ == "__main__":
    run_complete_demo() 