from typing import List, Set, Tuple
from collections import deque


class Solution:
    def largestIsland(self, grid: List[List[int]]) -> int:
        """
        You are given an n x n binary matrix grid. You are allowed to change at most one 0 to be 1.
        Return the size of the largest island in grid after applying this operation.
        An island is a 4-directionally connected group of 1s.
        
        Args:
            grid: List[List[int]] - n x n binary matrix
            
        Returns:
            int - Size of the largest island after changing at most one 0 to 1
        """
        # TODO: Implement this method
        pass


def test_make_largest_island():
    """Test cases for make largest island."""
    solution = Solution()
    
    # Test Case 1: Example 1 from problem
    print("Test Case 1:")
    grid1 = [[1, 0], [0, 1]]
    result1 = solution.largestIsland(grid1)
    expected1 = 3
    print(f"Input: {grid1}")
    print(f"Expected: {expected1}")
    print(f"Got:      {result1}")
    print(f"Explanation: Change one 0 to 1 and connect two 1s, island area = 3")
    print(f"Passed:   {result1 == expected1}")
    print()
    
    # Test Case 2: Example 2 from problem
    print("Test Case 2:")
    grid2 = [[1, 1], [1, 0]]
    result2 = solution.largestIsland(grid2)
    expected2 = 4
    print(f"Input: {grid2}")
    print(f"Expected: {expected2}")
    print(f"Got:      {result2}")
    print(f"Explanation: Change the 0 to 1 and make the island bigger, area = 4")
    print(f"Passed:   {result2 == expected2}")
    print()
    
    # Test Case 3: Example 3 from problem
    print("Test Case 3:")
    grid3 = [[1, 1], [1, 1]]
    result3 = solution.largestIsland(grid3)
    expected3 = 4
    print(f"Input: {grid3}")
    print(f"Expected: {expected3}")
    print(f"Got:      {result3}")
    print(f"Explanation: Can't change any 0 to 1, only one island with area = 4")
    print(f"Passed:   {result3 == expected3}")
    print()
    
    # Test Case 4: All zeros
    print("Test Case 4:")
    grid4 = [[0, 0], [0, 0]]
    result4 = solution.largestIsland(grid4)
    expected4 = 1
    print(f"Input: {grid4}")
    print(f"Expected: {expected4}")
    print(f"Got:      {result4}")
    print(f"Explanation: Change any 0 to 1, resulting island area = 1")
    print(f"Passed:   {result4 == expected4}")
    print()
    
    # Test Case 5: Single cell with 1
    print("Test Case 5:")
    grid5 = [[1]]
    result5 = solution.largestIsland(grid5)
    expected5 = 1
    print(f"Input: {grid5}")
    print(f"Expected: {expected5}")
    print(f"Got:      {result5}")
    print(f"Explanation: No 0 to change, island area = 1")
    print(f"Passed:   {result5 == expected5}")
    print()
    
    # Test Case 6: Single cell with 0
    print("Test Case 6:")
    grid6 = [[0]]
    result6 = solution.largestIsland(grid6)
    expected6 = 1
    print(f"Input: {grid6}")
    print(f"Expected: {expected6}")
    print(f"Got:      {result6}")
    print(f"Explanation: Change 0 to 1, island area = 1")
    print(f"Passed:   {result6 == expected6}")
    print()
    
    # Test Case 7: Larger grid with multiple islands
    print("Test Case 7:")
    grid7 = [
        [1, 0, 0, 1, 0],
        [1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0]
    ]
    result7 = solution.largestIsland(grid7)
    expected7 = 6  # Connect the two size-2 islands and the size-2 island at bottom
    print(f"Input: 5x5 grid with multiple islands")
    print("Grid visualization:")
    for row in grid7:
        print(f"  {row}")
    print(f"Expected: {expected7}")
    print(f"Got:      {result7}")
    print(f"Explanation: Connect multiple islands by changing strategic 0 to 1")
    print(f"Passed:   {result7 == expected7}")
    print()
    
    # Test Case 8: No zeros to change
    print("Test Case 8:")
    grid8 = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]
    result8 = solution.largestIsland(grid8)
    expected8 = 9
    print(f"Input: 3x3 grid all 1s")
    print("Grid visualization:")
    for row in grid8:
        print(f"  {row}")
    print(f"Expected: {expected8}")
    print(f"Got:      {result8}")
    print(f"Explanation: No 0 to change, return size of existing island")
    print(f"Passed:   {result8 == expected8}")
    print()
    
    # Test Case 9: Complex case with optimal placement
    print("Test Case 9:")
    grid9 = [
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0]
    ]
    result9 = solution.largestIsland(grid9)
    expected9 = 9  # Connect two size-4 islands
    print(f"Input: 5x5 grid with two separate size-4 islands")
    print("Grid visualization:")
    for row in grid9:
        print(f"  {row}")
    print(f"Expected: {expected9}")
    print(f"Got:      {result9}")
    print(f"Explanation: Change middle 0 to connect two size-4 islands: 4 + 4 + 1 = 9")
    print(f"Passed:   {result9 == expected9}")
    print()


if __name__ == "__main__":
    print("Make Largest Island Test Cases")
    print("=" * 40)
    test_make_largest_island()
    
    print("\nProblem Understanding:")
    print("- Given n x n binary matrix")
    print("- Can change at most one 0 to 1")
    print("- Return size of largest possible island")
    print("- Island = 4-directionally connected group of 1s")
    print("\nApproach:")
    print("1. Find all existing islands and assign unique IDs")
    print("2. Store each island's size")
    print("3. For each 0, calculate potential island size if changed to 1:")
    print("   - Check all 4 neighbors")
    print("   - Sum sizes of distinct neighboring islands")
    print("   - Add 1 for the changed cell")
    print("4. Return maximum possible island size")
    print("\nEdge Cases:")
    print("- All 1s (no 0 to change)")
    print("- All 0s (change any one)")
    print("- Single cell")
    print("- No improvement possible")
    
    print("\nVisualization for Example 1:")
    print("Original: [[1,0],    Change (0,1) or (1,0):  [[1,1],")
    print("           [0,1]]                             [0,1]]")
    print("Islands: 2 separate  →  Connected island size 3")
