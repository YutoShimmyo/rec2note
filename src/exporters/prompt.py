"""Prompt exporter: writes the ready-to-paste prompt (no API call).

This emits the skill's prompt template with the transcript already injected,
so it can be pasted straight into ChatGPT / Claude / any chat UI — no API key
and no API cost. ``main.py`` feeds it the rendered prompt as ``content``.
"""
from __future__ import annotations

from pathlib import Path

from .base import Exporter, ExportResult


class PromptExporter(Exporter):
    @property
    def name(self) -> str:
        return "prompt"

    @property
    def extension(self) -> str:
        return "txt"

    def export(self, markdown: str, *, out_path: Path, title: str = "") -> ExportResult:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        return ExportResult(path=out_path, format="prompt")
