# Popular Content Tracker

## Problem Statement

Imagine you are given a **stream of content IDs** along with associated actions to be performed on them. Examples of content include videos, pages, posts, etc.

There are **two actions** associated with a content ID:

- **`increasePopularity`** → increases the popularity of the content by 1. This happens when someone comments on the content or likes it
- **`decreasePopularity`** → decreases the popularity of the content by 1. This happens when spam bot comments/likes are removed from the content
- **Content IDs are positive integers**

**Goal**: Implement a class that can return the **most popular content ID** at any time while consuming the stream of content IDs and their associated actions. If there are no content IDs with popularity greater than 0, return **-1**.

## Solution Overview

This repository contains **three different implementations** with increasing levels of optimization:

| Implementation       | Time Complexity                                 | Space Complexity | Best Use Case                             |
| -------------------- | ----------------------------------------------- | ---------------- | ----------------------------------------- |
| **Part A: Basic**    | getMostPopular: O(n) <br> Updates: O(1)         | O(k)             | Small datasets, simple requirements       |
| **Part B: Heap**     | getMostPopular: O(log n) <br> Updates: O(log n) | O(k + s)         | Moderate datasets, frequent queries       |
| **Part C: Advanced** | getMostPopular: O(1) avg <br> Updates: O(1) avg | O(k + p)         | Large datasets, high-frequency operations |

Where:

- **n** = number of content items being tracked
- **k** = number of unique content IDs with popularity > 0
- **s** = number of stale entries in heap
- **p** = number of unique popularity levels

---

## Part A: Basic Implementation (`part_a_basic_implementation.py`)

### Approach

Uses a simple **dictionary** to track popularity counts and performs **linear search** to find the most popular content.

### Key Design Decisions

1. **Dictionary Storage**: `content_id → popularity_count`
2. **Automatic Cleanup**: Remove content when popularity drops to 0
3. **Linear Search**: Scan all entries to find maximum popularity

### Complexity Analysis

- **`increasePopularity()`**: O(1) - Direct dictionary update
- **`decreasePopularity()`**: O(1) - Direct dictionary update + potential deletion
- **`getMostPopular()`**: O(n) - Linear scan through all tracked content

### Intuition

This is the **simplest possible approach**. We trade query performance for implementation simplicity. The key insight is that we only need to track content with positive popularity, which naturally handles the "return -1" requirement.

### When to Use

- **Small datasets** (< 1000 content items)
- **Infrequent queries** compared to updates
- **Simple requirements** where implementation clarity is prioritized

### Code Highlights

```python
def getMostPopular(self) -> int:
    if not self.popularity_map:
        return -1

    max_popularity = max(self.popularity_map.values())
    for content_id, popularity in self.popularity_map.items():
        if popularity == max_popularity:
            return content_id
```

---

## Part B: Heap Optimization (`part_b_heap_optimization.py`)

### Approach

Uses a **max heap** (simulated with negative values) to efficiently find the most popular content while maintaining reasonable update performance.

### Key Design Decisions

1. **Max Heap**: Store `(-popularity, version, content_id)` tuples
2. **Lazy Deletion**: Use version numbers instead of expensive heap removal
3. **Stale Entry Cleanup**: Clean up outdated entries during `getMostPopular()`
4. **Dual Tracking**: Maintain both heap and dictionary for different operations

### Complexity Analysis

- **`increasePopularity()`**: O(log n) - Heap push operation
- **`decreasePopularity()`**: O(1) - Lazy deletion, just update version
- **`getMostPopular()`**: O(log n) amortized - Cleanup stale entries + heap operations

### Intuition

The **core challenge** with heaps is that they don't support efficient arbitrary element removal/update. Our solution uses **lazy deletion**:

1. Instead of removing/updating heap entries (expensive), we mark them as "stale"
2. Use **version numbers** to identify which heap entries are current
3. **Clean up stale entries** only when we encounter them at the heap top
4. This gives us **amortized good performance** without complex heap maintenance

### Lazy Deletion Example

```
Initial: heap = [(-2, v1, content1), (-1, v1, content2)]
After decreasing content1:
  - popularity_map: {content1: 1, content2: 1}
  - version_map: {content1: v2, content2: v1}
  - heap: [(-2, v1, content1), (-1, v1, content2), (-1, v2, content1)]

When getMostPopular() is called:
  - Top entry (-2, v1, content1) is stale (version mismatch)
  - Remove stale entry, check next entry
  - Continue until finding valid entry
```

### When to Use

- **Moderate datasets** (1K - 100K content items)
- **Frequent queries** with occasional updates
- **Balanced workload** between updates and queries

---

## Part C: Advanced Hybrid (`part_c_advanced_hybrid.py`)

### Approach

Combines **multiple optimization techniques** for maximum performance using frequency-based tracking and smart caching strategies.

### Key Design Decisions

1. **Frequency Tracking**: Map `popularity_level → count_of_items_with_this_popularity`
2. **Content Grouping**: Group content IDs by their popularity level
3. **Sorted Popularity Levels**: Maintain descending order of all popularity levels
4. **Cached Maximum**: Direct O(1) access to highest popularity
5. **Hybrid Data Structure**: Combine frequency maps, sets, and sorted lists

### Complexity Analysis

- **`increasePopularity()`**: O(1) average, O(log p) worst case (p = unique popularity levels)
- **`decreasePopularity()`**: O(1) average, O(log p) worst case
- **`getMostPopular()`**: O(1) average case (cached lookup), O(log p) worst case

### Intuition

The **key insight** is that many streaming scenarios have **relatively few unique popularity levels** compared to content items. For example:

- **1 million content items** might only have **100 unique popularity levels**
- Instead of tracking each item individually for max-finding, we can:
  1. **Group items by popularity level**
  2. **Track frequency of each popularity level**
  3. **Cache the maximum popularity** for O(1) access
  4. **Use sets for efficient item management within each level**

### Data Structure Design

```python
# Example state with 4 content items
popularity_map = {1: 3, 2: 2, 3: 2, 4: 1}  # content_id → popularity

# Frequency tracking
popularity_frequency = {3: 1, 2: 2, 1: 1}  # popularity → count of items
content_by_popularity = {
    3: {1},        # 1 item with popularity 3
    2: {2, 3},     # 2 items with popularity 2
    1: {4}         # 1 item with popularity 1
}
sorted_popularities = [3, 2, 1]  # Descending order
max_popularity = 3  # Cached for O(1) access
```

### Performance Optimizations

1. **O(1) getMostPopular**: Direct cache lookup when max popularity is stable
2. **Efficient Updates**: Only update frequency counters and sets
3. **Memory Efficiency**: Reduced overhead when many items have same popularity
4. **Top-K Queries**: Can efficiently return top K popular items
5. **Smart Cleanup**: Periodic validation to maintain data structure integrity

### When to Use

- **Large datasets** (100K+ content items)
- **High-frequency operations** (thousands of ops/second)
- **Streaming scenarios** with relatively few unique popularity levels
- **Production systems** requiring predictable performance

---

## Complexity Comparison

### Time Complexity Summary

| Operation            | Basic | Heap     | Advanced |
| -------------------- | ----- | -------- | -------- |
| `increasePopularity` | O(1)  | O(log n) | O(1) avg |
| `decreasePopularity` | O(1)  | O(1)     | O(1) avg |
| `getMostPopular`     | O(n)  | O(log n) | O(1) avg |

### Space Complexity Summary

| Implementation | Space    | Notes                                           |
| -------------- | -------- | ----------------------------------------------- |
| Basic          | O(k)     | k = active content items                        |
| Heap           | O(k + s) | s = stale heap entries                          |
| Advanced       | O(k + p) | p = unique popularity levels (typically p << k) |

### Performance Characteristics

**Query-Heavy Workloads** (many `getMostPopular` calls):

- **Advanced** >> **Heap** >> **Basic**

**Update-Heavy Workloads** (many increase/decrease calls):

- **Advanced** ≈ **Basic** > **Heap**

**Balanced Workloads**:

- **Advanced** > **Heap** > **Basic**

**Memory Efficiency**:

- **Basic** > **Advanced** > **Heap** (for small datasets)
- **Advanced** > **Basic** > **Heap** (for large datasets with few popularity levels)

---

## Real-World Applications

### Streaming Scenarios

- **Social Media**: Track post engagement in real-time
- **Video Platforms**: Monitor video popularity for trending algorithms
- **E-commerce**: Track product popularity for recommendation systems
- **Gaming**: Leaderboards and popular content tracking

### Performance Requirements

- **Low Latency**: Advanced implementation for sub-millisecond responses
- **High Throughput**: Advanced implementation for handling millions of updates/queries
- **Memory Constrained**: Basic implementation for simple embedded systems
- **Balanced Workload**: Heap implementation for general-purpose applications

---

## Running the Code

### Individual Implementations

```bash
# Run basic implementation demo
python part_a_basic_implementation.py

# Run heap optimization demo
python part_b_heap_optimization.py

# Run advanced hybrid demo
python part_c_advanced_hybrid.py
```

### Comprehensive Testing

```bash
# Run all correctness and performance tests
python test_all_implementations.py
```

### Expected Output

The test suite will show:

1. **Correctness verification** across all implementations
2. **Performance comparison** with timing measurements
3. **Scalability analysis** with different data sizes
4. **Stress test results** with high-volume operations

---

## Key Insights and Learnings

### Design Trade-offs

1. **Simplicity vs Performance**: Basic approach trades performance for simplicity
2. **Memory vs Speed**: Heap approach uses more memory for better query performance
3. **Complexity vs Optimality**: Advanced approach adds complexity for near-optimal performance

### Algorithm Techniques Demonstrated

1. **Lazy Deletion**: Defer expensive operations until necessary (Heap implementation)
2. **Frequency Counting**: Track distribution rather than individual items (Advanced implementation)
3. **Caching Strategies**: Cache expensive computations for repeated access
4. **Hybrid Data Structures**: Combine multiple structures for different operation types

### Production Considerations

1. **Choose implementation based on workload characteristics**
2. **Monitor memory usage**, especially with heap implementation's stale entries
3. **Consider batch processing** for very high-frequency scenarios
4. **Implement proper error handling** for invalid inputs and edge cases

### Extension Possibilities

1. **Top-K queries**: Get K most popular items (demonstrated in Advanced)
2. **Time-windowed popularity**: Track popularity over time windows
3. **Weighted operations**: Different increment/decrement values
4. **Persistent storage**: Save/restore popularity state
5. **Distributed implementation**: Handle popularity across multiple servers

---

## Conclusion

This implementation showcases **three distinct approaches** to the same problem, each optimized for different scenarios:

- **Part A** demonstrates the importance of **clear, simple solutions**
- **Part B** shows how **classical data structures** (heaps) can be adapted with creative techniques (lazy deletion)
- **Part C** illustrates **advanced optimization techniques** combining multiple data structures

The progression from O(n) → O(log n) → O(1) demonstrates how **algorithmic thinking** and **careful data structure design** can dramatically improve performance while handling the same fundamental requirements.
