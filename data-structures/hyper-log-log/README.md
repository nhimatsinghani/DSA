# HyperLogLog: Probabilistic Cardinality Estimation

This directory contains a comprehensive Python implementation of the HyperLogLog algorithm with detailed explanations of its mathematical foundations and internal workings.

## 📚 Table of Contents

- [Overview](#overview)
- [Mathematical Foundation](#mathematical-foundation)
- [Algorithm Details](#algorithm-details)
- [Implementation Features](#implementation-features)
- [Usage Examples](#usage-examples)
- [Performance Analysis](#performance-analysis)
- [Testing](#testing)
- [Real-World Applications](#real-world-applications)

## 🔍 Overview

HyperLogLog is a probabilistic data structure designed to estimate the cardinality (number of distinct elements) of very large datasets using minimal memory. It was invented by Philippe Flajolet and his colleagues in 2007.

### Key Characteristics:

- **Space Efficient**: Uses only ~12KB to estimate cardinalities up to billions
- **Mergeable**: Multiple HyperLogLog structures can be combined
- **Fast**: O(1) insertion and estimation time
- **Predictable Error**: Standard error ≈ 1.04/√m where m is number of buckets

## 🧮 Mathematical Foundation

### 1. Hash Function Uniformity

HyperLogLog relies on a uniform hash function that maps input elements to binary strings with uniform probability distribution.

```
h(x) → {0,1}^64  (64-bit binary string)
```

### 2. Leading Zeros Analysis

The core insight is based on the probability of leading zeros in random binary strings:

- **Probability of k leading zeros**: P(leading zeros = k) = 2^(-k-1)
- **Expected maximum leading zeros**: If we see n distinct random values, the maximum number of leading zeros is approximately log₂(n)

### 3. Bucket Division

To reduce variance, the algorithm divides the hash space into m = 2^b buckets:

- First b bits determine bucket index
- Remaining (64-b) bits used for leading zero counting

### 4. Harmonic Mean Estimation

The final estimate uses harmonic mean to combine bucket values:

```
Estimate = α × m² / Σ(2^(-bucket_rank))
```

Where α is a bias correction constant.

### 5. Error Analysis

The standard error is bounded by:

```
σ = 1.04/√m
```

For different precision values:

- b=10 (1024 buckets): σ ≈ 3.25%
- b=12 (4096 buckets): σ ≈ 1.625%
- b=16 (65536 buckets): σ ≈ 0.406%

## ⚙️ Algorithm Details

### Step-by-Step Process:

1. **Hash Input**: Convert element to 64-bit hash

   ```
   hash_value = SHA1(element)[:8]  # First 64 bits
   ```

2. **Extract Bucket**: Use first b bits for bucket index

   ```
   bucket_index = hash_value & (2^b - 1)
   ```

3. **Count Leading Zeros**: In remaining (64-b) bits

   ```
   remaining_bits = hash_value >> b
   rank = leading_zeros(remaining_bits) + 1
   ```

4. **Update Bucket**: Store maximum rank seen

   ```
   buckets[bucket_index] = max(buckets[bucket_index], rank)
   ```

5. **Estimate Cardinality**: Using harmonic mean

   ```
   raw_estimate = α × m² / Σ(2^(-buckets[i]))
   ```

6. **Apply Corrections**: For small/large ranges and bias

### Bias Corrections:

1. **Small Range Correction**: When many buckets are zero

   ```
   if estimate ≤ 2.5m and zeros > 0:
       estimate = m × ln(m/zeros)
   ```

2. **Large Range Correction**: For very large cardinalities
   ```
   if estimate > (1/30) × 2^32:
       estimate = -2^32 × ln(1 - estimate/2^32)
   ```

## 🛠️ Implementation Features

### Core Classes:

- `HyperLogLog`: Main implementation with educational features
- Detailed step-by-step information for learning
- Comprehensive analysis and statistics

### Key Methods:

- `add(item)`: Add element with detailed processing info
- `estimate_cardinality()`: Get estimate with calculation breakdown
- `merge(other)`: Combine two HyperLogLog structures
- `get_bucket_analysis()`: Analyze internal state
- `reset()`: Clear all data

### Educational Features:

- Step-by-step hash processing visualization
- Bucket distribution analysis
- Mathematical calculation breakdown
- Error rate analysis and theoretical bounds

## 💡 Usage Examples

### Basic Usage:

```python
from hyperloglog import HyperLogLog

# Create HyperLogLog with precision 12 (4096 buckets)
hll = HyperLogLog(precision=12)

# Add elements
for i in range(100000):
    hll.add(f"user_{i}")

# Get estimate
estimate = hll.estimate_cardinality()
print(f"Estimated cardinality: {estimate['estimated_cardinality']}")
```

### Detailed Analysis:

```python
# Get detailed processing information
details = hll.add("example_element")
print(f"Hash: {details['hash_value']}")
print(f"Bucket: {details['bucket_index']}")
print(f"Rank: {details['rank']}")

# Analyze bucket distribution
analysis = hll.get_bucket_analysis()
print(f"Bucket utilization: {analysis['bucket_utilization']:.2%}")
print(f"Memory usage: {analysis['memory_usage_bytes']} bytes")
```

### Merging HyperLogLogs:

```python
hll1 = HyperLogLog(precision=10)
hll2 = HyperLogLog(precision=10)

# Add different data to each
for i in range(50000):
    hll1.add(f"set1_{i}")
    hll2.add(f"set2_{i}")

# Merge them
merged = hll1.merge(hll2)
estimate = merged.estimate_cardinality()
```

## 📊 Performance Analysis

### Memory Usage:

| Precision | Buckets | Memory | Error Rate |
| --------- | ------- | ------ | ---------- |
| 4         | 16      | 12B    | 26%        |
| 8         | 256     | 192B   | 6.5%       |
| 10        | 1K      | 768B   | 3.25%      |
| 12        | 4K      | 3KB    | 1.625%     |
| 16        | 64K     | 48KB   | 0.406%     |

### Time Complexity:

- **Insertion**: O(1) - constant time hash and bucket update
- **Estimation**: O(m) - linear in number of buckets
- **Merging**: O(m) - compare all bucket pairs

### Space Efficiency Comparison:

For 1 million unique elements:

- **Exact counting**: ~20MB (20 bytes per element)
- **HyperLogLog (b=12)**: ~3KB (99.98% memory reduction)

## 🧪 Testing

### Run Basic Tests:

```bash
cd data-structures/hyper-log-log
python test_hyperloglog.py
```

### Run Educational Examples:

```bash
python test_hyperloglog.py --examples
```

### Run Real-World Examples:

```bash
python examples.py
```

### Test Categories:

1. **Correctness Tests**: Verify algorithm implementation
2. **Accuracy Tests**: Validate error bounds across different data sizes
3. **Edge Case Tests**: Handle special inputs and boundary conditions
4. **Performance Tests**: Measure speed and memory usage
5. **Educational Tests**: Demonstrate internal workings

## 🌍 Real-World Applications

### 1. Web Analytics

- **Use Case**: Count unique visitors to websites
- **Benefit**: Handle millions of users with minimal memory
- **Example**: Daily/weekly unique visitor counts

### 2. Database Optimization

- **Use Case**: Query optimizer cardinality estimation
- **Benefit**: Fast column cardinality estimates for query planning
- **Example**: Estimate distinct values in database columns

### 3. Distributed Systems

- **Use Case**: Aggregate cardinality across multiple nodes
- **Benefit**: Mergeable estimates reduce network overhead
- **Example**: Distributed log analysis

### 4. Stream Processing

- **Use Case**: Real-time unique count estimation
- **Benefit**: Constant memory usage regardless of stream size
- **Example**: Unique user counting in real-time analytics

### 5. Network Monitoring

- **Use Case**: Count unique IP addresses, flows, etc.
- **Benefit**: Handle high-volume network data efficiently
- **Example**: DDoS attack detection and analysis

## 📖 Further Reading

### Academic Papers:

1. **Original Paper**: "HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm" (Flajolet et al., 2007)
2. **Improvements**: "HyperLogLog in Practice" (Google, 2013)
3. **Applications**: Various papers on streaming algorithms and big data

### Implementation References:

1. **Redis HyperLogLog**: Production implementation
2. **PostgreSQL HyperLogLog**: Database integration
3. **Apache Spark**: Distributed computing applications

### Related Algorithms:

1. **LogLog**: Predecessor algorithm
2. **MinHash**: Jaccard similarity estimation
3. **Count-Min Sketch**: Frequency estimation
4. **Bloom Filters**: Set membership testing

---

## 🔬 Mathematical Intuition

The brilliance of HyperLogLog lies in its mathematical insight:

1. **Random Process**: Hash functions create pseudo-random binary strings
2. **Extreme Value Theory**: Maximum leading zeros relates to set size
3. **Variance Reduction**: Multiple buckets reduce estimation variance
4. **Harmonic Mean**: Provides better bias properties than arithmetic mean

This combination allows accurate cardinality estimation with logarithmic space complexity, making it practical for big data applications where exact counting would be impossible due to memory constraints.

The algorithm demonstrates how mathematical theory can be applied to solve practical computational problems with elegant simplicity and remarkable efficiency.
