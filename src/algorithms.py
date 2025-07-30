import random
from heapq import heappush, heappop
from typing import List, Tuple, Callable, Any
import numpy as np
from .puzzle import LightsOutPuzzle
from copy import deepcopy


def bfs_solve(puzzle: LightsOutPuzzle) -> Tuple[List[Tuple[int, int]], int]:
    initial_state = deepcopy(puzzle.board)
    fringe = [(initial_state, [])]
    visited = set()
    corrected_format = tuple(map(tuple, initial_state))
    visited.add(corrected_format) 
    z = 0

    while len(fringe) > 0:
        state, moves = fringe.pop(0)
        puzzle.board = state

        if puzzle.is_solved():
            return moves, z

        for move in puzzle.get_moves():
            puzzle.toggle(move[0], move[1])
            new_state = deepcopy(puzzle.board)
            z += 1

            corrected_format = tuple(map(tuple, new_state))
            if corrected_format not in visited:
                visited.add(corrected_format)
                fringe.append((new_state, moves + [move]))

            puzzle.toggle(move[0], move[1])

    return [], z


def dfs_solve(puzzle: LightsOutPuzzle, z, depth=0, max_depth=10, visited=None, moves=None):
    if visited is None:
        visited = set()
    if moves is None:
        moves = []
        z = 0

    if puzzle.is_solved():
        return True, moves, z

    if depth == max_depth:
        return False, [], z

    state = deepcopy(puzzle.board)

    corrected_format = tuple(map(tuple, state))
    if corrected_format in visited: 
        return False, [], z

    visited.add(corrected_format)

    for move in puzzle.get_moves():
        puzzle.toggle(move[0], move[1])
        moves.append((move[0], move[1]))
        z += 1

        found, final_moves, z = dfs_solve(puzzle, z, depth + 1, max_depth, visited, moves)
        if found:
            return True, final_moves, z

        puzzle.toggle(move[0], move[1])
        moves.pop()

    return False, [], z

def ids_solve(puzzle: LightsOutPuzzle, max_depth: int=10) -> Tuple[List[Tuple[int, int]], int]:
    for depth in range(max_depth + 1):
        visited = set()
        moves = []
        z = 0
        found, moves, z = dfs_solve(puzzle, z, 0, depth, visited, moves)
        if found:
            return moves, z

    return [], z


def heuristic1(puzzle: LightsOutPuzzle) -> int:
    h = np.sum(puzzle.board)
    return h

def heuristic2(puzzle: LightsOutPuzzle) -> int:
    center = puzzle.size // 2
    distance = 0
    for x in range(puzzle.size):
        for y in range(puzzle.size):
            if puzzle.board[x, y] == 1:
                distance += abs(x - center) + abs(y - center)
    return distance

def heuristic3(puzzle: LightsOutPuzzle) -> int:
    zero_count = 0
    for x in range(puzzle.size):
        for y in range(puzzle.size):
            if puzzle.board[x, y] == 1:
                adjacent_zeros = 0
                for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    if 0 <= x + dx < puzzle.size and 0 <= y + dy < puzzle.size and puzzle.board[x + dx, y + dy] == 0:
                        adjacent_zeros += 1
                zero_count += adjacent_zeros
    return zero_count

def astar_solve(puzzle: 'LightsOutPuzzle', heuristic: Callable[['LightsOutPuzzle'], int]) -> Tuple[List[Tuple[int, int]], int]:
    initial_state = tuple(map(tuple, puzzle.board))
    fringe = []
    heappush(fringe, (0, 0, initial_state, []))
    visited = set()
    visited.add(initial_state) 
    z = 0

    while len(fringe) > 0:
        f, g, state, moves = heappop(fringe)  
        puzzle.board = np.array(state)
                                
        if puzzle.is_solved():
            return moves, z  
        
        for move in puzzle.get_moves():
            puzzle.toggle(move[0], move[1])
            new_state = tuple(map(tuple, puzzle.board)) 
            z += 1

            if new_state not in visited:
                visited.add(new_state)

                h = heuristic(puzzle) 
                
                new_g = g + 1
                new_f = new_g + h

                heappush(fringe, (new_f, new_g, new_state, moves + [(move[0], move[1])]))

            puzzle.toggle(move[0], move[1])

    print("No solution found.")
    return None, z

def weighted_heuristic1(puzzle: LightsOutPuzzle, alpha):
  return heuristic2(puzzle) * alpha

def weighted_heuristic2(puzzle: LightsOutPuzzle, alpha):
  return heuristic3(puzzle) * alpha

weighted_heuristics = [weighted_heuristic1, weighted_heuristic2]

weights = [2, 5]