I'll explain how Bitcask uses checksums to handle partially written records in a simple way with examples.

## What are Partially Written Records?

When a database crashes (power failure, system crash, etc.), it might be in the middle of writing data to disk. This can result in **partially written records** - incomplete or corrupted data.

**Example scenario:**
```
Intended write: "user:123,name:Alice,email:alice@example.com"
After crash:   "user:123,name:Ali" (incomplete)
```

## How Checksums Work

A **checksum** is like a "fingerprint" for data - a small number calculated from the content that changes if the data is corrupted.

**Simple example:**
```
Data: "Hello"
Simple checksum: Sum of ASCII values = 72+101+108+108+111 = 500

If data gets corrupted to "Helo":
Corrupted checksum: 72+101+108+111 = 392 ≠ 500
```

## Bitcask's Approach

Bitcask stores each record with its checksum in the append-only log:

```
[Checksum][Key Length][Value Length][Key][Value]
[  1234  ][    4     ][     5      ][user][Alice]
```

**When reading data:**
1. Read the record from disk
2. Calculate checksum of the actual data
3. Compare with stored checksum
4. If they match → data is intact
5. If they don't match → data is corrupted, ignore it

## Real Example

**Normal write:**
```
Record: key="user123", value="Alice"
Calculated checksum: 8542
Stored: [8542][7][5][user123][Alice]
```

**After crash (partial write):**
```
Stored: [8542][7][5][user123][Ali] (missing 'ce')
When reading:
- Calculate checksum of "Ali" = 7891
- Compare: 7891 ≠ 8542 → CORRUPTED!
- Action: Skip this record, continue reading
```

**Benefits:**
- **Detection**: Instantly knows if data is corrupted
- **Safety**: Never returns corrupt data to applications  
- **Recovery**: Can continue operating by skipping bad records
- **Simplicity**: Just ignore corrupted entries rather than complex recovery

This approach ensures data integrity while keeping the system simple and robust against crashes.