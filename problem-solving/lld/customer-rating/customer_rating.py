from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, Any
import heapq

try:
    from sortedcontainers import SortedList  # type: ignore
except Exception:  # pragma: no cover - optional dependency guard
    SortedList = None  # type: ignore

from datetime import datetime, timezone
import csv
import json

YearMonth = Tuple[int, int]


# ---------- File Export Abstractions ----------

class FileExporter(ABC):
    @abstractmethod
    def write(self, path: str, rows: List[Dict[str, Any]]) -> None:
        raise NotImplementedError


class CsvFileExporter(FileExporter):
    def __init__(self, header: List[str], include_header: bool = True) -> None:
        self._header = header
        self._include_header = include_header

    def write(self, path: str, rows: List[Dict[str, Any]]) -> None:
        # We expect rows to have keys: user_id, year, month, value
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if self._include_header:
                writer.writerow(self._header)
            for r in rows:
                writer.writerow([r["user_id"], r["year"], r["month"], r["value"]])


class JsonFileExporter(FileExporter):
    def __init__(self, pretty: bool = True) -> None:
        self._pretty = pretty

    def write(self, path: str, rows: List[Dict[str, Any]]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            if self._pretty:
                json.dump(rows, f, indent=2, sort_keys=False)
            else:
                json.dump(rows, f, separators=(",", ":"))


# ---------- Domain Entities ----------

@dataclass(frozen=True)
class RatingBounds:
    min_rating: float
    max_rating: float

    def __post_init__(self) -> None:
        if self.max_rating <= self.min_rating:
            raise ValueError("max_rating must be greater than min_rating")

    def validate_or_raise(self, rating: float) -> None:
        if rating < self.min_rating or rating > self.max_rating:
            raise ValueError(
                f"rating {rating} out of bounds [{self.min_rating}, {self.max_rating}]"
            )


@dataclass
class UserRatingStats:
    total_score: float = 0.0
    count: int = 0

    def add(self, rating: float) -> None:
        self.total_score += rating
        self.count += 1

    def average(self) -> Optional[float]:
        if self.count == 0:
            return None
        return self.total_score / float(self.count)


# ---------- Storage Abstraction ----------

class RatingStore(ABC):
    """Abstract store for user rating aggregates.

    Allows swapping in persistent or distributed backends later without
    changing business logic.
    """

    @abstractmethod
    def get(self, user_id: int) -> Optional[UserRatingStats]:
        raise NotImplementedError

    @abstractmethod
    def set(self, user_id: int, stats: UserRatingStats) -> None:
        raise NotImplementedError

    @abstractmethod
    def iter_all(self) -> Iterator[Tuple[int, UserRatingStats]]:
        raise NotImplementedError


class InMemoryRatingStore(RatingStore):
    def __init__(self) -> None:
        self._data: Dict[int, UserRatingStats] = {}
        self._global_lock = threading.Lock()

    def get(self, user_id: int) -> Optional[UserRatingStats]:
        # Copy-by-reference is fine since service holds per-user locks
        return self._data.get(user_id)

    def set(self, user_id: int, stats: UserRatingStats) -> None:
        with self._global_lock:
            self._data[user_id] = stats

    def iter_all(self) -> Iterator[Tuple[int, UserRatingStats]]:
        # Snapshot keys under lock to avoid runtime mutation issues
        with self._global_lock:
            items = list(self._data.items())
        return iter(items)


# ---------- Service Facade ----------

class CustomerRatingService:
    """Thread-safe service to record ratings and compute per-user averages."""

    def __init__(
        self,
        store: Optional[RatingStore] = None,
        bounds: Optional[RatingBounds] = None,
    ) -> None:
        self._store: RatingStore = store or InMemoryRatingStore()
        self._bounds = bounds
        self._locks: Dict[int, threading.Lock] = {}  # lazily created per user
        self._locks_guard = threading.Lock()
        # Optimized ranking support: max-heap with lazy invalidation
        # Heap element: (-avg, user_id, version)
        self._versions: Dict[int, int] = {}
        self._max_heap: List[Tuple[float, int, int]] = []
        self._heap_lock = threading.Lock()
        # Full-ranked optimized index using SortedList (optional dependency)
        self._index_lock = threading.Lock()
        self._sorted_index = SortedList() if SortedList is not None else None  # type: ignore
        # Map user -> current tuple stored in sorted index for O(log U) replacement
        self._current_index_key_by_user: Dict[int, Tuple[float, int]] = {}
        # Monthly aggregates: (year, month, user_id) -> stats
        self._monthly_stats: Dict[Tuple[int, int, int], UserRatingStats] = {}
        # Locks for monthly structures (reuse per-user locks for updates)
        self._monthly_lock = threading.Lock()
        # Optimized monthly full-rank: per-month SortedList and key maps
        self._monthly_index_lock = threading.Lock()
        self._monthly_sorted_index: Dict[YearMonth, SortedList] = {}
        self._monthly_current_key_by_user: Dict[YearMonth, Dict[int, Tuple[float, int]]] = {}

    def _lock_for(self, user_id: int) -> threading.Lock:
        # Lazily initialize a per-user lock under a small critical section
        if user_id in self._locks:
            return self._locks[user_id]
        with self._locks_guard:
            if user_id not in self._locks:
                self._locks[user_id] = threading.Lock()
            return self._locks[user_id]

    def record_rating(self, user_id: int, rating: float, at: Optional[datetime] = None) -> None:
        if self._bounds is not None:
            self._bounds.validate_or_raise(rating)

        # Determine timestamp and month bucket
        at_dt = at or datetime.now(timezone.utc)
        year = at_dt.year
        month = at_dt.month
        ym: YearMonth = (year, month)

        lock = self._lock_for(user_id)
        # Update aggregate under per-user lock
        with lock:
            stats = self._store.get(user_id)
            if stats is None:
                stats = UserRatingStats()
            stats.add(rating)
            self._store.set(user_id, stats)
            avg_after = stats.average()
            # Update version for this user to invalidate older heap/index entries
            if avg_after is not None:
                new_version = self._versions.get(user_id, 0) + 1
                self._versions[user_id] = new_version
            else:
                new_version = None  # should not happen after add

            # Update monthly aggregates under same user lock for consistency
            key = (year, month, user_id)
            mstats = self._monthly_stats.get(key)
            if mstats is None:
                mstats = UserRatingStats()
            mstats.add(rating)
            self._monthly_stats[key] = mstats
            monthly_avg_after = mstats.average()

        # Push to heap outside per-user lock to avoid lock ordering issues
        if avg_after is not None and new_version is not None:
            with self._heap_lock:
                heapq.heappush(self._max_heap, (-avg_after, user_id, new_version))
        # Update SortedList index (if available)
        if self._sorted_index is not None:
            with self._index_lock:
                # Use authoritative average at index update time to avoid stale writes
                current_stats = self._store.get(user_id)
                current_avg = current_stats.average() if current_stats is not None else None
                if current_avg is None:
                    # Remove any existing key if user has no ratings (unlikely right after add)
                    current_key = self._current_index_key_by_user.pop(user_id, None)
                    if current_key is not None:
                        try:
                            self._sorted_index.remove(current_key)  # type: ignore[attr-defined]
                        except ValueError:
                            pass
                else:
                    new_key = (-current_avg, user_id)
                    old_key = self._current_index_key_by_user.get(user_id)
                    if old_key is not None:
                        try:
                            self._sorted_index.remove(old_key)  # type: ignore[attr-defined]
                        except ValueError:
                            pass
                    self._sorted_index.add(new_key)  # type: ignore[attr-defined]
                    self._current_index_key_by_user[user_id] = new_key

        # Optimized monthly structures: SortedList update for month (if available)
        if monthly_avg_after is not None and SortedList is not None:
            with self._monthly_index_lock:
                sl = self._monthly_sorted_index.get(ym)
                if sl is None:
                    sl = SortedList()
                    self._monthly_sorted_index[ym] = sl
                    self._monthly_current_key_by_user[ym] = {}
                key_map = self._monthly_current_key_by_user[ym]
                new_key = (-monthly_avg_after, user_id)
                old_key = key_map.get(user_id)
                if old_key is not None:
                    try:
                        sl.remove(old_key)
                    except ValueError:
                        pass
                sl.add(new_key)
                key_map[user_id] = new_key

    def get_average(self, user_id: int) -> Optional[float]:
        stats = self._store.get(user_id)
        return stats.average() if stats is not None else None

    def get_ranked_users(self, descending: bool = True) -> List[Tuple[int, float]]:
        # Build a list of (user_id, avg) for users with at least one rating
        results: List[Tuple[int, float]] = []
        for user_id, stats in self._store.iter_all():
            avg = stats.average()
            if avg is not None:
                results.append((user_id, avg))

        # Primary sort: average; Secondary: user_id ascending for stability
        results.sort(key=lambda x: (x[1], -x[0]) if not descending else (-x[1], x[0]))
        return results

    def get_ranked_users_optimized(self, top_k: Optional[int] = None) -> List[Tuple[int, float]]:
        """Optimized retrieval using a max-heap with lazy invalidation.

        - If top_k is provided, returns the top K users by average in O(K log U)
          after cleanup of stale heap entries.
        - If top_k is None, falls back to full ranking via sorting (same as
          get_ranked_users) to avoid destroying the heap.
        """
        if top_k is None:
            return self.get_ranked_users(descending=True)

        result: List[Tuple[int, float]] = []
        with self._heap_lock:
            while len(result) < top_k and self._max_heap:
                neg_avg, user_id, version = heapq.heappop(self._max_heap)
                # Validate against current version
                current_version = self._versions.get(user_id)
                if current_version is None or current_version != version:
                    # Stale entry; skip
                    continue
                # Fetch current average from store (authoritative)
                stats = self._store.get(user_id)
                if stats is None:
                    continue
                avg = stats.average()
                if avg is None:
                    continue
                # Re-push authoritative snapshot for future calls
                heapq.heappush(self._max_heap, (-avg, user_id, version))
                result.append((user_id, avg))
        return result

    def get_ranked_users_optimized_v2(self) -> List[Tuple[int, float]]:
        """Full ranking via a maintained SortedList index.

        Complexity:
        - Update (record_rating): O(log U)
        - Full ranking: O(U) to iterate the index in order

        Requires the optional dependency `sortedcontainers`.
        """
        if self._sorted_index is None:
            raise RuntimeError(
                "sortedcontainers is not installed. Install with `pip install sortedcontainers` to use get_ranked_users_optimized_v2."
            )
        results: List[Tuple[int, float]] = []
        with self._index_lock:
            for neg_avg, user_id in self._sorted_index:  # type: ignore[attr-defined]
                results.append((user_id, -neg_avg))
        return results

    # ---------- Monthly Queries (baseline) ----------

    def get_monthly_stats(
        self,
        year: int,
        month: int,
        aggregate: str = "average",
        sorted: bool = True,
    ) -> List[Tuple[int, float]]:
        """Return per-user monthly aggregate for given year-month.

        - aggregate: "average" or "total"
        - sorted: if True, sort by value desc then user_id asc; else keep insertion order
        """
        results: List[Tuple[int, float]] = []
        prefix = (year, month)
        # Iterate snapshot of keys to avoid runtime mutation issues
        with self._monthly_lock:
            items = list(self._monthly_stats.items())
        for (y, m, user_id), stats in items:
            if (y, m) != prefix:
                continue
            if aggregate == "total":
                value = stats.total_score
            else:
                avg = stats.average()
                if avg is None:
                    continue
                value = avg
            results.append((user_id, value))

        if sorted:
            results.sort(key=lambda x: (-x[1], x[0]))
        return results

    def get_best_agents_for_month(
        self,
        year: int,
        month: int,
        top_k: Optional[int] = None,
    ) -> List[Tuple[int, float]]:
        """Baseline: build and sort monthly averages, optionally return top_k."""
        ranked = self.get_monthly_stats(year, month, aggregate="average", sorted=True)
        if top_k is not None:
            return ranked[:top_k]
        return ranked

    def get_best_agents_for_month_optimized(
        self,
        year: int,
        month: int,
        top_k: int,
    ) -> List[Tuple[int, float]]:
        """Optimized top-K monthly using per-month SortedList when available, otherwise fallback."""
        ym: YearMonth = (year, month)
        if SortedList is not None:
            with self._monthly_index_lock:
                sl = self._monthly_sorted_index.get(ym)
                if sl is None or not sl:
                    return []
                # slice first top_k entries
                sliced = sl[:top_k]
                return [(user_id, -neg_avg) for (neg_avg, user_id) in sliced]
        # Fallback to baseline sort and slice
        return self.get_best_agents_for_month(year, month, top_k=top_k)

    def get_monthly_stats_optimized_v2(self, year: int, month: int) -> List[Tuple[int, float]]:
        """Full-ranked monthly using per-month SortedList index.

        Requires `sortedcontainers`. Falls back to baseline if not available.
        """
        ym: YearMonth = (year, month)
        if SortedList is None:
            return self.get_monthly_stats(year, month, aggregate="average", sorted=True)
        with self._monthly_index_lock:
            sl = self._monthly_sorted_index.get(ym)
            if sl is None:
                return []
            return [(user_id, -neg_avg) for (neg_avg, user_id) in sl]

    # ---------- Export (monthly) ----------

    def _collect_monthly_rows(
        self,
        aggregate: str = "average",
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        with self._monthly_lock:
            items = list(self._monthly_stats.items())
        for (y, m, user_id), stats in items:
            if year is not None and y != year:
                continue
            if month is not None and m != month:
                continue
            if aggregate == "total":
                value = stats.total_score
            else:
                avg = stats.average()
                if avg is None:
                    continue
                value = avg
            rows.append({
                "user_id": user_id,
                "year": y,
                "month": m,
                "value": value,
            })
        # Deterministic order
        rows.sort(key=lambda r: (r["year"], r["month"], -r["value"], r["user_id"]))
        return rows

    def export_monthly_stats(
        self,
        path: str,
        file_type: str = "csv",
        aggregate: str = "average",
        year: Optional[int] = None,
        month: Optional[int] = None,
        **options: Any,
    ) -> None:
        """Generic export using a FileExporter implementation.

        Supported file_type: "csv", "json".
        Options:
          - csv: include_header: bool (default True)
          - json: pretty: bool (default True)
        """
        rows = self._collect_monthly_rows(aggregate=aggregate, year=year, month=month)
        if file_type.lower() == "csv":
            header_last = aggregate
            header = ["user_id", "year", "month", header_last]
            include_header = bool(options.get("include_header", True))
            exporter: FileExporter = CsvFileExporter(header=header, include_header=include_header)
        elif file_type.lower() == "json":
            pretty = bool(options.get("pretty", True))
            exporter = JsonFileExporter(pretty=pretty)
        else:
            raise ValueError(f"Unsupported file_type: {file_type}")
        exporter.write(path, rows)

    def export_monthly_stats_csv(
        self,
        path: str,
        aggregate: str = "average",
        year: Optional[int] = None,
        month: Optional[int] = None,
        include_header: bool = True,
    ) -> None:
        # Delegate to generic exporter to avoid duplicate logic
        self.export_monthly_stats(
            path=path,
            file_type="csv",
            aggregate=aggregate,
            year=year,
            month=month,
            include_header=include_header,
        )

    def export_monthly_stats_json(
        self,
        path: str,
        aggregate: str = "average",
        year: Optional[int] = None,
        month: Optional[int] = None,
        pretty: bool = True,
    ) -> None:
        # Delegate to generic exporter to avoid duplicate logic
        self.export_monthly_stats(
            path=path,
            file_type="json",
            aggregate=aggregate,
            year=year,
            month=month,
            pretty=pretty,
        )


# ---------- Convenience API ----------

_default_service: Optional[CustomerRatingService] = None


def _get_default_service() -> CustomerRatingService:
    global _default_service
    if _default_service is None:
        # Default to 1..5 bounds which is common for ratings
        _default_service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
    return _default_service


def record_user_rating(user_id: int, rating: float) -> None:
    _get_default_service().record_rating(user_id, rating)


def get_user_average(user_id: int) -> Optional[float]:
    return _get_default_service().get_average(user_id)


def get_ranking() -> List[Tuple[int, float]]:
    return _get_default_service().get_ranked_users(descending=True) 