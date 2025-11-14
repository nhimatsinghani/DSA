# Find the Closest Organization Group for Target Employees

This repository contains comprehensive solutions for finding the closest common organizational group for a set of target employees across four different organizational structures and constraints.

## Problem Overview

**Core Challenge**: Given a set of target employees, find the closest common group they all belong to in an organizational structure.

### Parts Breakdown:

**Part A**: Basic hierarchical organization (tree structure)  
**Part B**: Shared groups/employees organization (graph structure)  
**Part C**: Thread-safe concurrent updates (design approaches)  
**Part D**: Single-level flat organization (set operations)

---

## Part A: Hierarchical Organization (Tree Structure)

### Problem Statement

- Tree-like organizational hierarchy
- Each group can have multiple subgroups
- Each employee belongs to exactly one group
- Find the closest common parent group for target employees

### Algorithm: Lowest Common Ancestor (LCA)

**Intuition**: In a tree structure, the "closest common group" is the deepest node that is an ancestor of all target employees' groups.

**Implementation Strategy**:

1. **Build Parent Pointers**: Create navigation structure from child to parent
2. **Path to Root**: For each target employee, find path from their group to root
3. **Find Intersection**: Identify the deepest common group in all paths

```python
def find_closest_common_group(employee_ids):
    # Get groups for each employee
    employee_groups = [get_employee_group(emp) for emp in employee_ids]

    # Get paths to root for each group
    paths = [get_path_to_root(group) for group in employee_groups]

    # Find LCA using path intersection
    return find_lca_from_paths(paths)
```

**Time Complexity**: `O(n + h×k)` where n=groups, h=height, k=target employees  
**Space Complexity**: `O(n + h×k)` for parent pointers and paths

**Key Insight**: Works correctly even with uneven path lengths because LCA cannot be deeper than the shallowest employee's level.

### When to Use Part A:

- Clear hierarchical structure with single reporting lines
- Traditional corporate org charts
- Department → Team → Subteam structures
- Need guaranteed unique result

---

## Part B: Shared Groups Organization (Graph Structure)

### Problem Statement

- Groups can be shared across different parts of organization
- Employees can belong to multiple groups
- Return ONE closest common group when multiple exist

### Algorithm: Multi-Source BFS

**Intuition**: With shared groups, we have a graph structure. "Closest" means minimum distance to the farthest employee.

**Why Not LCA?**

- LCA assumes tree structure with single parent per node
- Shared groups create cycles and multiple paths
- Need distance-based definition of "closest"

**Implementation Strategy**:

1. **Starting Points**: Find ALL groups each target employee belongs to
2. **Simultaneous BFS**: Start BFS from all employee groups simultaneously
3. **Convergence Detection**: Track which groups are reached by each employee's BFS
4. **First Common Group**: First group reached by ALL employees is closest

```python
def find_closest_common_group(employee_ids):
    # Collect starting groups for each employee
    employee_start_groups = {emp: get_employee_groups(emp) for emp in employee_ids}

    # Run multi-source BFS to find first convergence point
    return multi_source_bfs(employee_start_groups)
```

**Time Complexity**: `O(V + E + k×V)` where V=groups, E=connections, k=employees  
**Space Complexity**: `O(V + E + k×V)` for graph storage and BFS state

**Key Insight**: First convergence point gives deterministic result and handles any graph topology.

### When to Use Part B:

- Matrix organizations with shared teams
- Cross-functional groups
- Modern agile organizations
- Employees with multiple roles/responsibilities

---

## Part C: Thread-Safe Concurrent Updates (Design Approaches)

### Problem Statement

- 4 dynamic update methods running in separate threads
- `getCommonGroupForEmployees()` called during updates
- Must always reflect latest consistent state
- Efficient read/write handling required

### Approach 1: Read-Write Locks (ReentrantReadWriteLock)

**Strategy**: Separate read and write access with shared read, exclusive write

```python
class ThreadSafeOrganization:
    def __init__(self):
        self.rw_lock = ReadWriteLock()
        self.organization_data = {}

    def get_common_group(self, employees):
        with self.rw_lock.read_lock():
            return self._find_common_group_internal(employees)

    def update_structure(self, operation):
        with self.rw_lock.write_lock():
            self._apply_update_internal(operation)
```

**Pros**:

- Multiple concurrent reads allowed
- Strong consistency guarantees
- Simple to implement and reason about
- Read performance scales with CPU cores

**Cons**:

- Writers block all readers (latency spikes)
- Potential for writer starvation
- Lock contention under heavy read load
- Risk of deadlocks with complex operations

**Best For**: Read-heavy workloads with infrequent updates

### Approach 2: Copy-on-Write (Immutable Data Structures)

**Strategy**: Create new versions on writes, readers use immutable snapshots

```python
class CopyOnWriteOrganization:
    def __init__(self):
        self.current_version = AtomicReference(OrganizationSnapshot())

    def get_common_group(self, employees):
        snapshot = self.current_version.get()
        return snapshot.find_common_group(employees)

    def update_structure(self, operation):
        while True:
            current = self.current_version.get()
            new_version = current.apply_update(operation)
            if self.current_version.compare_and_set(current, new_version):
                break
```

**Pros**:

- Lock-free reads (zero contention)
- Excellent read scalability
- No blocking between reads and writes
- Natural snapshot isolation

**Cons**:

- Memory overhead (multiple versions)
- Write amplification (copy entire structure)
- Complex garbage collection
- Eventual consistency during updates

**Best For**: High-frequency reads with predictable update patterns

### Approach 3: Versioned State with MVCC

**Strategy**: Multi-Version Concurrency Control with timestamped versions

```python
class MVCCOrganization:
    def __init__(self):
        self.versions = {}  # timestamp -> organization_state
        self.current_version = 0
        self.version_lock = Lock()

    def get_common_group(self, employees):
        read_version = self.get_read_version()
        return self.versions[read_version].find_common_group(employees)

    def update_structure(self, operation):
        with self.version_lock:
            new_version = self.current_version + 1
            self.versions[new_version] = self.apply_update(operation)
            self.current_version = new_version
            self.cleanup_old_versions()
```

**Pros**:

- Non-blocking reads at specific versions
- Snapshot isolation guarantees
- Configurable consistency levels
- Supports time-travel queries

**Cons**:

- Complex version management
- Storage overhead for multiple versions
- Cleanup complexity
- Potential memory leaks if not managed properly

**Best For**: Systems requiring point-in-time consistency or audit trails

### Approach 4: Optimistic Concurrency with STM

**Strategy**: Software Transactional Memory with conflict detection

```python
@transactional
def get_common_group(self, employees):
    return self.organization.find_common_group(employees)

@transactional
def update_structure(self, operation):
    self.organization.apply_update(operation)
```

**Pros**:

- Automatic conflict detection and retry
- Composable transactions
- No explicit locking required
- Good for complex operations

**Cons**:

- Retry overhead under high contention
- Complex debugging (hidden retries)
- Performance unpredictability
- Limited language/library support

**Best For**: Complex business logic with low contention

### Approach 5: Event-Driven Architecture

**Strategy**: Async updates through event queue, eventual consistency

```python
class EventDrivenOrganization:
    def __init__(self):
        self.read_model = OrganizationReadModel()
        self.event_queue = AsyncQueue()
        self.processor = EventProcessor(self.event_queue, self.read_model)

    def get_common_group(self, employees):
        return self.read_model.find_common_group(employees)

    def update_structure(self, operation):
        event = StructureUpdateEvent(operation)
        self.event_queue.publish(event)
```

**Pros**:

- Excellent read performance (no locks)
- Natural decoupling of reads/writes
- Scalable architecture
- Audit trail built-in

**Cons**:

- Eventual consistency (stale reads possible)
- Complex error handling
- Ordering guarantees needed
- Higher architectural complexity

**Best For**: High-scale systems where eventual consistency is acceptable

### Recommendation Matrix

| Requirement                | Best Approach    | Rationale                                |
| -------------------------- | ---------------- | ---------------------------------------- |
| Strong Consistency         | Read-Write Locks | Immediate consistency, simpler reasoning |
| High Read Volume           | Copy-on-Write    | Lock-free reads, excellent scalability   |
| Audit Requirements         | MVCC             | Built-in versioning and history          |
| Complex Business Logic     | STM              | Composable transactions                  |
| Microservices Architecture | Event-Driven     | Natural service boundaries               |

---

## Part D: Single-Level Organization (Set Operations)

### Problem Statement

- Flat organization with no subgroups
- Each group has a set of employees
- Find group(s) containing ALL target employees

### Algorithm: Set Intersection

**Intuition**: Without hierarchy, "closest common group" becomes "which group(s) contain ALL target employees?"

**Implementation Strategy**:

1. **Membership Check**: For each group, verify it contains all target employees
2. **Tie-Breaking**: Apply strategy when multiple groups qualify
3. **Result**: Return selected group or indicate no common group exists

```python
def find_common_groups(employee_ids):
    common_groups = []
    for group in self.groups.values():
        if group.contains_all_employees(employee_ids):
            common_groups.append(group)
    return common_groups
```

**Tie-Breaking Strategies**:

- **Smallest Group**: Most specific (fewest total employees)
- **Alphabetical**: Deterministic selection
- **First Found**: Fastest execution
- **All Groups**: Return all qualifying (let caller decide)

**Time Complexity**: `O(G × k)` where G=groups, k=target employees  
**Space Complexity**: `O(G + E)` where E=total employees

### When to Use Part D:

- Flat organizational structures
- Project-based teams
- Simple role-based access control
- Startup organizations

---

## Complexity Analysis Summary

| Part             | Time Complexity    | Space Complexity   | Best For               |
| ---------------- | ------------------ | ------------------ | ---------------------- |
| A: Hierarchical  | O(n + h×k)         | O(n + h×k)         | Traditional org charts |
| B: Shared Groups | O(V + E + k×V)     | O(V + E + k×V)     | Matrix organizations   |
| C: Thread-Safe   | Varies by approach | Varies by approach | Production systems     |
| D: Single-Level  | O(G × k)           | O(G + E)           | Flat structures        |

Where: n=groups, h=height, V=vertices, E=edges, k=target employees, G=groups

---

## Implementation Files

- `part_a_hierarchical_org.py`: Complete LCA implementation with test cases
- `part_b_shared_groups.py`: Multi-source BFS with graph structure
- `part_d_single_level.py`: Set operations with tie-breaking strategies
- `readme.md`: This comprehensive documentation

---

## Key Insights & Design Principles

### 1. **Data Structure Drives Algorithm Choice**

- **Tree** → LCA algorithm
- **Graph** → BFS/shortest path algorithms
- **Flat** → Set operations

### 2. **Concurrency Patterns Have Clear Tradeoffs**

- **Consistency vs Performance**: Stronger consistency often reduces performance
- **Read vs Write Optimization**: Most systems are read-heavy, optimize accordingly
- **Complexity vs Control**: Simpler approaches are easier to debug and maintain

### 3. **Scalability Considerations**

- **Employee Growth**: Algorithms should handle organization scaling
- **Query Patterns**: Design for actual usage patterns (reads vs writes)
- **Caching Opportunities**: Common queries can be precomputed

### 4. **Real-World Applicability**

Each part addresses different organizational realities:

- **Part A**: Traditional hierarchies (banks, government)
- **Part B**: Modern tech companies (matrix structures)
- **Part C**: Production systems (reliability requirements)
- **Part D**: Small companies/startups (simple structures)

---

## Testing Strategy

All implementations include comprehensive test suites covering:

- **Edge Cases**: Single employee, no common group, deep hierarchies
- **Performance**: Large organizations, many target employees
- **Correctness**: Verify against manual calculations
- **Concurrency**: Thread safety verification (Part C approaches)
