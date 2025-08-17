# Time Series Databases Deep Dive

Time series databases (TSDBs) are specialized databases designed to efficiently store, retrieve, and analyze data points indexed by time. They are optimized for scenarios where data is generated in a continuous, time-ordered stream—such as metrics, logs, sensor data, financial ticks, etc. Here’s a deep dive into how they work, focusing on query optimization for time-based aggregation and data compression techniques.

---

## 1. How Time Series Databases Optimize Time-Based Queries

### a. Data Model and Storage Layout

- **Time-Partitioned Storage:** TSDBs organize data into time-based partitions (e.g., hourly, daily, monthly "chunks" or "shards"). This allows queries like "last month" or "last hour" to scan only relevant partitions, minimizing I/O.
- **Append-Only Writes:** Data is typically written in time order, enabling efficient sequential disk writes and reducing fragmentation.
- **Columnar Storage:** Many TSDBs use column-oriented storage for metrics, which allows fast aggregation and compression.

### b. Indexing

- **Time Indexing:** The primary index is on the timestamp, making range queries (e.g., last 24 hours) extremely fast.
- **Secondary Indexes:** Some TSDBs support secondary indexes on tags/labels (e.g., device, region) to further filter data before aggregation.

### c. Query Engine Optimizations

- **Downsampling and Rollups:** TSDBs often precompute and store aggregated data at various resolutions (minute, hour, day). Queries for "last year, daily average" can use pre-aggregated data, reducing compute time.
- **Pushdown Aggregation:** Aggregation functions (sum, avg, min, max) are pushed down to the storage engine, so only the aggregated result is returned, not raw data.
- **Time Bucketing:** Queries are optimized to group data into time buckets (e.g., GROUP BY time(1h)), which is a native operation in TSDBs.

---

## 2. Data Compression and Space Optimization

### a. Delta Encoding

- **Timestamps:** Instead of storing full timestamps, TSDBs store the difference (delta) between consecutive timestamps, which is usually a small number and compresses well.
- **Values:** For metrics that change slowly, the difference between values is small and can be efficiently encoded.

### b. Gorilla Compression (Facebook’s Algorithm)

- **Bit-Packing:** Only the bits that change between consecutive values are stored.
- **Run-Length Encoding:** Sequences of identical values or deltas are stored as a single value plus a count.

### c. Dictionary and Tag Compression

- **Tag/Label Dictionaries:** Instead of storing full tag strings with every data point, TSDBs store a dictionary of unique tags and reference them by ID.
- **Sparse Storage:** Only non-null values are stored, reducing space for sparse time series.

### d. Chunking and Block Compression

- **Chunked Storage:** Data is stored in blocks/chunks (e.g., 1,000 points per chunk), and each chunk is compressed as a unit using algorithms like LZ4, Snappy, or ZSTD.
- **Columnar Compression:** Each column (timestamp, value, tag) is compressed separately, leveraging redundancy within each column.

---

## 3. Accuracy vs. Compression

- **Lossless Compression:** Most TSDBs use lossless techniques, ensuring no data is lost during compression.
- **Downsampling with Aggregates:** When storing downsampled data (e.g., hourly averages), TSDBs may also store min, max, count, and sum to allow for more accurate rollups and error estimation.
- **Retention Policies:** Raw data can be kept for a short period, with only aggregates retained long-term, balancing storage cost and query accuracy.

---

## 4. Example: Query Optimization Flow

Suppose you want to query the average CPU usage per hour for the last month:

1. **Partition Pruning:** The TSDB scans only the partitions for the last month.
2. **Index Filtering:** If you filter by host or region, the index narrows the search further.
3. **Aggregation Pushdown:** The engine groups data into hourly buckets and computes the average within each bucket, possibly using pre-aggregated rollups.
4. **Compression-Aware Scanning:** The engine decompresses only the relevant chunks, using delta and bit-packing to minimize memory usage.

---

## 5. Popular TSDBs and Their Techniques

- **InfluxDB:** Time-partitioned storage, TSM engine with delta and Gorilla compression, downsampling, and retention policies.
- **TimescaleDB:** Built on PostgreSQL, uses time/space partitioning (hypertables), native time bucketing, and columnar compression.
- **Prometheus:** Chunked storage, delta and XOR compression, label dictionaries, and efficient time-based queries.
- **OpenTSDB:** Built on HBase, uses time-based row keys and tag dictionaries.

---

## 6. Summary Table

| Optimization        | How it Works                       | Benefit                       |
| ------------------- | ---------------------------------- | ----------------------------- |
| Time Partitioning   | Data split by time intervals       | Fast time-range queries       |
| Delta Encoding      | Store differences, not full values | High compression              |
| Bit-Packing         | Store only changed bits            | Space savings                 |
| Downsampling        | Precompute aggregates              | Fast aggregate queries        |
| Tag Dictionaries    | Store tag IDs, not full strings    | Reduces redundancy            |
| Chunked Compression | Compress blocks of data            | Efficient storage & retrieval |

---

## References

- [Facebook Gorilla Paper](https://www.vldb.org/pvldb/vol8/p1816-teller.pdf)
- [InfluxDB Storage Engine](https://docs.influxdata.com/influxdb/v2.0/reference/internals/storage-engine/)
- [TimescaleDB Compression](https://docs.timescale.com/timescaledb/latest/how-to-guides/compression/)
