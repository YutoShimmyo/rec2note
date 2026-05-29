"""Summarizer factory: creates the appropriate backend from config parameters."""
from __future__ import annotations

from typing import Optional

from .base import SummarizerBackend


def create_summarizer(
    backend: str,
    api_provider: str = "gemini",
    api_model: str = "gemini-1.5-flash",
    local_runtime: str = "mlx-lm",
    model_path: str = "",
    ollama_model: str = "gemma2:9b",
    ollama_url: str = "http://localhost:11434",
) -> Optional[SummarizerBackend]:
    """
    Create and return a SummarizerBackend, or None if backend is 'none'.

    Args:
        backend: 'none' | 'api' | 'local'
        api_provider: 'gemini' (used when backend='api')
        api_model: Gemini model name
        local_runtime: 'mlx-lm' | 'ollama' (used when backend='local')
        model_path: HuggingFace repo ID or local path for mlx-lm
        ollama_model: Model name for Ollama
        ollama_url: Ollama server URL
    """
    if not backend or backend == "none":
        return None

    if backend == "api":
        if api_provider in ("openai", "chatgpt"):
            from .openai_backend import OpenAISummarizer

            return OpenAISummarizer(model=api_model)
        if api_provider == "gemini":
            from .gemini import GeminiSummarizer

            return GeminiSummarizer(model=api_model)
        raise ValueError(
            f"Unknown API provider: '{api_provider}'. Supported: openai, gemini"
        )

    if backend == "local":
        if local_runtime == "mlx-lm":
            from .mlx_backend import MLXSummarizer

            return MLXSummarizer(model_path=model_path)
        if local_runtime == "mlx-vlm":
            from .mlx_vlm_backend import MLXVLMSummarizer

            return MLXVLMSummarizer(model_path=model_path)
        if local_runtime == "ollama":
            from .ollama_backend import OllamaSummarizer

            return OllamaSummarizer(model=ollama_model, base_url=ollama_url)
        raise ValueError(
            f"Unknown local runtime: '{local_runtime}'. Supported: mlx-lm, mlx-vlm, ollama"
        )

    raise ValueError(
        f"Unknown minutes backend: '{backend}'. Supported: none, api, local"
    )
