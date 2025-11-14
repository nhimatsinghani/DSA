"""
Popular Content Tracker - Part A: Basic Implementation

This implementation uses a simple dictionary to track popularity counts
and performs linear search to find the most popular content.

Time Complexity:
- increasePopularity: O(1)
- decreasePopularity: O(1) 
- getMostPopular: O(n) where n is number of unique content IDs

Space Complexity: O(k) where k is number of unique content IDs with popularity > 0
"""

class PopularContentTrackerBasic:
    def __init__(self):
        """
        Initialize the content tracker.
        
        popularity_map: Dictionary mapping content_id -> popularity_count
        Only stores content IDs with popularity > 0
        """
        self.popularity_map = {}
    
    def increasePopularity(self, content_id: int) -> None:
        """
        Increase the popularity of the given content by 1.
        
        Args:
            content_id (int): Positive integer representing content ID
            
        Time Complexity: O(1)
        """
        if content_id <= 0:
            raise ValueError("Content ID must be a positive integer")
            
        self.popularity_map[content_id] = self.popularity_map.get(content_id, 0) + 1
    
    def decreasePopularity(self, content_id: int) -> None:
        """
        Decrease the popularity of the given content by 1.
        If popularity becomes 0 or negative, remove the content from tracking.
        
        Args:
            content_id (int): Positive integer representing content ID
            
        Time Complexity: O(1)
        """
        if content_id <= 0:
            raise ValueError("Content ID must be a positive integer")
            
        if content_id in self.popularity_map:
            self.popularity_map[content_id] -= 1
            
            # Remove content if popularity becomes 0 or negative
            if self.popularity_map[content_id] <= 0:
                del self.popularity_map[content_id]
    
    def getMostPopular(self) -> int:
        """
        Return the content ID with the highest popularity.
        If multiple contents have the same highest popularity, return any one.
        If no content has popularity > 0, return -1.
        
        Returns:
            int: Content ID with highest popularity, or -1 if none exists
            
        Time Complexity: O(n) where n is number of unique content IDs
        """
        if not self.popularity_map:
            return -1
        
        # Find the content ID with maximum popularity
        max_popularity = max(self.popularity_map.values())
        
        # Find any content ID with the maximum popularity
        for content_id, popularity in self.popularity_map.items():
            if popularity == max_popularity:
                return content_id
        
        return -1  # Should never reach here if popularity_map is not empty
    
    def getPopularity(self, content_id: int) -> int:
        """
        Get the current popularity of a specific content ID.
        
        Args:
            content_id (int): Content ID to query
            
        Returns:
            int: Current popularity count (0 if not tracked)
        """
        return self.popularity_map.get(content_id, 0)
    
    def getAllPopularContent(self) -> dict:
        """
        Get all content IDs and their popularity counts.
        Useful for debugging and testing.
        
        Returns:
            dict: Copy of the popularity mapping
        """
        return self.popularity_map.copy()
    
    def size(self) -> int:
        """
        Get the number of content IDs currently being tracked.
        
        Returns:
            int: Number of unique content IDs with popularity > 0
        """
        return len(self.popularity_map)


def demo_basic_implementation():
    """
    Demonstrate the basic implementation with example usage.
    """
    print("=== Popular Content Tracker - Basic Implementation Demo ===\n")
    
    tracker = PopularContentTrackerBasic()
    
    # Test case 1: Basic operations
    print("1. Testing basic operations:")
    tracker.increasePopularity(1)
    tracker.increasePopularity(2)
    tracker.increasePopularity(1)  # Content 1 now has popularity 2
    
    print(f"Most popular: {tracker.getMostPopular()}")  # Should be 1
    print(f"Content 1 popularity: {tracker.getPopularity(1)}")  # Should be 2
    print(f"Content 2 popularity: {tracker.getPopularity(2)}")  # Should be 1
    print(f"All content: {tracker.getAllPopularContent()}")
    print()
    
    # Test case 2: Decrease operations
    print("2. Testing decrease operations:")
    tracker.decreasePopularity(1)  # Content 1 now has popularity 1
    print(f"Most popular after decrease: {tracker.getMostPopular()}")  # Could be 1 or 2
    print(f"Content 1 popularity: {tracker.getPopularity(1)}")  # Should be 1
    print()
    
    # Test case 3: Removing content
    print("3. Testing content removal:")
    tracker.decreasePopularity(2)  # Content 2 now has popularity 0, should be removed
    print(f"Most popular after removal: {tracker.getMostPopular()}")  # Should be 1
    print(f"Content 2 popularity: {tracker.getPopularity(2)}")  # Should be 0
    print(f"All content: {tracker.getAllPopularContent()}")
    print()
    
    # Test case 4: Empty state
    print("4. Testing empty state:")
    tracker.decreasePopularity(1)  # Remove last content
    print(f"Most popular when empty: {tracker.getMostPopular()}")  # Should be -1
    print(f"Size: {tracker.size()}")  # Should be 0
    print()
    
    # Test case 5: Stream simulation
    print("5. Simulating content stream:")
    actions = [
        ("increase", 10), ("increase", 20), ("increase", 10),
        ("increase", 30), ("decrease", 20), ("increase", 30),
        ("increase", 30)
    ]
    
    for action, content_id in actions:
        if action == "increase":
            tracker.increasePopularity(content_id)
        else:
            tracker.decreasePopularity(content_id)
        
        print(f"Action: {action} {content_id}, Most popular: {tracker.getMostPopular()}, "
              f"All content: {tracker.getAllPopularContent()}")


if __name__ == "__main__":
    demo_basic_implementation()
