# Time Complexity Analysis for Recursive & Backtracking Algorithms

## Table of Contents

1. [Framework for Analysis](#framework-for-analysis)
2. [Key Concepts](#key-concepts)
3. [Detailed Examples](#detailed-examples)
4. [Common Patterns](#common-patterns)
5. [Quick Analysis Methodology](#quick-analysis-methodology)

---

## Framework for Analysis

When analyzing recursive/backtracking algorithms, follow this systematic approach:

```
Time Complexity = (Number of Nodes in Recursion Tree) × (Work per Node)
```

### The 3-Step Analysis Method:

1. **Identify the Recursion Tree Structure**

   - What's the branching factor at each level?
   - What's the maximum depth?
   - How many total nodes are there?

2. **Calculate Work per Node**

   - What operations happen at each recursive call?
   - Are there loops inside the recursive function?

3. **Combine for Total Complexity**
   - Multiply nodes × work per node
   - Consider any additional space/time for storing results

---

## Key Concepts

### 1. Branching Factor

- **Definition**: Number of recursive calls made from each node
- **Variable vs Constant**: Can change by level or remain constant

### 2. Depth of Recursion

- **Definition**: Maximum number of recursive calls in the call stack
- **Usually relates to**: Input constraints (n, k, array length, etc.)

### 3. Work per Node

- **Definition**: Time spent at each recursive call (excluding recursive calls)
- **Common operations**: Loops, copying arrays, checking conditions

### 4. Tree Shapes

- **Complete Tree**: All levels fully filled
- **Pruned Tree**: Some branches cut short due to constraints
- **Asymmetric Tree**: Different branching at different levels

---

## Detailed Examples

### Example 1: Combinations (n choose k)

```python
def combine(n, k):
    result = []

    def backtrack(start, path):
        # Base case
        if len(path) == k:
            result.append(path[:])  # Work: O(k) to copy
            return

        # Recursive case
        for i in range(start, n + 1):  # Branching factor varies
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return result
```

#### Step-by-Step Analysis:

**1. Recursion Tree Structure:**

```
Level 0: backtrack(1, [])
Level 1: backtrack(2,[1]), backtrack(3,[1]), ..., backtrack(n+1,[1])
Level 2: From backtrack(2,[1]): backtrack(3,[1,2]), backtrack(4,[1,2]), ...
...
Level k: Base case reached
```

**2. Branching Factor Analysis:**

- Level 0: n choices (1 to n)
- Level 1: (n-1) choices on average
- Level 2: (n-2) choices on average
- ...
- Level i: (n-i) choices on average

**3. Depth:** k levels (until we collect k elements)

**4. Number of Nodes:**

- This forms a tree where we're essentially choosing k items from n
- Total recursive calls ≈ C(n,k) = n!/(k!(n-k)!)
- More precisely: Sum over all partial combinations

**5. Work per Node:**

- At non-leaf nodes: O(1) (just append/pop)
- At leaf nodes: O(k) (copy the path)

**Final Time Complexity: O(C(n,k) × k) = O(n!/(k!(n-k)!) × k)**

---

### Example 2: Permutations of Distinct Elements

```python
def permute(nums):
    result = []

    def backtrack(path):
        # Base case
        if len(path) == len(nums):
            result.append(path[:])  # Work: O(n) to copy
            return

        # Try each remaining number
        for i in range(len(nums)):
            if nums[i] in path:  # Work: O(n) to check
                continue
            path.append(nums[i])
            backtrack(path)
            path.pop()

    backtrack([])
    return result
```

#### Step-by-Step Analysis:

**1. Recursion Tree Structure:**

```
Level 0: [] (n choices)
Level 1: [1], [2], [3], ... (n-1 choices each)
Level 2: [1,2], [1,3], [2,1], [2,3], [3,1], [3,2] (n-2 choices each)
...
Level n: Complete permutations
```

**2. Branching Factor:**

- Level 0: n choices
- Level 1: (n-1) choices
- Level 2: (n-2) choices
- ...
- Level i: (n-i) choices

**3. Total Nodes in Tree:**

- Level 0: 1 node
- Level 1: n nodes
- Level 2: n × (n-1) nodes
- ...
- Level i: n × (n-1) × ... × (n-i+1) nodes
- Total nodes = 1 + n + n×(n-1) + ... + n! ≈ O(n!)

**4. Work per Node:**

- Check if element in path: O(n)
- Copy path at leaf: O(n)
- Other operations: O(1)

**Final Time Complexity: O(n! × n)**

---

### Example 3: N-Queens Problem

```python
def solveNQueens(n):
    result = []
    board = ['.' * n for _ in range(n)]

    def backtrack(row):
        if row == n:
            result.append([''.join(row) for row in board])  # O(n²)
            return

        for col in range(n):
            if is_safe(row, col):  # O(n) to check conflicts
                board[row] = board[row][:col] + 'Q' + board[row][col+1:]
                backtrack(row + 1)
                board[row] = board[row][:col] + '.' + board[row][col+1:]

    def is_safe(row, col):
        # Check column and diagonals - O(n) work
        for i in range(row):
            if (board[i][col] == 'Q' or
                (col - (row - i) >= 0 and board[i][col - (row - i)] == 'Q') or
                (col + (row - i) < n and board[i][col + (row - i)] == 'Q')):
                return False
        return True

    backtrack(0)
    return result
```

#### Step-by-Step Analysis:

**1. Recursion Tree Structure:**

```
Level 0: Place queen in row 0 (n choices)
Level 1: Place queen in row 1 (≤ n choices, but many pruned)
Level 2: Place queen in row 2 (≤ n choices, heavily pruned)
...
Level n: Solution found (or backtrack)
```

**2. Branching Factor:**

- Level 0: n choices
- Level 1: Much fewer due to conflicts (roughly n/2 on average)
- Level 2: Even fewer (roughly n/4 on average)
- **Key insight**: Heavy pruning occurs due to constraints

**3. Estimated Nodes:**

- Worst case (no pruning): n^n
- Actual case: Much less due to constraint propagation
- **Practical complexity**: O(n!)

**4. Work per Node:**

- `is_safe()` check: O(n)
- Board manipulation: O(n)
- Solution copying: O(n²)

**Final Time Complexity: O(n! × n)**

---

### Example 4: Permutations with Duplicates

```python
def permuteUnique(nums):
    result = []
    nums.sort()  # Important for handling duplicates
    used = [False] * len(nums)

    def backtrack(path):
        if len(path) == len(nums):
            result.append(path[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue
            # Skip duplicates: if current element equals previous
            # and previous is not used, skip current
            if i > 0 and nums[i] == nums[i-1] and not used[i-1]:
                continue

            used[i] = True
            path.append(nums[i])
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return result
```

#### Analysis:

**Key Difference**: The duplicate-skipping logic reduces the branching factor significantly.

- **Without duplicates**: O(n! × n)
- **With duplicates**: O(unique_permutations × n)
- **Practical bound**: Still O(n! × n) in worst case, but much better on average

---

## Common Patterns

### Pattern 1: Complete Enumeration

- **Examples**: All permutations, all subsets
- **Complexity**: Usually O(2^n) or O(n!)
- **Tree shape**: Complete or nearly complete

### Pattern 2: Constrained Search

- **Examples**: N-Queens, Sudoku, Valid combinations
- **Complexity**: Better than complete enumeration due to pruning
- **Tree shape**: Heavily pruned

### Pattern 3: Path Building

- **Examples**: Finding all paths, combinations
- **Complexity**: Depends on number of valid paths
- **Work per node**: Often includes path copying O(path_length)

### Pattern 4: Decision Trees

- **Examples**: Subset sum, knapsack variations
- **Complexity**: O(2^n) for binary decisions
- **Tree shape**: Binary tree structure

---

## Quick Analysis Methodology

### Step 1: Identify the Pattern

```
□ Complete Enumeration (generate all possibilities)
□ Constrained Search (heavy pruning expected)
□ Path Building (building/maintaining paths)
□ Decision Tree (binary choices at each step)
```

### Step 2: Quick Branching Factor Analysis

```
At each level, how many recursive calls?
- Constant b: O(b^depth)
- Decreasing (n, n-1, n-2, ...): O(n!)
- Variable with constraints: Analyze case by case
```

### Step 3: Quick Work Analysis

```
What happens at each node besides recursion?
- Simple operations: O(1)
- Linear search/copy: O(n)
- Path copying: O(path_length)
- Complex validation: Analyze separately
```

### Step 4: Combine and Estimate

```
Time = (Nodes in tree) × (Work per node)

Common results:
- O(2^n): Binary decisions, subsets
- O(n!): Permutations, heavily branching
- O(n^n): Worst case with n choices at n levels
- O(C(n,k)): Combinations
```

### Quick Reference Table

| Problem Type        | Typical Complexity | Key Insight                      |
| ------------------- | ------------------ | -------------------------------- |
| All Subsets         | O(2^n × n)         | Binary choice for each element   |
| All Permutations    | O(n! × n)          | n choices, then n-1, then n-2... |
| Combinations C(n,k) | O(C(n,k) × k)      | Choose k from n                  |
| N-Queens            | O(n!)              | Heavy constraint pruning         |
| Sudoku              | O(9^(empty_cells)) | 9 choices per empty cell         |
| Path Finding        | O(b^d)             | b = branching factor, d = depth  |

### Red Flags (Check These!)

- ✅ Are you copying paths/results? Add that cost!
- ✅ Are there nested loops inside recursion? Multiply!
- ✅ Are constraints significantly pruning the tree? Complexity might be much better!
- ✅ Is the branching factor changing at each level? Don't assume constant!

---

## Practice Problems

Try analyzing these step by step:

1. **Word Search II**: Find all words from a dictionary in a 2D board
2. **Generate Parentheses**: Generate all valid parentheses combinations
3. **Palindrome Partitioning**: Partition string into palindromes
4. **Restore IP Addresses**: Generate all valid IP addresses from string
5. **Combination Sum**: Find all combinations that sum to target

For each, identify:

- Branching factor pattern
- Maximum depth
- Work per node
- Final complexity

Remember: **The key is systematic analysis, not memorization!**
