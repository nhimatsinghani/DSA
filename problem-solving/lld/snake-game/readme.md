## Game of Snakes

Remember the old phone game of snake? The snake can move up, down, left or right in a 2D board of arbitrary size.

Rules (baseline):

- Every time `moveSnake()` is called, the snake moves up, down, left or right
- The snake’s initial size is 3 and grows by 1 every 5 moves
- The game ends when the snake hits itself

Proposed changes:

- Change#1: Make scale-up optional (configurable policy)
- Change#2: Growth when the snake eats food rather than every 5 moves (optional). Food is dropped at a random position on the board.

## Design Overview

Files:

- `snake_game.py` (implementation)
- `test_snake_game.py` (unit tests)

Entities and abstractions:

- `Direction` (enum): `UP`, `DOWN`, `LEFT`, `RIGHT`
- `Position` (value object): `(x, y)`
- `GrowthPolicy` (strategy interface): `should_grow(move_count: int, ate_food: bool) -> bool`
  - `FixedIntervalGrowthPolicy(interval_moves=5)`
  - `NoGrowthPolicy()`
  - `FoodGrowthPolicy()`
- `FoodSpawner` (strategy interface): `spawn(width, height, occupied) -> Optional[Position]`
  - `RandomFoodSpawner(seed=None)`
  - `DeterministicFoodSpawner` for tests
- `SnakeGame(width, height, *, growth_policy, food_spawner, enable_food, end_on_wall_collision)`
  - Public API: `move_snake(direction)`, `is_game_over()`, `get_snake_positions()`, `get_food_position()`, `get_move_count()`

Behavioral notes:

- Initial snake length is 3, centered horizontally, heading right
- Moves disallow instant reversal (opposite direction) to avoid degenerate self-hit flips
- Boundary: either end game on wall hit or wrap around (configurable)
- Self-collision ends game; moving into current tail is allowed when tail moves away on the same step
- Food is optional; when enabled it spawns in a random free cell via `FoodSpawner`

## Clean Code and Design Principles

- Single Responsibility (SRP)
  - `SnakeGame` orchestrates game state and step logic only
  - `GrowthPolicy` handles when growth happens
  - `FoodSpawner` handles where food appears
- Open/Closed Principle (OCP)
  - Add growth behaviors by implementing `GrowthPolicy` without changing `SnakeGame`
  - Add spawning behaviors by implementing `FoodSpawner`
- Liskov Substitution Principle (LSP)
  - Any `GrowthPolicy`/`FoodSpawner` can be injected and used interchangeably
- Interface Segregation (ISP)
  - Small, focused interfaces: `should_grow(...)`, `spawn(...)`
- Dependency Inversion (DIP)
  - `SnakeGame` depends on abstractions (`GrowthPolicy`, `FoodSpawner`) injected at construction
- Encapsulation
  - Internal state (deque body, occupied set, direction, move count) hidden behind methods
- Testability
  - Deterministic `FoodSpawner` and injected policies enable precise, reliable tests
- Deterministic behavior
  - Optional seed on `RandomFoodSpawner`; tests use deterministic spawner
- Naming and clarity
  - Intention-revealing names (`FoodGrowthPolicy`, `DeterministicFoodSpawner`)

## Usage

- Baseline (grow every 5 moves, wall collision ends game):

```python
from snake_game import SnakeGame, Direction

game = SnakeGame(10, 10)
while not game.is_game_over():
    game.move_snake(Direction.RIGHT)
```

- Food-based growth and wrap-around:

```python
from snake_game import SnakeGame, Direction, FoodGrowthPolicy

game = SnakeGame(
    10, 10,
    growth_policy=FoodGrowthPolicy(),
    enable_food=True,
    end_on_wall_collision=False,
)
```

- Deterministic food for testing/demo:

```python
from snake_game import SnakeGame, Direction, FoodGrowthPolicy, DeterministicFoodSpawner, Position

spawner = DeterministicFoodSpawner()
spawner.enqueue(Position(6, 5))

game = SnakeGame(10, 10, growth_policy=FoodGrowthPolicy(), food_spawner=spawner, enable_food=True)
```

## Testing

Run tests:

```bash
/usr/bin/python3 /Users/nishanthimath/PycharmProjects/DSA/problem-solving/lld/snake-game/test_snake_game.py
```

The suite covers initialization, wall vs wrap-around, fixed/no/food growth policies, deterministic food spawn, and self-collision.
