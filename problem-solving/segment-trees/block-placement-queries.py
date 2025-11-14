# There exists an infinite number line, with its origin at 0 and extending towards the positive x-axis.

# You are given a 2D array queries, which contains two types of queries:

# For a query of type 1, queries[i] = [1, x]. Build an obstacle at distance x from the origin. It is guaranteed that there is no obstacle at distance x when the query is asked.
# For a query of type 2, queries[i] = [2, x, sz]. Check if it is possible to place a block of size sz anywhere in the range [0, x] on the line, such that the block entirely lies in the range [0, x]. A block cannot be placed if it intersects with any obstacle, but it may touch it. Note that you do not actually place the block. Queries are separate.
# Return a boolean array results, where results[i] is true if you can place the block specified in the ith query of type 2, and false otherwise.

 

# Example 1:

# Input: queries = [[1,2],[2,3,3],[2,3,1],[2,2,2]]

# Output: [false,true,true]

# Explanation:

# For query 0, place an obstacle at x = 2. A block of size at most 2 can be placed before x = 3.

# -------------------------------------------------------------
# Intuition and Approaches
# -------------------------------------------------------------
# Think of obstacles as points on [0, +inf). For a check query [2, x, sz],
# we ask whether there exists a gap of length >= sz fully inside [0, x]
# that does not intersect any obstacle (touching allowed).
#
# Equivalently, among the gaps formed by consecutive obstacles up to x,
# including the edges [0, firstObstacle] and [lastObstacle, x], is the
# maximum gap length >= sz?
#
# Brute force approach (baseline):
# - Maintain a sorted list of obstacle positions.
# - Update [1, x]: insert x into the sorted list (bisect.insort).
# - Query [2, x, sz]: find how many obstacles <= x, then scan those to compute
#   the maximum gap inside [0, x]. This can be O(k) per query where k is the
#   number of obstacles <= x (worst-case O(n)).
#
# Segment tree approach (optimized):
# - We want to answer "max gap in prefix [0, x]" quickly, with point updates.
# - Each segment tree node stores a small summary that is mergeable:
#   (firstObstacle, lastObstacle, maxInternalGap) within its coordinate range.
# - Merging left L and right R:
#     first = L.first if L has any, else R.first
#     last  = R.last  if R has any, else L.last
#     best  = max(L.best, R.best, R.first - L.last) if both non-empty
# - On a query [2, x, sz], for the prefix [0..x]:
#     maxGap = max(prefix.best, prefix.first - 0, x - prefix.last)
#     If no obstacles in prefix, maxGap = x.
# - Use coordinate compression over all x appearing in queries (plus 0).
# - Updates and queries run in O(log N) where N is number of distinct coords.

from bisect import bisect_right, insort
from dataclasses import dataclass
from typing import List, Tuple


# -------------------------------------------------------------
# Brute-force implementation
# -------------------------------------------------------------

def process_queries_bruteforce(queries: List[List[int]]) -> List[bool]:
    """
    Process queries using a sorted list of obstacles.

    Type 1: [1, x] -> insert obstacle at x
    Type 2: [2, x, sz] -> return True/False for feasibility within [0, x]
    Returns list of booleans for each type-2 query in order.
    """
    obstacles: List[int] = []  # sorted
    results: List[bool] = []

    for q in queries:
        if q[0] == 1:
            # Insert obstacle at x
            x = q[1]
            insort(obstacles, x)
        else:
            # Query feasibility [0, x] for block size sz
            _, x, sz = q
            # Consider only obstacles <= x
            k = bisect_right(obstacles, x)
            if k == 0:
                # No obstacles within [0, x]
                results.append(x >= sz)
                continue

            max_gap = max(obstacles[0] - 0, x - obstacles[k - 1])
            for i in range(1, k):
                gap = obstacles[i] - obstacles[i - 1]
                if gap > max_gap:
                    max_gap = gap
            results.append(max_gap >= sz)

    return results


# -------------------------------------------------------------
# Segment Tree implementation (with coordinate compression)
# -------------------------------------------------------------

INF = float('inf')


@dataclass
class Node:
    first: float = INF
    last: float = -INF
    best: int = 0  # maximum internal gap fully inside this node's range

    @property
    def is_empty(self) -> bool:
        return self.first == INF


def merge_nodes(left: Node, right: Node) -> Node:
    if left.is_empty:
        return right
    if right.is_empty:
        return left
    cross = right.first - left.last
    if cross < 0:
        # Should not happen with consistent coordinate compression and updates,
        # but guard anyway.
        cross = 0
    return Node(
        first=left.first,
        last=right.last,
        best=max(left.best, right.best, int(cross)),
    )


class SegmentTree:
    def __init__(self, size: int):
        self.n = 1
        while self.n < size:
            self.n <<= 1
        self.tree: List[Node] = [Node() for _ in range(2 * self.n)]

    def update(self, idx: int, value: Node) -> None:
        i = idx + self.n
        self.tree[i] = value
        i //= 2
        while i >= 1:
            self.tree[i] = merge_nodes(self.tree[2 * i], self.tree[2 * i + 1])
            i //= 2

    def query(self, l: int, r: int) -> Node:
        # inclusive range query
        l += self.n
        r += self.n
        res_left = Node()
        res_right = Node()
        while l <= r:
            if (l & 1) == 1:
                res_left = merge_nodes(res_left, self.tree[l])
                l += 1
            if (r & 1) == 0:
                res_right = merge_nodes(self.tree[r], res_right)
                r -= 1
            l //= 2
            r //= 2
        return merge_nodes(res_left, res_right)


def process_queries_segment_tree(queries: List[List[int]]) -> List[bool]:
    """
    Optimized solution using a segment tree over coordinate-compressed positions.
    Each update sets a leaf to an obstacle at its exact coordinate.
    Each prefix query merges nodes and computes max gap inside [0, x].
    """
    # Coordinate compression: include all x and 0
    coords_set = {0}
    for q in queries:
        if q[0] == 1:
            coords_set.add(q[1])
        else:
            coords_set.add(q[1])  # x from type-2 query
    coords = sorted(coords_set)
    index_of = {v: i for i, v in enumerate(coords)}

    seg = SegmentTree(len(coords))

    results: List[bool] = []
    for q in queries:
        if q[0] == 1:
            x = q[1]
            i = index_of[x]
            seg.update(i, Node(first=x, last=x, best=0))
        else:
            _, x, sz = q
            i = index_of[x]
            prefix = seg.query(0, i)
            if prefix.is_empty:
                max_gap = x  # [0, x] is free
            else:
                left_edge = int(prefix.first - 0)
                right_edge = int(x - prefix.last)
                if left_edge < 0:
                    left_edge = 0
                if right_edge < 0:
                    right_edge = 0
                max_gap = max(prefix.best, left_edge, right_edge)
            results.append(max_gap >= sz)

    return results


# -------------------------------------------------------------
# Implicit Segment Tree (no coordinate compression)
# -------------------------------------------------------------

class ImplicitSegNode:
    def __init__(self, lo: int, hi: int):
        self.lo = lo
        self.hi = hi
        self.left = None  # type: ImplicitSegNode | None
        self.right = None  # type: ImplicitSegNode | None
        self.summary = Node()

    def _pull_up(self) -> None:
        left_summary = self.left.summary if self.left is not None else Node()
        right_summary = self.right.summary if self.right is not None else Node()
        self.summary = merge_nodes(left_summary, right_summary)

    def point_update(self, x: int) -> None:
        if self.lo == self.hi:
            self.summary = Node(first=self.lo, last=self.lo, best=0)
            return
        mid = (self.lo + self.hi) // 2
        if x <= mid:
            if self.left is None:
                self.left = ImplicitSegNode(self.lo, mid)
            self.left.point_update(x)
        else:
            if self.right is None:
                self.right = ImplicitSegNode(mid + 1, self.hi)
            self.right.point_update(x)
        self._pull_up()

    def range_query(self, ql: int, qr: int) -> Node:
        if qr < self.lo or ql > self.hi:
            return Node()
        if ql <= self.lo and self.hi <= qr:
            return self.summary
        left_summary = self.left.range_query(ql, qr) if self.left is not None else Node()
        right_summary = self.right.range_query(ql, qr) if self.right is not None else Node()
        return merge_nodes(left_summary, right_summary)


class ImplicitSegmentTree:
    def __init__(self):
        # Start with a small range and grow as needed.
        self.root = ImplicitSegNode(0, 1)

    def _ensure_cover(self, x: int) -> None:
        # Expand the tree's range to include x by doubling the range.
        while x > self.root.hi:
            new_hi = self.root.hi * 2
            new_root = ImplicitSegNode(0, new_hi)
            new_root.left = self.root
            new_root._pull_up()
            self.root = new_root

    def update(self, x: int) -> None:
        self._ensure_cover(x)
        self.root.point_update(x)

    def query_prefix(self, x: int) -> Node:
        self._ensure_cover(x)
        return self.root.range_query(0, x)


def process_queries_segment_tree_implicit(queries: List[List[int]]) -> List[bool]:
    """
    Segment tree version without coordinate compression using an implicit (dynamic) tree.
    The tree grows to cover new coordinates as they appear.
    """
    seg = ImplicitSegmentTree()
    results: List[bool] = []
    for q in queries:
        if q[0] == 1:
            x = q[1]
            seg.update(x)
        else:
            _, x, sz = q
            prefix = seg.query_prefix(x)
            if prefix.is_empty:
                max_gap = x
            else:
                left_edge = int(prefix.first)
                right_edge = int(x - prefix.last)
                if left_edge < 0:
                    left_edge = 0
                if right_edge < 0:
                    right_edge = 0
                max_gap = max(prefix.best, left_edge, right_edge)
            results.append(max_gap >= sz)
    return results


# -------------------------------------------------------------
# Demonstration
# -------------------------------------------------------------
if __name__ == "__main__":
    example = [[1, 2], [2, 3, 3], [2, 3, 1], [2, 2, 2]]
    expected = [False, True, True]
    out_brute = process_queries_bruteforce(example)
    out_seg = process_queries_segment_tree(example)
    out_simple = process_queries_segment_tree_implicit(example)
    print("Bruteforce:", out_brute)
    print("SegTree:   ", out_seg)
    print("Implicit:  ", out_simple)
    assert out_brute == expected, f"Bruteforce mismatch: {out_brute} != {expected}"
    assert out_seg == expected, f"SegmentTree mismatch: {out_seg} != {expected}"
    assert out_simple == expected, f"Implicit mismatch: {out_simple} != {expected}"
    print("Example passed.")