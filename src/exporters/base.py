"""Abstract base class for output exporters."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExportResult:
    path: Path
    format: str


class Exporter(ABC):
    """Abstract base for all output-format exporters.

    An exporter takes the generated Markdown (the single source of truth) and
    writes it to disk in some format.
    """

    @abstractmethod
    def export(self, markdown: str, *, out_path: Path, title: str = "") -> ExportResult:
        """Write ``markdown`` to ``out_path`` in this exporter's format."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this exporter."""
        ...

    @property
    @abstractmethod
    def extension(self) -> str:
        """File extension produced (without the dot), e.g. 'md' / 'pdf'."""
        ...
