"""
Word Search II – Optimized solution using Trie + backtracking.

This module exposes `find_words` (snake_case) and `findWords` (LeetCode-style)
that return all words from the given list that can be formed on the board.

Approach:
- Build a Trie for all words to enable shared-prefix exploration
- Backtrack from each board cell, walking the Trie to prune dead branches early
- Mark found words at Trie nodes and prune empty leaves to reduce future work

Time complexity (informal):
- Build Trie: O(S) where S is total characters across all words
- Search: O(B * 4 * 3^(L-1)) in the worst case (B = m*n, L = max word length),
  typically much smaller due to prefix pruning and dead-leaf pruning

Space complexity: O(S) for the Trie, plus O(L) recursion stack
"""

from typing import Dict, List, Optional


class TrieNode:
    """A compact Trie node with dictionary children and optional stored word."""

    __slots__ = ("children", "word")

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.word: Optional[str] = None  # Marks end of a word; stores the full word


def _build_trie(words: List[str]) -> TrieNode:
    """Builds and returns the Trie root from the given list of words."""
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.word = word
    return root


def find_words(board: List[List[str]], words: List[str]) -> List[str]:
    """Finds all words on the board using a Trie-guided backtracking search.

    Args:
        board: 2D grid of lowercase characters.
        words: List of words to search for.

    Returns:
        A list of words found on the board. Order is not guaranteed.
    """
    if not board or not board[0] or not words:
        return []

    rows, cols = len(board), len(board[0])
    trie_root = _build_trie(words)
    found: List[str] = []

    def backtrack(row: int, col: int, parent: TrieNode) -> None:
        char = board[row][col]
        if char not in parent.children:
            return

        node = parent.children[char]

        # If a complete word is found at this node, collect and clear it to avoid duplicates
        if node.word is not None:
            found.append(node.word)
            node.word = None

        # Mark the cell as visited
        board[row][col] = "#"

        # Explore neighbors: up, down, left, right
        if row > 0 and board[row - 1][col] != "#":
            backtrack(row - 1, col, node)
        if row + 1 < rows and board[row + 1][col] != "#":
            backtrack(row + 1, col, node)
        if col > 0 and board[row][col - 1] != "#":
            backtrack(row, col - 1, node)
        if col + 1 < cols and board[row][col + 1] != "#":
            backtrack(row, col + 1, node)

        # Restore the cell
        board[row][col] = char

        # Optional pruning: remove leaf nodes to cut future searches
        if not node.children and node.word is None:
            parent.children.pop(char)

    for r in range(rows):
        for c in range(cols):
            backtrack(r, c, trie_root)

    return found


# LeetCode-style alias
findWords = find_words


if __name__ == "__main__":
    # Minimal manual test
    sample_board = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    sample_words = ["oath", "pea", "eat", "rain"]
    print(sorted(find_words([row[:] for row in sample_board], sample_words)))
