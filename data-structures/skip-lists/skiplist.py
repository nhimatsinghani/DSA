"""
Skip List Implementation
======================

A probabilistic data structure that allows for efficient search, insertion, 
and deletion operations in O(log n) expected time.

Author: Data Structures & Algorithms Study
"""

import random
from typing import Optional, List, Tuple, Iterator, Any, Dict
import math


class SkipListNode:
    """
    Node class for Skip List.
    
    Each node contains:
    - key: The key value
    - value: Associated value (optional)
    - forward: Array of forward pointers for each level
    """
    
    def __init__(self, key: Any, value: Any, level: int):
        self.key = key
        self.value = value
        self.forward = [None] * (level + 1)
    
    def __repr__(self):
        return f"SkipListNode(key={self.key}, value={self.value}, level={len(self.forward)-1})"


class SkipList:
    """
    Skip List data structure implementation.
    
    A Skip List is a probabilistic data structure that maintains a sorted
    sequence of elements and allows for efficient search, insertion, and
    deletion operations.
    """
    
    def __init__(self, max_level: int = 16, p: float = 0.5):
        """
        Initialize a Skip List.
        
        Args:
            max_level: Maximum number of levels (default: 16)
            p: Probability for level promotion (default: 0.5)
        """
        self.max_level = max_level
        self.p = p
        self.level = 0  # Current maximum level in the skip list
        self.header = SkipListNode(None, None, max_level)
        self.size = 0
        
        # Statistics tracking
        self.search_comparisons = 0
        self.insert_comparisons = 0
        self.delete_comparisons = 0
    
    def _random_level(self) -> int:
        """
        Generate a random level for a new node using geometric distribution.
        
        Returns:
            Random level between 0 and max_level
        """
        level = 0
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level
    
    def search(self, key: Any) -> Optional[Any]:
        """
        Search for a key in the skip list.
        
        Args:
            key: Key to search for
            
        Returns:
            Value associated with the key, or None if not found
        """
        current = self.header
        self.search_comparisons = 0
        
        # Start from the highest level and work down
        for i in range(self.level, -1, -1):
            # Move forward while the next node's key is less than target
            while (current.forward[i] is not None and 
                   current.forward[i].key < key):
                current = current.forward[i]
                self.search_comparisons += 1
        
        # Move to level 0 and check if we found the key
        current = current.forward[0]
        self.search_comparisons += 1
        
        if current is not None and current.key == key:
            return current.value
        return None
    
    def insert(self, key: Any, value: Any) -> bool:
        """
        Insert a key-value pair into the skip list.
        
        Args:
            key: Key to insert
            value: Value to associate with the key
            
        Returns:
            True if inserted, False if key already exists (updates value)
        """
        update = [None] * (self.max_level + 1)
        current = self.header
        self.insert_comparisons = 0
        
        # Find the insertion point at each level
        for i in range(self.level, -1, -1):
            while (current.forward[i] is not None and 
                   current.forward[i].key < key):
                current = current.forward[i]
                self.insert_comparisons += 1
            update[i] = current
        
        # Move to level 0
        current = current.forward[0]
        self.insert_comparisons += 1
        
        # If key already exists, update value
        if current is not None and current.key == key:
            current.value = value
            return False
        
        # Generate random level for new node
        new_level = self._random_level()
        
        # If new level is higher than current level, update header pointers
        if new_level > self.level:
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.header
            self.level = new_level
        
        # Create new node
        new_node = SkipListNode(key, value, new_level)
        
        # Update forward pointers
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
        
        self.size += 1
        return True
    
    def delete(self, key: Any) -> bool:
        """
        Delete a key from the skip list.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False if key not found
        """
        update = [None] * (self.max_level + 1)
        current = self.header
        self.delete_comparisons = 0
        
        # Find the deletion point at each level
        for i in range(self.level, -1, -1):
            while (current.forward[i] is not None and 
                   current.forward[i].key < key):
                current = current.forward[i]
                self.delete_comparisons += 1
            update[i] = current
        
        # Move to level 0
        current = current.forward[0]
        self.delete_comparisons += 1
        
        # Check if key exists
        if current is None or current.key != key:
            return False
        
        # Update forward pointers to skip the deleted node
        for i in range(self.level + 1):
            if update[i].forward[i] != current:
                break
            update[i].forward[i] = current.forward[i]
        
        # Update level if necessary
        while self.level > 0 and self.header.forward[self.level] is None:
            self.level -= 1
        
        self.size -= 1
        return True
    
    def range_query(self, start_key: Any, end_key: Any) -> List[Tuple[Any, Any]]:
        """
        Get all key-value pairs in a given range.
        
        Args:
            start_key: Start of range (inclusive)
            end_key: End of range (inclusive)
            
        Returns:
            List of (key, value) tuples in the range
        """
        result = []
        current = self.header
        
        # Find the starting point
        for i in range(self.level, -1, -1):
            while (current.forward[i] is not None and 
                   current.forward[i].key < start_key):
                current = current.forward[i]
        
        # Move to level 0
        current = current.forward[0]
        
        # Collect all elements in range
        while current is not None and current.key <= end_key:
            if current.key >= start_key:
                result.append((current.key, current.value))
            current = current.forward[0]
        
        return result
    
    def min_key(self) -> Optional[Any]:
        """Get the minimum key in the skip list."""
        if self.size == 0:
            return None
        return self.header.forward[0].key
    
    def max_key(self) -> Optional[Any]:
        """Get the maximum key in the skip list."""
        if self.size == 0:
            return None
        
        current = self.header
        for i in range(self.level, -1, -1):
            while current.forward[i] is not None:
                current = current.forward[i]
        
        return current.key
    
    def __len__(self) -> int:
        """Return the number of elements in the skip list."""
        return self.size
    
    def __contains__(self, key: Any) -> bool:
        """Check if a key exists in the skip list."""
        return self.search(key) is not None
    
    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        """Iterate over key-value pairs in sorted order."""
        current = self.header.forward[0]
        while current is not None:
            yield (current.key, current.value)
            current = current.forward[0]
    
    def keys(self) -> Iterator[Any]:
        """Iterate over keys in sorted order."""
        for key, _ in self:
            yield key
    
    def values(self) -> Iterator[Any]:
        """Iterate over values in key-sorted order."""
        for _, value in self:
            yield value
    
    def items(self) -> Iterator[Tuple[Any, Any]]:
        """Iterate over key-value pairs in sorted order."""
        return self.__iter__()
    
    def clear(self) -> None:
        """Remove all elements from the skip list."""
        self.header = SkipListNode(None, None, self.max_level)
        self.level = 0
        self.size = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the skip list structure.
        
        Returns:
            Dictionary with statistics
        """
        # Count nodes at each level
        level_counts = [0] * (self.level + 1)
        current = self.header.forward[0]
        
        while current is not None:
            for i in range(len(current.forward)):
                if i <= self.level:
                    level_counts[i] += 1
            current = current.forward[0]
        
        # Calculate average level
        total_levels = sum(i * count for i, count in enumerate(level_counts))
        avg_level = total_levels / self.size if self.size > 0 else 0
        
        # Theoretical expected height
        expected_height = math.log(self.size) / math.log(1/self.p) if self.size > 0 else 0
        
        return {
            'size': self.size,
            'current_max_level': self.level,
            'max_possible_level': self.max_level,
            'level_counts': level_counts,
            'average_node_level': avg_level,
            'expected_height': expected_height,
            'probability': self.p,
            'last_search_comparisons': self.search_comparisons,
            'last_insert_comparisons': self.insert_comparisons,
            'last_delete_comparisons': self.delete_comparisons
        }
    
    def display(self, show_levels: bool = True) -> None:
        """
        Display the skip list structure.
        
        Args:
            show_levels: Whether to show all levels or just level 0
        """
        if self.size == 0:
            print("Skip List is empty")
            return
        
        print(f"Skip List (size={self.size}, levels=0-{self.level}):")
        print("=" * 50)
        
        if show_levels:
            # Display level by level
            for level in range(self.level, -1, -1):
                print(f"Level {level:2d}: ", end="")
                current = self.header.forward[level]
                
                if current is None:
                    print("(empty)")
                else:
                    elements = []
                    while current is not None:
                        elements.append(f"{current.key}")
                        current = current.forward[level]
                    print(" -> ".join(elements))
        else:
            # Display only level 0 (all elements)
            print("Elements: ", end="")
            current = self.header.forward[0]
            elements = []
            while current is not None:
                elements.append(f"{current.key}:{current.value}")
                current = current.forward[0]
            print(" -> ".join(elements))
        
        print("=" * 50)


# Utility functions for Skip List
def create_skip_list_from_list(items: List[Tuple[Any, Any]], 
                              max_level: int = 16, 
                              p: float = 0.5) -> SkipList:
    """
    Create a skip list from a list of (key, value) tuples.
    
    Args:
        items: List of (key, value) tuples
        max_level: Maximum level for skip list
        p: Probability for level promotion
        
    Returns:
        Populated skip list
    """
    sl = SkipList(max_level, p)
    for key, value in items:
        sl.insert(key, value)
    return sl


def merge_skip_lists(sl1: SkipList, sl2: SkipList) -> SkipList:
    """
    Merge two skip lists into a new skip list.
    
    Args:
        sl1: First skip list
        sl2: Second skip list
        
    Returns:
        New skip list containing all elements from both lists
    """
    result = SkipList(max(sl1.max_level, sl2.max_level), min(sl1.p, sl2.p))
    
    # Add all elements from both skip lists
    for key, value in sl1:
        result.insert(key, value)
    
    for key, value in sl2:
        result.insert(key, value)
    
    return result


if __name__ == "__main__":
    # Quick demonstration
    print("Skip List Implementation Demo")
    print("=" * 40)
    
    # Create skip list
    sl = SkipList()
    
    # Insert some data
    data = [(3, "three"), (1, "one"), (4, "four"), (1, "ONE"), (5, "five"), (2, "two")]
    print("Inserting:", data)
    
    for key, value in data:
        inserted = sl.insert(key, value)
        print(f"Insert {key}:{value} -> {'New' if inserted else 'Updated'}")
    
    print(f"\nSkip List size: {len(sl)}")
    
    # Display structure
    sl.display()
    
    # Search operations
    print("\nSearch Operations:")
    for key in [1, 3, 6]:
        result = sl.search(key)
        print(f"Search {key}: {result} (comparisons: {sl.search_comparisons})")
    
    # Range query
    print(f"\nRange query [2, 4]: {sl.range_query(2, 4)}")
    
    # Delete operation
    print(f"\nDelete 3: {sl.delete(3)}")
    sl.display(show_levels=False)
    
    # Statistics
    print("\nStatistics:")
    stats = sl.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}") 