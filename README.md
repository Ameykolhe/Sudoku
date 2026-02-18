# Sudoku PDF Generator

Generate one printable PDF with two pages:
- page 1: 9 Sudoku puzzles (3x3 layout)
- page 2: matching 9 solutions (3x3 layout)

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
```

By default, each run generates a new random set of puzzles.  
Use `--seed <number>` only when you want reproducible output.

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
