"""High-level orchestration for generating validated puzzle batches."""

from __future__ import annotations

import logging
import random
from typing import List, Tuple

from .generator import generate_unique_puzzle
from .models import Difficulty, Grid
from .validation import validate_puzzle_and_solution

DEFAULT_VALIDATION_RETRY_BUDGET = 100
logger = logging.getLogger(__name__)


def generate_validated_batch(
    difficulty: Difficulty,
    puzzle_count: int,
    rng: random.Random,
    validation_retry_budget: int = DEFAULT_VALIDATION_RETRY_BUDGET,
) -> Tuple[List[Grid], List[Grid]]:
    logger.info(
        "Generating %d validated puzzle(s) at %s difficulty.",
        puzzle_count,
        difficulty.name,
    )
    puzzles: List[Grid] = []
    solutions: List[Grid] = []

    for puzzle_index in range(puzzle_count):
        accepted = False
        for attempt in range(1, validation_retry_budget + 1):
            puzzle, solution = generate_unique_puzzle(difficulty, rng)
            if validate_puzzle_and_solution(puzzle, solution):
                puzzles.append(puzzle)
                solutions.append(solution)
                accepted = True
                logger.info(
                    "Completed puzzle %d/%d.",
                    puzzle_index + 1,
                    puzzle_count,
                )
                break
            logger.debug(
                "Validation retry %d/%d for puzzle %d/%d.",
                attempt,
                validation_retry_budget,
                puzzle_index + 1,
                puzzle_count,
            )
        if not accepted:
            raise RuntimeError("Failed to validate a generated puzzle.")

    logger.info("Finished generating puzzle batch.")
    return puzzles, solutions
