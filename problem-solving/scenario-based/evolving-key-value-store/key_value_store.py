import time
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import bisect
from sortedcontainers import SortedList


@dataclass
class Record:
    """Represents a single record in the database with timestamp and TTL."""
    value: Any
    timestamp: float
    ttl: Optional[float] = None  # TTL in seconds
    deleted: bool = False
    
    def is_expired(self, current_time: float) -> bool:
        """Check if the record is expired based on TTL."""
        if self.ttl is None:
            return False
        return current_time > self.timestamp + self.ttl
    
    def is_valid_at_time(self, query_time: float) -> bool:
        """Check if record is valid at a specific time (not expired and not deleted)."""
        if self.deleted:
            return False
        if self.ttl is None:
            return True
        return query_time <= self.timestamp + self.ttl


class EvolvingKeyValueStore:
    """
    An in-memory key-value store that evolves through 4 stages:
    Stage 1: Basic get/set functionality
    Stage 2: TTL (Time-To-Live) support
    Stage 3: Point-in-time queries
    Stage 4: Deletion functionality
    """
    
    def __init__(self):
        # Stage 1: Basic storage
        self.data: Dict[str, Any] = {}
        
        # Stage 2: TTL tracking
        self.ttl_data: Dict[str, Tuple[Any, float, Optional[float]]] = {}  # key -> (value, timestamp, ttl)
        
        # Stage 3: Historical data for point-in-time queries
        self.history: Dict[str, SortedList[Record]] = defaultdict(lambda: SortedList(key=lambda record: record.timestamp))
        
        # Stage 4: Deletion tracking
        self.deleted_keys: set = set()
    
    # ==================== STAGE 1: Basic Operations ====================
    
    def set_basic(self, key: str, value: Any) -> None:
        """Stage 1: Basic set operation without TTL."""
        self.data[key] = value
    
    def get_basic(self, key: str) -> Optional[Any]:
        """Stage 1: Basic get operation."""
        return self.data.get(key)
    
    # ==================== STAGE 2: TTL Operations ====================
    
    def set_with_ttl(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Stage 2: Set with optional TTL (time-to-live in seconds)."""
        current_time = time.time()
        self.ttl_data[key] = (value, current_time, ttl)
        
        # Also update basic storage for backward compatibility
        self.data[key] = value
    
    def get_with_ttl(self, key: str) -> Optional[Any]:
        """Stage 2: Get operation that respects TTL."""
        if key not in self.ttl_data:
            return None
        
        value, timestamp, ttl = self.ttl_data[key]
        current_time = time.time()
        
        # Check if expired
        if ttl is not None and current_time > timestamp + ttl:
            # Remove expired key
            del self.ttl_data[key]
            if key in self.data:
                del self.data[key]
            return None
        
        return value
    
    # ==================== STAGE 3: Point-in-Time Operations ====================
    
    def set_with_history(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Stage 3: Set operation that maintains history for point-in-time queries."""
        current_time = time.time()
        
        # Create a new record
        record = Record(value=value, timestamp=current_time, ttl=ttl)
        
        # Add to history (maintaining sorted order by timestamp)
        self.history[key].add(record)
        
        # Update current data structures for backward compatibility
        self.ttl_data[key] = (value, current_time, ttl)
        self.data[key] = value
        
        # Remove from deleted keys if it was deleted
        if key in self.deleted_keys:
            self.deleted_keys.remove(key)
    
    def get_at_time(self, key: str, timestamp: float) -> Optional[Any]:
        """Stage 3: Get the value of a key at a specific timestamp using binary search."""
        if key not in self.history:
            return None
        
        records = self.history[key]
        
        if not records:
            return None
        
        # Use binary search to find the latest record at or before the given timestamp
        # bisect_key_right finds the insertion point by comparing with the key (timestamp)
        # The record we want is at index - 1 (if it exists)
        index = records.bisect_key_right(timestamp)
        
        if index == 0:
            # No record at or before the given timestamp
            return None
        
        # Get the latest record at or before the timestamp
        latest_record : Record = records[index - 1]
        
        # Check if the record is valid at the query time
        if latest_record.is_valid_at_time(timestamp):
            return latest_record.value
        
        return None
    
    def get_current_with_history(self, key: str) -> Optional[Any]:
        """Stage 3: Get current value using history-based approach."""
        current_time = time.time()
        return self.get_at_time(key, current_time)
    
    # ==================== STAGE 4: Deletion Operations ====================
    
    def delete(self, key: str) -> bool:
        """Stage 4: Delete a key from the database."""
        current_time = time.time()
        
        # Check if key exists and is not already deleted
        if key in self.deleted_keys:
            return False
        
        # Check if key exists and is not expired (use exists method which handles TTL)
        if not self.exists(key):
            return False
        
        # Mark as deleted
        self.deleted_keys.add(key)
        
        # Add deletion record to history
        deletion_record = Record(value=None, timestamp=current_time, deleted=True)
        self.history[key].add(deletion_record)
        
        # Remove from current data structures
        if key in self.data:
            del self.data[key]
        if key in self.ttl_data:
            del self.ttl_data[key]
        
        return True
    
    def exists(self, key: str) -> bool:
        """Check if a key exists and is not deleted or expired."""
        if key in self.deleted_keys:
            return False
        
        # Check TTL-aware existence
        value = self.get_with_ttl(key)
        return value is not None
    
    # ==================== UNIFIED INTERFACE ====================
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Unified set method that works for all stages."""
        self.set_with_history(key, value, ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Unified get method that respects deletion and TTL."""
        if key in self.deleted_keys:
            return None
        return self.get_current_with_history(key)
    
    # ==================== UTILITY METHODS ====================
    
    def cleanup_expired(self) -> None:
        """Remove all expired keys from the database."""
        current_time = time.time()
        expired_keys = []
        
        for key, (value, timestamp, ttl) in self.ttl_data.items():
            if ttl is not None and current_time > timestamp + ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.ttl_data:
                del self.ttl_data[key]
            if key in self.data:
                del self.data[key]
    
    def get_all_keys(self) -> List[str]:
        """Get all non-deleted, non-expired keys."""
        keys = []
        for key in set(self.data.keys()) | set(self.ttl_data.keys()) | set(self.history.keys()):
            if self.exists(key):
                keys.append(key)
        return keys
    
    def size(self) -> int:
        """Get the number of valid keys in the database."""
        return len(self.get_all_keys())
    
    def clear(self) -> None:
        """Clear all data from the database."""
        self.data.clear()
        self.ttl_data.clear()
        self.history.clear()
        self.deleted_keys.clear() 