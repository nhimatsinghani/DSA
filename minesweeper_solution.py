from collections import deque
from typing import List

class Solution:
    def updateBoard(self, board: List[List[str]], click: List[int]) -> List[List[str]]:
        
        if board[click[0]][click[1]] == "M":
            board[click[0]][click[1]] = "X"
            return board

        dirs = [(-1,-1), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1, -1), (0,-1)]
        m, n = len(board), len(board[0])

        def countAdjMines(x, y):
            mines = 0
            for dir_x, dir_y in dirs:
                new_x = x + dir_x
                new_y = y + dir_y

                if 0 <= new_x < m and 0 <= new_y < n:
                    if board[new_x][new_y] == "M":
                        mines += 1

            return mines

        def bfsEmptySquares(x, y):
            queue = deque()
            queue.append((x, y))
            visited = set()
            visited.add((x, y))  # Mark as visited when adding to queue
            
            while queue:
                x, y = queue.popleft()
                
                # Skip if already processed
                if board[x][y] != 'E':
                    continue
                
                adj_mines = countAdjMines(x, y)

                if adj_mines != 0:
                    board[x][y] = str(adj_mines)
                    continue
                
                board[x][y] = 'B'

                # Add neighbors to queue
                for dir_x, dir_y in dirs:
                    new_x = x + dir_x
                    new_y = y + dir_y

                    if not(0 <= new_x < m and 0 <= new_y < n):
                        continue
                    
                    # Only process unrevealed empty squares
                    if board[new_x][new_y] != 'E':
                        continue
                    
                    if (new_x, new_y) in visited:
                        continue

                    visited.add((new_x, new_y))  # Mark as visited when adding
                    queue.append((new_x, new_y))

        bfsEmptySquares(click[0], click[1])
        return board 