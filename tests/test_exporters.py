"""Tests for output exporters."""
from pathlib import Path

import pytest

from src.exporters import create_exporter


_MD = "# タイトル\n\n## 概要\n**force** と double lift の解説。\n\n- 項目A\n- 項目B\n"


def test_markdown_exporter_writes_verbatim(tmp_path: Path):
    out = tmp_path / "note.md"
    res = create_exporter("md").export(_MD, out_path=out, title="note")
    assert res.path == out
    assert out.read_text(encoding="utf-8") == _MD
    assert res.format == "md"


def test_unknown_format_raises():
    with pytest.raises(ValueError):
        create_exporter("docx")


def test_pdf_exporter(tmp_path: Path):
    out = tmp_path / "note.pdf"
    exporter = create_exporter("pdf")
    try:
        res = exporter.export(_MD, out_path=out, title="note")
    except RuntimeError as e:
        pytest.skip(f"WeasyPrint system libraries unavailable: {e}")
    assert res.path.exists()
    assert res.path.stat().st_size > 0
    # A PDF file starts with the %PDF magic bytes.
    assert out.read_bytes()[:4] == b"%PDF"
