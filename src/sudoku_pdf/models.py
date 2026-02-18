"""Shared domain models for Sudoku generation and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

Grid = List[List[int]]  # 0 means empty


@dataclass(frozen=True)
class Difficulty:
    name: str
    clues_min: int
    clues_max: int

