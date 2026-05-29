"""Centralized prompt loading and transcript injection.

Prompts live as plain text/Markdown files, one per language (``ja.md``,
``en.md``, …). By default they are read from the top-level ``prompts/``
directory, but a skill supplies its own ``prompts/`` directory via the
``prompt_dir`` argument (see :mod:`src.skills`).

Override the default prompts directory with ``MINUTES_PROMPTS_DIR``.
"""
from __future__ import annotations

import os
from pathlib import Path


# Default location: <repo root>/prompts (this file lives in <repo root>/src).
_DEFAULT_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Language used when the requested one has no prompt file (or is "auto"/unknown).
DEFAULT_LANGUAGE = "ja"

# Placeholders that, when present in a prompt, mark where the transcript goes.
_TRANSCRIPT_PLACEHOLDERS = ("{transcript}", "[transcript]")


def prompts_dir() -> Path:
    """Return the default directory prompts are loaded from (env-overridable)."""
    override = os.getenv("MINUTES_PROMPTS_DIR")
    return Path(override) if override else _DEFAULT_PROMPTS_DIR


def available_languages(prompt_dir: Path | None = None) -> list[str]:
    """List language codes that have a prompt file, e.g. ['en', 'ja']."""
    directory = prompt_dir or prompts_dir()
    return sorted(p.stem for p in directory.glob("*.md") if p.stem != "README")


def load_prompt(
    language: str = DEFAULT_LANGUAGE,
    *,
    prompt_dir: Path | None = None,
    default_language: str = DEFAULT_LANGUAGE,
) -> str:
    """Load the system prompt for ``language``.

    Args:
        language: requested language code (e.g. "ja", "en").
        prompt_dir: directory to read from. Defaults to :func:`prompts_dir`.
        default_language: fallback when the requested language has no file.

    Falls back to ``default_language`` when the requested language has no
    prompt file (including ``"auto"`` or any unknown code).
    """
    directory = prompt_dir or prompts_dir()
    candidate = directory / f"{language}.md"
    if not candidate.exists():
        candidate = directory / f"{default_language}.md"

    if not candidate.exists():
        raise FileNotFoundError(
            f"No prompt file found for language '{language}' in {directory}.\n"
            f"  Expected: {directory / f'{language}.md'} "
            f"or {directory / f'{default_language}.md'}\n"
            "  Add a '<lang>.md' file, or check the skill's prompts/ directory."
        )
    return candidate.read_text(encoding="utf-8").strip()


def render_prompt(template: str, transcript: str) -> str:
    """Inject ``transcript`` into a prompt ``template``.

    If the template contains a ``{transcript}`` / ``[transcript]`` placeholder,
    the transcript is substituted there (the author controls its position).
    Otherwise the transcript is appended to the end of the template.
    """
    for placeholder in _TRANSCRIPT_PLACEHOLDERS:
        if placeholder in template:
            return template.replace(placeholder, transcript)
    return f"{template}\n\n{transcript}"
