I'll explain size-tiered and leveled compaction strategies used in LSM-tree storage engines with simple examples.

## Background: Why Compaction is Needed

**SSTables (Sorted String Tables)** are immutable files containing sorted key-value pairs. In LSM trees, writes go to memory first, then get flushed to disk as SSTables.

**Problem without compaction:**

```
Time 1: Write A=1, B=2 → SSTable1: [A=1, B=2]
Time 2: Write C=3, A=4 → SSTable2: [A=4, C=3]
Time 3: Write D=5, B=6 → SSTable3: [B=6, D=5]

Result: 3 files, duplicated keys (A, B), wasted space
To read A: Must check SSTable2, SSTable1 (multiple disk reads)
```

**Solution:** Merge SSTables to eliminate duplicates and improve read performance.

## Size-Tiered Compaction

**Strategy:** Merge SSTables of similar sizes into larger ones.

**Example Timeline:**

```
Initial state:
Level 0: [SST1: 10MB] [SST2: 10MB] [SST3: 10MB] [SST4: 10MB]

Step 1: Trigger compaction when 4 similar-sized files exist
→ Merge SST1+SST2+SST3+SST4 = SST5: 40MB

Level 0: [SST5: 40MB] [SST6: 10MB] [SST7: 10MB] [SST8: 10MB] [SST9: 10MB]

Step 2: Continue accumulating 10MB files...
Level 0: [SST5: 40MB] [SST10: 40MB] [SST11: 40MB] [SST12: 40MB]

Step 3: Merge 40MB files → SST13: 160MB
Level 0: [SST13: 160MB] [more 10MB files...]
```

**Visual Example:**

```
Time 0: A=1, B=2     → SST1 [A=1, B=2]              (Size: 2KB)
Time 1: C=3, D=4     → SST2 [C=3, D=4]              (Size: 2KB)
Time 2: A=5, E=6     → SST3 [A=5, E=6]              (Size: 2KB)
Time 3: F=7, G=8     → SST4 [F=7, G=8]              (Size: 2KB)

Compaction trigger: 4 files of ~2KB each
↓
Merged result: SST5 [A=5, B=2, C=3, D=4, E=6, F=7, G=8] (Size: 7KB)
Note: A=1 was overwritten by A=5
```

**Characteristics:**

- **Simple**: Just group by size
- **Write amplification**: Data gets rewritten multiple times as it moves through size tiers
- **Space overhead**: Can use up to 50% extra space during compaction

## Leveled Compaction

**Strategy:** Organize SSTables into levels with exponentially increasing capacity.

**Level Structure:**

```
Level 0: 10MB total   (overlapping key ranges allowed)
Level 1: 100MB total  (non-overlapping key ranges)
Level 2: 1GB total    (non-overlapping key ranges)
Level 3: 10GB total   (non-overlapping key ranges)
...
```

**Example with Key Ranges:**

```
Level 0: [SST1: A-F] [SST2: C-H] [SST3: E-K]  ← Can overlap!

Level 1: [SST4: A-D] [SST5: E-H] [SST6: I-M] [SST7: N-R] [SST8: S-Z]
         ↑          ↑          ↑           ↑           ↑
         No overlaps within level

Level 2: [SST9: A-M] [SST10: N-Z]
         ↑          ↑
         Larger ranges, no overlaps
```

**Compaction Process:**

```
Step 1: Level 0 gets full
Level 0: [A-F] [C-H] [E-K] [G-L] ← 4 files, threshold reached

Step 2: Pick overlapping range (say E-H) and merge with Level 1
Level 0: [A-F] [C-H] [E-K] [G-L]
Level 1: [A-D] [E-H] [I-M] [N-R] [S-Z]
                ↑
         Merge E-H from both levels

Step 3: Result after compaction
Level 0: [A-F] [G-L]  ← Files with E-H removed
Level 1: [A-D] [E-H: updated] [I-M] [N-R] [S-Z]
```

**Detailed Example:**

```
Before compaction:
Level 0 SST: [E=1, F=2, G=3, H=4]
Level 1 SST: [E=0, F=9, H=8, I=7]  ← Range E-I

Compaction process:
1. Merge both SSTables
2. Resolve conflicts (newer wins)
3. Result: [E=1, F=2, G=3, H=4, I=7]
4. Write back to Level 1
```

## Comparison

| Aspect                  | Size-Tiered                  | Leveled                     |
| ----------------------- | ---------------------------- | --------------------------- |
| **Organization**        | Group by size                | Group by level + key range  |
| **Space Overhead**      | High (up to 50%)             | Low (~10%)                  |
| **Write Amplification** | High                         | Lower                       |
| **Read Performance**    | Need to check multiple files | Check fewer files per range |
| **Implementation**      | Simpler                      | More complex                |

**Read Performance Example:**

Looking up key "M":

**Size-tiered:**

```
Must check: SST1[A-F], SST2[C-H], SST3[E-K], SST4[G-L], SST5[J-P]
→ Multiple files might contain "M"
```

**Leveled:**

```
Level 0: Check all files (overlapping ranges)
Level 1: Check only SST[I-M] (guaranteed range)
Level 2: Check only SST[A-M] (guaranteed range)
→ Fewer files to check per level
```

## Real-World Usage

**Size-tiered (HBase, Cassandra):**

- Better for write-heavy workloads
- Simpler to implement
- Acceptable for applications that can tolerate higher space usage

**Leveled (LevelDB, RocksDB):**

- Better for read-heavy workloads
- More efficient space utilization
- Used by databases prioritizing storage efficiency

**Cassandra's Hybrid Approach:**

- Allows configuration of both strategies
- Can switch based on workload characteristics
- Size-tiered for write-heavy tables, leveled for read-heavy tables

The choice between strategies depends on your specific requirements for read performance, write performance, and storage efficiency!
