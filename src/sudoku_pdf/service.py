"""High-level orchestration for generating validated puzzle batches."""

from __future__ import annotations

import random
from typing import List, Tuple

from .generator import generate_unique_puzzle
from .models import Difficulty, Grid
from .validation import validate_puzzle_and_solution

DEFAULT_VALIDATION_RETRY_BUDGET = 100


def generate_validated_batch(
    difficulty: Difficulty,
    puzzle_count: int,
    rng: random.Random,
    validation_retry_budget: int = DEFAULT_VALIDATION_RETRY_BUDGET,
) -> Tuple[List[Grid], List[Grid]]:
    puzzles: List[Grid] = []
    solutions: List[Grid] = []

    for _ in range(puzzle_count):
        accepted = False
        for _attempt in range(validation_retry_budget):
            puzzle, solution = generate_unique_puzzle(difficulty, rng)
            if validate_puzzle_and_solution(puzzle, solution):
                puzzles.append(puzzle)
                solutions.append(solution)
                accepted = True
                break
        if not accepted:
            raise RuntimeError("Failed to validate a generated puzzle.")

    return puzzles, solutions

