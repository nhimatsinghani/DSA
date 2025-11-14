# Dijkstra's Algorithm Summary

## Purpose

Find the shortest path from a source vertex to all other vertices in a weighted graph with non-negative edge weights.

## Key Components

1. **Distance Array**: Tracks the shortest known distance from source to each vertex
2. **Priority Queue (Min-Heap)**: Stores vertices to be processed, ordered by distance
3. **Visited Set**: Tracks processed vertices to avoid reprocessing

## Algorithm Steps

### 1. Initialization

- Set distance to source vertex = 0
- Set distance to all other vertices = ∞ (infinity)
- Add source vertex to priority queue with distance 0
- Mark all vertices as unvisited

### 2. Main Loop (while priority queue is not empty)

- **Extract minimum**: Remove vertex with smallest distance from priority queue
- **Skip if visited**: If vertex already processed, continue to next iteration
- **Mark as visited**: Mark current vertex as visited/processed

### 3. Relaxation Process (for each neighbor of current vertex)

- Calculate new distance: `current_distance + edge_weight`
- **If new distance < known distance**:
  - Update distance array with new shorter distance
  - Add neighbor to priority queue with new distance

### 4. Termination

- Algorithm ends when priority queue is empty
- Distance array contains shortest distances from source to all reachable vertices

## Key Properties

- **Time Complexity**: O((V + E) log V) with binary heap
- **Space Complexity**: O(V)
- **Greedy Approach**: Always selects the unvisited vertex with minimum distance
- **Optimal Substructure**: Shortest path to any vertex contains shortest paths to intermediate vertices

## Python Implementation

```python
import heapq
from collections import defaultdict
from typing import Dict, List, Tuple

def dijkstra(graph: Dict[int, List[Tuple[int, int]]], source: int) -> Dict[int, int]:
    """
    Dijkstra's algorithm implementation

    Args:
        graph: Adjacency list representation {vertex: [(neighbor, weight), ...]}
        source: Starting vertex

    Returns:
        Dictionary mapping each vertex to its shortest distance from source
    """
    # Initialize distances
    distances = defaultdict(lambda: float('inf'))
    distances[source] = 0

    # Priority queue: (distance, vertex)
    pq = [(0, source)]
    visited = set()

    while pq:
        # Extract vertex with minimum distance
        current_dist, current_vertex = heapq.heappop(pq)

        # Skip if already visited
        if current_vertex in visited:
            continue

        # Mark as visited
        visited.add(current_vertex)

        # Relaxation: check all neighbors
        for neighbor, weight in graph[current_vertex]:
            if neighbor not in visited:
                new_distance = current_dist + weight

                # If found shorter path, update distance
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor))

    return dict(distances)

def dijkstra_with_path(graph: Dict[int, List[Tuple[int, int]]], source: int) -> Tuple[Dict[int, int], Dict[int, int]]:
    """
    Dijkstra's algorithm with path reconstruction

    Returns:
        Tuple of (distances, previous_vertices) for path reconstruction
    """
    distances = defaultdict(lambda: float('inf'))
    distances[source] = 0
    previous = {}

    pq = [(0, source)]
    visited = set()

    while pq:
        current_dist, current_vertex = heapq.heappop(pq)

        if current_vertex in visited:
            continue

        visited.add(current_vertex)

        for neighbor, weight in graph[current_vertex]:
            if neighbor not in visited:
                new_distance = current_dist + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (new_distance, neighbor))

    return dict(distances), previous

def reconstruct_path(previous: Dict[int, int], source: int, target: int) -> List[int]:
    """
    Reconstruct shortest path from source to target
    """
    if target not in previous and target != source:
        return []  # No path exists

    path = []
    current = target

    while current is not None:
        path.append(current)
        current = previous.get(current)

    path.reverse()
    return path if path[0] == source else []

# Example Usage
def example_usage():
    """
    Example graph:
    A(0) --1-- B(1) --4-- C(2)
    |          |
    2          1
    |          |
    D(3) --3-- E(4)
    """

    # Create graph as adjacency list
    graph = {
        0: [(1, 1), (3, 2)],    # A -> B(1), D(2)
        1: [(0, 1), (2, 4), (4, 1)],  # B -> A(1), C(4), E(1)
        2: [(1, 4)],            # C -> B(4)
        3: [(0, 2), (4, 3)],    # D -> A(2), E(3)
        4: [(1, 1), (3, 3)]     # E -> B(1), D(3)
    }

    source = 0  # Start from vertex A

    # Find shortest distances
    distances = dijkstra(graph, source)
    print("Shortest distances from vertex 0:")
    for vertex, distance in sorted(distances.items()):
        print(f"  To vertex {vertex}: {distance}")

    # Find shortest distances with paths
    distances, previous = dijkstra_with_path(graph, source)

    print("\nShortest paths:")
    for target in sorted(distances.keys()):
        if target != source:
            path = reconstruct_path(previous, source, target)
            print(f"  Path to {target}: {' -> '.join(map(str, path))} (distance: {distances[target]})")

if __name__ == "__main__":
    example_usage()
```

## Example Walkthrough

Given the graph:

```
A(0) --1-- B(1) --4-- C(2)
|          |
2          1
|          |
D(3) --3-- E(4)
```

**Starting from vertex A (0):**

1. **Initial state**: distances = {0: 0, others: ∞}, pq = [(0, 0)]
2. **Process A(0)**: Visit neighbors B(1) and D(3)
   - Update B: distance = 1, pq = [(1, 1), (2, 3)]
   - Update D: distance = 2
3. **Process B(1)**: Visit neighbors C(2) and E(4)
   - Update C: distance = 5, pq = [(2, 3), (2, 4), (5, 2)]
   - Update E: distance = 2
4. **Process D(3)**: Visit neighbor E(4)
   - E already has distance 2, no update needed
5. **Process E(4)**: All neighbors already processed
6. **Process C(2)**: No unvisited neighbors

**Final distances**: A(0)→0, B(1)→1, C(2)→5, D(3)→2, E(4)→2

## Common Applications

- **GPS Navigation**: Finding shortest routes
- **Network Routing**: Internet packet routing protocols
- **Social Networks**: Finding degrees of separation
- **Game Development**: AI pathfinding
- **Resource Allocation**: Optimal resource distribution

## Limitations

- **Non-negative weights only**: Cannot handle negative edge weights
- **Dense graphs**: Performance degrades with many edges
- **Memory usage**: Requires storing all vertices in memory
