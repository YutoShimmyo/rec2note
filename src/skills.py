"""Skill loading.

A *skill* is a declarative recipe for turning a recording into a desired
artifact. Each skill is a directory under the top-level ``skills/`` folder:

    skills/<name>/
      skill.yaml          # metadata, generation defaults, outputs
      prompts/<lang>.md   # system prompt(s), one per language

Skills can be added or edited without touching any Python code. Override the
skills directory with the ``MINUTES_SKILLS_DIR`` environment variable.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


# Default location: <repo root>/skills (this file lives in <repo root>/src).
_DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

# Skill used when none is specified on the CLI / in config.
DEFAULT_SKILL = "meeting-minutes"


@dataclass
class SkillSpec:
    name: str
    description: str
    root: Path
    prompt_dir: Path
    # Prompt language selection: "audio" (follow the recording) or "fixed".
    prompt_language_mode: str = "audio"
    fixed_language: str = "ja"
    default_language: str = "ja"
    # Generation defaults (override config.yaml, overridden by CLI).
    defaults: dict = field(default_factory=dict)
    outputs: list[str] = field(default_factory=lambda: ["md"])
    output_subdir: str = ""
    output_stem_suffix: str = ""

    @property
    def subdir(self) -> str:
        """Output subdirectory; defaults to the skill name when unset."""
        return self.output_subdir or self.name


def skills_dir() -> Path:
    """Return the directory skills are loaded from (env-overridable)."""
    override = os.getenv("MINUTES_SKILLS_DIR")
    return Path(override) if override else _DEFAULT_SKILLS_DIR


def list_skills() -> list[str]:
    """List available skill names (directories containing a skill.yaml)."""
    directory = skills_dir()
    if not directory.exists():
        return []
    return sorted(
        p.parent.name for p in directory.glob("*/skill.yaml")
    )


def load_skill(name: str) -> SkillSpec:
    """Load and validate the skill named ``name``."""
    root = skills_dir() / name
    manifest = root / "skill.yaml"
    if not manifest.exists():
        available = ", ".join(list_skills()) or "(none)"
        raise FileNotFoundError(
            f"Skill '{name}' not found at {manifest}.\n"
            f"  Available skills: {available}\n"
            "  Add one by creating skills/<name>/skill.yaml + prompts/<lang>.md,"
            " or set MINUTES_SKILLS_DIR."
        )

    with open(manifest, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    prompt_raw = raw.get("prompt", {}) or {}
    output_raw = raw.get("output", {}) or {}

    return SkillSpec(
        name=raw.get("name", name),
        description=raw.get("description", ""),
        root=root,
        prompt_dir=root / prompt_raw.get("dir", "prompts"),
        prompt_language_mode=prompt_raw.get("language", "audio"),
        fixed_language=prompt_raw.get("fixed_language", "ja"),
        default_language=prompt_raw.get("default_language", "ja"),
        defaults=raw.get("defaults", {}) or {},
        outputs=list(raw.get("outputs", ["md"]) or ["md"]),
        output_subdir=output_raw.get("subdir", "") or "",
        output_stem_suffix=output_raw.get("stem_suffix", "") or "",
    )


def resolve_prompt_language(
    spec: SkillSpec,
    cli_language: str | None = None,
    detected_language: str | None = None,
) -> str:
    """Resolve which prompt language a skill should use.

    - mode "fixed": always ``spec.fixed_language``.
    - mode "audio": the CLI language if explicit, else the ASR-detected
      language, else ``spec.default_language``.
    """
    if spec.prompt_language_mode == "fixed":
        return spec.fixed_language

    lang = cli_language
    if not lang or lang == "auto":
        lang = detected_language
    return lang or spec.default_language
