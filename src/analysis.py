from .puzzle import LightsOutPuzzle, create_random_board, show_solution
from .algorithms import bfs_solve, ids_solve, astar_solve, weighted_heuristic1, weighted_heuristic2, weighted_heuristics, weights, heuristic1, heuristic2, heuristic3
from copy import deepcopy
from typing import List, Tuple, Callable, Any
from time import time
from tabulate import tabulate
from enum import Enum
from dataclasses import dataclass
import threading
from functools import partial


tests = [
    create_random_board(3, 42),
    create_random_board(3, 41),
    create_random_board(3, 42, 5),
    create_random_board(4, 42),
    create_random_board(4, 41),
    create_random_board(4, 42, 5),
    create_random_board(5, 42),
    create_random_board(5, 41),
    create_random_board(5, 42, 5),
]

class SearchStatus(Enum):
    SOLVED = "Solved"
    TIMEOUT = "Timeout"
    NO_SOLUTION = "No Solution"

@dataclass
class SearchResult:
    result: SearchStatus
    solution: Any = None
    nodes_visited: int = None
    time: float = None

    def __str__(self):
        output = f"Result: {self.result.value}\n"
        if self.result == SearchStatus.SOLVED:
            output += f"Solution: {self.solution}\n"
        if self.result != SearchStatus.TIMEOUT:
            output += f"Nodes Visited: {self.nodes_visited}\n"
            output += f"Time Taken: {self.time:.3f} seconds\n"

        return output


DEFAULT_SEARCH_RESULT = SearchResult(SearchStatus.TIMEOUT, None, None, float("inf"))


def run_searches(func: Callable, args: Any, time_limit: float = 60.0, name: str = "") -> SearchResult:
    result = []

    def target():
        try:
            solution, nodes_visited = func(*args)
            result.append((solution, nodes_visited))
        except Exception as e:
            result.append(e)

    thread = threading.Thread(target=target)
    thread.start()

    start_time = time()
    thread.join(timeout=time_limit)

    if thread.is_alive() or not result:
        print(f"\nTime limit of {time_limit} seconds exceeded for {name}")
        return SearchResult(SearchStatus.TIMEOUT)

    if isinstance(result[0], Exception):
        raise result[0]

    solution, nodes_visited = result[0]
    show_solution(args[0], solution, name, nodes_visited)
    time_taken = time() - start_time
    return SearchResult(SearchStatus.SOLVED if solution else SearchStatus.NO_SOLUTION, solution, nodes_visited, time_taken)

def run_test(test: List, heuristics: List[Callable[[Any], int]], time_limit: float = 60.0):

    print(f"Running test:\n {test}")

    puzzle = LightsOutPuzzle(test)

    bfs_result = run_searches(bfs_solve, (deepcopy(puzzle),), name="BFS", time_limit=time_limit)
    ids_result = run_searches(ids_solve, (deepcopy(puzzle),), name="IDS", time_limit=time_limit)

    astar_results = []
    for heuristic in heuristics:
        astar_results.append(
            run_searches(
                astar_solve,
                (deepcopy(puzzle), heuristic),
                name=f"A*({heuristic.__name__})",
                time_limit=time_limit,
            )
        )

    weighted_astar_results = []
    for heuristic in weighted_heuristics:
        for weight in weights:
          weighted_astar_results.append(
              run_searches(
                  astar_solve,
                  (deepcopy(puzzle), partial(heuristic, alpha = weight)),
                  name=f"weighted A*({heuristic.__name__}, alpha = {weight})",
                  time_limit=time_limit,
              )
          )

    print("\n-------------------------------\n")

    return (
        test,
        bfs_result,
        ids_result,
        *astar_results,
        *weighted_astar_results
    )

results: List[Tuple[str, SearchResult, SearchResult, SearchResult, SearchResult]] = []
heuristics = [heuristic1, heuristic2, heuristic3]
for test in tests:
    results.append(run_test(test, heuristics, 180))

table_data: List[List[str]] = []

for result in results:
    table_data.append(
        [
            "\n".join(" ".join(str(cell) for cell in row) for row in result[0]),
            str(result[1]),
            str(result[2]),
        ]
    )

    for i in range(len(heuristics)):
        table_data[-1].append(str(result[3 + i]))

    for i in range(len(weighted_heuristics)):
        for j in range(len(weights)):
          table_data[-1].append(str(result[3 + len(heuristics) + i * 2 + j]))

    table_data.append("\n\n\n")

if table_data[-1] == "\n\n\n":
    table_data.pop()

print(len(table_data))
print("Results:")
print(
    tabulate(
        table_data,
        headers=[
            "Test",
            "BFS",
            "IDS",
            *[f"A* ({heuristic.__name__})" for heuristic in heuristics],
            *[f"Weighted A* ({heuristic.__name__}, alpha = {weight})" for heuristic in weighted_heuristics for weight in weights]
        ],
        floatfmt=".3f",
        numalign="center",
        stralign="center",
        tablefmt="grid",
    )
)
