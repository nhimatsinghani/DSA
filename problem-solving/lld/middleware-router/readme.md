## Middleware Router

We want to implement a middleware router for a web service that returns different strings based on the request path.

Interface (conceptual):

```
Interface Router {
  addRoute(path: String, result: String): Unit;
  callRoute(path: String): String;
}
```

Usage:

- `addRoute("/bar", "result")`
- `callRoute("/bar") -> "result"`

Scale-ups:

- Wildcards using ordered checking (e.g., `/static/*`)
- Path params (e.g., `/users/:id/books/:bookId`)

## Design Overview

Files:

- `router.py` (implementation)
- `test_router.py` (unit tests)

Abstractions:

- `RouteMatcher` (interface)
  - `ExactRouteMatcher` — O(1) lookup via exact map
  - `WildcardRouteMatcher` — converts `*` to `.*`, `?` to `.` (anchored regex)
  - `PathParamRouteMatcher` — converts `:param` to `([^/]+)` (anchored regex)
- `Router`
  - Keeps an exact map for exact routes
  - Keeps an ordered list for wildcards and path-params (ordered checking)
  - `add_route(pattern, result)` builds the appropriate matcher and stores it
  - `call_route(path)` returns the first matching result

## Clean Code and Design Principles

- Single Responsibility (SRP)
  - Matchers focus on pattern-matching only; `Router` coordinates storage and resolution
- Open/Closed Principle (OCP)
  - New matching modes can be added by implementing `RouteMatcher` without changing `Router`
- Liskov Substitution Principle (LSP)
  - Any `RouteMatcher` can be used interchangeably in the router
- Interface Segregation (ISP)
  - Small `matches(path)` interface for matchers
- Dependency Inversion (DIP)
  - `Router` depends on the abstract `RouteMatcher`, not regex specifics
- Efficiency and Clarity
  - Exact matches use a dict for O(1) resolution
  - Wildcards and path-params use ordered checking to preserve deterministic behavior
- Deterministic Behavior
  - Ordered list ensures that earlier routes have priority when patterns overlap

## Usage

```python
from router import Router

r = Router()
r.add_route("/bar", "result")
print(r.call_route("/bar"))  # "result"

# Wildcard
r.add_route("/static/*", "static")
print(r.call_route("/static/css/app.css"))  # "static"

# Path params
r.add_route("/users/:id/books/:bookId", "user-book")
print(r.call_route("/users/42/books/abc"))  # "user-book"
```

## Notes on Scale-ups

- Wildcards using ordered checking:
  - The router checks wildcard routes in the order they were added; earlier routes take precedence
- Path params:
  - `:param` segments match any non-empty, non-`/` substring
  - For simplicity here we return the configured result; extracting param values would be a small extension (capture groups)

## Testing

Run tests:

```bash
/usr/bin/python3 /Users/nishanthimath/PycharmProjects/DSA/problem-solving/lld/middleware-router/test_router.py
```
