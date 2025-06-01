"""
Bloom Filter: Probabilistic Set Membership Data Structure

A Bloom filter is a space-efficient probabilistic data structure that tests 
whether an element is a member of a set. It can have false positives but never 
false negatives.

MATHEMATICAL FOUNDATION:
1. Bit Array: m bits, initially all 0
2. Hash Functions: k independent hash functions
3. False Positive Rate: P(fp) = (1 - e^(-kn/m))^k
4. Optimal Hash Functions: k = (m/n) × ln(2)
5. Space Requirement: m = -n × ln(p) / (ln(2))²

ALGORITHM:
1. Add(x): Set bits at h₁(x), h₂(x), ..., hₖ(x) to 1
2. Query(x): Check if ALL bits at h₁(x), h₂(x), ..., hₖ(x) are 1
3. If any bit is 0 → definitely NOT in set
4. If all bits are 1 → POSSIBLY in set

APPLICATIONS:
- Web caching (avoid cache misses)
- Database query optimization
- Network routing (blacklist checking)
- Distributed systems (membership testing)
"""

import hashlib
import math
import array
from typing import Any, List, Tuple, Dict, Union


class BloomFilter:
    """
    Bloom Filter implementation with detailed educational features.
    
    This implementation provides insights into the internal workings,
    mathematical calculations, and performance characteristics.
    """
    
    def __init__(self, capacity: int = 1000, error_rate: float = 0.01, 
                 num_hash_functions: int = None, bit_array_size: int = None):
        """
        Initialize Bloom Filter with optimal or custom parameters.
        
        Args:
            capacity: Expected number of elements
            error_rate: Desired false positive rate (0 < error_rate < 1)
            num_hash_functions: Number of hash functions (auto-calculated if None)
            bit_array_size: Size of bit array (auto-calculated if None)
            
        Mathematical Calculations:
        - If auto-calculating: m = -n × ln(p) / (ln(2))²
        - If auto-calculating: k = (m/n) × ln(2)
        """
        if not 0 < error_rate < 1:
            raise ValueError("Error rate must be between 0 and 1")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
            
        self.capacity = capacity
        self.desired_error_rate = error_rate
        
        # Calculate optimal parameters if not provided
        if bit_array_size is None:
            # m = -n × ln(p) / (ln(2))²
            self.bit_array_size = int(-capacity * math.log(error_rate) / (math.log(2) ** 2))
        else:
            self.bit_array_size = bit_array_size
            
        if num_hash_functions is None:
            # k = (m/n) × ln(2)
            self.num_hash_functions = int((self.bit_array_size / capacity) * math.log(2))
            # Ensure at least 1 hash function
            self.num_hash_functions = max(1, self.num_hash_functions)
        else:
            self.num_hash_functions = num_hash_functions
            
        # Initialize bit array (using array.array for memory efficiency)
        # Each element is 1 byte, we'll use bit operations
        self.bit_array = array.array('B', [0] * ((self.bit_array_size + 7) // 8))
        
        # Statistics for analysis
        self.elements_added = 0
        self.false_positive_tests = 0
        self.true_positive_tests = 0
        self.negative_tests = 0
        
        # For educational purposes - store added elements (in real use, this defeats the purpose!)
        self.actual_elements = set()  # Only for verification in tests
        
        # Calculate theoretical performance
        self.theoretical_fp_rate = self._calculate_theoretical_fp_rate()
        
    def _calculate_theoretical_fp_rate(self) -> float:
        """Calculate theoretical false positive rate."""
        if self.elements_added == 0:
            return 0.0
        # P(fp) = (1 - e^(-kn/m))^k
        return (1 - math.exp(-self.num_hash_functions * self.elements_added / self.bit_array_size)) ** self.num_hash_functions
    
    def _hash_functions(self, item: Any) -> List[int]:
        """
        Generate k hash values for an item using double hashing.
        
        Double hashing technique: h_i(x) = (h1(x) + i × h2(x)) mod m
        This gives us k different hash functions from just 2 base hash functions.
        
        Args:
            item: Item to hash
            
        Returns:
            List of k hash values (bit positions)
        """
        # Convert item to bytes
        if isinstance(item, str):
            data = item.encode('utf-8')
        elif isinstance(item, (int, float)):
            data = str(item).encode('utf-8')
        else:
            data = str(item).encode('utf-8')
        
        # Generate two independent hash values
        hash1 = int(hashlib.md5(data).hexdigest(), 16)
        hash2 = int(hashlib.sha1(data).hexdigest(), 16)
        
        # Generate k hash functions using double hashing
        hash_values = []
        for i in range(self.num_hash_functions):
            # h_i(x) = (h1(x) + i × h2(x)) mod m
            hash_val = (hash1 + i * hash2) % self.bit_array_size
            hash_values.append(hash_val)
            
        return hash_values
    
    def _set_bit(self, position: int) -> bool:
        """
        Set bit at given position to 1.
        
        Args:
            position: Bit position to set
            
        Returns:
            True if bit was previously 0, False if already 1
        """
        byte_index = position // 8
        bit_offset = position % 8
        
        # Check if bit was already set
        was_zero = (self.bit_array[byte_index] & (1 << bit_offset)) == 0
        
        # Set the bit
        self.bit_array[byte_index] |= (1 << bit_offset)
        
        return was_zero
    
    def _get_bit(self, position: int) -> bool:
        """
        Get bit value at given position.
        
        Args:
            position: Bit position to check
            
        Returns:
            True if bit is 1, False if bit is 0
        """
        byte_index = position // 8
        bit_offset = position % 8
        
        return (self.bit_array[byte_index] & (1 << bit_offset)) != 0
    
    def add(self, item: Any) -> Dict[str, Any]:
        """
        Add an item to the Bloom filter.
        
        Args:
            item: Item to add
            
        Returns:
            Dictionary with detailed information about the operation
        """
        # Get hash positions
        hash_positions = self._hash_functions(item)
        
        # Track which bits were newly set
        newly_set_bits = []
        already_set_bits = []
        
        # Set bits at hash positions
        for position in hash_positions:
            was_zero = self._set_bit(position)
            if was_zero:
                newly_set_bits.append(position)
            else:
                already_set_bits.append(position)
        
        # Update statistics
        self.elements_added += 1
        self.actual_elements.add(item)  # For educational purposes only
        
        # Update theoretical false positive rate
        self.theoretical_fp_rate = self._calculate_theoretical_fp_rate()
        
        return {
            'item': item,
            'hash_positions': hash_positions,
            'newly_set_bits': newly_set_bits,
            'already_set_bits': already_set_bits,
            'total_bits_set': len(newly_set_bits),
            'bits_already_set': len(already_set_bits),
            'elements_added': self.elements_added,
            'theoretical_fp_rate': self.theoretical_fp_rate,
            'fill_ratio': self._get_fill_ratio()
        }
    
    def query(self, item: Any) -> Dict[str, Any]:
        """
        Check if an item might be in the set.
        
        Args:
            item: Item to check
            
        Returns:
            Dictionary with detailed query results
        """
        # Get hash positions
        hash_positions = self._hash_functions(item)
        
        # Check if all bits are set
        bit_values = []
        all_bits_set = True
        
        for position in hash_positions:
            bit_set = self._get_bit(position)
            bit_values.append(bit_set)
            if not bit_set:
                all_bits_set = False
        
        # Determine result
        if all_bits_set:
            result = "POSSIBLY_IN_SET"
            # Check if it's actually in the set (for educational analysis)
            if item in self.actual_elements:
                self.true_positive_tests += 1
                actual_result = "TRUE_POSITIVE"
            else:
                self.false_positive_tests += 1
                actual_result = "FALSE_POSITIVE"
        else:
            result = "DEFINITELY_NOT_IN_SET"
            self.negative_tests += 1
            actual_result = "TRUE_NEGATIVE"
        
        return {
            'item': item,
            'result': result,
            'actual_result': actual_result,  # For educational purposes
            'hash_positions': hash_positions,
            'bit_values': bit_values,
            'all_bits_set': all_bits_set,
            'theoretical_fp_rate': self.theoretical_fp_rate,
            'query_statistics': {
                'true_positives': self.true_positive_tests,
                'false_positives': self.false_positive_tests,
                'true_negatives': self.negative_tests
            }
        }
    
    def _get_fill_ratio(self) -> float:
        """Calculate the ratio of bits set to 1."""
        total_bits = self.bit_array_size
        bits_set = sum(bin(byte).count('1') for byte in self.bit_array)
        return bits_set / total_bits if total_bits > 0 else 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the Bloom filter.
        
        Returns:
            Dictionary with performance metrics and analysis
        """
        fill_ratio = self._get_fill_ratio()
        actual_fp_rate = 0.0
        
        total_positive_tests = self.true_positive_tests + self.false_positive_tests
        if total_positive_tests > 0:
            actual_fp_rate = self.false_positive_tests / total_positive_tests
        
        # Calculate efficiency metrics
        memory_per_element = self.bit_array_size / max(1, self.elements_added)
        bits_per_element = self.bit_array_size / max(1, self.capacity)
        
        return {
            'configuration': {
                'capacity': self.capacity,
                'desired_error_rate': self.desired_error_rate,
                'bit_array_size': self.bit_array_size,
                'num_hash_functions': self.num_hash_functions,
                'memory_bytes': len(self.bit_array),
                'bits_per_element': bits_per_element
            },
            'performance': {
                'elements_added': self.elements_added,
                'fill_ratio': fill_ratio,
                'theoretical_fp_rate': self.theoretical_fp_rate,
                'actual_fp_rate': actual_fp_rate,
                'memory_per_element_bits': memory_per_element,
                'load_factor': self.elements_added / self.capacity if self.capacity > 0 else 0
            },
            'test_statistics': {
                'true_positives': self.true_positive_tests,
                'false_positives': self.false_positive_tests,
                'true_negatives': self.negative_tests,
                'total_queries': self.true_positive_tests + self.false_positive_tests + self.negative_tests
            },
            'mathematical_analysis': {
                'optimal_k_formula': f"k = (m/n) × ln(2) = ({self.bit_array_size}/{self.capacity}) × ln(2) ≈ {(self.bit_array_size/self.capacity) * math.log(2):.2f}",
                'actual_k': self.num_hash_functions,
                'fp_rate_formula': f"P(fp) = (1 - e^(-kn/m))^k",
                'space_efficiency': f"{self.bit_array_size / (self.capacity * 64):.3f}x vs 64-bit integers"
            }
        }
    
    def optimize_for_capacity(self, new_capacity: int) -> 'BloomFilter':
        """
        Create a new optimized Bloom filter for different capacity.
        
        Args:
            new_capacity: New expected capacity
            
        Returns:
            New optimized BloomFilter instance
        """
        return BloomFilter(capacity=new_capacity, error_rate=self.desired_error_rate)
    
    def union(self, other: 'BloomFilter') -> 'BloomFilter':
        """
        Create union of two Bloom filters (OR operation).
        
        Note: Only works if both filters have same size and hash functions.
        
        Args:
            other: Another BloomFilter
            
        Returns:
            New BloomFilter containing union
        """
        if (self.bit_array_size != other.bit_array_size or 
            self.num_hash_functions != other.num_hash_functions):
            raise ValueError("Bloom filters must have same size and hash functions for union")
        
        # Create new filter with same parameters
        union_filter = BloomFilter(
            capacity=max(self.capacity, other.capacity),
            error_rate=min(self.desired_error_rate, other.desired_error_rate),
            num_hash_functions=self.num_hash_functions,
            bit_array_size=self.bit_array_size
        )
        
        # Perform bitwise OR
        for i in range(len(self.bit_array)):
            union_filter.bit_array[i] = self.bit_array[i] | other.bit_array[i]
        
        # Update statistics (approximation)
        union_filter.elements_added = self.elements_added + other.elements_added
        union_filter.actual_elements = self.actual_elements | other.actual_elements
        union_filter.theoretical_fp_rate = union_filter._calculate_theoretical_fp_rate()
        
        return union_filter
    
    def intersection_estimate(self, other: 'BloomFilter') -> Dict[str, Any]:
        """
        Estimate intersection cardinality using Bloom filter properties.
        
        Note: This is an approximation and can be inaccurate.
        
        Args:
            other: Another BloomFilter
            
        Returns:
            Dictionary with intersection analysis
        """
        if (self.bit_array_size != other.bit_array_size or 
            self.num_hash_functions != other.num_hash_functions):
            raise ValueError("Bloom filters must have same parameters for intersection")
        
        # Count bits set in intersection (AND operation)
        intersection_bits = 0
        for i in range(len(self.bit_array)):
            intersection_bits += bin(self.bit_array[i] & other.bit_array[i]).count('1')
        
        # Estimate cardinality using inclusion-exclusion principle
        # This is a rough approximation
        fill_ratio_intersection = intersection_bits / self.bit_array_size
        
        # Rough estimate (not mathematically rigorous)
        if fill_ratio_intersection > 0:
            estimated_intersection = -self.bit_array_size * math.log(1 - fill_ratio_intersection) / self.num_hash_functions
        else:
            estimated_intersection = 0
        
        return {
            'estimated_intersection_size': max(0, int(estimated_intersection)),
            'intersection_fill_ratio': fill_ratio_intersection,
            'actual_intersection_size': len(self.actual_elements & other.actual_elements),  # For verification
            'note': 'Intersection estimation is approximate and may be inaccurate'
        }
    
    def reset(self):
        """Reset the Bloom filter to initial state."""
        self.bit_array = array.array('B', [0] * ((self.bit_array_size + 7) // 8))
        self.elements_added = 0
        self.false_positive_tests = 0
        self.true_positive_tests = 0
        self.negative_tests = 0
        self.actual_elements.clear()
        self.theoretical_fp_rate = 0.0
    
    def __contains__(self, item: Any) -> bool:
        """Support 'in' operator for convenient membership testing."""
        result = self.query(item)
        return result['result'] == "POSSIBLY_IN_SET"
    
    def __len__(self) -> int:
        """Return number of elements added (not necessarily unique)."""
        return self.elements_added
    
    def __str__(self) -> str:
        """String representation with key statistics."""
        stats = self.get_statistics()
        return (f"BloomFilter(capacity={self.capacity}, "
                f"error_rate={self.desired_error_rate:.3f}, "
                f"size={self.bit_array_size} bits, "
                f"hash_functions={self.num_hash_functions}, "
                f"elements={self.elements_added}, "
                f"fill_ratio={stats['performance']['fill_ratio']:.3f})") 