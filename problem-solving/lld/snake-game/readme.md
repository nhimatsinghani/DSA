Game of Snakes
Remember the old phone game of snake? The snake can move up, down, left or right in a 2Dimensional board of arbitrary size.
Lets try to pmplement the bae logic of this game
Rules:
• Every time moveSnake() is called, the snake moves up, down, left or right
• The snake’s initial size is 3 and grows by 1 every 5 moves
• The game ends when the snake hits itself
We can use the following as a starting point (pseudo-code):
Interface SnakeGame {
moveSnake(snakeDirection);
isGameOver();
}

Proposed Changes
Change#1
Make scale-up 2 optional
Remove scale-up 2 completely
Change#2
Add new optional scale up: snake grows when it eats food rather than every 5moves. Food is dropped at a random position on the board.
