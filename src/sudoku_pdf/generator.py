"""Sudoku puzzle generation logic."""

from __future__ import annotations

import logging
import random
from typing import Dict, Tuple

from .models import Difficulty, Grid
from .solver import copy_grid, count_solutions, empty_grid, solve_one_random

DEFAULT_GENERATION_RETRY_BUDGET = 250
logger = logging.getLogger(__name__)

DIFFICULTIES: Dict[str, Difficulty] = {
    "easy": Difficulty("easy", clues_min=38, clues_max=45),
    "medium": Difficulty("medium", clues_min=30, clues_max=37),
    "hard": Difficulty("hard", clues_min=24, clues_max=29),
}


def generate_full_solution(rng: random.Random) -> Grid:
    attempts = 0
    while True:
        attempts += 1
        grid = empty_grid()
        if solve_one_random(grid, rng):
            logger.debug("Generated full solved grid after %d attempt(s).", attempts)
            return grid


def _clue_count(grid: Grid) -> int:
    return sum(1 for row in range(9) for col in range(9) if grid[row][col] != 0)


def make_puzzle_from_solution(
    solution: Grid,
    clues_target: int,
    rng: random.Random,
) -> Grid:
    puzzle = copy_grid(solution)
    starting_clues = _clue_count(puzzle)
    cells = [(row, col) for row in range(9) for col in range(9)]
    rng.shuffle(cells)

    for row, col in cells:
        if _clue_count(puzzle) <= clues_target:
            break
        if puzzle[row][col] == 0:
            continue

        backup = puzzle[row][col]
        puzzle[row][col] = 0

        uniqueness_probe = copy_grid(puzzle)
        if count_solutions(uniqueness_probe, limit=2) != 1:
            puzzle[row][col] = backup

    logger.debug(
        "Reduced puzzle clues from %d to %d (target=%d).",
        starting_clues,
        _clue_count(puzzle),
        clues_target,
    )
    return puzzle


def generate_unique_puzzle(
    difficulty: Difficulty,
    rng: random.Random,
    retry_budget: int = DEFAULT_GENERATION_RETRY_BUDGET,
) -> Tuple[Grid, Grid]:
    logger.debug(
        "Generating unique puzzle (difficulty=%s, clue-range=%d-%d, retry_budget=%d).",
        difficulty.name,
        difficulty.clues_min,
        difficulty.clues_max,
        retry_budget,
    )
    for attempt in range(1, retry_budget + 1):
        solution = generate_full_solution(rng)
        target = rng.randint(difficulty.clues_min, difficulty.clues_max)
        puzzle = make_puzzle_from_solution(solution, clues_target=target, rng=rng)

        uniqueness_probe = copy_grid(puzzle)
        if count_solutions(uniqueness_probe, limit=2) == 1:
            logger.debug(
                "Accepted puzzle on attempt %d with %d clues.",
                attempt,
                _clue_count(puzzle),
            )
            return puzzle, solution
        logger.debug("Rejected non-unique candidate on attempt %d.", attempt)

    raise RuntimeError("Failed to generate a unique puzzle within retry budget.")
