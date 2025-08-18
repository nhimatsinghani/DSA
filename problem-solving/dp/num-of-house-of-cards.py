# Description
# You are given an integer n representing the number of playing cards you have. A house of cards meets the following conditions:

# A house of cards consists of one or more rows of triangles and horizontal cards.
# Triangles are created by leaning two cards against each other.
# One card must be placed horizontally between all adjacent triangles in a row.
# Any triangle on a row higher than the first must be placed on a horizontal card from the previous row.
# Each triangle is placed in the leftmost available spot in the row.
# Return the number of distinct house of cards you can build using all n cards. Two houses of cards are considered distinct if there exists a row where the two houses contain a different number of cards.

# We notice that the number of cards in each layer is 3×k+2, and the number of cards in each layer is different. Therefore, the problem can be transformed into: how many ways can the integer n be expressed as the sum of numbers of the form 3×k+2. This is a classic knapsack problem that can be solved using memoization search.

# We design a function dfs(n,k), which represents the number of ways to build different houses of cards when the remaining number of cards is n and the current layer is k. The answer is 
# dfs(n,0).

# The execution logic of the function 
# dfs(n,k)
#  is as follows:

# If 3×k+2>n, then the current layer cannot place any cards, return 0;If 3×k+2=n, then the current layer can place cards, and after placing them, the entire house of cards is completed, return 1;
# Otherwise, we can choose not to place cards or to place cards. If we choose not to place cards, the remaining number of cards does not change, and the number of layers increases by 1, i.e., 
# dfs(n,k+1). If we choose to place cards, the remaining number of cards decreases by 3×k+2, and the number of layers increases by 1,i.e., 
# dfs(n−(3×k+2),k+1). The sum of these two cases is the answer
from functools import lru_cache


def count_houses_k(n: int) -> int:
    """
    Count the number of distinct houses using all n cards via a memoized DFS with the 3k+2 formulation.

    Intuition:
    - A row with r triangles uses 2r leaning + (r-1) horizontal = 3r-1 cards.
    - Let k = r - 1, then 3r-1 = 3(k+1)-1 = 3k+2. Row costs are {2, 5, 8, ...}.
    - Each row size can be used at most once (rows strictly decrease going up), so we decide to include/skip each distinct cost exactly once.

    Recurrence (k-based):
    - s = 3k + 2
    - if s > remaining: 0
    - if s == remaining: 1
    - else: dfs(remaining, k+1) [skip] + dfs(remaining - s, k+1) [take]
    """
    @lru_cache(maxsize=None)
    def dfs(remaining: int, k: int) -> int:
        size = 3 * k + 2
        if size > remaining:
            return 0
        if size == remaining:
            return 1
        return dfs(remaining, k + 1) + dfs(remaining - size, k + 1)

    return dfs(n, 0)


def count_houses_r(n: int) -> int:
    """
    Count the number of distinct houses using all n cards via a memoized DFS with the 3r-1 formulation.

    Intuition:
    - Model directly by triangles per row, r >= 1. Row cost is cost(r) = 3r - 1.
    - Decisions are 0/1: for each r (in increasing order), either skip cost(r) or include it once.
    - This is equivalent to the 3k+2 formulation with r = k + 1; both yield identical counts.

    Recurrence (r-based):
    - c = 3r - 1
    - if c > remaining: 0
    - if c == remaining: 1
    - else: dfs(remaining, r+1) [skip] + dfs(remaining - c, r+1) [take]
    """
    @lru_cache(maxsize=None)
    def dfs(remaining: int, r: int) -> int:
        cost = 3 * r - 1
        if cost > remaining:
            return 0
        if cost == remaining:
            return 1
        return dfs(remaining, r + 1) + dfs(remaining - cost, r + 1)

    return dfs(n, 1)


if __name__ == "__main__":
    # Small demo to show equivalence of both formulations on a few values
    samples = [2, 5, 7, 8, 11, 13, 14, 20, 25, 30]
    for value in samples:
        by_k = count_houses_k(value)
        by_r = count_houses_r(value)
        print(f"n={value}: 3k+2 -> {by_k}, 3r-1 -> {by_r}")
