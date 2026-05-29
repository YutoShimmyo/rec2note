"""Tests for prompt loading and transcript injection."""
from pathlib import Path

import pytest

from src.prompts import load_prompt, render_prompt, available_languages


def test_render_prompt_with_square_placeholder():
    out = render_prompt("Intro\n[transcript]\nEnd", "BODY")
    assert out == "Intro\nBODY\nEnd"
    assert "[transcript]" not in out


def test_render_prompt_with_curly_placeholder():
    out = render_prompt("A {transcript} B", "X")
    assert out == "A X B"


def test_render_prompt_appends_when_no_placeholder():
    assert render_prompt("instructions", "BODY") == "instructions\n\nBODY"


def test_load_prompt_from_custom_dir(tmp_path: Path):
    (tmp_path / "ja.md").write_text("日本語プロンプト", encoding="utf-8")
    (tmp_path / "en.md").write_text("english prompt", encoding="utf-8")
    assert load_prompt("ja", prompt_dir=tmp_path) == "日本語プロンプト"
    assert load_prompt("en", prompt_dir=tmp_path) == "english prompt"


def test_load_prompt_falls_back_to_default_language(tmp_path: Path):
    (tmp_path / "ja.md").write_text("JA", encoding="utf-8")
    # "auto"/unknown has no file → falls back to default_language (ja)
    assert load_prompt("auto", prompt_dir=tmp_path, default_language="ja") == "JA"
    assert load_prompt("zz", prompt_dir=tmp_path, default_language="ja") == "JA"


def test_load_prompt_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_prompt("ja", prompt_dir=tmp_path, default_language="ja")


def test_available_languages(tmp_path: Path):
    (tmp_path / "ja.md").write_text("x", encoding="utf-8")
    (tmp_path / "en.md").write_text("x", encoding="utf-8")
    (tmp_path / "README.md").write_text("x", encoding="utf-8")
    assert available_languages(tmp_path) == ["en", "ja"]
