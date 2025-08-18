from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Pattern, Tuple, Dict


class RouteMatcher(ABC):
    @abstractmethod
    def matches(self, path: str) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class ExactRouteMatcher(RouteMatcher):
    path: str

    def matches(self, path: str) -> bool:
        return path == self.path


@dataclass(frozen=True)
class RegexRouteMatcher(RouteMatcher):
    pattern: Pattern[str]

    def matches(self, path: str) -> bool:
        return self.pattern.fullmatch(path) is not None


@dataclass(frozen=True)
class WildcardRouteMatcher(RegexRouteMatcher):
    """Simple wildcard matcher: '*' -> '.*', '?' -> '.' (regex anchored).

    Use from_pattern() for regex-based,
    from_pattern_v2() for char-level glob (no regex), and
    from_pattern_v3() for segment-level wildcards (no regex).
    """

    @staticmethod
    def from_pattern(pattern: str) -> "WildcardRouteMatcher":
        # Escape regex chars then replace wildcard tokens
        # We replace escaped \* and \? with regex equivalents
        escaped = re.escape(pattern)
        regex_str = "^" + escaped.replace(r"\*", ".*").replace(r"\?", ".") + "$"
        compiled = re.compile(regex_str)
        return WildcardRouteMatcher(pattern=compiled)

    @staticmethod
    def from_pattern_v2(pattern: str) -> "GlobRouteMatcher":
        # Non-regex alternative using two-pointer/backtracking char-level glob matcher
        return GlobRouteMatcher(pattern)

    @staticmethod
    def from_pattern_v3(pattern: str) -> "SegmentWildcardRouteMatcher":
        # Non-regex alternative using segment-level wildcards ('*' or '?' as a whole segment)
        return SegmentWildcardRouteMatcher(pattern)


@dataclass(frozen=True)
class PathParamRouteMatcher(RegexRouteMatcher):
    """Path params matcher (regex-based): '/users/:id/books/:bookId'.

    Use from_pattern() for regex-based and from_pattern_v2() for segment-based (no regex).
    """

    @staticmethod
    def from_pattern(pattern: str) -> "PathParamRouteMatcher":
        # Convert :param to ([^/]+)
        segments = pattern.split("/")
        regex_parts: List[str] = []
        for seg in segments:
            if not seg:
                continue
            if seg.startswith(":"):
                regex_parts.append(r"([^/]+)")
            else:
                regex_parts.append(re.escape(seg))
        regex_str = "^/" + "/".join(regex_parts) + "$" if pattern.startswith("/") else "^" + "/".join(regex_parts) + "$"
        compiled = re.compile(regex_str)
        return PathParamRouteMatcher(pattern=compiled)

    @staticmethod
    def from_pattern_v2(pattern: str) -> "SegmentParamRouteMatcher":
        # Non-regex alternative using segment-wise comparison
        return SegmentParamRouteMatcher(pattern)


# ---------- Non-regex alternative matchers ----------

@dataclass(frozen=True)
class GlobRouteMatcher(RouteMatcher):
    pattern: str

    def matches(self, path: str) -> bool:
        return glob_match(path, self.pattern)


@dataclass(frozen=True)
class SegmentWildcardRouteMatcher(RouteMatcher):
    pattern: str

    def matches(self, path: str) -> bool:
        return segment_glob_match(path, self.pattern)


@dataclass(frozen=True)
class SegmentParamRouteMatcher(RouteMatcher):
    pattern: str

    def matches(self, path: str) -> bool:
        return path_params_match(path, self.pattern)


def glob_match(path: str, pattern: str) -> bool:
    """Match path against glob pattern with '*' and '?' (no regex), character-level.

    Algorithm: two-pointer scan with backtracking to the last '*'.
    - '?' matches exactly one character
    - '*' matches zero or more characters
    """
    i = 0  # index in path
    j = 0  # index in pattern
    star = -1  # last position of '*' in pattern
    backtrack = -1  # position in path to backtrack to after a '*'

    while i < len(path):
        if j < len(pattern) and (pattern[j] == '?' or pattern[j] == path[i]):
            i += 1
            j += 1
        elif j < len(pattern) and pattern[j] == '*':
            star = j
            backtrack = i
            j += 1
        elif star != -1:
            # backtrack: let '*' consume one more character in path
            j = star + 1
            backtrack += 1
            i = backtrack
        else:
            return False

    # Consume trailing '*' in pattern
    while j < len(pattern) and pattern[j] == '*':
        j += 1

    return j == len(pattern)


def segment_glob_match(path: str, pattern: str) -> bool:
    """Segment-level wildcard matching without regex.

    Semantics:
    - Split path and pattern by '/'.
    - A pattern segment of '*' matches exactly one path segment (any value).
    - A pattern segment of '?' matches exactly one path segment (any value).
    - A pattern segment of '**' matches zero or more path segments.
    - Any other segment must match exactly.
    """
    pseg = [s for s in pattern.split('/') if s != '']
    sseg = [s for s in path.split('/') if s != '']
    i = 0  # index in sseg
    j = 0  # index in pseg
    star = -1  # index of '**' in pseg
    backtrack = -1  # index in sseg to backtrack to for '**'

    while i < len(sseg):
        if j < len(pseg) and (pseg[j] == '*' or pseg[j] == '?'):
            i += 1
            j += 1
        elif j < len(pseg) and pseg[j] == '**':
            star = j
            backtrack = i
            j += 1
        elif j < len(pseg) and pseg[j] == sseg[i]:
            i += 1
            j += 1
        elif star != -1:
            j = star + 1
            backtrack += 1
            i = backtrack
        else:
            return False

    # Consume trailing '**'
    while j < len(pseg) and pseg[j] == '**':
        j += 1

    return j == len(pseg)


def path_params_match(path: str, pattern: str) -> bool:
    """Match '/users/:id/books/:bookId' against '/users/123/books/abc' without regex.

    - Split by '/' and compare segment by segment
    - A segment starting with ':' matches any non-empty segment
    """
    pseg = [s for s in pattern.split('/') if s != '']
    sseg = [s for s in path.split('/') if s != '']
    if len(pseg) != len(sseg):
        return False
    for pp, sp in zip(pseg, sseg):
        if pp.startswith(':'):
            if not sp:
                return False
        elif pp != sp:
            return False
    return True


@dataclass
class RouteEntry:
    matcher: RouteMatcher
    result: str
    is_exact: bool


class Router:
    def __init__(self) -> None:
        self._exact_map: Dict[str, str] = {}
        self._ordered_routes: List[RouteEntry] = []  # for wildcard and params (ordered checking)

    def add_route(self, path_pattern: str, result: str) -> None:
        matcher, is_exact = self._build_matcher(path_pattern)
        if is_exact:
            self._exact_map[path_pattern] = result
        else:
            self._ordered_routes.append(RouteEntry(matcher=matcher, result=result, is_exact=False))

    def call_route(self, path: str) -> Optional[str]:
        # 1) Exact match fast path
        if path in self._exact_map:
            return self._exact_map[path]
        # 2) Ordered checking for wildcard and param routes
        for entry in self._ordered_routes:
            if entry.matcher.matches(path):
                return entry.result
        return None

    @staticmethod
    def _build_matcher(path_pattern: str) -> Tuple[RouteMatcher, bool]:
        if ":" in path_pattern:
            return PathParamRouteMatcher.from_pattern(path_pattern), False
        if "*" in path_pattern or "?" in path_pattern:
            return WildcardRouteMatcher.from_pattern(path_pattern), False
        return ExactRouteMatcher(path_pattern), True 