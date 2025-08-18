from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


class EvictionPolicy(ABC):
    @abstractmethod
    def record_access(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_insertion(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_removal(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def evict_one(self) -> Optional[str]:
        """Return a key to evict, or None if nothing to evict."""
        raise NotImplementedError


@dataclass
class _Node:
    key: str
    prev: Optional["_Node"] = None
    next: Optional["_Node"] = None


class LRUEvictionPolicy(EvictionPolicy):
    """Least Recently Used eviction using a doubly-linked list + hashmap.

    Head = most recently used; Tail = least recently used.
    """

    def __init__(self) -> None:
        # Sentinel nodes to simplify insert/remove
        self._head = _Node(key="__HEAD__")
        self._tail = _Node(key="__TAIL__")
        self._head.next = self._tail
        self._tail.prev = self._head
        self._nodes_by_key: Dict[str, _Node] = {}

    def record_access(self, key: str) -> None:
        node = self._nodes_by_key.get(key)
        if node is None:
            return  # access to non-existing key (caller may check existence separately)
        self._move_to_front(node)

    def record_insertion(self, key: str) -> None:
        if key in self._nodes_by_key:
            node = self._nodes_by_key[key]
            self._move_to_front(node)
            return
        node = _Node(key=key)
        self._nodes_by_key[key] = node
        self._insert_after(self._head, node)

    def record_removal(self, key: str) -> None:
        node = self._nodes_by_key.pop(key, None)
        if node is not None:
            self._detach(node)

    def evict_one(self) -> Optional[str]:
        # Evict from tail (least recently used)
        lru = self._tail.prev
        if lru is None or lru is self._head:
            return None
        key = lru.key
        self.record_removal(key)
        return key

    # ----- internal helpers -----

    def _insert_after(self, at: _Node, node: _Node) -> None:
        node.prev = at
        node.next = at.next
        if at.next:
            at.next.prev = node
        at.next = node

    def _detach(self, node: _Node) -> None:
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        node.prev = None
        node.next = None

    def _move_to_front(self, node: _Node) -> None:
        self._detach(node)
        self._insert_after(self._head, node)


class KeyValueCache:
    def __init__(self, capacity: int, eviction_policy: Optional[EvictionPolicy] = None) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._policy = eviction_policy or LRUEvictionPolicy()
        self._store: Dict[str, Any] = {}

    @property
    def capacity(self) -> int:
        return self._capacity

    def size(self) -> int:
        return len(self._store)

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        self._policy.record_access(key)
        return self._store[key]

    def put(self, key: str, value: Any) -> None:
        if key in self._store:
            # Update and mark as recently used
            self._store[key] = value
            self._policy.record_access(key)
            return

        # Evict if needed
        if self.size() >= self._capacity:
            victim = self._policy.evict_one()
            if victim is not None and victim in self._store:
                del self._store[victim]
        # Insert
        self._store[key] = value
        self._policy.record_insertion(key)

    def remove(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            self._policy.record_removal(key)
            return True
        return False

    def contains(self, key: str) -> bool:
        return key in self._store 