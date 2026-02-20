"""PDF rendering for puzzle and solution pages."""

from __future__ import annotations

import logging
from typing import List, Optional

from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.pdfgen import canvas

from .models import Grid

SIDE_PADDING = 18.0
BOTTOM_PADDING = 18.0
HEADER_BOTTOM_NO_LEGEND = 56.0
HEADER_BOTTOM_WITH_LEGEND = 70.0
MIN_GAP = 8.0
LABEL_BAND_HEIGHT = 16.0
LABEL_BASELINE_OFFSET = 4.0
logger = logging.getLogger(__name__)


def _compute_puzzle_size_for_page(
    page_w: float,
    page_h: float,
    layout_rows: int,
    layout_cols: int,
    has_legend: bool,
) -> float:
    header_bottom = page_h - (
        HEADER_BOTTOM_WITH_LEGEND if has_legend else HEADER_BOTTOM_NO_LEGEND
    )
    grid_area_w = page_w - 2 * SIDE_PADDING
    grid_area_h = header_bottom - BOTTOM_PADDING
    usable_h_for_grids = grid_area_h - layout_rows * LABEL_BAND_HEIGHT

    return min(
        (grid_area_w - (layout_cols + 1) * MIN_GAP) / float(layout_cols),
        (usable_h_for_grids - (layout_rows + 1) * MIN_GAP) / float(layout_rows),
    )


def _pick_best_pagesize(
    base_pagesize: tuple[float, float],
    orientation: str,
    layout_rows: int,
    layout_cols: int,
) -> tuple[float, float]:
    normalized = orientation.lower()
    if normalized == "portrait":
        logger.debug("Orientation override selected: portrait.")
        return base_pagesize
    if normalized == "landscape":
        logger.debug("Orientation override selected: landscape.")
        return landscape(base_pagesize)

    portrait_w, portrait_h = base_pagesize
    landscape_w, landscape_h = landscape(base_pagesize)

    portrait_score = min(
        _compute_puzzle_size_for_page(portrait_w, portrait_h, layout_rows, layout_cols, False),
        _compute_puzzle_size_for_page(portrait_w, portrait_h, layout_rows, layout_cols, True),
    )
    landscape_score = min(
        _compute_puzzle_size_for_page(landscape_w, landscape_h, layout_rows, layout_cols, False),
        _compute_puzzle_size_for_page(landscape_w, landscape_h, layout_rows, layout_cols, True),
    )
    logger.debug(
        "Auto orientation scores for %sx%s layout: portrait=%.2f, landscape=%.2f",
        layout_rows,
        layout_cols,
        portrait_score,
        landscape_score,
    )
    return landscape(base_pagesize) if landscape_score > portrait_score else base_pagesize


def draw_sudoku_grid(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    size: float,
    grid: Grid,
    label: str,
    reference_puzzle: Optional[Grid] = None,
    show_numbers: bool = True,
) -> None:
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(x, y + size + LABEL_BASELINE_OFFSET, label)

    cell = size / 9.0

    pdf.setLineWidth(1.4)
    pdf.rect(x, y, size, size)

    pdf.setLineWidth(0.6)
    for index in range(1, 9):
        pdf.line(x + index * cell, y, x + index * cell, y + size)
        pdf.line(x, y + index * cell, x + size, y + index * cell)

    pdf.setLineWidth(1.4)
    for index in (3, 6):
        pdf.line(x + index * cell, y, x + index * cell, y + size)
        pdf.line(x, y + index * cell, x + size, y + index * cell)

    if not show_numbers:
        return

    for row in range(9):
        for col in range(9):
            value = grid[row][col]
            if value == 0:
                continue

            if reference_puzzle is None:
                pdf.setFont("Helvetica-Bold", 16)
                pdf.setFillColorRGB(0, 0, 0)
            elif reference_puzzle[row][col] != 0:
                pdf.setFont("Helvetica-Bold", 16)
                pdf.setFillColorRGB(0, 0, 0)
            else:
                pdf.setFont("Helvetica", 16)
                pdf.setFillColorRGB(0.15, 0.28, 0.62)

            text_x = x + col * cell + cell / 2
            text_y = y + (8 - row) * cell + cell / 2
            pdf.drawCentredString(text_x, text_y - 4, str(value))

    pdf.setFillColorRGB(0, 0, 0)


def draw_grid_page(
    pdf: canvas.Canvas,
    page_w: float,
    page_h: float,
    title: str,
    grids: List[Grid],
    labels: List[str],
    layout_rows: int,
    layout_cols: int,
    reference_puzzles: Optional[List[Grid]] = None,
    legend: Optional[str] = None,
) -> None:
    logger.debug("Rendering page '%s' with %d grid(s).", title, len(grids))
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(page_w / 2, page_h - 36, title)

    header_bottom = page_h - (HEADER_BOTTOM_WITH_LEGEND if legend else HEADER_BOTTOM_NO_LEGEND)

    if legend:
        pdf.setFont("Helvetica", 11)
        pdf.drawCentredString(page_w / 2, page_h - 52, legend)

    # Fit the requested layout with equal outer/inner spacing.
    grid_area_w = page_w - 2 * SIDE_PADDING
    grid_area_h = header_bottom - BOTTOM_PADDING
    usable_h_for_grids = grid_area_h - layout_rows * LABEL_BAND_HEIGHT

    puzzle_size = _compute_puzzle_size_for_page(
        page_w=page_w,
        page_h=page_h,
        layout_rows=layout_rows,
        layout_cols=layout_cols,
        has_legend=legend is not None,
    )
    if puzzle_size <= 0:
        raise RuntimeError("Page layout is too tight to render puzzles.")
    logger.debug(
        "Computed layout metrics for '%s': size=%.2f, rows=%d, cols=%d.",
        title,
        puzzle_size,
        layout_rows,
        layout_cols,
    )

    gap_x = (grid_area_w - layout_cols * puzzle_size) / float(layout_cols + 1)
    gap_y = (usable_h_for_grids - layout_rows * puzzle_size) / float(layout_rows + 1)
    start_x = SIDE_PADDING + gap_x
    start_y = BOTTOM_PADDING + gap_y

    index = 0
    for row in range(layout_rows):
        for col in range(layout_cols):
            if index >= len(grids):
                break
            x = start_x + col * (puzzle_size + gap_x)
            y = start_y + (layout_rows - 1 - row) * (puzzle_size + LABEL_BAND_HEIGHT + gap_y)
            draw_sudoku_grid(
                pdf=pdf,
                x=x,
                y=y,
                size=puzzle_size,
                grid=grids[index],
                label=labels[index] if index < len(labels) else f"Puzzle {index + 1}",
                reference_puzzle=(
                    reference_puzzles[index]
                    if reference_puzzles is not None and index < len(reference_puzzles)
                    else None
                ),
                show_numbers=True,
            )
            index += 1


def build_combined_pdf(
    puzzles: List[Grid],
    solutions: List[Grid],
    out_path: str,
    page_size_name: str,
    orientation: str,
    layout_rows: int,
    layout_cols: int,
    difficulty_name: str,
    puzzles_per_page: int = 0,
    page_order: str = "sequential",
) -> None:
    base_pagesize = letter if page_size_name.lower() == "letter" else A4
    pagesize = _pick_best_pagesize(
        base_pagesize=base_pagesize,
        orientation=orientation,
        layout_rows=layout_rows,
        layout_cols=layout_cols,
    )
    page_w, page_h = pagesize
    resolved_orientation = "landscape" if page_w > page_h else "portrait"
    logger.info(
        "Rendering PDF to %s (%s, %s orientation, layout=%sx%s).",
        out_path,
        page_size_name,
        resolved_orientation,
        layout_rows,
        layout_cols,
    )
    pdf = canvas.Canvas(out_path, pagesize=pagesize)

    effective_ppp = puzzles_per_page if puzzles_per_page > 0 else len(puzzles)
    chunks = [
        (puzzles[i : i + effective_ppp], solutions[i : i + effective_ppp])
        for i in range(0, len(puzzles), effective_ppp)
    ]
    num_pages = len(chunks)

    def puzzle_title(page_idx: int) -> str:
        base = f"SUDOKU - {difficulty_name.capitalize()} Difficulty"
        return f"{base} (Page {page_idx + 1} of {num_pages})" if num_pages > 1 else base

    def solution_title(page_idx: int) -> str:
        base = f"SUDOKU - Solutions ({difficulty_name.capitalize()})"
        return f"{base} (Page {page_idx + 1} of {num_pages})" if num_pages > 1 else base

    def render_puzzle_page(page_idx: int, puz_chunk: List[Grid]) -> None:
        global_offset = page_idx * effective_ppp
        labels = [f"Puzzle {global_offset + j + 1}" for j in range(len(puz_chunk))]
        draw_grid_page(
            pdf=pdf,
            page_w=page_w,
            page_h=page_h,
            title=puzzle_title(page_idx),
            grids=puz_chunk,
            labels=labels,
            layout_rows=layout_rows,
            layout_cols=layout_cols,
        )
        logger.info("Rendered puzzles page %d of %d.", page_idx + 1, num_pages)
        pdf.showPage()

    def render_solution_page(page_idx: int, puz_chunk: List[Grid], sol_chunk: List[Grid]) -> None:
        global_offset = page_idx * effective_ppp
        labels = [f"Puzzle {global_offset + j + 1} Solution" for j in range(len(sol_chunk))]
        draw_grid_page(
            pdf=pdf,
            page_w=page_w,
            page_h=page_h,
            title=solution_title(page_idx),
            grids=sol_chunk,
            labels=labels,
            layout_rows=layout_rows,
            layout_cols=layout_cols,
            reference_puzzles=puz_chunk,
            legend="Bold black numbers are original clues. Blue numbers are filled solution values.",
        )
        logger.info("Rendered solutions page %d of %d.", page_idx + 1, num_pages)
        pdf.showPage()

    if page_order == "alternate":
        for page_idx, (puz_chunk, sol_chunk) in enumerate(chunks):
            render_puzzle_page(page_idx, puz_chunk)
            render_solution_page(page_idx, puz_chunk, sol_chunk)
    else:  # sequential
        for page_idx, (puz_chunk, _) in enumerate(chunks):
            render_puzzle_page(page_idx, puz_chunk)
        for page_idx, (puz_chunk, sol_chunk) in enumerate(chunks):
            render_solution_page(page_idx, puz_chunk, sol_chunk)

    pdf.save()
    logger.info("PDF save complete.")
