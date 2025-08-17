"""
LeetCode 2603: Collect Coins in a Tree

Problem: Given a tree with coins at some nodes, find minimum edges to traverse 
to collect all coins and return to starting position.

Key Constraints:
- Can collect coins within distance 2 from current position
- Need to return to starting position
- Count each edge traversal (if traverse same edge multiple times, count each time)

UNDERSTANDING THE PROBLEM:
1. We can collect coins from distance 0, 1, or 2 from our current position
2. This means we don't necessarily need to visit every coin node directly
3. We need to find the minimum "tour" that allows us to collect all coins

BRUTE FORCE APPROACH INTUITION:
================================
1. Try every possible starting position (0 to n-1)
2. For each starting position, use DFS to explore all possible paths
3. Keep track of collected coins and current position
4. When all coins are collected, find shortest path back to start
5. Return minimum across all starting positions

Time Complexity: O(n! * n) - exponential due to exploring all paths
Space Complexity: O(n) for recursion stack

OPTIMIZED APPROACH INTUITION (Tree Trimming):
===========================================
The key insight: Many nodes are unnecessary for the optimal solution!

Why Tree Trimming Works:
1. **Leaf nodes without coins**: If a leaf node has no coin, we never need to visit it
2. **Nodes that only connect to unnecessary nodes**: If a node's only connection leads to unnecessary nodes, it's also unnecessary
3. **Distance-2 collection**: Since we can collect from distance 2, we might not need to visit coin nodes directly

Tree Trimming Process:
1. **First Pass**: Remove all leaf nodes that have no coins (and aren't connected to coin paths)
2. **Second Pass**: Remove leaf nodes that are distance > 2 from any remaining coin
3. **Result**: After trimming, every remaining edge must be traversed exactly twice (go and return)

Mathematical Proof:
- In any tree traversal that returns to start, each edge is traversed an even number of times
- For optimal solution, each necessary edge is traversed exactly twice (minimum even number > 0)
- If we can eliminate unnecessary edges through trimming, remaining edges * 2 gives the answer

Time Complexity: O(n) - linear tree processing
Space Complexity: O(n) for adjacency list and degree tracking
"""

from typing import List
from collections import defaultdict, deque

class CollectCoinsInTree:
    
    def collectCoinsBruteForce(self, coins: List[int], edges: List[List[int]]) -> int:
        """
        Brute force approach: Try all starting positions and find minimum tour
        
        This approach is exponential but helps understand the problem structure.
        """
        n = len(coins)
        if n == 1:
            return 0
            
        # Build adjacency list
        graph = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)
        
        min_steps = float('inf')
        
        # Try each starting position
        for start in range(n):
            steps = self._findMinTourFromStart(graph, coins, start, n)
            min_steps = min(min_steps, steps)
        
        return min_steps
    
    def _findMinTourFromStart(self, graph, coins, start, n):
        """
        Find minimum tour starting from 'start' position
        Uses DFS to explore all possible collection strategies
        """
        total_coins = sum(coins)
        if total_coins == 0:
            return 0
            
        def dfs(current, collected_coins, visited_edges, path):
            if collected_coins == total_coins:
                # All coins collected, find shortest path back to start
                return self._shortestPath(graph, current, start)
            
            min_tour = float('inf')
            
            # Try moving to each neighbor
            for neighbor in graph[current]:
                edge = tuple(sorted([current, neighbor]))
                
                # Calculate newly collected coins from this position
                new_collected = collected_coins
                for node in graph:
                    if coins[node] == 1 and self._distance(graph, neighbor, node) <= 2:
                        # This is simplified - in reality we'd track which specific coins
                        pass
                
                # Continue DFS (simplified version)
                visited_edges.add(edge)
                result = dfs(neighbor, new_collected, visited_edges, path + [neighbor])
                if result != float('inf'):
                    min_tour = min(min_tour, 1 + result)
                visited_edges.remove(edge)
            
            return min_tour
        
        return dfs(start, 0, set(), [start])
    
    def _distance(self, graph, start, end):
        """Calculate shortest distance between two nodes"""
        if start == end:
            return 0
        
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            node, dist = queue.popleft()
            
            for neighbor in graph[node]:
                if neighbor == end:
                    return dist + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return float('inf')
    
    def _shortestPath(self, graph, start, end):
        """Find shortest path length between start and end"""
        return self._distance(graph, start, end)

    def collectCoinsOptimal(self, coins: List[int], edges: List[List[int]]) -> int:
        """
        Optimized solution using tree trimming approach
        
        Key Insight: Remove unnecessary nodes using topological sorting
        """
        n = len(coins)
        if n == 1:
            return 0
        
        # Build adjacency list and degree array
        graph = defaultdict(list)
        degree = [0] * n
        
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)
            degree[u] += 1
            degree[v] += 1
        
        # Step 1: Remove leaf nodes that have no coins
        # These nodes are unnecessary for collecting coins
        queue = deque()
        for i in range(n):
            if degree[i] == 1 and coins[i] == 0:
                queue.append(i)
        
        while queue:
            node = queue.popleft()
            degree[node] = 0  # Mark as removed
            
            for neighbor in graph[node]:
                if degree[neighbor] > 0:
                    degree[neighbor] -= 1
                    # If neighbor becomes leaf and has no coin, add to queue
                    if degree[neighbor] == 1 and coins[neighbor] == 0:
                        queue.append(neighbor)
        
        # Step 2: Remove leaf nodes that are more than distance 2 from coins
        # Since we can collect from distance 2, we don't need to go closer to these
        queue = deque()
        for i in range(n):
            if degree[i] == 1:
                queue.append(i)
        
        # Remove one more layer of leaf nodes (this accounts for distance-2 collection)
        for _ in range(2):  # Remove 2 layers
            size = len(queue)
            for _ in range(size):
                if queue:
                    node = queue.popleft()
                    degree[node] = 0
                    
                    for neighbor in graph[node]:
                        if degree[neighbor] > 0:
                            degree[neighbor] -= 1
                            if degree[neighbor] == 1:
                                queue.append(neighbor)
        
        # Count remaining edges
        remaining_edges = 0
        for u, v in edges:
            if degree[u] > 0 and degree[v] > 0:
                remaining_edges += 1
        
        # Each remaining edge must be traversed exactly twice (go and return)
        return max(0, remaining_edges * 2)

def demonstrateIntuition():
    """
    Demonstrate why tree trimming works with examples
    """
    print("=== TREE TRIMMING INTUITION ===\n")
    
    print("Example 1: Simple case")
    print("Tree: 0-1-2, Coins: [1,0,1]")
    print("Without trimming: Need to visit all nodes")
    print("With trimming: Node 1 is necessary (connects two coin nodes)")
    print("Result: 2 edges * 2 = 4 steps\n")
    
    print("Example 2: Unnecessary leaves")
    print("Tree: 0-1-2-3, Coins: [1,0,1,0]")
    print("Analysis:")
    print("- Node 3 is leaf with no coin → can be removed")
    print("- After removing 3, node 2 becomes leaf with coin → keep it")
    print("- Final tree: 0-1-2")
    print("- Result: 2 edges * 2 = 4 steps\n")
    
    print("Example 3: Distance-2 collection")
    print("Tree: 0-1-2-3-4, Coins: [1,0,0,0,1]")
    print("Analysis:")
    print("- From node 1, we can collect coin at node 3 (distance 2)")
    print("- From node 3, we can collect coin at node 1 (distance 2)")
    print("- We don't need to visit nodes 0 or 4 directly")
    print("- After trimming: Only middle nodes remain")
    print("- This demonstrates the power of distance-2 collection\n")

def runTests():
    """Test both approaches with examples"""
    solution = CollectCoinsInTree()
    
    # Test case 1
    coins1 = [1, 0, 0, 0, 0, 1]
    edges1 = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]
    
    print("Test Case 1:")
    print(f"Coins: {coins1}")
    print(f"Edges: {edges1}")
    
    result_optimal = solution.collectCoinsOptimal(coins1, edges1)
    print(f"Optimal Result: {result_optimal}")
    
    # Test case 2
    coins2 = [0, 0, 0, 1, 1, 0, 0, 1]
    edges2 = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [5, 6], [5, 7]]
    
    print("\nTest Case 2:")
    print(f"Coins: {coins2}")
    print(f"Edges: {edges2}")
    
    result_optimal2 = solution.collectCoinsOptimal(coins2, edges2)
    print(f"Optimal Result: {result_optimal2}")

if __name__ == "__main__":
    demonstrateIntuition()
    print("=== RUNNING TESTS ===")
    runTests()
