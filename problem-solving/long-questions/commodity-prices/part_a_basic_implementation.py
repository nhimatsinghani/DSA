"""
Part A: Basic Commodity Price Tracker Implementation

This implementation uses a simple dictionary to store timestamp -> price mappings.
- Time Complexity for upsert: O(1)
- Time Complexity for getMaxPrice: O(n) where n is number of unique timestamps
- Space Complexity: O(n) where n is number of unique timestamps

Key Features:
1. Handles out-of-order timestamps
2. Updates existing timestamps with new prices
3. Retrieves maximum commodity price across all timestamps
"""

from typing import Optional, Dict
from datetime import datetime


class BasicCommodityPriceTracker:
    """
    Basic implementation of commodity price tracker.
    
    Uses dictionary for timestamp -> price mapping.
    Max price calculation requires scanning all values.
    """
    
    def __init__(self):
        """Initialize the tracker with empty price data."""
        self.price_data: Dict[int, float] = {}
    
    def upsert_price(self, timestamp: int, price: float) -> None:
        """
        Insert or update commodity price for given timestamp.
        
        Args:
            timestamp: Unix timestamp or any integer representing time
            price: Commodity price as float
            
        Time Complexity: O(1)
        Space Complexity: O(1) additional space per unique timestamp
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
            
        self.price_data[timestamp] = price
        print(f"Updated price at timestamp {timestamp}: ${price:.2f}")
    
    def get_max_commodity_price(self) -> Optional[float]:
        """
        Get the maximum commodity price across all timestamps.
        
        Returns:
            Maximum price as float, or None if no data exists
            
        Time Complexity: O(n) where n is number of unique timestamps
        Space Complexity: O(1)
        """
        if not self.price_data:
            return None
            
        max_price = max(self.price_data.values())
        return max_price
    
    def get_price_at_timestamp(self, timestamp: int) -> Optional[float]:
        """
        Get commodity price at specific timestamp.
        
        Args:
            timestamp: Unix timestamp to query
            
        Returns:
            Price at timestamp or None if not found
            
        Time Complexity: O(1)
        """
        return self.price_data.get(timestamp)
    
    def get_all_prices(self) -> Dict[int, float]:
        """
        Get all timestamp -> price mappings.
        
        Returns:
            Copy of internal price data dictionary
            
        Time Complexity: O(n)
        """
        return self.price_data.copy()
    
    def size(self) -> int:
        """
        Get number of unique timestamps stored.
        
        Returns:
            Number of price entries
            
        Time Complexity: O(1)
        """
        return len(self.price_data)
    
    def clear(self) -> None:
        """
        Clear all price data.
        
        Time Complexity: O(1)
        """
        self.price_data.clear()
        print("All price data cleared")


def demo_basic_implementation():
    """Demonstrate the basic commodity price tracker functionality."""
    print("=== Basic Commodity Price Tracker Demo ===\n")
    
    tracker = BasicCommodityPriceTracker()
    
    # Test case 1: Normal sequential data
    print("1. Adding sequential price data:")
    tracker.upsert_price(1000, 50.25)
    tracker.upsert_price(1001, 52.00)
    tracker.upsert_price(1002, 48.75)
    print(f"Max price: ${tracker.get_max_commodity_price():.2f}")
    print()
    
    # Test case 2: Out-of-order timestamps
    print("2. Adding out-of-order timestamps:")
    tracker.upsert_price(999, 55.00)   # Earlier timestamp, higher price
    tracker.upsert_price(1003, 45.50)  # Later timestamp, lower price
    print(f"Max price: ${tracker.get_max_commodity_price():.2f}")
    print()
    
    # Test case 3: Duplicate timestamp updates
    print("3. Updating duplicate timestamps:")
    print(f"Original price at timestamp 1001: ${tracker.get_price_at_timestamp(1001):.2f}")
    tracker.upsert_price(1001, 60.00)  # Update existing timestamp
    print(f"Updated price at timestamp 1001: ${tracker.get_price_at_timestamp(1001):.2f}")
    print(f"New max price: ${tracker.get_max_commodity_price():.2f}")
    print()
    
    # Test case 4: Edge case - empty data
    print("4. Testing edge cases:")
    tracker.clear()
    print(f"Max price after clearing: {tracker.get_max_commodity_price()}")
    print(f"Size after clearing: {tracker.size()}")
    print()
    
    # Test case 5: Large dataset simulation
    print("5. Performance test with larger dataset:")
    import time
    
    # Add 1000 price points
    start_time = time.time()
    for i in range(1000):
        tracker.upsert_price(i, 50 + (i % 100) * 0.1)
    
    # Get max price
    max_price = tracker.get_max_commodity_price()
    end_time = time.time()
    
    print(f"Added 1000 price points and found max: ${max_price:.2f}")
    print(f"Time taken: {(end_time - start_time) * 1000:.2f} ms")
    print(f"Final dataset size: {tracker.size()} timestamps")


if __name__ == "__main__":
    demo_basic_implementation()
