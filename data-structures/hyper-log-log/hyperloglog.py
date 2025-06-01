"""
HyperLogLog: Probabilistic Cardinality Estimation Data Structure

HyperLogLog is a probabilistic data structure that estimates the cardinality 
(number of distinct elements) of very large multisets using a small, fixed amount of memory.

MATHEMATICAL FOUNDATION:
1. Hash Uniformity: Uses a hash function to uniformly distribute input elements
2. Leading Zeros Analysis: The probability of k leading zeros in a random binary 
   string is 2^(-k-1)
3. Maximum Leading Zeros: If we observe a maximum of k leading zeros among n 
   distinct elements, we can estimate n ≈ 2^k
4. Variance Reduction: Uses multiple buckets (2^b buckets where b is precision)
   and harmonic mean to reduce variance

ALGORITHM STEPS:
1. Hash the input element
2. Use first 'b' bits to determine bucket index
3. Count leading zeros in remaining bits (this gives the rank)
4. Store maximum rank seen for each bucket
5. Estimate cardinality using harmonic mean of 2^rank across all buckets

ERROR ANALYSIS:
- Standard error: σ = 1.04/√m where m = 2^b (number of buckets)
- For b=10 (1024 buckets): error ≈ 3.25%
- For b=16 (65536 buckets): error ≈ 0.41%
"""

import hashlib
import math
from typing import Union, Any


class HyperLogLog:
    """
    HyperLogLog probabilistic cardinality estimator.
    
    This implementation provides detailed insights into the internal workings
    of the HyperLogLog algorithm, including step-by-step calculations.
    """
    
    # Bias correction constants for different precision values
    # These are empirically derived constants that improve accuracy
    BIAS_CORRECTION = {
        4: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        # Add more as needed - simplified for demonstration
    }
    
    def __init__(self, precision: int = 10):
        """
        Initialize HyperLogLog with given precision.
        
        Args:
            precision (int): Number of bits used for bucketing (4-16 recommended)
                           Higher precision = more accuracy but more memory
                           
        Mathematical Impact:
        - Number of buckets = 2^precision
        - Memory usage = buckets * log2(64-precision) bits ≈ buckets * 6 bits
        - Standard error ≈ 1.04/√(2^precision)
        """
        if not 4 <= precision <= 16:
            raise ValueError("Precision should be between 4 and 16")
            
        self.precision = precision
        self.bucket_count = 2 ** precision
        self.bucket_mask = self.bucket_count - 1  # For efficient bucket selection
        
        # Initialize buckets to store maximum leading zeros (ranks) seen
        self.buckets = [0] * self.bucket_count
        
        # Alpha constant for bias correction in harmonic mean
        # This constant is derived from theoretical analysis
        if self.bucket_count >= 128:
            self.alpha = 0.7213 / (1 + 1.079 / self.bucket_count)
        elif self.bucket_count >= 64:
            self.alpha = 0.709
        elif self.bucket_count >= 32:
            self.alpha = 0.697
        else:
            self.alpha = 0.5
            
        # Statistics for analysis
        self.elements_added = 0
        self.unique_hashes_seen = set()  # For debugging only
    
    def _hash(self, item: Any) -> int:
        """
        Hash function that converts input to uniform 64-bit integer.
        
        Uses SHA-1 for good distribution properties.
        Returns the first 64 bits as an integer.
        """
        if isinstance(item, str):
            item = item.encode('utf-8')
        elif not isinstance(item, (bytes, bytearray)):
            item = str(item).encode('utf-8')
            
        hash_digest = hashlib.sha1(item).digest()
        # Take first 8 bytes and convert to integer
        hash_int = int.from_bytes(hash_digest[:8], byteorder='big')
        return hash_int
    
    def _leading_zeros(self, value: int, max_bits: int = 64) -> int:
        """
        Count leading zeros in binary representation.
        
        This is the core mathematical operation that enables cardinality estimation.
        The probability of seeing k leading zeros is 2^(-k-1), which allows us
        to estimate how many unique values we've seen.
        
        Args:
            value: Integer to count leading zeros for
            max_bits: Maximum number of bits to consider
            
        Returns:
            Number of leading zeros + 1 (the rank)
        """
        if value == 0:
            return max_bits + 1
            
        # Count leading zeros using bit operations
        leading_zeros = 0
        for i in range(max_bits - 1, -1, -1):
            if (value >> i) & 1:
                break
            leading_zeros += 1
            
        return leading_zeros + 1  # Add 1 to get the rank
    
    def add(self, item: Any) -> dict:
        """
        Add an element to the HyperLogLog structure.
        
        Returns detailed information about the internal processing for educational purposes.
        
        Args:
            item: Element to add (will be hashed)
            
        Returns:
            Dictionary with detailed step-by-step information
        """
        self.elements_added += 1
        
        # Step 1: Hash the input
        hash_value = self._hash(item)
        self.unique_hashes_seen.add(hash_value)
        
        # Step 2: Extract bucket index from first 'precision' bits
        bucket_index = hash_value & self.bucket_mask
        
        # Step 3: Get remaining bits for leading zero count
        remaining_bits = hash_value >> self.precision
        remaining_bit_count = 64 - self.precision
        
        # Step 4: Count leading zeros in remaining bits (this is the rank)
        rank = self._leading_zeros(remaining_bits, remaining_bit_count)
        
        # Step 5: Update bucket with maximum rank seen
        old_rank = self.buckets[bucket_index]
        self.buckets[bucket_index] = max(self.buckets[bucket_index], rank)
        
        # Return detailed information for educational purposes
        return {
            'item': item,
            'hash_value': f"0x{hash_value:016x}",
            'hash_binary': f"{hash_value:064b}",
            'bucket_bits': f"{bucket_index:0{self.precision}b}",
            'bucket_index': bucket_index,
            'remaining_bits': f"0x{remaining_bits:0{(remaining_bit_count+3)//4}x}",
            'remaining_binary': f"{remaining_bits:0{remaining_bit_count}b}",
            'rank': rank,
            'old_bucket_rank': old_rank,
            'new_bucket_rank': self.buckets[bucket_index],
            'bucket_updated': rank > old_rank
        }
    
    def estimate_cardinality(self) -> dict:
        """
        Estimate the cardinality using the HyperLogLog algorithm.
        
        Returns detailed breakdown of the calculation process.
        
        Mathematical Process:
        1. Calculate raw estimate using harmonic mean: α * m² / Σ(2^(-bucket_rank))
        2. Apply small range correction if estimate is small
        3. Apply large range correction if estimate is large
        4. Apply bias correction based on empirical data
        """
        # Step 1: Calculate raw estimate using harmonic mean
        raw_sum = sum(2 ** (-rank) for rank in self.buckets)
        raw_estimate = self.alpha * (self.bucket_count ** 2) / raw_sum
        
        # Step 2: Apply small range correction
        # When estimate is small, many buckets will be 0, causing bias
        zero_buckets = self.buckets.count(0)
        if raw_estimate <= 2.5 * self.bucket_count and zero_buckets > 0:
            small_range_estimate = self.bucket_count * math.log(self.bucket_count / zero_buckets)
        else:
            small_range_estimate = raw_estimate
            
        # Step 3: Apply large range correction
        # For very large cardinalities, hash collisions become significant
        if raw_estimate <= (1.0/30.0) * (2**32):
            final_estimate = small_range_estimate
        else:
            # Large range correction formula
            final_estimate = -1 * (2**32) * math.log(1 - raw_estimate / (2**32))
        
        # Calculate statistics
        non_zero_buckets = self.bucket_count - zero_buckets
        max_rank = max(self.buckets) if self.buckets else 0
        avg_rank = sum(self.buckets) / len(self.buckets)
        
        # Theoretical error bound
        theoretical_error = 1.04 / math.sqrt(self.bucket_count)
        
        return {
            'estimated_cardinality': int(final_estimate),
            'raw_estimate': raw_estimate,
            'small_range_estimate': small_range_estimate,
            'final_estimate': final_estimate,
            'calculation_details': {
                'alpha': self.alpha,
                'bucket_count': self.bucket_count,
                'raw_sum': raw_sum,
                'zero_buckets': zero_buckets,
                'non_zero_buckets': non_zero_buckets,
                'max_rank': max_rank,
                'avg_rank': avg_rank,
                'harmonic_mean_formula': f'{self.alpha} * {self.bucket_count}² / {raw_sum}',
                'theoretical_error_rate': f'{theoretical_error:.4f} ({theoretical_error*100:.2f}%)'
            },
            'bucket_distribution': {
                f'rank_{i}': self.buckets.count(i) for i in range(max_rank + 1)
            }
        }
    
    def get_bucket_analysis(self) -> dict:
        """
        Analyze the distribution of ranks across buckets.
        
        Useful for understanding how the algorithm distributes data
        and verifying that the hash function provides good uniformity.
        """
        rank_distribution = {}
        for rank in self.buckets:
            rank_distribution[rank] = rank_distribution.get(rank, 0) + 1
        
        return {
            'bucket_count': self.bucket_count,
            'precision': self.precision,
            'elements_added': self.elements_added,
            'unique_hashes': len(self.unique_hashes_seen),
            'rank_distribution': rank_distribution,
            'bucket_utilization': (self.bucket_count - self.buckets.count(0)) / self.bucket_count,
            'max_rank': max(self.buckets) if self.buckets else 0,
            'min_rank': min(self.buckets) if self.buckets else 0,
            'avg_rank': sum(self.buckets) / len(self.buckets),
            'memory_usage_bits': self.bucket_count * 6,  # Approximate
            'memory_usage_bytes': (self.bucket_count * 6) // 8
        }
    
    def merge(self, other: 'HyperLogLog') -> 'HyperLogLog':
        """
        Merge two HyperLogLog structures.
        
        This is done by taking the maximum rank for each bucket,
        which maintains the mathematical properties of the estimator.
        
        Args:
            other: Another HyperLogLog structure with same precision
            
        Returns:
            New merged HyperLogLog structure
        """
        if self.precision != other.precision:
            raise ValueError("Cannot merge HyperLogLog structures with different precisions")
        
        merged = HyperLogLog(self.precision)
        for i in range(self.bucket_count):
            merged.buckets[i] = max(self.buckets[i], other.buckets[i])
        
        return merged
    
    def reset(self):
        """Reset the HyperLogLog structure to initial state."""
        self.buckets = [0] * self.bucket_count
        self.elements_added = 0
        self.unique_hashes_seen.clear()
    
    def __str__(self) -> str:
        """String representation showing key statistics."""
        est = self.estimate_cardinality()
        return (f"HyperLogLog(precision={self.precision}, "
                f"buckets={self.bucket_count}, "
                f"estimated_cardinality={est['estimated_cardinality']}, "
                f"elements_added={self.elements_added})") 