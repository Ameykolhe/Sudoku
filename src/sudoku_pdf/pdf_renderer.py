"""PDF rendering for puzzle and solution pages."""

from __future__ import annotations

from typing import List, Optional

from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas

from .models import Grid


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
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x, y + size + 10, label)

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
                pdf.setFont("Helvetica", 11)
                pdf.setFillColorRGB(0, 0, 0)
            elif reference_puzzle[row][col] != 0:
                pdf.setFont("Helvetica-Bold", 11)
                pdf.setFillColorRGB(0, 0, 0)
            else:
                pdf.setFont("Helvetica", 11)
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
    reference_puzzles: Optional[List[Grid]] = None,
    legend: Optional[str] = None,
) -> None:
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(page_w / 2, page_h - 36, title)

    side_padding = 18
    bottom_padding = 18
    header_bottom = page_h - (70 if legend else 56)
    label_space = 14

    if legend:
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(page_w / 2, page_h - 52, legend)

    # Fit a 3x3 square-grid layout with equal outer/inner spacing.
    grid_area_w = page_w - 2 * side_padding
    grid_area_h = header_bottom - bottom_padding
    usable_h = grid_area_h - label_space
    min_gap = 8.0

    puzzle_size = min((grid_area_w - 4 * min_gap) / 3.0, (usable_h - 4 * min_gap) / 3.0)
    if puzzle_size <= 0:
        raise RuntimeError("Page layout is too tight to render puzzles.")

    gap_x = (grid_area_w - 3 * puzzle_size) / 4.0
    gap_y = (usable_h - 3 * puzzle_size) / 4.0
    start_x = side_padding + gap_x
    start_y = bottom_padding + gap_y

    index = 0
    for row in range(3):
        for col in range(3):
            if index >= len(grids):
                break
            x = start_x + col * (puzzle_size + gap_x)
            y = start_y + (2 - row) * (puzzle_size + gap_y)
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
    difficulty_name: str,
) -> None:
    pagesize = letter if page_size_name.lower() == "letter" else A4
    page_w, page_h = pagesize
    pdf = canvas.Canvas(out_path, pagesize=pagesize)

    puzzle_labels = [f"Puzzle {index + 1}" for index in range(len(puzzles))]
    draw_grid_page(
        pdf=pdf,
        page_w=page_w,
        page_h=page_h,
        title=f"SUDOKU - {difficulty_name.capitalize()} Difficulty",
        grids=puzzles,
        labels=puzzle_labels,
    )
    pdf.showPage()

    solution_labels = [f"Puzzle {index + 1} Solution" for index in range(len(solutions))]
    draw_grid_page(
        pdf=pdf,
        page_w=page_w,
        page_h=page_h,
        title=f"SUDOKU - Solutions ({difficulty_name.capitalize()})",
        grids=solutions,
        labels=solution_labels,
        reference_puzzles=puzzles,
        legend="Bold black numbers are original clues. Blue numbers are filled solution values.",
    )
    pdf.showPage()
    pdf.save()

