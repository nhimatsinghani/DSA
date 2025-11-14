"""
Popular Content Tracker - Part B: Heap-based Optimization

This implementation uses a max heap to efficiently find the most popular content
while maintaining O(1) increase/decrease operations and O(log n) getMostPopular.

Key Optimizations:
1. Max heap (simulated with negative values) for O(log n) max finding
2. Lazy deletion approach to handle decrease operations efficiently
3. Cleanup of stale entries during getMostPopular to maintain heap integrity

Time Complexity:
- increasePopularity: O(log n) - heap push operation
- decreasePopularity: O(1) - lazy deletion, just update counter
- getMostPopular: O(log n) amortized - cleanup stale entries + heap operations

Space Complexity: O(k + s) where k is unique content IDs and s is stale entries
"""

import heapq
from typing import Dict, Optional

class PopularContentTrackerHeap:
    def __init__(self):
        """
        Initialize the heap-based content tracker.
        
        popularity_map: Dictionary mapping content_id -> current_popularity_count
        max_heap: Max heap storing (-popularity, content_id) tuples
        version_map: Tracks version numbers to implement lazy deletion
        """
        self.popularity_map: Dict[int, int] = {}
        self.max_heap = []  # Min heap with negative values to simulate max heap
        self.version_map: Dict[int, int] = {}  # content_id -> version_number
    
    def increasePopularity(self, content_id: int) -> None:
        """
        Increase the popularity of the given content by 1.
        
        Args:
            content_id (int): Positive integer representing content ID
            
        Time Complexity: O(log n) due to heap push
        """
        if content_id <= 0:
            raise ValueError("Content ID must be a positive integer")
        
        # Update popularity count
        self.popularity_map[content_id] = self.popularity_map.get(content_id, 0) + 1
        current_popularity = self.popularity_map[content_id]
        
        # Increment version to invalidate old heap entries
        self.version_map[content_id] = self.version_map.get(content_id, 0) + 1
        current_version = self.version_map[content_id]
        
        # Push new entry to heap (negative popularity for max heap simulation)
        heapq.heappush(self.max_heap, (-current_popularity, current_version, content_id))
    
    def decreasePopularity(self, content_id: int) -> None:
        """
        Decrease the popularity of the given content by 1.
        Uses lazy deletion - just updates the popularity map and version.
        
        Args:
            content_id (int): Positive integer representing content ID
            
        Time Complexity: O(1) due to lazy deletion approach
        """
        if content_id <= 0:
            raise ValueError("Content ID must be a positive integer")
        
        if content_id in self.popularity_map:
            self.popularity_map[content_id] -= 1
            
            # Remove content if popularity becomes 0 or negative
            if self.popularity_map[content_id] <= 0:
                del self.popularity_map[content_id]
                # Keep version_map entry to invalidate old heap entries
            else:
                # Increment version to invalidate old heap entries
                self.version_map[content_id] = self.version_map.get(content_id, 0) + 1
                current_popularity = self.popularity_map[content_id]
                current_version = self.version_map[content_id]
                
                # Add updated entry to heap
                heapq.heappush(self.max_heap, (-current_popularity, current_version, content_id))
    
    def getMostPopular(self) -> int:
        """
        Return the content ID with the highest popularity.
        Cleans up stale entries from the heap top during the process.
        
        Returns:
            int: Content ID with highest popularity, or -1 if none exists
            
        Time Complexity: O(log n) amortized - stale entry cleanup is amortized
        """
        # Clean up stale entries from the top of the heap
        while self.max_heap:
            neg_popularity, version, content_id = self.max_heap[0]
            popularity = -neg_popularity
            
            # Check if this entry is stale
            current_version = self.version_map.get(content_id, 0)
            current_popularity = self.popularity_map.get(content_id, 0)
            
            # Entry is stale if:
            # 1. Version doesn't match (newer entry exists)
            # 2. Content no longer exists in popularity_map
            # 3. Popularity doesn't match (shouldn't happen with proper versioning)
            if (version != current_version or 
                content_id not in self.popularity_map or 
                popularity != current_popularity):
                heapq.heappop(self.max_heap)  # Remove stale entry
                continue
            
            # Found valid entry
            return content_id
        
        # No valid entries found
        return -1
    
    def getPopularity(self, content_id: int) -> int:
        """
        Get the current popularity of a specific content ID.
        
        Args:
            content_id (int): Content ID to query
            
        Returns:
            int: Current popularity count (0 if not tracked)
            
        Time Complexity: O(1)
        """
        return self.popularity_map.get(content_id, 0)
    
    def getAllPopularContent(self) -> Dict[int, int]:
        """
        Get all content IDs and their popularity counts.
        
        Returns:
            dict: Copy of the popularity mapping
            
        Time Complexity: O(k) where k is number of tracked content IDs
        """
        return self.popularity_map.copy()
    
    def size(self) -> int:
        """
        Get the number of content IDs currently being tracked.
        
        Returns:
            int: Number of unique content IDs with popularity > 0
            
        Time Complexity: O(1)
        """
        return len(self.popularity_map)
    
    def getHeapSize(self) -> int:
        """
        Get the current size of the internal heap (including stale entries).
        Useful for performance monitoring.
        
        Returns:
            int: Number of entries in the heap
        """
        return len(self.max_heap)
    
    def cleanupHeap(self) -> int:
        """
        Force cleanup of all stale entries from the heap.
        This is an expensive operation but can be useful for memory management.
        
        Returns:
            int: Number of stale entries removed
            
        Time Complexity: O(n log n) where n is heap size
        """
        old_size = len(self.max_heap)
        valid_entries = []
        
        # Extract all valid entries
        while self.max_heap:
            neg_popularity, version, content_id = heapq.heappop(self.max_heap)
            popularity = -neg_popularity
            
            current_version = self.version_map.get(content_id, 0)
            current_popularity = self.popularity_map.get(content_id, 0)
            
            # Keep only valid entries
            if (version == current_version and 
                content_id in self.popularity_map and 
                popularity == current_popularity):
                valid_entries.append((neg_popularity, version, content_id))
        
        # Rebuild heap with valid entries only
        self.max_heap = valid_entries
        heapq.heapify(self.max_heap)
        
        return old_size - len(self.max_heap)


def demo_heap_optimization():
    """
    Demonstrate the heap-based implementation with performance analysis.
    """
    print("=== Popular Content Tracker - Heap Optimization Demo ===\n")
    
    tracker = PopularContentTrackerHeap()
    
    # Test case 1: Basic operations
    print("1. Testing basic operations:")
    tracker.increasePopularity(1)
    tracker.increasePopularity(2)
    tracker.increasePopularity(1)  # Content 1 now has popularity 2
    
    print(f"Most popular: {tracker.getMostPopular()}")  # Should be 1
    print(f"Content 1 popularity: {tracker.getPopularity(1)}")  # Should be 2
    print(f"Heap size: {tracker.getHeapSize()}, Active content: {tracker.size()}")
    print()
    
    # Test case 2: Decrease operations and lazy deletion
    print("2. Testing decrease operations with lazy deletion:")
    tracker.decreasePopularity(1)  # Content 1 now has popularity 1
    print(f"Most popular after decrease: {tracker.getMostPopular()}")
    print(f"Heap size: {tracker.getHeapSize()}, Active content: {tracker.size()}")
    print(f"All content: {tracker.getAllPopularContent()}")
    print()
    
    # Test case 3: Stale entry cleanup demonstration
    print("3. Demonstrating stale entry cleanup:")
    # Create many updates to generate stale entries
    for i in range(5):
        tracker.increasePopularity(10)
        tracker.decreasePopularity(10)
    
    print(f"After many updates - Heap size: {tracker.getHeapSize()}")
    print(f"Most popular: {tracker.getMostPopular()}")  # This will trigger cleanup
    print(f"After getMostPopular cleanup - Heap size: {tracker.getHeapSize()}")
    print()
    
    # Test case 4: Performance comparison setup
    print("4. Setting up for performance comparison:")
    # Add multiple content items
    for content_id in [100, 200, 300, 400, 500]:
        for _ in range(content_id // 100):  # Different popularity levels
            tracker.increasePopularity(content_id)
    
    print(f"Content popularity distribution: {tracker.getAllPopularContent()}")
    print(f"Most popular: {tracker.getMostPopular()}")
    print(f"Heap size: {tracker.getHeapSize()}, Active content: {tracker.size()}")
    print()
    
    # Test case 5: Manual heap cleanup
    print("5. Testing manual heap cleanup:")
    removed = tracker.cleanupHeap()
    print(f"Manually cleaned up {removed} stale entries")
    print(f"Final heap size: {tracker.getHeapSize()}, Active content: {tracker.size()}")
    
    # Test case 6: Stream simulation with performance metrics
    print("\n6. Stream simulation with performance metrics:")
    import time
    
    actions = [
        ("increase", 1000), ("increase", 2000), ("increase", 1000),
        ("decrease", 2000), ("increase", 3000), ("increase", 3000),
        ("decrease", 1000), ("increase", 4000)
    ]
    
    for action, content_id in actions:
        start_time = time.perf_counter()
        
        if action == "increase":
            tracker.increasePopularity(content_id)
        else:
            tracker.decreasePopularity(content_id)
        
        # Measure getMostPopular performance
        most_popular = tracker.getMostPopular()
        end_time = time.perf_counter()
        
        print(f"Action: {action} {content_id}, Most popular: {most_popular}, "
              f"Time: {(end_time - start_time) * 1000:.3f}ms, "
              f"Heap: {tracker.getHeapSize()}, Active: {tracker.size()}")


if __name__ == "__main__":
    demo_heap_optimization()
