"""Markdown exporter: writes the generated Markdown verbatim."""
from __future__ import annotations

from pathlib import Path

from .base import Exporter, ExportResult


class MarkdownExporter(Exporter):
    @property
    def name(self) -> str:
        return "markdown"

    @property
    def extension(self) -> str:
        return "md"

    def export(self, markdown: str, *, out_path: Path, title: str = "") -> ExportResult:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        return ExportResult(path=out_path, format="md")
