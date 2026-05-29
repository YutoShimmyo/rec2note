"""Configuration management: loads config.yaml and merges CLI overrides."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


@dataclass
class ASRConfig:
    preset: str = "auto"
    backend: str = ""
    model: str = ""
    device: str = ""


@dataclass
class MinutesAPIConfig:
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"


@dataclass
class MinutesLocalConfig:
    runtime: str = "mlx-lm"
    model_path: str = "mlx-community/gemma-3-4b-it-4bit"
    ollama_model: str = "gemma2:9b"
    ollama_url: str = "http://localhost:11434"


@dataclass
class MinutesConfig:
    backend: str = "none"
    # Prompt/output language for the generated minutes.
    # "auto" = follow the lecture (audio) language (default),
    # "ja" = force Japanese, "en" = force English.
    output_language: str = "auto"
    # Generation cap. Skills may raise this for long, uncompressed output.
    max_tokens: int = 2048
    api: MinutesAPIConfig = field(default_factory=MinutesAPIConfig)
    local: MinutesLocalConfig = field(default_factory=MinutesLocalConfig)


@dataclass
class SkillConfig:
    # Which skill (recipe) to run. Default keeps backward-compatible behavior.
    name: str = "meeting-minutes"
    # Output formats to produce, e.g. ["md", "pdf"].
    outputs: list[str] = field(default_factory=lambda: ["md"])


@dataclass
class AppConfig:
    profile: str = "standard"
    language: str = "auto"
    skill: SkillConfig = field(default_factory=SkillConfig)
    asr: ASRConfig = field(default_factory=ASRConfig)
    minutes: MinutesConfig = field(default_factory=MinutesConfig)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load configuration from a YAML file, falling back to defaults."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not path.exists():
        if config_path:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        return AppConfig()

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    cfg = AppConfig()
    cfg.profile = raw.get("profile", cfg.profile)
    cfg.language = raw.get("language", cfg.language)

    skill_raw = raw.get("skill", {}) or {}
    if isinstance(skill_raw, str):  # allow `skill: magic-lecture` shorthand
        skill_raw = {"name": skill_raw}
    cfg.skill.name = skill_raw.get("name", cfg.skill.name)
    cfg.skill.outputs = list(skill_raw.get("outputs", cfg.skill.outputs) or cfg.skill.outputs)

    asr_raw = raw.get("asr", {})
    cfg.asr.preset = asr_raw.get("preset", cfg.asr.preset)
    cfg.asr.backend = asr_raw.get("backend", cfg.asr.backend) or ""
    cfg.asr.model = asr_raw.get("model", cfg.asr.model) or ""
    cfg.asr.device = asr_raw.get("device", cfg.asr.device) or ""

    min_raw = raw.get("minutes", {})
    cfg.minutes.backend = min_raw.get("backend", cfg.minutes.backend)
    cfg.minutes.output_language = min_raw.get("output_language", cfg.minutes.output_language)
    cfg.minutes.max_tokens = min_raw.get("max_tokens", cfg.minutes.max_tokens)

    api_raw = min_raw.get("api", {})
    cfg.minutes.api.provider = api_raw.get("provider", cfg.minutes.api.provider)
    cfg.minutes.api.model = api_raw.get("model", cfg.minutes.api.model)

    local_raw = min_raw.get("local", {})
    cfg.minutes.local.runtime = local_raw.get("runtime", cfg.minutes.local.runtime)
    cfg.minutes.local.model_path = local_raw.get("model_path", cfg.minutes.local.model_path) or ""
    cfg.minutes.local.ollama_model = local_raw.get("ollama_model", cfg.minutes.local.ollama_model)
    cfg.minutes.local.ollama_url = local_raw.get("ollama_url", cfg.minutes.local.ollama_url)

    return cfg


def apply_skill_defaults(cfg: AppConfig, skill_defaults: dict, outputs: list[str]) -> AppConfig:
    """Apply a skill's generation defaults on top of config.yaml values.

    Precedence: CLI > skill.yaml > config.yaml > code defaults. This function
    layers skill.yaml over the already-loaded config; CLI is applied afterwards.
    Only keys the skill actually specifies are overridden.
    """
    d = skill_defaults or {}
    if "backend" in d:
        cfg.minutes.backend = d["backend"]
    if "output_language" in d:
        cfg.minutes.output_language = d["output_language"]
    if "max_tokens" in d:
        cfg.minutes.max_tokens = d["max_tokens"]

    api = d.get("api", {}) or {}
    if "provider" in api:
        cfg.minutes.api.provider = api["provider"]
    if "model" in api:
        cfg.minutes.api.model = api["model"]

    local = d.get("local", {}) or {}
    if "runtime" in local:
        cfg.minutes.local.runtime = local["runtime"]
    if "model_path" in local:
        cfg.minutes.local.model_path = local["model_path"]
    if "ollama_model" in local:
        cfg.minutes.local.ollama_model = local["ollama_model"]
    if "ollama_url" in local:
        cfg.minutes.local.ollama_url = local["ollama_url"]

    if outputs:
        cfg.skill.outputs = list(outputs)
    return cfg


def apply_cli_overrides(cfg: AppConfig, args: argparse.Namespace) -> AppConfig:
    """Apply CLI argument overrides on top of the loaded config."""
    if getattr(args, "language", None):
        cfg.language = args.language
    if getattr(args, "profile", None):
        cfg.profile = args.profile
    if getattr(args, "asr_preset", None):
        cfg.asr.preset = args.asr_preset
    if getattr(args, "asr_backend", None):
        cfg.asr.backend = args.asr_backend
    if getattr(args, "asr_model", None):
        cfg.asr.model = args.asr_model
    if getattr(args, "minutes_backend", None):
        cfg.minutes.backend = args.minutes_backend
    if getattr(args, "minutes_provider", None):
        cfg.minutes.api.provider = args.minutes_provider
    if getattr(args, "minutes_language", None):
        cfg.minutes.output_language = args.minutes_language
    if getattr(args, "minutes_local_runtime", None):
        cfg.minutes.local.runtime = args.minutes_local_runtime
    if getattr(args, "minutes_model", None):
        if cfg.minutes.backend == "api":
            cfg.minutes.api.model = args.minutes_model
        elif cfg.minutes.local.runtime == "ollama":
            cfg.minutes.local.ollama_model = args.minutes_model
        else:
            cfg.minutes.local.model_path = args.minutes_model
    if getattr(args, "minutes_max_tokens", None):
        cfg.minutes.max_tokens = args.minutes_max_tokens
    if getattr(args, "skill", None):
        cfg.skill.name = args.skill
    if getattr(args, "output", None):
        cfg.skill.outputs = [s.strip() for s in args.output.split(",") if s.strip()]
    return cfg
