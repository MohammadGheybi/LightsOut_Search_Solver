import random
from typing import List, Tuple, Callable, Any
import numpy as np
from time import time


class LightsOutPuzzle:
    def __init__(self, board: List[List[int]]):
        self.board = np.array(board, dtype=np.uint8)
        self.size = len(board)

    def toggle(self, x, y):
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                self.board[nx, ny] ^= 1

    def is_solved(self):
        return np.all(self.board == 0)

    def get_moves(self):
        return [(x, y) for x in range(self.size) for y in range(self.size)]

    def __str__(self):
        return '\n'.join(' '.join(str(cell) for cell in row) for row in self.board)


def create_random_board(size: int,  seed: int, num_toggles: int = None):
    random.seed(time() if seed is None else seed)

    board = [[0 for _ in range(size)] for _ in range(size)]
    puzzle = LightsOutPuzzle(board)

    if num_toggles is None:
        num_toggles = random.randint(1, size * size)

    for _ in range(num_toggles):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        puzzle.toggle(x, y)

    return puzzle.board

def show_solution(
    puzzle: LightsOutPuzzle,
    solution: List[Tuple[int, int]],
    algorithm_name: str,
    nodes_visited: int,
    show_steps: bool = False,
):
    print(f"\nSolving with {algorithm_name}:")
    if solution is None:
        print("No solution found.")
        return
    print(f"Solution: {solution}")
    print(f"Nodes visited: {nodes_visited}")
    if show_steps:
        print("\nSolution steps:")
        for i, move in enumerate(solution):
            print(f"\nStep {i+1}: Toggle position {move}")
            puzzle.toggle(*move)
            print(puzzle)
        print(
            "\nFinal state (solved):"
            if puzzle.is_solved()
            else "\nFinal state (not solved):"
        )
        print(puzzle)
