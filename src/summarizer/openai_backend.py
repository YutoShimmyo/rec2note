"""OpenAI / ChatGPT API summarizer backend (recommended provider)."""
from __future__ import annotations

import os
import time
from typing import Optional

from dotenv import load_dotenv

from .base import SummarizerBackend
from ..preprocess import clean_transcript
from ..prompts import load_prompt, render_prompt


class OpenAISummarizer(SummarizerBackend):
    """Summarizer using the OpenAI (ChatGPT) API."""

    def __init__(self, model: str = "gpt-5.5", api_key: Optional[str] = None):
        load_dotenv()
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set.\n"
                "  1. Copy template:  cp .env.template .env\n"
                "  2. Edit .env and set OPENAI_API_KEY=<your_key>\n"
                "  Get a key at: https://platform.openai.com/api-keys"
            )

    @property
    def name(self) -> str:
        return f"openai/{self.model}"

    def summarize(
        self,
        transcript: str,
        language: str = "auto",
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        from openai import OpenAI

        from ..preprocess import truncate_transcript, count_tokens
        cleaned = clean_transcript(transcript)
        cleaned = truncate_transcript(cleaned, runtime="api", language=language)
        token_est = count_tokens(cleaned)
        print(f"[Summarizer] Estimated input tokens: ~{token_est:,}")
        system_prompt = system_prompt or load_prompt(language)
        prompt = render_prompt(system_prompt, cleaned)

        client = OpenAI(api_key=self.api_key)
        kwargs: dict = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if max_tokens:
            # Newer models use max_completion_tokens; older ones max_tokens.
            kwargs["max_completion_tokens"] = max_tokens

        for attempt in range(3):
            try:
                response = client.chat.completions.create(**kwargs)
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"[Summarizer] Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    wait = 2.0 * (2**attempt)
                    print(f"[Summarizer] Retrying in {wait:.0f}s...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        f"OpenAI summarization failed after 3 attempts: {e}"
                    ) from e
        return ""
