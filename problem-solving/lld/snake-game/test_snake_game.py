import unittest
from collections import deque

from snake_game import SnakeGame, Direction, FixedIntervalGrowthPolicy, NoGrowthPolicy, FoodGrowthPolicy, DeterministicFoodSpawner, Position


class TestSnakeGame(unittest.TestCase):
    def test_initial_state(self):
        game = SnakeGame(10, 10)
        self.assertFalse(game.is_game_over())
        self.assertEqual(len(game.get_snake_positions()), 3)
        self.assertIsNone(game.get_food_position())

    def test_move_and_wall_collision(self):
        game = SnakeGame(3, 3, end_on_wall_collision=True)
        # Snake starts heading RIGHT from center (1,1)->(0-based)
        game.move_snake(Direction.RIGHT)  # to (2,1)
        self.assertFalse(game.is_game_over())
        game.move_snake(Direction.RIGHT)  # hits wall
        self.assertTrue(game.is_game_over())

    def test_wrap_around(self):
        game = SnakeGame(3, 3, end_on_wall_collision=False)
        game.move_snake(Direction.RIGHT)  # to (2,1)
        game.move_snake(Direction.RIGHT)  # wraps to (0,1)
        self.assertFalse(game.is_game_over())

    def test_fixed_interval_growth(self):
        game = SnakeGame(10, 10, growth_policy=FixedIntervalGrowthPolicy(2))
        base_len = len(game.get_snake_positions())
        game.move_snake(Direction.RIGHT)  # 1
        game.move_snake(Direction.RIGHT)  # 2 -> grow
        self.assertEqual(len(game.get_snake_positions()), base_len + 1)

    def test_no_growth(self):
        game = SnakeGame(10, 10, growth_policy=NoGrowthPolicy())
        base_len = len(game.get_snake_positions())
        for _ in range(5):
            game.move_snake(Direction.RIGHT)
        self.assertEqual(len(game.get_snake_positions()), base_len)

    def test_food_growth_policy(self):
        spawner = DeterministicFoodSpawner(deque([Position(6, 5)]))
        game = SnakeGame(10, 10, growth_policy=FoodGrowthPolicy(), food_spawner=spawner, enable_food=True)
        base_len = len(game.get_snake_positions())
        # Snake head initially at (5,5). One move right to (6,5) eats food and grows.
        game.move_snake(Direction.RIGHT)
        self.assertEqual(len(game.get_snake_positions()), base_len + 1)
        self.assertIsNotNone(game.get_food_position())  # respawned

    def test_self_collision(self):
        game = SnakeGame(5, 5, growth_policy=NoGrowthPolicy())
        # Create a loop: move up, left, down to collide with body
        game.move_snake(Direction.UP)
        game.move_snake(Direction.LEFT)
        game.move_snake(Direction.DOWN)  # likely collides depending on initial shape
        self.assertTrue(game.is_game_over())


if __name__ == "__main__":
    unittest.main(verbosity=2) 