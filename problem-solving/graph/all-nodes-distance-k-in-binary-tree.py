from typing import List, Optional
from collections import defaultdict, deque


# Definition for a binary tree node
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution : 
    def allNodesAtDistanceKInBinaryK(self, root : TreeNode, node: TreeNode, distance : int)-> List:

        #COnvert tree into a graph in the form of adjacency list
        # Find the node in the graph
        # Do a BFS of the graph starting from the node and store all elements at level 'distance'




        #build adjacency list from tree
        adj_list = defaultdict(list)

        self.traverse_tree(root, None, adj_list)

        print("Adj List : ", adj_list)

        q = deque()
        visited = set()

        q.append((node.val, 0))
        res = []
        while q:

            level_len = len(q)
            id, level = q.popleft()

            if level == distance :
                res.append(id)
            
            if level > distance:
                break

            visited.add(id)

            for neighbor in adj_list[id]:

                if neighbor not in visited:
                    q.append((neighbor, level+1))

        return res
    

    def traverse_tree(self, node:TreeNode, parent:TreeNode, adj_list:dict):

        if not node : 
            return
        
        if parent : 
            adj_list[node.val].append(parent.val)
        if node.right:
            adj_list[node.val].append(node.right.val)
        if node.left:
            adj_list[node.val].append(node.left.val)
        
        self.traverse_tree(node.right, node, adj_list)
        self.traverse_tree(node.left, node, adj_list)



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



def test():
    sol = Solution()

    input = [3,5,1,6,2,0,8, None, None, 7,4]
    root = build_tree_from_list(input)
    res = sol.allNodesAtDistanceKInBinaryK(root, root.left, 2)
    print("Expected : [7,4,1]. Actual : ", res)
    assert 7 in res and 4 in res and 1 in res


    input = [3,5,1,6,2,0,8, None, None, 7,4, 10,15,17,18]
    root = build_tree_from_list(input)
    res = sol.allNodesAtDistanceKInBinaryK(root, root.right, 2)
    print("Expected : [5, 10,15,17,18]. Actual : ", res)
    assert 5 in res and 10 in res and 15 in res and 17 in res and 18 in res



if __name__ == "__main__":
    test()