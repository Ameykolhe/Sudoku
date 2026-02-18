from __future__ import annotations

import unittest

from sudoku_pdf.solver import copy_grid
from sudoku_pdf.validation import grid_is_consistent, validate_puzzle_and_solution

PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


class ValidationTests(unittest.TestCase):
    def test_grid_is_consistent_for_valid_partial_grid(self) -> None:
        self.assertTrue(grid_is_consistent(PUZZLE))

    def test_validate_puzzle_and_solution_accepts_valid_pair(self) -> None:
        self.assertTrue(validate_puzzle_and_solution(PUZZLE, SOLUTION))

    def test_validate_puzzle_and_solution_rejects_mismatched_clue(self) -> None:
        bad_solution = copy_grid(SOLUTION)
        bad_solution[0][0] = 9
        self.assertFalse(validate_puzzle_and_solution(PUZZLE, bad_solution))


if __name__ == "__main__":
    unittest.main()

