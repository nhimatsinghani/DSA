from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Set

try:
    from sortedcontainers import SortedList  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    SortedList = None  # type: ignore


@dataclass(frozen=True)
class FileRecord:
    name: str
    size: int
    collections: Tuple[str, ...]


class FileSystemAggregator:
    """Aggregates total file size and per-collection sizes.

    Part 1:
    - Add files and compute total and top-K collections

    Part 2 additions:
    - Same file can belong to multiple collections
    - Support updating a file already processed (size and/or collections)
      with correct delta adjustments to totals and collection sizes.
    """

    def __init__(self) -> None:
        self._total_size: int = 0
        self._collection_to_size: Dict[str, int] = {}
        # Optional optimized index: (-size, name) sorted ascending to simulate desc by size
        self._sorted_index: Optional[SortedList] = SortedList() if SortedList is not None else None  # type: ignore
        self._current_key_by_collection: Dict[str, Tuple[int, str]] = {}
        # Track files by name for updates
        self._files: Dict[str, FileRecord] = {}

    def _apply_collection_delta(self, collection: str, delta: int) -> None:
        if delta == 0:
            return
        new_size = self._collection_to_size.get(collection, 0) + delta
        self._collection_to_size[collection] = new_size
        if self._sorted_index is not None:
            old_key = self._current_key_by_collection.get(collection)
            if old_key is not None:
                try:
                    self._sorted_index.remove(old_key)  # type: ignore[attr-defined]
                except ValueError:
                    pass
            new_key = (-new_size, collection)
            self._sorted_index.add(new_key)  # type: ignore[attr-defined]
            self._current_key_by_collection[collection] = new_key

    def add_file(self, name: str, size: int, collections: Optional[Iterable[str]] = None) -> None:
        if size < 0:
            raise ValueError("size must be non-negative")
        if name in self._files:
            # For backward-compat, treat as update to avoid double counting
            self.update_file(name, size, collections)
            return
        col_tuple: Tuple[str, ...] = tuple(collections) if collections else tuple()
        record = FileRecord(name=name, size=size, collections=col_tuple)
        # Update totals
        self._total_size += size
        # Update collections (supports multiple)
        for col in col_tuple:
            self._apply_collection_delta(col, size)
        # Persist record
        self._files[name] = record

    def update_file(self, name: str, new_size: int, new_collections: Optional[Iterable[str]] = None) -> None:
        if new_size < 0:
            raise ValueError("new_size must be non-negative")
        old = self._files.get(name)
        if old is None:
            # If not present, treat as add
            self.add_file(name, new_size, new_collections)
            return
        old_cols: Set[str] = set(old.collections)
        new_cols: Set[str] = set(tuple(new_collections) if new_collections is not None else old.collections)

        # Total size delta
        size_delta = new_size - old.size
        if size_delta != 0:
            self._total_size += size_delta

        # Collections adjustments
        # 1) Collections present in both: apply size delta
        for col in (old_cols & new_cols):
            if size_delta != 0:
                self._apply_collection_delta(col, size_delta)
        # 2) Collections removed: subtract old size
        for col in (old_cols - new_cols):
            self._apply_collection_delta(col, -old.size)
        # 3) Collections added: add new size
        for col in (new_cols - old_cols):
            self._apply_collection_delta(col, new_size)

        # Save updated record
        self._files[name] = FileRecord(name=name, size=new_size, collections=tuple(new_cols))

    def get_total_size(self) -> int:
        return self._total_size

    def top_k_collections(self, k: int) -> List[Tuple[str, int]]:
        if k <= 0:
            return []
        # Sort by size desc, then name asc for deterministic output
        items = sorted(self._collection_to_size.items(), key=lambda kv: (-kv[1], kv[0]))
        return items[:k]

    def top_k_collections_optimized(self, k: int) -> List[Tuple[str, int]]:
        """Return top-K using SortedList if available; fallback to baseline otherwise."""
        if k <= 0:
            return []
        if self._sorted_index is None:
            return self.top_k_collections(k)
        # First k entries from (-size, name)
        sliced = list(self._sorted_index)[:k]  # type: ignore[arg-type]
        return [(name, -neg_size) for (neg_size, name) in sliced] 