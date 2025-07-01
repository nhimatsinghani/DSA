#!/usr/bin/env python3
"""
Cloud-Based File Storage System

A multi-level implementation of a cloud storage system that evolves through 3 stages:
Level 1: Basic file manipulation (add, get_size, delete)
Level 2: File retrieval with prefix filtering and sorting
Level 3: User management with storage capacity limits and account merging

This implementation is designed for technical interview preparation.
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import heapq
from collections import defaultdict


@dataclass
class FileInfo:
    """Represents a file in the storage system."""
    name: str
    size: int
    owner: Optional[str] = None  # For Level 3: user ownership
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, FileInfo):
            return False
        return self.name == other.name


@dataclass
class User:
    """Represents a user in the storage system."""
    user_id: str
    capacity: int
    used_storage: int = 0
    files: Set[str] = None
    
    def __post_init__(self):
        if self.files is None:
            self.files = set()
    
    def can_add_file(self, size: int) -> bool:
        """Check if user has enough capacity to add a file."""
        return self.used_storage + size <= self.capacity
    
    def add_file_usage(self, name: str, size: int) -> bool:
        """Add file to user's storage usage."""
        if not self.can_add_file(size):
            return False
        self.used_storage += size
        self.files.add(name)
        return True
    
    def remove_file_usage(self, name: str, size: int) -> bool:
        """Remove file from user's storage usage."""
        if name not in self.files:
            return False
        self.used_storage -= size
        self.files.remove(name)
        return True
    
    def get_remaining_capacity(self) -> int:
        """Get remaining storage capacity."""
        return self.capacity - self.used_storage


class CloudFileStorage:
    """
    Cloud-based file storage system supporting:
    - Basic file operations (Level 1)
    - Prefix-based file querying (Level 2)  
    - User management with capacity limits (Level 3)
    """
    
    def __init__(self):
        # Level 1: Basic file storage
        self.files: Dict[str, FileInfo] = {}
        
        # Level 2: Efficient prefix querying
        self.files_by_prefix: Dict[str, Set[str]] = defaultdict(set)
        
        # Level 3: User management
        self.users: Dict[str, User] = {}
        self.admin_user_id = "admin"  # Special admin user with unlimited capacity
        
        # Initialize admin user
        self.users[self.admin_user_id] = User(self.admin_user_id, float('inf'))
    
    # ==================== LEVEL 1: Basic File Operations ====================
    
    def add_file(self, name: str, size: int) -> bool:
        """
        Level 1: Add a new file to the storage.
        
        Args:
            name: File name
            size: File size in bytes
            
        Returns:
            True if file was added successfully, False if file already exists
        """
        if name in self.files:
            return False
        
        # Create file owned by admin (for Level 1 compatibility)
        file_info = FileInfo(name=name, size=size, owner=self.admin_user_id)
        
        # Add to storage
        self.files[name] = file_info
        
        # Update admin user's storage
        self.users[self.admin_user_id].add_file_usage(name, size)
        
        # Update prefix index for Level 2
        self._update_prefix_index(name, add=True)
        
        return True
    
    def get_file_size(self, name: str) -> Optional[int]:
        """
        Level 1: Get the size of a file.
        
        Args:
            name: File name
            
        Returns:
            File size if file exists, None otherwise
        """
        file_info = self.files.get(name)
        return file_info.size if file_info else None
    
    def delete_file(self, name: str) -> Optional[int]:
        """
        Level 1: Delete a file from storage.
        
        Args:
            name: File name
            
        Returns:
            Deleted file size if successful, None if file doesn't exist
        """
        if name not in self.files:
            return None
        
        file_info = self.files[name]
        size = file_info.size
        owner = file_info.owner
        
        # Remove from storage
        del self.files[name]
        
        # Update owner's storage usage
        if owner and owner in self.users:
            self.users[owner].remove_file_usage(name, size)
        
        # Update prefix index
        self._update_prefix_index(name, add=False)
        
        return size
    
    # ==================== LEVEL 2: Prefix-based Querying ====================
    
    def get_n_largest(self, prefix: str, n: int) -> List[str]:
        """
        Level 2: Get the n largest files with names starting with prefix.
        
        Args:
            prefix: Filename prefix to filter by
            n: Number of files to return
            
        Returns:
            List of filenames sorted by size (descending), then lexicographically.
            Returns empty list if no files match or n <= 0.
        """
        if n <= 0:
            return []
        
        # Optimization 1: Use prefix index for efficient prefix matching
        # Since files_by_prefix stores all prefixes of each filename,
        # we can directly look up files that start with the given prefix
        if prefix in self.files_by_prefix:
            matching_file_names = self.files_by_prefix[prefix].copy()
        else:
            # Fallback: prefix not in index, check all files manually
            matching_file_names = set()
            for file_name in self.files:
                if file_name.startswith(prefix):
                    matching_file_names.add(file_name)
        
        # Optimization 2: Use min heap to efficiently get top n largest files
        # This is O(m log n) instead of O(m log m) where m = matching files
        if len(matching_file_names) <= n:
            # If we have n or fewer files, just sort them all
            matching_files = []
            for file_name in matching_file_names:
                if file_name in self.files:  # Safety check
                    file_info = self.files[file_name]
                    matching_files.append((file_info.size, file_name))
            
            # Sort by size (descending), then by name (ascending)
            matching_files.sort(key=lambda x: (-x[0], x[1]))
            return [name for _, name in matching_files]
        
        else:
            # Use min heap for efficient top-n selection
            # Time complexity: O(m log n) instead of O(m log m)
            
            # Min heap to store (size, name) tuples
            # We'll maintain exactly n elements in the heap
            heap = []
            
            for file_name in matching_file_names:
                if file_name in self.files:  # Safety check
                    file_info = self.files[file_name]
                    file_size = file_info.size
                    
                    if len(heap) < n:
                        # Heap not full, add the file
                        # Note: we negate size for max heap behavior with min heap
                        heapq.heappush(heap, (file_size, file_name))
                    elif file_size > heap[0][0]:
                        # Current file is larger than smallest in heap
                        # Replace the smallest
                        heapq.heapreplace(heap, (file_size, file_name))
            
            # Extract all files from heap and sort them properly
            result_files = []
            while heap:
                size, name = heapq.heappop(heap)
                result_files.append((size, name))
            
            # Sort by size (descending), then by name (ascending)
            result_files.sort(key=lambda x: (-x[0], x[1]))
            
            return [name for _, name in result_files]
    
    def _update_prefix_index(self, name: str, add: bool):
        """Update the prefix index for efficient querying."""
        # Generate all prefixes of the filename
        for i in range(1, len(name) + 1):
            prefix = name[:i]
            if add:
                self.files_by_prefix[prefix].add(name)
            else:
                self.files_by_prefix[prefix].discard(name)
                # Clean up empty prefix sets
                if not self.files_by_prefix[prefix]:
                    del self.files_by_prefix[prefix]
    
    # ==================== LEVEL 3: User Management ====================
    
    def add_user(self, user_id: str, capacity: int) -> bool:
        """
        Level 3: Add a new user with storage capacity limit.
        
        Args:
            user_id: Unique user identifier
            capacity: Storage capacity in bytes
            
        Returns:
            True if user was created successfully, False if user already exists
        """
        if user_id in self.users:
            return False
        
        self.users[user_id] = User(user_id=user_id, capacity=capacity)
        return True
    
    def add_file_by(self, user_id: str, name: str, size: int) -> Optional[int]:
        """
        Level 3: Add a file owned by a specific user.
        
        Args:
            user_id: User who will own the file
            name: File name
            size: File size in bytes
            
        Returns:
            Remaining capacity of user after adding file, or None if operation failed
        """
        # Check if user exists
        if user_id not in self.users:
            return None
        
        # Check if file already exists
        if name in self.files:
            return None
        
        user = self.users[user_id]
        
        # Check capacity (except for admin)
        if user_id != self.admin_user_id and not user.can_add_file(size):
            return None
        
        # Add the file
        file_info = FileInfo(name=name, size=size, owner=user_id)
        self.files[name] = file_info
        
        # Update user's storage usage
        user.add_file_usage(name, size)
        
        # Update prefix index
        self._update_prefix_index(name, add=True)
        
        return user.get_remaining_capacity()
    
    def merge_user(self, user_id_1: str, user_id_2: str) -> Optional[int]:
        """
        Level 3: Merge two user accounts.
        
        Transfers ownership of user_id_2's files to user_id_1.
        Deletes user_id_2 after successful merge.
        
        Args:
            user_id_1: Target user (will receive all files)
            user_id_2: Source user (will be deleted after merge)
            
        Returns:
            Remaining capacity of user_id_1 after merge, or None if operation failed
        """
        # Validation checks
        if user_id_1 not in self.users or user_id_2 not in self.users:
            return None
        
        if user_id_1 == user_id_2:
            return None
        
        # Don't allow merging with admin unless both are admin-equivalent
        if user_id_1 == self.admin_user_id or user_id_2 == self.admin_user_id:
            if user_id_1 != self.admin_user_id and user_id_2 != self.admin_user_id:
                return None
        
        user1 = self.users[user_id_1]
        user2 = self.users[user_id_2]
        
        # Check if user1 has enough capacity for all of user2's files
        if user_id_1 != self.admin_user_id:
            required_capacity = user1.used_storage + user2.used_storage
            if required_capacity > user1.capacity:
                return None
        
        # Transfer all files from user2 to user1
        files_to_transfer = list(user2.files)
        for file_name in files_to_transfer:
            if file_name in self.files:
                # Update file ownership
                self.files[file_name].owner = user_id_1
                
                # Update user storage tracking
                file_size = self.files[file_name].size
                user2.remove_file_usage(file_name, file_size)
                user1.add_file_usage(file_name, file_size)
        
        # Add user2's remaining capacity to user1's total capacity
        user1.capacity += user2.get_remaining_capacity()
        
        # Delete user2
        del self.users[user_id_2]
        
        return user1.get_remaining_capacity()
    
    # ==================== UTILITY METHODS ====================
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get detailed information about a user."""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        return {
            'user_id': user.user_id,
            'capacity': user.capacity,
            'used_storage': user.used_storage,
            'remaining_capacity': user.get_remaining_capacity(),
            'file_count': len(user.files),
            'files': list(user.files)
        }
    
    def get_storage_stats(self) -> Dict:
        """Get overall storage system statistics."""
        total_files = len(self.files)
        total_size = sum(file_info.size for file_info in self.files.values())
        total_users = len(self.users)
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_users': total_users,
            'average_file_size': total_size / total_files if total_files > 0 else 0
        }
    
    def list_files_by_user(self, user_id: str) -> List[Tuple[str, int]]:
        """List all files owned by a specific user."""
        if user_id not in self.users:
            return []
        
        user_files = []
        for file_name in self.users[user_id].files:
            if file_name in self.files:
                file_info = self.files[file_name]
                user_files.append((file_name, file_info.size))
        
        return sorted(user_files, key=lambda x: x[0])  # Sort by filename
    
    def get_largest_files(self, n: int = 10) -> List[Tuple[str, int, str]]:
        """Get the n largest files in the system."""
        all_files = []
        for file_info in self.files.values():
            all_files.append((file_info.name, file_info.size, file_info.owner))
        
        # Sort by size (descending)
        all_files.sort(key=lambda x: -x[1])
        
        return all_files[:n]
    
    def clear_storage(self):
        """Clear all files and users (except admin)."""
        self.files.clear()
        self.files_by_prefix.clear()
        
        # Keep only admin user
        admin = self.users[self.admin_user_id]
        self.users.clear()
        self.users[self.admin_user_id] = User(self.admin_user_id, float('inf'))
    
    def validate_system_integrity(self) -> List[str]:
        """Validate system integrity and return any issues found."""
        issues = []
        
        # Check file ownership consistency
        for file_name, file_info in self.files.items():
            owner = file_info.owner
            if owner and owner in self.users:
                if file_name not in self.users[owner].files:
                    issues.append(f"File {file_name} not in owner {owner}'s file list")
            else:
                issues.append(f"File {file_name} has invalid owner {owner}")
        
        # Check user storage consistency
        for user_id, user in self.users.items():
            calculated_usage = 0
            for file_name in user.files:
                if file_name in self.files:
                    calculated_usage += self.files[file_name].size
                else:
                    issues.append(f"User {user_id} references non-existent file {file_name}")
            
            if calculated_usage != user.used_storage:
                issues.append(f"User {user_id} storage mismatch: calculated={calculated_usage}, recorded={user.used_storage}")
        
        return issues 