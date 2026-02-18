"""Sudoku solving primitives used by generation and validation."""

from __future__ import annotations

import random
from typing import Optional, Tuple

from .models import Grid


def empty_grid() -> Grid:
    return [[0] * 9 for _ in range(9)]


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def find_empty(grid: Grid) -> Optional[Tuple[int, int]]:
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return row, col
    return None


def is_value_valid(grid: Grid, row: int, col: int, value: int) -> bool:
    if any(grid[row][x] == value for x in range(9)):
        return False
    if any(grid[x][col] == value for x in range(9)):
        return False

    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    for rr in range(box_row, box_row + 3):
        for cc in range(box_col, box_col + 3):
            if grid[rr][cc] == value:
                return False
    return True


def solve_one_random(grid: Grid, rng: random.Random) -> bool:
    spot = find_empty(grid)
    if spot is None:
        return True
    row, col = spot

    values = list(range(1, 10))
    rng.shuffle(values)
    for value in values:
        if is_value_valid(grid, row, col, value):
            grid[row][col] = value
            if solve_one_random(grid, rng):
                return True
            grid[row][col] = 0
    return False


def solve_one_deterministic(grid: Grid) -> bool:
    spot = find_empty(grid)
    if spot is None:
        return True
    row, col = spot

    for value in range(1, 10):
        if is_value_valid(grid, row, col, value):
            grid[row][col] = value
            if solve_one_deterministic(grid):
                return True
            grid[row][col] = 0
    return False


def count_solutions(
    grid: Grid,
    limit: int = 2,
    rng: Optional[random.Random] = None,
) -> int:
    spot = find_empty(grid)
    if spot is None:
        return 1
    row, col = spot

    values = list(range(1, 10))
    if rng is not None:
        rng.shuffle(values)

    total = 0
    for value in values:
        if is_value_valid(grid, row, col, value):
            grid[row][col] = value
            total += count_solutions(grid, limit=limit, rng=rng)
            grid[row][col] = 0
            if total >= limit:
                return total
    return total

