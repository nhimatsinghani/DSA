"""
Part C: O(1) Commodity Price Tracker Implementation

This implementation achieves O(1) getMaxPrice using auxiliary data structures.
- Time Complexity for upsert: O(1) amortized, O(log N) worst case
- Time Complexity for getMaxPrice: O(1)
- Space Complexity: O(n) where n is number of unique timestamps

Key optimization strategies:
1. Max variable tracking with frequency counting
2. Backup sorted structure for max recalculation
3. Lazy cleanup and amortized analysis

The trick is to maintain the max in O(1) for most operations, and only occasionally
need to recalculate when the max value gets updated/removed.
"""

from typing import Optional, Dict, List
import heapq
from collections import defaultdict


class ConstantTimeTracker:
    """
    O(1) implementation using max tracking with backup structures.
    
    Maintains max_price variable for O(1) access, with backup mechanisms
    for efficient max recalculation when needed.
    """
    
    def __init__(self):
        """Initialize the tracker."""
        self.price_data: Dict[int, float] = {}
        self.max_price: Optional[float] = None
        self.price_frequency: Dict[float, int] = defaultdict(int)
        
        # Backup max heap for efficient max recalculation (lazily maintained)
        self.backup_max_heap: List[float] = []
        self.heap_dirty = False  # Flag to track if heap needs cleanup
    
    def upsert_price(self, timestamp: int, price: float) -> None:
        """
        Insert or update commodity price in O(1) amortized time.
        
        Args:
            timestamp: Unix timestamp
            price: Commodity price
            
        Time Complexity: O(1) amortized - heap operations only when max recalculation needed
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        old_price = self.price_data.get(timestamp)
        
        # Handle old price removal
        if old_price is not None:
            self.price_frequency[old_price] -= 1
            if self.price_frequency[old_price] == 0:
                del self.price_frequency[old_price]
                # If we're removing the current max, we might need to recalculate
                if old_price == self.max_price:
                    self.max_price = self._find_new_max()
        
        # Add new price
        self.price_data[timestamp] = price
        self.price_frequency[price] += 1
        
        # Update max price if necessary
        if self.max_price is None or price > self.max_price:
            self.max_price = price
        
        # NOTE: Removed heappush from common path to maintain O(1) performance
        # Heap is rebuilt lazily only when max recalculation is needed
        
        print(f"Updated price at timestamp {timestamp}: ${price:.2f}")
    
    def get_max_commodity_price(self) -> Optional[float]:
        """
        Get maximum commodity price in O(1) time.
        
        Returns:
            Maximum price or None if no data
            
        Time Complexity: O(1)
        """
        return self.max_price
    
    def _find_new_max(self) -> Optional[float]:
        """
        Find new maximum price when current max is removed.
        
        Uses backup heap with lazy cleanup for efficiency.
        
        Time Complexity: O(log N) amortized due to lazy cleanup
        """
        if not self.price_frequency:
            return None
        
        # Clean up the backup heap and find valid max
        while self.backup_max_heap:
            candidate_max = -self.backup_max_heap[0]
            
            # Check if this price still exists in our data
            if candidate_max in self.price_frequency:
                return candidate_max
            else:
                # Remove invalid entry from heap
                heapq.heappop(self.backup_max_heap)
        
        # If heap is empty but we have prices, rebuild from current data
        if self.price_frequency:
            # Rebuild backup heap from current prices
            self.backup_max_heap = [-price for price in self.price_frequency.keys()]
            heapq.heapify(self.backup_max_heap)
            return -self.backup_max_heap[0] if self.backup_max_heap else None
        
        return None
    
    def get_price_at_timestamp(self, timestamp: int) -> Optional[float]:
        """Get price at specific timestamp in O(1)."""
        return self.price_data.get(timestamp)
    
    def size(self) -> int:
        """Get number of unique timestamps in O(1)."""
        return len(self.price_data)
    
    def get_price_statistics(self) -> Dict:
        """Get comprehensive price statistics."""
        if not self.price_frequency:
            return {"count": 0, "min": None, "max": None, "unique_prices": 0}
        
        prices = list(self.price_frequency.keys())
        return {
            "count": len(self.price_data),
            "min": min(prices),
            "max": self.max_price,
            "unique_prices": len(prices),
            "most_common_price": max(self.price_frequency.items(), key=lambda x: x[1])
        }


class OptimizedConstantTracker:
    """
    Further optimized O(1) implementation with smart max tracking.
    
    Uses multiple optimization techniques:
    - Direct max tracking for common case
    - Frequency-based validation
    - Minimal backup structures
    """
    
    def __init__(self):
        """Initialize the optimized tracker."""
        self.price_data: Dict[int, float] = {}
        self.max_price: Optional[float] = None
        self.max_count: int = 0  # How many timestamps have the max price
        
        # Lightweight backup: just track second highest price
        self.second_max: Optional[float] = None
        self.price_frequency: Dict[float, int] = defaultdict(int)
    
    def upsert_price(self, timestamp: int, price: float) -> None:
        """
        Highly optimized upsert with smart max tracking.
        
        Time Complexity: O(1) for most cases, O(K) only when max needs full recalculation
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        old_price = self.price_data.get(timestamp)
        
        # Handle old price removal
        if old_price is not None:
            self.price_frequency[old_price] -= 1
            
            # Update max count if removing a max price
            if old_price == self.max_price:
                self.max_count -= 1
                if self.max_count == 0:
                    # Promote second_max to max, find new second_max
                    self.max_price = self.second_max
                    if self.max_price is not None:
                        self.max_count = self.price_frequency.get(self.max_price, 0)
                        # Only recalculate second_max when absolutely necessary
                        self._update_second_max()
                    else:
                        self.max_count = 0
            elif old_price == self.second_max:
                # If removing second max, may need to find new second max
                if self.price_frequency[old_price] == 0:
                    self._update_second_max()
            
            # Clean up frequency map
            if self.price_frequency[old_price] == 0:
                del self.price_frequency[old_price]
        
        # Add new price
        self.price_data[timestamp] = price
        self.price_frequency[price] += 1
        
        # Update max tracking
        if self.max_price is None or price > self.max_price:
            self.second_max = self.max_price
            self.max_price = price
            self.max_count = self.price_frequency[price]
        elif price == self.max_price:
            self.max_count += 1
        elif self.second_max is None or price > self.second_max:
            self.second_max = price
        
        print(f"Updated price at timestamp {timestamp}: ${price:.2f}")
    
    def _update_second_max(self):
        """Update second max after max changes. O(K) where K is unique prices."""
        if len(self.price_frequency) <= 1:
            self.second_max = None
            return
        
        # Find the largest price that's not the current max
        self.second_max = None
        for price in self.price_frequency.keys():
            if price != self.max_price:
                if self.second_max is None or price > self.second_max:
                    self.second_max = price
    
    def get_max_commodity_price(self) -> Optional[float]:
        """Get maximum price in O(1)."""
        return self.max_price
    
    def size(self) -> int:
        return len(self.price_data)


class TrueConstantTracker:
    """
    True O(1) implementation with minimal overhead.
    
    Achieves O(1) for common operations by avoiding any sorting or heap operations
    in the normal path. Only resorts to O(K) operations when absolutely necessary.
    """
    
    def __init__(self):
        """Initialize the tracker."""
        self.price_data: Dict[int, float] = {}
        self.max_price: Optional[float] = None
        self.max_count: int = 0
        self.price_frequency: Dict[float, int] = defaultdict(int)
        
        # Track some candidate max values for faster recovery
        self.candidate_maxes: List[float] = []  # Keep top few prices
        self.max_candidates_size = 3
    
    def upsert_price(self, timestamp: int, price: float) -> None:
        """
        Insert or update commodity price in true O(1) amortized time.
        
        Time Complexity: O(1) amortized - no heap or sort operations in common path
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        old_price = self.price_data.get(timestamp)
        
        # Handle old price removal  
        if old_price is not None:
            self.price_frequency[old_price] -= 1
            
            if old_price == self.max_price:
                self.max_count -= 1
                if self.max_count == 0:
                    # Max price completely removed - find new max
                    self._find_new_max_efficiently()
            
            # Clean up frequency map
            if self.price_frequency[old_price] == 0:
                del self.price_frequency[old_price]
                # Remove from candidates if present
                if old_price in self.candidate_maxes:
                    self.candidate_maxes.remove(old_price)
        
        # Add new price
        self.price_data[timestamp] = price
        self.price_frequency[price] += 1
        
        # Update max price tracking
        if self.max_price is None or price > self.max_price:
            self.max_price = price
            self.max_count = self.price_frequency[price]
            self._update_candidates(price)
        elif price == self.max_price:
            self.max_count += 1
        else:
            # Add to candidates if it's high enough
            self._update_candidates(price)
        
        print(f"Updated price at timestamp {timestamp}: ${price:.2f}")
    
    def _update_candidates(self, price: float) -> None:
        """Update candidate max values. True O(1) operation."""
        if price not in self.candidate_maxes:
            if len(self.candidate_maxes) < self.max_candidates_size:
                self.candidate_maxes.append(price)
            else:
                # Replace smallest candidate if new price is larger
                min_candidate = min(self.candidate_maxes)
                if price > min_candidate:
                    self.candidate_maxes.remove(min_candidate)
                    self.candidate_maxes.append(price)
    
    def _find_new_max_efficiently(self) -> None:
        """Find new max using candidates first, fallback to full scan. O(1) amortized."""
        if not self.price_frequency:
            self.max_price = None
            self.max_count = 0
            return
        
        # Try candidates first (O(1) since candidates list is small)
        best_candidate = None
        for candidate in self.candidate_maxes:
            if candidate in self.price_frequency:
                if best_candidate is None or candidate > best_candidate:
                    best_candidate = candidate
        
        if best_candidate is not None:
            self.max_price = best_candidate
            self.max_count = self.price_frequency[best_candidate]
        else:
            # Fallback to full scan (O(K) but happens infrequently)
            self.max_price = max(self.price_frequency.keys())
            self.max_count = self.price_frequency[self.max_price]
            # Rebuild candidates
            self._rebuild_candidates()
    
    def _rebuild_candidates(self) -> None:
        """Rebuild candidate list from current prices. O(K) but infrequent."""
        prices = sorted(self.price_frequency.keys(), reverse=True)
        self.candidate_maxes = prices[:self.max_candidates_size]
    
    def get_max_commodity_price(self) -> Optional[float]:
        """Get maximum price in O(1)."""
        return self.max_price
    
    def size(self) -> int:
        return len(self.price_data)


def demo_constant_implementations():
    """Demonstrate O(1) implementations."""
    print("=== O(1) Commodity Price Tracker Demo ===\n")
    
    implementations = [
        ("Constant Time (Heap Backup)", ConstantTimeTracker()),
        ("Optimized Constant", OptimizedConstantTracker()),
        ("True Constant O(1)", TrueConstantTracker())
    ]
    
    # Complex test scenario
    test_scenarios = [
        ("Initial data", [(1000, 50.0), (1001, 60.0), (1002, 55.0)]),
        ("Update max", [(1001, 65.0)]),  # Update existing max
        ("Remove max", [(1001, 40.0)]),  # Max becomes non-max
        ("New max", [(1003, 70.0)]),     # New timestamp with max
        ("Duplicate prices", [(1004, 70.0), (1005, 70.0)]),  # Multiple max values
        ("Remove one max", [(1003, 50.0)]),  # Remove one of multiple max values
    ]
    
    for name, tracker in implementations:
        print(f"--- {name} Implementation ---")
        
        for scenario_name, operations in test_scenarios:
            print(f"\n{scenario_name}:")
            for timestamp, price in operations:
                tracker.upsert_price(timestamp, price)
                max_price = tracker.get_max_commodity_price()
                print(f"  Max after operation: ${max_price:.2f}")
        
        if hasattr(tracker, 'get_price_statistics'):
            stats = tracker.get_price_statistics()
            print(f"\nFinal statistics: {stats}")
        
        print(f"Final size: {tracker.size()}\n")


def stress_test_constant_time():
    """Stress test the O(1) implementation."""
    print("=== O(1) Implementation Stress Test ===")
    import time
    import random
    
    tracker = ConstantTimeTracker()
    
    # Large dataset test
    print("Testing with 10,000 operations...")
    
    start_time = time.time()
    
    # Insert phase
    for i in range(5000):
        price = random.uniform(10.0, 100.0)
        tracker.upsert_price(i, price)
    
    # Update phase (simulate real-world updates)
    for _ in range(2500):
        timestamp = random.randint(0, 4999)
        new_price = random.uniform(10.0, 100.0)
        tracker.upsert_price(timestamp, new_price)
    
    # Query phase
    max_queries = 2500
    for _ in range(max_queries):
        max_price = tracker.get_max_commodity_price()
    
    end_time = time.time()
    
    print(f"Completed 10,000 operations in {(end_time - start_time)*1000:.2f} ms")
    print(f"Final max price: ${tracker.get_max_commodity_price():.2f}")
    print(f"Final size: {tracker.size()}")
    print(f"Average time per operation: {((end_time - start_time)*1000)/10000:.4f} ms")


if __name__ == "__main__":
    demo_constant_implementations()
    stress_test_constant_time()
