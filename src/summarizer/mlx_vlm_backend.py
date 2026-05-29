"""MLX-VLM local summarizer backend (Apple Silicon only).

Required for multimodal models like Gemma 4 E4B.
Install: uv add mlx-vlm
"""
from __future__ import annotations

import gc

from .base import SummarizerBackend
from ..preprocess import clean_transcript
from ..prompts import load_prompt, render_prompt


class MLXVLMSummarizer(SummarizerBackend):
    """Summarizer using mlx-vlm on Apple Silicon (supports multimodal models like Gemma 4)."""

    DEFAULT_MODEL = "mlx-community/gemma-4-e4b-it-4bit"

    def __init__(self, model_path: str = ""):
        self.model_path = model_path or self.DEFAULT_MODEL

    @property
    def name(self) -> str:
        return f"mlx-vlm/{self.model_path}"

    def summarize(
        self,
        transcript: str,
        language: str = "ja",
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        try:
            from mlx_vlm import load, generate
            from mlx_vlm.prompt_utils import apply_chat_template
            from mlx_vlm.utils import load_config as vlm_load_config
        except ImportError as exc:
            raise RuntimeError(
                "mlx-vlm is not installed.\n"
                "  Install:  uv add mlx-vlm\n"
                "  Note: mlx-vlm requires Apple Silicon (M1/M2/M3/M4).\n"
                "  On other hardware use --minutes-backend api or ollama."
            ) from exc

        from ..preprocess import truncate_transcript, count_tokens
        cleaned = clean_transcript(transcript)
        cleaned = truncate_transcript(cleaned, runtime="mlx-vlm", language=language)
        token_est = count_tokens(cleaned)
        print(f"[Summarizer] Estimated input tokens: ~{token_est:,}")
        system_prompt = system_prompt or load_prompt(language)
        user_message = render_prompt(system_prompt, cleaned)

        print(f"[Summarizer] Loading MLX-VLM model: {self.model_path}")
        model, processor = load(self.model_path)
        config = vlm_load_config(self.model_path)

        # apply_chat_template formats the prompt for the specific model
        # num_images=0 for text-only inference
        prompt = apply_chat_template(
            processor, config, user_message, num_images=0
        )

        print("[Summarizer] Generating summary…")
        result = generate(
            model,
            processor,
            prompt=prompt,
            image=None,
            max_tokens=max_tokens or 2048,
            verbose=True,
        )

        del model, processor
        gc.collect()

        # mlx-vlm returns a GenerationResult object; extract text if needed
        if isinstance(result, str):
            return result
        return str(result.text) if hasattr(result, "text") else str(result)
