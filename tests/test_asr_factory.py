"""ASR factory behaviour that does not require model downloads."""
import platform
import sys
import types

import numpy as np

from src.asr import create_backend
from src.asr import mlx_whisper_backend
from src.asr.mlx_whisper_backend import MLXWhisperBackend


def test_default_uses_mlx_whisper_on_apple_silicon():
    backend = create_backend(profile="standard", language="ja")
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        assert backend.name.startswith("mlx-whisper/")
    else:
        assert backend.name.startswith("faster-whisper/")


def test_mlx_backend_accepts_familiar_model_alias():
    backend = create_backend(backend_override="mlx_whisper", model_override="small")
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        assert "mlx-community/whisper-small" in backend.name


def test_mlx_keeps_context_inside_vad_speech_blocks(monkeypatch, tmp_path):
    """Long-form context is retained inside each VAD-delimited speech block."""
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        return

    captured = []

    def fake_transcribe(*args, **kwargs):
        captured.append(kwargs)
        return {"text": "done", "language": "en"}

    monkeypatch.setitem(sys.modules, "mlx_whisper", types.SimpleNamespace(transcribe=fake_transcribe))
    monkeypatch.setattr(
        mlx_whisper_backend,
        "_load_speech_blocks",
        lambda _: [
            mlx_whisper_backend._SpeechBlock(np.zeros(16_000, dtype=np.float32), 0.0, 1.0),
            mlx_whisper_backend._SpeechBlock(np.zeros(16_000, dtype=np.float32), 10.0, 11.0),
        ],
    )
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"")
    MLXWhisperBackend("small").transcribe(str(audio), language="en")

    assert len(captured) == 2
    assert all(call["condition_on_previous_text"] is True for call in captured)
