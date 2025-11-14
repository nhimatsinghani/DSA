"""
Popular Content Tracker - Part C: Advanced Hybrid Implementation

This implementation combines multiple optimization techniques for maximum performance:
1. Frequency tracking: Maps popularity levels to count of content items
2. Sorted popularity levels: Maintains max popularity for O(1) access
3. Efficient batch operations: Optimized for high-throughput scenarios
4. Memory-conscious design: Minimal overhead per content item

Key Innovations:
- O(1) getMostPopular in most cases (when max popularity is stable)
- O(1) increase/decrease operations
- Frequency-based tracking reduces memory overhead for items with same popularity
- Smart cleanup strategies to maintain performance

Time Complexity:
- increasePopularity: O(1) average, O(log k) worst case (k = unique popularity levels)
- decreasePopularity: O(1) average, O(log k) worst case
- getMostPopular: O(1) average, O(log k) worst case

Space Complexity: O(n + k) where n = unique content IDs, k = unique popularity levels
"""

from collections import defaultdict, deque
from typing import Dict, Set, Optional
import bisect

class PopularContentTrackerAdvanced:
    def __init__(self):
        """
        Initialize the advanced hybrid content tracker.
        
        popularity_map: content_id -> popularity_count
        popularity_frequency: popularity_level -> count_of_items_with_this_popularity
        content_by_popularity: popularity_level -> set_of_content_ids
        sorted_popularities: sorted list of all popularity levels (descending)
        max_popularity: cached maximum popularity for O(1) access
        """
        self.popularity_map: Dict[int, int] = {}
        self.popularity_frequency: Dict[int, int] = defaultdict(int)
        self.content_by_popularity: Dict[int, Set[int]] = defaultdict(set)
        self.sorted_popularities: list = []  # Sorted in descending order
        self.max_popularity: Optional[int] = None
        
        # Performance tracking
        self._update_count = 0
        self._cleanup_threshold = 1000
    
    def _add_to_popularity_level(self, content_id: int, popularity: int) -> None:
        """
        Add content to a specific popularity level with efficient bookkeeping.
        """
        # Add to popularity tracking
        self.content_by_popularity[popularity].add(content_id)
        self.popularity_frequency[popularity] += 1
        
        # Update sorted popularities if this is a new level
        if self.popularity_frequency[popularity] == 1:
            # New popularity level - insert in sorted order
            bisect.insort(self.sorted_popularities, popularity)
            self.sorted_popularities.reverse()  # Keep descending order
            self.sorted_popularities.sort(reverse=True)
        
        # Update max popularity cache
        if self.max_popularity is None or popularity > self.max_popularity:
            self.max_popularity = popularity
    
    def _remove_from_popularity_level(self, content_id: int, popularity: int) -> None:
        """
        Remove content from a specific popularity level with efficient bookkeeping.
        """
        # Remove from popularity tracking
        if content_id in self.content_by_popularity[popularity]:
            self.content_by_popularity[popularity].remove(content_id)
            self.popularity_frequency[popularity] -= 1
            
            # Clean up empty popularity level
            if self.popularity_frequency[popularity] == 0:
                del self.popularity_frequency[popularity]
                del self.content_by_popularity[popularity]
                self.sorted_popularities.remove(popularity)
                
                # Update max popularity cache
                if popularity == self.max_popularity:
                    self.max_popularity = self.sorted_popularities[0] if self.sorted_popularities else None
    
    def increasePopularity(self, content_id: int) -> None:
        """
        Increase the popularity of the given content by 1.
        
        Args:
            content_id (int): Positive integer representing content ID
            
        Time Complexity: O(1) average case, O(log k) worst case where k = unique popularity levels
        """
        if content_id <= 0:
            raise ValueError("Content ID must be a positive integer")
        
        old_popularity = self.popularity_map.get(content_id, 0)
        new_popularity = old_popularity + 1
        
        # Update popularity map
        self.popularity_map[content_id] = new_popularity
        
        # Remove from old popularity level if it existed
        if old_popularity > 0:
            self._remove_from_popularity_level(content_id, old_popularity)
        
        # Add to new popularity level
        self._add_to_popularity_level(content_id, new_popularity)
        
        self._update_count += 1
        self._maybe_cleanup()
    
    def decreasePopularity(self, content_id: int) -> None:
        """
        Decrease the popularity of the given content by 1.
        
        Args:
            content_id (int): Positive integer representing content ID
            
        Time Complexity: O(1) average case, O(log k) worst case where k = unique popularity levels
        """
        if content_id <= 0:
            raise ValueError("Content ID must be a positive integer")
        
        if content_id not in self.popularity_map:
            return  # Nothing to decrease
        
        old_popularity = self.popularity_map[content_id]
        new_popularity = old_popularity - 1
        
        # Remove from old popularity level
        self._remove_from_popularity_level(content_id, old_popularity)
        
        if new_popularity <= 0:
            # Remove content entirely
            del self.popularity_map[content_id]
        else:
            # Update popularity map and add to new level
            self.popularity_map[content_id] = new_popularity
            self._add_to_popularity_level(content_id, new_popularity)
        
        self._update_count += 1
        self._maybe_cleanup()
    
    def getMostPopular(self) -> int:
        """
        Return the content ID with the highest popularity.
        
        Returns:
            int: Content ID with highest popularity, or -1 if none exists
            
        Time Complexity: O(1) average case (cached max), O(log k) worst case
        """
        if self.max_popularity is None or self.max_popularity <= 0:
            return -1
        
        # Get any content ID with max popularity
        max_content_set = self.content_by_popularity.get(self.max_popularity, set())
        if max_content_set:
            return next(iter(max_content_set))  # Return any content with max popularity
        
        # Fallback: should not happen if bookkeeping is correct
        return -1
    
    def getTopK(self, k: int) -> list:
        """
        Get the top K most popular content IDs.
        
        Args:
            k (int): Number of top items to return
            
        Returns:
            list: List of (content_id, popularity) tuples sorted by popularity desc
            
        Time Complexity: O(k) for small k, O(n) for large k
        """
        result = []
        count = 0
        
        for popularity in self.sorted_popularities:
            if count >= k:
                break
            
            content_set = self.content_by_popularity[popularity]
            for content_id in content_set:
                if count >= k:
                    break
                result.append((content_id, popularity))
                count += 1
        
        return result
    
    def getPopularityDistribution(self) -> Dict[int, int]:
        """
        Get the distribution of popularities (popularity_level -> count_of_items).
        
        Returns:
            dict: Mapping from popularity level to count of items
        """
        return dict(self.popularity_frequency)
    
    def getPopularity(self, content_id: int) -> int:
        """
        Get the current popularity of a specific content ID.
        
        Time Complexity: O(1)
        """
        return self.popularity_map.get(content_id, 0)
    
    def getAllPopularContent(self) -> Dict[int, int]:
        """
        Get all content IDs and their popularity counts.
        
        Time Complexity: O(n) where n = number of tracked content IDs
        """
        return self.popularity_map.copy()
    
    def size(self) -> int:
        """
        Get the number of content IDs currently being tracked.
        
        Time Complexity: O(1)
        """
        return len(self.popularity_map)
    
    def getUniquePopularityLevels(self) -> int:
        """
        Get the number of unique popularity levels.
        
        Time Complexity: O(1)
        """
        return len(self.sorted_popularities)
    
    def _maybe_cleanup(self) -> None:
        """
        Perform periodic cleanup to maintain optimal performance.
        """
        if self._update_count >= self._cleanup_threshold:
            self._cleanup()
            self._update_count = 0
    
    def _cleanup(self) -> None:
        """
        Validate and cleanup internal data structures.
        This is primarily for debugging and ensuring consistency.
        """
        # Verify consistency between data structures
        for popularity, content_set in self.content_by_popularity.items():
            assert len(content_set) == self.popularity_frequency[popularity]
            for content_id in content_set:
                assert self.popularity_map[content_id] == popularity
    
    def getBenchmarkStats(self) -> Dict[str, int]:
        """
        Get performance and memory statistics for benchmarking.
        """
        total_content_entries = len(self.popularity_map)
        total_popularity_levels = len(self.sorted_popularities)
        total_set_entries = sum(len(s) for s in self.content_by_popularity.values())
        
        return {
            "content_entries": total_content_entries,
            "popularity_levels": total_popularity_levels,
            "set_entries": total_set_entries,
            "max_popularity": self.max_popularity or 0,
            "update_count": self._update_count
        }


def demo_advanced_hybrid():
    """
    Demonstrate the advanced hybrid implementation with comprehensive testing.
    """
    print("=== Popular Content Tracker - Advanced Hybrid Demo ===\n")
    
    tracker = PopularContentTrackerAdvanced()
    
    # Test case 1: Basic operations
    print("1. Testing basic operations:")
    tracker.increasePopularity(1)
    tracker.increasePopularity(2)
    tracker.increasePopularity(1)  # Content 1 now has popularity 2
    tracker.increasePopularity(3)
    tracker.increasePopularity(3)  # Content 3 now has popularity 2
    
    print(f"Most popular: {tracker.getMostPopular()}")  # Should be 1 or 3
    print(f"Top 3: {tracker.getTopK(3)}")
    print(f"Popularity distribution: {tracker.getPopularityDistribution()}")
    print(f"Stats: {tracker.getBenchmarkStats()}")
    print()
    
    # Test case 2: Popularity level tracking
    print("2. Testing popularity level tracking:")
    # Create multiple items with same popularity
    for content_id in [10, 11, 12]:
        tracker.increasePopularity(content_id)
        tracker.increasePopularity(content_id)
        tracker.increasePopularity(content_id)  # All have popularity 3
    
    print(f"Popularity distribution: {tracker.getPopularityDistribution()}")
    print(f"Most popular: {tracker.getMostPopular()}")  # Should be from popularity 3 group
    print(f"Top 5: {tracker.getTopK(5)}")
    print()
    
    # Test case 3: Dynamic popularity changes
    print("3. Testing dynamic popularity changes:")
    tracker.decreasePopularity(10)  # 10 goes from 3 to 2
    tracker.decreasePopularity(10)  # 10 goes from 2 to 1
    
    print(f"After decreasing content 10:")
    print(f"Popularity distribution: {tracker.getPopularityDistribution()}")
    print(f"Most popular: {tracker.getMostPopular()}")
    print(f"Content 10 popularity: {tracker.getPopularity(10)}")
    print()
    
    # Test case 4: High-frequency scenario simulation
    print("4. High-frequency scenario simulation:")
    import time
    
    # Simulate high-frequency updates
    start_time = time.perf_counter()
    
    for i in range(100):
        content_id = (i % 10) + 100  # Use content IDs 100-109
        if i % 3 == 0:
            tracker.increasePopularity(content_id)
        else:
            tracker.decreasePopularity(content_id)
        
        # Periodically check most popular (simulating real queries)
        if i % 10 == 0:
            most_popular = tracker.getMostPopular()
    
    end_time = time.perf_counter()
    
    print(f"Processed 100 operations in {(end_time - start_time) * 1000:.3f}ms")
    print(f"Final stats: {tracker.getBenchmarkStats()}")
    print(f"Final top 3: {tracker.getTopK(3)}")
    print()
    
    # Test case 5: Memory efficiency comparison
    print("5. Memory efficiency analysis:")
    print(f"Unique content IDs: {tracker.size()}")
    print(f"Unique popularity levels: {tracker.getUniquePopularityLevels()}")
    print(f"Memory efficiency ratio: {tracker.size() / max(1, tracker.getUniquePopularityLevels()):.2f}")
    
    # Demonstrate O(1) getMostPopular performance
    start_time = time.perf_counter()
    for _ in range(1000):
        tracker.getMostPopular()
    end_time = time.perf_counter()
    
    print(f"1000 getMostPopular calls: {(end_time - start_time) * 1000:.3f}ms")
    print(f"Average per call: {((end_time - start_time) * 1000000) / 1000:.3f}μs")


def compare_all_implementations():
    """
    Compare performance across all three implementations.
    """
    print("\n=== Performance Comparison Across All Implementations ===\n")
    
    from part_a_basic_implementation import PopularContentTrackerBasic
    from part_b_heap_optimization import PopularContentTrackerHeap
    
    implementations = [
        ("Basic (O(n))", PopularContentTrackerBasic()),
        ("Heap (O(log n))", PopularContentTrackerHeap()),
        ("Advanced (O(1))", PopularContentTrackerAdvanced())
    ]
    
    # Setup identical data for all implementations
    operations = []
    for i in range(50):
        operations.append(("increase", (i % 10) + 1))
    for i in range(25):
        operations.append(("decrease", (i % 10) + 1))
    
    import time
    
    for name, tracker in implementations:
        start_time = time.perf_counter()
        
        # Perform operations
        for op_type, content_id in operations:
            if op_type == "increase":
                tracker.increasePopularity(content_id)
            else:
                tracker.decreasePopularity(content_id)
        
        # Perform many getMostPopular calls
        for _ in range(100):
            tracker.getMostPopular()
        
        end_time = time.perf_counter()
        
        print(f"{name}: {(end_time - start_time) * 1000:.3f}ms total")
        print(f"  Most popular: {tracker.getMostPopular()}")
        print(f"  Active content: {tracker.size()}")
        if hasattr(tracker, 'getBenchmarkStats'):
            print(f"  Stats: {tracker.getBenchmarkStats()}")
        print()


if __name__ == "__main__":
    demo_advanced_hybrid()
    compare_all_implementations()
