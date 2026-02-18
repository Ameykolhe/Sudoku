from __future__ import annotations

import random
import unittest

from sudoku_pdf.generator import DIFFICULTIES, generate_unique_puzzle
from sudoku_pdf.validation import validate_puzzle_and_solution


class GeneratorTests(unittest.TestCase):
    def test_generate_unique_puzzle_respects_difficulty_and_validates(self) -> None:
        rng = random.Random(12345)
        difficulty = DIFFICULTIES["easy"]
        puzzle, solution = generate_unique_puzzle(difficulty=difficulty, rng=rng)

        clues = sum(1 for row in puzzle for value in row if value != 0)
        self.assertGreaterEqual(clues, difficulty.clues_min)
        self.assertLessEqual(clues, difficulty.clues_max)
        self.assertTrue(validate_puzzle_and_solution(puzzle, solution))


if __name__ == "__main__":
    unittest.main()

