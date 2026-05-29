"""Exporter factory: maps a format string to an Exporter."""
from __future__ import annotations

from .base import Exporter
from .markdown import MarkdownExporter
from .pdf_weasyprint import PDFWeasyPrintExporter


EXPORTERS: dict[str, type[Exporter]] = {
    "md": MarkdownExporter,
    "markdown": MarkdownExporter,
    "pdf": PDFWeasyPrintExporter,
}


def create_exporter(fmt: str) -> Exporter:
    """Create an Exporter for ``fmt`` (e.g. 'md', 'pdf')."""
    key = fmt.strip().lower()
    if key not in EXPORTERS:
        supported = ", ".join(sorted(EXPORTERS))
        raise ValueError(
            f"Unknown output format: '{fmt}'. Supported: {supported}"
        )
    return EXPORTERS[key]()
