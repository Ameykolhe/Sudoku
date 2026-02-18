"""Validation utilities for generated puzzle/solution pairs."""

from __future__ import annotations

from typing import List

from .models import Grid
from .solver import copy_grid, count_solutions, solve_one_deterministic


def has_no_duplicates(values: List[int]) -> bool:
    seen = set()
    for value in values:
        if value == 0:
            continue
        if value in seen:
            return False
        seen.add(value)
    return True


def grid_is_consistent(grid: Grid) -> bool:
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        return False

    for row in range(9):
        if not has_no_duplicates(grid[row]):
            return False

    for col in range(9):
        values = [grid[row][col] for row in range(9)]
        if not has_no_duplicates(values):
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box_values = [
                grid[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            ]
            if not has_no_duplicates(box_values):
                return False

    for row in grid:
        for value in row:
            if not isinstance(value, int) or not (0 <= value <= 9):
                return False

    return True


def validate_puzzle_and_solution(puzzle: Grid, solution: Grid) -> bool:
    if not grid_is_consistent(puzzle) or not grid_is_consistent(solution):
        return False

    if any(0 in row for row in solution):
        return False

    for row in range(9):
        for col in range(9):
            puzzle_value = puzzle[row][col]
            if puzzle_value != 0 and puzzle_value != solution[row][col]:
                return False

    uniqueness_probe = copy_grid(puzzle)
    if count_solutions(uniqueness_probe, limit=2) != 1:
        return False

    solved = copy_grid(puzzle)
    if not solve_one_deterministic(solved):
        return False
    if solved != solution:
        return False

    return True

