# Sudoku PDF Generator

Generate one printable PDF with two pages:
- page 1: Sudoku puzzles in your selected layout
- page 2: matching solutions in the same layout

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
sudoku-pdf
sudoku-pdf --out sudoku.pdf
sudoku-pdf --difficulty hard --page-size letter --seed 42
sudoku-pdf --layout 3x2 --orientation landscape
sudoku-pdf --layout 3x3 --puzzles-per-page 8
sudoku-pdf --layout 1x3 --log-level debug
```

By default, each run generates a new random set of puzzles.  
Use `--seed <number>` only when you want reproducible output.

Layout and page options:
- `--layout ROWSxCOLS` controls puzzle arrangement per page (for example `3x3`, `3x2`, `2x2`).
- `--puzzles-per-page N` limits how many puzzles are rendered (must be `<= ROWS*COLS`).
- `--orientation auto|portrait|landscape` controls page direction (`auto` picks the best fit for the chosen layout).
- `--log-level info|debug` controls runtime progress logging.

On the solutions page:
- bold black digits are the original puzzle clues
- blue digits are the filled-in solution values

You can also run it directly:

```bash
python -m sudoku_pdf
```

## Project Structure

- `src/sudoku_pdf/cli.py`: argument parsing and application entrypoint
- `src/sudoku_pdf/service.py`: high-level generation orchestration
- `src/sudoku_pdf/generator.py`: puzzle generation logic and difficulty profiles
- `src/sudoku_pdf/solver.py`: Sudoku solving/counting primitives
- `src/sudoku_pdf/validation.py`: puzzle/solution correctness checks
- `src/sudoku_pdf/pdf_renderer.py`: PDF layout and rendering

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
