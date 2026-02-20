"""Command-line interface for Sudoku PDF generation."""

from __future__ import annotations

import argparse
import logging
import random
import re
from typing import Optional, Sequence

from .generator import DIFFICULTIES
from .service import generate_validated_batch

DEFAULT_LAYOUT = "3x2"
LOG_LEVEL_CHOICES = ["info", "debug"]
logger = logging.getLogger(__name__)


def parse_layout_spec(layout: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*[xX]\s*(\d+)\s*", layout)
    if not match:
        raise argparse.ArgumentTypeError(
            "Layout must use ROWSxCOLS format (for example: 3x3 or 3x2)."
        )

    rows = int(match.group(1))
    cols = int(match.group(2))
    if rows <= 0 or cols <= 0:
        raise argparse.ArgumentTypeError("Layout rows and columns must both be positive.")

    return rows, cols


def resolve_puzzle_count(
    *,
    rows: int,
    cols: int,
    puzzles_per_page: Optional[int],
    pages: int = 1,
) -> int:
    max_capacity = rows * cols
    if puzzles_per_page is None:
        return max_capacity * pages
    if puzzles_per_page <= 0:
        raise ValueError("--puzzles-per-page must be a positive integer.")
    if puzzles_per_page > max_capacity:
        raise ValueError(
            f"--puzzles-per-page ({puzzles_per_page}) exceeds layout capacity "
            f"({rows}x{cols} => {max_capacity})."
        )
    return puzzles_per_page * pages


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
    parser.add_argument(
        "--orientation",
        default="auto",
        choices=["auto", "portrait", "landscape"],
        help="Page orientation (`auto` picks best fit for the chosen layout)",
    )
    parser.add_argument(
        "--layout",
        default=DEFAULT_LAYOUT,
        type=parse_layout_spec,
        help="Puzzle grid layout as ROWSxCOLS (for example: 3x3, 3x2, 2x2)",
    )
    parser.add_argument(
        "--puzzles-per-page",
        type=int,
        default=None,
        help="How many puzzles to place on each page (must be <= layout capacity)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of puzzle pages to generate (default: 1)",
    )
    parser.add_argument(
        "--page-order",
        default="sequential",
        choices=["sequential", "alternate"],
        help=(
            "Order of puzzle and solution pages. "
            "`sequential`: all puzzle pages then all solution pages. "
            "`alternate`: puzzle page followed immediately by its solution page "
            "(good for back-to-back/duplex printing)."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=LOG_LEVEL_CHOICES,
        help="Logging verbosity (`info` or `debug`)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    return parser.parse_args(argv)


def build_rng(seed: Optional[int]) -> random.Random:
    # A missing seed intentionally uses fresh entropy each run.
    return random.Random(seed)


def configure_logging(log_level: str) -> None:
    level = logging.DEBUG if log_level == "debug" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-5s | %(name)-24s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    configure_logging(args.log_level)
    rng = build_rng(args.seed)
    difficulty = DIFFICULTIES[args.difficulty]
    layout_rows, layout_cols = args.layout

    if args.pages < 1:
        raise SystemExit("--pages must be a positive integer.")

    effective_ppp = args.puzzles_per_page or (layout_rows * layout_cols)

    try:
        puzzle_count = resolve_puzzle_count(
            rows=layout_rows,
            cols=layout_cols,
            puzzles_per_page=args.puzzles_per_page,
            pages=args.pages,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    try:
        from .pdf_renderer import build_combined_pdf
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.startswith("reportlab"):
            raise SystemExit(
                "Missing dependency: reportlab. Install project dependencies with `pip install -e .`."
            ) from exc
        raise

    logger.info(
        "Starting generation: difficulty=%s, layout=%sx%s, puzzles=%d, pages=%d, page_order=%s, page_size=%s, orientation=%s",
        difficulty.name,
        layout_rows,
        layout_cols,
        puzzle_count,
        args.pages,
        args.page_order,
        args.page_size,
        args.orientation,
    )
    logger.debug("CLI seed value: %s", args.seed)

    puzzles, solutions = generate_validated_batch(
        difficulty=difficulty,
        puzzle_count=puzzle_count,
        rng=rng,
    )

    if args.solutions_out:
        logger.info("Note: --solutions-out is deprecated; solutions are page 2 in --out.")

    build_combined_pdf(
        puzzles=puzzles,
        solutions=solutions,
        out_path=args.out,
        page_size_name=args.page_size,
        orientation=args.orientation,
        layout_rows=layout_rows,
        layout_cols=layout_cols,
        difficulty_name=difficulty.name,
        puzzles_per_page=effective_ppp,
        page_order=args.page_order,
    )
    logger.info("Wrote combined PDF (puzzles + solutions): %s", args.out)


if __name__ == "__main__":
    main()
