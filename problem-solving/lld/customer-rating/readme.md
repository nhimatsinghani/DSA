## Problem

We need to maintain the average rating of each user in the system. The system receives many requests, each containing a `user_id` and a `rating`. Design and implement a solution that:

- Records ratings per user (with validation against allowed bounds)
- Computes the current average rating per user
- Produces the list of all users with their average ratings, sorted in descending order of rating (with a deterministic tie-break)

### Design Overview

- `RatingBounds`: immutable configuration for valid rating range (e.g., 1..5)
- `UserRatingStats`: per-user aggregate (sum and count) with an `average()` helper
- `RatingStore` abstraction with an in-memory implementation `InMemoryRatingStore`
- `CustomerRatingService`: thread-safe service exposing:
  - `record_rating(user_id, rating)`
  - `get_average(user_id)`
  - `get_ranked_users(descending=True)`
  - `get_ranked_users_optimized(top_k=None)` — heap-based top-K
  - `get_ranked_users_optimized_v2()` — SortedList-based full ranking (optional dependency)
- Convenience module-level API for simple use:
  - `record_user_rating(user_id, rating)`
  - `get_user_average(user_id)`
  - `get_ranking()`

Files:

- `customer_rating.py` (implementation)
- `test_customer_rating.py` (unit tests)
- `run_tests.py` (test runner)

## Clean Code and Design Principles Applied

- **Single Responsibility (SRP)**

  - `RatingBounds` only validates rating ranges.
  - `UserRatingStats` only aggregates and computes averages.
  - `InMemoryRatingStore` only stores aggregates.
  - `CustomerRatingService` orchestrates validation, aggregation, and queries.

- **Open/Closed Principle (OCP)**

  - Swap storage by implementing `RatingStore` (e.g., Redis-based store) without changing service logic.
  - Add or swap ranking strategies without impacting the core aggregation path.

- **Liskov Substitution Principle (LSP)**

  - Any `RatingStore` implementation is usable wherever a `RatingStore` is expected.

- **Interface Segregation Principle (ISP)**

  - `RatingStore` exposes a minimal surface: `get`, `set`, `iter_all`.

- **Dependency Inversion Principle (DIP)**

  - `CustomerRatingService` depends on the `RatingStore` abstraction via constructor injection, not a concrete data store.
  - Sorted index behind an optional dependency is accessed through the service, keeping call sites unchanged.

- **Encapsulation and Information Hiding**

  - Internal synchronization (per-user locks and guard), heap, and sorted index are hidden behind the service API.

- **Immutability Where Appropriate**

  - `RatingBounds` is `@dataclass(frozen=True)` to avoid accidental drift at runtime.

- **Input Validation and Fail-Fast**

  - `RatingBounds.validate_or_raise` ensures ratings fall within the acceptable range.

- **Thread-Safety Considerations**

  - Per-user locks protect per-user aggregates.
  - Separate locks protect heap (`_heap_lock`) and sorted index (`_index_lock`) to prevent contention and lock ordering issues.

- **DRY and Reuse**

  - Aggregation logic is centralized in `UserRatingStats`.

- **Deterministic Ranking**

  - Sorted by average rating desc, tie-break by `user_id` asc (`(-avg, user_id, version)` keys).

- **Testability by Design**

  - In-memory store and pure service methods enable fast unit tests.
  - Tests optionally skip SortedList-based checks if dependency is absent.

- **Future Extensibility**
  - Replace in-memory store with a persistent/distributed store implementing `RatingStore`.
  - Add percentile/median support with new stats structures.

## Optimized Ranking Approaches

- **Baseline**: `get_ranked_users()` — collects all averages and does an in-memory sort.

  - Complexity: `O(U log U)` per call, minimal write overhead.
  - Best when full-ranked output is rare or `U` is small.

- **Top-K optimization**: `get_ranked_users_optimized(top_k)` using a max-heap with lazy invalidation.

  - Update: `O(log U)` push per rating.
  - Query (top-K): `O(K log U)` after skipping stale entries.
  - Best when clients frequently ask for only the top N users.

- **Full-ranked optimization (v2)**: `get_ranked_users_optimized_v2()` using `sortedcontainers.SortedList`.
  - Update: Remove old key (if present) and insert new key ⇒ `O(log U)`.
  - Query: Iterate sorted index ⇒ `O(U)`; no re-sorting.
  - Requires `sortedcontainers` (install via `pip install sortedcontainers`).
  - Best when full-ranked output is frequent and you want predictable `O(log U)` update cost.

## Usage

- Using the service directly:

```python
from customer_rating import CustomerRatingService, RatingBounds

service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
service.record_rating(1, 5)
service.record_rating(1, 3)
service.record_rating(2, 4)

print(service.get_average(1))           # 4.0
print(service.get_ranked_users())       # [(1, 4.0), (2, 4.0)] — tie broken by user_id
print(service.get_ranked_users_optimized(top_k=1))  # [(1, 4.0)]
```

- Using the SortedList full ranking (if dependency installed):

```python
from customer_rating import CustomerRatingService, RatingBounds

service = CustomerRatingService(bounds=RatingBounds(1.0, 5.0))
service.record_rating(10, 5)
service.record_rating(20, 3)
service.record_rating(30, 4)

print(service.get_ranked_users_optimized_v2())  # [(10, 5.0), (30, 4.0), (20, 3.0)]
```

## Testing

Run tests:

```bash
/usr/bin/python3 /Users/nishanthimath/PycharmProjects/DSA/problem-solving/lld/customer-rating/run_tests.py
```

If `sortedcontainers` is not installed, the SortedList-specific test will be skipped. Install via:

```bash
pip install sortedcontainers
```

## New requirements and plan

- c) See who the best agents are each month
- d) Export each agent’s average ratings per month (CSV/JSON/XML)
- e) Support returning unsorted averages and totals (sum) instead of averages

### High-level approach

Add a time dimension (month buckets) alongside existing overall aggregates. Keep the API backward compatible while adding new methods. Maintain efficient read paths with optional sorted indexes per month when needed.

### API additions (proposed)

- Recording with timestamp (defaults to now):
  - `record_rating(user_id: int, rating: float, at: Optional[datetime] = None) -> None`
- Monthly queries:
  - `get_best_agents_for_month(year: int, month: int, top_k: Optional[int] = None) -> List[Tuple[int, float]]`
    - If `top_k` is provided, return top-K by monthly average; else full ranked list.
  - `get_monthly_stats(year: int, month: int, aggregate: Literal["average", "total"] = "average", sorted: bool = True) -> List[Tuple[int, float]]`
    - Supports requirement (e): unsorted averages or totals by setting `sorted=False` or `aggregate="total"`.
- Export:
  - `export_monthly_averages_csv(path: str) -> None`
  - `export_monthly_averages_json(path: str) -> None`
  - (Optional) `export_monthly_averages_xml(path: str) -> None`

### Data model changes

- Keep existing per-user aggregate: `user_id -> UserRatingStats`.
- Add monthly aggregates: `(year, month, user_id) -> UserRatingStats`.
  - Represent month as `year * 100 + month` or a small `YearMonth` dataclass for clarity.
- Extend `RatingStore` or add a parallel `MonthlyRatingStore` interface. To minimize churn, we can keep the current `RatingStore` for overall stats and manage monthly maps within the service (still testable and encapsulated). If we anticipate distributed storage, define a `MonthlyRatingStore` abstraction early.

### Time source

- Accept an optional `at: datetime` in `record_rating`. If `None`, use a `Clock`-like abstraction (`SystemClock` returning `datetime.now(tz=UTC)`), mirroring the rate limiter’s approach for testability.
- Compute the bucket `(year, month)` from `at`.

### Indexing for monthly “best agents”

Two optimized paths (pick based on usage):

- Top-K per month (frequent top-K queries):

  - Maintain a per-month max-heap with lazy invalidation similar to `get_ranked_users_optimized(top_k)`.
  - Map: `month -> heap[(-avg, user_id, version)]` and `month -> versions[user_id]`.
  - Update: O(log U_month); Query top-K: O(K log U_month).

- Full ranked per month (frequent full-ranked output):
  - Maintain a per-month `SortedList` index keyed by `(-avg, user_id)`.
  - Maps: `month -> SortedList`, and `month -> {user_id -> (-avg, user_id)}` to support O(log U_month) replacement.
  - Update: O(log U_month); Query: O(U_month).

We can support both; the per-month index maintenance happens during `record_rating` after computing the new monthly average.

### Implementation outline (incremental edits to `customer_rating.py`)

1. Types and imports

- Add `from datetime import datetime, timezone` and a small helper to compute `(year, month)`.
- Introduce `YearMonth = Tuple[int, int]` or a small dataclass.

2. Service state

- Add `_monthly_stats: Dict[Tuple[int, int, int], UserRatingStats]` keyed by `(year, month, user_id)`.
- Add locks reuse: same per-user locks; monthly structures updated under the same per-user lock to keep aggregates consistent.
- If optimizing:
  - Heaps: `_monthly_heap: Dict[YearMonth, List[Tuple[float,int,int]]]` and `_monthly_versions: Dict[YearMonth, Dict[int,int]]` + a `_monthly_heap_lock`.
  - SortedList: `_monthly_sorted_index: Dict[YearMonth, SortedList]` and `_monthly_current_key: Dict[YearMonth, Dict[int, Tuple[float,int]]]` + `_monthly_index_lock`.

3. record_rating changes

- Signature: `record_rating(user_id, rating, at=None)`.
- Determine `at_dt = at or datetime.now(timezone.utc)`; derive `(year, month)`.
- Under the user lock: update overall stats and the monthly stats entry.
- After releasing the user lock: update the monthly heap and/or monthly sorted index as configured.

4. Query methods

- `get_best_agents_for_month(year, month, top_k=None)`:
  - If `top_k` provided, pop/validate from monthly heap; else iterate monthly SortedList or build/sort from `_monthly_stats` fallback.
- `get_monthly_stats(year, month, aggregate="average", sorted=True)`:
  - Build list using `_monthly_stats` for that month and compute either `average()` or `total_score`.
  - If `sorted`, sort by value desc then `user_id` asc; else return insertion order list.

5. Export methods

- CSV: columns `user_id,year,month,average` (or `total` variant).
- JSON: array of objects `{ "user_id": 123, "year": 2025, "month": 8, "average": 4.25 }`.
- Implement with a single internal iterator over all `(year, month, user_id)` stats to generate rows/objects.
- Optionally accept a filter `year=None, month=None` to export a subset.

### Complexity considerations

- Writes: O(1) for aggregate updates; plus O(log U_month) if using per-month indexes.
- Reads:
  - Best agents per month (top-K): O(K log U_month) using heap.
  - Full-ranked per month: O(U_month) using SortedList iteration.
  - Fallback (no indexes): O(U_month log U_month) to sort on demand.

### Backward compatibility

- Existing methods (`record_rating(user_id, rating)`, `get_average`, overall ranking) keep working.
- Timestamp is optional; existing callers need no change.

### Testing plan

- Unit tests for monthly aggregates: single user, multiple users, cross-month isolation.
- Best-agents per month: top-1/top-K, ties, after updates.
- Export: validate CSV/JSON shape and values; round average to a stable precision.
- Concurrency: simulate concurrent updates to different users in the same month and across months.

### Optional configuration

- Flags to enable/disable per-month heap or SortedList indexes based on workload; fall back to on-demand sorting if disabled.
