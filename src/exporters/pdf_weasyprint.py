"""PDF exporter using WeasyPrint (Markdown → HTML → PDF).

WeasyPrint needs system libraries (pango, cairo, gdk-pixbuf, libffi). On macOS:
    brew install pango cairo gdk-pixbuf libffi
The import is deferred so the rest of the tool works even when PDF is unavailable.
"""
from __future__ import annotations

import html as _html
import os
import sys
from pathlib import Path

from .base import Exporter, ExportResult


_CSS_PATH = Path(__file__).resolve().parent / "assets" / "pdf_ja.css"


def _ensure_macos_dyld_path() -> None:
    """Help WeasyPrint find Homebrew libraries on macOS (Apple Silicon/Intel).

    WeasyPrint loads libgobject/pango/cairo via ctypes, which on macOS needs the
    Homebrew lib dir on DYLD_FALLBACK_LIBRARY_PATH. Set it (preserving any
    existing value) so PDF works without the user exporting env vars manually.
    """
    if sys.platform != "darwin":
        return
    existing = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    parts = existing.split(":") if existing else []
    for cand in ("/opt/homebrew/lib", "/usr/local/lib"):
        if os.path.isdir(cand) and cand not in parts:
            parts.append(cand)
    if parts:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(parts)


class PDFWeasyPrintExporter(Exporter):
    @property
    def name(self) -> str:
        return "pdf-weasyprint"

    @property
    def extension(self) -> str:
        return "pdf"

    def export(self, markdown: str, *, out_path: Path, title: str = "") -> ExportResult:
        _ensure_macos_dyld_path()
        try:
            from weasyprint import HTML, CSS
        except (ImportError, OSError) as exc:
            raise RuntimeError(
                "WeasyPrint is unavailable (PDF export).\n"
                "  Install the Python package:  uv add weasyprint\n"
                "  Install system libraries (macOS):  brew install pango cairo gdk-pixbuf libffi\n"
                "  Or drop 'pdf' from the skill's outputs to produce Markdown only.\n"
                f"  Original error: {exc}"
            ) from exc

        import markdown as md_lib

        body = md_lib.markdown(
            markdown,
            extensions=["extra", "sane_lists", "toc", "nl2br"],
        )
        doc = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{_html.escape(title)}</title></head>"
            f"<body>{body}</body></html>"
        )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        stylesheets = [CSS(filename=str(_CSS_PATH))] if _CSS_PATH.exists() else []
        HTML(string=doc).write_pdf(str(out_path), stylesheets=stylesheets)
        return ExportResult(path=out_path, format="pdf")
