"""Command-line interface for Sudoku PDF generation."""

from __future__ import annotations

import argparse
import random
from typing import Optional, Sequence

from .generator import DIFFICULTIES
from .service import generate_validated_batch

PUZZLES_PER_RUN = 9


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a printable Sudoku PDF with puzzle and solution pages.",
    )
    parser.add_argument(
        "--out",
        default="sudoku.pdf",
        help="Output PDF path (contains puzzles page + solutions page)",
    )
    parser.add_argument(
        "--solutions-out",
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--difficulty",
        default="medium",
        choices=sorted(DIFFICULTIES.keys()),
        help="Puzzle difficulty (controls clue count range)",
    )
    parser.add_argument(
        "--page-size",
        default="a4",
        choices=["a4", "letter"],
        help="PDF page size",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    return parser.parse_args(argv)


def build_rng(seed: Optional[int]) -> random.Random:
    # A missing seed intentionally uses fresh entropy each run.
    return random.Random(seed)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    rng = build_rng(args.seed)
    difficulty = DIFFICULTIES[args.difficulty]

    try:
        from .pdf_renderer import build_combined_pdf
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.startswith("reportlab"):
            raise SystemExit(
                "Missing dependency: reportlab. Install project dependencies with `pip install -e .`."
            ) from exc
        raise

    puzzles, solutions = generate_validated_batch(
        difficulty=difficulty,
        puzzle_count=PUZZLES_PER_RUN,
        rng=rng,
    )

    if args.solutions_out:
        print("Note: --solutions-out is deprecated; solutions are page 2 in --out.")

    build_combined_pdf(
        puzzles=puzzles,
        solutions=solutions,
        out_path=args.out,
        page_size_name=args.page_size,
        difficulty_name=difficulty.name,
    )
    print(f"Wrote combined PDF (puzzles + solutions): {args.out}")


if __name__ == "__main__":
    main()
