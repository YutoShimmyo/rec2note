"""Tests for the skill loader."""
from src.skills import list_skills, load_skill, resolve_prompt_language
from src.prompts import load_prompt, render_prompt


def test_bundled_skills_present():
    skills = list_skills()
    assert "meeting-minutes" in skills
    assert "magic-lecture" in skills


def test_meeting_minutes_backward_compatible_output():
    s = load_skill("meeting-minutes")
    assert s.subdir == "minutes"
    assert s.output_stem_suffix == "_minutes"
    assert s.outputs == ["md"]
    assert s.prompt_language_mode == "audio"


def test_magic_lecture_spec():
    s = load_skill("magic-lecture")
    assert s.subdir == "magic-lecture"   # empty subdir → skill name
    assert s.output_stem_suffix == ""
    assert s.outputs == ["md", "pdf"]
    assert s.prompt_language_mode == "fixed"
    assert s.fixed_language == "ja"
    assert s.defaults["api"]["provider"] == "openai"
    assert s.defaults["max_tokens"] == 8192


def test_magic_lecture_always_japanese():
    s = load_skill("magic-lecture")
    # Even an English recording resolves to ja (fixed).
    assert resolve_prompt_language(s, cli_language="en", detected_language="en") == "ja"


def test_meeting_minutes_follows_audio_language():
    s = load_skill("meeting-minutes")
    assert resolve_prompt_language(s, cli_language="auto", detected_language="en") == "en"
    assert resolve_prompt_language(s, cli_language="ja", detected_language=None) == "ja"
    assert resolve_prompt_language(s, cli_language="auto", detected_language=None) == "ja"  # default


def test_magic_prompt_has_placeholder_and_injects():
    s = load_skill("magic-lecture")
    prompt = load_prompt("ja", prompt_dir=s.prompt_dir, default_language=s.default_language)
    assert "[transcript]" in prompt
    rendered = render_prompt(prompt, "TRANSCRIPT_BODY")
    assert "TRANSCRIPT_BODY" in rendered
    assert "[transcript]" not in rendered
