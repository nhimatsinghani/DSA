# Cloud-Based File Storage System

A comprehensive implementation of a multi-level cloud-based file storage system designed for technical interview preparation. This system progressively evolves through three levels, each adding new functionality while maintaining backward compatibility.

## 🎯 Problem Description

This is a **step-by-step coding problem** commonly seen in 90-minute technical assessments where each level unlocks after completing the previous one. The system must support:

- **Level 1**: Basic file operations (add, retrieve, delete)
- **Level 2**: Prefix-based file querying with sorting
- **Level 3**: User management with storage capacity limits and account merging

## 🏗️ System Architecture

```
CloudFileStorage
├── Level 1: Core File Operations
│   ├── add_file(name, size) -> bool
│   ├── get_file_size(name) -> int | None
│   └── delete_file(name) -> int | None
│
├── Level 2: Prefix-Based Querying
│   └── get_n_largest(prefix, n) -> list[str]
│
└── Level 3: User Management
    ├── add_user(user_id, capacity) -> bool
    ├── add_file_by(user_id, name, size) -> int | None
    └── merge_user(user_id_1, user_id_2) -> int | None
```

## 📋 Detailed Requirements

### Level 1: Basic File Operations

**File Management:**

- `add_file(name: str, size: int) -> bool`

  - Adds a new file to storage
  - Returns `True` if successful, `False` if file already exists
  - Files are owned by admin user (unlimited capacity)

- `get_file_size(name: str) -> int | None`

  - Returns file size if exists, `None` otherwise
  - O(1) lookup time

- `delete_file(name: str) -> int | None`
  - Deletes file and returns its size if successful
  - Returns `None` if file doesn't exist
  - Updates owner's storage usage

### Level 2: Prefix-Based File Querying

**Query Interface:**

- `get_n_largest(prefix: str, n: int) -> list[str]`
  - Returns up to `n` largest files with names starting with `prefix`
  - **Sorting Priority**: Size (descending), then name (lexicographically ascending)
  - Returns empty list if `n <= 0` or no matches found
  - Case-sensitive prefix matching

**Examples:**

```python
# Files: log_error.txt(150), log_warning.txt(100), log_info.txt(75)
get_n_largest("log_", 2)  # Returns: ["log_error.txt", "log_warning.txt"]

# Same size files sorted by name
# Files: file_a.txt(100), file_z.txt(100), file_m.txt(100)
get_n_largest("file_", 3)  # Returns: ["file_a.txt", "file_m.txt", "file_z.txt"]
```

### Level 3: User Management & Capacity Limits

**User Operations:**

- `add_user(user_id: str, capacity: int) -> bool`

  - Creates user with storage capacity limit in bytes
  - Returns `False` if user already exists

- `add_file_by(user_id: str, name: str, size: int) -> int | None`

  - Adds file owned by specific user
  - Returns remaining capacity after addition
  - Returns `None` if: user doesn't exist, file exists, or exceeds capacity

- `merge_user(user_id_1: str, user_id_2: str) -> int | None`
  - Transfers all files from `user_id_2` to `user_id_1`
  - Adds `user_id_2`'s remaining capacity to `user_id_1`'s total capacity
  - Deletes `user_id_2` after successful merge
  - Returns `user_id_1`'s remaining capacity after merge
  - Returns `None` if merge would exceed `user_id_1`'s capacity

**Special Admin User:**

- Pre-created "admin" user with unlimited capacity
- Level 1 operations use admin user for backward compatibility

## 🚀 Quick Start

### Running the Demo

```bash
python demo.py
```

Interactive demonstration of all functionality with step-by-step examples.

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific level
python run_tests.py --level 1
python run_tests.py --level 2
python run_tests.py --level 3

# Run comprehensive integration tests
python run_tests.py --comprehensive

# Quick smoke test
python run_tests.py --quick
```

### Basic Usage Example

```python
from file_storage_system import CloudFileStorage

# Initialize storage
storage = CloudFileStorage()

# Level 1: Basic operations
storage.add_file("document.pdf", 1000)
size = storage.get_file_size("document.pdf")  # Returns: 1000
deleted_size = storage.delete_file("document.pdf")  # Returns: 1000

# Level 2: Prefix queries
storage.add_file("log_error.txt", 150)
storage.add_file("log_info.txt", 100)
files = storage.get_n_largest("log_", 2)  # Returns: ["log_error.txt", "log_info.txt"]

# Level 3: User management
storage.add_user("alice", 500)
remaining = storage.add_file_by("alice", "alice_file.txt", 200)  # Returns: 300
storage.add_user("bob", 300)
storage.add_file_by("bob", "bob_file.txt", 100)
merge_result = storage.merge_user("alice", "bob")  # Returns remaining capacity
```

## 🏛️ Implementation Details

### Data Structures

**Core Storage:**

```python
# Primary file storage
self.files: Dict[str, FileInfo] = {}

# FileInfo dataclass
@dataclass
class FileInfo:
    name: str
    size: int
    owner: Optional[str] = None
```

**User Management:**

```python
# User storage
self.users: Dict[str, User] = {}

# User dataclass
@dataclass
class User:
    user_id: str
    capacity: int
    used_storage: int = 0
    files: Set[str] = None
```

**Optimization Structures:**

```python
# Prefix indexing for efficient queries (optional optimization)
self.files_by_prefix: Dict[str, Set[str]] = defaultdict(set)
```

### Time Complexity Analysis

| Operation       | Time Complexity | Space Complexity                         |
| --------------- | --------------- | ---------------------------------------- |
| `add_file`      | O(k)            | O(k) where k = filename length           |
| `get_file_size` | O(1)            | O(1)                                     |
| `delete_file`   | O(k)            | O(1) where k = filename length           |
| `get_n_largest` | O(m log n)      | O(n) where m = matching files, n = limit |
| `add_user`      | O(1)            | O(1)                                     |
| `add_file_by`   | O(k)            | O(k) where k = filename length           |
| `merge_user`    | O(f)            | O(1) where f = files to transfer         |

**🚀 Key Optimizations in `get_n_largest`:**

1. **Prefix Index**: O(1) prefix lookup instead of O(F) file scanning
2. **Min Heap**: O(m log n) selection instead of O(m log m) full sorting

### Memory Usage

- **File Storage**: O(F × K) where F = files, K = avg filename length
- **User Storage**: O(U × F) where U = users, F = files per user
- **Prefix Index**: O(F × K²) in worst case (all prefixes stored)

## 🧪 Testing Strategy

### Test Coverage

**Level 1 Tests (`test_level1.py`):**

- ✅ Basic file operations
- ✅ Duplicate file handling
- ✅ Non-existent file operations
- ✅ Edge cases (empty names, zero sizes)
- ✅ Multiple file independence

**Level 2 Tests (`test_level2.py`):**

- ✅ Prefix matching accuracy
- ✅ Size-based sorting priority
- ✅ Lexicographical tie-breaking
- ✅ Limit parameter validation
- ✅ Edge cases (empty prefix, case sensitivity)

**Level 3 Tests (`test_level3.py`):**

- ✅ User creation and validation
- ✅ Capacity enforcement
- ✅ File ownership tracking
- ✅ Account merging logic
- ✅ Integration with previous levels

**Comprehensive Tests:**

- ✅ Cross-level integration
- ✅ Large-scale operations (20 users, 100 files)
- ✅ System integrity validation
- ✅ Complex merge scenarios

### Test Execution Options

```bash
# Individual level testing
python test_level1.py
python test_level2.py
python test_level3.py

# Comprehensive test runner
python run_tests.py --all           # Everything
python run_tests.py --comprehensive # Integration only
python run_tests.py --quick         # Smoke tests
```

## 🎯 Interview Preparation Guide

### Key Discussion Points

**Design Decisions:**

1. **Data Structure Choice**: Why dictionaries for O(1) operations
2. **User Model**: Separation of concerns between files and users
3. **Admin User**: Backward compatibility strategy
4. **Prefix Indexing**: Trade-offs between memory and query performance

**Scalability Considerations:**

1. **Horizontal Scaling**: File sharding strategies
2. **Caching**: Redis for frequent queries
3. **Database Backend**: Migration from in-memory to persistent storage
4. **Load Balancing**: Distributing user requests

**Alternative Approaches:**

1. **Database Normalization**: Files and Users as separate tables
2. **Trie Data Structure**: For prefix queries
3. **Heap/Priority Queue**: For top-N queries
4. **Event Sourcing**: For audit trails

### Common Interview Questions

**Q: How would you scale this system to handle millions of files?**
A: Implement sharding by filename hash, use distributed caching (Redis), migrate to database backend (PostgreSQL), implement async operations.

**Q: What if we need to support file versioning?**
A: Extend `FileInfo` to include version history, modify operations to handle version parameters, implement cleanup policies for old versions.

**Q: How would you handle concurrent access?**
A: Add locking mechanisms (file-level or user-level), implement optimistic concurrency control, use database transactions for consistency.

**Q: What about file permissions and access control?**
A: Add permission matrix to `User` class, implement role-based access control (RBAC), add file visibility levels (public/private/shared).

### Performance Optimization Ideas

**Query Optimization:**

- Pre-compute sorted file lists by prefix
- Use binary search for range queries
- Implement caching for frequent prefix patterns

**Memory Optimization:**

- Lazy loading of file metadata
- Compression for filename storage
- LRU cache for recently accessed files

**User Management Optimization:**

- Batch operations for bulk user updates
- Asynchronous user merging for large accounts
- Capacity monitoring and alerting

## 📁 File Structure

```
cloud-based-file-storage/
├── file_storage_system.py     # Main implementation
├── test_level1.py            # Level 1 tests
├── test_level2.py            # Level 2 tests
├── test_level3.py            # Level 3 tests
├── run_tests.py              # Comprehensive test runner
├── demo.py                   # Interactive demonstration
├── README.md                 # This documentation
└── requirements.txt          # Dependencies (if any)
```

## 🐛 Known Limitations & Edge Cases

### Current Limitations

1. **In-Memory Only**: No persistence across restarts
2. **Single-Threaded**: No concurrent access protection
3. **No Validation**: Limited input sanitization
4. **Fixed Capacity**: No dynamic capacity adjustment

### Edge Cases Handled

- ✅ Empty filenames and zero-size files
- ✅ Unicode characters in filenames
- ✅ Very large file sizes (within system limits)
- ✅ Capacity arithmetic overflow protection
- ✅ User merging with complex ownership chains

### Edge Cases for Future Consideration

- 🔄 Circular user dependencies in complex systems
- 🔄 Filename collisions across different character encodings
- 🔄 Time-based operations (file timestamps, expiration)
- 🔄 Atomic transaction rollback for failed operations

## 🚀 Future Enhancements

### Priority Features

1. **Persistence Layer**: SQLite/PostgreSQL backend
2. **File Metadata**: Creation time, last modified, file type
3. **Access Control**: User permissions and file sharing
4. **Audit Logging**: Track all operations for compliance

### Advanced Features

1. **File Versioning**: Multiple versions per file
2. **Quota Management**: Hierarchical capacity limits
3. **Search Engine**: Full-text search within files
4. **API Interface**: REST API for external access

### Performance Features

1. **Async Operations**: Non-blocking I/O for large operations
2. **Streaming**: Support for very large files
3. **Compression**: On-the-fly file compression
4. **CDN Integration**: Geographic file distribution

## 📜 License

This implementation is designed for educational and interview preparation purposes. Feel free to use, modify, and learn from it.

## 🤝 Contributing

This is an interview preparation project, but suggestions and improvements are welcome! Areas of particular interest:

- Additional test cases
- Performance optimizations
- Alternative implementation approaches
- Documentation improvements

---

**Happy coding and good luck with your technical interviews! 🎉**
