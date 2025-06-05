from typing import List, Optional
from collections import defaultdict, deque


# Definition for a binary tree node
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def verticalOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        """
        Given the root of a binary tree, return the vertical order traversal of its nodes' values.
        (i.e., from top to bottom, column by column).
        
        If two nodes are in the same row and column, the order should be from left to right.
        
        Args:
            root: TreeNode - The root of the binary tree
            
        Returns:
            List[List[int]] - The vertical order traversal
        """
        result : List[List[int]] = []

        if not root:
            return result
        queue = deque([(root, 0)])
        vertical_order = defaultdict(list)
        left,right = 0,0
        while queue:
            node, hd = queue.popleft()
            left = min(hd,left)
            right = max(right, hd)

            vertical_order[hd].append(node.val)

            if node.left:
                queue.append((node.left, hd-1))
            
            if node.right:
                queue.append((node.right, hd+1))
            
        for column in range(left,right+1):
            
            result.append(vertical_order[column])

        return result    
        


        


def build_tree_from_list(vals: List[Optional[int]]) -> Optional[TreeNode]:
    """Helper function to build a tree from a list representation."""
    if not vals or vals[0] is None:
        return None
    
    root = TreeNode(vals[0])
    queue = deque([root])
    i = 1
    
    while queue and i < len(vals):
        node = queue.popleft()
        
        # Left child
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        
        # Right child
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    
    return root


def test_vertical_order_traversal():
    """Test cases for vertical order traversal."""
    solution = Solution()
    
    # Test Case 1: Basic tree
    print("Test Case 1:")
    tree1 = build_tree_from_list([3, 9, 20, None, None, 15, 7])
    result1 = solution.verticalOrder(tree1)
    expected1 = [[9], [3, 15], [20], [7]]
    print(f"Input: [3, 9, 20, None, None, 15, 7]")
    print(f"Expected: {expected1}")
    print(f"Got:      {result1}")
    print(f"Passed:   {result1 == expected1}")
    print()
    
    # Test Case 2: More complex tree
    print("Test Case 2:")
    tree2 = build_tree_from_list([3, 9, 8, 4, 0, 1, 7])
    result2 = solution.verticalOrder(tree2)
    expected2 = [[4], [9], [3, 0, 1], [8], [7]]
    print(f"Input: [3, 9, 8, 4, 0, 1, 7]")
    print(f"Expected: {expected2}")
    print(f"Got:      {result2}")
    print(f"Passed:   {result2 == expected2}")
    print()
    
    # Test Case 3: Empty tree
    print("Test Case 3:")
    tree3 = None
    result3 = solution.verticalOrder(tree3)
    expected3 = []
    print(f"Input: None")
    print(f"Expected: {expected3}")
    print(f"Got:      {result3}")
    print(f"Passed:   {result3 == expected3}")
    print()
    
    # Test Case 4: Single node
    print("Test Case 4:")
    tree4 = build_tree_from_list([1])
    result4 = solution.verticalOrder(tree4)
    expected4 = [[1]]
    print(f"Input: [1]")
    print(f"Expected: {expected4}")
    print(f"Got:      {result4}")
    print(f"Passed:   {result4 == expected4}")
    print()
    
    # Test Case 5: Left-skewed tree
    print("Test Case 5:")
    tree5 = build_tree_from_list([1, 2, None, 3, None, None, None])
    result5 = solution.verticalOrder(tree5)
    expected5 = [[3], [2], [1]]
    print(f"Input: [1, 2, None, 3, None]")
    print(f"Expected: {expected5}")
    print(f"Got:      {result5}")
    print(f"Passed:   {result5 == expected5}")
    print()
    
    # Test Case 6: Right-skewed tree
    print("Test Case 6:")
    tree6 = build_tree_from_list([1, None, 2, None, None, None, 3])
    result6 = solution.verticalOrder(tree6)
    expected6 = [[1], [2], [3]]
    print(f"Input: [1, None, 2, None, 3]")
    print(f"Expected: {expected6}")
    print(f"Got:      {result6}")
    print(f"Passed:   {result6 == expected6}")
    print()


if __name__ == "__main__":
    print("Vertical Order Traversal Test Cases")
    print("=" * 40)
    test_vertical_order_traversal()
    
    print("\nTree visualization for Test Case 1:")
    print("       3")
    print("      / \\")
    print("     9   20")
    print("        /  \\")
    print("       15   7")
    print("\nVertical columns:")
    print("Column -2: [9]")
    print("Column -1: [3, 15]")
    print("Column  0: [20]")
    print("Column  1: [7]")
    print("\nResult: [[9], [3, 15], [20], [7]]")
