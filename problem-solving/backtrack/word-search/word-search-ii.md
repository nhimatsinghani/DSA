## Word Search II – Trie-based Optimization (Intuition and Complexity)

### Problem

Given an m x n character `board` and a list of `words`, return all words that can be formed by sequentially adjacent (up, down, left, right) letters on the board. A cell cannot be reused within the same word.

### Why a Trie helps

- **Multi-word search in one pass**: Insert all `words` into a Trie. Then run a single DFS from each board cell, walking the Trie at the same time. You avoid running a full single-word search for each word.
- **Prefix pruning**: If the path built from the board is not a prefix of any word, the Trie tells you immediately—stop exploring that branch.
- **Shared prefixes searched once**: Words share Trie nodes for shared prefixes, so the search work for common starts is reused.
- **On-the-fly dedup**: When you reach a Trie node that marks a complete word, record it and clear the marker to avoid duplicates.
- **Dead-leaf pruning (optional)**: After exploring, if a Trie node has no children and isn’t a word-end anymore, remove it. This shrinks the search space as you go.

### Algorithm (high level)

1. Build a Trie for all `words`. Each node stores `children: char -> node` and optionally `word` when the node terminates a word.
2. For each cell `(r, c)` in `board`:
   - If `board[r][c]` isn’t a child of the current Trie node, stop this path.
   - Otherwise move into that child; if `node.word` is set, add to results and clear it.
   - Mark `(r, c)` as visited (e.g., set `'#'`), recurse into its 4 neighbors, then restore the character.
   - Optionally prune empty Trie nodes to save future work.

### Pseudocode

```
root = buildTrie(words)
result = []
for each cell (r, c) on board:
    backtrack(r, c, root)

backtrack(r, c, parent):
    ch = board[r][c]
    if ch not in parent.children: return
    node = parent.children[ch]

    if node.word != null:
        result.add(node.word)
        node.word = null   # de-duplicate

    board[r][c] = '#'
    for each (nr, nc) in four_neighbors(r, c):
        if inBounds and board[nr][nc] != '#':
            backtrack(nr, nc, node)
    board[r][c] = ch

    if node.children is empty and node.word is null:
        remove parent.children[ch]  # dead-leaf pruning
```

### Complexity

Let:

- **B = m × n**: number of board cells
- **L**: maximum word length
- **S**: total number of characters across all words

- **Build Trie**: O(S)
- **Search**: In the worst case, a path can extend at most L steps; from the first step you may have up to 4 directions, and subsequently up to 3 (cannot go back to the cell you just came from). This yields a common bound: **O(B × 4 × 3^(L−1))**.
  - Crucially, this bound is independent of the number of words W. Without the Trie, you would roughly do that DFS for each word separately (multiplying by W). With the Trie, you unify them into one pass and prune aggressively.
- **Space**: O(S) for the Trie, plus O(L) recursion stack, and O(1) extra board space (in-place visited marks).

### Why it’s faster than naive

- **Naive** (per-word search): Σ over words w of O(B × 4 × 3^(|w|−1))
- **Trie-based** (combined search): O(B × 4 × 3^(L−1))

The Trie eliminates the multiplicative factor by the number of words, and prefix pruning/dead-leaf pruning reduce the branching dramatically in practice.

### Practical notes

- Mutate the board to mark visited (e.g., `'#'`) and restore after recursion; this avoids extra memory.
- Clearing `node.word` after recording prevents duplicates for words found via different paths.
- Dead-leaf pruning speeds things up when many words are found early and share prefixes.
- Return order of results is not guaranteed; sort at the end if order matters to you.

### Example

Board:

```
[
  ["o","a","a","n"],
  ["e","t","a","e"],
  ["i","h","k","r"],
  ["i","f","l","v"],
]
```

Words: `["oath", "pea", "eat", "rain"]`

The search naturally follows prefixes `o→a→t→h` (finds `oath`) and `e→a→t` (finds `eat`), while other branches are pruned as soon as they stop matching any Trie prefix.
