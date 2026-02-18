"""Orientation auto-selection tests for PDF layout fit."""

from __future__ import annotations

import unittest

try:
    from reportlab.lib.pagesizes import A4, landscape

    from sudoku_pdf.pdf_renderer import _pick_best_pagesize

    RENDERER_IMPORT_ERROR = None
except ModuleNotFoundError as exc:  # pragma: no cover - dependency-gated
    A4 = None  # type: ignore[assignment]
    landscape = None  # type: ignore[assignment]
    _pick_best_pagesize = None  # type: ignore[assignment]
    RENDERER_IMPORT_ERROR = exc


@unittest.skipIf(RENDERER_IMPORT_ERROR is not None, "reportlab is not installed")
class TestAutoOrientation(unittest.TestCase):
    def test_auto_prefers_landscape_for_wide_layout(self) -> None:
        chosen = _pick_best_pagesize(A4, "auto", layout_rows=1, layout_cols=3)
        self.assertEqual(chosen, landscape(A4))

    def test_auto_prefers_portrait_for_tall_layout(self) -> None:
        chosen = _pick_best_pagesize(A4, "auto", layout_rows=3, layout_cols=1)
        self.assertEqual(chosen, A4)


if __name__ == "__main__":
    unittest.main()
