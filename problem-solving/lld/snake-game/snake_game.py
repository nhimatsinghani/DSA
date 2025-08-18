from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Deque, Dict, Iterable, List, Optional, Set, Tuple
from abc import ABC, abstractmethod
from collections import deque
import random


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]


@dataclass(frozen=True)
class Position:
    x: int
    y: int


class GrowthPolicy(ABC):
    @abstractmethod
    def should_grow(self, move_count: int, ate_food: bool) -> bool:
        raise NotImplementedError


class FixedIntervalGrowthPolicy(GrowthPolicy):
    def __init__(self, interval_moves: int = 5) -> None:
        if interval_moves <= 0:
            raise ValueError("interval_moves must be positive")
        self._interval = interval_moves

    def should_grow(self, move_count: int, ate_food: bool) -> bool:
        return move_count > 0 and (move_count % self._interval == 0)


class NoGrowthPolicy(GrowthPolicy):
    def should_grow(self, move_count: int, ate_food: bool) -> bool:
        return False


class FoodGrowthPolicy(GrowthPolicy):
    def should_grow(self, move_count: int, ate_food: bool) -> bool:
        return ate_food


class FoodSpawner(ABC):
    @abstractmethod
    def spawn(self, width: int, height: int, occupied: Set[Position]) -> Optional[Position]:
        raise NotImplementedError


class RandomFoodSpawner(FoodSpawner):
    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def spawn(self, width: int, height: int, occupied: Set[Position]) -> Optional[Position]:
        free_cells: List[Position] = []
        for y in range(height):
            for x in range(width):
                p = Position(x, y)
                if p not in occupied:
                    free_cells.append(p)
        if not free_cells:
            return None
        return self._rng.choice(free_cells)


class DeterministicFoodSpawner(FoodSpawner):
    """Test helper: returns the next provided position that is free."""

    def __init__(self, queue: Optional[Deque[Position]] = None) -> None:
        self._queue: Deque[Position] = queue or deque()

    def enqueue(self, pos: Position) -> None:
        self._queue.append(pos)

    def spawn(self, width: int, height: int, occupied: Set[Position]) -> Optional[Position]:
        while self._queue:
            p = self._queue.popleft()
            if 0 <= p.x < width and 0 <= p.y < height and p not in occupied:
                return p
        return None


class SnakeGame:
    def __init__(
        self,
        width: int,
        height: int,
        *,
        growth_policy: Optional[GrowthPolicy] = None,
        food_spawner: Optional[FoodSpawner] = None,
        enable_food: bool = False,
        end_on_wall_collision: bool = True,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        self._width = width
        self._height = height
        self._growth_policy = growth_policy or FixedIntervalGrowthPolicy(5)
        self._food_spawner = food_spawner or RandomFoodSpawner()
        self._enable_food = enable_food
        self._end_on_wall_collision = end_on_wall_collision

        # Initialize snake of length 3 centered horizontally, heading RIGHT
        cx = width // 2
        cy = height // 2
        self._snake: Deque[Position] = deque([
            Position(cx, cy),
            Position(cx - 1, cy),
            Position(cx - 2, cy),
        ])
        self._occupied: Set[Position] = set(self._snake)
        self._head_dir: Direction = Direction.RIGHT
        self._moves: int = 0
        self._game_over: bool = False
        self._food: Optional[Position] = None

        if self._enable_food:
            self._maybe_spawn_food()

    # ---------- Public API ----------

    def move_snake(self, direction: Direction) -> None:
        if self._game_over:
            return
        # Disallow immediate opposite direction to avoid instant self-collision flip
        if not self._is_opposite(direction, self._head_dir):
            self._head_dir = direction
        self._step()

    def is_game_over(self) -> bool:
        return self._game_over

    def get_snake_positions(self) -> List[Position]:
        return list(self._snake)

    def get_food_position(self) -> Optional[Position]:
        return self._food

    def get_move_count(self) -> int:
        return self._moves

    # ---------- Internal mechanics ----------

    def _step(self) -> None:
        head = self._snake[0]
        new_head = Position(head.x + self._head_dir.dx, head.y + self._head_dir.dy)
        # Bounds handling
        if not (0 <= new_head.x < self._width and 0 <= new_head.y < self._height):
            if self._end_on_wall_collision:
                self._game_over = True
                return
            # Wrap-around
            # This logic implements "wrap-around" behavior for the snake when it moves off the board edges.
            # If the snake's new head position goes beyond the board's width or height, it wraps around to the opposite side.
            # For example, if the board is 10x10 and the snake moves right from (9, 5), new_head.x becomes 10.
            # Applying new_head.x % self._width gives 0, so the new head appears at (0, 5).
            # Similarly, moving up from (3, 0) would result in new_head.y = -1, and -1 % 10 = 9, so the new head appears at (3, 9).
            new_head = Position(new_head.x % self._width, new_head.y % self._height)

        # Check self collision (note: moving into current tail is allowed if tail moves)
        tail = self._snake[-1]
        will_hit_self = new_head in self._occupied and new_head != tail
        if will_hit_self:
            self._game_over = True
            return

        self._moves += 1
        ate_food = self._enable_food and self._food is not None and new_head == self._food

        # Add new head
        self._snake.appendleft(new_head)
        self._occupied.add(new_head)

        # Determine growth
        should_grow = self._growth_policy.should_grow(self._moves, ate_food)
        if ate_food:
            # Clear food first; respawn after move
            self._food = None
        if not should_grow and not ate_food:
            # Normal move: remove tail
            removed = self._snake.pop()
            self._occupied.remove(removed)
        else:
            # Grew: keep tail, no removal
            pass

        if self._enable_food and self._food is None:
            self._maybe_spawn_food()

        # After movement, if head equals any body segment (excluding the new tail when removed), already handled

    def _maybe_spawn_food(self) -> None:
        if not self._enable_food:
            return
        pos = self._food_spawner.spawn(self._width, self._height, self._occupied)
        self._food = pos

    @staticmethod
    def _is_opposite(a: Direction, b: Direction) -> bool:
        return (a.dx + b.dx == 0) and (a.dy + b.dy == 0) 