import sys
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict


def parse_timestamp(value: str) -> datetime:
    """Parse a wide range of common timestamp formats into a timezone-aware UTC datetime.

    Falls back to treating the value as a UNIX epoch (seconds) if numeric.
    """
    value = value.strip()
    formats: List[str] = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y",
        "%d-%m-%Y %H:%M:%S",
        "%m/%d/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%d-%b-%Y",
        "%d-%b-%Y %H:%M:%S",
        "%Y/%m/%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            # Make timezone-aware (UTC) if naive
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue

    # Try UNIX epoch seconds
    try:
        seconds = float(value)
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except ValueError:
        pass

    # As a last resort, try to parse ISO with fractional seconds and/or Z
    try:
        # Handle trailing Z
        cleaned = value.replace("Z", "+0000").replace(".000", "")
        dt = datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(timezone.utc)
    except Exception as exc:
        raise ValueError(f"Unrecognized timestamp format: '{value}'") from exc


def days_between(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 86400.0


def calcMissing() -> None:
    """Read input from stdin and print the 20 missing mercury max values as floats.

    Input: each line contains two tab-separated columns: timestamp, value (float or 'Missing_i').
    Strategy: sort by timestamp, then perform linear interpolation across missing blocks using
    the nearest known neighbors in time. For leading/trailing missing blocks, use the closest
    known neighbor's value. Finally, print Missing_1..Missing_20 in numeric order.
    """
    lines: List[str] = [line.rstrip("\n") for line in sys.stdin if line.strip()]
    if not lines:
        return

    records: List[Tuple[datetime, Optional[float], Optional[str]]] = []
    missing_labels_in_input: List[str] = []

    for raw in lines:
        # Prefer tab, but be resilient to multiple spaces if needed
        if "\t" in raw:
            ts_part, val_part = raw.split("\t", 1)
        else:
            parts = raw.split()
            if len(parts) < 2:
                # Skip malformed lines silently
                continue
            ts_part, val_part = parts[0], parts[1]

        timestamp = parse_timestamp(ts_part)
        val_str = val_part.strip()

        if val_str.startswith("Missing_"):
            records.append((timestamp, None, val_str))
            missing_labels_in_input.append(val_str)
        else:
            try:
                value = float(val_str)
            except ValueError:
                # Skip malformed numeric values
                continue
            records.append((timestamp, value, None))

    # Sort by timestamp to ensure proper temporal interpolation
    records.sort(key=lambda r: r[0])

    n = len(records)
    values: List[Optional[float]] = [val for (_, val, _) in records]
    labels: List[Optional[str]] = [lbl for (_, _, lbl) in records]
    times: List[datetime] = [ts for (ts, _, _) in records]

    # Identify contiguous missing runs and interpolate
    i = 0
    while i < n:
        if values[i] is not None:
            i += 1
            continue
        # Start of a missing block
        start = i
        while i < n and values[i] is None:
            i += 1
        end = i - 1

        prev_idx = start - 1
        next_idx = end + 1 if end + 1 < n else None

        prev_time = times[prev_idx] if prev_idx >= 0 else None
        prev_val = values[prev_idx] if prev_idx >= 0 else None
        next_time = times[next_idx] if next_idx is not None else None
        next_val = values[next_idx] if next_idx is not None else None

        if prev_val is not None and next_val is not None:
            total_days = days_between(prev_time, next_time)
            if total_days <= 0:
                # Fallback to equal split if timestamps are identical or inverted
                for j in range(start, end + 1):
                    frac = (j - start + 1) / (end - start + 2)
                    values[j] = prev_val + frac * (next_val - prev_val)
            else:
                for j in range(start, end + 1):
                    frac = days_between(prev_time, times[j]) / total_days
                    values[j] = prev_val + frac * (next_val - prev_val)
        elif prev_val is not None:
            # Trailing block: carry forward previous known value
            for j in range(start, end + 1):
                values[j] = prev_val
        elif next_val is not None:
            # Leading block: carry backward next known value
            for j in range(start, end + 1):
                values[j] = next_val
        else:
            # Entire sequence missing (should not happen per problem constraints)
            for j in range(start, end + 1):
                values[j] = 0.0

    # Prepare output for Missing_1..Missing_20
    label_to_value: Dict[str, float] = {}
    for idx, lbl in enumerate(labels):
        if lbl:
            # Enforce constraint < 400 just in case of pathological input
            val = float(values[idx]) if values[idx] is not None else 0.0
            if val >= 400.0:
                val = 399.0
            label_to_value[lbl] = val

    # Print Missing_1..Missing_20 in order, each on new line
    for k in range(1, 21):
        key = f"Missing_{k}"
        if key in label_to_value:
            print(f"{label_to_value[key]:.2f}")
        else:
            # Default to 0.00 if label not present (robustness)
            print("0.00")


if __name__ == "__main__":
    calcMissing()
