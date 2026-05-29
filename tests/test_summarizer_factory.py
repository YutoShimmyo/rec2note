"""Tests for the summarizer factory (no network calls)."""
import pytest

from src.summarizer import create_summarizer


def test_backend_none_returns_none():
    assert create_summarizer("none") is None
    assert create_summarizer("") is None


def test_openai_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    s = create_summarizer("api", api_provider="openai", api_model="gpt-5.5")
    assert type(s).__name__ == "OpenAISummarizer"
    assert s.name == "openai/gpt-5.5"


def test_gemini_provider(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    s = create_summarizer("api", api_provider="gemini", api_model="gemini-2.5-flash")
    assert type(s).__name__ == "GeminiSummarizer"


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        create_summarizer("api", api_provider="bogus")


def test_unknown_backend_raises():
    with pytest.raises(ValueError):
        create_summarizer("bogus")
