"""Abstract base class for summarization backends."""
from abc import ABC, abstractmethod
from typing import Optional


class SummarizerBackend(ABC):
    """Abstract base for all meeting-minutes generation backends."""

    @abstractmethod
    def summarize(
        self,
        transcript: str,
        language: str = "auto",
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate structured output from the given transcript.

        Args:
            transcript: the raw transcript text.
            language: language code used to pick a prompt when ``system_prompt``
                is not given.
            system_prompt: an explicit system prompt (e.g. supplied by a skill).
                When ``None``, the backend loads one via ``load_prompt(language)``.
            max_tokens: generation cap. When ``None``, the backend's default.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this backend."""
        ...
