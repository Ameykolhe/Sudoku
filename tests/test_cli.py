"""CLI argument parsing and option validation tests."""

from __future__ import annotations

import argparse
import unittest

from sudoku_pdf.cli import parse_args, parse_layout_spec, resolve_puzzle_count


class TestCliLayoutParsing(unittest.TestCase):
    def test_parse_layout_spec_accepts_rows_by_cols(self) -> None:
        self.assertEqual(parse_layout_spec("3x3"), (3, 3))
        self.assertEqual(parse_layout_spec(" 2X4 "), (2, 4))

    def test_parse_layout_spec_rejects_bad_format(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_layout_spec("3-3")

    def test_parse_args_defaults_include_layout_and_orientation(self) -> None:
        args = parse_args([])
        self.assertEqual(args.layout, (3, 2))
        self.assertEqual(args.orientation, "auto")
        self.assertEqual(args.log_level, "info")
        self.assertIsNone(args.puzzles_per_page)

    def test_resolve_puzzle_count_uses_layout_capacity_by_default(self) -> None:
        self.assertEqual(resolve_puzzle_count(rows=3, cols=2, puzzles_per_page=None), 6)

    def test_resolve_puzzle_count_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            resolve_puzzle_count(rows=3, cols=2, puzzles_per_page=0)
        with self.assertRaises(ValueError):
            resolve_puzzle_count(rows=3, cols=2, puzzles_per_page=7)


if __name__ == "__main__":
    unittest.main()
