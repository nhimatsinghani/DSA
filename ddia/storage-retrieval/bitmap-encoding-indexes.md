I'll explain bitmap encoding and bitmap indexes in column-oriented storage with examples and code.

## Column-Oriented Storage Background

**Row-oriented storage:**

```
Record 1: [ID=1, Name="Alice", City="NYC", Age=25]
Record 2: [ID=2, Name="Bob", City="LA", Age=30]
Record 3: [ID=3, Name="Carol", City="NYC", Age=28]

Stored as: [1,"Alice","NYC",25][2,"Bob","LA",30][3,"Carol","NYC",28]
```

**Column-oriented storage:**

```
ID column:   [1, 2, 3]
Name column: ["Alice", "Bob", "Carol"]
City column: ["NYC", "LA", "NYC"]
Age column:  [25, 30, 28]

Each column stored separately on disk
```

## What is Bitmap Encoding?

**Bitmap encoding** represents each distinct value in a column as a separate bitmap (bit array), where each bit corresponds to a row.

**Example with City column:**

```
Data: ["NYC", "LA", "NYC", "SF", "NYC", "LA", "SF"]
Rows:    1     2     3     4     5     6     7

Bitmap encoding:
NYC: [1, 0, 1, 0, 1, 0, 0]  ← bit=1 where value="NYC"
LA:  [0, 1, 0, 0, 0, 1, 0]  ← bit=1 where value="LA"
SF:  [0, 0, 0, 1, 0, 0, 1]  ← bit=1 where value="SF"
```

## Code Implementation

```python
class BitmapIndex:
    def __init__(self):
        self.bitmaps = {}  # value -> bitmap
        self.row_count = 0

    def build_index(self, column_data):
        self.row_count = len(column_data)

        # Get unique values
        unique_values = set(column_data)

        # Create bitmap for each unique value
        for value in unique_values:
            bitmap = []
            for i, row_value in enumerate(column_data):
                bitmap.append(1 if row_value == value else 0)
            self.bitmaps[value] = bitmap

    def get_bitmap(self, value):
        return self.bitmaps.get(value, [0] * self.row_count)

    def print_index(self):
        for value, bitmap in self.bitmaps.items():
            print(f"{value}: {bitmap}")

# Example usage
cities = ["NYC", "LA", "NYC", "SF", "NYC", "LA", "SF"]
city_index = BitmapIndex()
city_index.build_index(cities)
city_index.print_index()

# Output:
# NYC: [1, 0, 1, 0, 1, 0, 0]
# LA: [0, 1, 0, 0, 0, 1, 0]
# SF: [0, 0, 0, 1, 0, 0, 1]
```

## Why Bitmap Encoding is Great for Compression

### 1. Run-Length Encoding (RLE)

**Sparse bitmaps compress very well:**

```python
def run_length_encode(bitmap):
    """Compress bitmap using run-length encoding"""
    if not bitmap:
        return []

    compressed = []
    current_bit = bitmap[0]
    count = 1

    for i in range(1, len(bitmap)):
        if bitmap[i] == current_bit:
            count += 1
        else:
            compressed.append((current_bit, count))
            current_bit = bitmap[i]
            count = 1

    compressed.append((current_bit, count))
    return compressed

def run_length_decode(compressed):
    """Decompress run-length encoded bitmap"""
    bitmap = []
    for bit, count in compressed:
        bitmap.extend([bit] * count)
    return bitmap

# Example
bitmap = [1, 1, 1, 0, 0, 0, 0, 0, 1, 1]
compressed = run_length_encode(bitmap)
print(f"Original:   {bitmap}")
print(f"Compressed: {compressed}")  # [(1, 3), (0, 5), (1, 2)]
print(f"Decoded:    {run_length_decode(compressed)}")

# Real-world example with sparse data
sparse_bitmap = [0] * 1000 + [1] * 10 + [0] * 1000
compressed_sparse = run_length_encode(sparse_bitmap)
print(f"Compression ratio: {len(sparse_bitmap)} -> {len(compressed_sparse)} entries")
# Output: 2010 -> 3 entries! Huge compression
```

### 2. Real Example with Employee Data

```python
class ColumnStore:
    def __init__(self):
        self.columns = {}
        self.bitmap_indexes = {}
        self.row_count = 0

    def load_data(self, data):
        if not data:
            return

        self.row_count = len(data)

        # Extract columns
        column_names = data[0].keys()
        for col_name in column_names:
            self.columns[col_name] = [row[col_name] for row in data]

            # Build bitmap index for categorical columns
            if self._is_categorical(self.columns[col_name]):
                self.bitmap_indexes[col_name] = BitmapIndex()
                self.bitmap_indexes[col_name].build_index(self.columns[col_name])

    def _is_categorical(self, column_data):
        # Simple heuristic: if unique values < 10% of total, treat as categorical
        unique_count = len(set(column_data))
        return unique_count < len(column_data) * 0.1

    def query_equal(self, column, value):
        """Find rows where column = value"""
        if column in self.bitmap_indexes:
            return self.bitmap_indexes[column].get_bitmap(value)
        else:
            # Fallback to linear scan for non-indexed columns
            return [1 if v == value else 0 for v in self.columns[column]]

    def query_and(self, conditions):
        """Find rows matching ALL conditions (AND operation)"""
        result_bitmap = [1] * self.row_count

        for column, value in conditions.items():
            column_bitmap = self.query_equal(column, value)
            # Bitwise AND
            result_bitmap = [a & b for a, b in zip(result_bitmap, column_bitmap)]

        return result_bitmap

    def query_or(self, column, values):
        """Find rows where column IN (values) - OR operation"""
        result_bitmap = [0] * self.row_count

        for value in values:
            column_bitmap = self.query_equal(column, value)
            # Bitwise OR
            result_bitmap = [a | b for a, b in zip(result_bitmap, column_bitmap)]

        return result_bitmap

# Example dataset
employees = [
    {"id": 1, "department": "Engineering", "level": "Senior", "salary": 100000},
    {"id": 2, "department": "Marketing", "level": "Junior", "salary": 60000},
    {"id": 3, "department": "Engineering", "level": "Junior", "salary": 80000},
    {"id": 4, "department": "Sales", "level": "Senior", "salary": 90000},
    {"id": 5, "department": "Engineering", "level": "Senior", "salary": 110000},
    {"id": 6, "department": "Marketing", "level": "Senior", "salary": 85000},
    {"id": 7, "department": "Sales", "level": "Junior", "salary": 55000},
]

# Load data into column store
store = ColumnStore()
store.load_data(employees)

# Show bitmap indexes
print("Department bitmap index:")
store.bitmap_indexes["department"].print_index()
print("\nLevel bitmap index:")
store.bitmap_indexes["level"].print_index()

# Example queries
print("\n=== Query Examples ===")

# Query 1: Find all Engineering employees
eng_bitmap = store.query_equal("department", "Engineering")
print(f"Engineering employees: {eng_bitmap}")  # [1, 0, 1, 0, 1, 0, 0]

# Query 2: Find Senior employees in Engineering (AND operation)
senior_eng = store.query_and({"department": "Engineering", "level": "Senior"})
print(f"Senior Engineering: {senior_eng}")     # [1, 0, 0, 0, 1, 0, 0]

# Query 3: Find employees in Engineering OR Marketing (OR operation)
eng_or_marketing = store.query_or("department", ["Engineering", "Marketing"])
print(f"Eng OR Marketing: {eng_or_marketing}") # [1, 1, 1, 0, 1, 1, 0]

# Convert bitmap to actual row IDs
def bitmap_to_rows(bitmap):
    return [i for i, bit in enumerate(bitmap) if bit == 1]

print(f"Senior Engineering employee IDs: {bitmap_to_rows(senior_eng)}")
```

## Bitmap Operations

**Efficient bitwise operations:**

```python
class FastBitmapOps:
    @staticmethod
    def bitmap_and(bitmap1, bitmap2):
        """Bitwise AND operation"""
        return [a & b for a, b in zip(bitmap1, bitmap2)]

    @staticmethod
    def bitmap_or(bitmap1, bitmap2):
        """Bitwise OR operation"""
        return [a | b for a, b in zip(bitmap1, bitmap2)]

    @staticmethod
    def bitmap_not(bitmap):
        """Bitwise NOT operation"""
        return [1 - bit for bit in bitmap]

    @staticmethod
    def bitmap_count(bitmap):
        """Count number of 1s (cardinality)"""
        return sum(bitmap)

    @staticmethod
    def bitmap_intersection_count(bitmap1, bitmap2):
        """Count intersection without materializing result"""
        return sum(a & b for a, b in zip(bitmap1, bitmap2))

# Example complex query
ops = FastBitmapOps()

# Find: (Engineering OR Marketing) AND Senior AND NOT Junior
dept_bitmap = store.query_or("department", ["Engineering", "Marketing"])
senior_bitmap = store.query_equal("level", "Senior")
junior_bitmap = store.query_equal("level", "Junior")

result = ops.bitmap_and(dept_bitmap, senior_bitmap)
result = ops.bitmap_and(result, ops.bitmap_not(junior_bitmap))

print(f"Complex query result: {result}")
print(f"Matching employee count: {ops.bitmap_count(result)}")
```

## Advanced: Compressed Bitmaps

**For very large datasets, use compressed representations:**

```python
class CompressedBitmap:
    def __init__(self, bitmap):
        self.compressed = self._compress(bitmap)
        self.original_length = len(bitmap)

    def _compress(self, bitmap):
        """Simple compression: store (start_pos, length) for runs of 1s"""
        compressed = []
        i = 0
        while i < len(bitmap):
            if bitmap[i] == 1:
                start = i
                while i < len(bitmap) and bitmap[i] == 1:
                    i += 1
                compressed.append((start, i - start))
            else:
                i += 1
        return compressed

    def intersect_with(self, other_compressed):
        """Intersection without decompressing"""
        result_ranges = []

        for start1, len1 in self.compressed:
            end1 = start1 + len1
            for start2, len2 in other_compressed.compressed:
                end2 = start2 + len2

                # Find overlap
                overlap_start = max(start1, start2)
                overlap_end = min(end1, end2)

                if overlap_start < overlap_end:
                    result_ranges.append((overlap_start, overlap_end - overlap_start))

        result = CompressedBitmap([])
        result.compressed = result_ranges
        result.original_length = self.original_length
        return result

    def decompress(self):
        """Convert back to regular bitmap"""
        bitmap = [0] * self.original_length
        for start, length in self.compressed:
            for i in range(start, start + length):
                bitmap[i] = 1
        return bitmap

# Example with sparse data
sparse_bitmap1 = [0, 0, 1, 1, 1, 0, 0, 0, 1, 1]
sparse_bitmap2 = [0, 1, 1, 1, 0, 0, 1, 0, 1, 0]

compressed1 = CompressedBitmap(sparse_bitmap1)
compressed2 = CompressedBitmap(sparse_bitmap2)

print(f"Original 1: {sparse_bitmap1}")
print(f"Compressed 1: {compressed1.compressed}")  # [(2, 3), (8, 2)]

print(f"Original 2: {sparse_bitmap2}")
print(f"Compressed 2: {compressed2.compressed}")  # [(1, 3), (6, 1), (8, 1)]

# Fast intersection on compressed data
intersection = compressed1.intersect_with(compressed2)
print(f"Intersection: {intersection.decompress()}")
```

## Why Bitmap Indexes Excel in Data Warehouses

### 1. Typical Query Patterns

```python
# Common OLAP queries that benefit from bitmap indexes:

# 1. Equality filters
# SELECT * FROM sales WHERE region = 'West' AND product_type = 'Electronics'
region_west = store.query_equal("region", "West")
product_electronics = store.query_equal("product_type", "Electronics")
result = ops.bitmap_and(region_west, product_electronics)

# 2. IN clauses
# SELECT * FROM sales WHERE region IN ('West', 'East')
regions_we = store.query_or("region", ["West", "East"])

# 3. Range queries (can be converted to OR of exact matches)
# SELECT * FROM sales WHERE quarter IN ('Q1', 'Q2', 'Q3')
quarters_123 = store.query_or("quarter", ["Q1", "Q2", "Q3"])

# 4. Complex boolean logic
# SELECT * FROM sales WHERE (region = 'West' OR region = 'East')
#                       AND product_type != 'Services'
west_or_east = store.query_or("region", ["West", "East"])
not_services = ops.bitmap_not(store.query_equal("product_type", "Services"))
complex_result = ops.bitmap_and(west_or_east, not_services)
```

### 2. Aggregations

```python
def aggregate_with_bitmap(store, group_column, metric_column, bitmap_filter):
    """Aggregate metric grouped by column, filtered by bitmap"""
    groups = {}

    for i, include in enumerate(bitmap_filter):
        if include:
            group_key = store.columns[group_column][i]
            metric_value = store.columns[metric_column][i]

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(metric_value)

    # Calculate aggregates
    result = {}
    for group, values in groups.items():
        result[group] = {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values)
        }

    return result

# Example: Average salary by department for Senior employees only
senior_filter = store.query_equal("level", "Senior")
salary_by_dept = aggregate_with_bitmap(store, "department", "salary", senior_filter)
print("Senior employee salaries by department:")
for dept, stats in salary_by_dept.items():
    print(f"{dept}: avg=${stats['avg']:,.0f}, count={stats['count']}")
```

## Benefits Summary

**Why bitmap indexes are perfect for data warehouses:**

1. **High Compression**: Categorical data compresses extremely well
2. **Fast Boolean Operations**: Hardware-optimized bitwise operations
3. **Multiple Index Intersection**: Can combine many filters efficiently
4. **Low Memory Overhead**: Compressed bitmaps use minimal RAM
5. **Parallel Processing**: Easy to parallelize bitmap operations
6. **Cache Friendly**: Sequential access patterns work well with CPU cache

**Trade-offs:**

- **High Cardinality**: Not suitable for unique columns (like primary keys)
- **Update Cost**: Insertions require updating all relevant bitmaps
- **Read-Optimized**: Best for OLAP workloads, not OLTP

This makes bitmap encoding ideal for analytical queries on dimensions like geography, product categories, time periods, and other categorical attributes common in data warehouses!
