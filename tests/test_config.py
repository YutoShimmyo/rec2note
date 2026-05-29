"""Tests for config loading and the precedence merge."""
import argparse

from src.config import (
    AppConfig,
    load_config,
    apply_skill_defaults,
    apply_cli_overrides,
)
from src.skills import load_skill


def _empty_args(**kw):
    keys = [
        "language", "profile", "asr_preset", "asr_backend", "asr_model",
        "minutes_backend", "minutes_language", "minutes_local_runtime",
        "minutes_model", "minutes_max_tokens", "skill", "output",
    ]
    ns = argparse.Namespace(**{k: None for k in keys})
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


def test_defaults():
    cfg = AppConfig()
    assert cfg.skill.name == "meeting-minutes"
    assert cfg.minutes.max_tokens == 2048


def test_skill_defaults_override_config():
    cfg = load_config(None)  # repo config.yaml
    skill = load_skill("magic-lecture")
    cfg = apply_skill_defaults(cfg, skill.defaults, skill.outputs)
    assert cfg.minutes.backend == "api"
    assert cfg.minutes.api.provider == "openai"
    assert cfg.minutes.max_tokens == 8192
    assert cfg.skill.outputs == ["md", "pdf"]


def test_cli_beats_skill():
    cfg = load_config(None)
    skill = load_skill("magic-lecture")
    cfg = apply_skill_defaults(cfg, skill.defaults, skill.outputs)
    cfg = apply_cli_overrides(
        cfg, _empty_args(minutes_backend="local", output="md", minutes_max_tokens=4096)
    )
    assert cfg.minutes.backend == "local"
    assert cfg.skill.outputs == ["md"]
    assert cfg.minutes.max_tokens == 4096


def test_meeting_minutes_keeps_config_provider():
    # meeting-minutes does not set api defaults → config.yaml provider wins.
    cfg = load_config(None)
    config_provider = cfg.minutes.api.provider
    skill = load_skill("meeting-minutes")
    cfg = apply_skill_defaults(cfg, skill.defaults, skill.outputs)
    assert cfg.minutes.api.provider == config_provider
    assert cfg.skill.outputs == ["md"]


def test_output_parsing_splits_csv():
    cfg = AppConfig()
    cfg = apply_cli_overrides(cfg, _empty_args(output="md, pdf"))
    assert cfg.skill.outputs == ["md", "pdf"]
