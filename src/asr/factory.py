"""ASR backend factory: resolves presets and creates backends with fallback."""
from __future__ import annotations

from .base import ASRBackend
from .faster_whisper_backend import FasterWhisperBackend
from .mlx_whisper_backend import MLXWhisperBackend
from .parakeet_backend import ParakeetBackend


# ---------------------------------------------------------------------------
# Preset definitions
# Each preset lists (backend_name, model_name) candidates in priority order.
# If the first candidate fails (e.g. missing dependency), the next is tried.
# ---------------------------------------------------------------------------
PRESETS: dict[str, dict] = {
    "A": {
        "description": "English · High Quality  (MLX Whisper large-v3 → Parakeet TDT → Whisper large-v3)",
        "candidates": [
            ("mlx_whisper", "mlx-community/whisper-large-v3"),
            ("parakeet", "nvidia/parakeet-tdt-0.6b-v2"),
            ("faster_whisper", "large-v3"),
        ],
    },
    "B": {
        "description": "English · Standard  (MLX Whisper large-v3-turbo → Whisper large-v3-turbo)",
        "candidates": [
            ("mlx_whisper", "mlx-community/whisper-large-v3-turbo"),
            ("faster_whisper", "large-v3-turbo"),
        ],
        "fallback_candidates": [
            ("faster_whisper", "medium"),
            ("faster_whisper", "small"),
        ],
    },
    "C": {
        "description": "Multilingual · High Quality  (MLX Whisper large-v3 → Whisper large-v3)",
        "candidates": [
            ("mlx_whisper", "mlx-community/whisper-large-v3"),
            ("faster_whisper", "large-v3"),
        ],
    },
    "D": {
        "description": "Multilingual · Standard  (MLX Whisper large-v3-turbo → Whisper large-v3-turbo)",
        "candidates": [
            ("mlx_whisper", "mlx-community/whisper-large-v3-turbo"),
            ("faster_whisper", "large-v3-turbo"),
        ],
        "fallback_candidates": [
            ("faster_whisper", "medium"),
        ],
    },
}

# Map (profile, language) → default preset letter.
# Whisper large-v3 / large-v3-turbo handle both ja and en natively;
# presets C/D are used for Japanese and auto-detection.
_PROFILE_PRESET_MAP: dict[tuple[str, str], str] = {
    ("quality",  "en"):   "A",
    ("standard", "en"):   "B",
    ("fast",     "en"):   "B",
    ("quality",  "ja"):   "C",
    ("standard", "ja"):   "D",
    ("fast",     "ja"):   "D",
    ("quality",  "auto"): "C",
    ("standard", "auto"): "D",
    ("fast",     "auto"): "D",
}


def resolve_preset(preset: str, profile: str, language: str) -> str:
    """Resolve 'auto' preset to a concrete letter (A–D)."""
    if preset and preset != "auto" and preset in PRESETS:
        return preset
    return _PROFILE_PRESET_MAP.get((profile, language), "D")


def create_backend(
    preset: str = "auto",
    backend_override: str = "",
    model_override: str = "",
    device: str = "",
    profile: str = "standard",
    language: str = "auto",
) -> ASRBackend:
    """
    Create an ASR backend.

    Priority:
    1. backend_override + model_override  →  specific backend/model
    2. preset (or resolved from profile+language)  →  candidate list with fallback
    """
    if backend_override:
        return _instantiate(backend_override, model_override, device)

    resolved = resolve_preset(preset, profile, language)
    preset_def = PRESETS[resolved]
    print(f"[ASR] Preset {resolved}: {preset_def['description']}")

    errors: list[str] = []
    for backend_name, model_name in preset_def.get("candidates", []):
        actual_model = model_override or model_name
        try:
            return _instantiate(backend_name, actual_model, device)
        except Exception as e:
            errors.append(f"  {backend_name}/{actual_model}: {e}")

    for backend_name, model_name in preset_def.get("fallback_candidates", []):
        actual_model = model_override or model_name
        try:
            backend = _instantiate(backend_name, actual_model, device)
            print(f"[ASR] Using fallback: {backend_name}/{actual_model}")
            return backend
        except Exception as e:
            errors.append(f"  {backend_name}/{actual_model} (fallback): {e}")

    raise RuntimeError(
        f"No available ASR backend for preset '{resolved}'.\n"
        "Attempted:\n" + "\n".join(errors) + "\n"
        "Please install faster-whisper:  uv add faster-whisper"
    )


def _instantiate(backend: str, model: str, device: str) -> ASRBackend:
    """Instantiate a backend by name; raises if unavailable."""
    if backend == "faster_whisper":
        return FasterWhisperBackend(
            model_size=model or "large-v3-turbo", device=device
        )
    if backend == "mlx_whisper":
        return MLXWhisperBackend(model_size=model or "mlx-community/whisper-large-v3-turbo")
    if backend == "parakeet":
        try:
            import nemo.collections.asr  # noqa: F401 – availability check
        except ImportError as exc:
            raise ImportError("nemo_toolkit not installed") from exc
        return ParakeetBackend(model_name=model)
    raise ValueError(
        f"Unknown ASR backend: '{backend}'. "
        "Supported: mlx_whisper, faster_whisper, parakeet"
    )
