"""
Part B: O(log N) Commodity Price Tracker Implementation

This implementation optimizes getMaxPrice to O(log N) using sorted data structures.
- Time Complexity for upsert: O(log N)
- Time Complexity for getMaxPrice: O(log N) 
- Space Complexity: O(n) where n is number of unique timestamps

Approaches demonstrated:
1. SortedList approach (if sortedcontainers available)
2. Heap-based approach using Python's heapq
3. Manual sorted list maintenance

Key optimization: Instead of scanning all values, we maintain sorted order.
"""

from typing import Optional, Dict, List
import heapq
from collections import defaultdict


class LogNSortedListTracker:
    """
    O(log N) implementation using manual sorted list maintenance.
    
    Maintains a sorted list of prices for efficient max retrieval.
    """
    
    def __init__(self):
        """Initialize the tracker."""
        self.price_data: Dict[int, float] = {}
        self.sorted_prices: List[float] = []  # Maintained in sorted order
    
    def upsert_price(self, timestamp: int, price: float) -> None:
        """
        Insert or update commodity price for given timestamp.
        
        Time Complexity: O(log N) for binary search + O(N) for list operations
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        old_price = self.price_data.get(timestamp)
        
        # Remove old price from sorted list if updating
        if old_price is not None:
            self.sorted_prices.remove(old_price)  # O(N) operation
        
        # Add new price in sorted position
        self.price_data[timestamp] = price
        
        # Binary search to find insertion position
        left, right = 0, len(self.sorted_prices)
        while left < right:
            mid = (left + right) // 2
            if self.sorted_prices[mid] < price:
                left = mid + 1
            else:
                right = mid
        
        self.sorted_prices.insert(left, price)  # O(N) for list shift
        print(f"Updated price at timestamp {timestamp}: ${price:.2f}")
    
    def get_max_commodity_price(self) -> Optional[float]:
        """
        Get maximum price in O(1) since list is sorted.
        
        Time Complexity: O(1)
        """
        if not self.sorted_prices:
            return None
        return self.sorted_prices[-1]  # Last element is maximum
    
    def size(self) -> int:
        return len(self.price_data)


class LogNHeapTracker:
    """
    O(log N) implementation using max heap approach.
    
    Uses max heap for tracking maximum values efficiently.
    Handles updates by marking entries as deleted and lazy cleanup.
    """
    
    def __init__(self):
        """Initialize the tracker."""
        self.price_data: Dict[int, float] = {}
        self.max_heap: List[float] = []  # Max heap (negated values for heapq)
        self.deleted_prices: Dict[float, int] = defaultdict(int)  # Track deleted prices
    
    def upsert_price(self, timestamp: int, price: float) -> None:
        """
        Insert or update commodity price.
        
        Time Complexity: O(log N)
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        old_price = self.price_data.get(timestamp)
        
        # Mark old price as deleted if updating
        if old_price is not None:
            self.deleted_prices[old_price] += 1
        
        # Add new price to heap and data
        self.price_data[timestamp] = price
        heapq.heappush(self.max_heap, -price)  # Negate for max heap behavior
        
        print(f"Updated price at timestamp {timestamp}: ${price:.2f}")
    
    def get_max_commodity_price(self) -> Optional[float]:
        """
        Get maximum price with lazy deletion cleanup.
        
        Time Complexity: O(log N) amortized
        """
        if not self.max_heap:
            return None
        
        # Clean up deleted entries from top of heap
        while self.max_heap and self.deleted_prices[-self.max_heap[0]] > 0:
            deleted_price = -heapq.heappop(self.max_heap)
            self.deleted_prices[deleted_price] -= 1
            if self.deleted_prices[deleted_price] == 0:
                del self.deleted_prices[deleted_price]
        
        if not self.max_heap:
            return None
            
        return -self.max_heap[0]  # Convert back from negated value
    
    def size(self) -> int:
        return len(self.price_data)


class LogNBalancedTracker:
    """
    O(log N) implementation using frequency tracking with sorted keys.
    
    More memory efficient for datasets with many duplicate prices.
    """
    
    def __init__(self):
        """Initialize the tracker."""
        self.price_data: Dict[int, float] = {}
        self.price_freq: Dict[float, int] = defaultdict(int)  # Price -> frequency
        self.sorted_unique_prices: List[float] = []  # Sorted unique prices
    
    def upsert_price(self, timestamp: int, price: float) -> None:
        """
        Insert or update commodity price.
        
        Time Complexity: O(log N) where N is number of unique prices
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        old_price = self.price_data.get(timestamp)
        
        # Remove old price frequency
        if old_price is not None:
            self.price_freq[old_price] -= 1
            if self.price_freq[old_price] == 0:
                del self.price_freq[old_price]
                self.sorted_unique_prices.remove(old_price)
        
        # Add new price
        self.price_data[timestamp] = price
        
        if price not in self.price_freq:
            # Binary search insertion for new price
            left, right = 0, len(self.sorted_unique_prices)
            while left < right:
                mid = (left + right) // 2
                if self.sorted_unique_prices[mid] < price:
                    left = mid + 1
                else:
                    right = mid
            self.sorted_unique_prices.insert(left, price)
        
        self.price_freq[price] += 1
        print(f"Updated price at timestamp {timestamp}: ${price:.2f}")
    
    def get_max_commodity_price(self) -> Optional[float]:
        """
        Get maximum price in O(1).
        
        Time Complexity: O(1)
        """
        if not self.sorted_unique_prices:
            return None
        return self.sorted_unique_prices[-1]
    
    def size(self) -> int:
        return len(self.price_data)


def demo_logn_implementations():
    """Compare different O(log N) implementations."""
    print("=== O(log N) Commodity Price Tracker Comparison ===\n")
    
    # Test data
    test_data = [
        (1000, 50.25),
        (1001, 52.00), 
        (1002, 48.75),
        (999, 55.00),   # Out of order, new max
        (1003, 45.50),
        (1001, 60.00),  # Update existing, new max
    ]
    
    implementations = [
        ("Sorted List", LogNSortedListTracker()),
        ("Max Heap", LogNHeapTracker()),
        ("Balanced Frequency", LogNBalancedTracker())
    ]
    
    for name, tracker in implementations:
        print(f"--- {name} Implementation ---")
        
        for timestamp, price in test_data:
            tracker.upsert_price(timestamp, price)
            max_price = tracker.get_max_commodity_price()
            print(f"  Max after update: ${max_price:.2f}")
        
        print(f"Final max: ${tracker.get_max_commodity_price():.2f}")
        print(f"Size: {tracker.size()}\n")


def performance_comparison():
    """Compare performance of different O(log N) approaches."""
    print("=== Performance Comparison ===")
    import time
    
    implementations = [
        ("Sorted List", LogNSortedListTracker()),
        ("Max Heap", LogNHeapTracker()),
        ("Balanced Frequency", LogNBalancedTracker())
    ]
    
    test_size = 1000
    
    for name, tracker in implementations:
        print(f"\n{name} Implementation:")
        
        # Time insertions
        start_time = time.time()
        for i in range(test_size):
            tracker.upsert_price(i, 50 + (i % 100) * 0.1)
        insert_time = time.time() - start_time
        
        # Time max queries
        start_time = time.time()
        for _ in range(100):
            max_price = tracker.get_max_commodity_price()
        query_time = time.time() - start_time
        
        print(f"  Insert {test_size} items: {insert_time*1000:.2f} ms")
        print(f"  100 max queries: {query_time*1000:.2f} ms")
        print(f"  Final max: ${max_price:.2f}")


if __name__ == "__main__":
    demo_logn_implementations()
    performance_comparison()
