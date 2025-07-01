from typing import Optional, List
from collections import deque


class Node:
    """
    Definition for a Node with parent pointer.
    """
    def __init__(self, val=0, left=None, right=None, parent=None):
        self.val = val
        self.left = left
        self.right = right
        self.parent = parent


class Solution:
    def lowestCommonAncestor(self, p: 'Node', q: 'Node') -> 'Node':
        """
        Given two nodes of a binary tree p and q, return their lowest common ancestor (LCA).
        
        According to the definition of LCA on Wikipedia: "The lowest common ancestor of two nodes p and q 
        in a tree T is the lowest node that has both p and q as descendants 
        (where we allow a node to be a descendant of itself)."
        
        Each node has a reference to its parent node.
        
        Args:
            p: Node - First node
            q: Node - Second node
            
        Returns:
            Node - The lowest common ancestor of p and q
        """
        # TODO: Implement this method
        pass


def build_tree_with_parents(vals: List[Optional[int]]) -> Optional[Node]:
    """Helper function to build a tree with parent pointers from a list representation."""
    if not vals or vals[0] is None:
        return None
    
    root = Node(vals[0])
    queue = deque([root])
    i = 1
    
    while queue and i < len(vals):
        node = queue.popleft()
        
        # Left child
        if i < len(vals) and vals[i] is not None:
            node.left = Node(vals[i], parent=node)
            queue.append(node.left)
        i += 1
        
        # Right child
        if i < len(vals) and vals[i] is not None:
            node.right = Node(vals[i], parent=node)
            queue.append(node.right)
        i += 1
    
    return root


def find_node_by_value(root: Optional[Node], val: int) -> Optional[Node]:
    """Helper function to find a node by its value in the tree."""
    if not root:
        return None
    
    if root.val == val:
        return root
    
    left_result = find_node_by_value(root.left, val)
    if left_result:
        return left_result
    
    return find_node_by_value(root.right, val)


def get_path_to_root(node: Node) -> List[int]:
    """Helper function to get path from node to root for debugging."""
    path = []
    current = node
    while current:
        path.append(current.val)
        current = current.parent
    return path


def test_lca_with_parent_pointers():
    """Test cases for LCA with parent pointers."""
    solution = Solution()
    
    # Test Case 1: Example from image - p=4, q=8, expected=3
    print("Test Case 1:")
    tree1 = build_tree_with_parents([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    p1 = find_node_by_value(tree1, 4)
    q1 = find_node_by_value(tree1, 8)
    result1 = solution.lowestCommonAncestor(p1, q1)
    expected1_val = 3
    print(f"Input: Tree with p=4, q=8")
    print(f"Expected LCA value: {expected1_val}")
    print(f"Got LCA value:      {result1.val if result1 else None}")
    print(f"Path from p to root: {get_path_to_root(p1)}")
    print(f"Path from q to root: {get_path_to_root(q1)}")
    print(f"Passed: {result1.val == expected1_val if result1 else False}")
    print()
    
    # Test Case 2: p=6, q=4, expected=5
    print("Test Case 2:")
    p2 = find_node_by_value(tree1, 6)
    q2 = find_node_by_value(tree1, 4)
    result2 = solution.lowestCommonAncestor(p2, q2)
    expected2_val = 5
    print(f"Input: Tree with p=6, q=4")
    print(f"Expected LCA value: {expected2_val}")
    print(f"Got LCA value:      {result2.val if result2 else None}")
    print(f"Path from p to root: {get_path_to_root(p2)}")
    print(f"Path from q to root: {get_path_to_root(q2)}")
    print(f"Passed: {result2.val == expected2_val if result2 else False}")
    print()
    
    # Test Case 3: One node is ancestor of another - p=5, q=4, expected=5
    print("Test Case 3:")
    p3 = find_node_by_value(tree1, 5)
    q3 = find_node_by_value(tree1, 4)
    result3 = solution.lowestCommonAncestor(p3, q3)
    expected3_val = 5
    print(f"Input: Tree with p=5, q=4 (p is ancestor of q)")
    print(f"Expected LCA value: {expected3_val}")
    print(f"Got LCA value:      {result3.val if result3 else None}")
    print(f"Path from p to root: {get_path_to_root(p3)}")
    print(f"Path from q to root: {get_path_to_root(q3)}")
    print(f"Passed: {result3.val == expected3_val if result3 else False}")
    print()
    
    # Test Case 4: Simple tree - p=2, q=3, expected=1
    print("Test Case 4:")
    tree4 = build_tree_with_parents([1, 2, 3])
    p4 = find_node_by_value(tree4, 2)
    q4 = find_node_by_value(tree4, 3)
    result4 = solution.lowestCommonAncestor(p4, q4)
    expected4_val = 1
    print(f"Input: Simple tree [1,2,3] with p=2, q=3")
    print(f"Expected LCA value: {expected4_val}")
    print(f"Got LCA value:      {result4.val if result4 else None}")
    print(f"Path from p to root: {get_path_to_root(p4)}")
    print(f"Path from q to root: {get_path_to_root(q4)}")
    print(f"Passed: {result4.val == expected4_val if result4 else False}")
    print()
    
    # Test Case 5: Same node - p=1, q=1, expected=1
    print("Test Case 5:")
    tree5 = build_tree_with_parents([1, 2, 3])
    p5 = find_node_by_value(tree5, 1)
    q5 = find_node_by_value(tree5, 1)
    result5 = solution.lowestCommonAncestor(p5, q5)
    expected5_val = 1
    print(f"Input: Tree with p=1, q=1 (same node)")
    print(f"Expected LCA value: {expected5_val}")
    print(f"Got LCA value:      {result5.val if result5 else None}")
    print(f"Passed: {result5.val == expected5_val if result5 else False}")
    print()
    
    # Test Case 6: Deep tree - test with deeper nodes
    print("Test Case 6:")
    tree6 = build_tree_with_parents([1, 2, 3, 4, 5, 6, 7, 8, 9])
    p6 = find_node_by_value(tree6, 8)
    q6 = find_node_by_value(tree6, 9)
    result6 = solution.lowestCommonAncestor(p6, q6)
    expected6_val = 4
    print(f"Input: Deep tree with p=8, q=9")
    print(f"Expected LCA value: {expected6_val}")
    print(f"Got LCA value:      {result6.val if result6 else None}")
    print(f"Path from p to root: {get_path_to_root(p6)}")
    print(f"Path from q to root: {get_path_to_root(q6)}")
    print(f"Passed: {result6.val == expected6_val if result6 else False}")
    print()


if __name__ == "__main__":
    print("Lowest Common Ancestor III (with Parent Pointers) Test Cases")
    print("=" * 65)
    test_lca_with_parent_pointers()
    
    print("\nTree visualization for Test Case 1:")
    print("        3")
    print("       / \\")
    print("      5   1")
    print("     / \\ / \\")
    print("    6  2 0  8")
    print("      / \\")
    print("     7   4")
    print("\nProblem Understanding:")
    print("- Each node has a parent pointer")
    print("- LCA is the lowest node that has both p and q as descendants")
    print("- A node can be a descendant of itself")
    print("- Use parent pointers to traverse up from both nodes")
    print("\nApproaches:")
    print("1. Two-pointer technique: Move both nodes up until they meet")
    print("2. Set approach: Store path from one node to root, check other path")
    print("3. Depth calculation: Align depths first, then move both up together")

